"""Generate and deliver LinkedIn/Indeed application prep packs via Telegram."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime

import structlog
from sqlmodel import col, select

from bot.telegram import TelegramClient
from config.profile import Profile, load_profile
from config.settings import get_settings
from core.db import (
    Job,
    Status,
    get_job_by_id,
    get_unsent_prep_pack_jobs,
    init_db,
    session_scope,
)
from prep.builder import generate_prep_pack
from scorer.engine import LLMClient

log = structlog.get_logger(__name__)

STRONG_SCORE = 75
FILL_FLOOR = 60
SHORTLIST_FLOOR_COUNT = 20


def select_shortlist(jobs: list[Job]) -> list[Job]:
    """All scores above 75. If that is under 20, fill from scores of at least 60."""
    eligible = [
        job for job in jobs if job.score is not None and job.prep_pack_sent_at is None
    ]

    def _score(job: Job) -> int:
        return job.score if job.score is not None else 0

    strong = sorted(
        (job for job in eligible if _score(job) > STRONG_SCORE),
        key=lambda job: (-_score(job), job.id or 0),
    )
    if len(strong) >= SHORTLIST_FLOOR_COUNT:
        return strong
    fill = sorted(
        (job for job in eligible if FILL_FLOOR <= _score(job) <= STRONG_SCORE),
        key=lambda job: (-_score(job), job.id or 0),
    )
    need = SHORTLIST_FLOOR_COUNT - len(strong)
    return strong + fill[:need]


def render_shortlist(jobs: list[Job]) -> str:
    """Plain-text shortlist. Fill-band rows are marked so a 70 is not read as a 90."""
    lines: list[str] = []
    for index, job in enumerate(jobs, 1):
        score = int(job.score or 0)
        band = "" if score > STRONG_SCORE else "  [fill]"
        lines.append(
            f"{index}. {score}{band}  {job.title} @ {job.company}\n"
            f"    {job.location or 'N/A'}\n"
            f"    {job.url}"
        )
    return "\n\n".join(lines)


def shortlist_caption(jobs: list[Job]) -> str:
    strong = sum(1 for job in jobs if (job.score or 0) > STRONG_SCORE)
    return f"{len(jobs)} leads, {strong} above 75"


@dataclass
class PrepSummary:
    sent: int = 0
    jobs: int = 0
    skipped: int = 0
    errors: int = 0
    error_details: list[str] = field(default_factory=list)
    markdown_path: str | None = None
    pdf_path: str | None = None


async def _load_scored(job_ids: list[int]) -> list[Job]:
    found: list[Job] = []
    async with session_scope() as session:
        for job_id in job_ids:
            job = await get_job_by_id(session, job_id)
            if job is not None:
                found.append(job)
    return found


async def _unsent_scored_jobs() -> list[Job]:
    async with session_scope() as session:
        result = await session.exec(
            select(Job).where(
                col(Job.score).is_not(None),  # type: ignore[union-attr]
                col(Job.prep_pack_sent_at).is_(None),  # type: ignore[union-attr]
                col(Job.status).in_([Status.staged, Status.filtered_out]),  # type: ignore[union-attr]
            )
        )
        return list(result.all())


async def _mark_sent(jobs: list[Job], now: datetime) -> None:
    for job in jobs:
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


async def _send_shortlist_document(
    jobs: list[Job],
    client: TelegramClient,
) -> PrepSummary:
    """One text file for the run. Empty input sends nothing."""
    summary = PrepSummary()
    if not jobs:
        summary.skipped = 1
        log.info("send_prep_pack_empty")
        return summary

    settings = get_settings()
    stamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    path = settings.prep_packs_path / f"shortlist_{stamp}.txt"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(render_shortlist(jobs), encoding="utf-8")
    caption = shortlist_caption(jobs)
    try:
        await client.send_document(path, caption=caption)
    except Exception as exc:
        log.warning("prep_pack_send_failed", error=str(exc))
        summary.errors += 1
        summary.error_details.append(f"telegram: {exc}")
        return summary

    await _mark_sent(jobs, datetime.now(UTC))
    summary.sent = 1
    summary.jobs = len(jobs)
    summary.markdown_path = str(path)
    log.info(
        "send_prep_pack_complete",
        mode="shortlist",
        jobs=summary.jobs,
        above_75=sum(1 for job in jobs if (job.score or 0) > STRONG_SCORE),
        path=str(path),
    )
    return summary


async def send_prep_pack(
    client: TelegramClient | None = None,
    *,
    profile: Profile | None = None,
    llm_client: LLMClient | None = None,
    limit: int | None = None,
    job_ids: list[int] | None = None,
) -> PrepSummary:
    """Build and send a prep pack for unsent staged LinkedIn/Indeed jobs.

    Brief mode sends one shortlist text file: every score above 75, then
    scores of at least 60 until the file has 20. Nothing under 60 is included.

    Full mode (PREP_PACK_BRIEF=false): LLM-drafted answers + Typst PDF + Markdown.

    ``limit`` defaults to ``settings.prep_pack_limit`` (20).
    """
    await init_db()
    client = client or TelegramClient()
    profile = profile or load_profile()
    summary = PrepSummary()

    settings = get_settings()
    if settings.prep_pack_brief:
        if job_ids is not None:
            pool = await _load_scored(job_ids)
        else:
            pool = await _unsent_scored_jobs()
        return await _send_shortlist_document(select_shortlist(pool), client)

    effective_limit = limit if limit is not None else settings.prep_pack_limit

    async with session_scope() as session:
        jobs = await get_unsent_prep_pack_jobs(session, limit=effective_limit)

    if not jobs:
        log.info("send_prep_pack_empty")
        summary.skipped = 1
        return summary

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
