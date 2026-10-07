"""LinkedIn / Indeed discovery via python-jobspy (async wrapper).

Each query runs in a child process. The parent kills that process group when
``jobspy_query_timeout_seconds`` elapses. A thread timeout is not used: cancelling
the await would leave JobSpy's blocking HTTP calls running.
"""

from __future__ import annotations

import asyncio
import hashlib
import math
from collections.abc import Awaitable, Callable
from datetime import UTC, datetime
from typing import Any

import structlog

from config.profile import Profile
from config.settings import get_settings
from config.targets import SearchConfig, Targets
from core.db import Source
from scraper.coverage import SearchObservation, observe_search, result_identity
from scraper.discovery import DiscoveryPlan, PlannedSearch
from scraper.filters import location_acceptable
from scraper.jobspy_process import LineWorker, QueryTimeoutError, worker_argv
from scraper.models import RawPosting
from scraper.redact import redact_error

QueryExecutor = Callable[..., Awaitable[list[dict[str, Any]]]]
OnBatch = Callable[[list[RawPosting]], Awaitable[bool | None]]

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


def _explicit_company_url(row: dict[str, Any]) -> str | None:
    """Employer site already on the source row. The job posting URL is not used."""
    raw = _row_value(row, "company_url", "company_url_direct")
    if raw is None:
        return None
    text = str(raw).strip()
    if not text or text.lower() == "nan":
        return None
    return text


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
) -> tuple[list[RawPosting], dict[str, dict[str, int]]]:
    if df is None or getattr(df, "empty", True):
        return [], {}

    records = df.to_dict(orient="records")
    seen: set[tuple[str, str]] = set()
    out: list[RawPosting] = []
    stats: dict[str, dict[str, int]] = {}

    def _bucket(name: str) -> dict[str, int]:
        row = stats.get(name)
        if row is None:
            row = {"fetched": 0, "location_dropped": 0}
            stats[name] = row
        return row

    for row in records:
        site_raw = str(_row_value(row, "site", default="") or "").lower().strip()
        source = _SITE_MAP.get(site_raw)
        if source is None:
            unidentified = stats.setdefault("unidentified", {"count": 0})
            unidentified["count"] += 1
            continue
        bucket = _bucket(source.value)
        bucket["fetched"] += 1

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
            bucket["location_dropped"] += 1
            continue

        description = _row_value(row, "description")
        company_url = _explicit_company_url(row)
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
                company_url=company_url,
            )
        )
    return out, stats


def google_executed_query(term: str) -> str:
    """Text sent to Google Jobs. This does not apply ``hours_old``."""
    return f"{term} internship"


def _google_search_term(_search: SearchConfig, term: str) -> str:
    """Google Jobs needs a natural-language query; bare keywords return little.

    Location is passed separately via ``scrape_jobs(location=...)``. Embedding
    a country like "United States" in the query is rejected by Google Jobs.
    """
    return google_executed_query(term)


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
        log.warning("jobspy_google_search_term_unsupported", error=redact_error(str(exc)))
        kwargs.pop("google_search_term", None)
        return scrape_jobs(**kwargs)


def possible_result_cap(returned: int, limit: int | None) -> bool:
    """True when a source filled its configured cap. Not proof that rows were missed."""
    return bool(limit) and returned >= limit


def _jobspy_observations(
    item: PlannedSearch,
    sites: list[str],
    batch: list[RawPosting],
    *,
    error: str | None = None,
    stats: dict[str, dict[str, int]] | None = None,
    results_wanted: int | None = None,
) -> list[SearchObservation]:
    by_site: dict[str, list[RawPosting]] = {site: [] for site in sites}
    for posting in batch:
        by_site.setdefault(posting.source.value, []).append(posting)
    unidentified = int((stats or {}).get("unidentified", {}).get("count", 0))
    ambiguous = unidentified > 0 and error is None
    notes: list[SearchObservation] = []
    extras = [site for site in by_site if site not in sites and site != "unidentified"]
    ordered = list(sites) + extras
    for site in ordered:
        rows = by_site.get(site, [])
        hits = tuple(
            result_identity(row.source.value, row.external_id) for row in rows
        )
        site_stats = (stats or {}).get(site, {})
        fetched = site_stats.get("fetched", 0 if error else len(rows))
        site_error = error
        if ambiguous and not site_error:
            site_error = "jobspy rows had no recognized site and were not attributed"
        notes.append(
            observe_search(
                family_id=item.family_id,
                bucket_id=item.bucket_id,
                query=item.query,
                source=site,
                hits=() if error else hits,
                error=site_error,
                failed=error is not None,
                fetched_count=fetched,
                location_dropped=site_stats.get("location_dropped", 0),
                possible_cap=possible_result_cap(fetched, results_wanted),
                ambiguous=ambiguous,
            )
        )
    if ambiguous:
        notes.append(
            observe_search(
                family_id=item.family_id,
                bucket_id=item.bucket_id,
                query=item.query,
                source="unidentified",
                hits=(None,) * unidentified,
                error="jobspy rows had no recognized site and were not attributed",
                ambiguous=True,
            )
        )
    return notes


