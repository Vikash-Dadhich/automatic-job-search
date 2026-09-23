"""Batch runner: staged Workday-eligible jobs -> pending_review (or manual_review).

Eligibility includes native Workday ingest jobs AND LinkedIn/Indeed postings whose
stored URL already points at a company Workday careers page (job_url_direct).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime

import structlog

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
    errors: int = 0
    error_details: list[str] = field(default_factory=list)


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
    ) -> ApplySummary:
        await init_db()
        settings = get_settings()
        effective_limit = limit if limit is not None else settings.apply_limit
        applicator = applicator or self._resolve_applicator()
        summary = ApplySummary()

        async with session_scope() as session:
            jobs = await get_jobs_by_status(
                session,
                Status.staged,
                limit=effective_limit,
            )

        if not jobs:
            log.info("apply_pending_empty")
            return summary

        for job in jobs:
            if not _eligible(job):
                summary.skipped += 1
                log.info(
                    "apply_skipped",
                    job_id=job.id,
                    source=job.source.value if job.source else None,
                    has_resume=bool(job.resume_path),
                )
                continue

            try:
                job = await _ensure_tenant(job)
                result = await applicator.apply(job)
                await self._persist_success(job, result)
                summary.applied += 1
                summary.pending_review += 1
            except BlockerError as exc:
                log.warning(
                    "apply_blocker",
                    job_id=job.id,
                    error=str(exc),
                    screenshot=exc.screenshot_path,
                )
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
) -> ApplySummary:
    """Module-level entry point used by README / Step 7."""
    return await ApplyRunner(applicator=applicator, profile=profile).apply_pending(
        limit=limit,
        applicator=applicator,
    )
