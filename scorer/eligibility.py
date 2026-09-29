"""Visa and eligibility from the profile and the posting. Not fit and not legal advice."""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import asdict, dataclass, field
from datetime import date

import structlog
from pydantic import BaseModel, ValidationError

from config.profile import Profile
from core.db import Job
from scorer.clients import LLMClient
from scraper.filters import (
    _YOE_REQUIRED_RE,
    citizenship_restriction,
    clearance_requirement,
    has_internship_signal,
    location_acceptable,
    max_acceptable_years,
    visa_sponsorship_signal,
)

log = structlog.get_logger(__name__)

ELIGIBILITY_VERSION = "phase9-v1"
CONFIRMED_ELIGIBLE = "CONFIRMED_ELIGIBLE"
LIKELY_ELIGIBLE = "LIKELY_ELIGIBLE"
UNKNOWN = "UNKNOWN"
CLEARLY_INELIGIBLE = "CLEARLY_INELIGIBLE"
_STATES = {CONFIRMED_ELIGIBLE, LIKELY_ELIGIBLE, UNKNOWN, CLEARLY_INELIGIBLE}
_DIMENSIONS = (
    "WORK_AUTHORIZATION",
    "VISA_SPONSORSHIP",
    "CITIZENSHIP",
    "SECURITY_CLEARANCE",
    "INTERNSHIP_REQUIREMENT",
    "EDUCATION",
    "GRADUATION_TIMING",
    "EXPERIENCE_REQUIREMENT",
    "LOCATION",
    "INTERNSHIP_DATES",
)
_MONTHS = {
    "january": 1,
    "february": 2,
    "march": 3,
    "april": 4,
    "may": 5,
    "june": 6,
    "july": 7,
    "august": 8,
    "september": 9,
    "october": 10,
    "november": 11,
    "december": 12,
}
_PERMANENT_AUTH_RE = re.compile(
    r"\b(?:unrestricted|permanent)\s+(?:u\.?s\.?\s+)?work\s+authorization\b"
    r"|\bauthorized\s+to\s+work\s+permanently\b"
    r"|\bpermanently\s+authorized\s+to\s+work\b",
    re.IGNORECASE,
)
_AMBIGUOUS_AUTH_RE = re.compile(
    r"\b(?:work authorization|authorized to work|legally authorized|eligible to work)\b",
    re.IGNORECASE,
)
_MBA_REQUIRED_RE = re.compile(
    r"\bmba\b.{0,40}\brequired\b"
    r"|\brequired\b.{0,40}\bmba\b"
    r"|\bcurrently enrolled in an mba\b"
    r"|\bmust\b.{0,60}\b(?:enrolled|pursuing)\b.{0,40}\bmba\b",
    re.IGNORECASE,
)
_MBA_PREFERRED_RE = re.compile(r"\bmba\b.{0,40}\bpreferred\b|\bpreferred\b.{0,40}\bmba\b", re.I)
_BACHELOR_CURRENT_RE = re.compile(
    r"\b(?:must|required)\b.{0,80}\bcurrently\s+(?:pursuing|enrolled)\b.{0,40}\bbachelor"
    r"|\bcurrently\s+(?:pursuing|enrolled)\b.{0,50}\bbachelor.{0,40}\b(?:must|required)\b",
    re.IGNORECASE,
)
_OTHER_DEGREE_RE = re.compile(
    r"\b(?:ph\.?d|doctorate|j\.d\.|m\.d\.)\b.{0,30}\brequired\b"
    r"|\brequired\b.{0,30}\b(?:ph\.?d|doctorate)\b",
    re.IGNORECASE,
)
_GRAD_WINDOW_RE = re.compile(
    r"\bbetween\s+([A-Za-z]+)\s+(20\d{2})\s+and\s+([A-Za-z]+)\s+(20\d{2})\b",
    re.IGNORECASE,
)
_GRAD_YEAR_RE = re.compile(
    r"\b(?:graduat(?:e|ing)|graduation)\b.{0,40}\b(20\d{2})\b",
    re.IGNORECASE,
)
_GRAD_PREFERRED_RE = re.compile(
    r"\bgraduat\w+\b.{0,40}\bpreferred\b|\bpreferred\b.{0,40}\bgraduat",
    re.IGNORECASE,
)
_DATE_RANGE_RE = re.compile(
    r"\b(January|February|March|April|May|June|July|August|September|October|November|December)"
    r"\s+(20\d{2})\s*[–—-]\s*"
    r"(January|February|March|April|May|June|July|August|September|October|November|December)"
    r"\s+(20\d{2})\b",
    re.IGNORECASE,
)
_EEO_RE = re.compile(r"\bequal opportunity\b", re.IGNORECASE)


