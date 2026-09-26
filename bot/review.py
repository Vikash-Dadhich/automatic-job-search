"""Build and send Telegram review cards for pending_review jobs."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import structlog

from bot.telegram import ReviewAction, TelegramClient, encode_callback
from core.db import (
    Job,
    Status,
    get_job_by_id,
    get_unsent_pending_reviews,
    init_db,
    session_scope,
)

log = structlog.get_logger(__name__)

CAPTION_MAX = 1024
MESSAGE_MAX = 4096


@dataclass
class ReviewSummary:
    sent: int = 0
    skipped: int = 0
    errors: int = 0
    error_details: list[str] = field(default_factory=list)


def build_keyboard(job_id: int) -> dict[str, Any]:
    """Inline keyboard: Approve / Manual Takeover / Discard."""
    return {
        "inline_keyboard": [
            [
                {
                    "text": "Approve",
                    "callback_data": encode_callback(ReviewAction.ok, job_id),
                },
                {
                    "text": "Manual Takeover",
                    "callback_data": encode_callback(ReviewAction.manual, job_id),
                },
                {
                    "text": "Discard",
                    "callback_data": encode_callback(ReviewAction.discard, job_id),
                },
            ]
        ]
    }


def build_review_caption(job: Job, *, max_len: int = CAPTION_MAX) -> str:
    """Compact review caption fitting Telegram photo caption limits."""
    tier = job.tier.value if job.tier else "?"
    score = job.score if job.score is not None else "?"
    source = job.source.value if job.source else "?"
    lines = [
        f"{job.title} @ {job.company}",
        f"Location: {job.location or 'N/A'}",
        f"Score: {score} | Tier: {tier} | Source: {source}",
        f"URL: {job.url}",
    ]
    if job.tier and job.tier.value == "one" and job.outreach_draft:
        lines.append("Outreach draft ready (Tier 1).")
    if job.cover_letter:
        lines.append("Cover letter ready (Tier 1).")
    if job.justification:
        reasons = "; ".join(job.justification[:3])
        lines.append(f"Why: {reasons}")
    lines.append("Approve = submit | Manual = you take over | Discard = ignore")
    text = "\n".join(lines)
    if len(text) > max_len:
        text = text[: max_len - 1] + "…"
    return text


def format_answers_message(job: Job, *, max_len: int = MESSAGE_MAX) -> str | None:
    """Optional follow-up text with drafted application answers."""
    payload = job.application_answers
    if not payload or not isinstance(payload, dict):
        return None
    items = payload.get("items") or []
    if not items:
        return None
    lines = [f"Drafted answers for job #{job.id}:"]
    for item in items:
        if not isinstance(item, dict):
            continue
        q = str(item.get("question") or "").strip()
        a = str(item.get("answer") or "").strip()
        src = str(item.get("source") or "").strip()
        if not q:
            continue
        if a:
            lines.append(f"• {q}\n  → {a} ({src})")
        else:
            lines.append(f"• {q}\n  → (blank)")
    text = "\n".join(lines)
    if len(text) > max_len:
        text = text[: max_len - 1] + "…"
    return text


def format_cover_letter_message(job: Job, *, max_len: int = MESSAGE_MAX) -> str | None:
    """Follow-up text with the stored cover letter, if one was drafted."""
    letter = (job.cover_letter or "").strip()
    if not letter:
        return None
    text = f"Cover letter for job #{job.id}:\n\n{letter}"
    if len(text) > max_len:
        text = text[: max_len - 1] + "…"
    return text


async def send_pending_reviews(
    client: TelegramClient | None = None,
    *,
    limit: int | None = None,
) -> ReviewSummary:
    """Send Telegram review cards for unsent pending_review jobs."""
    await init_db()
    client = client or TelegramClient()
    summary = ReviewSummary()

    async with session_scope() as session:
        jobs = await get_unsent_pending_reviews(session, limit=limit)

    if not jobs:
        log.info("send_pending_reviews_empty")
        return summary

    for job in jobs:
        if job.id is None:
            summary.skipped += 1
            continue
        try:
            await _send_one(client, job)
            summary.sent += 1
        except Exception as exc:
            log.warning("send_review_failed", job_id=job.id, error=str(exc))
            summary.errors += 1
            summary.error_details.append(f"job {job.id}: {exc}")

    log.info(
        "send_pending_reviews_complete",
        sent=summary.sent,
        skipped=summary.skipped,
        errors=summary.errors,
    )
    return summary


async def _send_one(client: TelegramClient, job: Job) -> None:
    assert job.id is not None
    caption = build_review_caption(job)
    keyboard = build_keyboard(job.id)
    screenshot = Path(job.screenshot_path) if job.screenshot_path else None

    if screenshot is not None and screenshot.is_file():
        result = await client.send_photo(
            screenshot,
            caption=caption,
            reply_markup=keyboard,
        )
    else:
        log.warning("review_missing_screenshot", job_id=job.id)
        result = await client.send_message(
            caption,
            reply_markup=keyboard,
        )

    message_id = result.get("message_id")
    chat = result.get("chat") or {}
    chat_id = str(chat.get("id") or client.chat_id or "")
    if message_id is None:
        raise RuntimeError(f"Telegram send returned no message_id for job {job.id}")

    answers_text = format_answers_message(job)
    if answers_text:
        try:
            await client.send_message(answers_text, chat_id=chat_id or None)
        except Exception as exc:
            log.warning("send_answers_followup_failed", job_id=job.id, error=str(exc))

    letter_text = format_cover_letter_message(job)
    if letter_text:
        try:
            await client.send_message(letter_text, chat_id=chat_id or None)
        except Exception as exc:
            log.warning("send_cover_letter_followup_failed", job_id=job.id, error=str(exc))

    now = datetime.now(UTC)
    async with session_scope() as session:
        target = await get_job_by_id(session, job.id)
        if target is None:
            raise ValueError(f"job {job.id} missing")
        if target.status != Status.pending_review:
            log.info("send_review_status_changed", job_id=job.id, status=target.status)
            return
        target.review_message_id = int(message_id)
        target.review_chat_id = chat_id or target.review_chat_id
        target.updated_at = now
        session.add(target)
