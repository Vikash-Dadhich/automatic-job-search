"""Ingestion orchestrator: fetch → clean → filter → upsert."""

from __future__ import annotations

import asyncio
import os
from dataclasses import dataclass, field

import structlog

from config.profile import Profile, load_profile
from config.targets import Targets, load_targets
from core.db import Job, Status, get_job_by_source_id, init_db, session_scope, upsert_job
from scorer.clients import LLMClient
from scraper.coverage import (
    CoverageReport,
    SearchObservation,
    build_coverage_report,
    fail_unrecorded,
    log_coverage,
    write_coverage,
)
from scraper.discovery import DiscoveryPlan, build_discovery_plan, log_discovery_plan
from scraper.filters import evaluate
from scraper.linkedin_jobspy import fetch_linkedin_indeed
from scraper.models import RawPosting, to_job
from scraper.workday_rest import fetch_all_workday

log = structlog.get_logger(__name__)


@dataclass
class IngestSummary:
    fetched: int = 0
    discovered: int = 0
    filtered_out: int = 0
    upserted: int = 0
    by_source: dict[str, int] = field(default_factory=dict)
    errors: list[str] = field(default_factory=list)
    coverage: CoverageReport | None = None


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
        return
    classified = await classify_role(
        title=job.title,
        description=job.description_clean or "",
        content_hash=job.content_hash,
        discovery_family=job.discovery_family,
        discovery_bucket=job.discovery_bucket,
        discovery_query=job.discovery_query,
        client=role_client,
    )
    job.role_family = classified.role_family
    job.role_subfamily = classified.role_subfamily
    job.role_confidence = classified.role_confidence
    job.role_evidence = classified.role_evidence
    job.role_classifier_version = classified.role_classifier_version or ROLE_CLASSIFIER_VERSION
    job.role_content_hash = classified.role_content_hash


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


def _dedupe(postings: list[RawPosting]) -> list[RawPosting]:
    seen: set[tuple[str, str]] = set()
    out: list[RawPosting] = []
    for posting in postings:
        key = (posting.source.value, posting.external_id)
        if key in seen:
            continue
        seen.add(key)
        out.append(posting)
    return out


async def run_ingestion(
    *,
    targets: Targets | None = None,
    profile: Profile | None = None,
    include_jobspy: bool = True,
    include_workday: bool = True,
    search_capacity: int | None = None,
) -> IngestSummary:
    """Run one full discovery cycle and persist results.

    ``search_capacity`` is how many query executions to run. ``None`` runs every
    enabled discovery query once. Allocation does not look at fit scores.
    """
    await init_db()
    targets = targets or load_targets()
    profile = profile or load_profile()
    summary = IngestSummary()
    plan = build_discovery_plan(targets, capacity=search_capacity)
    log_discovery_plan(plan)
    provenance = {
        search.query: (search.family_id, search.bucket_id) for search in plan.searches
    }
    jobspy_observations: list[SearchObservation] = []
    workday_observations: list[SearchObservation] = []

    tasks: list[asyncio.Task[list[RawPosting]]] = []
    labels: list[str] = []

    if include_jobspy and plan.jobspy_sites and plan.searches:
        tasks.append(
            asyncio.create_task(
                fetch_linkedin_indeed(
                    targets,
                    profile=profile,
                    plan=plan,
                    observations=jobspy_observations,
                ),
                name="jobspy",
            )
        )
        labels.append("jobspy")

    active_tenants = targets.active_workday_tenants()
    if include_workday and plan.workday_enabled and active_tenants and plan.searches:
        tasks.append(
            asyncio.create_task(
                fetch_all_workday(
                    active_tenants,
                    default_search_terms=[search.query for search in plan.searches],
                    hours_old=targets.search.hours_old,
                    provenance=provenance,
                    observations=workday_observations,
                ),
                name="workday",
            )
        )
        labels.append("workday")

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
    raw: list[RawPosting] = []
    for label, result in zip(labels, results, strict=True):
        if isinstance(result, BaseException):
            msg = f"{label}: {result}"
            summary.errors.append(msg)
            log.warning("ingestion_source_failed", source=label, error=str(result))
            _mark_source_failed(
                plan,
                label,
                str(result)[:200],
                jobspy_observations,
                workday_observations,
                tuple(tenant.name for tenant in active_tenants),
            )
            continue
        raw.extend(result)
        summary.by_source[label] = len(result)

    postings = _dedupe(raw)
    summary.fetched = len(postings)

    # Ensure clean descriptions before filtering
    for posting in postings:
        posting.ensure_clean_description()

    role_client = await _load_role_client()
    async with session_scope() as session:
        for posting in postings:
            result = evaluate(posting, profile)
            if result.passed:
                job = to_job(posting, status=Status.discovered)
                summary.discovered += 1
            else:
                job = to_job(
                    posting,
                    status=Status.filtered_out,
                    justification=[result.reason or "filtered"],
                )
                summary.filtered_out += 1

            await _apply_role_classification(session, job, role_client)
            await upsert_job(session, job)
            summary.upserted += 1

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
    )
    return summary