@dataclass(frozen=True, slots=True)
class DimensionResult:
    state: str
    reason: str
    evidence: list[str] = field(default_factory=list)


@dataclass(frozen=True, slots=True)
class EligibilityDecision:
    state: str
    available: bool
    reasons: list[str]
    evidence: list[str]
    dimensions: dict[str, DimensionResult]
    version: str
    content_hash: str | None
    profile_hash: str | None


class _ModelState(BaseModel):
    state: str


def profile_eligibility_hash(profile: Profile) -> str:
    """Hash of the profile facts this engine reads. Dream companies are excluded."""
    payload = {
        "work_authorization": profile.work_authorization.model_dump(),
        "education": [
            {"degree": item.degree, "graduation_date": item.graduation_date}
            for item in profile.education
        ],
        "experience": [
            {"start_date": item.start_date, "end_date": item.end_date}
            for item in profile.experience
        ],
        "remote_ok": profile.preferences.remote_ok,
        "relocation_ok": profile.preferences.relocation_ok,
        "locations": list(profile.preferences.locations),
        "clearance_required": profile.exclusions.clearance_required,
    }
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(raw.encode()).hexdigest()


def eligibility_is_current(job: Job, profile: Profile) -> bool:
    return bool(
        job.eligibility_state in _STATES
        and job.eligibility_version == ELIGIBILITY_VERSION
        and job.eligibility_content_hash
        and job.eligibility_content_hash == job.content_hash
        and job.eligibility_profile_hash == profile_eligibility_hash(profile)
        and job.eligibility_dimensions
    )


def _needs_sponsorship(profile: Profile) -> bool:
    auth = profile.work_authorization
    return bool(auth.sponsorship_required or auth.needs_visa_sponsorship)


def _graduation(profile: Profile) -> tuple[int, int] | None:
    chosen = None
    for item in profile.education:
        if "mba" in item.degree.lower():
            chosen = item
            break
    if chosen is None and profile.education:
        chosen = profile.education[0]
    if chosen is None:
        return None
    year, month = chosen.graduation_date.split("-")
    return int(year), int(month)


def _has_degree(profile: Profile, needle: str) -> bool:
    return any(needle in item.degree.lower() for item in profile.education)


def _current_student(profile: Profile, needle: str, *, today: date | None = None) -> bool:
    now = today or date.today()
    for item in profile.education:
        if needle not in item.degree.lower():
            continue
        year, month = (int(part) for part in item.graduation_date.split("-"))
        if date(year, month, 1) >= date(now.year, now.month, 1):
            return True
    return False


def _dim(state: str, reason: str, evidence: list[str] | None = None) -> DimensionResult:
    return DimensionResult(state=state, reason=reason, evidence=list(evidence or []))


def _snippet(text: str, pattern: str) -> list[str]:
    match = re.search(pattern, text, re.IGNORECASE)
    if match is None:
        return []
    return [re.sub(r"\s+", " ", match.group(0)).strip()]


def _posting_text(job: Job) -> str:
    return "\n".join(
        part for part in (job.title or "", job.description_clean or "") if part
    )


def _work_authorization(text: str) -> DimensionResult:
    if _PERMANENT_AUTH_RE.search(text):
        return _dim(
            CLEARLY_INELIGIBLE,
            "The posting requires permanent or unrestricted work authorization.",
            _snippet(text, _PERMANENT_AUTH_RE.pattern),
        )
    if _AMBIGUOUS_AUTH_RE.search(text) and visa_sponsorship_signal(text) == "unknown":
        return _dim(
            UNKNOWN,
            "Work-authorization wording is present but does not state a clear rule.",
            _snippet(text, _AMBIGUOUS_AUTH_RE.pattern),
        )
    return _dim(UNKNOWN, "No explicit work-authorization rule is stated.")


def _visa(text: str, profile: Profile) -> DimensionResult:
    signal = visa_sponsorship_signal(text)
    if signal == "hostile" and _needs_sponsorship(profile):
        return _dim(
            CLEARLY_INELIGIBLE,
            "The posting explicitly refuses visa sponsorship.",
            ["hostile sponsorship language"],
        )
    if signal == "friendly":
        return _dim(
            CONFIRMED_ELIGIBLE,
            "The posting explicitly accepts a sponsorship or CPT/OPT path.",
            ["friendly sponsorship language"],
        )
    return _dim(UNKNOWN, "The posting does not state a visa-sponsorship rule.")


