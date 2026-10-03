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
    get_job_by_id,
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
    """Legacy score fill. Production Telegram does not call this.

    The canonical shortlist is ``scorer.shortlist``. This helper remains for
    older tests only.
    """
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


EMPTY_SHORTLIST_MESSAGE = "No jobs are currently selected for review."


def _fit_lines(job: Job) -> list[str]:
    raw = job.fit_evidence if job.fit_evidence else job.justification
    if not isinstance(raw, list):
        return []
    return [str(item) for item in raw if str(item).strip()]


def _visa_state(job: Job) -> str | None:
    dimensions = job.eligibility_dimensions
    if not isinstance(dimensions, dict):
        return None
    visa = dimensions.get("VISA_SPONSORSHIP")
    if not isinstance(visa, dict):
        return None
    state = visa.get("state")
    if not isinstance(state, str) or not state.strip():
        return None
    return state.strip()


def _dedupe(jobs: list[Job]) -> list[Job]:
    seen: set[int] = set()
    unique: list[Job] = []
    for job in jobs:
        if job.id is None or job.id in seen:
            continue
        seen.add(job.id)
        unique.append(job)
    return unique


def render_job_card(index: int, job: Job) -> str:
    """One factual card. Missing fields are omitted. Nothing is inferred."""
    lines = [f"{index}. {job.title}", f"   {job.company}"]
    if job.location:
        lines.append(f"   {job.location}")
    lines.append("")
    if job.score is not None:
        lines.append(f"   Fit: {job.score}")
    if job.priority_score is not None:
        lines.append(f"   Priority: {job.priority_score}")
    if job.eligibility_state:
        lines.append(f"   Eligibility: {job.eligibility_state}")
    if job.role_family:
        lines.append(f"   Role: {job.role_family}")
    if job.role_secondary_family:
        lines.append(f"   Secondary role: {job.role_secondary_family}")
    if job.role_confidence:
        lines.append(f"   Confidence: {job.role_confidence}")
    reasons = _fit_lines(job)
    if reasons:
        lines.append("")
        lines.append("   Why it fits:")
        for reason in reasons:
            lines.append(f"   • {reason}")
    visa = _visa_state(job)
    if visa:
        lines.append("")
        lines.append(f"   Visa: {visa}")
    if job.source is not None:
        lines.append("")
        lines.append(f"   Source: {job.source.value}")
    if job.url:
        lines.append("")
        lines.append("   Apply:")
        lines.append(f"   {job.url}")
    return "\n".join(lines)


def render_shortlist(jobs: list[Job]) -> str:
    """Cards in the order given. Duplicate ids are shown once."""
    cards = [
        render_job_card(index, job)
        for index, job in enumerate(_dedupe(jobs), start=1)
    ]
    return "\n\n".join(cards)


def shortlist_caption(jobs: list[Job]) -> str:
    count = len(_dedupe(jobs))
    if count == 1:
        return "1 job selected for review"
    return f"{count} jobs selected for review"


@dataclass
class PrepSummary:
    sent: int = 0
    jobs: int = 0
    skipped: int = 0
    errors: int = 0
    error_details: list[str] = field(default_factory=list)
    markdown_path: str | None = None
    pdf_path: str | None = None


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
        path=str(path),
    )
    return summary


async def _load_canonical_shortlist() -> list[Job]:
    """Persisted shortlist rows, in shortlist order. Does not select jobs."""
    async with session_scope() as session:
        result = await session.exec(
            select(Job)
            .where(col(Job.shortlist_rank).is_not(None))  # type: ignore[union-attr]
            .order_by(col(Job.shortlist_rank), col(Job.id))
        )
        return _dedupe(list(result.all()))


async def _notify_empty(client: TelegramClient, summary: PrepSummary) -> PrepSummary:
    summary.skipped = 1
    try:
        await client.send_message(EMPTY_SHORTLIST_MESSAGE)
    except Exception as exc:
        log.warning("prep_pack_send_failed", error=str(exc))
        summary.errors += 1
        summary.error_details.append(f"telegram: {exc}")
        return summary
    log.info("send_prep_pack_empty")
    return summary


async def send_prep_pack(
    client: TelegramClient | None = None,
    *,
    profile: Profile | None = None,
    llm_client: LLMClient | None = None,
    limit: int | None = None,
    job_ids: list[int] | None = None,
) -> PrepSummary:
    """Deliver the persisted shortlist. This function does not choose jobs.

    Membership is ``shortlist_rank`` from ``scorer.shortlist``. Brief mode
    sends one text file of those unsent rows, in that order. An empty
    shortlist sends a notice and does not fill from other scores.

    Full mode (PREP_PACK_BRIEF=false) drafts answers only for that same set.

    ``job_ids`` and ``limit`` do not add or drop shortlist members.
    """
    del job_ids, limit
    await init_db()
    client = client or TelegramClient()
    profile = profile or load_profile()
    summary = PrepSummary()

    settings = get_settings()
    shortlist = await _load_canonical_shortlist()
    jobs = [job for job in shortlist if job.prep_pack_sent_at is None]
    if not shortlist:
        return await _notify_empty(client, summary)
    if not jobs:
        log.info("send_prep_pack_already_sent")
        summary.skipped = 1
        return summary
    if settings.prep_pack_brief:
        return await _send_shortlist_document(jobs, client)

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
