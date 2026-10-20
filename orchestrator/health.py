"""Operational snapshot. It does not score, rank, or apply to jobs."""

from __future__ import annotations

from datetime import datetime, timedelta

import structlog
from sqlmodel import col, select

from core.db import PipelineRun, PipelineStageRun, Status, _as_utc, _utcnow, init_db, session_scope
from orchestrator.monitoring import (
    count_jobs_by_status,
    count_stale_jobs,
    database_reachable,
    interrupt_stale_runs,
    load_monitoring_config,
    validate_operational_config,
)

log = structlog.get_logger(__name__)


async def get_health_report(*, now: datetime | None = None) -> dict[str, object]:
    """Read operational state. Optional pieces that fail become explicit unknowns."""
    moment = _as_utc(now) or _utcnow()
    config_errors = validate_operational_config()
    if config_errors:
        log.warning("monitoring_config_invalid", errors=config_errors)
    database_ok = await database_reachable()
    thresholds = _thresholds()
    interrupted = 0
    if database_ok:
        try:
            await init_db()
            interrupted = await interrupt_stale_runs(now=moment)
            if interrupted:
                log.warning("monitoring_run_interrupted", count=interrupted)
        except Exception as exc:
            log.warning("monitoring_stale_check_failed", error=str(exc)[:200])
    runs: list[PipelineRun] = []
    stages: list[PipelineStageRun] = []
    backlog: dict[str, int] = {}
    stale: dict[str, int | None] = {
        "pending_review": None,
        "manual_review": None,
        "staged": None,
        "error": None,
    }
    recent_stage_failures = 0
    if database_ok:
        try:
            await init_db()
            async with session_scope() as session:
                result = await session.exec(
                    select(PipelineRun).order_by(col(PipelineRun.id).desc()).limit(20)
                )
                runs = list(result.all())
            if runs:
                stages = await _stages(runs[0].id)
            backlog = await count_jobs_by_status()
            stale = {
                "pending_review": await count_stale_jobs(
                    Status.pending_review,
                    older_than=moment - timedelta(days=thresholds["stale_pending_review_days"]),
                ),
                "manual_review": await count_stale_jobs(
                    Status.manual_review,
                    older_than=moment - timedelta(days=thresholds["stale_manual_review_days"]),
                ),
                "staged": await count_stale_jobs(
                    Status.staged,
                    older_than=moment - timedelta(days=thresholds["stale_staged_days"]),
                ),
                "error": backlog.get("error", 0),
            }
            recent_stage_failures = await _recent_failures(
                moment - timedelta(hours=thresholds["recent_error_hours"])
            )
        except Exception as exc:
            log.warning("monitoring_health_query_failed", error=str(exc)[:200])
            database_ok = False
    completed = [run for run in runs if run.status != "running"]
    latest = runs[0] if runs else None
    latest_completed = completed[0] if completed else None
    window_start = moment - timedelta(hours=thresholds["recent_error_hours"])
    interrupted_recent = sum(
        1
        for run in runs
        if run.status == "interrupted" and _as_utc(run.started_at) is not None
        and (_as_utc(run.started_at) or moment) >= window_start
    )
    repeated = _repeated_failures(completed, thresholds["critical_repeated_failures"])
    status = _status(
        database_ok=database_ok,
        config_errors=config_errors,
        interrupted_recent=interrupted_recent,
        critical_stale_runs=thresholds["critical_stale_runs"],
        repeated_failures=repeated,
        latest_completed=latest_completed.status if latest_completed else None,
        recent_stage_failures=recent_stage_failures,
        manual_review=backlog.get("manual_review", 0),
        manual_review_backlog=thresholds["manual_review_backlog"],
        stale=stale,
    )
    report: dict[str, object] = {
        "status": status,
        "database_ok": database_ok,
        "config_errors": config_errors,
        "latest_run": _run_view(latest),
        "latest_completed_run": _run_view(latest_completed),
        "stage_failures": [row.stage for row in stages if row.status == "failed"],
        "interrupted_recent": interrupted_recent,
        "recent_stage_failures": recent_stage_failures,
        "backlog": backlog,
        "stale": stale,
        "monitoring_version": "phase18-v1",
    }
    log.info("monitoring_health_completed", status=status, database_ok=database_ok)
    return report


