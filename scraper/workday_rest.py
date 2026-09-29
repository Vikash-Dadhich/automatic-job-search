"""Workday CXS REST client for public career portals (async httpx)."""

from __future__ import annotations

import asyncio
import re
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

from config.targets import WorkdayParts, WorkdayTenant
from core.db import Source
from scraper.models import RawPosting

log = structlog.get_logger(__name__)

_PAGE_LIMIT = 20
_DEFAULT_HEADERS = {
    "Accept": "application/json",
    "Content-Type": "application/json",
    "Accept-Language": "en-US",
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
    ),
}


class WorkdayBlockedError(Exception):
    """Raised when a tenant returns 403 / challenge / Akamai block."""


class WorkdayTransientError(WorkdayBlockedError):
    """Rate limit or temporary unavailability — retried before giving up.

    Subclasses WorkdayBlockedError so exhausted retries still fall back to the
    existing soft-fail handling instead of crashing a run.
    """


def _is_recent_posted_on(posted_on: str | None, *, max_hours: int = 24) -> bool:
    """Interpret Workday's relative postedOn strings for ~24h shortlisting."""
    if not posted_on:
        return True  # unknown → keep and let startDate decide later
    text = posted_on.strip().lower()
    if "today" in text or "hour" in text or "minute" in text or "just posted" in text:
        return True
    if "yesterday" in text:
        return max_hours >= 24
    match = re.search(r"(\d+)\s+days?\s+ago", text)
    if match:
        days = int(match.group(1))
        return days * 24 <= max_hours
    # "Posted 30+ Days Ago" etc.
    if "day" in text or "week" in text or "month" in text:
        return False
    return True


def _parse_start_date(value: str | None) -> datetime | None:
    if not value:
        return None
    text = value.strip()
    for fmt in ("%Y-%m-%d", "%Y-%m-%dT%H:%M:%S.%f%z", "%Y-%m-%dT%H:%M:%S%z"):
        try:
            dt = datetime.strptime(text, fmt)
            return dt if dt.tzinfo else dt.replace(tzinfo=UTC)
        except ValueError:
            continue
    try:
        return datetime.fromisoformat(text.replace("Z", "+00:00"))
    except ValueError:
        return None


def _within_hours(dt: datetime | None, *, max_hours: int) -> bool:
    if dt is None:
        return True
    now = datetime.now(UTC)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=UTC)
    return dt >= now - timedelta(hours=max_hours)


@retry(
    retry=retry_if_exception_type(
        (httpx.TransportError, httpx.TimeoutException, WorkdayTransientError)
    ),
    stop=stop_after_attempt(4),
    wait=wait_exponential(multiplier=1, min=2, max=15),
    reraise=True,
)
async def _request(
    client: httpx.AsyncClient,
    method: str,
    url: str,
    **kwargs: Any,
) -> httpx.Response:
    response = await client.request(method, url, **kwargs)
    if response.status_code in {429, 502, 503, 504}:
        raise WorkdayTransientError(f"{method} {url} -> HTTP {response.status_code}")
    if response.status_code == 403:
        raise WorkdayBlockedError(f"{method} {url} -> HTTP {response.status_code}")
    # Akamai / challenge HTML disguised as 200 (listing POST or detail GET)
    content_type = response.headers.get("content-type", "")
    if "json" not in content_type:
        body_l = response.text[:500].lower()
        if "akamai" in body_l or "challenge" in body_l or "access denied" in body_l:
            raise WorkdayBlockedError(f"Bot challenge on {url}")
    response.raise_for_status()
    return response


def _parse_json(response: httpx.Response, *, url: str) -> dict[str, Any]:
    """Decode JSON or raise WorkdayBlockedError on HTML/challenge bodies."""
    try:
        data = response.json()
    except ValueError as exc:
        raise WorkdayBlockedError(f"Non-JSON response from {url}") from exc
    if not isinstance(data, dict):
        raise WorkdayBlockedError(f"Unexpected JSON shape from {url}")
    return data


def _as_text(value: Any) -> str | None:
    """Coerce Workday location/company fields (str | dict | None) to plain text."""
    if value is None:
        return None
    if isinstance(value, str):
        text = value.strip()
        return text or None
    if isinstance(value, dict):
        descriptor = value.get("descriptor") or value.get("name")
        if descriptor is not None:
            return str(descriptor).strip() or None
    return str(value).strip() or None


