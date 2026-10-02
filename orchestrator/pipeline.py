"""Full pipeline: ingest, score, shortlist, resume, suggest, prep, apply, reviews."""

from __future__ import annotations

import contextvars
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
_current_run: contextvars.ContextVar[int | None] = contextvars.ContextVar(
    "pipeline_run_id",
    default=None,
)

# Module-level aliases so tests can monkeypatch orchestrator.pipeline.*
_run_ingestion = run_ingestion
_score_pending = score_pending
_prepare_resumes = prepare_pending


async def _shortlist_stage() -> dict[str, Any]:
    """Move the current staged selection into pending_review."""
    from scorer.shortlist import apply_shortlist

    result = await apply_shortlist()
    return {
        "selected": result.selected,
        "considered": result.considered,
        "already_pending": result.already_pending,
        "selected_ids": list(result.selected_ids),
    }


async def _portfolio_stage() -> dict[str, Any]:
    """Allocate apply capacity among staged candidates. Does not change status."""
    from scorer.application_portfolio import apply_portfolio

    result = await apply_portfolio()
    return {
        "allocated": result.allocated,
        "deferred": result.deferred,
        "allocated_ids": list(result.allocated_ids),
    }


def _allocated_ids(summary: PipelineSummary) -> list[int]:
    """Staged ids the portfolio layer just allocated. Empty when that stage did not run."""
    payload = summary.stages.get("portfolio")
    if not isinstance(payload, dict):
        return []
    raw = payload.get("allocated_ids") or []
    return [item for item in raw if isinstance(item, int)]


def _selected_ids(summary: PipelineSummary) -> list[int]:
    """Job ids the shortlist just moved into review. Empty when that stage did not run."""
    payload = summary.stages.get("shortlist")
    if not isinstance(payload, dict):
        return []
    raw = payload.get("selected_ids") or []
    return [item for item in raw if isinstance(item, int)]


async def _prepare_shortlisted_resumes() -> Any:
    """Prepare resumes for the review queue, not for every staged job."""
    from core.db import Status

    return await _prepare_resumes(status=Status.pending_review)


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


async def _generate_suggestions_stage(job_ids: list[int] | None = None) -> dict[str, int]:
    """Create skill suggestions for the jobs this run placed in review.

    Leftover staged jobs are not included. Passing no ids generates nothing.
    """
    from core.db import get_suggestions_for_job, init_db, session_scope

    await init_db()
    settings = get_settings()
    if not settings.enable_suggestions:
        return {"generated": 0, "skipped": 0}

    generated = 0
    skipped = 0
    for job_id in job_ids or []:
        async with session_scope() as session:
            existing = await get_suggestions_for_job(session, job_id)
        if existing:
            skipped += 1
            continue
        try:
            await generate_suggestions_for_job(job_id)
            generated += 1
        except Exception as exc:
            log.warning("pipeline_suggest_job_failed", job_id=job_id, error=str(exc))
    return {"generated": generated, "skipped": skipped}


async def _benchmark_tier_one_stage(job_ids: list[int] | None = None) -> dict[str, int]:
    """Benchmark Tier-1 jobs from this run's shortlist. Not the leftover staged pool."""
    from benchmark.engine import run_benchmark
    from core.db import Tier, get_job_by_id, init_db, session_scope

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
        jobs = []
        for job_id in job_ids or []:
            job = await get_job_by_id(session, job_id)
            if job is not None:
                jobs.append(job)

    tier_one = [j for j in jobs if j.tier == Tier.one and j.id is not None][:10]
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
    run_id = await _safe_open_run()
    token = _current_run.set(run_id)

    async def _prep_stage() -> Any:
        # Prep already loads these ids without a status filter, so a job that
        # scoring just wrote and shortlist then moved is still included.
        scoring = summary.stages.get("scoring")
        raw_ids = getattr(scoring, "scored_ids", []) or []
        return await _send_prep_pack(job_ids=list(raw_ids))

    async def _suggest_stage() -> dict[str, int]:
        return await _generate_suggestions_stage(_selected_ids(summary))

    async def _benchmark_stage() -> dict[str, int]:
        return await _benchmark_tier_one_stage(_selected_ids(summary))

    async def _apply_allocated() -> Any:
        return await _apply_pending(job_ids=_allocated_ids(summary))

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
        run_id=run_id,
        enable_apply=do_apply,
        enable_reviews=do_reviews,
        enable_prep_pack=do_prep,
        enable_suggestions=do_suggest,
        enable_benchmark=do_benchmark,
    )
    log.info("monitoring_run_started", run_id=run_id)

    try:
        await _run_stage(summary, "ingestion", _run_ingestion)
        await _run_stage(summary, "scoring", _score_pending)
        await _run_stage(summary, "shortlist", _shortlist_stage)
        await _run_stage(summary, "resume", _prepare_shortlisted_resumes)

        if do_suggest:
            await _run_stage(summary, "suggest_generate", _suggest_stage)
            if do_suggest_send:
                await _run_stage(summary, "suggest_send", _send_pending_suggestions)
            else:
                await _note_skipped(summary, "suggest_send")
        else:
            await _note_skipped(summary, "suggest_generate")
            await _note_skipped(summary, "suggest_send")

        if do_benchmark:
            await _run_stage(summary, "benchmark", _benchmark_stage)
        else:
            await _note_skipped(summary, "benchmark")

        if do_prep:
            await _run_stage(summary, "prep", _prep_stage)
        else:
            await _note_skipped(summary, "prep")
            log.info("pipeline_stage_skipped", stage="prep")

        if do_apply:
            await _run_stage(summary, "portfolio", _portfolio_stage)
            await _run_stage(summary, "apply", _apply_allocated)
        else:
            await _note_skipped(summary, "portfolio")
            await _note_skipped(summary, "apply")
            log.info("pipeline_stage_skipped", stage="portfolio")
            log.info("pipeline_stage_skipped", stage="apply")

        if do_reviews:
            await _run_stage(summary, "reviews", _send_pending_reviews)
            await _run_stage(summary, "outcome_prompts", _send_outcome_prompts)
            await _run_stage(summary, "alerts", _send_pending_alerts)
        else:
            await _note_skipped(summary, "reviews")
            await _note_skipped(summary, "outcome_prompts")
            await _note_skipped(summary, "alerts")
            log.info("pipeline_stage_skipped", stage="reviews")
            log.info("pipeline_stage_skipped", stage="outcome_prompts")
            log.info("pipeline_stage_skipped", stage="alerts")
    except Exception:
        await _safe_close_run(run_id, summary, status="failed")
        _current_run.reset(token)
        raise

    summary.duration_ms = int((time.perf_counter() - started) * 1000)
    status = "partial" if summary.stage_errors else "succeeded"
    await _safe_close_run(run_id, summary, status=status)
    _current_run.reset(token)
    log.info(
        "pipeline_complete",
        run_id=run_id,
        duration_ms=summary.duration_ms,
        errors=list(summary.stage_errors.keys()),
        skipped=summary.skipped,
    )
    log.info(
        "monitoring_run_completed",
        run_id=run_id,
        status=status,
        duration_ms=summary.duration_ms,
        error_count=len(summary.stage_errors),
    )
    return summary


