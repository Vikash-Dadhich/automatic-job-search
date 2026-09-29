"""Full pipeline: ingest, score, resume, suggest, prep, apply, reviews, outcomes, alerts."""

from __future__ import annotations

import os
import time
from dataclasses import dataclass, field
from typing import Any

import structlog

from automation.runner import apply_pending
from bot.alerts import send_pending_alerts
from bot.outcomes import send_pending_outcome_prompts
from bot.prep import send_prep_pack
from bot.review import send_pending_reviews
from bot.suggest import send_pending_suggestions
from config.diagnostics import effective_baseline, write_effective_baseline
from config.settings import get_settings
from resume.compiler import prepare_pending
from resume.diff import generate_suggestions_for_job
from scorer.engine import score_pending
from scraper.ingest import run_ingestion

log = structlog.get_logger(__name__)

# Module-level aliases so tests can monkeypatch orchestrator.pipeline.*
_run_ingestion = run_ingestion
_score_pending = score_pending
_prepare_resumes = prepare_pending
_send_prep_pack = send_prep_pack
_apply_pending = apply_pending
_send_pending_reviews = send_pending_reviews
_send_outcome_prompts = send_pending_outcome_prompts
_send_pending_alerts = send_pending_alerts
_send_pending_suggestions = send_pending_suggestions


@dataclass
class PipelineSummary:
    """Aggregated results from one full pipeline run."""

    stages: dict[str, Any] = field(default_factory=dict)
    stage_errors: dict[str, str] = field(default_factory=dict)
    skipped: list[str] = field(default_factory=list)
    duration_ms: int = 0

    @property
    def ok(self) -> bool:
        return not self.stage_errors


async def _generate_suggestions_stage() -> dict[str, int]:
    """Create skill suggestions for staged jobs that lack pending rows."""
    from core.db import Status, get_jobs_by_status, get_suggestions_for_job, init_db, session_scope

    await init_db()
    settings = get_settings()
    if not settings.enable_suggestions:
        return {"generated": 0, "skipped": 0}

    async with session_scope() as session:
        jobs = await get_jobs_by_status(session, Status.staged, limit=20)

    generated = 0
    skipped = 0
    for job in jobs:
        if job.id is None:
            continue
        async with session_scope() as session:
            existing = await get_suggestions_for_job(session, job.id)
        if existing:
            skipped += 1
            continue
        try:
            await generate_suggestions_for_job(job.id)
            generated += 1
        except Exception as exc:
            log.warning("pipeline_suggest_job_failed", job_id=job.id, error=str(exc))
    return {"generated": generated, "skipped": skipped}


async def _benchmark_tier_one_stage() -> dict[str, int]:
    """Auto-discover + benchmark Tier-1 staged jobs (LinkedIn scrape, gated)."""
    from benchmark.engine import run_benchmark
    from core.db import Status, Tier, get_jobs_by_status, init_db, session_scope

    await init_db()
    settings = get_settings()
    if not settings.enable_benchmark:
        return {"benchmarked": 0, "skipped": 0}
    if not settings.enable_linkedin_scrape:
        log.warning(
            "pipeline_benchmark_needs_linkedin_scrape",
            hint="Set ENABLE_LINKEDIN_SCRAPE=true and save a LinkedIn session",
        )
        return {"benchmarked": 0, "skipped": 0}

    async with session_scope() as session:
        jobs = await get_jobs_by_status(session, Status.staged, limit=10)

    tier_one = [j for j in jobs if j.tier == Tier.one and j.id is not None]
    benchmarked = 0
    skipped = 0
    for job in tier_one:
        assert job.id is not None
        try:
            summary = await run_benchmark(job.id, auto_discover=True)
            if summary.report is not None:
                benchmarked += 1
            else:
                skipped += 1
        except Exception as exc:
            log.warning("pipeline_benchmark_job_failed", job_id=job.id, error=str(exc)[:200])
            skipped += 1
    return {"benchmarked": benchmarked, "skipped": skipped}


