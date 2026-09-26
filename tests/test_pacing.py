"""Workday apply throttle: classifier, AIMD, blackout, and runner wiring."""

from __future__ import annotations

import random
from datetime import UTC, datetime, timedelta

import pytest
from sqlmodel import select

from automation.pacing import (
    acquire,
    end_of_local_day,
    gap_seconds,
    is_pace_blocker,
    note_pace_block,
    note_success,
)
from automation.runner import apply_pending
from automation.workday import ApplyResult, BlockerError
from config.settings import get_settings
from core.db import (
    Job,
    PlatformPacing,
    Source,
    Status,
    _as_utc,
    get_job_by_id,
    session_scope,
    upsert_job,
)

NOW = datetime(2026, 9, 25, 20, 0, tzinfo=UTC)
LA_END = datetime(2026, 9, 26, 6, 59, 59, tzinfo=UTC)
_URL = "https://acme.wd5.myworkdayjobs.com/en-US/External/job/City/Title_R1"


class _Sleep:
    def __init__(self) -> None:
        self.calls: list[float] = []

    async def __call__(self, seconds: float) -> None:
        self.calls.append(seconds)


class _Applicator:
    def __init__(self, *, mode: str = "ok") -> None:
        self.mode = mode
        self.calls: list[int | None] = []

    async def apply(self, job: Job) -> ApplyResult:
        self.calls.append(job.id)
        if self.mode == "cloudflare":
            raise BlockerError("cloudflare")
        if self.mode == "mfa":
            raise BlockerError("multi-factor")
        return ApplyResult(
            screenshot_path="/tmp/review.png",
            application_answers={"items": [], "count": 0},
            reached_review=True,
        )


def _enable(monkeypatch: pytest.MonkeyPatch, **env: str) -> None:
    monkeypatch.setenv("APPLY_PACING_ENABLED", "true")
    for key, value in env.items():
        monkeypatch.setenv(key, value)
    get_settings.cache_clear()


async def _seed(external_id: str) -> Job:
    job = Job(
        source=Source.workday,
        external_id=external_id,
        title="Software Engineer",
        company="Acme",
        url=_URL,
        tenant="acme",
        status=Status.staged,
        resume_path="/tmp/resume.pdf",
    )
    async with session_scope() as session:
        return await upsert_job(session, job)


async def _row() -> PlatformPacing | None:
    async with session_scope() as session:
        result = await session.exec(
            select(PlatformPacing).where(PlatformPacing.platform == "workday")
        )
        return result.first()


@pytest.mark.parametrize(
    "message",
    ["cloudflare", "Captcha challenge", "cf-challenge", "verify you are human"],
)
def test_pace_hints_match(message: str) -> None:
    assert is_pace_blocker(message)


@pytest.mark.parametrize(
    "message",
    ["multi-factor", "two-factor", "verification code", "enter the code", "No saved session", ""],
)
def test_pace_hints_ignore_mfa_and_empty(message: str) -> None:
    assert not is_pace_blocker(message)


def test_end_of_los_angeles_day() -> None:
    assert end_of_local_day(NOW, "America/Los_Angeles") == LA_END


def test_unknown_timezone_uses_utc() -> None:
    assert end_of_local_day(NOW, "Not/AZone") == datetime(2026, 9, 25, 23, 59, 59, tzinfo=UTC)


def test_gap_treats_max_below_min_as_min(monkeypatch: pytest.MonkeyPatch) -> None:
    _enable(monkeypatch, APPLY_GAP_MIN_S="100", APPLY_GAP_MAX_S="10")
    assert gap_seconds(2, rng=random.Random(0)) == 200


