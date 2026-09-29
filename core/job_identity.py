"""Deterministic posting identity. Uncertain matches stay separate jobs."""

from __future__ import annotations

import re
from urllib.parse import parse_qsl, urlencode, urlparse, urlunparse

from core.textmatch import company_tokens, is_remote_location, location_matches, normalize_text

_TRACKING_KEYS = frozenset(
    {
        "fbclid",
        "gclid",
        "gclsrc",
        "dclid",
        "msclkid",
        "yclid",
        "igshid",
        "mc_cid",
        "mc_eid",
        "mkt_tok",
        "_ga",
        "_gl",
        "si",
        "trk",
        "trkinfo",
        "tracking",
        "ref",
        "ref_src",
        "referrer",
    }
)
_GENERIC_LOCATIONS = frozenset(
    {
        "united states",
        "usa",
        "us",
        "remote",
        "multiple locations",
        "various locations",
        "various",
    }
)
_TITLE_SPACE = re.compile(r"\s+")


def canonicalize_job_url(url: str | None) -> str | None:
    """Drop fragments and tracking parameters. Keep query keys that can be the posting id."""
    raw = (url or "").strip()
    if not raw:
        return None
    parsed = urlparse(raw)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        return None
    kept = [
        (key, value)
        for key, value in parse_qsl(parsed.query, keep_blank_values=False)
        if not _is_tracking_param(key)
    ]
    kept.sort()
    path = parsed.path or ""
    if len(path) > 1:
        path = path.rstrip("/")
    return urlunparse(
        (
            parsed.scheme.lower(),
            parsed.netloc.lower(),
            path,
            "",
            urlencode(kept),
            "",
        )
    )


def url_identifies_posting(canonical: str | None) -> bool:
    """True when the URL is a posting, not a bare site homepage."""
    if not canonical:
        return False
    parsed = urlparse(canonical)
    segments = [part for part in parsed.path.split("/") if part]
    if segments:
        return True
    return bool(parse_qsl(parsed.query))


def same_posting_url(left: str | None, right: str | None) -> bool:
    """True when both URLs canonicalize to one posting identity."""
    a = canonicalize_job_url(left)
    b = canonicalize_job_url(right)
    if not a or not b or a != b:
        return False
    return url_identifies_posting(a)


def urls_conflict(left: str | None, right: str | None) -> bool:
    """True when both URLs identify postings and those postings differ."""
    a = canonicalize_job_url(left)
    b = canonicalize_job_url(right)
    if not a or not b or not url_identifies_posting(a) or not url_identifies_posting(b):
        return False
    return a != b


def normalize_title(title: str | None) -> str:
    return _TITLE_SPACE.sub(" ", (title or "").strip().lower())


def same_employer(left: str | None, right: str | None) -> bool:
    """Exact company tokens. A shorter name is not treated as the same employer."""
    a = company_tokens(left)
    b = company_tokens(right)
    return bool(a) and a == b


def locations_conflict(left: str | None, right: str | None) -> bool:
    """True when both locations are specific and name different places."""
    a = (left or "").strip()
    b = (right or "").strip()
    if not a or not b:
        return False
    if normalize_text(a) in _GENERIC_LOCATIONS or normalize_text(b) in _GENERIC_LOCATIONS:
        return False
    if is_remote_location(a) and is_remote_location(b):
        return False
    if location_matches(a, b) or location_matches(b, a):
        return False
    return True


def locations_agree(left: str | None, right: str | None) -> bool:
    """Both sides name a compatible place. A missing location does not count."""
    a = (left or "").strip()
    b = (right or "").strip()
    if not a or not b or locations_conflict(a, b):
        return False
    if is_remote_location(a) and is_remote_location(b):
        return True
    return location_matches(a, b) or location_matches(b, a)


def strong_field_match(
    *,
    company_a: str | None,
    title_a: str | None,
    location_a: str | None,
    company_b: str | None,
    title_b: str | None,
    location_b: str | None,
) -> bool:
    """Company, title, and an agreeing location. Not enough without a shared description hash."""
    return (
        same_employer(company_a, company_b)
        and normalize_title(title_a) == normalize_title(title_b)
        and bool(normalize_title(title_a))
        and locations_agree(location_a, location_b)
    )


def _is_tracking_param(key: str) -> bool:
    name = key.strip().lower()
    return name.startswith("utm_") or name in _TRACKING_KEYS
