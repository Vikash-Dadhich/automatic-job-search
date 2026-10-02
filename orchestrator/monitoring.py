"""Durable pipeline history. A failure here must not stop the pipeline."""

from __future__ import annotations

import hashlib
import json
import uuid
from datetime import datetime, timedelta
from functools import lru_cache
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

import yaml
from sqlmodel import col, func, select

from config.diagnostics import effective_config_hash
from config.settings import get_settings
from core.db import (
    Job,
    PipelineRun,
    PipelineStageRun,
    Status,
    _as_utc,
    _utcnow,
    get_engine,
    init_db,
    session_scope,
)
from orchestrator.scheduler import parse_hhmm

MONITORING_VERSION = "phase18-v1"
CONFIG_PATH = Path(__file__).resolve().parent.parent / "config" / "monitoring.yaml"
_COUNTERS = {
    "fetched",
    "discovered",
    "filtered_out",
    "upserted",
    "scored",
    "staged",
    "errors",
    "skipped",
    "vector_rejected",
    "generated",
    "selected",
    "considered",
    "already_pending",
    "allocated",
    "deferred",
    "blocked_company",
    "blocked_capacity",
    "applied",
    "pending_review",
    "manual_review",
    "blackout_skipped",
    "sent",
    "benchmarked",
}


def _require_int(name: str, value: object, *, lower: int, upper: int) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < lower or value > upper:
        raise ValueError(f"{name} must be an integer from {lower} through {upper}")
    return value


def _validate(raw: object) -> dict[str, Any]:
    if not isinstance(raw, dict) or raw.get("version") != MONITORING_VERSION:
        raise ValueError(f"monitoring version must be {MONITORING_VERSION}")
    block = raw.get("monitoring")
    if not isinstance(block, dict):
        raise ValueError("monitoring config must contain a monitoring mapping")
    keys = {
        "stale_run_minutes",
        "recent_error_hours",
        "stale_pending_review_days",
        "stale_manual_review_days",
        "stale_staged_days",
        "critical_stale_runs",
        "critical_repeated_failures",
        "manual_review_backlog",
    }
    if set(block) != keys:
        raise ValueError("monitoring config must set each operational threshold once")
    return {
        "version": MONITORING_VERSION,
        "monitoring": {
            name: _require_int(name, block[name], lower=1, upper=100000) for name in keys
        },
    }


@lru_cache
def load_monitoring_config(path: str | None = None) -> dict[str, Any]:
    target = Path(path) if path else CONFIG_PATH
    with target.open(encoding="utf-8") as handle:
        raw: Any = yaml.safe_load(handle)
    return _validate(raw)


