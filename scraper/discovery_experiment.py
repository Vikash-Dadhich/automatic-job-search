"""Controlled comparison of the frozen 111-phrase and 123-phrase catalogs.

Dry-run is the default. It builds a plan and does not contact a job board or
write the job database. Live execution is opt-in and still does not upsert,
score, or notify. Production ingestion does not call this module.
"""

from __future__ import annotations

import json
import random
import uuid
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import yaml

from config.settings import PROJECT_ROOT
from config.targets import Targets, load_targets
from scraper.discovery import DiscoveryPlan, PlannedSearch, build_discovery_plan
from scraper.discovery_recall import ObservedJob, case_is_captured, eligible, load_benchmark
from scraper.redact import redact_error

EXPERIMENT_VERSION = "discovery-experiment-v1"
ARM_BASELINE = "baseline_111"
ARM_TREATMENT = "treatment_123"
_FIXTURE_DIR = PROJECT_ROOT / "tests" / "fixtures"
BASELINE_PATH = _FIXTURE_DIR / "discovery_baseline_111.yaml"
TREATMENT_PATH = _FIXTURE_DIR / "discovery_treatment_123.yaml"
_DEFAULT_PERSIST_DIR = PROJECT_ROOT / "storage" / "experiments"

SOURCE_LIMITATIONS: dict[str, str] = {
    "linkedin": (
        "JobSpy sends hours_old as f_TPR at request time. One scrape covers every "
        "selected JobSpy site. An exception fails each of those sites for that phrase "
        "and is not stored as an empty result."
    ),
    "indeed": "hours_old is sent as dateOnIndeed. HTTP 403 is a failed search.",
    "google": (
        "hours_old is ignored. The adapter sends '{phrase} internship', not the "
        "planned phrase. That rewrite is stored as executed_query. Confirmed "
        "vocabulary yield is withheld for Google. This does not fix recency."
    ),
    "zip_recruiter": "hours_old is rounded up to whole days, so 36 hours becomes 1 day.",
        "workday": (
            "The frozen phrase is sent to each active tenant, one tenant after another. "
            "Recency is applied after the response. A block or HTTP error is a failed "
            "search. Placeholder tenants are excluded, matching ordinary ingestion. Rows "
            "are attributed to the phrase that was requested, not to words in the title."
        ),
}

_SUCCESS = frozenset({"results", "empty"})
_RETURNED = frozenset({"results", "partial"})
_BASELINE_PRIORITY = {
    "missing_baseline": 0,
    "baseline_failed": 1,
    "baseline_skipped": 2,
    "baseline_incomplete": 3,
    "ambiguous_attribution": 4,
}


class ExperimentRefusal(Exception):
    """The requested mode is not allowed to run."""


@dataclass(frozen=True, slots=True)
class FrozenPhrase:
    arm: str
    family_id: str
    bucket_id: str
    query: str


@dataclass(frozen=True, slots=True)
class QueryExecution:
    experiment_id: str
    arm: str
    family_id: str
    bucket_id: str
    query: str
    source: str
    detail: str
    started_at: str
    finished_at: str
    status: str
    result_count: int | None
    unidentified: int
    identities: tuple[str, ...]
    possible_cap: bool
    error: str | None
    ambiguous: bool = False
    executed_query: str = ""

    def as_dict(self) -> dict[str, Any]:
        return {
            "experiment_id": self.experiment_id,
            "arm": self.arm,
            "family_id": self.family_id,
            "bucket_id": self.bucket_id,
            "query": self.query,
            "executed_query": self.executed_query or self.query,
            "source": self.source,
            "detail": self.detail,
            "started_at": self.started_at,
            "finished_at": self.finished_at,
            "status": self.status,
            "result_count": self.result_count,
            "unidentified": self.unidentified,
            "identities": list(self.identities),
            "possible_cap": self.possible_cap,
            "error": self.error,
            "ambiguous": self.ambiguous,
        }


def _now() -> str:
    return datetime.now(UTC).isoformat()


def _require_phrase(raw: object, arm: str) -> FrozenPhrase:
    if not isinstance(raw, dict):
        raise ValueError(f"{arm} phrase must be a mapping")
    family_id = raw.get("family_id")
    bucket_id = raw.get("bucket_id")
    query = raw.get("query")
    if not all(isinstance(item, str) and item.strip() for item in (family_id, bucket_id, query)):
        raise ValueError(f"{arm} phrase is missing family, bucket, or query")
    return FrozenPhrase(
        arm=arm,
        family_id=str(family_id).strip(),
        bucket_id=str(bucket_id).strip(),
        query=str(query).strip(),
    )


