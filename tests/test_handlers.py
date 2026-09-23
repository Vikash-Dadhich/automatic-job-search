"""Offline tests for Telegram callback handlers with FakeSubmitter."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from bot.handlers import handle_callback
from bot.submit import SubmitResult
from bot.telegram import ReviewAction, TelegramClient, encode_callback
from core.db import Job, Source, Status, Tier, get_job_by_id, session_scope, upsert_job
from tests.test_telegram import FakeTransport


class FakeSubmitter:
    def __init__(self, *, mode: str = "ok") -> None:
        self.mode = mode
        self.calls: list[int | None] = []

    async def submit(self, job: Job) -> SubmitResult:
        self.calls.append(job.id)
        if self.mode == "ok":
            return SubmitResult(
                submitted=True,
                screenshot_path="/tmp/submitted.png",
                reason="submitted",
            )
        return SubmitResult(
            submitted=False,
            screenshot_path="/tmp/blocker.png",
            reason="cloudflare",
        )


async def _seed_pending(*, external_id: str = "wd-cb-1") -> Job:
    job = Job(
        source=Source.workday,
        external_id=external_id,
        title="Backend Engineer",
        company="Acme",
        url="https://acme.wd5.myworkdayjobs.com/en-US/External/job/1",
        tenant="acme",
        status=Status.pending_review,
        screenshot_path="/tmp/review.png",
        review_message_id=10,
        review_chat_id="999",
        score=88,
        tier=Tier.one,
    )
    async with session_scope() as session:
        return await upsert_job(session, job)


def _callback_update(job_id: int, action: ReviewAction, *, update_id: int = 1) -> dict[str, Any]:
    return {
        "update_id": update_id,
        "callback_query": {
            "id": f"cq-{update_id}",
            "data": encode_callback(action, job_id),
            "message": {
                "message_id": 10,
                "chat": {"id": 999},
            },
        },
    }


async def test_approve_submits(db_ready: Path) -> None:
    job = await _seed_pending(external_id="wd-approve")
    assert job.id is not None
    transport = FakeTransport()
    client = TelegramClient(transport=transport, chat_id="999")
    submitter = FakeSubmitter(mode="ok")

    status = await handle_callback(
        _callback_update(job.id, ReviewAction.ok),
        client=client,
        submitter=submitter,
    )
    assert status == Status.submitted
    assert submitter.calls == [job.id]

    async with session_scope() as session:
        refreshed = await get_job_by_id(session, job.id)
        assert refreshed is not None
        assert refreshed.status == Status.submitted
        assert refreshed.decided_at is not None
        assert refreshed.screenshot_path == "/tmp/submitted.png"

    methods = [c["method"] for c in transport.calls]
    assert "editMessageCaption" in methods or "editMessageReplyMarkup" in methods
    assert "answerCallbackQuery" in methods


async def test_approve_blocker_manual(db_ready: Path) -> None:
    job = await _seed_pending(external_id="wd-block")
    assert job.id is not None
    transport = FakeTransport()
    client = TelegramClient(transport=transport, chat_id="999")
    status = await handle_callback(
        _callback_update(job.id, ReviewAction.ok),
        client=client,
        submitter=FakeSubmitter(mode="blocker"),
    )
    assert status == Status.manual_review
    async with session_scope() as session:
        refreshed = await get_job_by_id(session, job.id)
        assert refreshed is not None
        assert refreshed.status == Status.manual_review
        assert refreshed.screenshot_path == "/tmp/blocker.png"


async def test_manual_takeover(db_ready: Path) -> None:
    job = await _seed_pending(external_id="wd-manual")
    assert job.id is not None
    transport = FakeTransport()
    client = TelegramClient(transport=transport, chat_id="999")
    status = await handle_callback(
        _callback_update(job.id, ReviewAction.manual),
        client=client,
        submitter=FakeSubmitter(),
    )
    assert status == Status.manual_review
    async with session_scope() as session:
        refreshed = await get_job_by_id(session, job.id)
        assert refreshed is not None
        assert refreshed.status == Status.manual_review


async def test_discard(db_ready: Path) -> None:
    job = await _seed_pending(external_id="wd-discard")
    assert job.id is not None
    transport = FakeTransport()
    client = TelegramClient(transport=transport, chat_id="999")
    status = await handle_callback(
        _callback_update(job.id, ReviewAction.discard),
        client=client,
        submitter=FakeSubmitter(),
    )
    assert status == Status.ignored
    async with session_scope() as session:
        refreshed = await get_job_by_id(session, job.id)
        assert refreshed is not None
        assert refreshed.status == Status.ignored


async def test_unknown_job(db_ready: Path) -> None:
    transport = FakeTransport()
    client = TelegramClient(transport=transport, chat_id="999")
    status = await handle_callback(
        _callback_update(999999, ReviewAction.ok),
        client=client,
        submitter=FakeSubmitter(),
    )
    assert status is None
    assert any(c["method"] == "answerCallbackQuery" for c in transport.calls)


async def test_already_decided(db_ready: Path) -> None:
    job = await _seed_pending(external_id="wd-done")
    assert job.id is not None
    async with session_scope() as session:
        target = await get_job_by_id(session, job.id)
        assert target is not None
        target.status = Status.submitted
        session.add(target)

    transport = FakeTransport()
    client = TelegramClient(transport=transport, chat_id="999")
    status = await handle_callback(
        _callback_update(job.id, ReviewAction.ok),
        client=client,
        submitter=FakeSubmitter(),
    )
    assert status == Status.submitted
