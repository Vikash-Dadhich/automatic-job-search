"""Map Workday form questions to profile facts or LLM-drafted answers."""

from __future__ import annotations

import asyncio
import re
from dataclasses import dataclass
from enum import StrEnum
from typing import TYPE_CHECKING, Any

import structlog

from config.profile import Profile
from config.settings import get_settings
from core.db import Job, Source
from core.token_optimizer import cache_block, minify_job
from scorer.outreach import contains_banned, strip_banned_sentences

if TYPE_CHECKING:
    from scorer.clients import LLMClient

log = structlog.get_logger(__name__)

ANSWER_SYSTEM = """\
You draft a short application / screening answer (1-3 sentences).
Use ONLY the candidate facts provided. Invent nothing.
Tone: clear, professional, human. Avoid banned AI buzzwords.
Return ONLY the answer text (no quotes, no markdown, no preamble).
"""


class AnswerSource(StrEnum):
    deterministic = "deterministic"
    llm = "llm"
    blank = "blank"
    # Looks required but nothing could answer it — surface to the human.
    needs_review = "needs_review"


@dataclass
class ResolvedAnswer:
    question: str
    answer: str
    source: AnswerSource

    def to_dict(self) -> dict[str, str]:
        return {
            "question": self.question,
            "answer": self.answer,
            "source": self.source.value,
        }


def _norm(label: str) -> str:
    return re.sub(r"\s+", " ", (label or "").strip().lower())


def _matches(label: str, *needles: str) -> bool:
    """True if any needle appears as a whole phrase (word-boundary safe)."""
    text = _norm(label)
    for needle in needles:
        n = _norm(needle)
        if not n:
            continue
        if re.search(rf"(?<!\w){re.escape(n)}(?!\w)", text):
            return True
    return False


def _split_name(full_name: str) -> tuple[str, str]:
    parts = [p for p in full_name.strip().split() if p]
    if not parts:
        return "", ""
    if len(parts) == 1:
        return parts[0], ""
    return parts[0], parts[-1]


_SOURCE_LABELS = {
    Source.linkedin: "LinkedIn",
    Source.indeed: "Indeed",
    Source.workday: "Company career site",
}


def _discovery_channel(job: Job | None) -> str:
    """Name the channel the posting actually came from."""
    if job is None:
        return "Company career site"
    try:
        source = job.source if isinstance(job.source, Source) else Source(job.source)
    except ValueError:
        return "Company career site"
    return _SOURCE_LABELS.get(source, "Company career site")


def _latest_education(profile: Profile) -> Any:
    """Most recent degree, not just the first listed entry."""
    if not profile.education:
        return None
    return max(profile.education, key=lambda e: (e.graduation_date or ""))