def load_frozen_catalog(path: Path, arm: str) -> tuple[FrozenPhrase, ...]:
    """Load one frozen arm. Duplicate phrases are rejected."""
    with path.open(encoding="utf-8") as handle:
        raw = yaml.safe_load(handle)
    if not isinstance(raw, dict) or raw.get("version") != EXPERIMENT_VERSION:
        raise ValueError(f"{path.name} version must be {EXPERIMENT_VERSION}")
    if raw.get("arm") != arm:
        raise ValueError(f"{path.name} arm must be {arm}")
    phrases = raw.get("phrases")
    if not isinstance(phrases, list) or not phrases:
        raise ValueError(f"{path.name} needs a phrase list")
    loaded = tuple(_require_phrase(item, arm) for item in phrases)
    folded = [item.query.casefold() for item in loaded]
    if len(folded) != len(set(folded)):
        raise ValueError(f"{arm} has duplicate phrases")
    expected = 111 if arm == ARM_BASELINE else 123
    if len(loaded) != expected:
        raise ValueError(f"{arm} must contain {expected} phrases, found {len(loaded)}")
    return loaded


def load_arms(
    baseline_path: Path | None = None,
    treatment_path: Path | None = None,
) -> tuple[tuple[FrozenPhrase, ...], tuple[FrozenPhrase, ...]]:
    baseline = load_frozen_catalog(baseline_path or BASELINE_PATH, ARM_BASELINE)
    treatment = load_frozen_catalog(treatment_path or TREATMENT_PATH, ARM_TREATMENT)
    return baseline, treatment


def treatment_only_phrases(
    baseline: tuple[FrozenPhrase, ...],
    treatment: tuple[FrozenPhrase, ...],
) -> tuple[str, ...]:
    known = {item.query.casefold() for item in baseline}
    return tuple(item.query for item in treatment if item.query.casefold() not in known)


def build_schedule(
    baseline: tuple[FrozenPhrase, ...],
    treatment: tuple[FrozenPhrase, ...],
    seed: int,
) -> tuple[FrozenPhrase, ...]:
    """Interleave the two arms. Shared phrases run back to back, order randomized."""
    rng = random.Random(seed)
    baseline_by = {item.query.casefold(): item for item in baseline}
    treatment_by = {item.query.casefold(): item for item in treatment}
    shared = [item.query.casefold() for item in baseline if item.query.casefold() in treatment_by]
    schedule: list[FrozenPhrase] = []
    for key in shared:
        first: FrozenPhrase = baseline_by[key]
        second: FrozenPhrase = treatment_by[key]
        if rng.randrange(2) == 1:
            first, second = second, first
        schedule.extend((first, second))
    extras = [
        item for item in baseline if item.query.casefold() not in treatment_by
    ] + [item for item in treatment if item.query.casefold() not in baseline_by]
    rng.shuffle(extras)
    for phrase in extras:
        schedule.insert(rng.randrange(len(schedule) + 1), phrase)
    return tuple(schedule)


def _settings_snapshot(targets: Targets) -> dict[str, Any]:
    """Source settings both arms share. Query text is not taken from this object."""
    plan = build_discovery_plan(targets)
    return {
        "jobspy_sites": list(plan.jobspy_sites),
        "workday_enabled": plan.workday_enabled,
        "location": targets.search.location,
        "distance": targets.search.distance,
        "results_wanted": targets.search.results_wanted,
        "hours_old": targets.search.hours_old,
        "country_indeed": targets.search.country_indeed,
        "linkedin_fetch_description": targets.search.linkedin_fetch_description,
        "active_workday_tenants": [item.name for item in targets.active_workday_tenants()],
        "placeholder_workday_tenants": [
            item.name for item in targets.workday_tenants if item.is_placeholder
        ],
        "note": (
            "Both arms use these settings. Phrases come from the frozen fixtures, "
            "not from search.terms."
        ),
    }


def _one_plan(phrase: FrozenPhrase, settings: dict[str, Any]) -> DiscoveryPlan:
    return DiscoveryPlan(
        capacity_requested=1,
        capacity_usable=1,
        capacity_assigned=1,
        families=(),
        bucket_assigned={phrase.bucket_id: 1},
        searches=(
            PlannedSearch(
                family_id=phrase.family_id,
                bucket_id=phrase.bucket_id,
                query=phrase.query,
            ),
        ),
        jobspy_sites=tuple(settings["jobspy_sites"]),
        workday_enabled=bool(settings["workday_enabled"]),
    )


def _identities(rows: list[QueryExecution], arm: str | None = None) -> set[str]:
    found: set[str] = set()
    for row in rows:
        if arm is not None and row.arm != arm:
            continue
        if row.status not in _RETURNED:
            continue
        found.update(row.identities)
    return found


