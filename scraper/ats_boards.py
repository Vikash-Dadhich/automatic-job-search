"""Public job boards on Greenhouse, Lever and Ashby (async httpx, no login).

Each company publishes one JSON feed with every open role. Boards list far more
than internships, so rows without an internship signal in the title are dropped
here, before they use any of the ingest cap.
"""

from __future__ import annotations

import asyncio
import html
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from typing import Any

import httpx
import structlog
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from config.targets import AtsBoard
from core.db import Source
from scraper.filters import has_internship_signal
from scraper.models import RawPosting
from scraper.redact import redact_error

log = structlog.get_logger(__name__)

_CONCURRENCY = 5
_HEADERS = {"Accept": "application/json", "User-Agent": "job-agent/1.0 (personal job search)"}

class BoardTransientError(Exception):
    """Rate limit or server error. Retried, then reported as a failed board."""


@dataclass
class BoardRun:
    postings: list[RawPosting] = field(default_factory=list)
    not_found: list[str] = field(default_factory=list)
    failed: list[str] = field(default_factory=list)
    seen: int = 0
    kept: int = 0


def board_url(board: AtsBoard) -> str:
    token = board.token
    if board.provider == "greenhouse":
        return f"https://boards-api.greenhouse.io/v1/boards/{token}/jobs?content=true"
    if board.provider == "lever":
        return f"https://api.lever.co/v0/postings/{token}?mode=json"
    return f"https://api.ashbyhq.com/posting-api/job-board/{token}"


def _text(value: object) -> str | None:
    if isinstance(value, str):
        stripped = value.strip()
        return stripped or None
    return None


def _parse_time(value: object) -> datetime | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, int | float):
        # Lever sends epoch milliseconds.
        return datetime.fromtimestamp(value / 1000, tz=UTC)
    if isinstance(value, str) and value.strip():
        try:
            parsed = datetime.fromisoformat(value.strip().replace("Z", "+00:00"))
        except ValueError:
            return None
        return parsed if parsed.tzinfo else parsed.replace(tzinfo=UTC)
    return None


def _greenhouse(board: AtsBoard, data: Any) -> list[RawPosting]:
    jobs = data.get("jobs") if isinstance(data, dict) else None
    out: list[RawPosting] = []
    for item in jobs or []:
        if not isinstance(item, dict) or item.get("id") is None:
            continue
        title, url = _text(item.get("title")), _text(item.get("absolute_url"))
        if not title or not url:
            continue
        location = item.get("location")
        out.append(
            RawPosting(
                source=Source.greenhouse,
                external_id=f"{board.token}:{item['id']}",
                title=title,
                company=board.name,
                location=_text(location.get("name")) if isinstance(location, dict) else None,
                url=url,
                # Greenhouse sends the description as HTML-escaped HTML.
                description_html=html.unescape(_text(item.get("content")) or "") or None,
                posted_at=_parse_time(item.get("first_published") or item.get("updated_at")),
                tenant=board.token,
            )
        )
    return out


def _lever(board: AtsBoard, data: Any) -> list[RawPosting]:
    out: list[RawPosting] = []
    for item in data if isinstance(data, list) else []:
        if not isinstance(item, dict) or not _text(item.get("id")):
            continue
        title = _text(item.get("text"))
        url = _text(item.get("hostedUrl")) or _text(item.get("applyUrl"))
        if not title or not url:
            continue
        categories = item.get("categories")
        parts = [_text(item.get("description")) or ""]
        for block in item.get("lists") or []:
            if isinstance(block, dict):
                parts.append(f"<h3>{_text(block.get('text')) or ''}</h3>")
                parts.append(_text(block.get("content")) or "")
        parts.append(_text(item.get("additional")) or "")
        out.append(
            RawPosting(
                source=Source.lever,
                external_id=f"{board.token}:{item['id']}",
                title=title,
                company=board.name,
                location=(
                    _text(categories.get("location")) if isinstance(categories, dict) else None
                ),
                url=url,
                description_html="\n".join(part for part in parts if part) or None,
                posted_at=_parse_time(item.get("createdAt")),
                tenant=board.token,
            )
        )
    return out


