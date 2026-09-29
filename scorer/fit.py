"""Candidate-to-JD fit. This is not a rank, a visa decision, or a discovery label."""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass, field
from typing import Any

from pydantic import BaseModel, Field, ValidationError

from config.profile import Profile
from core.db import Job
from core.token_optimizer import cache_block, minify_job
from scorer.clients import LLMClient

FIT_VERSION = "phase6-v1"
_MIN_JD_CHARS = 80

DIMENSIONS = (
    "ROLE_ALIGNMENT",
    "EXPERIENCE_RELEVANCE",
    "SKILLS_MATCH",
    "RESPONSIBILITY_MATCH",
    "EDUCATION_MBA_ALIGNMENT",
    "EXPERIENCE_LEVEL_FIT",
    "LOCATION_WORK_MODE_FIT",
    "REQUIREMENTS_RISK",
)
_JUDGMENTS = frozenset(
    {"confirmed_match", "transferable_match", "unknown", "gap", "conflict"}
)
_CONFIDENCE = frozenset({"high", "medium", "low"})

# Words the rubric uses that are not candidate facts.
_GROUND_STOP = frozenset(
    {
        "candidate",
        "transferable",
        "requirements",
        "preferred",
        "experience",
        "description",
        "responsibilities",
        "qualification",
        "qualifications",
        "alignment",
        "evidence",
        "background",
        "internship",
        "internal",
        "company",
        "profile",
        "unknown",
        "conflict",
        "strength",
        "strengths",
    }
)

FIT_RUBRIC = """\
You evaluate how well ONE candidate matches ONE job description.
Use only the candidate block and the job text. Do not invent employers, titles,
dates, degrees, skills, or accomplishments.

Role classification, when present, says what the job is. It is not a fit score.
Discovery labels are not fit. Do not treat the search query as evidence.
Do not use company prestige. Do not predict interviews or offers.
Do not rank this job against other jobs or other people.

Distinguish required qualifications from preferred ones.
A missing preferred item is unknown or a light gap, not a rejection.
A missing required item is a real gap. A stated conflict is a conflict.
Absence of evidence is not evidence of absence.
Recognize transferable experience and say why it transfers.
Do not require the candidate's old job title to match the posting title.

Dimension weights, totaling 100:
ROLE_ALIGNMENT 20, EXPERIENCE_RELEVANCE 20, SKILLS_MATCH 15,
RESPONSIBILITY_MATCH 15, EDUCATION_MBA_ALIGNMENT 10,
EXPERIENCE_LEVEL_FIT 10, LOCATION_WORK_MODE_FIT 5, REQUIREMENTS_RISK 5.
A preferred gap must not erase an otherwise strong fit.

Return JSON only:
{"fit_score":0-100,"confidence":"high|medium|low",
"strengths":["..."],"gaps":["..."],"evidence":["..."],
"dimensions":{"ROLE_ALIGNMENT":{"judgment":"confirmed_match|transferable_match|unknown|gap|conflict","note":"..."}}}
Include every dimension key. fit_score is candidate-to-JD fit only.
"""


class _Dimension(BaseModel):
    judgment: str
    note: str = ""


class _FitPayload(BaseModel):
    fit_score: int = Field(ge=0, le=100)
    confidence: str
    strengths: list[str] = Field(default_factory=list)
    gaps: list[str] = Field(default_factory=list)
    evidence: list[str] = Field(default_factory=list)
    dimensions: dict[str, _Dimension]


@dataclass(frozen=True, slots=True)
class FitDecision:
    available: bool
    score: int | None
    confidence: str
    strengths: list[str] = field(default_factory=list)
    gaps: list[str] = field(default_factory=list)
    evidence: list[str] = field(default_factory=list)
    dimensions: dict[str, Any] = field(default_factory=dict)
    version: str = FIT_VERSION
    content_hash: str | None = None
    profile_hash: str | None = None
    legacy: bool = False


def profile_fit_hash(profile: Profile) -> str:
    """Hash of the candidate block the fit prompt uses."""
    text = profile.static_context_block().strip()
    return hashlib.sha256(text.encode()).hexdigest()


def fit_is_current(job: Job, profile: Profile) -> bool:
    return bool(
        job.score is not None
        and job.fit_version == FIT_VERSION
        and job.fit_content_hash
        and job.fit_content_hash == job.content_hash
        and job.fit_profile_hash == profile_fit_hash(profile)
        and job.fit_confidence
    )


def _insufficient(job: Job) -> bool:
    if job.jd_truncated is True:
        return True
    if job.jd_status in {"missing", "suspicious"}:
        return True
    return not (job.description_clean or "").strip()


def _unavailable(job: Job, profile: Profile, reason: str) -> FitDecision:
    return FitDecision(
        available=False,
        score=None,
        confidence="low",
        evidence=[reason],
        content_hash=job.content_hash,
        profile_hash=profile_fit_hash(profile),
    )


def _lines(value: object) -> list[str]:
    if not isinstance(value, list):
        return []
    out: list[str] = []
    for item in value:
        text = str(item).strip()
        if text:
            out.append(text[:240])
    return out[:5]


