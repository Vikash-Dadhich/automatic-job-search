"""Offline tests for outcome labels, claim, and Telegram callbacks."""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from bot.handlers import handle_callback
from bot.outcomes import send_outcome_prompt
from bot.telegram import (
    CALLBACK_MAX_BYTES,
    ReviewAction,
    TelegramClient,
    decode_callback,
    decode_outcome_callback,
    encode_outcome_callback,
)
from core.db import (
    Job,
    Outcome,
    Source,
    Status,
    claim_outcome_prompt,
    get_job_by_id,
    release_outcome_prompt,
    session_scope,
    upsert_job,
)
from tests.test_handlers import FakeSubmitter, _callback_update
from tests.test_telegram import FakeTransport


def test_outcome_callback_roundtrip() -> None:
    data = encode_outcome_callback(Outcome.screening, 42)
    assert data == "o1|screening|42"
    assert len(data.encode("utf-8")) <= CALLBACK_MAX_BYTES
    outcome, job_id = decode_outcome_callback(data)
    assert outcome == Outcome.screening
    assert job_id == 42
    longest = encode_outcome_callback(Outcome.screening, 2_147_483_647)
    assert len(longest.encode("utf-8")) <= CALLBACK_MAX_BYTES


def test_review_decoder_rejects_outcome_payload() -> None:
    data = encode_outcome_callback(Outcome.interview, 7)
    try:
        decode_callback(data)
    except ValueError:
        return
    raise AssertionError("o1 payload must not decode as a review action")


async def _submitted(external_id: str, **extra: object) -> Job:
    job = Job(
        source=Source.workday,
        external_id=external_id,
        title="Backend Engineer",
        company="Acme",
        url="https://acme.wd5.myworkdayjobs.com/en-US/External/job/1",
        status=Status.submitted,
        decided_at=datetime(2026, 3, 1, tzinfo=UTC),
    )
    for key, value in extra.items():
        setattr(job, key, value)
    async with session_scope() as session:
        return await upsert_job(session, job)


async def test_claim_is_single_winner_and_release_retries(db_ready: Path) -> None:
    job = await _submitted("claim-1")
    assert job.id is not None
    async with session_scope() as session:
        assert await claim_outcome_prompt(session, job.id) is True
    async with session_scope() as session:
        assert await claim_outcome_prompt(session, job.id) is False
        await release_outcome_prompt(session, job.id)
    async with session_scope() as session:
        assert await claim_outcome_prompt(session, job.id) is True


async def test_failed_send_releases_claim(db_ready: Path) -> None:
    job = await _submitted("claim-fail")
    assert job.id is not None

    class BoomTransport(FakeTransport):
        async def post(
            self,
            method: str,
            payload: dict[str, Any] | None = None,
            *,
            files: dict[str, Any] | None = None,
            timeout: float | None = None,
        ) -> dict[str, Any]:
            if method == "sendMessage":
                raise RuntimeError("telegram down")
            return await super().post(method, payload, files=files, timeout=timeout)

    client = TelegramClient(transport=BoomTransport(), chat_id="999")
    assert await send_outcome_prompt(job.id, client) is False
    async with session_scope() as session:
        saved = await get_job_by_id(session, job.id)
        assert saved is not None
        assert saved.outcome_message_id is None


def _outcome_update(job_id: int, outcome: Outcome, *, update_id: int = 1) -> dict:
    return {
        "update_id": update_id,
        "callback_query": {
            "id": f"cq-{update_id}",
            "data": encode_outcome_callback(outcome, job_id),
            "message": {"message_id": 77, "chat": {"id": 999}},
        },
    }


async def test_outcome_tap_does_not_move_decided_at(db_ready: Path) -> None:
    decided = datetime(2026, 3, 1, tzinfo=UTC)
    job = await _submitted("label-1", decided_at=decided, outcome_message_id=77)
    assert job.id is not None
    transport = FakeTransport()
    client = TelegramClient(transport=transport, chat_id="999")
    status = await handle_callback(_outcome_update(job.id, Outcome.interview), client=client)
    assert status == Status.submitted
    async with session_scope() as session:
        saved = await get_job_by_id(session, job.id)
        assert saved is not None
        assert saved.outcome == "interview"
        assert saved.decided_at is not None
        assert saved.decided_at.replace(tzinfo=UTC) == decided
        assert saved.status == Status.submitted
    assert any(call["method"] == "editMessageText" for call in transport.calls)

    status_again = await handle_callback(
        _outcome_update(job.id, Outcome.offer, update_id=2),
        client=client,
    )
    assert status_again == Status.submitted
    async with session_scope() as session:
        saved = await get_job_by_id(session, job.id)
        assert saved is not None
        assert saved.outcome == "offer"
        assert saved.decided_at is not None
        assert saved.decided_at.replace(tzinfo=UTC) == decided


async def test_outcome_tap_rejected_unless_submitted(db_ready: Path) -> None:
    job = Job(
        source=Source.workday,
        external_id="label-pending",
        title="Backend Engineer",
        company="Acme",
        url="https://acme.wd5.myworkdayjobs.com/en-US/External/job/2",
        status=Status.pending_review,
    )
    async with session_scope() as session:
        job = await upsert_job(session, job)
    assert job.id is not None
    client = TelegramClient(transport=FakeTransport(), chat_id="999")
    status = await handle_callback(_outcome_update(job.id, Outcome.rejected), client=client)
    assert status == Status.pending_review
    async with session_scope() as session:
        saved = await get_job_by_id(session, job.id)
        assert saved is not None
        assert saved.outcome is None


async def test_approve_still_submits(db_ready: Path) -> None:
    job = Job(
        source=Source.workday,
        external_id="approve-still",
        title="Backend Engineer",
        company="Acme",
        url="https://acme.wd5.myworkdayjobs.com/en-US/External/job/3",
        status=Status.pending_review,
        review_message_id=10,
        review_chat_id="999",
    )
    async with session_scope() as session:
        job = await upsert_job(session, job)
    assert job.id is not None
    transport = FakeTransport()
    client = TelegramClient(transport=transport, chat_id="999")
    status = await handle_callback(
        _callback_update(job.id, ReviewAction.ok),
        client=client,
        submitter=FakeSubmitter(mode="ok"),
    )
    assert status == Status.submitted
    async with session_scope() as session:
        saved = await get_job_by_id(session, job.id)
        assert saved is not None
        assert saved.status == Status.submitted
        assert saved.outcome_message_id == 43
    assert any(call["method"] == "sendMessage" for call in transport.calls)
