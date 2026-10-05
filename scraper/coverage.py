"""Discovery coverage diagnostics. These measure searches, not candidate fit.

Identity is source plus external id, the same key the database already uses.
The same posting on two boards stays two discoveries. This is not market recall.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, is_dataclass
from enum import StrEnum
from pathlib import Path
from typing import Any

import structlog

from config.settings import PROJECT_ROOT
from scraper.discovery import DiscoveryPlan
from scraper.redact import redact_error

log = structlog.get_logger(__name__)

_COVERAGE_PATH = PROJECT_ROOT / "storage" / "diagnostics" / "discovery_coverage.json"
IDENTITY_SCOPE = "source_and_external_id"


class SearchStatus(StrEnum):
    results = "results"
    empty = "empty"
    failed = "failed"
    not_executed = "not_executed"
    partial = "partial"


@dataclass(frozen=True, slots=True)
class SearchObservation:
    """One executed search on one source. Hits keep result order."""

    family_id: str
    bucket_id: str
    query: str
    source: str
    status: SearchStatus
    hits: tuple[str | None, ...] = ()
    error: str | None = None
    detail: str = ""
    fetched_count: int | None = None
    location_dropped: int | None = None
    recency_dropped: int | None = None
    possible_cap: bool = False
    ambiguous: bool = False

    @property
    def raw_count(self) -> int:
        return len(self.hits)

    @property
    def unidentified_count(self) -> int:
        return sum(1 for hit in self.hits if hit is None)

    @property
    def identities(self) -> tuple[str, ...]:
        return tuple(hit for hit in self.hits if hit is not None)


def result_identity(source: str, external_id: str | None) -> str | None:
    """Database identity. Blank ids are raw results we cannot count as unique."""
    text = (external_id or "").strip()
    source_name = source.strip()
    if not text or not source_name:
        return None
    return f"{source_name}:{text}"


def observe_search(
    *,
    family_id: str,
    bucket_id: str,
    query: str,
    source: str,
    hits: tuple[str | None, ...] = (),
    error: str | None = None,
    detail: str = "",
    failed: bool = False,
    skipped: bool = False,
    fetched_count: int | None = None,
    location_dropped: int | None = None,
    recency_dropped: int | None = None,
    possible_cap: bool = False,
    ambiguous: bool = False,
) -> SearchObservation:
    """Build an observation. Failure stays failure even when nothing came back.

    Hits plus an error are partial: the rows are kept and the error is kept.
    Partial is not an empty result. Ambiguous rows are partial too, including
    a scrape that returned nothing attributable.
    """
    if failed and hits:
        status = SearchStatus.partial
    elif failed:
        status = SearchStatus.failed
    elif skipped:
        status = SearchStatus.not_executed
    elif ambiguous:
        status = SearchStatus.partial
    elif hits:
        status = SearchStatus.results
    else:
        status = SearchStatus.empty
    safe_error = redact_error(error) if error else None
    return SearchObservation(
        family_id=family_id,
        bucket_id=bucket_id,
        query=query,
        source=source,
        status=status,
        hits=hits,
        error=safe_error,
        detail=detail,
        fetched_count=fetched_count,
        location_dropped=location_dropped,
        recency_dropped=recency_dropped,
        possible_cap=possible_cap,
        ambiguous=ambiguous,
    )


@dataclass(frozen=True, slots=True)
class GroupMetrics:
    name: str
    planned: int
    executed: int
    with_results: int
    zero_result: int
    failed: int
    raw: int
    unique: int
    incremental: int
    unidentified: int
    duplicate: int


@dataclass(frozen=True, slots=True)
class QueryMetrics:
    family_id: str
    bucket_id: str
    query: str
    source: str
    detail: str
    status: SearchStatus
    raw: int
    unique: int
    incremental: int
    unidentified: int
    duplicate: int
    error: str | None
    fetched_count: int | None = None
    location_dropped: int | None = None
    recency_dropped: int | None = None
    possible_cap: bool = False
    hits: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class CoverageReport:
    """Internal discovery coverage. Not a share of the internship market."""

    searches_planned: int
    searches_executed: int
    with_results: int
    zero_result: int
    failed: int
    not_executed: int
    raw: int
    unique: int
    duplicate: int
    unidentified: int
    duplicate_rate: float | None
    zero_result_rate: float | None
    searches_with_incremental: int
    families: tuple[GroupMetrics, ...]
    buckets: tuple[GroupMetrics, ...]
    sources: tuple[GroupMetrics, ...]
    queries: tuple[QueryMetrics, ...]
    identity_scope: str = IDENTITY_SCOPE

    def to_dict(self) -> dict[str, object]:
        payload = _jsonable(self)
        assert isinstance(payload, dict)
        return payload


def _jsonable(value: object) -> object:
    if isinstance(value, StrEnum):
        return value.value
    if isinstance(value, tuple):
        return [_jsonable(item) for item in value]
    if isinstance(value, list):
        return [_jsonable(item) for item in value]
    if is_dataclass(value) and not isinstance(value, type):
        return {
            key: _jsonable(getattr(value, key))
            for key in value.__dataclass_fields__
        }
    return value


@dataclass(frozen=True, slots=True)
class _Slot:
    family_id: str
    bucket_id: str
    query: str
    source: str
    detail: str


@dataclass
class _Tally:
    name: str
    planned: int = 0
    executed: int = 0
    with_results: int = 0
    zero_result: int = 0
    failed: int = 0
    raw: int = 0
    unidentified: int = 0
    incremental: int = 0
    identities: set[str] | None = None

    def __post_init__(self) -> None:
        if self.identities is None:
            self.identities = set()

    def finish(self) -> GroupMetrics:
        found = self.identities or set()
        identifiable = self.raw - self.unidentified
        return GroupMetrics(
            name=self.name,
            planned=self.planned,
            executed=self.executed,
            with_results=self.with_results,
            zero_result=self.zero_result,
            failed=self.failed,
            raw=self.raw,
            unique=len(found),
            incremental=self.incremental,
            unidentified=self.unidentified,
            duplicate=max(0, identifiable - len(found)),
        )


def _planned_slots(
    plan: DiscoveryPlan,
    workday_tenants: tuple[str, ...],
) -> list[_Slot]:
    slots: list[_Slot] = []
    tenants = workday_tenants if plan.workday_enabled else ()
    for search in plan.searches:
        for site in plan.jobspy_sites:
            slots.append(
                _Slot(search.family_id, search.bucket_id, search.query, site, "")
            )
        for tenant in tenants:
            slots.append(
                _Slot(
                    search.family_id,
                    search.bucket_id,
                    search.query,
                    "workday",
                    tenant,
                )
            )
    return slots


def _slot_key(query: str, source: str, detail: str) -> tuple[str, str, str]:
    return (query, source, detail)


def build_coverage_report(
    plan: DiscoveryPlan,
    observations: list[SearchObservation],
    *,
    workday_tenants: tuple[str, ...] = (),
) -> CoverageReport:
    """Aggregate a run. Incremental counts follow plan order, not finish order."""
    slots = _planned_slots(plan, workday_tenants)
    slot_index = {
        _slot_key(slot.query, slot.source, slot.detail): index
        for index, slot in enumerate(slots)
    }
    ranked = sorted(
        enumerate(observations),
        key=lambda pair: (
            slot_index.get(_slot_key(pair[1].query, pair[1].source, pair[1].detail), 10**9),
            pair[0],
        ),
    )
    unused: dict[tuple[str, str, str], list[SearchObservation]] = {}
    for _index, observation in ranked:
        unused.setdefault(
            _slot_key(observation.query, observation.source, observation.detail),
            [],
        ).append(observation)

    executed: list[SearchObservation] = []
    query_rows: list[tuple[_Slot | None, SearchObservation | None]] = []
    for slot in slots:
        queue = unused.get(_slot_key(slot.query, slot.source, slot.detail))
        if queue:
            observation = queue.pop(0)
            executed.append(observation)
            query_rows.append((slot, observation))
        else:
            query_rows.append((slot, None))
    leftovers: list[SearchObservation] = []
    for _index, observation in ranked:
        queue = unused.get(_slot_key(observation.query, observation.source, observation.detail))
        if queue and observation in queue:
            queue.remove(observation)
            leftovers.append(observation)
    for observation in leftovers:
        executed.append(observation)
        query_rows.append((None, observation))

    seen: set[str] = set()
    incremental_by_id: dict[int, int] = {}
    for observation in executed:
        fresh = 0
        local: set[str] = set()
        for identity in observation.identities:
            if identity in local:
                continue
            local.add(identity)
            if identity not in seen:
                seen.add(identity)
                fresh += 1
        incremental_by_id[id(observation)] = fresh

    families = {family.family_id: _Tally(family.family_id) for family in plan.families}
    buckets: dict[str, _Tally] = {}
    sources: dict[str, _Tally] = {}
    for site in plan.jobspy_sites:
        sources.setdefault(site, _Tally(site))
    if workday_tenants and plan.workday_enabled:
        sources.setdefault("workday", _Tally("workday"))

    def group_for(mapping: dict[str, _Tally], name: str) -> _Tally:
        tally = mapping.get(name)
        if tally is None:
            tally = _Tally(name)
            mapping[name] = tally
        return tally

    def add_planned(family_id: str, bucket_id: str, source: str) -> None:
        group_for(families, family_id).planned += 1
        group_for(buckets, bucket_id).planned += 1
        group_for(sources, source).planned += 1

    for slot in slots:
        add_planned(slot.family_id, slot.bucket_id, slot.source)

    queries: list[QueryMetrics] = []
    for slot, observation in query_rows:
        if observation is None:
            assert slot is not None
            queries.append(
                QueryMetrics(
                    family_id=slot.family_id,
                    bucket_id=slot.bucket_id,
                    query=slot.query,
                    source=slot.source,
                    detail=slot.detail,
                    status=SearchStatus.not_executed,
                    raw=0,
                    unique=0,
                    incremental=0,
                    unidentified=0,
                    duplicate=0,
                    error=None,
                )
            )
            continue
        identities = list(dict.fromkeys(observation.identities))
        incremental = incremental_by_id.get(id(observation), 0)
        identifiable = observation.raw_count - observation.unidentified_count
        unique = len(identities)
        row = QueryMetrics(
            family_id=observation.family_id,
            bucket_id=observation.bucket_id,
            query=observation.query,
            source=observation.source,
            detail=observation.detail,
            status=observation.status,
            raw=observation.raw_count,
            unique=unique,
            incremental=incremental,
            unidentified=observation.unidentified_count,
            duplicate=max(0, identifiable - unique),
            error=observation.error,
            fetched_count=observation.fetched_count,
            location_dropped=observation.location_dropped,
            recency_dropped=observation.recency_dropped,
            possible_cap=observation.possible_cap,
            hits=tuple(identities),
        )
        queries.append(row)
        for tally in (
            group_for(families, observation.family_id),
            group_for(buckets, observation.bucket_id),
            group_for(sources, observation.source),
        ):
            tally.executed += 1
            tally.raw += observation.raw_count
            tally.unidentified += observation.unidentified_count
            tally.incremental += incremental
            assert tally.identities is not None
            tally.identities.update(identities)
            if observation.status is SearchStatus.results:
                tally.with_results += 1
            elif observation.status is SearchStatus.empty:
                tally.zero_result += 1
            elif observation.status in {SearchStatus.failed, SearchStatus.partial}:
                tally.failed += 1

    family_rows = tuple(families[name].finish() for name in families)
    bucket_rows = tuple(buckets[name].finish() for name in buckets)
    source_rows = tuple(sources[name].finish() for name in sources)

    raw = sum(row.raw for row in queries)
    unidentified = sum(row.unidentified for row in queries)
    unique = len(seen)
    identifiable = raw - unidentified
    duplicate = max(0, identifiable - unique)
    with_results = sum(1 for row in queries if row.status is SearchStatus.results)
    zero_result = sum(1 for row in queries if row.status is SearchStatus.empty)
    failed = sum(
        1 for row in queries if row.status in {SearchStatus.failed, SearchStatus.partial}
    )
    not_executed = sum(1 for row in queries if row.status is SearchStatus.not_executed)
    executed_count = with_results + zero_result + failed
    successful = with_results + zero_result
    return CoverageReport(
        searches_planned=len(slots),
        searches_executed=executed_count,
        with_results=with_results,
        zero_result=zero_result,
        failed=failed,
        not_executed=not_executed,
        raw=raw,
        unique=unique,
        duplicate=duplicate,
        unidentified=unidentified,
        duplicate_rate=(round(duplicate / identifiable, 4) if identifiable else None),
        zero_result_rate=(round(zero_result / successful, 4) if successful else None),
        searches_with_incremental=sum(1 for row in queries if row.incremental > 0),
        families=family_rows,
        buckets=bucket_rows,
        sources=source_rows,
        queries=tuple(queries),
    )


def fail_unrecorded(
    plan: DiscoveryPlan,
    observations: list[SearchObservation],
    *,
    sources: tuple[str, ...],
    detail: str,
    error: str,
) -> None:
    """Mark planned searches that never reported in as failures, not empty results."""
    recorded = {(item.query, item.source, item.detail) for item in observations}
    for search in plan.searches:
        for source in sources:
            key = (search.query, source, detail)
            if key in recorded:
                continue
            observations.append(
                observe_search(
                    family_id=search.family_id,
                    bucket_id=search.bucket_id,
                    query=search.query,
                    source=source,
                    error=error,
                    detail=detail,
                    failed=True,
                )
            )
            recorded.add(key)


def log_coverage(report: CoverageReport) -> None:
    """Aggregate coverage only. Query rows stay in the JSON file."""
    log.info(
        "discovery_coverage",
        planned=report.searches_planned,
        executed=report.searches_executed,
        with_results=report.with_results,
        zero_result=report.zero_result,
        failed=report.failed,
        not_executed=report.not_executed,
        raw=report.raw,
        unique=report.unique,
        duplicate=report.duplicate,
        unidentified=report.unidentified,
        searches_with_incremental=report.searches_with_incremental,
        families=[
            {
                "name": family.name,
                "raw": family.raw,
                "unique": family.unique,
                "incremental": family.incremental,
                "zero_result": family.zero_result,
                "failed": family.failed,
            }
            for family in report.families
        ],
        identity_scope=report.identity_scope,
    )


RECENCY_SEMANTICS = {
    "linkedin": "JobSpy sends f_TPR seconds equal to hours_old * 3600 at request time",
    "indeed": "JobSpy sends dateOnIndeed starting hours_old hours before the request",
    "google": "hours_old is ignored because google_search_term replaces the time phrase",
    "zip_recruiter": "hours_old is rounded up to the next full day",
    "workday": "post-fetch postedOn and startDate filter; a missing date is kept",
}


def discovery_evidence(
    report: CoverageReport,
    *,
    hours_old: int | None,
    within_run_duplicates: int | None,
    hard_filtered_out: int | None,
    persisted: int | None,
) -> dict[str, Any]:
    """JSON stored on the ingestion stage. No descriptions or credentials."""
    queries = []
    for row in report.queries:
        queries.append(
            {
                "family_id": row.family_id,
                "bucket_id": row.bucket_id,
                "query": row.query,
                "source": row.source,
                "detail": row.detail,
                "status": row.status.value,
                "fetched_count": row.fetched_count,
                "retained_count": row.raw,
                "location_dropped": row.location_dropped,
                "recency_dropped": row.recency_dropped,
                "within_query_duplicates": row.duplicate,
                "possible_cap_hit": row.possible_cap,
                "hits": list(row.hits),
                "error": row.error,
            }
        )
    return {
        "hours_old": hours_old,
        "recency_semantics": dict(RECENCY_SEMANTICS),
        "within_run_duplicates_removed": within_run_duplicates,
        "hard_filtered_out": hard_filtered_out,
        "persisted": persisted,
        "persistence_note": "upsert_job does not distinguish insert from update",
        "queries": queries,
    }


def write_coverage(report: CoverageReport, path: Path | None = None) -> Path:
    target = path or _COVERAGE_PATH
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(report.to_dict(), indent=2) + "\n", encoding="utf-8")
    return target
