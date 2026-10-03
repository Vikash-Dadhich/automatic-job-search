"""Batch runner: staged Workday-eligible jobs -> pending_review (or manual_review).

Eligibility includes native Workday ingest jobs AND LinkedIn/Indeed postings whose
stored URL already points at a company Workday careers page (job_url_direct).
"""

from __future__ import annotations

import random
from collections.abc import Awaitable, Callable
from dataclasses import dataclass, field
from datetime import UTC, datetime

import structlog

from automation.pacing import acquire, is_pace_blocker, note_pace_block, note_success
from automation.workday import Applicator, ApplyResult, BlockerError, WorkdayApplicator
from config.profile import Profile, load_profile
from config.settings import get_settings
from core.apply_url import is_automateable_apply_url, workday_parts
from core.db import (
    Job,
    Source,
    Status,
    get_job_by_id,
    get_jobs_by_status,
    init_db,
    session_scope,
)

log = structlog.get_logger(__name__)


@dataclass
class ApplySummary:
    applied: int = 0
    pending_review: int = 0
    manual_review: int = 0
    skipped: int = 0
    blackout_skipped: int = 0
    errors: int = 0
    error_details: list[str] = field(default_factory=list)


def _ready_for_explicit_apply(job: Job | None) -> bool:
    """Portfolio handed this id. It must still be staged, allocated, and applyable."""
    return (
        job is not None
        and job.status == Status.staged
        and job.portfolio_decision == "ALLOCATED"
        and job.eligibility_state != "CLEARLY_INELIGIBLE"
        and _eligible(job)
    )


def _log_explicit_skip(job: Job | None, job_id: int | None) -> None:
    if job is not None and job.portfolio_decision != "ALLOCATED":
        log.info("apply_skipped_portfolio_not_allocated", job_id=job_id)
        return
    log.info(
        "apply_skipped",
        job_id=job_id,
        source=job.source.value if job is not None and job.source else None,
        has_resume=bool(job.resume_path) if job is not None else False,
    )


async def _reload_job(job_id: int | None) -> Job | None:
    if job_id is None:
        return None
    async with session_scope() as session:
        return await get_job_by_id(session, job_id)


def _eligible(job: Job) -> bool:
    """Workday source OR any source whose URL is a Workday company apply link."""
    if not job.resume_path:
        return False
    if job.source == Source.workday:
        return True
    return is_automateable_apply_url(job.url or "")


async def _ensure_tenant(job: Job) -> Job:
    """Stamp job.tenant from the Workday URL when missing (LinkedIn→Workday case)."""
    if (job.tenant or "").strip():
        return job
    parts = workday_parts(job.url or "")
    if parts is None or job.id is None:
        return job
    async with session_scope() as session:
        target = await get_job_by_id(session, job.id)
        if target is None:
            return job
        if not (target.tenant or "").strip():
            target.tenant = parts.tenant
            session.add(target)
            log.info(
                "apply_tenant_inferred",
                job_id=job.id,
                tenant=parts.tenant,
                source=job.source.value if job.source else None,
            )
    job.tenant = parts.tenant
    return job


