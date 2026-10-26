"""Apply queue on Telegram: one card per job with Applied / Skip / Later.

The agent never submits. The owner applies by hand (Simplify fills the form) and
taps a button. A pipeline run is one-shot, so taps are read on the next run
through ``sync_telegram``.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from enum import StrEnum
from typing import Any

import structlog

from automation.answers import AnswerResolver
from bot.review import format_answers_message
from bot.submit import SubmitResult
from bot.telegram import TelegramClient
from config.settings import get_settings
from core.db import (
    Job,
    Status,
    get_expired_queue_jobs,
    get_job_by_id,
    get_unsent_pending_reviews,
    init_db,
    session_scope,
)
from resume.kit import build_answers, has_kit, kit_lines

log = structlog.get_logger(__name__)

MESSAGE_MAX = 4096
_PREFIX = "q1"


class QueueAction(StrEnum):
    applied = "a"
    skip = "s"
    later = "l"


_LABELS = {
    QueueAction.applied: "APPLIED",
    QueueAction.skip: "SKIPPED",
    QueueAction.later: "LATER",
}


def encode_queue_callback(action: QueueAction, job_id: int) -> str:
    if job_id < 0:
        raise ValueError("job_id must be non-negative")
    return f"{_PREFIX}|{action.value}|{job_id}"


def decode_queue_callback(data: str) -> tuple[QueueAction, int]:
    parts = (data or "").strip().split("|")
    if len(parts) != 3 or parts[0] != _PREFIX:
        raise ValueError(f"Invalid queue callback_data: {data!r}")
    return QueueAction(parts[1]), int(parts[2])


def is_queue_callback(data: str) -> bool:
    return (data or "").startswith(f"{_PREFIX}|")


def build_queue_keyboard(job_id: int) -> dict[str, Any]:
    return {
        "inline_keyboard": [
            [
                {
                    "text": "Applied",
                    "callback_data": encode_queue_callback(QueueAction.applied, job_id),
                },
                {
                    "text": "Skip",
                    "callback_data": encode_queue_callback(QueueAction.skip, job_id),
                },
                {
                    "text": "Later",
                    "callback_data": encode_queue_callback(QueueAction.later, job_id),
                },
            ]
        ]
    }


def build_queue_text(job: Job) -> str:
    """Short card: what the role is, why it fits, and the direct link."""
    tier = job.tier.value if job.tier else "?"
    score = job.score if job.score is not None else "?"
    lines = [
        f"{job.title} @ {job.company}",
        f"Location: {job.location or 'N/A'}",
        f"Fit {score} | Tier {tier} | {job.role_family or 'role unknown'}",
    ]
    if job.justification:
        lines.append("Why: " + "; ".join(str(item) for item in job.justification[:2]))
    lines.extend(kit_lines(job))
    lines.append(f"Apply: {job.url}")
    lines.append("Tap Applied once you have submitted it yourself.")
    text = "\n".join(lines)
    return text if len(text) <= MESSAGE_MAX else text[: MESSAGE_MAX - 1] + "…"


@dataclass
class QueueSummary:
    sent: int = 0
    errors: int = 0
    error_details: list[str] = field(default_factory=list)


async def send_queue_cards(
    client: TelegramClient | None = None,
    *,
    limit: int | None = None,
    resolver: AnswerResolver | None = None,
) -> QueueSummary:
    """Send a card for every pending_review job that has none yet.

    Each new card also gets two drafted answers. A model failure only skips the answers.
    """
    await init_db()
    client = client or TelegramClient()
    summary = QueueSummary()
    async with session_scope() as session:
        jobs = await get_unsent_pending_reviews(session, limit=limit)
    for job in jobs:
        if job.id is None:
            continue
        try:
            if not has_kit(job):
                try:
                    payload = await build_answers(job, resolver)
                except Exception as exc:
                    log.warning("kit_answers_failed", job_id=job.id, error=str(exc)[:200])
                    payload = None
                if payload:
                    job.application_answers = payload
            result = await client.send_message(
                build_queue_text(job), reply_markup=build_queue_keyboard(job.id)
            )
            message_id = result.get("message_id")
            if message_id is None:
                raise RuntimeError("Telegram send returned no message_id")
            chat = result.get("chat") or {}
            chat_id = str(chat.get("id") or client.chat_id or "")
            async with session_scope() as session:
                target = await get_job_by_id(session, job.id)
                if target is None or target.status != Status.pending_review:
                    continue
                target.review_message_id = int(message_id)
                target.review_chat_id = chat_id or target.review_chat_id
                if job.application_answers and not has_kit(target):
                    target.application_answers = job.application_answers
                target.updated_at = datetime.now(UTC)
                session.add(target)
            answers_text = format_answers_message(job)
            if answers_text:
                try:
                    await client.send_message(answers_text, chat_id=chat_id or None)
                except Exception as exc:
                    log.warning("queue_answers_send_failed", job_id=job.id, error=str(exc)[:100])
            summary.sent += 1
        except Exception as exc:
            log.warning("send_queue_card_failed", job_id=job.id, error=str(exc)[:200])
            summary.errors += 1
            summary.error_details.append(f"job {job.id}: {str(exc)[:200]}")
    log.info("send_queue_cards_complete", sent=summary.sent, errors=summary.errors)
    return summary


async def expire_queue(*, now: datetime | None = None) -> int:
    """Close queued jobs nobody answered within QUEUE_EXPIRY_DAYS. Returns the count."""
    await init_db()
    moment = now or datetime.now(UTC)
    cutoff = moment - timedelta(days=get_settings().queue_expiry_days)
    async with session_scope() as session:
        expired = await get_expired_queue_jobs(session, cutoff)
        for job in expired:
            job.status = Status.ignored
            job.decided_at = moment
            job.updated_at = moment
            job.last_error = "queue expired without a decision"
            session.add(job)
    if expired:
        log.info("queue_expired", count=len(expired))
    return len(expired)


async def _safe_answer(client: TelegramClient, callback_id: str, text: str) -> None:
    if not callback_id:
        return
    try:
        await client.answer_callback_query(callback_id, text=text)
    except Exception as exc:
        log.warning("queue_answer_failed", error=str(exc)[:200])


async def handle_queue_callback(
    cq: dict[str, Any],
    *,
    client: TelegramClient,
) -> Status | None:
    """Apply one Applied / Skip / Later tap. A repeat tap changes nothing."""
    callback_id = str(cq.get("id") or "")
    message = cq.get("message") or {}
    chat_id = (message.get("chat") or {}).get("id")
    message_id = message.get("message_id")
    try:
        action, job_id = decode_queue_callback(str(cq.get("data") or ""))
    except ValueError as exc:
        log.warning("queue_callback_decode_failed", error=str(exc))
        await _safe_answer(client, callback_id, "Invalid button")
        return None

    now = datetime.now(UTC)
    async with session_scope() as session:
        job = await get_job_by_id(session, job_id)
        if job is None:
            await _safe_answer(client, callback_id, "Job not found")
            return None
        if job.status != Status.pending_review:
            await _safe_answer(client, callback_id, f"Already {job.status.value}")
            return job.status
        title, company = job.title, job.company
        job.decided_at = now
        job.updated_at = now
        if action == QueueAction.applied:
            job.status = Status.submitted
        elif action == QueueAction.skip:
            job.status = Status.ignored
        else:
            job.status = Status.staged
            job.decided_at = None
            job.queued_at = None
            job.review_message_id = None
            job.review_chat_id = None
            job.snoozed_until = now + timedelta(days=get_settings().queue_snooze_days)
        new_status = job.status
        session.add(job)

    from automation.tracker import record_submitted, record_withdrawn

    if action == QueueAction.applied:
        await record_submitted(job_id, occurred_at=now, source="telegram")
    elif action == QueueAction.skip:
        await record_withdrawn(job_id, occurred_at=now, source="telegram")

    edit_chat = chat_id if chat_id is not None else client.chat_id
    if edit_chat is not None and message_id is not None:
        try:
            await client.edit_message_text(
                chat_id=edit_chat,
                message_id=int(message_id),
                text=f"{title} @ {company}\n{_LABELS[action]}",
                reply_markup={"inline_keyboard": []},
            )
        except Exception as exc:
            log.warning("queue_edit_failed", job_id=job_id, error=str(exc)[:200])
    await _safe_answer(client, callback_id, _LABELS[action].title())
    log.info("queue_decision", job_id=job_id, action=action.name)
    return new_status


class NullSubmitter:
    """Sync never submits. A stale Approve button from an old card lands in manual review."""

    async def submit(self, job: Job) -> SubmitResult:
        return SubmitResult(submitted=False, reason="submit disabled in sync")


async def sync_telegram(client: TelegramClient | None = None) -> int:
    """Read taps made since the last run, apply them, then confirm them to Telegram.

    Returns the number of updates handled. Telegram keeps unconfirmed updates for
    24 hours, so a daily run loses nothing.
    """
    from bot.poller import process_updates

    await init_db()
    client = client or TelegramClient()
    updates = await client.get_updates(timeout=0)
    if not updates:
        return 0
    next_offset = await process_updates(updates, client=client, submitter=NullSubmitter())
    if next_offset is not None:
        await client.get_updates(offset=next_offset, timeout=0)
    log.info("telegram_sync_complete", handled=len(updates))
    return len(updates)
