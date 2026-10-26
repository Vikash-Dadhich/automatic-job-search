"""One stuck discovery source must not hold up the whole ingestion."""

from __future__ import annotations

import asyncio

import pytest

from scraper.ingest import _wait_for_sources
from scraper.models import RawPosting


async def _fast() -> list[RawPosting]:
    return []


async def _slow() -> list[RawPosting]:
    await asyncio.sleep(30)
    return []


async def _boom() -> list[RawPosting]:
    raise RuntimeError("source broke")


async def test_stuck_source_is_cancelled_and_reported() -> None:
    tasks = [asyncio.create_task(_fast()), asyncio.create_task(_slow())]
    results = await _wait_for_sources(tasks, ["boards", "jobspy"], timeout=1.0, tick=0.2)
    assert results[0] == []
    assert isinstance(results[1], TimeoutError)
    assert tasks[1].cancelled()


async def test_failed_source_is_returned_not_raised() -> None:
    tasks = [asyncio.create_task(_boom()), asyncio.create_task(_fast())]
    results = await _wait_for_sources(tasks, ["workday", "boards"], timeout=5.0, tick=0.2)
    assert isinstance(results[0], RuntimeError)
    assert results[1] == []


async def test_progress_lines_name_waiting_sources(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setenv("GITHUB_ACTIONS", "true")
    tasks = [asyncio.create_task(_slow())]
    await _wait_for_sources(tasks, ["jobspy"], timeout=0.5, tick=0.2)
    out = capsys.readouterr().out
    assert "ingestion waiting" in out
    assert "jobspy" in out
    assert "cancelled" in out
