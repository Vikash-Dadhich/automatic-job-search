"""Generate and deliver LinkedIn/Indeed application prep packs via Telegram."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime

import structlog

from bot.telegram import TelegramClient
from config.profile import Profile, load_profile
from config.settings import get_settings
from core.db import (
    Job,
    get_job_by_id,
    get_unsent_prep_pack_jobs,
    init_db,
    session_scope,
)
from prep.builder import generate_prep_pack
from scorer.engine import LLMClient
from scraper.filters import sponsorship_signal

log = structlog.get_logger(__name__)


@dataclass
class PrepSummary:
    sent: int = 0
    jobs: int = 0
    skipped: int = 0
    errors: int = 0
    error_details: list[str] = field(default_factory=list)
    markdown_path: str | None = None
    pdf_path: str | None = None


_VISA_EMOJI = {
    "friendly": "🟢 Sponsors visa",
    "hostile": "🔴 No sponsorship",  # should not reach brief (filtered at ingest)
    "unknown": "⚠️ Sponsorship not mentioned — verify before applying",
}


def _brief_message(jobs: list[Job]) -> str:
    """Compact job list — no LLM, no PDF, just the 6 fields the user wants."""
    lines: list[str] = [f"🔍 {len(jobs)} new internship lead(s)\n"]
    for i, job in enumerate(jobs, 1):
        tier_num = job.tier.value if job.tier else "?"
        visa_status = sponsorship_signal(job.description_clean or "")
        visa_line = _VISA_EMOJI.get(visa_status, "⚠️ Sponsorship unknown")
        lines.append(
            f"{i}. {job.title} @ {job.company}\n"
            f"   📍 {job.location or 'N/A'}\n"
            f"   Score / Tier: {job.score} / {tier_num}\n"
            f"   Source: {job.source.value if job.source else '?'}\n"
            f"   🛂 {visa_line}\n"
            f"   🔗 {job.url}\n"
        )
    return "\n".join(lines).strip()


async def _send_brief(
    jobs: list[Job],
    client: TelegramClient,
) -> PrepSummary:
    """Send a compact text message — no LLM calls, no file uploads."""
    summary = PrepSummary()
    # Telegram message limit is 4096 chars; chunk if needed.
    CHUNK = 15
    chunks = [jobs[i : i + CHUNK] for i in range(0, len(jobs), CHUNK)]
    now = datetime.now(UTC)
    for chunk in chunks:
        text = _brief_message(chunk)
        try:
            await client.send_message(text)
            summary.sent += 1
        except Exception as exc:
            log.warning("prep_pack_brief_send_failed", error=str(exc))
            summary.errors += 1
            summary.error_details.append(f"telegram: {exc}")
            return summary

        for job in chunk:
            if job.id is None:
                continue
            try:
                async with session_scope() as session:
                    target = await get_job_by_id(session, job.id)
                    if target is None or target.prep_pack_sent_at is not None:
                        continue
                    target.prep_pack_sent_at = now
                    target.updated_at = now
                    session.add(target)
            except Exception as exc:
                log.warning("prep_pack_mark_failed", job_id=job.id, error=str(exc))

    summary.jobs = len(jobs)
    log.info(
        "send_prep_pack_complete",
        mode="brief",
        jobs=summary.jobs,
        sent=summary.sent,
        errors=summary.errors,
    )
    return summary


async def send_prep_pack(
    client: TelegramClient | None = None,
    *,
    profile: Profile | None = None,
    llm_client: LLMClient | None = None,
    limit: int | None = None,
) -> PrepSummary:
    """Build and send a prep pack for unsent staged LinkedIn/Indeed jobs.

    Brief mode (PREP_PACK_BRIEF=true): sends a compact Telegram text message with
    just title, location, score, source and URL — no LLM calls, no PDF.

    Full mode (default): generates LLM-drafted answers + Typst PDF + Markdown.
    Switch back by setting PREP_PACK_BRIEF=false.

    ``limit`` defaults to ``settings.prep_pack_limit`` (20).
    """
    await init_db()
    client = client or TelegramClient()
    profile = profile or load_profile()
    summary = PrepSummary()

    settings = get_settings()
    effective_limit = limit if limit is not None else settings.prep_pack_limit

    async with session_scope() as session:
        jobs = await get_unsent_prep_pack_jobs(session, limit=effective_limit)

    if not jobs:
        log.info("send_prep_pack_empty")
        summary.skipped = 1
        return summary

    # --- Brief mode: no LLM, no PDF ----------------------------------------
    if settings.prep_pack_brief:
        return await _send_brief(jobs, client)

    # --- Full mode: LLM essay drafting + Typst PDF --------------------------
    try:
        pack = await generate_prep_pack(
            jobs,
            profile=profile,
            client=llm_client,
        )
    except Exception as exc:
        log.warning("prep_pack_generate_failed", error=str(exc))
        summary.errors += 1
        summary.error_details.append(str(exc))
        return summary

    summary.error_details.extend(pack.errors)
    summary.errors += len(pack.errors)
    summary.jobs = pack.job_count

    if pack.job_count == 0:
        log.info("send_prep_pack_no_sections")
        return summary

    caption = (
        f"Application prep pack — {pack.job_count} LinkedIn/Indeed job(s)\n"
        f"Copy answers when you apply manually."
    )

    try:
        if pack.pdf_path is not None and pack.pdf_path.is_file():
            await client.send_document(pack.pdf_path, caption=caption)
            summary.pdf_path = str(pack.pdf_path)
            summary.sent += 1
        if pack.markdown_path is not None and pack.markdown_path.is_file():
            await client.send_document(
                pack.markdown_path,
                caption="Markdown copy (easy to paste from)",
            )
            summary.markdown_path = str(pack.markdown_path)
            summary.sent += 1
    except Exception as exc:
        log.warning("prep_pack_send_failed", error=str(exc))
        summary.errors += 1
        summary.error_details.append(f"telegram: {exc}")
        return summary

    now = datetime.now(UTC)
    for job_id in pack.job_ids:
        try:
            async with session_scope() as session:
                target = await get_job_by_id(session, job_id)
                if target is None:
                    continue
                if target.prep_pack_sent_at is not None:
                    continue
                target.prep_pack_sent_at = now
                target.updated_at = now
                session.add(target)
        except Exception as exc:
            log.warning("prep_pack_mark_failed", job_id=job_id, error=str(exc))
            summary.errors += 1
            summary.error_details.append(f"mark job {job_id}: {exc}")

    log.info(
        "send_prep_pack_complete",
        mode="full",
        jobs=summary.jobs,
        sent=summary.sent,
        errors=summary.errors,
        markdown=summary.markdown_path,
        pdf=summary.pdf_path,
    )
    return summary
