"""Tier-1 cover letter drafting with the same anti-AI gate as outreach."""

from __future__ import annotations

from typing import TYPE_CHECKING

import structlog

from config.profile import Profile
from config.settings import get_settings
from core.db import Job
from scorer.outreach import contains_banned, strip_banned_sentences
from scorer.prompts import COVER_LETTER_SYSTEM, build_cover_letter_user

if TYPE_CHECKING:
    from scorer.clients import LLMClient

log = structlog.get_logger(__name__)

COVER_LETTER_MAX_CHARS = 1500


def cap_cover_letter(text: str, *, limit: int = COVER_LETTER_MAX_CHARS) -> str:
    """Trim to the last sentence that fits, so a runaway letter stays usable."""
    cleaned = text.strip()
    if len(cleaned) <= limit:
        return cleaned
    window = cleaned[:limit]
    boundary = max(window.rfind("."), window.rfind("!"), window.rfind("?"))
    if boundary > 0:
        return window[: boundary + 1].strip()
    return window.strip()


def _fallback_cover_letter(job: Job, profile: Profile) -> str:
    """Deterministic letter used when the model keeps failing the style gate."""
    role = (job.title or "this role").strip()
    company = (job.company or "your team").strip()
    name = profile.identity.full_name.strip() or "I"
    result = "My recent work lines up with what this posting describes."
    if profile.experience and profile.experience[0].bullets:
        bullet = profile.experience[0].bullets[0].strip()
        if bullet and not contains_banned(bullet):
            result = bullet if bullet.endswith((".", "!", "?")) else f"{bullet}."
    return (
        f"I am applying for the {role} role at {company}. "
        f"{name} — the posting matches work I have already done. "
        f"{result}"
    )


async def generate_cover_letter(
    job: Job,
    profile: Profile,
    client: LLMClient,
) -> str:
    """Draft a short cover letter; retry once if banned words appear."""
    settings = get_settings()
    system_blocks = [{"type": "text", "text": COVER_LETTER_SYSTEM}]
    user = build_cover_letter_user(job, profile)

    draft = (
        await client.complete(
            model=settings.active_writer_model,
            system_blocks=system_blocks,
            user=user,
            max_tokens=settings.writer_max_tokens,
            temperature=0.7,
            thinking_level=settings.gemini_writer_thinking_level,
        )
    ).strip()

    banned = contains_banned(draft)
    if banned:
        log.info("cover_letter_banned_retry", banned=banned, job_id=job.id)
        retry_user = (
            f"{user}\n\nRewrite without these phrases: {', '.join(banned)}. "
            "Keep 3 to 5 sentences."
        )
        draft = (
            await client.complete(
                model=settings.active_writer_model,
                system_blocks=system_blocks,
                user=retry_user,
                max_tokens=settings.writer_max_tokens,
                temperature=0.5,
                thinking_level=settings.gemini_writer_thinking_level,
            )
        ).strip()
        if contains_banned(draft):
            stripped = strip_banned_sentences(draft)
            draft = stripped or _fallback_cover_letter(job, profile)

    if not draft.strip():
        draft = _fallback_cover_letter(job, profile)
    return cap_cover_letter(draft)