def _ashby(board: AtsBoard, data: Any) -> list[RawPosting]:
    jobs = data.get("jobs") if isinstance(data, dict) else None
    out: list[RawPosting] = []
    for item in jobs or []:
        if not isinstance(item, dict) or not _text(item.get("id")):
            continue
        if item.get("isListed") is False:
            continue
        title = _text(item.get("title"))
        url = _text(item.get("jobUrl")) or _text(item.get("applyUrl"))
        if not title or not url:
            continue
        location = _text(item.get("location"))
        if item.get("isRemote") and not location:
            location = "Remote"
        out.append(
            RawPosting(
                source=Source.ashby,
                external_id=f"{board.token}:{item['id']}",
                title=title,
                company=board.name,
                location=location,
                url=url,
                description_html=_text(item.get("descriptionHtml")),
                description_clean=None
                if _text(item.get("descriptionHtml"))
                else _text(item.get("descriptionPlain")),
                posted_at=_parse_time(item.get("publishedAt")),
                tenant=board.token,
            )
        )
    return out


_PARSERS = {"greenhouse": _greenhouse, "lever": _lever, "ashby": _ashby}


def parse_board(board: AtsBoard, data: Any) -> list[RawPosting]:
    """Turn one provider payload into postings. Unknown shapes give an empty list."""
    return _PARSERS[board.provider](board, data)


def keep_posting(
    posting: RawPosting,
    *,
    max_age_hours: int | None,
    now: datetime | None = None,
) -> bool:
    if not has_internship_signal(posting.title):
        return False
    if max_age_hours is not None and posting.posted_at is not None:
        cutoff = (now or datetime.now(UTC)) - timedelta(hours=max_age_hours)
        if posting.posted_at < cutoff:
            return False
    return True


@retry(
    retry=retry_if_exception_type(
        (httpx.TransportError, httpx.TimeoutException, BoardTransientError)
    ),
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=8),
    reraise=True,
)
async def _get(client: httpx.AsyncClient, url: str) -> httpx.Response:
    response = await client.get(url)
    if response.status_code in {429, 500, 502, 503, 504}:
        raise BoardTransientError(f"HTTP {response.status_code}")
    return response


async def fetch_board(
    client: httpx.AsyncClient,
    board: AtsBoard,
    *,
    max_age_hours: int | None,
    now: datetime | None = None,
) -> tuple[list[RawPosting], int, str]:
    """Return (kept postings, rows seen, status). Status is ok, not_found or failed."""
    try:
        response = await _get(client, board_url(board))
    except Exception as exc:
        log.warning("ats_board_failed", board=board.name, error=redact_error(str(exc)))
        return [], 0, "failed"
    if response.status_code == 404:
        return [], 0, "not_found"
    if response.status_code >= 400:
        log.warning("ats_board_failed", board=board.name, status=response.status_code)
        return [], 0, "failed"
    try:
        data = response.json()
    except ValueError:
        log.warning("ats_board_failed", board=board.name, reason="not_json")
        return [], 0, "failed"
    rows = parse_board(board, data)
    kept = [row for row in rows if keep_posting(row, max_age_hours=max_age_hours, now=now)]
    return kept, len(rows), "ok"


async def fetch_all_boards(
    boards: list[AtsBoard],
    *,
    max_age_hours: int | None = None,
    client: httpx.AsyncClient | None = None,
) -> BoardRun:
    """Read every board. One bad board never stops the others."""
    run = BoardRun()
    gate = asyncio.Semaphore(_CONCURRENCY)
    owns_client = client is None
    http = client or httpx.AsyncClient(
        timeout=httpx.Timeout(30.0, connect=10.0), headers=_HEADERS, follow_redirects=True
    )

    async def _one(board: AtsBoard) -> None:
        async with gate:
            kept, seen, status = await fetch_board(http, board, max_age_hours=max_age_hours)
        run.seen += seen
        run.kept += len(kept)
        run.postings.extend(kept)
        if status == "not_found":
            run.not_found.append(board.name)
        elif status == "failed":
            run.failed.append(board.name)

    try:
        await asyncio.gather(*(_one(board) for board in boards))
    finally:
        if owns_client:
            await http.aclose()
    log.info(
        "ats_boards_complete",
        boards=len(boards),
        seen=run.seen,
        kept=run.kept,
        not_found=run.not_found,
        failed=run.failed,
    )
    return run
