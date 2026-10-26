"""Ingestion orchestrator: fetch → clean → filter → upsert."""

from __future__ import annotations

import asyncio
import os
from dataclasses import dataclass, field

import structlog

from config.profile import Profile, load_profile
from config.settings import get_settings
from config.targets import Targets, load_targets
from core.db import Job, Status, get_job_by_source_id, init_db, session_scope, upsert_job
from scorer.clients import LLMClient
from scorer.company_intelligence import (
    HttpCompanyIntelProvider,
    attach_company_intelligence,
    trustworthy_company_source,
)
from scorer.eligibility import attach_eligibility
from scraper.ats_boards import fetch_all_boards
from scraper.coverage import (
    CoverageReport,
    SearchObservation,
    SearchStatus,
    build_coverage_report,
    fail_unrecorded,
    log_coverage,
    write_coverage,
)
from scraper.discovery import DiscoveryPlan, build_discovery_plan, log_discovery_plan
from scraper.filters import evaluate
from scraper.linkedin_jobspy import QueryExecutor, fetch_linkedin_indeed
from scraper.models import RawPosting, to_job
from scraper.redact import redact_error
from scraper.simplify_list import discover_boards, fetch_simplify_rows
from scraper.structured_jd import attach_structured_jd
from scraper.workday_rest import fetch_all_workday

log = structlog.get_logger(__name__)

_CATCHUP_HOURS = 720
_DAILY_BOARD_HOURS = 36


@dataclass
class IngestSummary:
    fetched: int = 0
    discovered: int = 0
    filtered_out: int = 0
    upserted: int = 0
    by_source: dict[str, int] = field(default_factory=dict)
    errors: list[str] = field(default_factory=list)
    coverage: CoverageReport | None = None
    within_run_duplicates: int = 0
    hours_old: int | None = None
    partial: bool = False
    queries_failed: int = 0
    boards_not_found: list[str] = field(default_factory=list)
    boards_discovered: int = 0
    mode: str = "daily"


async def _load_role_client() -> LLMClient | None:
    try:
        from scorer.clients import build_llm_client

        return build_llm_client()
    except Exception:
        return None


async def _apply_role_classification(
    session: object,
    job: Job,
    role_client: LLMClient | None,
) -> None:
    """Label the role from the normalized JD. Does not change job status."""
    from sqlmodel.ext.asyncio.session import AsyncSession

    from scorer.role_classify import (
        ROLE_CLASSIFIER_VERSION,
        classification_is_current,
        classify_role,
    )

    if not isinstance(session, AsyncSession):
        return
    existing = await get_job_by_source_id(session, job.source, job.external_id)
    if existing is not None and classification_is_current(
        role_family=existing.role_family,
        role_content_hash=existing.role_content_hash,
        role_classifier_version=existing.role_classifier_version,
        content_hash=job.content_hash,
    ):
        job.role_family = existing.role_family
        job.role_subfamily = existing.role_subfamily
        job.role_confidence = existing.role_confidence
        job.role_evidence = existing.role_evidence
        job.role_classifier_version = existing.role_classifier_version
        job.role_content_hash = existing.role_content_hash
        job.role_secondary_family = existing.role_secondary_family
        job.role_secondary_subfamily = existing.role_secondary_subfamily
        job.role_secondary_confidence = existing.role_secondary_confidence
        job.role_secondary_evidence = existing.role_secondary_evidence
        return
    structured = None
    if job.id is not None:
        from scraper.structured_jd import (
            STRUCTURED_JD_VERSION,
            StructuredJdDocument,
            get_structured_jd,
        )

        stored = await get_structured_jd(session, job.id)
        if (
            stored is not None
            and stored.version == STRUCTURED_JD_VERSION
            and stored.availability != "unavailable"
        ):
            try:
                structured = StructuredJdDocument.model_validate(stored.document)
            except Exception:
                structured = None
    classified = await classify_role(
        title=job.title,
        description=job.description_clean or "",
        content_hash=job.content_hash,
        discovery_family=job.discovery_family,
        discovery_bucket=job.discovery_bucket,
        discovery_query=job.discovery_query,
        client=role_client,
        truncated=job.jd_truncated is True,
        structured=structured,
    )
    job.role_family = classified.role_family
    job.role_subfamily = classified.role_subfamily
    job.role_confidence = classified.role_confidence
    job.role_evidence = classified.role_evidence
    job.role_classifier_version = classified.role_classifier_version or ROLE_CLASSIFIER_VERSION
    job.role_content_hash = classified.role_content_hash
    job.role_secondary_family = classified.role_secondary_family
    job.role_secondary_subfamily = classified.role_secondary_subfamily
    job.role_secondary_confidence = classified.role_secondary_confidence
    job.role_secondary_evidence = classified.role_secondary_evidence or None