def _citizenship(text: str, profile: Profile) -> DimensionResult:
    if citizenship_restriction(text) and _needs_sponsorship(profile):
        return _dim(
            CLEARLY_INELIGIBLE,
            "The posting requires U.S. citizenship.",
            ["citizenship restriction"],
        )
    if _EEO_RE.search(text):
        return _dim(UNKNOWN, "Equal-opportunity language is not a citizenship rule.")
    return _dim(UNKNOWN, "No citizenship restriction is stated.")


def _clearance(text: str) -> DimensionResult:
    kind = clearance_requirement(text)
    if kind == "required":
        return _dim(
            CLEARLY_INELIGIBLE,
            "The posting requires a security clearance the profile does not list.",
            ["clearance required"],
        )
    if kind == "preferred":
        return _dim(UNKNOWN, "Clearance is preferred, not required.")
    return _dim(UNKNOWN, "No clearance requirement is stated.")


def _internship(job: Job) -> DimensionResult:
    if has_internship_signal(job.title):
        return _dim(CONFIRMED_ELIGIBLE, "The title matches an existing internship signal.")
    return _dim(UNKNOWN, "The title has no internship signal. That is not a visa rejection.")


def _education(text: str, profile: Profile) -> DimensionResult:
    if _MBA_PREFERRED_RE.search(text) and not _MBA_REQUIRED_RE.search(text):
        return _dim(UNKNOWN, "MBA is preferred, not required.")
    if _OTHER_DEGREE_RE.search(text):
        return _dim(CLEARLY_INELIGIBLE, "The posting requires a degree the profile does not list.")
    if _BACHELOR_CURRENT_RE.search(text) and not _current_student(profile, "bachelor"):
        return _dim(
            CLEARLY_INELIGIBLE,
            "The posting requires a current bachelor's student.",
        )
    if _MBA_REQUIRED_RE.search(text):
        if _current_student(profile, "mba") or _has_degree(profile, "mba"):
            return _dim(CONFIRMED_ELIGIBLE, "The posting asks for an MBA and the profile has one.")
        return _dim(CLEARLY_INELIGIBLE, "The posting requires an MBA the profile does not list.")
    return _dim(UNKNOWN, "No hard education requirement is stated.")


def _in_window(candidate: tuple[int, int], start: tuple[int, int], end: tuple[int, int]) -> bool:
    return start <= candidate <= end


def _graduation_timing(text: str, profile: Profile) -> DimensionResult:
    if _GRAD_PREFERRED_RE.search(text) and _GRAD_WINDOW_RE.search(text) is None:
        if _GRAD_YEAR_RE.search(text) is None or _GRAD_PREFERRED_RE.search(text):
            years = [int(item) for item in _GRAD_YEAR_RE.findall(text)]
            window = _GRAD_WINDOW_RE.search(text)
            if window is None and (not years or _GRAD_PREFERRED_RE.search(text)):
                return _dim(UNKNOWN, "Graduation timing is preferred, not required.")
    candidate = _graduation(profile)
    window = _GRAD_WINDOW_RE.search(text)
    if window and candidate is not None:
        start_month = _MONTHS.get(window.group(1).lower())
        end_month = _MONTHS.get(window.group(3).lower())
        if start_month and end_month:
            start = (int(window.group(2)), start_month)
            end = (int(window.group(4)), end_month)
            if _in_window(candidate, start, end):
                return _dim(
                    CONFIRMED_ELIGIBLE,
                    "The stated graduation window includes the profile.",
                )
            return _dim(
                CLEARLY_INELIGIBLE,
                "The stated graduation window does not include the profile graduation.",
                [window.group(0)],
            )
    if _GRAD_PREFERRED_RE.search(text):
        return _dim(UNKNOWN, "Graduation timing is preferred, not required.")
    years = [int(item) for item in _GRAD_YEAR_RE.findall(text)]
    if years and candidate is not None:
        if candidate[0] in years:
            return _dim(CONFIRMED_ELIGIBLE, "The stated graduation year matches the profile.")
        if re.search(r"\bmust\b", text, re.IGNORECASE):
            return _dim(
                CLEARLY_INELIGIBLE,
                "The required graduation year does not match the profile.",
            )
    return _dim(UNKNOWN, "No graduation requirement is stated.")