def _tally(rows: list[QueryExecution]) -> dict[str, Any]:
    raw = 0
    unidentified = 0
    seen: list[str] = []
    for row in rows:
        if row.status not in _SUCCESS and row.status != "partial":
            continue
        raw += (row.result_count or 0) + row.unidentified
        unidentified += row.unidentified
        if row.status in _RETURNED:
            seen.extend(row.identities)
    unique = set(seen)
    identified = len(seen)
    return {
        # `planned` is the number of observation rows in this tally, not the
        # number of scheduled slots. `observation_rows` is the same count.
        "planned": len(rows),
        "observation_rows": len(rows),
        "executed": sum(1 for row in rows if row.status in _SUCCESS),
        "with_results": sum(1 for row in rows if row.status == "results"),
        "empty": sum(1 for row in rows if row.status == "empty"),
        "failed": sum(1 for row in rows if row.status == "failed"),
        "skipped": sum(1 for row in rows if row.status == "not_executed"),
        "incomplete": sum(1 for row in rows if row.status == "incomplete"),
        "partial": sum(1 for row in rows if row.status == "partial"),
        "capped": sum(1 for row in rows if row.possible_cap and row.status in _SUCCESS),
        "raw_results": raw,
        "unidentified": unidentified,
        "unique_identities": len(unique),
        "duplicate_identities": max(0, identified - len(unique)),
    }


def _returning_rows(rows: list[QueryExecution], arm: str, identity: str) -> list[QueryExecution]:
    return [
        row
        for row in rows
        if row.arm == arm and row.status in _RETURNED and identity in row.identities
    ]


def _supporters(rows: list[QueryExecution], arm: str, identity: str) -> set[str]:
    return {row.query.casefold() for row in _returning_rows(rows, arm, identity)}


def _baseline_slot_reason(
    rows: list[QueryExecution],
    slots: set[tuple[str, str, str]],
    source: str,
) -> str | None:
    """Why this source cannot prove the baseline missed a posting."""
    relevant = [slot for slot in slots if slot[1] == source]
    if not relevant:
        return "missing_baseline"
    found: str | None = None
    for query, slot_source, detail in relevant:
        matched = [
            row
            for row in rows
            if row.arm == ARM_BASELINE
            and row.query.casefold() == query
            and row.source == slot_source
            and row.detail == detail
        ]
        if not matched:
            code = "missing_baseline"
        elif any(row.ambiguous for row in matched):
            code = "ambiguous_attribution"
        elif all(row.status in _SUCCESS for row in matched):
            continue
        elif any(row.status == "failed" for row in matched):
            code = "baseline_failed"
        elif any(row.status == "not_executed" for row in matched):
            code = "baseline_skipped"
        else:
            code = "baseline_incomplete"
        if found is None or _BASELINE_PRIORITY[code] < _BASELINE_PRIORITY[found]:
            found = code
    return found


def _classify_incremental(
    rows: list[QueryExecution],
    identities: set[str],
    new_phrases: set[str],
    *,
    baseline_slots: set[tuple[str, str, str]],
    run_complete: bool,
) -> dict[str, Any]:
    """Split treatment-only ids. Confirmed yield needs a finished baseline."""
    vocabulary: list[str] = []
    withheld: list[dict[str, str]] = []
    mixed: list[str] = []
    volatility: list[str] = []
    for identity in sorted(identities):
        queries = _supporters(rows, ARM_TREATMENT, identity)
        evidence = _returning_rows(rows, ARM_TREATMENT, identity)
        if not queries:
            withheld.append({"identity": identity, "reason": "ambiguous_attribution"})
            continue
        if queries & new_phrases and not queries <= new_phrases:
            mixed.append(identity)
            continue
        if not queries <= new_phrases:
            volatility.append(identity)
            continue
        if not run_complete:
            withheld.append({"identity": identity, "reason": "run_incomplete"})
            continue
        if any(row.source == "google" for row in evidence):
            # The adapter searched a rewritten string. Do not confirm the planned phrase.
            withheld.append({"identity": identity, "reason": "ambiguous_attribution"})
            continue
        if any(row.ambiguous or row.source == "unidentified" for row in evidence):
            withheld.append({"identity": identity, "reason": "ambiguous_attribution"})
            continue
        sources = sorted({row.source for row in evidence})
        reason: str | None = None
        for source in sources:
            slot_reason = _baseline_slot_reason(rows, baseline_slots, source)
            if slot_reason is None:
                continue
            if reason is None or _BASELINE_PRIORITY[slot_reason] < _BASELINE_PRIORITY[reason]:
                reason = slot_reason
        if reason is None:
            vocabulary.append(identity)
        else:
            withheld.append({"identity": identity, "reason": reason})
    return {
        "vocabulary_only": vocabulary,
        "vocabulary_withheld": withheld,
        "mixed_with_shared_phrases": mixed,
        "shared_phrase_only": volatility,
    }


