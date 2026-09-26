"""Persisted gap between Workday pre-fills.

A captcha or Cloudflare block doubles the gap and blacks out the rest of the
local day. A streak of clean pre-fills halves the gap back toward the baseline.
The sleep happens outside the database session.
"""

from __future__ import annotations

import asyncio
import random
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

import structlog
from sqlmodel import select

from config.settings import get_settings
from core.db import PlatformPacing, _as_utc, init_db, session_scope

log = structlog.get_logger(__name__)

SleepFn = Callable[[float], Awaitable[None]]

_PACE_HINTS: tuple[str, ...] = (
    "captcha",
    "cloudflare",
    "cf-challenge",
    "challenge-platform",
    "just a moment",
    "verify you are human",
    "attention required",
    "access denied",
)


@dataclass(frozen=True)
class AcquireResult:
    skip: bool = False
    waited_s: float = 0.0


def is_pace_blocker(message: str) -> bool:
    """True when a blocker looks like a bot wall, not MFA or a missing session."""
    text = message.lower()
    return any(hint in text for hint in _PACE_HINTS)


def end_of_local_day(now: datetime, tz_name: str) -> datetime:
    """23:59:59 in ``tz_name``, returned as UTC. Unknown zones fall back to UTC."""
    try:
        tz = ZoneInfo(tz_name)
    except (ZoneInfoNotFoundError, ValueError):
        log.warning("pacing_timezone_invalid", timezone=tz_name)
        tz = UTC
    instant = _as_utc(now)
    assert instant is not None
    local = instant.astimezone(tz)
    end = local.replace(hour=23, minute=59, second=59, microsecond=0)
    return end.astimezone(UTC)


def gap_seconds(multiplier: int, *, rng: random.Random) -> int:
    """Random baseline gap times the clamped multiplier."""
    settings = get_settings()
    lo = settings.apply_gap_min_s
    hi = settings.apply_gap_max_s
    if hi < lo:
        hi = lo
    span = rng.randint(lo, hi) if hi > lo else lo
    return span * _clamp_multiplier(multiplier)


def _clamp_multiplier(multiplier: int) -> int:
    cap = get_settings().apply_gap_multiplier_cap
    return max(1, min(cap, multiplier))


def _clock(now: datetime | None) -> datetime:
    instant = _as_utc(now if now is not None else datetime.now(UTC))
    assert instant is not None
    return instant


async def _asyncio_sleep(seconds: float) -> None:
    await asyncio.sleep(seconds)


async def acquire(
    platform: str,
    *,
    now: datetime | None = None,
    sleep: SleepFn | None = None,
    rng: random.Random | None = None,
) -> AcquireResult:
    """Reserve the next Workday slot.

    Disabled pacing returns immediately and writes nothing. A blackout returns
    ``skip`` without sleeping. Otherwise any remaining gap is slept *after*
    the session closes, then ``next_eligible_at`` is committed before the
    caller starts the pre-fill. A fresh row does not sleep on its first attempt.
    """
    settings = get_settings()
    if not settings.apply_pacing_enabled:
        return AcquireResult()

    started = _clock(now)
    roller = rng or random.Random()
    pause = sleep or _asyncio_sleep
    await init_db()

    wait_s = 0.0
    async with session_scope() as session:
        result = await session.exec(
            select(PlatformPacing).where(PlatformPacing.platform == platform)
        )
        row = result.first()
        fresh = row is None
        if row is None:
            row = PlatformPacing(
                platform=platform,
                multiplier=1,
                clean_streak=0,
                updated_at=started,
            )
            session.add(row)
            await session.flush()

        blocked = _as_utc(row.blocked_until)
        if blocked is not None and blocked > started:
            return AcquireResult(skip=True)

        eligible = _as_utc(row.next_eligible_at)
        if not fresh and eligible is not None and eligible > started:
            wait_s = (eligible - started).total_seconds()
        else:
            row.next_eligible_at = started + timedelta(
                seconds=gap_seconds(row.multiplier, rng=roller)
            )
            row.updated_at = started
            session.add(row)
            return AcquireResult()

    await pause(wait_s)
    started = started + timedelta(seconds=wait_s)

    async with session_scope() as session:
        result = await session.exec(
            select(PlatformPacing).where(PlatformPacing.platform == platform)
        )
        row = result.first()
        if row is None:
            row = PlatformPacing(
                platform=platform,
                multiplier=1,
                clean_streak=0,
                updated_at=started,
            )
            session.add(row)
        blocked = _as_utc(row.blocked_until)
        if blocked is not None and blocked > started:
            return AcquireResult(skip=True, waited_s=wait_s)
        row.next_eligible_at = started + timedelta(
            seconds=gap_seconds(row.multiplier, rng=roller)
        )
        row.updated_at = started
        session.add(row)
    return AcquireResult(waited_s=wait_s)


async def note_success(platform: str, *, now: datetime | None = None) -> None:
    """Count a clean pre-fill. Every ``apply_clean_streak`` successes halves the gap."""
    settings = get_settings()
    if not settings.apply_pacing_enabled:
        return
    instant = _clock(now)
    await init_db()
    async with session_scope() as session:
        result = await session.exec(
            select(PlatformPacing).where(PlatformPacing.platform == platform)
        )
        row = result.first()
        if row is None:
            row = PlatformPacing(
                platform=platform,
                multiplier=1,
                clean_streak=0,
                updated_at=instant,
            )
            session.add(row)
            await session.flush()
        row.clean_streak += 1
        if row.clean_streak >= settings.apply_clean_streak:
            row.multiplier = max(1, row.multiplier // 2)
            row.clean_streak = 0
        row.updated_at = instant
        session.add(row)


async def note_pace_block(platform: str, *, now: datetime | None = None) -> None:
    """Double the gap and black out the rest of the local day."""
    settings = get_settings()
    if not settings.apply_pacing_enabled:
        return
    instant = _clock(now)
    until = end_of_local_day(instant, settings.timezone)
    await init_db()
    async with session_scope() as session:
        result = await session.exec(
            select(PlatformPacing).where(PlatformPacing.platform == platform)
        )
        row = result.first()
        if row is None:
            row = PlatformPacing(
                platform=platform,
                multiplier=1,
                clean_streak=0,
                updated_at=instant,
            )
            session.add(row)
            await session.flush()
        doubled = _clamp_multiplier(row.multiplier) * 2
        row.multiplier = min(settings.apply_gap_multiplier_cap, doubled)
        row.clean_streak = 0
        row.blocked_until = until
        row.next_eligible_at = until
        row.updated_at = instant
        session.add(row)
