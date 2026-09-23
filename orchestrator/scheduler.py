"""APScheduler construction for the 3x/day pipeline."""

from __future__ import annotations

import re
from collections.abc import Awaitable, Callable
from typing import Any
from zoneinfo import ZoneInfo

import structlog
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from config.settings import get_settings
from orchestrator.pipeline import run_pipeline

log = structlog.get_logger(__name__)

_HHMM_RE = re.compile(r"^(\d{1,2}):(\d{2})$")


def parse_hhmm(value: str) -> tuple[int, int]:
    """Parse 'HH:MM' into (hour, minute). Raises ValueError on bad input."""
    text = (value or "").strip()
    match = _HHMM_RE.match(text)
    if not match:
        raise ValueError(f"Invalid schedule time {value!r}; expected HH:MM")
    hour = int(match.group(1))
    minute = int(match.group(2))
    if not (0 <= hour <= 23 and 0 <= minute <= 59):
        raise ValueError(f"Invalid schedule time {value!r}; out of range")
    return hour, minute


def build_scheduler(
    *,
    func: Callable[..., Awaitable[Any]] | None = None,
    schedule_times: list[str] | None = None,
    timezone: str | None = None,
) -> AsyncIOScheduler:
    """Build (but do not start) an AsyncIOScheduler with one job per HH:MM.

    Jobs use CronTrigger, max_instances=1, coalesce=True so overlapping runs
    are skipped/merged rather than stacked.
    """
    settings = get_settings()
    times = schedule_times if schedule_times is not None else settings.schedule_times
    tz_name = timezone if timezone is not None else settings.timezone
    job_func = func if func is not None else run_pipeline

    try:
        tz = ZoneInfo(tz_name)
    except Exception as exc:
        raise ValueError(f"Invalid timezone {tz_name!r}: {exc}") from exc

    scheduler = AsyncIOScheduler(timezone=tz)
    registered: list[str] = []

    for raw in times:
        try:
            hour, minute = parse_hhmm(raw)
        except ValueError as exc:
            log.warning("schedule_time_skipped", value=raw, error=str(exc))
            continue

        job_id = f"pipeline_{hour:02d}{minute:02d}"
        trigger = CronTrigger(hour=hour, minute=minute, timezone=tz)
        scheduler.add_job(
            job_func,
            trigger=trigger,
            id=job_id,
            name=f"pipeline@{hour:02d}:{minute:02d}",
            replace_existing=True,
            max_instances=1,
            coalesce=True,
            misfire_grace_time=300,
        )
        registered.append(job_id)

    if not registered:
        log.warning("scheduler_no_jobs", schedule_times=times)

    log.info(
        "scheduler_built",
        jobs=registered,
        timezone=tz_name,
        schedule_times=times,
    )
    return scheduler