def format_health_report(report: dict[str, object]) -> str:
    """Compact text. Counts and statuses only."""
    latest = report.get("latest_run")
    completed = report.get("latest_completed_run")
    raw_failures = report.get("stage_failures")
    failures = raw_failures if isinstance(raw_failures, list) else []
    raw_backlog = report.get("backlog")
    backlog = raw_backlog if isinstance(raw_backlog, dict) else {}
    raw_stale = report.get("stale")
    stale = raw_stale if isinstance(raw_stale, dict) else {}
    raw_errors = report.get("config_errors")
    config_errors = raw_errors if isinstance(raw_errors, list) else []
    lines = [
        f"status: {report.get('status')}",
        f"database: {'ok' if report.get('database_ok') else 'unavailable'}",
        f"config: {'ok' if not config_errors else 'invalid'}",
        f"latest_run: {_brief(latest)}",
        f"latest_completed: {_brief(completed)}",
        f"stage_failures: {', '.join(str(item) for item in failures) or 'none'}",
        f"interrupted_recent: {report.get('interrupted_recent')}",
        f"recent_stage_failures: {report.get('recent_stage_failures')}",
        "backlog: "
        + ", ".join(f"{name}={backlog.get(name, 0)}" for name in (
            "discovered",
            "staged",
            "pending_review",
            "manual_review",
            "submitted",
            "error",
            "filtered_out",
            "ignored",
        )),
        "stale: "
        + ", ".join(f"{name}={stale.get(name)}" for name in (
            "pending_review",
            "manual_review",
            "staged",
            "error",
        )),
    ]
    if config_errors:
        lines.extend(f"config_error: {item}" for item in config_errors)
    return "\n".join(lines)


def _brief(run: object) -> str:
    if not isinstance(run, dict):
        return "none"
    return (
        f"id={run.get('id')} status={run.get('status')} "
        f"duration_ms={run.get('duration_ms')}"
    )


def _run_view(run: PipelineRun | None) -> dict[str, object] | None:
    if run is None:
        return None
    return {
        "id": run.id,
        "run_key": run.run_key,
        "status": run.status,
        "started_at": None if run.started_at is None else run.started_at.isoformat(),
        "finished_at": None if run.finished_at is None else run.finished_at.isoformat(),
        "duration_ms": run.duration_ms,
        "error_count": run.error_count,
        "skipped_count": run.skipped_count,
        "monitoring_version": run.monitoring_version,
    }


def _thresholds() -> dict[str, int]:
    try:
        return dict(load_monitoring_config()["monitoring"])
    except Exception:
        return {
            "stale_run_minutes": 180,
            "recent_error_hours": 24,
            "stale_pending_review_days": 14,
            "stale_manual_review_days": 7,
            "stale_staged_days": 21,
            "critical_stale_runs": 1,
            "critical_repeated_failures": 3,
            "manual_review_backlog": 25,
        }


def _repeated_failures(runs: list[PipelineRun], needed: int) -> bool:
    if needed <= 0 or len(runs) < needed:
        return False
    return all(run.status == "failed" for run in runs[:needed])


def _status(
    *,
    database_ok: bool,
    config_errors: list[str],
    interrupted_recent: int,
    critical_stale_runs: int,
    repeated_failures: bool,
    latest_completed: str | None,
    recent_stage_failures: int,
    manual_review: int,
    manual_review_backlog: int,
    stale: dict[str, int | None],
) -> str:
    if not database_ok or config_errors or repeated_failures:
        return "unhealthy"
    if interrupted_recent >= critical_stale_runs:
        return "unhealthy"
    stale_hits = any(isinstance(value, int) and value > 0 for value in stale.values())
    if (
        latest_completed in {"partial", "failed", "interrupted"}
        or recent_stage_failures > 0
        or manual_review >= manual_review_backlog
        or stale_hits
    ):
        return "degraded"
    return "healthy"


async def _stages(run_id: int | None) -> list[PipelineStageRun]:
    if run_id is None:
        return []
    async with session_scope() as session:
        result = await session.exec(
            select(PipelineStageRun)
            .where(col(PipelineStageRun.pipeline_run_id) == run_id)
            .order_by(col(PipelineStageRun.id))
        )
        return list(result.all())


async def _recent_failures(cutoff: datetime) -> int:
    async with session_scope() as session:
        result = await session.exec(
            select(PipelineStageRun).where(col(PipelineStageRun.status) == "failed")
        )
        count = 0
        for row in result.all():
            finished = _as_utc(row.finished_at)
            if finished is not None and finished >= cutoff:
                count += 1
        return count