class _RecordFrame:
    """Just enough of a DataFrame for ``_dataframe_to_postings``."""

    def __init__(self, records: list[dict[str, Any]]) -> None:
        self._records = records
        self.empty = not records

    def to_dict(self, orient: str = "records") -> list[dict[str, Any]]:
        del orient
        return self._records


def _query_payload(search: SearchConfig, term: str, sites: list[str]) -> dict[str, Any]:
    return {
        "term": term,
        "sites": sites,
        "search": {
            "terms": [term],
            "sites": sites,
            "location": search.location,
            "distance": search.distance,
            "results_wanted": search.results_wanted,
            "country_indeed": search.country_indeed,
            "hours_old": search.hours_old,
            "linkedin_fetch_description": search.linkedin_fetch_description,
        },
    }


async def _records_from_worker(
    worker: LineWorker,
    search: SearchConfig,
    term: str,
    sites: list[str],
    timeout: float,
) -> list[dict[str, Any]]:
    message = await worker.request(_query_payload(search, term, sites), timeout)
    if not message.get("ok", False):
        raise RuntimeError(str(message.get("error") or "jobspy worker failed"))
    records = message.get("records")
    if not isinstance(records, list):
        raise RuntimeError("jobspy worker returned no record list")
    return [row for row in records if isinstance(row, dict)]


async def fetch_linkedin_indeed(
    targets: Targets,
    *,
    profile: Profile | None = None,
    plan: DiscoveryPlan | None = None,
    observations: list[SearchObservation] | None = None,
    on_batch: OnBatch | None = None,
    query_executor: QueryExecutor | None = None,
    timeout: float | None = None,
    command: list[str] | None = None,
) -> list[RawPosting]:
    """Fetch JobSpy postings for the discovery plan, once per selected query.

    A failed or timed-out query is recorded as failed and the loop continues.
    When ``on_batch`` is set, each query's new postings are handed off immediately
    and this function does not keep them. Callers that need the full list omit
    ``on_batch``.
    """
    search = targets.search
    if plan is None:
        planned = tuple(
            PlannedSearch(family_id="", bucket_id="", query=term) for term in search.terms
        )
        sites = list(search.sites)
    else:
        planned = plan.searches
        sites = list(plan.jobspy_sites)
    limit = (
        float(timeout)
        if timeout is not None
        else float(get_settings().jobspy_query_timeout_seconds)
    )
    all_postings: list[RawPosting] = []
    seen: set[tuple[str, str]] = set()
    worker: LineWorker | None = None
    if query_executor is None:
        worker = LineWorker(command or worker_argv())

    async def run_query(term: str) -> list[dict[str, Any]]:
        if query_executor is not None:
            return await query_executor(search, term, sites, limit)
        if worker is None:
            raise RuntimeError("jobspy worker is not running")
        return await _records_from_worker(worker, search, term, sites, limit)

    log.warning(
        "jobspy_recency_windows",
        configured_hours_old=search.hours_old,
        effective=_effective_windows(search, sites),
    )

    try:
        for item in planned:
            log.info(
                "jobspy_scrape_start",
                term=item.query,
                family=item.family_id or None,
                bucket=item.bucket_id or None,
                sites=sites,
            )
            try:
                records = await run_query(item.query)
            except asyncio.CancelledError:
                raise
            except QueryTimeoutError as exc:
                log.warning("jobspy_scrape_timeout", term=item.query, error=str(exc))
                if observations is not None:
                    observations.extend(
                        _jobspy_observations(item, sites, [], error=str(exc))
                    )
                continue
            except Exception as exc:
                safe = redact_error(str(exc))
                log.warning("jobspy_scrape_failed", term=item.query, error=safe)
                if observations is not None:
                    observations.extend(
                        _jobspy_observations(item, sites, [], error=safe)
                    )
                continue

            batch, stats = _dataframe_to_postings(
                _RecordFrame(records),
                profile=profile,
                search=item,
            )
            if observations is not None:
                observations.extend(
                    _jobspy_observations(
                        item,
                        sites,
                        batch,
                        stats=stats,
                        results_wanted=search.results_wanted,
                    )
                )
            fresh: list[RawPosting] = []
            fresh_keys: set[tuple[str, str]] = set()
            for posting in batch:
                key = (posting.source.value, posting.external_id)
                if key in seen or key in fresh_keys:
                    continue
                fresh_keys.add(key)
                fresh.append(posting)
            # Remember an id only after the caller accepts it. A failed commit
            # returns False so a later query can try that posting again.
            accepted = True
            if on_batch is not None:
                accepted = (await on_batch(fresh)) is not False
            else:
                all_postings.extend(fresh)
            if accepted:
                seen.update(fresh_keys)
            log.info("jobspy_scrape_done", term=item.query, count=len(batch))
    finally:
        if worker is not None:
            await worker.close()

    log.info("jobspy_total", count=len(all_postings))
    return all_postings