def monitoring_config_hash(config: dict[str, Any] | None = None) -> str:
    loaded = config if config is not None else load_monitoring_config()
    raw = json.dumps(loaded, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(raw.encode()).hexdigest()


def operational_config_hash() -> str:
    payload = {
        "effective": effective_config_hash(),
        "monitoring": monitoring_config_hash(),
    }
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(raw.encode()).hexdigest()


def validate_operational_config() -> list[str]:
    """Actionable configuration problems. Empty means the checked settings are usable."""
    errors: list[str] = []
    settings = get_settings()
    try:
        ZoneInfo(settings.timezone)
    except Exception:
        errors.append(f"timezone {settings.timezone!r} is not a known zone")
    if not settings.schedule_times:
        errors.append("schedule_times is empty")
    for value in settings.schedule_times:
        try:
            parse_hhmm(value)
        except ValueError:
            errors.append(f"schedule time {value!r} is not HH:MM")
    if not (settings.database_url or "").strip():
        errors.append("database_url is empty")
    try:
        load_monitoring_config()
    except Exception as exc:
        errors.append(f"monitoring config: {exc}")
    return errors


def stage_counters(result: object) -> dict[str, int]:
    """Small integers already returned by a stage. Lists and text are ignored."""
    raw: dict[str, object] = {}
    if isinstance(result, dict):
        raw = dict(result)
    elif result is not None:
        raw = {name: getattr(result, name) for name in _COUNTERS if hasattr(result, name)}
    counters: dict[str, int] = {}
    for name, value in raw.items():
        if name in _COUNTERS and isinstance(value, int) and not isinstance(value, bool):
            counters[name] = value
    return counters


def _moment(value: datetime | None) -> datetime:
    return _as_utc(value) or _utcnow()


async def open_pipeline_run(
    *,
    now: datetime | None = None,
    run_key: str | None = None,
) -> int | None:
    await init_db()
    started = _moment(now)
    run = PipelineRun(
        run_key=run_key or uuid.uuid4().hex,
        status="running",
        started_at=started,
        config_hash=operational_config_hash(),
        monitoring_version=MONITORING_VERSION,
    )
    async with session_scope() as session:
        session.add(run)
        await session.flush()
        assert run.id is not None
        return run.id


async def close_pipeline_run(
    run_id: int,
    *,
    status: str,
    now: datetime | None = None,
    error_count: int = 0,
    skipped_count: int = 0,
) -> None:
    finished = _moment(now)
    async with session_scope() as session:
        statement = select(PipelineRun).where(col(PipelineRun.id) == run_id)
        result = await session.exec(statement)
        run = result.first()
        if run is None:
            return
        started = _as_utc(run.started_at) or finished
        run.status = status
        run.finished_at = finished
        run.duration_ms = max(0, int((finished - started).total_seconds() * 1000))
        run.error_count = error_count
        run.skipped_count = skipped_count
        session.add(run)


async def open_stage_run(
    run_id: int,
    stage: str,
    *,
    now: datetime | None = None,
) -> int | None:
    started = _moment(now)
    row = PipelineStageRun(
        pipeline_run_id=run_id,
        stage=stage,
        status="running",
        started_at=started,
        counters={},
    )
    async with session_scope() as session:
        session.add(row)
        await session.flush()
        assert row.id is not None
        return row.id


async def close_stage_run(
    stage_id: int,
    *,
    status: str,
    now: datetime | None = None,
    error: str | None = None,
    counters: dict[str, int] | None = None,
) -> None:
    finished = _moment(now)
    async with session_scope() as session:
        statement = select(PipelineStageRun).where(col(PipelineStageRun.id) == stage_id)
        result = await session.exec(statement)
        row = result.first()
        if row is None:
            return
        started = _as_utc(row.started_at) or finished
        row.status = status
        row.finished_at = finished
        row.duration_ms = max(0, int((finished - started).total_seconds() * 1000))
        if error:
            row.error = error.replace("\n", " ")[:500]
        if counters is not None:
            row.counters = dict(counters)
        session.add(row)


async def record_skipped_stage(run_id: int, stage: str, *, now: datetime | None = None) -> None:
    moment = _moment(now)
    row = PipelineStageRun(
        pipeline_run_id=run_id,
        stage=stage,
        status="skipped",
        started_at=moment,
        finished_at=moment,
        duration_ms=0,
        counters={},
    )
    async with session_scope() as session:
        session.add(row)


async def interrupt_stale_runs(
    *,
    now: datetime | None = None,
    stale_minutes: int | None = None,
) -> int:
    """Mark old running rows interrupted. A run newer than the threshold stays running."""
    moment = _moment(now)
    minutes = stale_minutes
    if minutes is None:
        minutes = int(load_monitoring_config()["monitoring"]["stale_run_minutes"])
    cutoff = moment - timedelta(minutes=minutes)
    async with session_scope() as session:
        statement = select(PipelineRun).where(col(PipelineRun.status) == "running")
        result = await session.exec(statement)
        changed = 0
        for run in result.all():
            started = _as_utc(run.started_at)
            if started is None or started >= cutoff:
                continue
            run.status = "interrupted"
            run.finished_at = moment
            run.duration_ms = max(0, int((moment - started).total_seconds() * 1000))
            session.add(run)
            changed += 1
        return changed


async def list_pipeline_runs(limit: int = 20) -> list[PipelineRun]:
    await init_db()
    async with session_scope() as session:
        statement = select(PipelineRun).order_by(col(PipelineRun.id).desc()).limit(limit)
        result = await session.exec(statement)
        return list(result.all())


async def list_stage_runs(run_id: int) -> list[PipelineStageRun]:
    await init_db()
    async with session_scope() as session:
        statement = (
            select(PipelineStageRun)
            .where(col(PipelineStageRun.pipeline_run_id) == run_id)
            .order_by(col(PipelineStageRun.id))
        )
        result = await session.exec(statement)
        return list(result.all())


async def count_jobs_by_status() -> dict[str, int]:
    await init_db()
    counts = {status.value: 0 for status in Status}
    async with session_scope() as session:
        statement = select(Job.status, func.count()).group_by(Job.status)
        result = await session.exec(statement)
        for status, count in result.all():
            name = status.value if isinstance(status, Status) else str(status)
            counts[name] = int(count)
    return counts


async def count_stale_jobs(status: Status, *, older_than: datetime) -> int:
    cutoff = _moment(older_than)
    async with session_scope() as session:
        statement = (
            select(func.count())
            .select_from(Job)
            .where(col(Job.status) == status)
            .where(col(Job.updated_at) < cutoff)
        )
        result = await session.exec(statement)
        value = result.one()
        raw = value[0] if isinstance(value, tuple) else value
        return int(raw or 0)


async def database_reachable() -> bool:
    try:
        await init_db()
        engine = get_engine()
        async with engine.connect() as conn:
            await conn.exec_driver_sql("SELECT 1")
        return True
    except Exception:
        return False
