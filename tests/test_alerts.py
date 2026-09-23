"""Offline tests for blocker/error Telegram alerts."""

from __future__ import annotations

from pathlib import Path

from bot.alerts import build_alert_caption, send_pending_alerts
from bot.telegram import TelegramClient
from core.db import Job, Source, Status, get_job_by_id, session_scope, upsert_job
from tests.test_telegram import FakeTransport


def _tiny_png(path: Path) -> Path:
    path.write_bytes(
        b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01"
        b"\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00"
        b"\x00\x0cIDATx\x9cc\xf8\x0f\x00\x00\x01\x01\x00\x05\x18"
        b"\xd8N\x00\x00\x00\x00IEND\xaeB`\x82"
    )
    return path


def test_build_alert_caption() -> None:
    job = Job(
        source=Source.workday,
        external_id="wd-a",
        title="Engineer",
        company="Acme",
        url="https://example.com",
        status=Status.manual_review,
        last_error="Blocker detected (cloudflare)",
    )
    caption = build_alert_caption(job)
    assert "ALERT [MANUAL_REVIEW]" in caption
    assert "Engineer @ Acme" in caption
    assert "cloudflare" in caption


async def test_send_pending_alerts_photo_and_skip(
    db_ready: Path,
    tmp_path: Path,
) -> None:
    shot = _tiny_png(tmp_path / "blocker.png")
    job = Job(
        source=Source.workday,
        external_id="wd-alert-1",
        title="Software Engineer",
        company="Acme",
        url="https://acme.wd5.myworkdayjobs.com/en-US/External/job/1",
        tenant="acme",
        status=Status.manual_review,
        screenshot_path=str(shot),
        last_error="Blocker detected (cloudflare)",
    )
    async with session_scope() as session:
        job = await upsert_job(session, job)

    transport = FakeTransport()
    client = TelegramClient(transport=transport, chat_id="999")
    summary = await send_pending_alerts(client)

    assert summary.sent == 1
    assert summary.errors == 0
    assert transport.calls[0]["method"] == "sendPhoto"
    assert "ALERT" in transport.calls[0]["payload"]["caption"]

    async with session_scope() as session:
        assert job.id is not None
        refreshed = await get_job_by_id(session, job.id)
        assert refreshed is not None
        assert refreshed.alerted_at is not None

    # Second send should skip already-alerted
    summary2 = await send_pending_alerts(client)
    assert summary2.sent == 0
    assert len(transport.calls) == 1


async def test_send_pending_alerts_text_for_error(db_ready: Path) -> None:
    job = Job(
        source=Source.workday,
        external_id="wd-err-alert",
        title="Backend",
        company="Co",
        url="https://co.wd1.myworkdayjobs.com/en-US/External/job/2",
        status=Status.error,
        last_error="boom",
        screenshot_path=None,
    )
    async with session_scope() as session:
        job = await upsert_job(session, job)

    transport = FakeTransport()
    client = TelegramClient(transport=transport, chat_id="1")
    summary = await send_pending_alerts(client)

    assert summary.sent == 1
    assert transport.calls[0]["method"] == "sendMessage"
    assert "ALERT [ERROR]" in transport.calls[0]["payload"]["text"]

    async with session_scope() as session:
        assert job.id is not None
        refreshed = await get_job_by_id(session, job.id)
        assert refreshed is not None
        assert refreshed.alerted_at is not None


async def test_send_pending_alerts_empty(db_ready: Path) -> None:
    transport = FakeTransport()
    client = TelegramClient(transport=transport, chat_id="1")
    summary = await send_pending_alerts(client)
    assert summary.sent == 0
    assert transport.calls == []
