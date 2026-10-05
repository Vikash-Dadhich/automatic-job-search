"""Conservative application-deadline reading.

Explicit apply-by or closing dates only. This does not score, rank, or decide
whether to apply. A missing year is not filled in.
"""

from __future__ import annotations

import re
from datetime import date
from typing import Literal

from pydantic import BaseModel

from scraper.textclean import SUSPICIOUS_BELOW

DEADLINE_EXTRACTION_VERSION = "deadline-v1"
_EVIDENCE_LIMIT = 160

DeadlineState = Literal["CONFIRMED", "AMBIGUOUS", "NOT_FOUND", "UNUSABLE"]

_MONTHS = {
    "january": 1,
    "jan": 1,
    "february": 2,
    "feb": 2,
    "march": 3,
    "mar": 3,
    "april": 4,
    "apr": 4,
    "may": 5,
    "june": 6,
    "jun": 6,
    "july": 7,
    "jul": 7,
    "august": 8,
    "aug": 8,
    "september": 9,
    "sept": 9,
    "sep": 9,
    "october": 10,
    "oct": 10,
    "november": 11,
    "nov": 11,
    "december": 12,
    "dec": 12,
}
_MONTH = (
    r"january|february|march|april|may|june|july|august|september|october|november|"
    r"december|jan|feb|mar|apr|jun|jul|aug|sept|sep|oct|nov|dec"
)
_DATE = (
    rf"\b(?:{_MONTH})\.?\s+\d{{1,2}}(?:st|nd|rd|th)?\b(?!\d)(?:,?\s+20\d{{2}})?"
    rf"|\b\d{{1,2}}(?:st|nd|rd|th)?\s+(?:{_MONTH})\b(?:,?\s+20\d{{2}})?"
    rf"|\b20\d{{2}}-\d{{2}}-\d{{2}}\b"
    rf"|\b\d{{1,2}}/\d{{1,2}}/20\d{{2}}\b"
    rf"|\b\d{{1,2}}/\d{{1,2}}/\d{{2}}\b"
)
_GAP = r"(?:[\s*:#\-–—.,()\[\]/]|\\|\*|\bon\b|\bdate\b|\bis\b|\bthe\b){0,80}"
_CUE = (
    r"deadline\s+to\s+apply|application\s+deadline|applications?\s+deadline|"
    r"(?:job\s+)?posting\s+expiration(?:\s+date)?|"
    r"application\s+window[\s\S]{0,60}?will\s+close|"
    r"applications?\s+(?:will\s+)?close|closing\s+date|close\s+date|"
    r"apply\s+no\s+later\s+than|apply\s+on\s+or\s+before|apply\s+before|apply\s+by|"
    r"must\s+be\s+(?:received|submitted)\s+by|applications?\s+accepted\s+until|"
    r"submit(?:\s+your)?(?:\s+application)?\s+by|"
    r"recruiting\s+for\s+this\s+role\s+ends\s+on|posted\s+until|deadline\s+is"
)
_CLEAR = re.compile(rf"(?P<cue>{_CUE}){_GAP}(?P<date>{_DATE})", re.IGNORECASE)
_CUE_ONLY = re.compile(_CUE, re.IGNORECASE)
_YEAR_TAIL = re.compile(
    r"^(?:[\s*\\,._\-]|\\|\b(?:st|nd|rd|th)\b){0,16}(20\d{2})\b",
    re.IGNORECASE,
)
_EXCLUDE = re.compile(
    r"\b(?:interview|last\s+revised|date\s+posted|date\s+live|job\s+posting\s+date|"
    r"start\s+date|employment\s+dates?|graduat(?:e|ion)|born|effective)\b",
    re.IGNORECASE,
)
_MONTH_DAY = re.compile(
    rf"({_MONTH})\.?\s+(\d{{1,2}})(?:st|nd|rd|th)?(?:,?\s+(20\d{{2}}))?",
    re.IGNORECASE,
)
_DAY_MONTH = re.compile(
    rf"(\d{{1,2}})(?:st|nd|rd|th)?\s+({_MONTH})\.?(?:,?\s+(20\d{{2}}))?",
    re.IGNORECASE,
)


class ApplicationDeadline(BaseModel):
    """One deadline reading. ``deadline_date`` is set only for a full valid date."""

    state: DeadlineState
    deadline_date: str | None = None
    evidence: str | None = None
    rule: str | None = None
    version: str = DEADLINE_EXTRACTION_VERSION


def empty_application_deadline() -> ApplicationDeadline:
    """Reading used when an older document has no deadline block."""
    return ApplicationDeadline(state="NOT_FOUND")