def _ground(lines: list[str], corpus: str) -> list[str]:
    """Drop lines that name a specific fact absent from the profile and the JD."""
    haystack = corpus.lower()
    kept: list[str] = []
    for line in lines:
        tokens = re.findall(r"[a-z]{8,}", line.lower())
        foreign = [token for token in tokens if token not in _GROUND_STOP and token not in haystack]
        if foreign:
            continue
        kept.append(line)
    return kept


def _legacy(data: dict[str, Any], job: Job, profile: Profile) -> FitDecision | None:
    if "fit_score" in data or "s" not in data:
        return None
    try:
        score = int(data["s"])
    except (TypeError, ValueError):
        return None
    score = max(0, min(100, score))
    reasons = _ground(
        _lines(data.get("r")),
        f"{profile.static_context_block()}\n{job.description_clean or ''}",
    )
    return FitDecision(
        available=True,
        score=score,
        confidence="medium",
        strengths=reasons,
        evidence=reasons or ["Fit score from the compatibility score payload."],
        legacy=True,
        content_hash=job.content_hash,
        profile_hash=profile_fit_hash(profile),
    )


def parse_fit(text: str, job: Job, profile: Profile) -> FitDecision | None:
    """Parse a fit payload. None means the output is not usable."""
    cleaned = (text or "").strip()
    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```(?:json)?\s*|\s*```$", "", cleaned, flags=re.IGNORECASE).strip()
    try:
        data = json.loads(cleaned)
    except json.JSONDecodeError:
        return None
    if not isinstance(data, dict):
        return None
    legacy = _legacy(data, job, profile)
    if legacy is not None:
        return legacy
    try:
        payload = _FitPayload.model_validate(data)
    except ValidationError:
        return None
    if payload.confidence not in _CONFIDENCE:
        return None
    if set(payload.dimensions) != set(DIMENSIONS):
        return None
    for item in payload.dimensions.values():
        if item.judgment not in _JUDGMENTS:
            return None
    corpus = f"{profile.static_context_block()}\n{job.description_clean or ''}\n{job.title or ''}"
    strengths = _ground(_lines(payload.strengths), corpus)
    gaps = _ground(_lines(payload.gaps), corpus)
    evidence = _ground(_lines(payload.evidence), corpus)
    if _lines(payload.strengths) and not strengths and not evidence:
        return None
    return FitDecision(
        available=True,
        score=payload.fit_score,
        confidence=payload.confidence,  # type: ignore[arg-type]
        strengths=strengths,
        gaps=gaps,
        evidence=evidence or strengths,
        dimensions={
            name: {"judgment": item.judgment, "note": item.note}
            for name, item in payload.dimensions.items()
        },
        content_hash=job.content_hash,
        profile_hash=profile_fit_hash(profile),
    )


def build_fit_system_blocks(profile: Profile) -> list[dict[str, Any]]:
    text = (
        "CANDIDATE (ground truth — do not invent beyond this):\n"
        f"{profile.static_context_block()}\n\n"
        f"RUBRIC:\n{FIT_RUBRIC}"
    )
    return [cache_block(text)]


def build_fit_user(job: Job) -> str:
    """Job text plus role classification. Discovery query is omitted on purpose."""
    role = ""
    if job.role_family:
        role = (
            "Role classification (what the job is, not a fit score): "
            f"{job.role_family}"
            + (f" / {job.role_subfamily}" if job.role_subfamily else "")
            + f" confidence={job.role_confidence or 'unknown'}\n"
        )
    return f"Evaluate this job posting:\n\n{role}{minify_job(job)}"


def cached_fit(job: Job, profile: Profile) -> FitDecision | None:
    if not fit_is_current(job, profile):
        return None
    return FitDecision(
        available=True,
        score=job.score,
        confidence=job.fit_confidence or "low",
        strengths=list(job.fit_strengths or []),
        gaps=list(job.fit_gaps or []),
        evidence=list(job.fit_evidence or job.justification or []),
        dimensions=dict(job.fit_dimensions or {}),
        content_hash=job.content_hash,
        profile_hash=job.fit_profile_hash,
    )


async def evaluate_fit(
    job: Job,
    profile: Profile,
    client: LLMClient | None,
    *,
    model: str,
    max_tokens: int,
) -> FitDecision:
    """Fit one job. Short or missing descriptions do not call the model."""
    if _insufficient(job):
        return _unavailable(job, profile, "Insufficient job description to assess fit.")
    cached = cached_fit(job, profile)
    if cached is not None:
        return cached
    if client is None:
        return _unavailable(job, profile, "Fit model is unavailable.")
    raw = await client.complete(
        model=model,
        system_blocks=build_fit_system_blocks(profile),
        user=build_fit_user(job),
        max_tokens=max_tokens,
        temperature=0.0,
        json_mode=True,
    )
    parsed = parse_fit(raw, job, profile)
    if parsed is None:
        return _unavailable(job, profile, "Fit model returned an unusable result.")
    return parsed
