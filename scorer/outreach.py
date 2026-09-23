"""Tier-1 alumni/referral outreach drafting with anti-AI style gate."""

from __future__ import annotations

import re
from typing import TYPE_CHECKING

import structlog

from config.profile import Profile
from config.settings import get_settings
from core.db import Job
from core.textmatch import contains_phrase
from scorer.prompts import BANNED_WORDS, OUTREACH_SYSTEM, build_outreach_user

if TYPE_CHECKING:
    from scorer.clients import LLMClient

log = structlog.get_logger(__name__)


def contains_banned(text: str) -> list[str]:
    """Return banned phrases present as whole words (case-insensitive)."""
    if not text:
        return []
    return [word for word in BANNED_WORDS if contains_phrase(text, word)]


def strip_banned_sentences(text: str) -> str:
    """Drop sentences that contain banned words; keep the rest."""
    sentences = re.split(r"(?<=[.!?])\s+", text.strip())
    kept = [s for s in sentences if s and not contains_banned(s)]
    return " ".join(kept).strip()


# Back-compat alias for existing internal callers.
_strip_banned_sentences = strip_banned_sentences


async def generate_outreach(
    job: Job,
    profile: Profile,
    client: LLMClient,
) -> str:
    """Draft a 3-sentence outreach note; retry once if banned words appear."""
    settings = get_settings()
    system_blocks = [{"type": "text", "text": OUTREACH_SYSTEM}]
    user = build_outreach_user(job, profile)

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
        log.info("outreach_banned_retry", banned=banned, job_id=job.id)
        retry_user = (
            f"{user}\n\nRewrite without these phrases: {', '.join(banned)}. "
            "Keep exactly 3 sentences."
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
            # Stripping every sentence would leave an empty outreach card; fall
            # back to a grounded note rather than shipping banned filler.
            draft = stripped or _fallback_outreach(job, profile)

    return draft


def _fallback_outreach(job: Job, profile: Profile) -> str:
    """Deterministic, profile-grounded note used when the model keeps failing the gate."""
    role = (job.title or "the role").strip()
    company = (job.company or "your team").strip()
    current = profile.experience[0].title if profile.experience else "my current role"
    return (
        f"I came across the {role} opening at {company} and wanted to reach out. "
        f"My background as a {current} lines up with what the posting describes. "
        "Would you be open to a short chat about the team?"
    )
