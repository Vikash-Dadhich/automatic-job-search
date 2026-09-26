"""Minified, cacheable LLM prompts for scoring and outreach."""

from __future__ import annotations

from typing import Any

from config.profile import Profile
from core.db import Job
from core.token_optimizer import cache_block, minify_job

BANNED_WORDS: tuple[str, ...] = (
    "delve",
    "tapestry",
    "beacon",
    "testament",
    "thrilled to apply",
    "leverage synergies",
    "cutting-edge",
    "passionate about",
    "excited to bring",
    "seamless",
    "robust solution",
    "game-changer",
)

SCORING_RUBRIC = """\
You are a strict job-fit evaluator. Use ONLY the candidate facts in the system block.
Never invent degrees, dates, titles, skills, or work-auth status.

Score 0-100 on: title match, must-have skills overlap, YOE fit, location/remote fit,
work-auth/sponsorship gate (hard penalty if role requires sponsorship the candidate needs
or clearance they lack).

Tier hint (model may suggest; code recomputes): 1=score>=85 or dream company; 2=65-84; 3=<65.

Return ONLY compact JSON, no markdown, no prose:
{"s":<0-100>,"t":<1|2|3>,"r":["short reason","short reason"]}
Keep r to 1-3 concise bullets. No banned fluff words.
"""

OUTREACH_SYSTEM = """\
You draft a concise 3-sentence alumni/referral outreach message.
Ground every claim in the provided candidate facts — invent nothing.
Tone: human, specific, professional. No hype. Avoid banned AI buzzwords.
Return ONLY the message text (no subject line, no quotes, no markdown).
"""

COVER_LETTER_SYSTEM = """\
You draft a 3-5 sentence cover letter for one job application.
Ground every claim in the provided candidate facts — invent nothing.
Explain why this company, why this role, and one concrete past result
that already appears in the facts.
Tone: human, specific, professional. No hype. Avoid banned AI buzzwords.
Return ONLY the letter text (no subject line, no quotes, no markdown).
"""


def build_scoring_system_blocks(profile: Profile) -> list[dict[str, Any]]:
    """Static system content: candidate facts + rubric (prompt-cache friendly)."""
    text = (
        "CANDIDATE (ground truth — do not invent beyond this):\n"
        f"{profile.static_context_block()}\n\n"
        f"RUBRIC:\n{SCORING_RUBRIC}"
    )
    return [cache_block(text)]


def build_scoring_user(job: Job) -> str:
    """Dynamic user content: minified job posting only."""
    return f"Evaluate this job posting:\n\n{minify_job(job)}"


def build_outreach_user(job: Job, profile: Profile) -> str:
    """User prompt for Tier-1 referral/alumni outreach."""
    name = profile.identity.full_name
    return (
        f"Candidate: {name}\n"
        f"Facts:\n{profile.static_context_block()}\n\n"
        f"Target role: {job.title} at {job.company}\n"
        f"Location: {job.location or 'N/A'}\n"
        f"Write a 3-sentence outreach asking for a referral or brief chat."
    )


def build_cover_letter_user(job: Job, profile: Profile) -> str:
    """User prompt for a Tier-1 cover letter. Phrase is matched by test fakes."""
    name = profile.identity.full_name
    return (
        f"Candidate: {name}\n"
        f"Facts:\n{profile.static_context_block()}\n\n"
        f"Target role: {job.title} at {job.company}\n"
        f"Location: {job.location or 'N/A'}\n"
        "Write a 3-5 sentence cover letter for this application."
    )