def _experience(text: str, profile: Profile) -> DimensionResult:
    required: list[int] = []
    for match in _YOE_REQUIRED_RE.finditer(text):
        span = text[max(0, match.start() - 40) : match.end() + 40]
        years = int(match.group(1))
        if not 0 < years <= 40:
            continue
        preferred = re.search(r"\bpreferred\b", span, re.IGNORECASE)
        mandatory = re.search(r"\b(?:must|requir\w*)\b", span, re.IGNORECASE)
        if preferred and not mandatory:
            continue
        if not mandatory:
            continue
        required.append(years)
    if not required:
        return _dim(UNKNOWN, "No mandatory experience floor is stated.")
    ceiling = max_acceptable_years(profile)
    if min(required) > ceiling:
        return _dim(
            CLEARLY_INELIGIBLE,
            f"The posting requires {min(required)}+ years, above the profile ceiling {ceiling}.",
        )
    return _dim(CONFIRMED_ELIGIBLE, "The stated experience floor is within the profile ceiling.")


def _location(job: Job, profile: Profile) -> DimensionResult:
    if not (job.location or "").strip():
        return _dim(UNKNOWN, "No location is stated.")
    if location_acceptable(job.location, profile):
        return _dim(
            LIKELY_ELIGIBLE,
            "The location is compatible. A city preference is not an eligibility gate.",
        )
    return _dim(CLEARLY_INELIGIBLE, "The location conflicts with the profile's location rules.")


def _dates(text: str) -> tuple[DimensionResult, bool]:
    match = _DATE_RANGE_RE.search(text)
    if match is None:
        return _dim(UNKNOWN, "No internship dates are stated."), False
    return (
        _dim(
            UNKNOWN,
            "The posting lists dates, and the profile has no internship availability window.",
            [match.group(0)],
        ),
        True,
    )


def _overall(
    dimensions: dict[str, DimensionResult],
    *,
    dates_unresolved: bool,
    ambiguous_auth: bool,
    internship: bool,
) -> str:
    if any(item.state == CLEARLY_INELIGIBLE for item in dimensions.values()):
        return CLEARLY_INELIGIBLE
    if dates_unresolved or ambiguous_auth:
        return UNKNOWN
    visa = dimensions["VISA_SPONSORSHIP"].state
    if visa == CONFIRMED_ELIGIBLE:
        return CONFIRMED_ELIGIBLE
    if visa == UNKNOWN and internship:
        return LIKELY_ELIGIBLE
    return UNKNOWN


def _decision_from_job(job: Job) -> EligibilityDecision:
    raw = job.eligibility_dimensions or {}
    dimensions: dict[str, DimensionResult] = {}
    for name in _DIMENSIONS:
        item = raw.get(name) if isinstance(raw, dict) else None
        if isinstance(item, dict):
            dimensions[name] = DimensionResult(
                state=str(item.get("state") or UNKNOWN),
                reason=str(item.get("reason") or ""),
                evidence=[str(line) for line in item.get("evidence") or []],
            )
        else:
            dimensions[name] = _dim(UNKNOWN, "Cached dimension was missing.")
    return EligibilityDecision(
        state=str(job.eligibility_state or UNKNOWN),
        available=True,
        reasons=list(job.eligibility_reasons or []),
        evidence=list(job.eligibility_evidence or []),
        dimensions=dimensions,
        version=ELIGIBILITY_VERSION,
        content_hash=job.eligibility_content_hash,
        profile_hash=job.eligibility_profile_hash,
    )


def evaluate_eligibility_sync(job: Job, profile: Profile) -> EligibilityDecision:
    """Deterministic eligibility. Does not read fit, discovery, or company facts."""
    text = _posting_text(job)
    dates, dates_unresolved = _dates(text)
    dimensions = {
        "WORK_AUTHORIZATION": _work_authorization(text),
        "VISA_SPONSORSHIP": _visa(text, profile),
        "CITIZENSHIP": _citizenship(text, profile),
        "SECURITY_CLEARANCE": _clearance(text),
        "INTERNSHIP_REQUIREMENT": _internship(job),
        "EDUCATION": _education(text, profile),
        "GRADUATION_TIMING": _graduation_timing(text, profile),
        "EXPERIENCE_REQUIREMENT": _experience(text, profile),
        "LOCATION": _location(job, profile),
        "INTERNSHIP_DATES": dates,
    }
    ambiguous = dimensions["WORK_AUTHORIZATION"].state == UNKNOWN and bool(
        _AMBIGUOUS_AUTH_RE.search(text)
    ) and visa_sponsorship_signal(text) == "unknown" and not _PERMANENT_AUTH_RE.search(text)
    state = _overall(
        dimensions,
        dates_unresolved=dates_unresolved,
        ambiguous_auth=ambiguous,
        internship=dimensions["INTERNSHIP_REQUIREMENT"].state == CONFIRMED_ELIGIBLE,
    )
    reasons = [item.reason for item in dimensions.values() if item.state == state]
    if not reasons:
        reasons = [item.reason for item in dimensions.values() if item.state == CLEARLY_INELIGIBLE]
    if not reasons:
        reasons = ["Eligibility is based only on the posting and the profile."]
    evidence: list[str] = []
    for item in dimensions.values():
        evidence.extend(item.evidence)
    return EligibilityDecision(
        state=state,
        available=True,
        reasons=reasons[:8],
        evidence=evidence[:8],
        dimensions=dimensions,
        version=ELIGIBILITY_VERSION,
        content_hash=job.content_hash,
        profile_hash=profile_eligibility_hash(profile),
    )


