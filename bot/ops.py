"""Run health on Telegram: a notice after a long silence and a short weekly summary.

A scheduler that stops cannot report itself, so the next run that does start says
how long the gap was. The weekly summary is sent by the first run on Monday.
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from zoneinfo import ZoneInfo

import structlog
from sqlalchemy import func
from sqlmodel import col, select

from bot.telegram import TelegramClient
from config.settings import get_settings
from core.db import Job, PipelineRun, PipelineStageRun, Status, init_db, session_scope

log = structlog.get_logger(__name__)

HEARTBEAT_GAP_HOURS = 26
WEEKLY_STAGE = "weekly_summary"
_GOOD = ("succeeded", "partial")


def _utc(moment: datetime) -> datetime:
    return moment if moment.tzinfo else moment.replace(tzinfo=UTC)


async def last_good_run_finish(*, before: datetime | None = None) -> datetime | None:
    """When the most recent succeeded or partial run finished, if any."""
    await init_db()
    async with session_scope() as session:
        statement = select(func.max(PipelineRun.finished_at)).where(
            col(PipelineRun.status).in_(_GOOD)
        )
        if before is not None:
            statement = statement.where(col(PipelineRun.finished_at) < before)
        found = (await session.exec(statement)).one()
    return _utc(found) if found else None


async def send_heartbeat_notice(
    client: TelegramClient | None = None,
    *,
    now: datetime | None = None,
) -> bool:
    """Tell the owner when the last good run was more than HEARTBEAT_GAP_HOURS ago."""
    moment = now or datetime.now(UTC)
    last = await last_good_run_finish(before=moment)
    if last is None or moment - last <= timedelta(hours=HEARTBEAT_GAP_HOURS):
        return False
    hours = int((moment - last).total_seconds() // 3600)
    client = client or TelegramClient()
    await client.send_message(
        f"The job agent was quiet for {hours} hours (last good run {last:%b %d %H:%M} UTC). "
        "It is running again now."
    )
    log.info("heartbeat_gap_notice", hours=hours)
    return True


async def build_weekly_summary(*, now: datetime | None = None) -> str:
    moment = now or datetime.now(UTC)
    since = moment - timedelta(days=7)
    await init_db()
    async with session_scope() as session:

        async def count(*conditions: object) -> int:
            result = await session.exec(select(func.count()).select_from(Job).where(*conditions))  # type: ignore[arg-type]
            return int(result.one())

        queued = await count(col(Job.queued_at) >= since)
        applied = await count(col(Job.status) == Status.submitted, col(Job.decided_at) >= since)
        closed = await count(col(Job.status) == Status.ignored, col(Job.decided_at) >= since)
        waiting = await count(col(Job.status) == Status.pending_review)
    return (
        "Weekly summary\n"
        f"Queued: {queued}\n"
        f"You applied to: {applied}\n"
        f"Skipped or expired: {closed}\n"
        f"Waiting for you now: {waiting}"
    )


async def _weekly_already_sent(now: datetime) -> bool:
    async with session_scope() as session:
        found = (
            await session.exec(
                select(func.count())
                .select_from(PipelineStageRun)
                .where(
                    col(PipelineStageRun.stage) == WEEKLY_STAGE,
                    col(PipelineStageRun.status) == "succeeded",
                    col(PipelineStageRun.started_at) >= now - timedelta(days=6),
                )
            )
        ).one()
    return int(found) > 0


async def send_weekly_summary(
    client: TelegramClient | None = None,
    *,
    now: datetime | None = None,
) -> bool:
    """Send on Monday (owner's timezone) unless one already went out this week.

    The previous weekly stage is read before this run's own stage row counts: this
    run's row is still ``running`` while the stage executes, so it is not matched.
    """
    moment = now or datetime.now(UTC)
    local = moment.astimezone(ZoneInfo(get_settings().timezone))
    if local.weekday() != 0:
        return False
    await init_db()
    if await _weekly_already_sent(moment):
        return False
    client = client or TelegramClient()
    await client.send_message(await build_weekly_summary(now=moment))
    return True
