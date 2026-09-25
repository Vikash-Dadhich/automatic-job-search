"""Deterministic negative pre-filter before LLM scoring."""

from __future__ import annotations

import re
from dataclasses import dataclass

from config.profile import Profile
from config.settings import get_settings
from core.db import Job, Source
from core.textmatch import (
    company_matches,
    contains_phrase,
    is_remote_location,
    location_matches,
)
from scraper.models import RawPosting

# Word-boundary match so "international" / "internal" are not false-positives.
_INTERN_WORD_RE = re.compile(r"\bintern(ship)?\b", re.IGNORECASE)

_CLEARANCE_PATTERNS = (
    r"security clearance",
    r"active\s+(ts/?sci|top secret|secret)\b",
    r"\bts/?sci\b",
    r"must\s+(?:have|hold|possess).{0,40}clearance",
    r"requires?.{0,30}clearance",
    r"us\s+citizenship\s+required.{0,40}clearance",
)
_STAFFING_PATTERNS = (
    r"staffing\s+agency",
    r"recruiting\s+firm",
    r"third[- ]party\s+(?:staffing|recruiter)",
    r"\brevature\b",
    r"\bdice\b",
    r"contract[- ]to[- ]hire\s+agency",
)
# Captures the demanded years so the gate can be compared against the profile.
_YOE_REQUIRED_RE = re.compile(
    r"\b(\d{1,2})\s*\+?\s*(?:-|to|–)?\s*(?:\d{1,2})?\s*\+?\s*(?:years?|yrs?)"
    r"(?:\s+of)?\s+(?:relevant\s+|professional\s+|related\s+)?(?:experience|exp\.?)\b",
    re.IGNORECASE,
)
_SPONSORSHIP_HOSTILE_PATTERNS = (
    r"no\s+(?:visa\s+)?sponsorship",
    # do/does not + cannot offer/provide sponsorship
    r"do(?:es)?\s+not\s+(?:offer|provide)\s+(?:visa\s+)?sponsorship",
    r"cannot\s+(?:offer|provide|sponsor)\b",
    r"can\s+not\s+(?:offer|provide|sponsor)\b",
    r"must\s+be\s+(?:a\s+)?(?:us|u\.s\.)\s+citizen",
    r"(?:us|u\.s\.)\s+citizens?\s+only",
    r"citizenship\s+required",
    # "requires US citizenship" (word order reversed from "citizenship required")
    r"requires?\s+(?:us|u\.s\.)\s+citizenship",
    r"unable\s+to\s+sponsor",
    r"will\s+not\s+sponsor",
)
# Patterns that signal the company actively sponsors visas.
# Hostile patterns are checked first, so negated variants ("we do NOT sponsor")
# are never misclassified as friendly.
_SPONSORSHIP_FRIENDLY_PATTERNS = (
    r"visa\s+sponsorship\s+(?:is\s+)?(?:available|provided|offered)",
    r"we\s+(?:do\s+)?(?:offer|provide)\s+(?:visa\s+)?sponsorship",
    r"sponsorship\s+(?:is\s+)?(?:available|provided|offered)",
    r"open\s+to\s+(?:visa\s+)?sponsorship",
    r"we\s+(?:will\s+)?sponsor\b",
    # OPT/CPT/F-1 friendly signals common in internship JDs
    r"\bopt(?:\s*/\s*cpt)?\s+(?:friendly|accepted|welcome|eligible|ok|okay|students?\s+welcome)\b",
    r"\bcpt(?:\s*/\s*opt)?\s+(?:friendly|accepted|welcome|eligible|ok|okay)\b",
    r"\bf-?1\s+(?:visa\s+)?(?:students?\s+)?(?:friendly|accepted|welcome|eligible)\b",
    r"\bopt\s+and\s+cpt\b",
)


@dataclass(frozen=True, slots=True)
class FilterResult:
    passed: bool
    reason: str | None = None


def sponsorship_signal(text: str) -> str:
    """Classify a JD's stance on visa sponsorship without a profile dependency.

    Returns:
        ``"hostile"``  – explicit refusal (no sponsorship / citizens only).
        ``"friendly"`` – explicit offer (will sponsor / OPT welcome / …).
        ``"unknown"``  – no mention either way; candidate should verify.

    Hostile is checked before friendly so a phrase like
    "We do NOT sponsor visas" is never misclassified.
    """
    haystack = text.lower()
    for pattern in _SPONSORSHIP_HOSTILE_PATTERNS:
        if re.search(pattern, haystack, re.IGNORECASE):
            return "hostile"
    for pattern in _SPONSORSHIP_FRIENDLY_PATTERNS:
        if re.search(pattern, haystack, re.IGNORECASE):
            return "friendly"
    return "unknown"


def _seniority_reason(title: str) -> str | None:
    settings = get_settings()
    if not settings.enable_seniority_filter:
        return None
    for keyword in settings.seniority_title_keywords:
        if contains_phrase(title, keyword):
            return f"seniority mismatch title: {title}"
    return None


def max_acceptable_years(profile: Profile) -> int:
    """Highest demanded YOE still worth scoring, derived from the candidate."""
    settings = get_settings()
    if settings.max_required_years_experience is not None:
        return settings.max_required_years_experience
    return int(round(profile.total_years_experience())) + settings.years_experience_slack


def _yoe_reason(haystack: str, profile: Profile) -> str | None:
    """Reject only when every stated YOE requirement is out of reach.

    A JD often lists both "3+ years required" and "8+ years preferred"; dropping
    on the highest number alone discards reachable roles.
    """
    demands = [int(m.group(1)) for m in _YOE_REQUIRED_RE.finditer(haystack)]
    demands = [d for d in demands if 0 < d <= 40]
    if not demands:
        return None
    ceiling = max_acceptable_years(profile)
    if min(demands) > ceiling:
        return f"requires {min(demands)}+ years experience (ceiling {ceiling})"
    return None


