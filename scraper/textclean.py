"""HTML → clean text and section extraction for token-efficient scoring."""

from __future__ import annotations

import hashlib
import re

from selectolax.parser import HTMLParser

from config.settings import get_settings
from core.textmatch import truncate_middle

_STRIP_TAGS = ("script", "style", "noscript", "nav", "footer", "header", "svg")
_SECTION_HEADERS = (
    "requirements",
    "responsibilities",
    "qualifications",
    "minimum qualifications",
    "preferred qualifications",
    "what you'll do",
    "what you will do",
    "what we're looking for",
    "about the role",
    "about this role",
    "required skills",
    "basic qualifications",
)
_HEADER_RE = re.compile(
    r"(?im)^(?:#{1,6}\s*)?"
    r"(" + "|".join(re.escape(h) for h in _SECTION_HEADERS) + r")"
    r"\s*:?\s*$"
)
_WS_RE = re.compile(r"[ \t]+\n")
_MULTI_NL_RE = re.compile(r"\n{3,}")


def html_to_text(html: str) -> str:
    """Strip boilerplate tags and return readable plain text."""
    if not html or not html.strip():
        return ""
    tree = HTMLParser(html)
    for tag in _STRIP_TAGS:
        for node in tree.css(tag):
            node.decompose()
    text = tree.body.text(separator="\n") if tree.body else tree.text(separator="\n")
    return _normalize_whitespace(text)


def extract_sections(text: str) -> str:
    """Keep Requirements / Responsibilities / Qualifications blocks when present.

    Falls back to the full trimmed text when no known section headers are found.
    """
    cleaned = _normalize_whitespace(text)
    if not cleaned:
        return ""

    # Storage keeps headroom over the scoring budget so re-scoring can widen later.
    limit = max(get_settings().max_jd_chars * 2, 4000)

    matches = list(_HEADER_RE.finditer(cleaned))
    if not matches:
        return truncate_middle(cleaned, limit)

    parts: list[str] = []
    for i, match in enumerate(matches):
        start = match.start()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(cleaned)
        block = cleaned[start:end].strip()
        if block:
            parts.append(block)

    combined = "\n\n".join(parts)
    # If extraction collapsed to almost nothing, fall back
    if len(combined) < 80:
        return truncate_middle(cleaned, limit)
    return truncate_middle(combined, limit)


def content_hash(text: str) -> str:
    """Stable SHA-256 of normalized text for dedup."""
    normalized = _normalize_whitespace(text).lower().encode()
    return hashlib.sha256(normalized).hexdigest()


def _normalize_whitespace(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = _WS_RE.sub("\n", text)
    text = _MULTI_NL_RE.sub("\n\n", text)
    lines = [line.strip() for line in text.split("\n")]
    return "\n".join(lines).strip()