def _verified_benchmark_hits(identities: list[str]) -> list[dict[str, str]]:
    """Checked-in Summer 2027 cases only. Title text is not evidence."""
    if not identities:
        return []
    cases = [case for case in load_benchmark() if eligible(case)]
    hits: list[dict[str, str]] = []
    for identity in identities:
        source, _, external_id = identity.partition(":")
        if not source or not external_id:
            continue
        job = ObservedJob(source=source, external_id=external_id)
        for case in cases:
            if case_is_captured(case, (job,)):
                hits.append({"identity": identity, "case_id": case.case_id})
                break
    return hits


def compare_arms(
    executions: list[QueryExecution],
    *,
    new_phrases: tuple[str, ...],
    baseline_slots: set[tuple[str, str, str]] | None = None,
    run_complete: bool = True,
) -> dict[str, Any]:
    """Overlap of source-and-external-id identities. Failed searches add none.

    ``baseline_slots`` are the scheduled shared-phrase slots ``(query, source, detail)``.
    A slot with no row is missing evidence, not an empty search.
    """
    baseline_ids = _identities(executions, ARM_BASELINE)
    treatment_ids = _identities(executions, ARM_TREATMENT)
    both = baseline_ids & treatment_ids
    baseline_only = baseline_ids - treatment_ids
    treatment_only = treatment_ids - baseline_ids
    new_folded = {phrase.casefold() for phrase in new_phrases}
    incremental = _classify_incremental(
        executions,
        treatment_only,
        new_folded,
        baseline_slots=baseline_slots or set(),
        run_complete=run_complete,
    )
    by_source: dict[str, Any] = {}
    sources = sorted({row.source for row in executions})
    for source in sources:
        source_rows = [row for row in executions if row.source == source]
        by_source[source] = {
            "baseline": _tally([row for row in source_rows if row.arm == ARM_BASELINE]),
            "treatment": _tally([row for row in source_rows if row.arm == ARM_TREATMENT]),
            "overall": _tally(source_rows),
        }
    return {
        "by_source": by_source,
        "overall": {
            "baseline": _tally([row for row in executions if row.arm == ARM_BASELINE]),
            "treatment": _tally([row for row in executions if row.arm == ARM_TREATMENT]),
            "overall": _tally(executions),
        },
        "in_both_arms": sorted(both),
        "baseline_only": sorted(baseline_only),
        "treatment_only": sorted(treatment_only),
        "incremental": incremental,
        "verified_summer_2027_mba_in_vocabulary_increment": _verified_benchmark_hits(
            incremental["vocabulary_only"]
        ),
        "interpretation": (
            "vocabulary_only is a confirmed candidate: the run finished, every "
            "returning observation used one of the 12 new phrases, and every "
            "scheduled baseline search on those sources finished as results or empty. "
            "vocabulary_withheld means that proof is missing. shared_phrase_only is "
            "volatility, not new vocabulary. This is not market recall, and it is "
            "not the separate 5/21 benchmark."
        ),
    }


def _incomplete(
    phrase: FrozenPhrase,
    experiment_id: str,
    source: str,
    detail: str,
    *,
    error: str | None = None,
) -> QueryExecution:
    stamp = _now()
    return QueryExecution(
        experiment_id=experiment_id,
        arm=phrase.arm,
        family_id=phrase.family_id,
        bucket_id=phrase.bucket_id,
        query=phrase.query,
        source=source,
        detail=detail,
        started_at=stamp,
        finished_at=stamp,
        status="incomplete",
        result_count=None,
        unidentified=0,
        identities=(),
        possible_cap=False,
        error=error,
        ambiguous=False,
    )


def _from_observation(
    obs: Any,
    phrase: FrozenPhrase,
    experiment_id: str,
    started_at: str,
    finished_at: str,
) -> QueryExecution:
    mismatch = obs.query != phrase.query
    raw_status = obs.status.value if hasattr(obs.status, "value") else obs.status
    status = "failed" if mismatch else str(raw_status)
    returned = status in _RETURNED
    error = obs.error
    if mismatch:
        error = "adapter query did not match the requested phrase"
    if status in _RETURNED:
        result_count: int | None = len(obs.identities)
    elif status == "empty":
        result_count = 0
    else:
        result_count = None
    ambiguous = bool(getattr(obs, "ambiguous", False)) or str(obs.source) == "unidentified"
    from scraper.linkedin_jobspy import google_executed_query

    executed_query = (
        google_executed_query(phrase.query) if str(obs.source) == "google" else phrase.query
    )
    return QueryExecution(
        experiment_id=experiment_id,
        arm=phrase.arm,
        family_id=phrase.family_id,
        bucket_id=phrase.bucket_id,
        query=phrase.query,
        source=str(obs.source),
        detail=str(obs.detail or ""),
        started_at=started_at,
        finished_at=finished_at,
        status=status,
        result_count=result_count,
        unidentified=int(obs.unidentified_count) if returned else 0,
        identities=tuple(obs.identities) if returned else (),
        possible_cap=bool(obs.possible_cap) and status in _SUCCESS,
        error=redact_error(error) if error else None,
        ambiguous=ambiguous,
        executed_query=executed_query,
    )


