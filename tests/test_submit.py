"""Offline tests for WorkdaySubmitter guard paths (no browser)."""

from __future__ import annotations

from contextlib import asynccontextmanager
from typing import Any
from unittest.mock import AsyncMock

import pytest

from automation.browser import SessionMissingError
from bot.submit import WorkdaySubmitter
from core.db import Job, Source


async def test_submit_missing_url() -> None:
    job = Job(
        source=Source.workday,
        external_id="wd-1",
        title="Eng",
        company="Co",
        url="",
        tenant="co",
    )
    result = await WorkdaySubmitter().submit(job)
    assert result.submitted is False
    assert result.reason == "Job missing url"


async def test_submit_unparseable_without_tenant() -> None:
    job = Job(
        source=Source.workday,
        external_id="wd-2",
        title="Eng",
        company="Co",
        url="https://example.com/not-workday",
        tenant=None,
    )
    result = await WorkdaySubmitter().submit(job)
    assert result.submitted is False
    assert result.reason is not None
    assert "parseable" in result.reason.lower() or "tenant" in result.reason.lower()


async def test_submit_session_missing(monkeypatch: pytest.MonkeyPatch) -> None:
    @asynccontextmanager
    async def boom_launch(*_args: Any, **_kwargs: Any):
        raise SessionMissingError("No saved session for tenant 'acme'")
        yield  # pragma: no cover

    monkeypatch.setattr("bot.submit.launch_context", boom_launch)

    job = Job(
        source=Source.workday,
        external_id="wd-3",
        title="Eng",
        company="Acme",
        url="https://acme.wd5.myworkdayjobs.com/en-US/External/job/1",
        tenant="acme",
    )
    result = await WorkdaySubmitter(sessions_dir=None).submit(job)
    assert result.submitted is False
    assert result.reason is not None
    assert "session" in result.reason.lower()


async def test_submit_generic_exception(monkeypatch: pytest.MonkeyPatch) -> None:
    @asynccontextmanager
    async def boom_launch(*_args: Any, **_kwargs: Any):
        raise RuntimeError("browser crash")
        yield  # pragma: no cover

    monkeypatch.setattr("bot.submit.launch_context", boom_launch)
    monkeypatch.setattr("bot.submit.new_page", AsyncMock())

    job = Job(
        source=Source.workday,
        external_id="wd-4",
        title="Eng",
        company="Acme",
        url="https://acme.wd5.myworkdayjobs.com/en-US/External/job/1",
        tenant="acme",
    )
    result = await WorkdaySubmitter().submit(job)
    assert result.submitted is False
    assert "browser crash" in (result.reason or "")
