"""Telegram outcome keyboards for jobs that were actually submitted."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import structlog

from bot.telegram import TelegramClient, encode_outcome_callback
from core.db import (
    Job,
    Outcome,
    Status,
    claim_outcome_prompt,
    finish_outcome_prompt,
    get_job_by_id,
    get_jobs_needing_outcome_prompt,
    init_db,
    release_outcome_prompt,
    session_scope,
)

log = structlog.get_logger(__name__)

OUTCOME_LABELS: dict[Outcome, str] = {
    Outcome.ghosted: "No reply",
    Outcome.screening: "Screening",
    Outcome.interview: "Interview",
    Outcome.rejected: "Rejected",
    Outcome.offer: "Offer",
}


@dataclass
class OutcomePromptSummary:
    sent: int = 0
    skipped: int = 0


def outcome_label(outcome: Outcome) -> str:
    return OUTCOME_LABELS[outcome]


def build_outcome_keyboard(job_id: int) -> dict[str, Any]:
    """Two-row keyboard. Callbacks stay well under Telegram's 64-byte cap."""

    def button(text: str, outcome: Outcome) -> dict[str, str]:
        return {
            "text": text,
            "callback_data": encode_outcome_callback(outcome, job_id),
        }

    return {
        "inline_keyboard": [
            [
                button("No reply", Outcome.ghosted),
                button("Screening", Outcome.screening),
                button("Interview", Outcome.interview),
            ],
            [
                button("Rejected", Outcome.rejected),
                button("Offer", Outcome.offer),
            ],
        ]
    }


def outcome_message_text(job: Job, outcome: Outcome | None = None) -> str:
    lines = [f"{job.title} @ {job.company}"]
    if outcome is None:
        lines.append("How did this application turn out?")
    else:
        lines.append(f"Outcome: {outcome_label(outcome)}")
        lines.append("Tap again to update.")
    return "\n".join(lines)


async def send_outcome_prompt(
    job_id: int,
    client: TelegramClient | None = None,
) -> bool:
    """Send one outcome keyboard. Never raises. False when the claim loses or send fails."""
    try:
        await init_db()
        client = client or TelegramClient()
        async with session_scope() as session:
            job = await get_job_by_id(session, job_id)
            if job is None or job.status != Status.submitted:
                return False
            # Copy before the session closes; the ORM expires attributes on commit.
            source = job.source
            external_id = job.external_id
            title = job.title
            company = job.company
            url = job.url
            if not await claim_outcome_prompt(session, job_id):
                return False
        prompt_job = Job(
            source=source,
            external_id=external_id,
            title=title,
            company=company,
            url=url,
        )
        try:
            result = await client.send_message(
                outcome_message_text(prompt_job),
                reply_markup=build_outcome_keyboard(job_id),
            )
            message_id = result.get("message_id")
            if not isinstance(message_id, int) or message_id <= 0:
                raise RuntimeError(f"Telegram send returned no message_id for job {job_id}")
        except Exception as exc:
            async with session_scope() as session:
                await release_outcome_prompt(session, job_id)
            log.warning("outcome_prompt_failed", job_id=job_id, error=str(exc)[:200])
            return False
        async with session_scope() as session:
            await finish_outcome_prompt(session, job_id, message_id)
        return True
    except Exception as exc:
        log.warning("outcome_prompt_failed", job_id=job_id, error=str(exc)[:200])
        return False


async def send_pending_outcome_prompts(
    client: TelegramClient | None = None,
    *,
    limit: int | None = None,
) -> OutcomePromptSummary:
    """Backfill outcome keyboards for submitted jobs that never got one."""
    await init_db()
    client = client or TelegramClient()
    summary = OutcomePromptSummary()
    async with session_scope() as session:
        jobs = await get_jobs_needing_outcome_prompt(session, limit=limit)
    for job in jobs:
        if job.id is None:
            summary.skipped += 1
            continue
        if await send_outcome_prompt(job.id, client):
            summary.sent += 1
        else:
            summary.skipped += 1
    log.info(
        "outcome_prompts_complete",
        sent=summary.sent,
        skipped=summary.skipped,
    )
    return summary