def _expected_slots(settings: dict[str, Any]) -> list[tuple[str, str]]:
    slots = [(site, "") for site in settings["jobspy_sites"]]
    if settings["workday_enabled"]:
        slots.extend(("workday", name) for name in settings["active_workday_tenants"])
    return slots


async def _execute_phrase(
    phrase: FrozenPhrase,
    *,
    experiment_id: str,
    targets: Targets,
    settings: dict[str, Any],
    jobspy_fetch: Callable[..., Awaitable[Any]],
    workday_fetch: Callable[..., Awaitable[Any]],
) -> list[QueryExecution]:
    started = _now()
    observations: list[Any] = []
    plan = _one_plan(phrase, settings)
    provenance = {phrase.query: (phrase.family_id, phrase.bucket_id)}
    try:
        if plan.jobspy_sites:
            await jobspy_fetch(targets, plan=plan, observations=observations)
        if plan.workday_enabled and settings["active_workday_tenants"]:
            tenants = [
                tenant
                for tenant in targets.active_workday_tenants()
                if tenant.name in settings["active_workday_tenants"]
            ]
            for tenant in tenants:
                await workday_fetch(
                    tenant,
                    search_terms=[phrase.query],
                    hours_old=targets.search.hours_old,
                    provenance=provenance,
                    observations=observations,
                )
    except Exception as exc:
        finished = _now()
        message = redact_error(str(exc))
        converted = [
            _from_observation(obs, phrase, experiment_id, started, finished) for obs in observations
        ]
        present = {(row.source, row.detail) for row in converted}
        for source, detail in _expected_slots(settings):
            if (source, detail) in present:
                continue
            converted.append(
                QueryExecution(
                    experiment_id=experiment_id,
                    arm=phrase.arm,
                    family_id=phrase.family_id,
                    bucket_id=phrase.bucket_id,
                    query=phrase.query,
                    source=source,
                    detail=detail,
                    started_at=started,
                    finished_at=finished,
                    status="failed",
                    result_count=None,
                    unidentified=0,
                    identities=(),
                    possible_cap=False,
                    error=message,
                    ambiguous=False,
                )
            )
        return converted or [
            _incomplete(phrase, experiment_id, "none", "", error=message)
        ]
    finished = _now()
    converted = [
        _from_observation(obs, phrase, experiment_id, started, finished) for obs in observations
    ]
    present = {(row.source, row.detail) for row in converted}
    for source, detail in _expected_slots(settings):
        if (source, detail) not in present:
            converted.append(
                _incomplete(
                    phrase,
                    experiment_id,
                    source,
                    detail,
                    error="no observation was recorded; this is not an empty result",
                )
            )
    return converted


async def _execute(
    schedule: tuple[FrozenPhrase, ...],
    *,
    experiment_id: str,
    targets: Targets,
    settings: dict[str, Any],
    jobspy_fetch: Callable[..., Awaitable[Any]],
    workday_fetch: Callable[..., Awaitable[Any]],
) -> tuple[list[QueryExecution], str, str | None, bool]:
    """Run the schedule. KeyboardInterrupt propagates and does not return a report."""
    executions: list[QueryExecution] = []
    status = "complete"
    error: str | None = None
    runner_finished = True
    for index, phrase in enumerate(schedule):
        try:
            executions.extend(
                await _execute_phrase(
                    phrase,
                    experiment_id=experiment_id,
                    targets=targets,
                    settings=settings,
                    jobspy_fetch=jobspy_fetch,
                    workday_fetch=workday_fetch,
                )
            )
        except Exception as exc:
            # KeyboardInterrupt is not caught. In-flight observations for the
            # phrase that was running are discarded, and no report is returned.
            status = "incomplete"
            error = redact_error(str(exc))
            runner_finished = False
            for rest in schedule[index:]:
                for source, detail in _expected_slots(settings) or [("none", "")]:
                    executions.append(
                        _incomplete(rest, experiment_id, source, detail, error=error)
                    )
            break
    if any(row.status == "incomplete" for row in executions):
        status = "incomplete"
    return executions, status, error, runner_finished


