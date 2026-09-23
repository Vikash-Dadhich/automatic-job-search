"""Offline tests for APScheduler construction (never started)."""

from __future__ import annotations

import pytest

from orchestrator.scheduler import build_scheduler, parse_hhmm


def test_parse_hhmm() -> None:
    assert parse_hhmm("08:00") == (8, 0)
    assert parse_hhmm("13:30") == (13, 30)
    assert parse_hhmm("0:05") == (0, 5)


def test_parse_hhmm_invalid() -> None:
    with pytest.raises(ValueError):
        parse_hhmm("25:00")
    with pytest.raises(ValueError):
        parse_hhmm("8")
    with pytest.raises(ValueError):
        parse_hhmm("ab:cd")


async def _noop() -> None:
    return None


def test_build_scheduler_registers_jobs(monkeypatch: pytest.MonkeyPatch) -> None:
    from config.settings import get_settings

    monkeypatch.setenv("SCHEDULE_TIMES", '["09:15","18:45"]')
    monkeypatch.setenv("TIMEZONE", "America/New_York")
    get_settings.cache_clear()

    scheduler = build_scheduler(func=_noop)
    jobs = scheduler.get_jobs()
    assert len(jobs) == 2
    ids = sorted(j.id for j in jobs)
    assert ids == ["pipeline_0915", "pipeline_1845"]

    by_id = {j.id: j for j in jobs}
    t_am = by_id["pipeline_0915"].trigger
    t_pm = by_id["pipeline_1845"].trigger
    assert str(t_am.timezone) == "America/New_York"
    assert t_am.fields[5].expressions[0].first == 9  # hour field
    assert t_am.fields[6].expressions[0].first == 15  # minute
    assert t_pm.fields[5].expressions[0].first == 18
    assert t_pm.fields[6].expressions[0].first == 45

    # Never started
    assert not scheduler.running
    get_settings.cache_clear()


def test_build_scheduler_skips_invalid_times(monkeypatch: pytest.MonkeyPatch) -> None:
    from config.settings import get_settings

    get_settings.cache_clear()
    scheduler = build_scheduler(
        func=_noop,
        schedule_times=["08:00", "bad", "25:99", "18:00"],
        timezone="UTC",
    )
    ids = sorted(j.id for j in scheduler.get_jobs())
    assert ids == ["pipeline_0800", "pipeline_1800"]
    assert not scheduler.running
    get_settings.cache_clear()


def test_build_scheduler_invalid_timezone() -> None:
    with pytest.raises(ValueError, match="timezone"):
        build_scheduler(func=_noop, schedule_times=["08:00"], timezone="Not/AZone")