async def run_pipeline(
    *,
    enable_apply: bool | None = None,
    enable_reviews: bool | None = None,
    enable_prep_pack: bool | None = None,
    enable_suggestions: bool | None = None,
    enable_benchmark: bool | None = None,
) -> PipelineSummary:
    """Run all pipeline stages sequentially with per-stage isolation.

    A failure in one stage is logged and recorded; later stages still run.
    """
    settings = get_settings()
    do_apply = settings.enable_apply if enable_apply is None else enable_apply
    do_reviews = settings.enable_reviews if enable_reviews is None else enable_reviews
    do_prep = (
        settings.enable_prep_pack if enable_prep_pack is None else enable_prep_pack
    )
    do_suggest = (
        settings.enable_suggestions if enable_suggestions is None else enable_suggestions
    )
    do_benchmark = (
        settings.enable_benchmark if enable_benchmark is None else enable_benchmark
    )
    # Prep packs / suggestions are delivered via Telegram — require reviews toggle too
    do_prep = do_prep and do_reviews
    do_suggest_send = do_suggest and do_reviews

    summary = PipelineSummary()
    started = time.perf_counter()

    async def _prep_stage() -> Any:
        scoring = summary.stages.get("scoring")
        raw_ids = getattr(scoring, "scored_ids", []) or []
        return await _send_prep_pack(job_ids=list(raw_ids))

    baseline = effective_baseline(settings)
    baseline_path = None
    if os.environ.get("PYTEST_CURRENT_TEST") is None:
        try:
            baseline_path = write_effective_baseline()
        except OSError as exc:
            log.warning("pipeline_baseline_write_failed", error=str(exc))
    log.info(
        "pipeline_baseline",
        path=str(baseline_path) if baseline_path else None,
        **baseline,
    )
    if not settings.internship_only:
        log.warning(
            "pipeline_internship_only_off",
            hint=(
                "Full-time titles will be ingested. "
                "Production sets INTERNSHIP_ONLY=true."
            ),
        )

    log.info(
        "pipeline_start",
        enable_apply=do_apply,
        enable_reviews=do_reviews,
        enable_prep_pack=do_prep,
        enable_suggestions=do_suggest,
        enable_benchmark=do_benchmark,
    )

    await _run_stage(summary, "ingestion", _run_ingestion)
    await _run_stage(summary, "scoring", _score_pending)
    await _run_stage(summary, "resume", _prepare_resumes)

    if do_suggest:
        await _run_stage(summary, "suggest_generate", _generate_suggestions_stage)
        if do_suggest_send:
            await _run_stage(summary, "suggest_send", _send_pending_suggestions)
        else:
            summary.skipped.append("suggest_send")
    else:
        summary.skipped.append("suggest_generate")
        summary.skipped.append("suggest_send")

    if do_benchmark:
        await _run_stage(summary, "benchmark", _benchmark_tier_one_stage)
    else:
        summary.skipped.append("benchmark")

    if do_prep:
        await _run_stage(summary, "prep", _prep_stage)
    else:
        summary.skipped.append("prep")
        log.info("pipeline_stage_skipped", stage="prep")

    if do_apply:
        await _run_stage(summary, "apply", _apply_pending)
    else:
        summary.skipped.append("apply")
        log.info("pipeline_stage_skipped", stage="apply")

    if do_reviews:
        await _run_stage(summary, "reviews", _send_pending_reviews)
        await _run_stage(summary, "outcome_prompts", _send_outcome_prompts)
        await _run_stage(summary, "alerts", _send_pending_alerts)
    else:
        summary.skipped.append("reviews")
        summary.skipped.append("outcome_prompts")
        summary.skipped.append("alerts")
        log.info("pipeline_stage_skipped", stage="reviews")
        log.info("pipeline_stage_skipped", stage="outcome_prompts")
        log.info("pipeline_stage_skipped", stage="alerts")

    summary.duration_ms = int((time.perf_counter() - started) * 1000)
    log.info(
        "pipeline_complete",
        duration_ms=summary.duration_ms,
        errors=list(summary.stage_errors.keys()),
        skipped=summary.skipped,
    )
    return summary


async def _run_stage(
    summary: PipelineSummary,
    name: str,
    coro_factory: Any,
) -> None:
    stage_started = time.perf_counter()
    try:
        result = await coro_factory()
        summary.stages[name] = result
        duration_ms = int((time.perf_counter() - stage_started) * 1000)
        log.info("pipeline_stage_ok", stage=name, duration_ms=duration_ms)
    except Exception as exc:
        summary.stage_errors[name] = str(exc)
        duration_ms = int((time.perf_counter() - stage_started) * 1000)
        log.warning(
            "pipeline_stage_failed",
            stage=name,
            error=str(exc),
            duration_ms=duration_ms,
        )
