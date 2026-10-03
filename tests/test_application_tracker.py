"""Application history starts only when an application does."""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

import pytest
from sqlmodel import select

from automation.runner import apply_pending
from automation.tracker import application_history, record_outcome, record_submitted
from automation.workday import ApplyResult, BlockerError
from bot.handlers import handle_callback
from bot.submit import SubmitResult
from bot.telegram import ReviewAction, TelegramClient, encode_callback, encode_outcome_callback
from core.db import (
    Application,
    Job,
    Outcome,
    Source,
    Status,
    get_application_for_job,
    get_job_by_id,
    init_db,
    session_scope,
    upsert_job,
)
from tests.test_telegram import FakeTransport

WHEN = datetime(2026, 10, 2, 15, 0, tzinfo=UTC)


def _job(external_id: str, **kwargs: object) -> Job:
    data: dict[str, object] = {
        "source": Source.linkedin,
        "external_id": external_id,
        "title": "Intern",
        "company": "Acme",
        "url": f"https://jobs.example.com/{external_id}",
        "status": Status.staged,
        "score": 80,
        "priority_score": 70,
    }
    data.update(kwargs)
    return Job(**data)  # type: ignore[arg-type]


class _Prefill:
    async def apply(self, job: Job) -> ApplyResult:
        del job
        return ApplyResult(screenshot_path="/tmp/review.png", reached_review=True)


class _Blocker:
    async def apply(self, job: Job) -> ApplyResult:
        del job
        raise BlockerError("cloudflare", screenshot_path="/tmp/block.png")


class _Submitter:
    def __init__(self, *, submitted: bool) -> None:
        self.submitted = submitted

    async def submit(self, job: Job) -> SubmitResult:
        del job
        if self.submitted:
            return SubmitResult(submitted=True, screenshot_path="/tmp/ok.png", reason="submitted")
        return SubmitResult(submitted=False, screenshot_path="/tmp/no.png", reason="cloudflare")


def _tap(job_id: int, action: ReviewAction) -> dict[str, object]:
    return {
        "update_id": 1,
        "callback_query": {
            "id": "cq",
            "data": encode_callback(action, job_id),
            "message": {"message_id": 10, "chat": {"id": 999}},
        },
    }


async def _count() -> int:
    async with session_scope() as session:
        result = await session.exec(select(Application))
        return len(list(result.all()))


async def test_staging_and_portfolio_do_not_create_an_application(db_ready: Path) -> None:
    del db_ready
    async with session_scope() as session:
        staged = await upsert_job(session, _job("staged-only"))
        allocated = await upsert_job(
            session,
            _job(
                "allocated",
                source=Source.workday,
                resume_path="/tmp/resume.pdf",
                url="https://acme.wd5.myworkdayjobs.com/en-US/External/job/1",
                portfolio_decision="ALLOCATED",
                status=Status.staged,
            ),
        )
        review = await upsert_job(session, _job("review-only", status=Status.pending_review))
        assert staged.id and allocated.id and review.id
    assert await _count() == 0


async def test_prefill_starts_an_application_without_submitting(db_ready: Path) -> None:
    del db_ready
    async with session_scope() as session:
        job = await upsert_job(
            session,
            _job(
                "prefill",
                source=Source.workday,
                resume_path="/tmp/resume.pdf",
                url="https://acme.wd5.myworkdayjobs.com/en-US/External/job/2",
                portfolio_decision="ALLOCATED",
            ),
        )
        assert job.id
    await apply_pending(applicator=_Prefill(), job_ids=[job.id])
    await apply_pending(applicator=_Prefill(), job_ids=[job.id])
    async with session_scope() as session:
        saved = await get_job_by_id(session, job.id)
        app = await get_application_for_job(session, job.id)
        assert saved is not None and app is not None
        assert saved.status == Status.pending_review
        assert app.state == "in_progress"
        assert app.submitted_at is None
        assert app.method == "workday"
        assert app.tracker_version == "phase15-v1"
    events = await application_history(job.id)
    assert [event.event_type for event in events] == ["started"]
    assert await _count() == 1


async def test_blocker_and_manual_takeover_are_not_submissions(db_ready: Path) -> None:
    del db_ready
    async with session_scope() as session:
        blocked = await upsert_job(
            session,
            _job(
                "blocked",
                source=Source.workday,
                resume_path="/tmp/resume.pdf",
                url="https://acme.wd5.myworkdayjobs.com/en-US/External/job/3",
                portfolio_decision="ALLOCATED",
            ),
        )
        manual = await upsert_job(
            session,
            _job(
                "manual",
                status=Status.pending_review,
                review_message_id=10,
                review_chat_id="999",
                source=Source.linkedin,
            ),
        )
        assert blocked.id and manual.id
    await apply_pending(applicator=_Blocker(), job_ids=[blocked.id])
    client = TelegramClient(transport=FakeTransport(), chat_id="999")
    await handle_callback(
        _tap(manual.id, ReviewAction.manual),
        client=client,
        submitter=_Submitter(submitted=True),
    )
    async with session_scope() as session:
        blocked_job = await get_job_by_id(session, blocked.id)
        blocked_app = await get_application_for_job(session, blocked.id)
        manual_job = await get_job_by_id(session, manual.id)
        manual_app = await get_application_for_job(session, manual.id)
        assert blocked_job is not None and blocked_app is not None
        assert blocked_job.status == Status.manual_review
        assert blocked_app.state == "manual_review"
        assert blocked_app.submitted_at is None
        assert manual_job is not None and manual_app is not None
        assert manual_job.status == Status.manual_review
        assert manual_app.state == "manual_review"
        assert manual_app.submitted_at is None
        assert manual_app.method == "manual"