def resolve_deterministic(
    label: str,
    profile: Profile,
    *,
    job: Job | None = None,
) -> str | None:
    """Return a profile-backed answer when the question matches a known pattern."""
    identity = profile.identity
    address = identity.address
    auth = profile.work_authorization
    first, last = _split_name(identity.full_name)

    # Identity
    if _matches(label, "first name", "given name"):
        return first or identity.full_name
    if _matches(label, "last name", "family name", "surname"):
        return last or identity.full_name
    if _matches(label, "full name", "legal name") and not _matches(
        label, "first name", "last name"
    ):
        return identity.full_name
    if _matches(label, "email"):
        return identity.email
    if _matches(label, "phone", "mobile", "cell"):
        return identity.phone
    if _matches(label, "linkedin"):
        return identity.linkedin_url
    if _matches(label, "github"):
        return identity.github_url
    if _matches(label, "portfolio", "personal website", "website url"):
        return identity.portfolio_url or ""

    # Address
    if _matches(label, "street", "address line 1", "address 1"):
        return address.street
    if _matches(label, "address line 2", "address 2", "apt", "suite", "unit"):
        return ""
    if _matches(label, "city") and not _matches(label, "university", "school"):
        return address.city
    if _matches(label, "state", "province") and not _matches(label, "statement"):
        return address.state
    if _matches(label, "zip", "postal", "postcode"):
        return address.zip
    if _matches(label, "country") and not _matches(label, "country of"):
        return address.country

    # Work authorization
    if _matches(
        label,
        "authorized to work",
        "legally authorized",
        "eligible to work",
        "work authorization",
        "right to work",
    ):
        return "Yes" if auth.authorized_to_work_us else "No"
    if _matches(
        label,
        "require sponsorship",
        "need sponsorship",
        "visa sponsorship",
        "require visa",
        "need a visa",
    ):
        return "Yes" if auth.needs_visa_sponsorship or auth.sponsorship_required else "No"
    if _matches(label, "visa status", "immigration status", "work status"):
        return auth.status

    # Relocation / remote
    if _matches(label, "willing to relocate", "open to relocate", "relocation"):
        return "Yes" if profile.preferences.relocation_ok else "No"
    if _matches(label, "remote", "work from home") and _matches(
        label, "willing", "able", "open", "prefer"
    ):
        return "Yes" if profile.preferences.remote_ok else "No"

    # EEO / self-ID — decline to self-identify
    if _matches(
        label,
        "race",
        "ethnicity",
        "gender",
        "sex",
        "veteran",
        "disability",
        "hispanic",
        "latino",
        "lgbt",
        "sexual orientation",
        "gender identity",
    ):
        if _matches(
            label,
            "decline",
            "prefer not",
            "do not wish",
            "choose not",
            "self-identify",
            "voluntary",
            "eeo",
            "equal opportunity",
            "disability",
            "veteran",
            "race",
            "ethnicity",
            "gender",
            "sex",
        ):
            return "Decline to self-identify"

    # How did you hear / source
    if _matches(
        label,
        "how did you hear",
        "how did you find",
        "source of",
        "where did you hear",
        "referral source",
        "application source",
    ):
        return _discovery_channel(job)

    # Education (most recent degree)
    edu = _latest_education(profile)
    if edu is not None:
        if _matches(label, "school", "university", "college") and not _matches(
            label, "high school"
        ):
            return edu.school
        if _matches(label, "degree") and not _matches(label, "agree"):
            return f"{edu.degree} {edu.field}".strip()
        if _matches(label, "gpa", "grade point"):
            return "" if edu.gpa is None else str(edu.gpa)
        if _matches(label, "graduation", "graduat"):
            return edu.graduation_date

    return None


def is_open_ended(label: str) -> bool:
    """Heuristic: long-form / why / cover-letter style questions."""
    return _matches(
        label,
        "why are you",
        "why do you",
        "why would you",
        "tell us about",
        "tell me about",
        "describe",
        "cover letter",
        "additional information",
        "additional comments",
        "anything else",
        "what interests you",
        "what excites you",
        "what makes you",
        "why this role",
        "why this company",
        "why our",
        "why do you want",
        "relevant experience",
        "summarize your",
        "summarise your",
        "briefly explain",
        "please explain",
        "please share",
        "in your own words",
        "walk us through",
        "give an example",
        "provide an example",
        "how would you",
        "how do you approach",
        "what would you",
        "your motivation",
        "open-ended",
    )


# Labels a form will usually block submission on; a blank here needs a human.
_REVIEW_REQUIRED_HINTS = (
    "salary",
    "compensation",
    "pay rate",
    "desired pay",
    "expected pay",
    "start date",
    "available to start",
    "availability",
    "notice period",
    "willing to travel",
    "travel requirement",
    "shift",
    "background check",
    "drug test",
    "criminal",
    "non-compete",
    "reference",
    "certification",
    "license",
    "security clearance",
)


def needs_human_review(label: str) -> bool:
    """True for fields that commonly gate submission and cannot be guessed safely."""
    return _matches(label, *_REVIEW_REQUIRED_HINTS)


