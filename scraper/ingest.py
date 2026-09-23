"""Ingestion orchestrator: fetch → clean → filter → upsert."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass, field

import structlog

from config.profile import Profile, load_profile
from config.targets import Targets, load_targets
from core.db import Status, init_db, session_scope, upsert_job
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
) -> IngestSummary:
    """Run one full discovery cycle and persist results."""
    await init_db()
    targets = targets or load_targets()
    profile = profile or load_profile()
    summary = IngestSummary()

    tasks: list[asyncio.Task[list[RawPosting]]] = []
    labels: list[str] = []

    if include_jobspy and targets.search.terms:
        tasks.append(
            asyncio.create_task(
                fetch_linkedin_indeed(targets, profile=profile),
                name="jobspy",
            )
        )
        labels.append("jobspy")

    active_tenants = targets.active_workday_tenants()
    if include_workday and active_tenants:
        tasks.append(
            asyncio.create_task(
                fetch_all_workday(
                    active_tenants,
                    default_search_terms=targets.search.terms,
                    hours_old=targets.search.hours_old,
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
        return summary

    results = await asyncio.gather(*tasks, return_exceptions=True)
    raw: list[RawPosting] = []
    for label, result in zip(labels, results, strict=True):
        if isinstance(result, BaseException):
            msg = f"{label}: {result}"
            summary.errors.append(msg)
            log.warning("ingestion_source_failed", source=label, error=str(result))
            continue
        raw.extend(result)
        summary.by_source[label] = len(result)

    postings = _dedupe(raw)
    summary.fetched = len(postings)

    # Ensure clean descriptions before filtering
    for posting in postings:
        posting.ensure_clean_description()

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

            await upsert_job(session, job)
            summary.upserted += 1

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
