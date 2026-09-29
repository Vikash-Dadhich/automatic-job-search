"""HTML → clean text and section extraction for token-efficient scoring."""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass
from enum import StrEnum

from selectolax.parser import HTMLParser

from config.settings import get_settings
from core.textmatch import truncate_middle

# Shorter than this after normalization, a non-empty JD is extraction-suspicious.
# This is description length, not job quality.
SUSPICIOUS_BELOW = 80
_TRIM_MARKER = "\n[... trimmed ...]\n"

_STRIP_TAGS = ("script", "style", "noscript", "nav", "footer", "header", "svg")
# Longer phrases first so the line regex does not stop at a shorter prefix.
_SECTION_HEADERS = (
    "minimum qualifications",
    "preferred qualifications",
    "required qualifications",
    "basic qualifications",
    "what we're looking for",
    "what you will do",
    "what you'll do",
    "about the role",
    "about this role",
    "about the team",
    "about you",
    "responsibilities",
    "qualifications",
    "requirements",
    "compensation",
    "experience",
    "education",
    "benefits",
    "skills",
    "required skills",
)
_BOILER_RE = re.compile(
    r"(?i)\b(equal opportunity|eeoc|privacy policy|cookie policy|all rights reserved|copyright)\b"
)
_HEADER_RE = re.compile(
    r"(?im)^(?:#{1,6}\s*)?"
    r"(" + "|".join(re.escape(h) for h in _SECTION_HEADERS) + r")"
    r"\s*:?\s*$"
)
_WS_RE = re.compile(r"[ \t]+\n")
_MULTI_NL_RE = re.compile(r"\n{3,}")


class JdStatus(StrEnum):
    missing = "missing"
    present = "present"
    truncated = "truncated"
    suspicious = "suspicious"


@dataclass(frozen=True, slots=True)
class NormalizedJd:
    """Persisted description plus how it was produced. Not a fit judgment."""

    text: str
    status: JdStatus
    char_count: int
    truncated: bool
    extraction_path: str


def html_to_text(html: str) -> str:
    """Strip boilerplate tags and return readable plain text."""
    if not html or not html.strip():
        return ""
    try:
        tree = HTMLParser(html)
    except Exception:
        plain = re.sub(r"<[^>]+>", " ", html)
        return _normalize_whitespace(plain)
    for tag in _STRIP_TAGS:
        for node in tree.css(tag):
            node.decompose()
    text = tree.body.text(separator="\n") if tree.body else tree.text(separator="\n")
    return _normalize_whitespace(text)


def extract_sections(text: str) -> str:
    """Keep the JD body, including text before the first known heading.

    Falls back to the full trimmed text when no known section headers are found
    or the headed extract collapses.
    """
    return normalize_description(text).text


def normalize_description(text: str, *, from_html: bool = False) -> NormalizedJd:
    """Normalize one JD and record whether it is missing, short, or cut off."""
    raw = text or ""
    if from_html:
        cleaned_source = html_to_text(raw)
        path = "html"
    else:
        cleaned_source = raw
        path = "markdown" if re.search(r"(?m)^#{1,6}\s+\S", raw) else "plain"

    body, used_sections = _extract_body(cleaned_source)
    if used_sections:
        path = "sections"
    stored, truncated = _truncate(body)
    status = _status(stored, truncated)
    if status is JdStatus.missing:
        path = "empty"
    return NormalizedJd(
        text=stored,
        status=status,
        char_count=len(stored),
        truncated=truncated,
        extraction_path=path,
    )


def content_hash(text: str) -> str:
    """Stable SHA-256 of normalized text for dedup."""
    normalized = _normalize_whitespace(text).lower().encode()
    return hashlib.sha256(normalized).hexdigest()


def _extract_body(text: str) -> tuple[str, bool]:
    cleaned = _normalize_whitespace(text)
    if not cleaned:
        return "", False
    matches = list(_HEADER_RE.finditer(cleaned))
    if not matches:
        return cleaned, False

    parts: list[str] = []
    preamble = _drop_boilerplate_lines(cleaned[: matches[0].start()])
    if len(preamble) >= SUSPICIOUS_BELOW:
        parts.append(preamble)
    for index, match in enumerate(matches):
        start = match.start()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(cleaned)
        block = cleaned[start:end].strip()
        if block:
            parts.append(block)
    combined = "\n\n".join(parts).strip()
    if len(combined) < SUSPICIOUS_BELOW:
        return cleaned, False
    return combined, True


def _truncate(text: str) -> tuple[str, bool]:
    if not text:
        return "", False
    # Storage keeps headroom over the scoring budget so re-scoring can widen later.
    limit = max(get_settings().max_jd_chars * 2, 4000)
    stored = truncate_middle(text, limit)
    truncated = len(text) > len(stored) or _TRIM_MARKER in stored
    return stored, truncated


def _status(text: str, truncated: bool) -> JdStatus:
    if not text.strip():
        return JdStatus.missing
    if truncated:
        return JdStatus.truncated
    if len(text) < SUSPICIOUS_BELOW:
        return JdStatus.suspicious
    return JdStatus.present


def _drop_boilerplate_lines(text: str) -> str:
    kept = [line for line in text.split("\n") if line.strip() and not _BOILER_RE.search(line)]
    return "\n".join(kept).strip()


def _normalize_whitespace(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = _WS_RE.sub("\n", text)
    text = _MULTI_NL_RE.sub("\n\n", text)
    lines = [line.strip() for line in text.split("\n")]
    collapsed: list[str] = []
    for line in lines:
        if collapsed and line and line == collapsed[-1]:
            continue
        collapsed.append(line)
    return "\n".join(collapsed).strip()
