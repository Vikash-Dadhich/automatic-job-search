"""Telegram alerts for blocked / errored jobs (not pending_review cards)."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path

import structlog

from bot.telegram import TelegramClient
from core.db import (
    Job,
    Status,
    get_job_by_id,
    get_unsent_alerts,
    init_db,
    session_scope,
)

log = structlog.get_logger(__name__)

CAPTION_MAX = 1024


@dataclass
class AlertSummary:
    sent: int = 0
    skipped: int = 0
    errors: int = 0
    error_details: list[str] = field(default_factory=list)


def build_alert_caption(job: Job, *, max_len: int = CAPTION_MAX) -> str:
    """Caption for a blocker / error alert."""
    status = job.status.value if job.status else "?"
    reason = (job.last_error or "No details").strip()
    lines = [
        f"ALERT [{status.upper()}]",
        f"{job.title} @ {job.company}",
        f"Location: {job.location or 'N/A'}",
        f"URL: {job.url}",
        f"Reason: {reason}",
    ]
    text = "\n".join(lines)
    if len(text) > max_len:
        text = text[: max_len - 1] + "…"
    return text


async def send_pending_alerts(
    client: TelegramClient | None = None,
    *,
    limit: int | None = None,
) -> AlertSummary:
    """Notify on unsent manual_review / error jobs (screenshot + reason)."""
    await init_db()
    client = client or TelegramClient()
    summary = AlertSummary()

    async with session_scope() as session:
        jobs = await get_unsent_alerts(session, limit=limit)

    if not jobs:
        log.info("send_pending_alerts_empty")
        return summary

    for job in jobs:
        if job.id is None:
            summary.skipped += 1
            continue
        # Manual takeover / discard via Telegram already decided — still alert
        # only when alerted_at is null (query already filters that).
        try:
            await _send_one(client, job)
            summary.sent += 1
        except Exception as exc:
            log.warning("send_alert_failed", job_id=job.id, error=str(exc))
            summary.errors += 1
            summary.error_details.append(f"job {job.id}: {exc}")

    log.info(
        "send_pending_alerts_complete",
        sent=summary.sent,
        skipped=summary.skipped,
        errors=summary.errors,
    )
    return summary


async def _send_one(client: TelegramClient, job: Job) -> None:
    assert job.id is not None
    caption = build_alert_caption(job)
    screenshot = Path(job.screenshot_path) if job.screenshot_path else None

    if screenshot is not None and screenshot.is_file():
        await client.send_photo(screenshot, caption=caption)
    else:
        await client.send_message(caption)

    now = datetime.now(UTC)
    async with session_scope() as session:
        target = await get_job_by_id(session, job.id)
        if target is None:
            raise ValueError(f"job {job.id} missing")
        if target.status not in {Status.manual_review, Status.error}:
            log.info(
                "send_alert_status_changed",
                job_id=job.id,
                status=target.status,
            )
            return
        if target.alerted_at is not None:
            return
        target.alerted_at = now
        target.updated_at = now
        session.add(target)
