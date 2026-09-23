"""Offline tests for review caption/keyboard and send_pending_reviews."""

from __future__ import annotations

from pathlib import Path

from bot.review import (
    build_keyboard,
    build_review_caption,
    format_answers_message,
    send_pending_reviews,
)
from bot.telegram import TelegramClient, decode_callback
from core.db import Job, Source, Status, Tier, get_job_by_id, session_scope, upsert_job
from tests.test_telegram import FakeTransport


def _tiny_png(path: Path) -> Path:
    path.write_bytes(
        b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01"
        b"\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00"
        b"\x00\x0cIDATx\x9cc\xf8\x0f\x00\x00\x01\x01\x00\x05\x18"
        b"\xd8N\x00\x00\x00\x00IEND\xaeB`\x82"
    )
    return path


def test_build_keyboard_and_caption() -> None:
    job = Job(
        id=5,
        source=Source.workday,
        external_id="wd-5",
        title="Backend Engineer",
        company="Acme",
        location="Remote",
        url="https://acme.wd5.myworkdayjobs.com/en-US/External/job/1",
        score=90,
        tier=Tier.one,
        outreach_draft="Hi there.",
        justification=["strong Python", "remote ok"],
        status=Status.pending_review,
    )
    caption = build_review_caption(job)
    assert "Backend Engineer @ Acme" in caption
    assert "Score: 90" in caption
    assert "Outreach draft ready" in caption
    assert "Approve" in caption

    keyboard = build_keyboard(5)
    row = keyboard["inline_keyboard"][0]
    assert len(row) == 3
    assert row[0]["text"] == "Approve"
    action, job_id = decode_callback(row[0]["callback_data"])
    assert action.value == "ok"
    assert job_id == 5


def test_format_answers_message() -> None:
    job = Job(
        source=Source.workday,
        external_id="wd-a",
        title="Eng",
        company="Co",
        url="https://example.com",
        id=3,
        application_answers={
            "items": [
                {"question": "Email", "answer": "a@b.com", "source": "deterministic"},
                {"question": "Why?", "answer": "", "source": "blank"},
            ],
            "count": 2,
        },
    )
    text = format_answers_message(job)
    assert text is not None
    assert "Email" in text
    assert "a@b.com" in text
    assert "(blank)" in text


async def test_send_pending_reviews_persists_message_id(
    db_ready: Path,
    tmp_path: Path,
) -> None:
    shot = _tiny_png(tmp_path / "review.png")
    job = Job(
        source=Source.workday,
        external_id="wd-review-1",
        title="Software Engineer",
        company="Acme",
        url="https://acme.wd5.myworkdayjobs.com/en-US/External/job/1",
        tenant="acme",
        status=Status.pending_review,
        screenshot_path=str(shot),
        score=80,
        tier=Tier.two,
    )
    async with session_scope() as session:
        job = await upsert_job(session, job)

    transport = FakeTransport()
    client = TelegramClient(transport=transport, chat_id="999")
    summary = await send_pending_reviews(client)

    assert summary.sent == 1
    assert summary.errors == 0
    assert transport.calls[0]["method"] == "sendPhoto"

    async with session_scope() as session:
        assert job.id is not None
        refreshed = await get_job_by_id(session, job.id)
        assert refreshed is not None
        assert refreshed.review_message_id == 42
        assert refreshed.review_chat_id == "999"

    # Second send should skip already-sent
    summary2 = await send_pending_reviews(client)
    assert summary2.sent == 0
    assert len(transport.calls) == 1


async def test_send_pending_reviews_empty(db_ready: Path) -> None:
    transport = FakeTransport()
    client = TelegramClient(transport=transport, chat_id="1")
    summary = await send_pending_reviews(client)
    assert summary.sent == 0
    assert transport.calls == []