async def test_submit_is_idempotent_and_discard_without_an_attempt_is_empty(db_ready: Path) -> None:
    del db_ready
    async with session_scope() as session:
        job = await upsert_job(
            session,
            _job(
                "submit",
                status=Status.pending_review,
                review_message_id=10,
                review_chat_id="999",
            ),
        )
        discarded = await upsert_job(
            session,
            _job(
                "discard",
                status=Status.pending_review,
                review_message_id=10,
                review_chat_id="999",
            ),
        )
        assert job.id and discarded.id
    client = TelegramClient(transport=FakeTransport(), chat_id="999")
    status = await handle_callback(
        _tap(job.id, ReviewAction.ok),
        client=client,
        submitter=_Submitter(submitted=True),
    )
    assert status == Status.submitted
    await handle_callback(
        _tap(job.id, ReviewAction.ok),
        client=client,
        submitter=_Submitter(submitted=True),
    )
    await handle_callback(
        _tap(discarded.id, ReviewAction.discard),
        client=client,
        submitter=_Submitter(submitted=True),
    )
    async with session_scope() as session:
        app = await get_application_for_job(session, job.id)
        none = await get_application_for_job(session, discarded.id)
        saved = await get_job_by_id(session, job.id)
        assert app is not None and saved is not None and none is None
        assert app.state == "submitted"
        assert app.submitted_at is not None
        first_submitted = app.submitted_at
        assert saved.score == 80
        saved.priority_score = 1
        saved.score = 1
        session.add(saved)
    await record_submitted(job.id, occurred_at=datetime(2027, 1, 1, tzinfo=UTC), source="telegram")
    async with session_scope() as session:
        app = await get_application_for_job(session, job.id)
        saved = await get_job_by_id(session, job.id)
        assert app is not None and saved is not None
        assert app.submitted_at == first_submitted
        assert app.state == "submitted"
        assert saved.priority_score == 1
    events = await application_history(job.id)
    assert [event.event_type for event in events] == ["started", "submitted"]


@pytest.mark.parametrize("outcome", list(Outcome))
async def test_each_outcome_is_stored_once(db_ready: Path, outcome: Outcome) -> None:
    del db_ready
    async with session_scope() as session:
        job = await upsert_job(
            session,
            _job("out-" + outcome.value, status=Status.submitted, decided_at=WHEN),
        )
        assert job.id
    await init_db()
    async with session_scope() as session:
        app = await get_application_for_job(session, job.id)
        assert app is not None
        assert app.submitted_at is not None
        assert app.submitted_at.replace(tzinfo=UTC) == WHEN
        assert app.state == "submitted"
    client = TelegramClient(transport=FakeTransport(), chat_id="999")
    update = {
        "update_id": 1,
        "callback_query": {
            "id": "cq",
            "data": encode_outcome_callback(outcome, job.id),
            "message": {"message_id": 77, "chat": {"id": 999}},
        },
    }
    await handle_callback(update, client=client)
    await handle_callback(update, client=client)
    events = await application_history(job.id)
    outcome_events = [event for event in events if event.event_type == outcome.value]
    assert len(outcome_events) == 1
    async with session_scope() as session:
        app = await get_application_for_job(session, job.id)
        saved = await get_job_by_id(session, job.id)
        assert app is not None and saved is not None
        assert app.outcome == outcome.value
        assert saved.outcome == outcome.value
        assert saved.status == Status.submitted
        stamped = app.outcome_at
    await record_outcome(
        job.id,
        outcome,
        occurred_at=datetime(2027, 2, 2, tzinfo=UTC),
        source="telegram",
    )
    events_again = await application_history(job.id)
    assert [event.event_type for event in events_again].count(outcome.value) == 1
    async with session_scope() as session:
        app = await get_application_for_job(session, job.id)
        assert app is not None
        assert app.outcome_at == stamped


async def test_a_later_outcome_keeps_the_earlier_event(db_ready: Path) -> None:
    del db_ready
    async with session_scope() as session:
        job = await upsert_job(
            session,
            _job("later", status=Status.submitted, decided_at=WHEN),
        )
        assert job.id
    client = TelegramClient(transport=FakeTransport(), chat_id="999")

    def update(outcome: Outcome, update_id: int) -> dict[str, object]:
        return {
            "update_id": update_id,
            "callback_query": {
                "id": f"cq-{update_id}",
                "data": encode_outcome_callback(outcome, job.id or 0),
                "message": {"message_id": 77, "chat": {"id": 999}},
            },
        }

    await handle_callback(update(Outcome.ghosted, 1), client=client)
    await handle_callback(update(Outcome.interview, 2), client=client)
    events = await application_history(job.id)
    ghosted = next(event for event in events if event.event_type == "ghosted")
    assert any(event.event_type == "interview" for event in events)
    async with session_scope() as session:
        app = await get_application_for_job(session, job.id)
        assert app is not None
        assert app.outcome == "interview"
    later = await application_history(job.id)
    kept = next(event for event in later if event.event_type == "ghosted")
    assert ghosted.occurred_at == kept.occurred_at
