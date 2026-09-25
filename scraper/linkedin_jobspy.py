"""LinkedIn / Indeed discovery via python-jobspy (async wrapper)."""

from __future__ import annotations

import asyncio
import hashlib
import math
from datetime import UTC, datetime
from typing import Any

import structlog

from config.profile import Profile
from config.targets import SearchConfig, Targets
from core.db import Source
from scraper.filters import location_acceptable
from scraper.models import RawPosting

log = structlog.get_logger(__name__)

_SITE_MAP: dict[str, Source] = {
    "linkedin": Source.linkedin,
    "indeed": Source.indeed,
    "google": Source.google,
    "zip_recruiter": Source.zip_recruiter,
}


def _row_value(row: dict[str, Any], *keys: str, default: Any = None) -> Any:
    for key in keys:
        if key in row and row[key] is not None:
            val = row[key]
            if isinstance(val, float) and math.isnan(val):
                continue
            return val
    return default


def _parse_posted_at(value: Any) -> datetime | None:
    if value is None:
        return None
    if isinstance(value, datetime):
        return value if value.tzinfo else value.replace(tzinfo=UTC)
    text = str(value).strip()
    if not text or text.lower() == "nan":
        return None
    for fmt in ("%Y-%m-%d", "%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S"):
        try:
            dt = datetime.strptime(text[:19], fmt)
            return dt.replace(tzinfo=UTC)
        except ValueError:
            continue
    try:
        # date-only from pandas Timestamp string
        return datetime.fromisoformat(text.replace("Z", "+00:00"))
    except ValueError:
        return None


def _external_id(row: dict[str, Any], source: Source, url: str) -> str:
    raw_id = _row_value(row, "id", "job_id")
    if raw_id is not None and str(raw_id).strip() and str(raw_id).lower() != "nan":
        return str(raw_id).strip()
    digest = hashlib.sha256(url.encode()).hexdigest()[:24]
    return f"{source.value}:{digest}"


def _location_matches(location: str | None, profile: Profile | None) -> bool:
    """Client-side location/remote filter (JobSpy drops is_remote when hours_old set).

    Delegates to the ingest rule so scraping does not keep postings the
    pre-filter will reject moments later.
    """
    if profile is None:
        return True
    return location_acceptable(location, profile)


def _dataframe_to_postings(
    df: Any,
    *,
    profile: Profile | None,
) -> list[RawPosting]:
    if df is None or getattr(df, "empty", True):
        return []

    records = df.to_dict(orient="records")
    seen: set[tuple[str, str]] = set()
    out: list[RawPosting] = []

    for row in records:
        site_raw = str(_row_value(row, "site", default="") or "").lower().strip()
        source = _SITE_MAP.get(site_raw)
        if source is None:
            continue

        title = str(_row_value(row, "title", default="") or "").strip()
        company = str(_row_value(row, "company", default="") or "").strip()
        url = str(
            _row_value(row, "job_url_direct", "job_url", "url", default="") or ""
        ).strip()
        if not title or not company or not url:
            continue

        location = _row_value(row, "location")
        location_s = str(location).strip() if location is not None else None
        if location_s and location_s.lower() == "nan":
            location_s = None

        if not _location_matches(location_s, profile):
            continue

        description = _row_value(row, "description")
        description_s = str(description).strip() if description is not None else None
        if description_s and description_s.lower() == "nan":
            description_s = None

        ext_id = _external_id(row, source, url)
        key = (source.value, ext_id)
        if key in seen:
            continue
        seen.add(key)

        out.append(
            RawPosting(
                source=source,
                external_id=ext_id,
                title=title,
                company=company,
                location=location_s,
                url=url,
                description_clean=description_s,
                posted_at=_parse_posted_at(_row_value(row, "date_posted", "date")),
            )
        )
    return out


def _google_search_term(search: SearchConfig, term: str) -> str:
    """Google Jobs needs a natural-language query; bare keywords return little.

    'since yesterday' is how Google encodes recency (the scraper has no
    hours_old for google), which pairs with our 36h window + upsert dedupe.
    """
    return f"{term} jobs near {search.location} since yesterday"


def _scrape_term(search: SearchConfig, term: str) -> Any:
    from jobspy import scrape_jobs

    kwargs: dict[str, Any] = dict(
        site_name=list(search.sites),
        search_term=term,
        location=search.location,
        distance=search.distance,
        results_wanted=search.results_wanted,
        hours_old=search.hours_old,
        country_indeed=search.country_indeed,
        description_format="markdown",
        linkedin_fetch_description=search.linkedin_fetch_description,
        verbose=0,
    )
    if "google" in search.sites:
        kwargs["google_search_term"] = _google_search_term(search, term)
    return scrape_jobs(**kwargs)


async def fetch_linkedin_indeed(
    targets: Targets,
    *,
    profile: Profile | None = None,
) -> list[RawPosting]:
    """Fetch LinkedIn/Indeed postings for all configured search terms."""
    search = targets.search
    all_postings: list[RawPosting] = []
    seen: set[tuple[str, str]] = set()

    for term in search.terms:
        log.info("jobspy_scrape_start", term=term, sites=search.sites)
        try:
            df = await asyncio.to_thread(_scrape_term, search, term)
        except Exception as exc:
            log.warning("jobspy_scrape_failed", term=term, error=str(exc))
            continue

        batch = _dataframe_to_postings(df, profile=profile)
        for posting in batch:
            key = (posting.source.value, posting.external_id)
            if key in seen:
                continue
            seen.add(key)
            all_postings.append(posting)
        log.info("jobspy_scrape_done", term=term, count=len(batch))

    log.info("jobspy_total", count=len(all_postings))
    return all_postings