def _phrase_row(phrase: FrozenPhrase) -> dict[str, str]:
    return {
        "arm": phrase.arm,
        "family_id": phrase.family_id,
        "bucket_id": phrase.bucket_id,
        "query": phrase.query,
    }


def _baseline_slots(
    baseline: tuple[FrozenPhrase, ...],
    treatment: tuple[FrozenPhrase, ...],
    settings: dict[str, Any],
) -> set[tuple[str, str, str]]:
    """Scheduled shared-phrase slots. A missing row is not an empty search."""
    shared = {item.query.casefold() for item in baseline} & {
        item.query.casefold() for item in treatment
    }
    details = _source_details(settings)
    return {
        (query, source, detail)
        for query in shared
        for source, source_details in details.items()
        for detail in source_details
    }


def _source_details(settings: dict[str, Any]) -> dict[str, tuple[str, ...]]:
    details: dict[str, tuple[str, ...]] = {
        site: ("",) for site in settings.get("jobspy_sites", ())
    }
    if settings.get("workday_enabled"):
        tenants = tuple(settings.get("active_workday_tenants") or ("",))
        details["workday"] = tenants
    return details


def scheduled_slots(
    schedule: tuple[FrozenPhrase, ...],
    settings: dict[str, Any],
) -> set[tuple[str, str, str, str]]:
    """Expected slots: arm, planned phrase, source, and detail."""
    details = _source_details(settings)
    return {
        (phrase.arm, phrase.query.casefold(), source, detail)
        for phrase in schedule
        for source, source_details in details.items()
        for detail in source_details
    }


def _slot_bucket(rows: list[QueryExecution]) -> str:
    """One bucket per scheduled slot. Missing rows are incomplete, not empty."""
    if not rows:
        return "incomplete"
    statuses = {row.status for row in rows}
    if "failed" in statuses:
        return "failed"
    if "incomplete" in statuses:
        return "incomplete"
    if "partial" in statuses or any(row.ambiguous for row in rows):
        return "partial"
    if "not_executed" in statuses:
        return "skipped"
    if statuses <= _SUCCESS:
        return "completed"
    return "incomplete"


def plan_request_volume(
    schedule: tuple[FrozenPhrase, ...],
    baseline: tuple[FrozenPhrase, ...],
    treatment: tuple[FrozenPhrase, ...],
    settings: dict[str, Any],
) -> dict[str, Any]:
    """Adapter-call counts. These are not HTTP request counts.

    One JobSpy phrase call sends every configured JobSpy site together and may
    issue more than one HTTP request. One Workday tenant call is one adapter
    invocation for one phrase on one active tenant. Observation slots count
    each site or tenant separately.
    """
    shared = {item.query.casefold() for item in baseline} & {
        item.query.casefold() for item in treatment
    }
    baseline_only = {item.query.casefold() for item in baseline} - shared
    treatment_only = {item.query.casefold() for item in treatment} - shared
    sites = list(settings.get("jobspy_sites") or [])
    tenants = (
        list(settings.get("active_workday_tenants") or [])
        if settings.get("workday_enabled")
        else []
    )
    phrases = len(schedule)
    jobspy_calls = phrases if sites else 0
    workday_calls = phrases * len(tenants)
    return {
        "shared_phrases": len(shared),
        "shared_phrase_executions": sum(
            1 for item in schedule if item.query.casefold() in shared
        ),
        "treatment_only_phrases": len(treatment_only),
        "treatment_only_executions": sum(
            1 for item in schedule if item.query.casefold() in treatment_only
        ),
        "baseline_only_phrases": len(baseline_only),
        "baseline_only_executions": sum(
            1 for item in schedule if item.query.casefold() in baseline_only
        ),
        "schedule_length": phrases,
        "jobspy_phrase_calls": jobspy_calls,
        "jobspy_sites_per_call": len(sites),
        "workday_tenant_calls": workday_calls,
        "workday_tenants": len(tenants),
        "planned_adapter_calls": jobspy_calls + workday_calls,
        "scheduled_observation_slots": len(scheduled_slots(schedule, settings)),
        "note": (
            "One JobSpy phrase call contacts every configured JobSpy site and may "
            "issue more than one HTTP request. planned_adapter_calls is not an HTTP "
            "request count. workday_tenant_calls is one adapter call per scheduled "
            "phrase per active tenant. scheduled_observation_slots counts one slot "
            "per site or tenant and is not a JobSpy call count."
        ),
    }