def _attach_coverage(
    summary: IngestSummary,
    plan: DiscoveryPlan,
    jobspy_observations: list[SearchObservation],
    workday_observations: list[SearchObservation],
    tenants: tuple[str, ...],
) -> None:
    try:
        summary.coverage = build_coverage_report(
            plan,
            [*jobspy_observations, *workday_observations],
            workday_tenants=tenants,
        )
        log_coverage(summary.coverage)
        if os.environ.get("PYTEST_CURRENT_TEST") is None:
            write_coverage(summary.coverage)
    except Exception as exc:
        log.warning("discovery_coverage_failed", error=str(exc)[:200])


def _mark_source_failed(
    plan: DiscoveryPlan,
    label: str,
    error: str,
    jobspy_observations: list[SearchObservation],
    workday_observations: list[SearchObservation],
    tenants: tuple[str, ...],
) -> None:
    if label == "boards":
        return
    if label == "jobspy":
        fail_unrecorded(
            plan,
            jobspy_observations,
            sources=plan.jobspy_sites,
            detail="",
            error=error,
        )
        return
    for tenant in tenants:
        fail_unrecorded(
            plan,
            workday_observations,
            sources=("workday",),
            detail=tenant,
            error=error,
        )


@dataclass(frozen=True, slots=True)
class _PersistCounts:
    discovered: int
    filtered_out: int
    upserted: int


async def _persist_postings(
    postings: list[RawPosting],
    profile: Profile,
    role_client: LLMClient | None,
) -> _PersistCounts:
    """Commit one batch. The caller records counts only after this returns.

    A raise here rolls this transaction back. Earlier commits stay. The caller
    must not mark these ids as handled until this function returns.
    """
    if not postings:
        return _PersistCounts(0, 0, 0)
    discovered = 0
    filtered_out = 0
    upserted = 0
    async with session_scope() as session:
        for posting in postings:
            posting.ensure_clean_description()
            result = evaluate(posting, profile)
            if result.passed:
                job = to_job(posting, status=Status.discovered)
                discovered += 1
            else:
                job = to_job(
                    posting,
                    status=Status.filtered_out,
                    justification=[result.reason or "filtered"],
                )
                filtered_out += 1
            saved = await upsert_job(session, job)
            upserted += 1
            if not result.passed:
                # A hard-filtered row never reaches scoring. Company lookups,
                # eligibility, JD reading and role calls would be spent for nothing.
                continue
            try:
                source = trustworthy_company_source(posting.company_url)
                await attach_company_intelligence(
                    session,
                    saved,
                    source_url=source[0] if source else None,
                    source_type=source[1] if source else "official_website",
                    provider=HttpCompanyIntelProvider() if source else None,
                )
            except Exception as exc:
                log.warning(
                    "company_intelligence_provider_failure",
                    company=saved.company,
                    error=str(exc)[:200],
                )
            try:
                await attach_eligibility(saved, profile)
            except Exception as exc:
                log.warning(
                    "eligibility_failed",
                    company=saved.company,
                    error=str(exc)[:200],
                )
            try:
                await attach_structured_jd(session, saved)
            except Exception as exc:
                log.warning(
                    "structured_jd_failed",
                    company=saved.company,
                    error=str(exc)[:200],
                )
            try:
                await _apply_role_classification(session, saved, role_client)
                from core.db import _stamp_role_family_weight

                _stamp_role_family_weight(saved)
                session.add(saved)
            except Exception as exc:
                log.warning(
                    "role_classification_failed",
                    company=saved.company,
                    error=str(exc)[:200],
                )
    return _PersistCounts(discovered, filtered_out, upserted)