async def _note_skipped(summary: PipelineSummary, name: str) -> None:
    summary.skipped.append(name)
    run_id = _current_run.get()
    if run_id is None:
        return
    try:
        from orchestrator.monitoring import record_skipped_stage

        await record_skipped_stage(run_id, name)
    except Exception as exc:
        log.warning("monitoring_stage_record_failed", stage=name, error=str(exc)[:200])


async def _run_stage(
    summary: PipelineSummary,
    name: str,
    coro_factory: Any,
) -> None:
    stage_started = time.perf_counter()
    stage_id = await _safe_open_stage(name)
    log.info("monitoring_stage_started", run_id=_current_run.get(), stage=name)
    try:
        result = await coro_factory()
        summary.stages[name] = result
        duration_ms = int((time.perf_counter() - stage_started) * 1000)
        log.info("pipeline_stage_ok", stage=name, duration_ms=duration_ms)
        log.info(
            "monitoring_stage_completed",
            run_id=_current_run.get(),
            stage=name,
            status="succeeded",
            duration_ms=duration_ms,
        )
        await _safe_close_stage(stage_id, status="succeeded", result=result)
    except Exception as exc:
        summary.stage_errors[name] = str(exc)
        duration_ms = int((time.perf_counter() - stage_started) * 1000)
        log.warning(
            "pipeline_stage_failed",
            stage=name,
            error=str(exc),
            duration_ms=duration_ms,
        )
        log.warning(
            "monitoring_stage_failed",
            run_id=_current_run.get(),
            stage=name,
            status="failed",
            duration_ms=duration_ms,
            error=str(exc)[:200],
        )
        await _safe_close_stage(stage_id, status="failed", error=str(exc))


async def _safe_open_run() -> int | None:
    try:
        from orchestrator.monitoring import interrupt_stale_runs

        await interrupt_stale_runs()
    except Exception as exc:
        log.warning("monitoring_run_record_failed", error=str(exc)[:200])
    try:
        from orchestrator.monitoring import open_pipeline_run

        return await open_pipeline_run()
    except Exception as exc:
        log.warning("monitoring_run_record_failed", error=str(exc)[:200])
        return None


async def _safe_close_run(run_id: int | None, summary: PipelineSummary, *, status: str) -> None:
    if run_id is None:
        return
    try:
        from orchestrator.monitoring import close_pipeline_run

        await close_pipeline_run(
            run_id,
            status=status,
            error_count=len(summary.stage_errors),
            skipped_count=len(summary.skipped),
        )
    except Exception as exc:
        log.warning("monitoring_run_record_failed", run_id=run_id, error=str(exc)[:200])


async def _safe_open_stage(name: str) -> int | None:
    run_id = _current_run.get()
    if run_id is None:
        return None
    try:
        from orchestrator.monitoring import open_stage_run

        return await open_stage_run(run_id, name)
    except Exception as exc:
        log.warning("monitoring_stage_record_failed", stage=name, error=str(exc)[:200])
        return None


async def _safe_close_stage(
    stage_id: int | None,
    *,
    status: str,
    result: object = None,
    error: str | None = None,
) -> None:
    if stage_id is None:
        return
    try:
        from orchestrator.monitoring import close_stage_run, stage_counters

        await close_stage_run(
            stage_id,
            status=status,
            error=error,
            counters=stage_counters(result),
        )
    except Exception as exc:
        log.warning("monitoring_stage_record_failed", error=str(exc)[:200])