def account_executions(
    executions: list[QueryExecution],
    slots: set[tuple[str, str, str, str]],
    incremental: dict[str, Any],
) -> dict[str, Any]:
    """Slot counts separate from observation rows. Failed slots are not empty."""
    buckets = {"completed": 0, "partial": 0, "failed": 0, "skipped": 0, "incomplete": 0}
    for arm, query, source, detail in slots:
        matched = [
            row
            for row in executions
            if row.arm == arm
            and row.query.casefold() == query
            and row.source == source
            and row.detail == detail
        ]
        buckets[_slot_bucket(matched)] += 1
    withheld = incremental.get("vocabulary_withheld") or []
    reasons: dict[str, int] = {}
    for item in withheld:
        reason = str(item.get("reason", ""))
        reasons[reason] = reasons.get(reason, 0) + 1
    attributed = sum(len(row.identities) for row in executions if row.status in _RETURNED)
    return {
        "scheduled_slots": len(slots),
        "observation_rows": len(executions),
        "completed_slots": buckets["completed"],
        "partial_slots": buckets["partial"],
        "failed_slots": buckets["failed"],
        "skipped_slots": buckets["skipped"],
        "incomplete_slots": buckets["incomplete"],
        "raw_attributed_hits": attributed,
        "unidentified_rows": sum(row.unidentified for row in executions),
        "distinct_identities": len(_identities(executions)),
        "vocabulary_only_count": len(incremental.get("vocabulary_only") or []),
        "withheld_reason_counts": reasons,
        "metric_notes": {
            "planned": "Observation rows in a tally. Not the scheduled-slot count.",
            "observation_rows": "Same count as planned: recorded observation rows.",
            "scheduled_slots": "Expected (arm, planned phrase, source, detail) slots.",
            "completed_slots": "Scheduled slots whose rows are only results or empty.",
            "raw_results": (
                "Attributed hits plus unidentified placeholders on results, empty, "
                "and partial rows. raw_attributed_hits excludes unidentified placeholders."
            ),
            "status": (
                "complete means the runner finished the schedule without an incomplete "
                "slot. It does not mean every slot succeeded."
            ),
        },
    }


def _payload(
    *,
    experiment_id: str,
    mode: str,
    status: str,
    seed: int,
    started_at: str,
    finished_at: str,
    settings: dict[str, Any],
    baseline: tuple[FrozenPhrase, ...],
    treatment: tuple[FrozenPhrase, ...],
    schedule: tuple[FrozenPhrase, ...],
    executions: list[QueryExecution],
    measured: bool,
    run_error: str | None,
    persisted_path: str | None,
    runner_finished: bool,
) -> dict[str, Any]:
    new_phrases = treatment_only_phrases(baseline, treatment)
    comparison = (
        compare_arms(
            executions,
            new_phrases=new_phrases,
            baseline_slots=_baseline_slots(baseline, treatment, settings),
            run_complete=status == "complete",
        )
        if measured
        else {
        "by_source": {},
        "overall": {},
        "in_both_arms": [],
        "baseline_only": [],
        "treatment_only": [],
        "incremental": {
            "vocabulary_only": [],
            "vocabulary_withheld": [],
            "mixed_with_shared_phrases": [],
            "shared_phrase_only": [],
        },
        "verified_summer_2027_mba_in_vocabulary_increment": [],
        "interpretation": (
            "Dry-run records the plan only. It does not measure yield. "
            "A live run is still observational and is not the 5/21 benchmark."
        ),
        }
    )
    accounting = account_executions(
        executions,
        scheduled_slots(schedule, settings),
        comparison["incremental"],
    )
    all_required = (
        accounting["scheduled_slots"] > 0
        and accounting["completed_slots"] == accounting["scheduled_slots"]
    )
    if measured and status != "complete":
        comparison["interpretation"] = (
            "This run is incomplete. Counts cover only the searches recorded before it stopped. "
            + str(comparison["interpretation"])
        )
    return {
        "version": EXPERIMENT_VERSION,
        "experiment_id": experiment_id,
        "mode": mode,
        "status": status,
        "runner_finished": runner_finished,
        "all_required_slots_completed": all_required,
        "completion_note": (
            "status complete means the runner finished the schedule and no slot is "
            "incomplete. Failed or partial slots can still be present. "
            "all_required_slots_completed is true only when every scheduled slot is "
            "results or empty. KeyboardInterrupt is not caught; observations for the "
            "phrase then running are discarded and no report is returned."
        ),
        "accounting": accounting,
        "request_volume": plan_request_volume(schedule, baseline, treatment, settings),
        "measured": measured,
        "seed": seed,
        "started_at": started_at,
        "finished_at": finished_at,
        "external_requests": mode == "live",
        "database_writes": False,
        "production_catalog_mutated": False,
        "telegram": False,
        "run_error": run_error,
        "persisted_path": persisted_path,
        "arms": {
            ARM_BASELINE: {"phrases": len(baseline)},
            ARM_TREATMENT: {"phrases": len(treatment)},
        },
        "treatment_only_phrases": list(new_phrases),
        "schedule_length": len(schedule),
        "schedule_preview": [_phrase_row(item) for item in schedule[:6]],
        "schedule": [_phrase_row(item) for item in schedule],
        "settings": settings,
        "limitations": dict(SOURCE_LIMITATIONS),
        "executions": [row.as_dict() for row in executions],
        "comparison": comparison,
    }


