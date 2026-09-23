"""Offline tests for run_service lifecycle (no real polling)."""

from __future__ import annotations

import asyncio
from pathlib import Path

import pytest

from orchestrator.service import run_service


async def test_run_service_stops_without_poller(
    db_ready: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Scheduler starts; preset stop_event exits cleanly with run_poller=False."""
    from config.settings import get_settings

    monkeypatch.setenv("SCHEDULE_TIMES", '["08:00"]')
    monkeypatch.setenv("TIMEZONE", "UTC")
    get_settings.cache_clear()

    stop = asyncio.Event()
    stop.set()

    await run_service(run_poller=False, stop_event=stop)
    get_settings.cache_clear()


async def test_run_service_with_poller_respects_stop(
    db_ready: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from config.settings import get_settings

    monkeypatch.setenv("SCHEDULE_TIMES", '["09:00"]')
    monkeypatch.setenv("TIMEZONE", "UTC")
    get_settings.cache_clear()

    stop = asyncio.Event()

    async def fake_polling(*, stop_event: asyncio.Event, **_kwargs: object) -> None:
        await stop_event.wait()

    monkeypatch.setattr("orchestrator.service.run_polling", fake_polling)

    async def stopper() -> None:
        await asyncio.sleep(0.05)
        stop.set()

    await asyncio.gather(
        run_service(run_poller=True, stop_event=stop),
        stopper(),
    )
    get_settings.cache_clear()