def evaluate(posting: RawPosting, profile: Profile) -> FilterResult:
    """Return whether a posting should proceed to scoring."""
    settings = get_settings()
    haystack = _haystack(posting)
    exclusions = profile.exclusions

    # Company blocklist (whole-name match so "Meta" does not drop "MetLife")
    for blocked in exclusions.companies:
        if company_matches(posting.company, blocked):
            return FilterResult(False, f"excluded company: {blocked}")

    # Explicit exclusion keywords
    for keyword in exclusions.keywords:
        if contains_phrase(haystack, keyword):
            return FilterResult(False, f"excluded keyword: {keyword}")

    # Clearance hard gate
    if exclusions.clearance_required:
        for pattern in _CLEARANCE_PATTERNS:
            if re.search(pattern, haystack, re.IGNORECASE):
                return FilterResult(False, f"clearance required matched: {pattern}")

    # Third-party staffing
    if exclusions.third_party_staffing:
        for pattern in _STAFFING_PATTERNS:
            if re.search(pattern, haystack, re.IGNORECASE):
                return FilterResult(False, f"staffing agency matched: {pattern}")

    # Internship-only gate: title must carry at least one internship signal.
    # Positive signals: "intern/internship", "summer 202x", "new grad/graduate".
    # Seniority words (senior/lead/staff/…) override a positive match and still
    # drop the role — avoids "Senior PM, New Grad Program" sneaking through.
    # Enabled when INTERNSHIP_ONLY=true (summer internship search mode).
    if settings.internship_only:
        title_lower = (posting.title or "").lower()
        _INTERN_POSITIVE = (
            "intern",
            "internship",
            "summer 2025",
            "summer 2026",
            "summer 2027",
            "summer 2028",
            "new grad",
            "new graduate",
        )
        _INTERN_SENIORITY_BLOCK = (
            "senior",
            "sr.",
            " lead ",
            "lead ",
            " staff ",
            "staff ",
            "principal",
            "director",
            "head of",
            " vp ",
            "vice president",
        )
        has_intern_word = bool(_INTERN_WORD_RE.search(posting.title or ""))
        has_positive = has_intern_word or any(sig in title_lower for sig in _INTERN_POSITIVE)
        # Seniority block only applies when we're relying on softer signals
        # (new grad, summer 202x) — not when "intern/internship" is explicit.
        # This preserves roles like "Summer VP Internship" (bank MBA programs).
        has_seniority = (not has_intern_word) and any(
            sig in title_lower for sig in _INTERN_SENIORITY_BLOCK
        )
        if not has_positive:
            return FilterResult(False, "internship_only: no internship signal in title")
        if has_seniority:
            return FilterResult(False, f"internship_only: seniority word in title: {posting.title}")

    # Seniority mismatch (title-only — avoid matching inside descriptions)
    seniority = _seniority_reason(posting.title or "")
    if seniority:
        return FilterResult(False, seniority)

    # YOE gate, scaled to the candidate's own experience
    yoe = _yoe_reason(haystack, profile)
    if yoe:
        return FilterResult(False, yoe)

    # Sponsorship-hostile language when candidate needs sponsorship
    auth = profile.work_authorization
    if auth.sponsorship_required or auth.needs_visa_sponsorship:
        for pattern in _SPONSORSHIP_HOSTILE_PATTERNS:
            if re.search(pattern, haystack, re.IGNORECASE):
                return FilterResult(False, f"sponsorship-hostile matched: {pattern}")

    # Location gate
    loc_result = _location_ok(posting.location, profile)
    if not loc_result.passed:
        return loc_result

    return FilterResult(True, None)


def evaluate_job(job: Job, profile: Profile) -> FilterResult:
    """Apply the same hard-negative rules to a persisted Job (scoring backlog guard)."""
    source = job.source if isinstance(job.source, Source) else Source(job.source)
    posting = RawPosting(
        source=source,
        external_id=job.external_id or f"job-{job.id or 0}",
        title=job.title or "Unknown",
        company=job.company or "Unknown",
        location=job.location,
        url=job.url or "https://example.com/job",
        description_clean=job.description_clean,
    )
    return evaluate(posting, profile)


def _haystack(posting: RawPosting) -> str:
    parts = [
        posting.title or "",
        posting.company or "",
        posting.location or "",
        posting.description_clean or "",
    ]
    return "\n".join(parts).lower()


def location_acceptable(location: str | None, profile: Profile) -> bool:
    """Shared geo rule for JobSpy pre-filtering, ingest, and the scoring guard."""
    return _location_ok(location, profile).passed


def _location_ok(location: str | None, profile: Profile) -> FilterResult:
    prefs = profile.preferences
    if not location:
        # Unknown location: soft-pass and let the LLM judge from the JD body.
        return FilterResult(True, None)

    if is_remote_location(location):
        if prefs.remote_ok:
            return FilterResult(True, None)
        return FilterResult(False, "remote role but remote_ok=false")

    # On-site / hybrid: city+state aware so Portland OR != Portland ME
    non_remote_prefs = [p for p in prefs.locations if p.strip().lower() != "remote"]
    for preferred in non_remote_prefs:
        if location_matches(location, preferred):
            return FilterResult(True, None)

    if prefs.relocation_ok:
        return FilterResult(True, None)
    if not non_remote_prefs and prefs.remote_ok:
        # Remote-only preference: an on-site role elsewhere is off-target.
        return FilterResult(False, f"off-target location: {location}")
    if non_remote_prefs:
        return FilterResult(False, f"off-target location: {location}")

    return FilterResult(True, None)