async def _fetch_listing_page(
    client: httpx.AsyncClient,
    parts: WorkdayParts,
    *,
    search_text: str,
    offset: int,
) -> dict[str, Any]:
    url = f"{parts.base_cxs}/jobs"
    payload = {
        "appliedFacets": {},
        "limit": _PAGE_LIMIT,
        "offset": offset,
        "searchText": search_text or "",
    }
    headers = {
        **_DEFAULT_HEADERS,
        "Referer": f"{parts.public_base}",
    }
    response = await _request(client, "POST", url, json=payload, headers=headers)
    return _parse_json(response, url=url)


async def _fetch_detail(
    client: httpx.AsyncClient,
    parts: WorkdayParts,
    external_path: str,
    sem: asyncio.Semaphore,
) -> dict[str, Any] | None:
    path = external_path if external_path.startswith("/") else f"/{external_path}"
    url = f"https://{parts.host}/wday/cxs/{parts.tenant}/{parts.site}{path}"
    headers = {
        **_DEFAULT_HEADERS,
        "Referer": f"{parts.public_base}{path}",
    }
    async with sem:
        await asyncio.sleep(0.15)
        try:
            response = await _request(client, "GET", url, headers=headers)
        except WorkdayBlockedError:
            raise
        except httpx.HTTPStatusError as exc:
            log.warning(
                "workday_detail_http_error",
                path=external_path,
                status=exc.response.status_code,
            )
            return None
        try:
            data = _parse_json(response, url=url)
        except WorkdayBlockedError:
            log.warning("workday_detail_non_json", path=external_path)
            return None
        info = data.get("jobPostingInfo") or data
        return info if isinstance(info, dict) else None


def _company_name(tenant: WorkdayTenant, info: dict[str, Any] | None) -> str:
    if info:
        for key in ("company", "hiringOrganization"):
            text = _as_text(info.get(key))
            if text:
                return text
    return tenant.name


