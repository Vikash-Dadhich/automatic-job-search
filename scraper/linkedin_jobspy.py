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
from scraper.discovery import DiscoveryPlan, PlannedSearch
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
    search: PlannedSearch | None = None,
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
                discovery_family=search.family_id if search else None,
                discovery_bucket=search.bucket_id if search else None,
                discovery_query=search.query if search else None,
            )
        )
    return out


def _google_search_term(_search: SearchConfig, term: str) -> str:
    """Google Jobs needs a natural-language query; bare keywords return little.

    Location is passed separately via ``scrape_jobs(location=...)``. Embedding
    a country like "United States" in the query is rejected by Google Jobs.
    """
    return f"{term} internship"


def _effective_windows(search: SearchConfig, sites: list[str] | None = None) -> dict[str, str]:
    """How each site actually applies ``hours_old`` (JobSpy does not honor it uniformly)."""
    configured = f"{search.hours_old}h"
    notes = {
        "linkedin": configured,
        "indeed": configured,
        "google": "hours_old ignored (no recency clause in the Google query)",
        "zip_recruiter": "hours_old rounded up to the next full day",
    }
    chosen = search.sites if sites is None else sites
    return {site: notes.get(site, configured) for site in chosen}


def _scrape_term(search: SearchConfig, term: str, sites: list[str]) -> Any:
    from jobspy import scrape_jobs

    kwargs: dict[str, Any] = dict(
        site_name=list(sites),
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
    if "google" in sites:
        kwargs["google_search_term"] = _google_search_term(search, term)
    try:
        return scrape_jobs(**kwargs)
    except TypeError as exc:
        # Older JobSpy builds reject google_search_term. Retrying without it
        # keeps LinkedIn/Indeed/ZipRecruiter results for this term.
        if "google_search_term" not in kwargs or "google_search_term" not in str(exc):
            raise
        log.warning("jobspy_google_search_term_unsupported", error=str(exc))
        kwargs.pop("google_search_term", None)
        return scrape_jobs(**kwargs)


async def fetch_linkedin_indeed(
    targets: Targets,
    *,
    profile: Profile | None = None,
    plan: DiscoveryPlan | None = None,
) -> list[RawPosting]:
    """Fetch JobSpy postings for the discovery plan, once per selected query."""
    search = targets.search
    if plan is None:
        planned = tuple(
            PlannedSearch(family_id="", bucket_id="", query=term) for term in search.terms
        )
        sites = list(search.sites)
    else:
        planned = plan.searches
        sites = list(plan.jobspy_sites)
    all_postings: list[RawPosting] = []
    seen: set[tuple[str, str]] = set()

    log.warning(
        "jobspy_recency_windows",
        configured_hours_old=search.hours_old,
        effective=_effective_windows(search, sites),
    )

    for item in planned:
        log.info(
            "jobspy_scrape_start",
            term=item.query,
            family=item.family_id or None,
            bucket=item.bucket_id or None,
            sites=sites,
        )
        try:
            df = await asyncio.to_thread(_scrape_term, search, item.query, sites)
        except Exception as exc:
            log.warning("jobspy_scrape_failed", term=item.query, error=str(exc))
            continue

        batch = _dataframe_to_postings(df, profile=profile, search=item)
        for posting in batch:
            key = (posting.source.value, posting.external_id)
            if key in seen:
                continue
            seen.add(key)
            all_postings.append(posting)
        log.info("jobspy_scrape_done", term=item.query, count=len(batch))

    log.info("jobspy_total", count=len(all_postings))
    return all_postings