def extract_application_deadline(
    text: str,
    *,
    jd_status: str | None = None,
) -> ApplicationDeadline:
    """Read an explicit closing date. Unusable text is not guessed."""
    if jd_status in {"missing", "suspicious"} or len((text or "").strip()) < SUSPICIOUS_BELOW:
        return ApplicationDeadline(state="UNUSABLE")
    confirmed: ApplicationDeadline | None = None
    ambiguous: ApplicationDeadline | None = None
    covered: list[tuple[int, int]] = []
    for match in _CLEAR.finditer(text):
        if _excluded(text, match.start(), match.end()):
            continue
        covered.append((match.start(), match.end()))
        parsed, evidence = _from_match(text, match)
        if parsed is not None:
            if confirmed is None:
                confirmed = ApplicationDeadline(
                    state="CONFIRMED",
                    deadline_date=parsed,
                    evidence=evidence,
                    rule=_rule_id(match.group("cue")),
                )
            continue
        if ambiguous is None:
            ambiguous = ApplicationDeadline(
                state="AMBIGUOUS",
                evidence=evidence,
                rule=_rule_id(match.group("cue")),
            )
    if confirmed is not None:
        return confirmed
    for match in _CUE_ONLY.finditer(text):
        if _excluded(text, match.start(), match.end()):
            continue
        if any(start <= match.start() < end for start, end in covered):
            continue
        return ApplicationDeadline(
            state="AMBIGUOUS",
            evidence=_clip(match.group(0)),
            rule=_rule_id(match.group(0)),
        )
    if ambiguous is not None:
        return ambiguous
    return ApplicationDeadline(state="NOT_FOUND")


def _from_match(text: str, match: re.Match[str]) -> tuple[str | None, str]:
    following = text[match.end() : match.end() + 40]
    iso, extra = _parse_date(match.group("date"), following)
    evidence = _clip(text[match.start() : match.end() + extra])
    return iso, evidence


def _parse_date(token: str, following: str) -> tuple[str | None, int]:
    stripped = " ".join(token.split())
    iso_match = re.fullmatch(r"(20\d{2})-(\d{2})-(\d{2})", stripped)
    if iso_match:
        parsed = _valid(int(iso_match.group(1)), int(iso_match.group(2)), int(iso_match.group(3)))
        return parsed, 0
    numeric = re.fullmatch(r"(\d{1,2})/(\d{1,2})/(\d{2}|20\d{2})", stripped)
    if numeric:
        year_text = numeric.group(3)
        year = int(year_text) if len(year_text) == 4 else 2000 + int(year_text)
        return _valid(year, int(numeric.group(1)), int(numeric.group(2))), 0
    month_day = _MONTH_DAY.fullmatch(stripped)
    if month_day:
        return _named(month_day.group(1), month_day.group(2), month_day.group(3), following)
    day_month = _DAY_MONTH.fullmatch(stripped)
    if day_month:
        return _named(day_month.group(2), day_month.group(1), day_month.group(3), following)
    return None, 0


def _named(
    month_name: str,
    day_text: str,
    year_text: str | None,
    following: str,
) -> tuple[str | None, int]:
    month = _MONTHS.get(month_name.lower().rstrip("."))
    if month is None:
        return None, 0
    if year_text:
        return _valid(int(year_text), month, int(day_text)), 0
    tail = _YEAR_TAIL.match(following)
    if tail:
        return _valid(int(tail.group(1)), month, int(day_text)), tail.end()
    return None, 0


def _valid(year: int, month: int, day: int) -> str | None:
    try:
        return date(year, month, day).isoformat()
    except ValueError:
        return None


def _excluded(text: str, start: int, end: int) -> bool:
    window = text[max(0, start - 60) : end + 20]
    return _EXCLUDE.search(window) is not None


def _rule_id(cue: str) -> str:
    compact = re.sub(r"\s+", " ", cue).strip().lower()
    rules = (
        ("deadline to apply", "deadline_to_apply"),
        ("application deadline", "application_deadline"),
        ("posting expiration", "posting_expiration"),
        ("will close", "application_window_close"),
        ("applications close", "applications_close"),
        ("application close", "applications_close"),
        ("closing date", "closing_date"),
        ("close date", "close_date"),
        ("apply by", "apply_by"),
        ("apply before", "apply_by"),
        ("apply no later", "apply_by"),
        ("apply on or before", "apply_by"),
        ("submitted by", "must_be_submitted_by"),
        ("received by", "must_be_submitted_by"),
        ("accepted until", "accepted_until"),
        ("submit", "submit_by"),
        ("recruiting", "recruiting_ends"),
        ("posted until", "posted_until"),
        ("deadline is", "deadline_is"),
    )
    for needle, rule in rules:
        if needle in compact:
            return rule
    return "explicit_close"


def _clip(text: str) -> str:
    return " ".join(text.split())[:_EVIDENCE_LIMIT]
