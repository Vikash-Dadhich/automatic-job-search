"""Read the public Simplify Summer 2027 internship list (a README with HTML tables).

The list has no job descriptions, so it is used to find companies. An apply link on
a Greenhouse, Lever or Ashby board gives us that company's board token, and the board
reader then pulls every open internship with its full description.
"""

from __future__ import annotations

import html
import re
from dataclasses import dataclass
from urllib.parse import urlparse

import httpx
import structlog

from config.targets import AtsBoard

log = structlog.get_logger(__name__)

README_URL = "https://raw.githubusercontent.com/SimplifyJobs/Summer2027-Internships/dev/README.md"
_PRODUCT_SECTION = re.compile(r"product management", re.IGNORECASE)
_ROW = re.compile(r"<tr[^>]*>(.*?)</tr>", re.IGNORECASE | re.DOTALL)
_CELL = re.compile(r"<td[^>]*>(.*?)</td>", re.IGNORECASE | re.DOTALL)
_HREF = re.compile(r'href="([^"]+)"', re.IGNORECASE)
_TAG = re.compile(r"<[^>]+>")
_BREAK = re.compile(r"<br\s*/?>", re.IGNORECASE)
_SAME_COMPANY = "↳"
_MARKERS = "🔥🎓🛂🇺🇸🔒"

_GREENHOUSE_HOSTS = {"boards.greenhouse.io", "job-boards.greenhouse.io"}


@dataclass(frozen=True, slots=True)
class SimplifyRow:
    section: str
    company: str
    role: str
    location: str
    url: str
    closed: bool = False
    no_sponsorship: bool = False
    citizens_only: bool = False


def _plain(fragment: str, *, joiner: str = " ") -> str:
    text = _BREAK.sub(joiner, fragment)
    text = html.unescape(_TAG.sub("", text))
    return re.sub(r"\s+", " ", text).strip()


def _clean_marked(text: str) -> str:
    for marker in _MARKERS:
        text = text.replace(marker, "")
    return re.sub(r"\s+", " ", text).strip()


def _apply_url(cell: str) -> str | None:
    for href in _HREF.findall(cell):
        host = (urlparse(html.unescape(href)).hostname or "").lower()
        if host and "simplify.jobs" not in host:
            return html.unescape(href)
    return None


def parse_simplify_readme(text: str, *, only_product: bool = True) -> list[SimplifyRow]:
    """Rows from each category table. Unknown markup gives fewer rows, never an error."""
    rows: list[SimplifyRow] = []
    for block in re.split(r"(?m)^##\s+", text)[1:]:
        heading, _, body = block.partition("\n")
        if only_product and not _PRODUCT_SECTION.search(heading):
            continue
        section = _clean_marked(_plain(heading))
        company = ""
        for row_html in _ROW.findall(body):
            cells = _CELL.findall(row_html)
            if len(cells) < 4:
                continue
            raw_company = _plain(cells[0])
            if raw_company and _SAME_COMPANY not in raw_company:
                company = _clean_marked(raw_company)
            role_raw = _plain(cells[1])
            url = _apply_url(cells[3])
            if not company or not role_raw or not url:
                continue
            flags = role_raw + _plain(cells[3]) + raw_company
            rows.append(
                SimplifyRow(
                    section=section,
                    company=company,
                    role=_clean_marked(role_raw),
                    location=_clean_marked(_plain(cells[2], joiner="; ")),
                    url=url,
                    closed="🔒" in flags,
                    no_sponsorship="🛂" in flags,
                    citizens_only="🇺🇸" in flags,
                )
            )
    return rows


def board_from_url(url: str, company: str) -> AtsBoard | None:
    """Board for a Greenhouse, Lever or Ashby job link. Other links give None."""
    parsed = urlparse(url)
    host = (parsed.hostname or "").lower()
    parts = [part for part in parsed.path.split("/") if part]
    if not parts:
        return None
    if host in _GREENHOUSE_HOSTS:
        provider = "greenhouse"
    elif host == "jobs.lever.co":
        provider = "lever"
    elif host == "jobs.ashbyhq.com":
        provider = "ashby"
    else:
        return None
    token = parts[0]
    if not re.fullmatch(r"[A-Za-z0-9_.-]+", token):
        return None
    return AtsBoard(name=company, provider=provider, token=token)


def discover_boards(
    rows: list[SimplifyRow],
    known: set[tuple[str, str]],
    *,
    limit: int = 150,
) -> list[AtsBoard]:
    """New boards from open rows, one per company, skipping boards we already read."""
    found: list[AtsBoard] = []
    seen = set(known)
    for row in rows:
        if row.closed:
            continue
        board = board_from_url(row.url, row.company)
        if board is None:
            continue
        key = (board.provider, board.token.lower())
        if key in seen:
            continue
        seen.add(key)
        found.append(board)
        if len(found) >= limit:
            break
    return found


async def fetch_simplify_rows(
    client: httpx.AsyncClient | None = None,
    *,
    url: str = README_URL,
) -> list[SimplifyRow]:
    owns = client is None
    http = client or httpx.AsyncClient(timeout=httpx.Timeout(30.0, connect=10.0))
    try:
        response = await http.get(url)
        if response.status_code != 200:
            log.warning("simplify_list_unavailable", status=response.status_code)
            return []
        rows = parse_simplify_readme(response.text)
        log.info("simplify_list_read", rows=len(rows))
        return rows
    except httpx.HTTPError as exc:
        log.warning("simplify_list_failed", error=str(exc)[:200])
        return []
    finally:
        if owns:
            await http.aclose()
