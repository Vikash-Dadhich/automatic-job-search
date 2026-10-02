"""Empirical rates from submitted applications. This does not change scores."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from datetime import datetime
from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml

from core.db import (
    Application,
    ApplicationEvent,
    FeedbackRun,
    FeedbackSignal,
    Job,
    _as_utc,
    get_feedback_run,
    get_feedback_signals,
    get_latest_feedback_run,
    init_db,
    list_events_for_applications,
    list_jobs_by_ids,
    list_submitted_applications,
    save_feedback_run,
    session_scope,
)

FEEDBACK_VERSION = "phase16-v1"
CONFIG_PATH = Path(__file__).resolve().parent.parent / "config" / "feedback.yaml"
INSUFFICIENT = "insufficient_evidence"
SUFFICIENT = "sufficient"
_OUTCOMES = ("screening", "interview", "offer", "rejected", "ghosted")
_GROUP_KEYS = ("early_positive", "strong_positive", "final_positive", "negative")
_DIMENSIONS = (
    "overall",
    "fit_band",
    "priority_band",
    "role_family",
    "role_subfamily",
    "eligibility",
    "method",
    "source",
)


@dataclass(frozen=True, slots=True)
class FeedbackCase:
    """One submitted application and the events visible to the caller."""

    application_id: int
    submitted_at: datetime
    fit_score: int | None
    priority_score: int | None
    role_family: str | None
    role_subfamily: str | None
    eligibility_state: str | None
    method: str
    source: str
    events: tuple[tuple[str, datetime], ...]


@dataclass(frozen=True, slots=True)
class FeedbackObservation:
    dimension: str
    segment: str
    sample_size: int
    known_outcomes: int
    counts: dict[str, int]
    rates: dict[str, float]
    baseline_rate: float | None
    adjusted_rate: float | None
    evidence_status: str
    adjustment: int


@dataclass(frozen=True, slots=True)
class FeedbackReport:
    version: str
    as_of: datetime
    config_hash: str
    total_applications: int
    signals: tuple[FeedbackObservation, ...] = field(default_factory=tuple)


def _require_int(name: str, value: object, *, lower: int, upper: int) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < lower or value > upper:
        raise ValueError(f"{name} must be an integer from {lower} through {upper}")
    return value


def _validate(raw: object) -> dict[str, Any]:
    if not isinstance(raw, dict) or raw.get("version") != FEEDBACK_VERSION:
        raise ValueError(f"feedback version must be {FEEDBACK_VERSION}")
    block = raw.get("feedback")
    if not isinstance(block, dict):
        raise ValueError("feedback config must contain a feedback mapping")
    bands = block.get("bands")
    if not isinstance(bands, list) or not bands:
        raise ValueError("feedback bands must be a non-empty list")
    parsed_bands: list[dict[str, int | str]] = []
    for band in bands:
        if not isinstance(band, dict):
            raise ValueError("each feedback band must be a mapping")
        parsed_bands.append(
            {
                "name": str(band["name"]),
                "min": _require_int("band.min", band["min"], lower=0, upper=100),
                "max": _require_int("band.max", band["max"], lower=0, upper=100),
            }
        )
    groups = block.get("groups")
    if not isinstance(groups, dict) or set(groups) != set(_GROUP_KEYS):
        raise ValueError("feedback groups must name each outcome group once")
    parsed_groups = {key: [str(item) for item in groups[key]] for key in _GROUP_KEYS}
    dimensions = block.get("dimensions")
    if not isinstance(dimensions, list) or set(dimensions) != set(_DIMENSIONS):
        raise ValueError("feedback dimensions must name each learning dimension once")
    enabled = block.get("priority_integration")
    if not isinstance(enabled, bool):
        raise ValueError("priority_integration must be true or false")
    return {
        "version": FEEDBACK_VERSION,
        "feedback": {
            "minimum_overall": _require_int(
                "minimum_overall", block["minimum_overall"], lower=1, upper=100000
            ),
            "minimum_segment": _require_int(
                "minimum_segment", block["minimum_segment"], lower=1, upper=100000
            ),
            "minimum_subfamily": _require_int(
                "minimum_subfamily", block["minimum_subfamily"], lower=1, upper=100000
            ),
            "shrinkage_prior": _require_int(
                "shrinkage_prior", block["shrinkage_prior"], lower=0, upper=100000
            ),
            "max_adjustment": _require_int(
                "max_adjustment", block["max_adjustment"], lower=0, upper=100
            ),
            "adjustment_per_rate": _require_int(
                "adjustment_per_rate", block["adjustment_per_rate"], lower=0, upper=1000
            ),
            "priority_integration": enabled,
            "bands": parsed_bands,
            "groups": parsed_groups,
            "dimensions": list(_DIMENSIONS),
        },
    }


@lru_cache
def load_feedback_config(path: str | None = None) -> dict[str, Any]:
    target = Path(path) if path else CONFIG_PATH
    with target.open(encoding="utf-8") as handle:
        raw: Any = yaml.safe_load(handle)
    return _validate(raw)


def feedback_config_hash(config: dict[str, Any]) -> str:
    raw = json.dumps(config, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(raw.encode()).hexdigest()


def _rate(numerator: int, denominator: int) -> float:
    if denominator <= 0:
        return 0.0
    return round(numerator / denominator, 6)


def shrink_rate(observed: float, sample_size: int, baseline: float, prior: int) -> float:
    """Pull a segment rate toward the overall rate. Large samples move less."""
    if prior < 0:
        raise ValueError("shrinkage prior must be non-negative")
    weight = sample_size + prior
    if weight <= 0:
        return round(baseline, 6)
    return round((sample_size * observed + prior * baseline) / weight, 6)


def _half_up(value: float) -> int:
    if value >= 0:
        return int(value + 0.5)
    return int(value - 0.5)


def _band(score: int | None, bands: list[dict[str, int | str]]) -> str:
    if score is None:
        return "missing"
    for band in bands:
        low = int(band["min"])
        high = int(band["max"])
        if low <= score <= high:
            return str(band["name"])
    return "missing"


def _visible(case: FeedbackCase, as_of: datetime) -> set[str]:
    cutoff = _as_utc(as_of)
    found: set[str] = set()
    if cutoff is None:
        return found
    for event_type, occurred_at in case.events:
        moment = _as_utc(occurred_at)
        if event_type in _OUTCOMES and moment is not None and moment <= cutoff:
            found.add(event_type)
    return found


def _in_cohort(case: FeedbackCase, as_of: datetime) -> bool:
    submitted = _as_utc(case.submitted_at)
    cutoff = _as_utc(as_of)
    return submitted is not None and cutoff is not None and submitted <= cutoff


def _counts(cases: list[FeedbackCase], as_of: datetime) -> dict[str, int]:
    counts = {name: 0 for name in ("submitted", "known", *_OUTCOMES)}
    for case in cases:
        if not _in_cohort(case, as_of):
            continue
        counts["submitted"] += 1
        reached = _visible(case, as_of)
        if reached:
            counts["known"] += 1
        for name in _OUTCOMES:
            if name in reached:
                counts[name] += 1
    return counts


def _group_hit(reached: set[str], labels: list[str]) -> bool:
    return any(label in reached for label in labels)


def _strong_count(
    cases: list[FeedbackCase],
    as_of: datetime,
    labels: list[str],
) -> int:
    total = 0
    for case in cases:
        if _in_cohort(case, as_of) and _group_hit(_visible(case, as_of), labels):
            total += 1
    return total


def _rates(
    counts: dict[str, int],
    *,
    strong: int,
    early: int,
    final: int,
    negative: int,
) -> dict[str, float]:
    submitted = counts["submitted"]
    return {
        "known_outcome_rate": _rate(counts["known"], submitted),
        "screening_rate": _rate(counts["screening"], submitted),
        "interview_rate": _rate(counts["interview"], submitted),
        "offer_rate": _rate(counts["offer"], submitted),
        "rejected_rate": _rate(counts["rejected"], submitted),
        "ghosted_rate": _rate(counts["ghosted"], submitted),
        "early_positive_rate": _rate(early, submitted),
        "strong_positive_rate": _rate(strong, submitted),
        "final_positive_rate": _rate(final, submitted),
        "negative_rate": _rate(negative, submitted),
        "offer_rate_among_known": _rate(counts["offer"], counts["known"]),
    }


def _minimum(dimension: str, config: dict[str, Any]) -> int:
    block = config["feedback"]
    if dimension == "overall":
        return int(block["minimum_overall"])
    if dimension == "role_subfamily":
        return int(block["minimum_subfamily"])
    return int(block["minimum_segment"])


def _adjustment(
    *,
    dimension: str,
    sample_size: int,
    observed: float,
    baseline: float,
    config: dict[str, Any],
) -> tuple[str, float, int]:
    block = config["feedback"]
    status = SUFFICIENT if sample_size >= _minimum(dimension, config) else INSUFFICIENT
    adjusted = shrink_rate(observed, sample_size, baseline, int(block["shrinkage_prior"]))
    if status == INSUFFICIENT or dimension == "overall":
        return status, adjusted, 0
    gap = (adjusted - baseline) * int(block["adjustment_per_rate"])
    limit = int(block["max_adjustment"])
    amount = _half_up(gap)
    if amount > limit:
        amount = limit
    if amount < -limit:
        amount = -limit
    return status, adjusted, amount


def segment_for(
    case: FeedbackCase,
    dimension: str,
    config: dict[str, Any] | None = None,
) -> str | None:
    """Segment label Phase 16 uses. Empty subfamilies return None."""
    loaded = config if config is not None else load_feedback_config()
    return _segment_value(case, dimension, loaded["feedback"]["bands"])


def _segment_value(
    case: FeedbackCase,
    dimension: str,
    bands: list[dict[str, int | str]],
) -> str | None:
    if dimension == "overall":
        return "all"
    if dimension == "fit_band":
        return _band(case.fit_score, bands)
    if dimension == "priority_band":
        return _band(case.priority_score, bands)
    if dimension == "role_family":
        family = (case.role_family or "").strip()
        return family or "UNKNOWN"
    if dimension == "role_subfamily":
        subfamily = (case.role_subfamily or "").strip()
        return subfamily or None
    if dimension == "eligibility":
        state = (case.eligibility_state or "").strip()
        return state or "missing"
    if dimension == "method":
        return case.method or "missing"
    if dimension == "source":
        return case.source or "missing"
    return None


def build_feedback(
    cases: list[FeedbackCase],
    *,
    as_of: datetime,
    config: dict[str, Any] | None = None,
) -> FeedbackReport:
    """Rates for submitted applications on or before as_of. Later events are ignored."""
    loaded = config if config is not None else load_feedback_config()
    block = loaded["feedback"]
    groups: dict[str, list[str]] = block["groups"]
    bands: list[dict[str, int | str]] = block["bands"]
    cohort = [case for case in cases if _in_cohort(case, as_of)]
    overall_counts = _counts(cohort, as_of)
    baseline = _rate(_strong_count(cohort, as_of, groups["strong_positive"]), len(cohort))
    signals: list[FeedbackObservation] = []
    for dimension in block["dimensions"]:
        grouped: dict[str, list[FeedbackCase]] = {}
        for case in cohort:
            segment = _segment_value(case, dimension, bands)
            if segment is None:
                continue
            grouped.setdefault(segment, []).append(case)
        for segment in sorted(grouped):
            members = grouped[segment]
            counts = _counts(members, as_of)
            strong = _strong_count(members, as_of, groups["strong_positive"])
            early = _strong_count(members, as_of, groups["early_positive"])
            final = _strong_count(members, as_of, groups["final_positive"])
            negative = _strong_count(members, as_of, groups["negative"])
            rates = _rates(
                counts,
                strong=strong,
                early=early,
                final=final,
                negative=negative,
            )
            observed = rates["strong_positive_rate"]
            status, adjusted, amount = _adjustment(
                dimension=dimension,
                sample_size=counts["submitted"],
                observed=observed,
                baseline=baseline,
                config=loaded,
            )
            rates["strong_positive_adjusted"] = adjusted
            rates["strong_positive_baseline"] = baseline
            signals.append(
                FeedbackObservation(
                    dimension=dimension,
                    segment=segment,
                    sample_size=counts["submitted"],
                    known_outcomes=counts["known"],
                    counts=counts,
                    rates=rates,
                    baseline_rate=baseline,
                    adjusted_rate=adjusted,
                    evidence_status=status,
                    adjustment=amount,
                )
            )
    ordered = tuple(sorted(signals, key=lambda item: (item.dimension, item.segment)))
    return FeedbackReport(
        version=FEEDBACK_VERSION,
        as_of=_as_utc(as_of) or as_of,
        config_hash=feedback_config_hash(loaded),
        total_applications=overall_counts["submitted"],
        signals=ordered,
    )


def _case_from_rows(
    application: Application,
    job: Job | None,
    events: list[ApplicationEvent],
) -> FeedbackCase | None:
    submitted = _as_utc(application.submitted_at)
    if submitted is None or application.id is None:
        return None
    visible = []
    for event in events:
        moment = _as_utc(event.occurred_at)
        if moment is not None:
            visible.append((event.event_type, moment))
    return FeedbackCase(
        application_id=application.id,
        submitted_at=submitted,
        fit_score=None if job is None else job.score,
        priority_score=None if job is None else job.priority_score,
        role_family=None if job is None else job.role_family,
        role_subfamily=None if job is None else job.role_subfamily,
        eligibility_state=None if job is None else job.eligibility_state,
        method=application.method,
        source=job.source.value if job is not None and job.source is not None else "missing",
        events=tuple(visible),
    )


async def load_feedback_cases() -> list[FeedbackCase]:
    """Read Phase 15 rows. Cutoff filtering happens in build_feedback."""
    await init_db()
    async with session_scope() as session:
        applications = await list_submitted_applications(session)
        ids = [row.id for row in applications if row.id is not None]
        events = await list_events_for_applications(session, ids)
        jobs = await list_jobs_by_ids(session, [row.job_id for row in applications])
    by_job = {job.id: job for job in jobs if job.id is not None}
    by_app: dict[int, list[ApplicationEvent]] = {}
    for event in events:
        by_app.setdefault(event.application_id, []).append(event)
    cases: list[FeedbackCase] = []
    for application in applications:
        if application.id is None:
            continue
        built = _case_from_rows(
            application,
            by_job.get(application.job_id),
            by_app.get(application.id, []),
        )
        if built is not None:
            cases.append(built)
    return cases


async def persist_feedback(report: FeedbackReport) -> int:
    """Store derived signals. Application rows are not copied."""
    await init_db()
    run = FeedbackRun(
        version=report.version,
        as_of=report.as_of,
        config_hash=report.config_hash,
        total_applications=report.total_applications,
    )
    signals = [
        FeedbackSignal(
            run_id=0,
            dimension=item.dimension,
            segment=item.segment,
            sample_size=item.sample_size,
            known_outcomes=item.known_outcomes,
            counts=dict(item.counts),
            rates=dict(item.rates),
            baseline_rate=item.baseline_rate,
            adjusted_rate=item.adjusted_rate,
            evidence_status=item.evidence_status,
            adjustment=item.adjustment,
        )
        for item in report.signals
    ]
    async with session_scope() as session:
        saved = await save_feedback_run(session, run, signals)
        assert saved.id is not None
        return saved.id


async def load_persisted_feedback(run_id: int) -> tuple[FeedbackRun | None, list[FeedbackSignal]]:
    await init_db()
    async with session_scope() as session:
        run = await get_feedback_run(session, run_id)
        signals = await get_feedback_signals(session, run_id)
    return run, signals


async def latest_feedback_run() -> FeedbackRun | None:
    await init_db()
    async with session_scope() as session:
        return await get_latest_feedback_run(session)