def _persist(payload: dict[str, Any], directory: Path) -> str:
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / f"{payload['experiment_id']}.json"
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return str(path)


def format_summary(payload: dict[str, Any]) -> str:
    """Short JSON for the terminal. The full schedule stays in the payload."""
    view = {
        "experiment_id": payload["experiment_id"],
        "mode": payload["mode"],
        "status": payload["status"],
        "runner_finished": payload["runner_finished"],
        "all_required_slots_completed": payload["all_required_slots_completed"],
        "completion_note": payload["completion_note"],
        "accounting": payload["accounting"],
        "request_volume": payload["request_volume"],
        "measured": payload["measured"],
        "seed": payload["seed"],
        "external_requests": payload["external_requests"],
        "database_writes": payload["database_writes"],
        "production_catalog_mutated": payload["production_catalog_mutated"],
        "telegram": payload["telegram"],
        "persisted_path": payload["persisted_path"],
        "arms": payload["arms"],
        "treatment_only_phrases": payload["treatment_only_phrases"],
        "schedule_length": payload["schedule_length"],
        "schedule_preview": payload["schedule_preview"],
        "settings": payload["settings"],
        "limitations": payload["limitations"],
        "comparison": {
            key: payload["comparison"][key]
            for key in (
                "in_both_arms",
                "baseline_only",
                "treatment_only",
                "incremental",
                "verified_summer_2027_mba_in_vocabulary_increment",
                "interpretation",
            )
        },
    }
    return json.dumps(view, indent=2)


async def run_discovery_experiment(
    *,
    live: bool = False,
    persist: bool = False,
    seed: int | None = None,
    experiment_id: str | None = None,
    persist_dir: Path | None = None,
    targets: Targets | None = None,
    jobspy_fetch: Callable[..., Awaitable[Any]] | None = None,
    workday_fetch: Callable[..., Awaitable[Any]] | None = None,
) -> dict[str, Any]:
    """Plan both arms. Contact boards only when ``live`` is true.

    ``persist`` writes a JSON file and still does not touch the jobs table.
    It is refused unless ``live`` is also set.
    """
    if persist and not live:
        raise ExperimentRefusal("Persistence requires --live. A dry-run writes nothing.")
    chosen_seed = seed if seed is not None else random.SystemRandom().randrange(2**31)
    run_id = experiment_id or uuid.uuid4().hex
    started = _now()
    baseline, treatment = load_arms()
    schedule = build_schedule(baseline, treatment, chosen_seed)
    loaded_targets = targets if targets is not None else load_targets()
    settings = _settings_snapshot(loaded_targets)
    if not live:
        return _payload(
            experiment_id=run_id,
            mode="dry_run",
            status="planned",
            seed=chosen_seed,
            started_at=started,
            finished_at=_now(),
            settings=settings,
            baseline=baseline,
            treatment=treatment,
            schedule=schedule,
            executions=[],
            measured=False,
            run_error=None,
            persisted_path=None,
            runner_finished=False,
        )

    if jobspy_fetch is None or workday_fetch is None:
        from scraper.linkedin_jobspy import fetch_linkedin_indeed
        from scraper.workday_rest import fetch_workday

        jobspy_fetch = jobspy_fetch or fetch_linkedin_indeed
        workday_fetch = workday_fetch or fetch_workday

    executions, status, run_error, runner_finished = await _execute(
        schedule,
        experiment_id=run_id,
        targets=loaded_targets,
        settings=settings,
        jobspy_fetch=jobspy_fetch,
        workday_fetch=workday_fetch,
    )
    payload = _payload(
        experiment_id=run_id,
        mode="live",
        status=status,
        seed=chosen_seed,
        started_at=started,
        finished_at=_now(),
        settings=settings,
        baseline=baseline,
        treatment=treatment,
        schedule=schedule,
        executions=executions,
        measured=True,
        run_error=run_error,
        persisted_path=None,
        runner_finished=runner_finished,
    )
    if persist:
        payload["persisted_path"] = _persist(payload, persist_dir or _DEFAULT_PERSIST_DIR)
    return payload