def _dedupe(postings: list[RawPosting]) -> tuple[list[RawPosting], int]:
    seen: set[tuple[str, str]] = set()
    out: list[RawPosting] = []
    removed = 0
    for posting in postings:
        key = (posting.source.value, posting.external_id)
        if key in seen:
            removed += 1
            continue
        seen.add(key)
        out.append(posting)
    return out, removed


async def run_ingestion(
    *,
    targets: Targets | None = None,
    profile: Profile | None = None,
    include_jobspy: bool = True,
    include_workday: bool = True,
    include_boards: bool | None = None,
    search_capacity: int | None = None,
    jobspy_executor: QueryExecutor | None = None,
) -> IngestSummary:
    """Run one full discovery cycle and persist results.

    ``search_capacity`` is how many discovery queries to plan. ``None`` runs every
    enabled query once. One query is not one HTTP request or one posting: JobSpy
    still searches each configured site, and Workday still searches each tenant.
    ``INGEST_POSTING_CAP`` limits how many of those rows this run commits. It
    does not stop the sites from returning more. Allocation does not look at fit.
    """
    await init_db()
    targets = targets or load_targets()
    profile = profile or load_profile()
    settings = get_settings()
    if settings.ingest_mode == "catchup" and targets.search.hours_old < _CATCHUP_HOURS:
        # Catch-up looks back a month so roles that opened before the first run are found.
        targets = targets.model_copy(
            update={
                "search": targets.search.model_copy(update={"hours_old": _CATCHUP_HOURS}),
            }
        )
    summary = IngestSummary(hours_old=targets.search.hours_old, mode=settings.ingest_mode)
    plan = build_discovery_plan(targets, capacity=search_capacity)
    log_discovery_plan(plan)
    provenance = {
        search.query: (search.family_id, search.bucket_id) for search in plan.searches
    }
    jobspy_observations: list[SearchObservation] = []
    workday_observations: list[SearchObservation] = []

    active_tenants = targets.active_workday_tenants()
    role_client = await _load_role_client()
    seen: set[tuple[str, str]] = set()
    committed = 0
    persist_lock = asyncio.Lock()

    async def _accept(label: str, postings: list[RawPosting]) -> bool:
        nonlocal committed
        if not postings:
            return True
        async with persist_lock:
            fresh: list[RawPosting] = []
            for posting in postings:
                key = (posting.source.value, posting.external_id)
                if key in seen:
                    summary.within_run_duplicates += 1
                    continue
                fresh.append(posting)
            if not fresh:
                summary.by_source[label] = summary.by_source.get(label, 0) + len(postings)
                return True
            cap = get_settings().ingest_posting_cap
            to_save = fresh
            if cap is not None:
                room = cap - committed
                if room <= 0:
                    log.info("ingest_posting_cap_reached", cap=cap, skipped=len(fresh))
                    return True
                if len(fresh) > room:
                    log.info(
                        "ingest_posting_cap_reached",
                        cap=cap,
                        skipped=len(fresh) - room,
                    )
                    to_save = fresh[:room]
            try:
                counts = await _persist_postings(to_save, profile, role_client)
            except Exception as exc:
                safe = redact_error(str(exc))
                summary.errors.append(f"{label}: {safe}")
                log.warning("ingestion_persist_failed", source=label, error=safe)
                return False
            for posting in to_save:
                seen.add((posting.source.value, posting.external_id))
            committed += counts.upserted
            summary.discovered += counts.discovered
            summary.filtered_out += counts.filtered_out
            summary.upserted += counts.upserted
            summary.fetched += len(to_save)
            summary.by_source[label] = summary.by_source.get(label, 0) + len(postings)
            return True

    use_boards = settings.enable_ats_boards if include_boards is None else include_boards
    boards = list(targets.ats_boards) if use_boards else []
    board_age = settings.ats_max_age_hours
    if board_age is None and settings.ingest_mode == "daily":
        board_age = _DAILY_BOARD_HOURS

    tasks: list[asyncio.Task[list[RawPosting]]] = []
    labels: list[str] = []

    async def _run_boards() -> list[RawPosting]:
        to_read = list(boards)
        if settings.simplify_discovery:
            known = {(item.provider, item.token.lower()) for item in to_read}
            extra = discover_boards(await fetch_simplify_rows(), known)
            summary.boards_discovered = len(extra)
            to_read.extend(extra)
        run = await fetch_all_boards(to_read, max_age_hours=board_age)
        summary.boards_not_found = run.not_found
        if run.failed:
            summary.errors.append(f"boards: {len(run.failed)} failed: {', '.join(run.failed)}")
        await _accept("boards", run.postings)
        return []

    async def _run_jobspy() -> list[RawPosting]:
        leftover = await fetch_linkedin_indeed(
            targets,
            profile=profile,
            plan=plan,
            observations=jobspy_observations,
            on_batch=lambda batch: _accept("jobspy", batch),
            query_executor=jobspy_executor,
        )
        # A caller that replaces fetch and returns rows still gets those rows saved.
        await _accept("jobspy", leftover)
        return []

    async def _run_workday() -> list[RawPosting]:
        postings = await fetch_all_workday(
            active_tenants,
            default_search_terms=[search.query for search in plan.searches],
            hours_old=targets.search.hours_old,
            provenance=provenance,
            observations=workday_observations,
        )
        await _accept("workday", postings)
        return []

    if include_jobspy and plan.jobspy_sites and plan.searches:
        tasks.append(asyncio.create_task(_run_jobspy(), name="jobspy"))
        labels.append("jobspy")

    if include_workday and plan.workday_enabled and active_tenants and plan.searches:
        tasks.append(asyncio.create_task(_run_workday(), name="workday"))
        labels.append("workday")

    if use_boards and (boards or settings.simplify_discovery):
        tasks.append(asyncio.create_task(_run_boards(), name="boards"))
        labels.append("boards")

    if not tasks:
        log.warning(
            "ingestion_noop",
            reason="no enabled sources produced work",
            include_jobspy=include_jobspy,
            include_workday=include_workday,
            search_terms=len(targets.search.terms),
            active_workday=len(active_tenants),
        )
        _attach_coverage(summary, plan, jobspy_observations, workday_observations, ())
        return summary

    results = await asyncio.gather(*tasks, return_exceptions=True)
    for label, result in zip(labels, results, strict=True):
        if isinstance(result, BaseException):
            safe = redact_error(str(result))
            summary.errors.append(f"{label}: {safe}")
            log.warning("ingestion_source_failed", source=label, error=safe)
            _mark_source_failed(
                plan,
                label,
                safe,
                jobspy_observations,
                workday_observations,
                tuple(tenant.name for tenant in active_tenants),
            )

    observations = (*jobspy_observations, *workday_observations)
    failed_queries = {
        observation.query
        for observation in observations
        if observation.status is SearchStatus.failed
    }
    troubled = {
        observation.query
        for observation in observations
        if observation.status in {SearchStatus.failed, SearchStatus.partial}
    }
    summary.queries_failed = len(failed_queries)
    summary.partial = bool(troubled or summary.errors)

    tenants = tuple(tenant.name for tenant in active_tenants) if include_workday else ()
    _attach_coverage(summary, plan, jobspy_observations, workday_observations, tenants)

    log.info(
        "ingestion_complete",
        fetched=summary.fetched,
        discovered=summary.discovered,
        filtered_out=summary.filtered_out,
        upserted=summary.upserted,
        by_source=summary.by_source,
        errors=summary.errors,
        partial=summary.partial,
        queries_failed=summary.queries_failed,
    )
    return summary