async def fetch_workday(
    tenant: WorkdayTenant,
    *,
    search_terms: list[str] | None = None,
    hours_old: int = 24,
    max_pages: int = 25,
    provenance: dict[str, tuple[str, str]] | None = None,
) -> list[RawPosting]:
    """Fetch recent postings from a single Workday tenant."""
    if tenant.is_placeholder:
        log.info("workday_skip_placeholder", name=tenant.name)
        return []

    try:
        parts = tenant.parsed()
    except ValueError as exc:
        log.warning("workday_bad_url", name=tenant.name, error=str(exc))
        return []

    terms = search_terms or tenant.search_terms or [""]
    # Deduplicate empty + real terms: run once with "" if no specific terms
    cleaned_terms = [t.strip() for t in terms if t and t.strip()]
    if not cleaned_terms:
        cleaned_terms = [""]

    postings: list[RawPosting] = []
    seen_ids: set[str] = set()
    sem = asyncio.Semaphore(4)
    # A block on one search term is often transient; only a repeated block means
    # the tenant is genuinely shutting us out.
    blocks = 0
    max_blocks = 2

    timeout = httpx.Timeout(30.0, connect=10.0)
    try:
        async with httpx.AsyncClient(timeout=timeout, follow_redirects=True) as client:
            for term in cleaned_terms:
                if blocks >= max_blocks:
                    break
                offset = 0
                pages = 0
                while pages < max_pages:
                    try:
                        data = await _fetch_listing_page(
                            client, parts, search_text=term, offset=offset
                        )
                    except WorkdayBlockedError as exc:
                        blocks += 1
                        log.warning(
                            "workday_blocked",
                            tenant=parts.tenant,
                            term=term,
                            blocks=blocks,
                            error=str(exc),
                        )
                        break
                    except (httpx.HTTPError, ValueError) as exc:
                        log.warning(
                            "workday_list_error",
                            tenant=parts.tenant,
                            error=str(exc),
                        )
                        break

                    batch = data.get("jobPostings") or []
                    total = int(data.get("total") or 0)
                    if not batch:
                        break

                    recent = [
                        item
                        for item in batch
                        if _is_recent_posted_on(item.get("postedOn"), max_hours=hours_old)
                    ]

                    # Pair each item with its own task: filtering the task list while
                    # zipping against `recent` shifted details onto the wrong jobs.
                    fetchable = [item for item in recent if item.get("externalPath")]
                    details = await asyncio.gather(
                        *(
                            _fetch_detail(client, parts, item["externalPath"], sem)
                            for item in fetchable
                        ),
                        return_exceptions=True,
                    )

                    detail_blocked = False
                    for item, detail_result in zip(fetchable, details, strict=True):
                        if isinstance(detail_result, WorkdayBlockedError):
                            if not detail_blocked:
                                detail_blocked = True
                                blocks += 1
                                log.warning(
                                    "workday_blocked",
                                    tenant=parts.tenant,
                                    term=term,
                                    blocks=blocks,
                                    error=str(detail_result),
                                )
                            continue
                        if isinstance(detail_result, BaseException):
                            log.warning(
                                "workday_detail_error",
                                path=item.get("externalPath"),
                                error=str(detail_result),
                            )
                            continue

                        info: dict[str, Any] = detail_result or {}
                        start = _parse_start_date(info.get("startDate"))
                        if not _within_hours(start, max_hours=hours_old):
                            # postedOn said recent but startDate is older
                            if start is not None:
                                continue

                        job_req = (
                            info.get("jobReqId")
                            or info.get("id")
                            or item.get("bulletFields", [None])[0]
                            or item.get("externalPath", "").rstrip("/").split("/")[-1]
                        )
                        if not job_req:
                            continue
                        external_id = f"{parts.tenant}:{job_req}"
                        if external_id in seen_ids:
                            continue
                        seen_ids.add(external_id)

                        external_path = item.get("externalPath") or ""
                        public_url = f"{parts.public_base}{external_path}"
                        title = (
                            info.get("title")
                            or item.get("title")
                            or "Untitled"
                        )
                        title = str(title).strip() or "Untitled"
                        location = _as_text(
                            info.get("location") or item.get("locationsText")
                        )
                        description_html = info.get("jobDescription")
                        if description_html is not None and not isinstance(
                            description_html, str
                        ):
                            description_html = str(description_html)

                        family_id = None
                        bucket_id = None
                        if provenance and term in provenance:
                            family_id, bucket_id = provenance[term]
                        postings.append(
                            RawPosting(
                                source=Source.workday,
                                external_id=external_id,
                                title=title,
                                company=_company_name(tenant, info),
                                location=location,
                                url=public_url,
                                description_html=description_html,
                                posted_at=start,
                                tenant=parts.tenant,
                                discovery_family=family_id,
                                discovery_bucket=bucket_id,
                                discovery_query=term or None,
                            )
                        )
                    if detail_blocked and blocks >= max_blocks:
                        break
                    offset += _PAGE_LIMIT
                    pages += 1
                    if offset >= total:
                        break
                    await asyncio.sleep(0.25)
    except WorkdayBlockedError as exc:
        log.warning("workday_blocked", tenant=parts.tenant, error=str(exc))
        return postings

    log.info(
        "workday_fetch_done",
        tenant=parts.tenant,
        site=parts.site,
        count=len(postings),
    )
    return postings


async def fetch_all_workday(
    tenants: list[WorkdayTenant],
    *,
    default_search_terms: list[str] | None = None,
    hours_old: int = 24,
    provenance: dict[str, tuple[str, str]] | None = None,
) -> list[RawPosting]:
    """Fetch from many tenants concurrently; failures are isolated."""
    if not tenants:
        return []

    async def _one(tenant: WorkdayTenant) -> list[RawPosting]:
        terms = tenant.search_terms or default_search_terms
        try:
            return await fetch_workday(
                tenant,
                search_terms=terms,
                hours_old=hours_old,
                provenance=provenance,
            )
        except Exception as exc:
            log.warning("workday_tenant_failed", name=tenant.name, error=str(exc))
            return []

    results = await asyncio.gather(*[_one(t) for t in tenants])
    merged: list[RawPosting] = []
    seen: set[str] = set()
    for batch in results:
        for posting in batch:
            if posting.external_id in seen:
                continue
            seen.add(posting.external_id)
            merged.append(posting)
    return merged