class AnswerResolver:
    """Resolve form labels to answers; LLM only for open-ended unknowns."""

    def __init__(
        self,
        profile: Profile,
        *,
        client: LLMClient | None = None,
    ) -> None:
        self._profile = profile
        self._client = client

    def _resolve_client(self) -> LLMClient:
        if self._client is not None:
            return self._client
        from scorer.engine import build_llm_client

        return build_llm_client()

    async def resolve(
        self,
        question: str,
        *,
        job: Job | None = None,
        force_llm: bool = False,
    ) -> ResolvedAnswer:
        if not force_llm:
            deterministic = resolve_deterministic(question, self._profile, job=job)
            if deterministic is not None:
                return ResolvedAnswer(
                    question=question,
                    answer=deterministic,
                    source=AnswerSource.deterministic,
                )

        if not force_llm and not is_open_ended(question):
            return ResolvedAnswer(
                question=question,
                answer="",
                source=self._unanswered_source(question),
            )

        try:
            text = await self._draft_open_ended(question, job=job)
            if not text:
                return ResolvedAnswer(
                    question=question,
                    answer="",
                    source=self._unanswered_source(question),
                )
            return ResolvedAnswer(
                question=question,
                answer=text,
                source=AnswerSource.llm,
            )
        except Exception as exc:
            log.warning("answer_llm_failed", question=question[:80], error=str(exc))
            # An LLM outage on an essay question is exactly the case a human
            # must see before the form is submitted.
            return ResolvedAnswer(
                question=question,
                answer="",
                source=AnswerSource.needs_review,
            )

    @staticmethod
    def _unanswered_source(question: str) -> AnswerSource:
        return (
            AnswerSource.needs_review
            if needs_human_review(question)
            else AnswerSource.blank
        )

    async def resolve_many(
        self,
        questions: list[str],
        *,
        job: Job | None = None,
        concurrency: int | None = None,
    ) -> list[ResolvedAnswer]:
        """Resolve questions concurrently, preserving input order."""
        if not questions:
            return []
        settings = get_settings()
        workers = max(1, concurrency or settings.scorer_concurrency)
        semaphore = asyncio.Semaphore(workers)

        async def one(question: str) -> ResolvedAnswer:
            async with semaphore:
                return await self.resolve(question, job=job)

        return list(await asyncio.gather(*(one(q) for q in questions)))

    async def _draft_open_ended(
        self,
        question: str,
        *,
        job: Job | None = None,
    ) -> str:
        client = self._resolve_client()
        settings = get_settings()
        system_blocks = [cache_block(ANSWER_SYSTEM + "\n\n" + self._profile.static_context_block())]
        job_blob = minify_job(job) if job is not None else "N/A"
        user = (
            f"Job:\n{job_blob}\n\n"
            f"Application question:\n{question}\n\n"
            "Write a 1-3 sentence answer grounded only in candidate facts."
        )
        draft = (
            await client.complete(
                model=settings.active_writer_model,
                system_blocks=system_blocks,
                user=user,
                max_tokens=settings.writer_max_tokens,
                temperature=0.5,
                thinking_level=settings.gemini_writer_thinking_level,
            )
        ).strip()

        banned = contains_banned(draft)
        if banned:
            log.info("answer_banned_retry", banned=banned)
            retry_user = (
                f"{user}\n\nRewrite without these phrases: {', '.join(banned)}."
            )
            draft = (
                await client.complete(
                    model=settings.active_writer_model,
                    system_blocks=system_blocks,
                    user=retry_user,
                    max_tokens=settings.writer_max_tokens,
                    temperature=0.4,
                    thinking_level=settings.gemini_writer_thinking_level,
                )
            ).strip()
            if contains_banned(draft):
                # If every sentence is banned the answer goes out blank, and the
                # resolver escalates it rather than shipping AI filler.
                draft = strip_banned_sentences(draft)
        return draft


def answers_to_payload(answers: list[ResolvedAnswer]) -> dict[str, Any]:
    """Persistable JSON blob for Job.application_answers."""
    return {
        "items": [a.to_dict() for a in answers],
        "count": len(answers),
    }
