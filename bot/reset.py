"""Start the queue over: clear waiting cards and drop off-target jobs from the pool.

Used once when the queue rules change. It never deletes job rows and never
touches jobs the owner already acted on (applied, skipped).
"""

from __future__ import annotations

from dataclasses import dataclass, field

import structlog

from bot.telegram import TelegramClient
from core.db import Job, Status, get_jobs_by_status, init_db, session_scope
from scraper.filters import target_title_reason

log = structlog.get_logger(__name__)


@dataclass
class ResetSummary:
    returned: int = 0
    deleted_messages: int = 0
    dropped: int = 0
    reasons: dict[str, int] = field(default_factory=dict)


async def _delete_cards(client: TelegramClient, jobs: list[Job]) -> int:
    """Delete each card, and the answers message sent right after it when there was one.

    Telegram only lets a bot delete its messages for 48 hours; older ones stay.
    """
    deleted = 0
    for job in jobs:
        if not job.review_message_id or not job.review_chat_id:
            continue
        ids = [job.review_message_id]
        if job.application_answers:
            ids.append(job.review_message_id + 1)
        for message_id in ids:
            try:
                if await client.delete_message(chat_id=job.review_chat_id, message_id=message_id):
                    deleted += 1
            except Exception as exc:
                log.info("reset_delete_skipped", job_id=job.id, error=str(exc)[:120])
    return deleted


async def reset_queue(client: TelegramClient | None = None) -> ResetSummary:
    await init_db()
    summary = ResetSummary()
    async with session_scope() as session:
        waiting = list(await get_jobs_by_status(session, Status.pending_review))
    if client is not None and waiting:
        summary.deleted_messages = await _delete_cards(client, waiting)

    async with session_scope() as session:
        for status in (Status.pending_review, Status.staged, Status.discovered, Status.scored):
            for job in await get_jobs_by_status(session, status):
                reason = target_title_reason(job.title or "", job.description_clean or "")
                if status == Status.pending_review:
                    job.review_message_id = None
                    job.review_chat_id = None
                    job.queued_at = None
                    job.shortlist_rank = None
                    job.shortlist_reason = None
                    job.status = Status.staged
                    summary.returned += 1
                if reason:
                    if job.score is None:
                        job.justification = [reason]
                    job.last_error = reason
                    job.status = Status.filtered_out
                    summary.dropped += 1
                    key = reason.split(":")[0]
                    summary.reasons[key] = summary.reasons.get(key, 0) + 1
                session.add(job)
    log.info(
        "queue_reset",
        returned=summary.returned,
        deleted_messages=summary.deleted_messages,
        dropped=summary.dropped,
    )
    return summary