async def _ask_model(client: LLMClient, job: Job, profile: Profile) -> str | None:
    system = (
        "You classify internship eligibility. Use only the profile facts and the job text. "
        "Do not give legal advice. Do not invent sponsorship. "
        "Reply as JSON with a state of UNKNOWN when the posting is ambiguous. "
        "Allowed states: CONFIRMED_ELIGIBLE, LIKELY_ELIGIBLE, UNKNOWN, CLEARLY_INELIGIBLE."
    )
    auth = profile.work_authorization
    user = (
        f"Work auth: {auth.status}\n"
        f"sponsorship_required={auth.sponsorship_required}\n"
        f"needs_visa_sponsorship={auth.needs_visa_sponsorship}\n"
        f"Job text:\n{_posting_text(job)[:4000]}"
    )
    raw = await client.complete(
        model="eligibility",
        system_blocks=[{"type": "text", "text": system}],
        user=user,
        max_tokens=200,
        temperature=0,
        json_mode=True,
    )
    try:
        parsed = _ModelState.model_validate_json(raw)
    except ValidationError:
        return None
    if parsed.state not in _STATES:
        return None
    return parsed.state


async def evaluate_eligibility(
    job: Job,
    profile: Profile,
    *,
    client: LLMClient | None = None,
) -> EligibilityDecision:
    """Return a cached decision, or compute one. Model failure stays UNKNOWN."""
    if eligibility_is_current(job, profile):
        log.info("eligibility_reused", job_id=job.id, state=job.eligibility_state)
        return _decision_from_job(job)

    decision = evaluate_eligibility_sync(job, profile)
    ambiguous = decision.dimensions["WORK_AUTHORIZATION"].state == UNKNOWN and bool(
        _AMBIGUOUS_AUTH_RE.search(_posting_text(job))
    )
    if ambiguous and client is not None and decision.state == UNKNOWN:
        try:
            model_state = await _ask_model(client, job, profile)
        except Exception as exc:
            log.warning("eligibility_model_failed", job_id=job.id, error=type(exc).__name__)
            model_state = None
        if model_state is None or model_state != UNKNOWN:
            # An ambiguous posting cannot be promoted or rejected by the model.
            decision = EligibilityDecision(
                state=UNKNOWN,
                available=decision.available,
                reasons=["Ambiguous authorization wording stays unknown."],
                evidence=decision.evidence,
                dimensions=decision.dimensions,
                version=decision.version,
                content_hash=decision.content_hash,
                profile_hash=decision.profile_hash,
            )
    event = (
        "eligibility_unknown" if decision.state == UNKNOWN else "eligibility_resolved"
    )
    log.info(event, job_id=job.id, state=decision.state)
    return decision


def assign_eligibility(job: Job, decision: EligibilityDecision) -> None:
    """Copy a decision onto the job. Does not change score, tier, or status."""
    job.eligibility_state = decision.state
    job.eligibility_reasons = list(decision.reasons)
    job.eligibility_evidence = list(decision.evidence)
    job.eligibility_dimensions = {
        name: asdict(item) for name, item in decision.dimensions.items()
    }
    job.eligibility_version = decision.version
    job.eligibility_content_hash = decision.content_hash
    job.eligibility_profile_hash = decision.profile_hash


async def attach_eligibility(
    job: Job,
    profile: Profile,
    *,
    client: LLMClient | None = None,
) -> EligibilityDecision:
    decision = await evaluate_eligibility(job, profile, client=client)
    assign_eligibility(job, decision)
    return decision


def eligibility_column_types() -> dict[str, str]:
    """PostgreSQL types for the eligibility columns. Used by the schema test."""
    return {
        "eligibility_state": "VARCHAR(32)",
        "eligibility_reasons": "JSON",
        "eligibility_evidence": "JSON",
        "eligibility_dimensions": "JSON",
        "eligibility_version": "VARCHAR(32)",
        "eligibility_content_hash": "VARCHAR(64)",
        "eligibility_profile_hash": "VARCHAR(64)",
    }