class ApplyRunner:
    """Drive Workday pre-fill for staged jobs with injectable Applicator."""

    def __init__(
        self,
        *,
        applicator: Applicator | None = None,
        profile: Profile | None = None,
    ) -> None:
        self._applicator = applicator
        self._profile = profile

    def _resolve_applicator(self) -> Applicator:
        if self._applicator is not None:
            return self._applicator
        profile = self._profile or load_profile()
        return WorkdayApplicator(profile=profile)

    async def apply_pending(
        self,
        *,
        limit: int | None = None,
        applicator: Applicator | None = None,
        sleep: Callable[[float], Awaitable[None]] | None = None,
        rng: random.Random | None = None,
        now: datetime | None = None,
        job_ids: list[int] | None = None,
    ) -> ApplySummary:
        await init_db()
        settings = get_settings()
        effective_limit = limit if limit is not None else settings.apply_limit
        applicator = applicator or self._resolve_applicator()
        summary = ApplySummary()

        require_allocation = job_ids is not None
        async with session_scope() as session:
            if job_ids is None:
                jobs = await get_jobs_by_status(
                    session,
                    Status.staged,
                    limit=effective_limit,
                )
            else:
                jobs = []
                seen: set[int] = set()
                for job_id in job_ids:
                    if job_id in seen:
                        summary.skipped += 1
                        log.info("apply_skipped", job_id=job_id, reason="duplicate")
                        continue
                    seen.add(job_id)
                    loaded = await get_job_by_id(session, job_id)
                    if loaded is not None and _ready_for_explicit_apply(loaded):
                        jobs.append(loaded)
                        continue
                    job = loaded
                    summary.skipped += 1
                    _log_explicit_skip(job, job_id)

        if not jobs:
            log.info("apply_pending_empty")
            return summary

        for job in jobs:
            if require_allocation:
                current = await _reload_job(job.id)
                if current is None or not _ready_for_explicit_apply(current):
                    summary.skipped += 1
                    _log_explicit_skip(current, job.id)
                    continue
                job = current
            elif not _eligible(job):
                summary.skipped += 1
                log.info(
                    "apply_skipped",
                    job_id=job.id,
                    source=job.source.value if job.source else None,
                    has_resume=bool(job.resume_path),
                )
                continue

            if settings.apply_pacing_enabled:
                slot = await acquire("workday", now=now, sleep=sleep, rng=rng)
                if slot.skip:
                    summary.blackout_skipped += 1
                    log.info("apply_platform_blackout", job_id=job.id, platform="workday")
                    continue

            try:
                job = await _ensure_tenant(job)
                result = await applicator.apply(job)
                await self._persist_success(job, result)
                if settings.apply_pacing_enabled:
                    await note_success("workday", now=now)
                summary.applied += 1
                summary.pending_review += 1
            except BlockerError as exc:
                log.warning(
                    "apply_blocker",
                    job_id=job.id,
                    error=str(exc),
                    screenshot=exc.screenshot_path,
                )
                if settings.apply_pacing_enabled and is_pace_blocker(str(exc)):
                    await note_pace_block("workday", now=now)
                await self._persist_blocker(job, exc)
                summary.manual_review += 1
            except Exception as exc:
                log.warning("apply_failed", job_id=job.id, error=str(exc))
                summary.errors += 1
                summary.error_details.append(f"job {job.id}: {exc}")
                await self._persist_error(job, str(exc))

        log.info(
            "apply_pending_complete",
            applied=summary.applied,
            pending_review=summary.pending_review,
            manual_review=summary.manual_review,
            skipped=summary.skipped,
            blackout_skipped=summary.blackout_skipped,
            errors=summary.errors,
        )
        return summary

    async def _persist_success(self, job: Job, result: ApplyResult) -> None:
        if job.id is None:
            return
        now = datetime.now(UTC)
        async with session_scope() as session:
            target = await get_job_by_id(session, job.id)
            if target is None:
                return
            target.status = Status.pending_review
            target.screenshot_path = result.screenshot_path
            target.application_answers = result.application_answers
            target.last_error = None
            target.updated_at = now
            session.add(target)
        from automation.tracker import record_prefill

        await record_prefill(job.id, occurred_at=now)

    async def _persist_blocker(self, job: Job, exc: BlockerError) -> None:
        if job.id is None:
            return
        now = datetime.now(UTC)
        async with session_scope() as session:
            target = await get_job_by_id(session, job.id)
            if target is None:
                return
            target.status = Status.manual_review
            if exc.screenshot_path:
                target.screenshot_path = exc.screenshot_path
            target.last_error = str(exc)
            target.alerted_at = None
            target.updated_at = now
            session.add(target)
        from automation.tracker import record_manual_review

        await record_manual_review(
            job.id,
            occurred_at=now,
            source="workday",
            note=str(exc)[:500],
        )

    async def _persist_error(self, job: Job, reason: str) -> None:
        if job.id is None:
            return
        try:
            now = datetime.now(UTC)
            async with session_scope() as session:
                target = await get_job_by_id(session, job.id)
                if target is None:
                    return
                target.status = Status.error
                target.last_error = reason
                target.alerted_at = None
                target.updated_at = now
                session.add(target)
        except Exception as persist_exc:
            log.warning(
                "apply_error_persist_failed",
                job_id=job.id,
                error=str(persist_exc),
            )


async def apply_pending(
    *,
    limit: int | None = None,
    applicator: Applicator | None = None,
    profile: Profile | None = None,
    sleep: Callable[[float], Awaitable[None]] | None = None,
    rng: random.Random | None = None,
    now: datetime | None = None,
    job_ids: list[int] | None = None,
) -> ApplySummary:
    """Module-level entry point used by README / Step 7.

    ``job_ids`` limits the run to those rows, in that order. Each must still be
    staged, Workday-eligible, and ``portfolio_decision`` ALLOCATED.
    ``None`` keeps the previous staged query and does not require a portfolio decision.
    """
    return await ApplyRunner(applicator=applicator, profile=profile).apply_pending(
        limit=limit,
        applicator=applicator,
        sleep=sleep,
        rng=rng,
        now=now,
        job_ids=job_ids,
    )