async def test_block_doubles_until_cap_and_resets_streak(
    db_ready: object,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _enable(monkeypatch)
    await note_success("workday", now=NOW)
    await note_success("workday", now=NOW)
    await note_pace_block("workday", now=NOW)
    row = await _row()
    assert row is not None
    assert row.multiplier == 2
    assert row.clean_streak == 0
    assert _as_utc(row.blocked_until) == LA_END
    assert _as_utc(row.next_eligible_at) == LA_END

    await note_pace_block("workday", now=NOW)
    row = await _row()
    assert row is not None
    assert row.multiplier == 4
    await note_pace_block("workday", now=NOW)
    row = await _row()
    assert row is not None
    assert row.multiplier == 8
    await note_pace_block("workday", now=NOW)
    row = await _row()
    assert row is not None
    assert row.multiplier == 8
    assert row.clean_streak == 0


async def test_acquire_skips_during_blackout(
    db_ready: object,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _enable(monkeypatch)
    await note_pace_block("workday", now=NOW)
    sleeper = _Sleep()
    slot = await acquire("workday", now=NOW, sleep=sleeper, rng=random.Random(0))
    assert slot.skip is True
    assert sleeper.calls == []


async def test_acquire_after_blackout_keeps_multiplier(
    db_ready: object,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _enable(monkeypatch, APPLY_GAP_MIN_S="10", APPLY_GAP_MAX_S="10")
    await note_pace_block("workday", now=NOW)
    await note_pace_block("workday", now=NOW)
    sleeper = _Sleep()
    later = LA_END + timedelta(seconds=1)
    slot = await acquire("workday", now=later, sleep=sleeper, rng=random.Random(0))
    assert slot.skip is False
    assert slot.waited_s == 0
    assert sleeper.calls == []
    row = await _row()
    assert row is not None
    assert row.multiplier == 4


async def test_three_successes_halve_multiplier(
    db_ready: object,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _enable(monkeypatch)
    await note_pace_block("workday", now=NOW)
    await note_pace_block("workday", now=NOW)
    for _ in range(3):
        await note_success("workday", now=NOW)
    row = await _row()
    assert row is not None
    assert row.multiplier == 2
    assert row.clean_streak == 0
    assert _as_utc(row.blocked_until) == LA_END


async def test_successes_at_multiplier_one_stay_at_one(
    db_ready: object,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _enable(monkeypatch)
    for _ in range(6):
        await note_success("workday", now=NOW)
    row = await _row()
    assert row is not None
    assert row.multiplier == 1
    assert row.clean_streak == 0


async def test_runner_waits_then_both_pending(
    db_ready: object,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _enable(monkeypatch, APPLY_GAP_MIN_S="10", APPLY_GAP_MAX_S="10")
    await _seed("pace-a")
    await _seed("pace-b")
    sleeper = _Sleep()
    fake = _Applicator()
    summary = await apply_pending(
        applicator=fake,
        limit=10,
        sleep=sleeper,
        rng=random.Random(0),
        now=NOW,
    )
    assert summary.pending_review == 2
    assert summary.blackout_skipped == 0
    assert sleeper.calls == [10.0]
    assert len(fake.calls) == 2


async def test_runner_blackout_leaves_second_job_staged(
    db_ready: object,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _enable(monkeypatch)
    first = await _seed("pace-block")
    second = await _seed("pace-later")
    sleeper = _Sleep()
    fake = _Applicator(mode="cloudflare")
    summary = await apply_pending(
        applicator=fake,
        limit=10,
        sleep=sleeper,
        rng=random.Random(0),
        now=NOW,
    )
    assert summary.manual_review == 1
    assert summary.blackout_skipped == 1
    assert summary.skipped == 0
    assert len(fake.calls) == 1
    assert sleeper.calls == []
    async with session_scope() as session:
        assert first.id is not None
        assert second.id is not None
        blocked = await get_job_by_id(session, first.id)
        held = await get_job_by_id(session, second.id)
        assert blocked is not None
        assert held is not None
        assert blocked.status == Status.manual_review
        assert held.status == Status.staged


async def test_runner_mfa_does_not_black_out(
    db_ready: object,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _enable(monkeypatch, APPLY_GAP_MIN_S="10", APPLY_GAP_MAX_S="10")
    await _seed("pace-mfa-1")
    await _seed("pace-mfa-2")
    sleeper = _Sleep()
    fake = _Applicator(mode="mfa")
    summary = await apply_pending(
        applicator=fake,
        limit=10,
        sleep=sleeper,
        rng=random.Random(0),
        now=NOW,
    )
    assert summary.manual_review == 2
    assert summary.blackout_skipped == 0
    assert len(fake.calls) == 2
    row = await _row()
    assert row is not None
    assert row.multiplier == 1
    assert row.blocked_until is None


async def test_runner_pacing_disabled_does_not_sleep(
    db_ready: object,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("APPLY_PACING_ENABLED", "false")
    get_settings.cache_clear()
    await _seed("pace-off-1")
    await _seed("pace-off-2")
    sleeper = _Sleep()
    summary = await apply_pending(
        applicator=_Applicator(),
        limit=10,
        sleep=sleeper,
        rng=random.Random(0),
        now=NOW,
    )
    assert summary.pending_review == 2
    assert sleeper.calls == []
    assert await _row() is None
