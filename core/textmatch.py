"""Shared matching + truncation helpers used by filters, scoring, and answers.

Centralized so scraper pre-filters, the scoring backlog guard, and the JobSpy
client agree on what "same company" / "acceptable location" mean.
"""

from __future__ import annotations

import re

_WORD_SPLIT_RE = re.compile(r"[^a-z0-9]+")
# Legal suffixes dropped before comparing company names.
_COMPANY_SUFFIXES = frozenset(
    {
        "inc",
        "llc",
        "ltd",
        "limited",
        "corp",
        "corporation",
        "co",
        "company",
        "plc",
        "gmbh",
        "sa",
        "ag",
        "nv",
        "bv",
        "pvt",
        "private",
        "group",
        "holdings",
        "technologies",
        "technology",
        "labs",
    }
)
_REMOTE_TOKENS = ("remote", "work from home", "wfh", "anywhere", "distributed")
# US state abbreviations, used to disambiguate same-named cities.
_STATE_RE = re.compile(r"\b([a-z]{2})\b")


def normalize_text(value: str | None) -> str:
    return re.sub(r"\s+", " ", (value or "").strip().lower())


def contains_phrase(haystack: str | None, needle: str | None) -> bool:
    """Whole-phrase, word-boundary match — avoids 'Meta' hitting 'MetLife'."""
    text = normalize_text(haystack)
    phrase = normalize_text(needle)
    if not text or not phrase:
        return False
    return re.search(rf"(?<!\w){re.escape(phrase)}(?!\w)", text) is not None


def company_tokens(name: str | None) -> tuple[str, ...]:
    """Significant tokens of a company name with legal suffixes removed."""
    words = [w for w in _WORD_SPLIT_RE.split(normalize_text(name)) if w]
    kept = [w for w in words if w not in _COMPANY_SUFFIXES]
    return tuple(kept or words)


def company_matches(candidate: str | None, target: str | None) -> bool:
    """True when two company names refer to the same employer.

    'Google' == 'Google LLC'; 'Meta' != 'MetLife'.
    """
    a = company_tokens(candidate)
    b = company_tokens(target)
    if not a or not b:
        return False
    if a == b:
        return True
    # Allow the shorter name to be a leading subsequence ("Barclays" vs "Barclays Bank").
    short, long = (a, b) if len(a) <= len(b) else (b, a)
    return long[: len(short)] == short


def is_remote_location(location: str | None) -> bool:
    """Whole-word remote detection so 'Remoteville, IN' is not treated as remote."""
    return any(contains_phrase(location, token) for token in _REMOTE_TOKENS)


def _city_state(value: str | None) -> tuple[str, str | None]:
    """Split 'Seattle, WA, US' into ('seattle', 'wa')."""
    text = normalize_text(value)
    if not text:
        return "", None
    parts = [p.strip() for p in text.split(",") if p.strip()]
    city = parts[0] if parts else ""
    state: str | None = None
    for part in parts[1:]:
        match = _STATE_RE.fullmatch(part)
        if match and match.group(1) not in {"us", "usa"}:
            state = match.group(1)
            break
    return city, state


def location_matches(location: str | None, preferred: str) -> bool:
    """True when a posting location satisfies one preference entry.

    Compares city and (when both sides declare one) state, so 'Portland, OR'
    does not satisfy a 'Portland, ME' preference.
    """
    pref = normalize_text(preferred)
    if not pref:
        return False
    if pref == "remote":
        return is_remote_location(location)

    loc_city, loc_state = _city_state(location)
    pref_city, pref_state = _city_state(pref)
    if not loc_city or not pref_city:
        return False
    if loc_city != pref_city and not contains_phrase(location, pref_city):
        return False
    if loc_state and pref_state and loc_state != pref_state:
        return False
    return True


def truncate_middle(text: str, max_chars: int, *, marker: str = "\n[... trimmed ...]\n") -> str:
    """Keep the head and tail of long text.

    Job descriptions bury sponsorship and YOE requirements at the bottom, so a
    plain head-chop silently hides the facts scoring depends on.
    """
    cleaned = (text or "").strip()
    if max_chars <= 0 or len(cleaned) <= max_chars:
        return cleaned
    budget = max_chars - len(marker)
    if budget <= 0:
        return cleaned[:max_chars].rstrip()
    head = (budget * 2) // 3
    tail = budget - head
    return cleaned[:head].rstrip() + marker + cleaned[-tail:].lstrip()
