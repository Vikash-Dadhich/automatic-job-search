"""Payload compression, schema minification, and prompt-caching utilities."""

from __future__ import annotations

import json
from typing import Any

from config.settings import get_settings
from core.textmatch import truncate_middle


def cache_block(text: str, *, block_type: str = "text") -> dict[str, Any]:
    """Build an Anthropic system content block with ephemeral prompt caching."""
    return {
        "type": block_type,
        "text": text,
        "cache_control": {"type": "ephemeral"},
    }


def minify_job(job: Any, *, max_chars: int | None = None) -> str:
    """Compact job description for scoring: title/company/location + cleaned JD."""
    title = getattr(job, "title", "") or ""
    company = getattr(job, "company", "") or ""
    location = getattr(job, "location", None) or "N/A"
    description = getattr(job, "description_clean", None) or ""
    limit = max_chars if max_chars is not None else get_settings().max_jd_chars
    description = truncate_middle(description, limit)

    parts = [
        f"Title: {title}",
        f"Company: {company}",
        f"Location: {location}",
    ]
    if description:
        parts.append("")
        parts.append(description)
    return "\n".join(parts)


def approx_tokens(text: str) -> int:
    """Rough token estimate (~4 chars/token). Good enough for budgeting."""
    if not text:
        return 0
    return max(1, (len(text) + 3) // 4)


def compact_json_dumps(obj: Any) -> str:
    """Serialize JSON with no extra whitespace (minimize output tokens)."""
    return json.dumps(obj, separators=(",", ":"), ensure_ascii=False)
