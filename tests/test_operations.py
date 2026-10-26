"""Heartbeat notice, weekly summary and the production flags that switch them on."""

from __future__ import annotations

import re
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest
from sqlmodel import select

from bot.ops import (
    WEEKLY_STAGE,
    build_weekly_summary,
    send_heartbeat_notice,
    send_weekly_summary,
)
from bot.telegram import TelegramClient
from core.db import (
    Job,
    PipelineRun,
    PipelineStageRun,
    Source,
    Status,
    session_scope,
    upsert_job,
)
from tests.test_telegram import FakeTransport

MONDAY = datetime(2026, 10, 26, 18, 0, tzinfo=UTC)
TUESDAY = MONDAY + timedelta(days=1)


def _client() -> tuple[TelegramClient, FakeTransport]:
    transport = FakeTransport()
    return TelegramClient(transport=transport, chat_id="999"), transport


def _sent(transport: FakeTransport) -> list[str]:
    return [c["payload"]["text"] for c in transport.calls if c["method"] == "sendMessage"]


async def _run(finished: datetime, status: str = "succeeded", key: str = "r1") -> None:
    async with session_scope() as session:
        session.add(
            PipelineRun(
                run_key=key,
                status=status,
                started_at=finished - timedelta(minutes=5),
                finished_at=finished,
            )
        )


async def test_no_notice_after_a_recent_good_run(db_ready: Path) -> None:
    del db_ready
    await _run(MONDAY - timedelta(hours=20))
    client, transport = _client()
    assert await send_heartbeat_notice(client, now=MONDAY) is False
    assert _sent(transport) == []


async def test_notice_after_a_long_gap(db_ready: Path) -> None:
    del db_ready
    await _run(MONDAY - timedelta(hours=60))
    client, transport = _client()
    assert await send_heartbeat_notice(client, now=MONDAY) is True
    assert "60 hours" in _sent(transport)[0]


async def test_failed_runs_do_not_count_as_good(db_ready: Path) -> None:
    del db_ready
    await _run(MONDAY - timedelta(hours=60), key="old")
    await _run(MONDAY - timedelta(hours=2), status="failed", key="bad")
    client, _ = _client()
    assert await send_heartbeat_notice(client, now=MONDAY) is True


async def test_first_ever_run_is_silent(db_ready: Path) -> None:
    del db_ready
    client, transport = _client()
    assert await send_heartbeat_notice(client, now=MONDAY) is False
    assert _sent(transport) == []


async def test_weekly_summary_counts(db_ready: Path) -> None:
    del db_ready
    async with session_scope() as session:
        for name, status in (
            ("a", Status.submitted),
            ("b", Status.submitted),
            ("c", Status.ignored),
            ("d", Status.pending_review),
        ):
            await upsert_job(
                session,
                Job(
                    source=Source.linkedin,
                    external_id=name,
                    title="PM Intern",
                    company=f"Co {name}",
                    url=f"https://x.example/{name}",
                    status=status,
                    queued_at=MONDAY - timedelta(days=2),
                    decided_at=(
                        None if status == Status.pending_review else MONDAY - timedelta(days=1)
                    ),
                ),
            )
    text = await build_weekly_summary(now=MONDAY)
    assert "Queued: 4" in text
    assert "You applied to: 2" in text
    assert "Skipped or expired: 1" in text
    assert "Waiting for you now: 1" in text


async def test_weekly_summary_only_on_monday(db_ready: Path) -> None:
    del db_ready
    client, transport = _client()
    assert await send_weekly_summary(client, now=TUESDAY) is False
    assert await send_weekly_summary(client, now=MONDAY) is True
    assert len(_sent(transport)) == 1


async def test_weekly_summary_not_repeated_within_the_week(db_ready: Path) -> None:
    del db_ready
    await _run(MONDAY - timedelta(hours=1), key="today")
    async with session_scope() as session:
        run = (await session.exec(select(PipelineRun))).first()
        assert run is not None and run.id is not None
        session.add(
            PipelineStageRun(
                pipeline_run_id=run.id,
                stage=WEEKLY_STAGE,
                status="succeeded",
                started_at=MONDAY - timedelta(hours=1),
                counters={},
            )
        )
    client, transport = _client()
    assert await send_weekly_summary(client, now=MONDAY) is False
    assert _sent(transport) == []


def test_production_workflow_turns_on_boards_and_queue() -> None:
    text = Path(".github/workflows/pipeline.yml").read_text(encoding="utf-8")
    assert 'ENABLE_ATS_BOARDS: "true"' in text
    assert 'SIMPLIFY_DISCOVERY: "true"' in text
    match = re.search(r'^\s+QUEUE_DAILY_LIMIT: "(\d+)"$', text, re.MULTILINE)
    assert match is not None and 0 < int(match.group(1)) <= 25
    assert "schedule:" not in text


def test_stage_annotation_only_inside_actions(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    from orchestrator.pipeline import _annotate

    monkeypatch.delenv("GITHUB_ACTIONS", raising=False)
    _annotate("stage x", "ok in 3s")
    assert capsys.readouterr().out == ""
    monkeypatch.setenv("GITHUB_ACTIONS", "true")
    _annotate("stage x", "line one\nline two")
    assert capsys.readouterr().out == "::notice title=stage x::line one line two\n"
