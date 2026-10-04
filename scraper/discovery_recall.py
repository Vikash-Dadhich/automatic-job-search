"""Recall of a frozen posting list against stored jobs.

This does not search, score, or merge rows. A case is captured only when an
existing identity rule matches a stored job. An empty list is not 100% recall.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

from core.db import Source
from core.job_identity import (
    locations_conflict,
    same_employer,
    same_posting_url,
    strong_field_match,
    urls_conflict,
)

BENCHMARK_VERSION = "discovery-recall-v1"
_SOURCES = frozenset(item.value for item in Source)
_DEFAULT_PATH = (
    Path(__file__).resolve().parent.parent
    / "tests"
    / "fixtures"
    / "discovery_recall_benchmark.yaml"
)


@dataclass(frozen=True, slots=True)
class Observation:
    source: str
    external_id: str | None = None
    url: str | None = None
    company: str | None = None
    title: str | None = None
    location: str | None = None
    content_hash: str | None = None


@dataclass(frozen=True, slots=True)
class BenchmarkCase:
    case_id: str
    relevant: bool
    internship: bool
    summer_2027: bool
    verified_on: str
    provenance: str
    observations: tuple[Observation, ...]
    role_family: str | None = None


@dataclass(frozen=True, slots=True)
class ObservedJob:
    source: str
    external_id: str | None = None
    url: str | None = None
    company: str | None = None
    title: str | None = None
    location: str | None = None
    content_hash: str | None = None


@dataclass(frozen=True, slots=True)
class RecallReport:
    status: str
    relevant: int
    matched: int
    unmatched: int
    recall: float | None
    unmatched_ids: tuple[str, ...]
    by_source: dict[str, dict[str, int]]
    by_family: dict[str, dict[str, int]]


def _require_str(name: str, value: object) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} must be a non-empty string")
    return value.strip()


def _observation(raw: object, case_id: str) -> Observation:
    if not isinstance(raw, dict):
        raise ValueError(f"{case_id} has an observation that is not a mapping")
    source = _require_str(f"{case_id} source", raw.get("source"))
    if source not in _SOURCES:
        raise ValueError(f"{case_id} source is not a V1 board: {source}")
    external_id = raw.get("external_id")
    url = raw.get("url")
    if external_id is not None and not isinstance(external_id, str):
        raise ValueError(f"{case_id} external_id must be a string")
    if url is not None and not isinstance(url, str):
        raise ValueError(f"{case_id} url must be a string")
    if not (external_id or "").strip() and not (url or "").strip():
        raise ValueError(f"{case_id} observation needs an external_id or a url")
    return Observation(
        source=source,
        external_id=(external_id or "").strip() or None,
        url=(url or "").strip() or None,
        company=_optional_str(raw.get("company")),
        title=_optional_str(raw.get("title")),
        location=_optional_str(raw.get("location")),
        content_hash=_optional_str(raw.get("content_hash")),
    )


def _optional_str(value: object) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str):
        raise ValueError("optional text fields must be strings")
    text = value.strip()
    return text or None


def _case(raw: object) -> BenchmarkCase:
    if not isinstance(raw, dict):
        raise ValueError("benchmark case must be a mapping")
    case_id = _require_str("case_id", raw.get("case_id"))
    for name in ("relevant", "internship", "summer_2027"):
        if not isinstance(raw.get(name), bool):
            raise ValueError(f"{case_id} {name} must be true or false")
    observations = raw.get("observations")
    if not isinstance(observations, list) or not observations:
        raise ValueError(f"{case_id} needs at least one observation")
    family = raw.get("role_family")
    if family is not None and not isinstance(family, str):
        raise ValueError(f"{case_id} role_family must be a string")
    return BenchmarkCase(
        case_id=case_id,
        relevant=bool(raw["relevant"]),
        internship=bool(raw["internship"]),
        summer_2027=bool(raw["summer_2027"]),
        verified_on=_require_str(f"{case_id} verified_on", raw.get("verified_on")),
        provenance=_require_str(f"{case_id} provenance", raw.get("provenance")),
        observations=tuple(_observation(item, case_id) for item in observations),
        role_family=(family or "").strip() or None,
    )


def load_benchmark(path: str | Path | None = None) -> tuple[BenchmarkCase, ...]:
    target = Path(path) if path else _DEFAULT_PATH
    with target.open(encoding="utf-8") as handle:
        raw: Any = yaml.safe_load(handle)
    if not isinstance(raw, dict) or raw.get("version") != BENCHMARK_VERSION:
        raise ValueError(f"benchmark version must be {BENCHMARK_VERSION}")
    cases = raw.get("cases")
    if not isinstance(cases, list):
        raise ValueError("benchmark cases must be a list")
    loaded = tuple(_case(item) for item in cases)
    ids = [item.case_id for item in loaded]
    if len(ids) != len(set(ids)):
        raise ValueError("benchmark case ids must be unique")
    return loaded


def eligible(case: BenchmarkCase) -> bool:
    """Relevant Summer 2027 internships. Other rows stay out of the denominator."""
    return case.relevant and case.internship and case.summer_2027


def observation_matches(obs: Observation, job: ObservedJob) -> bool:
    """Same rules as job upsert: source id, posting URL, or strong field match."""
    if (
        obs.source == job.source
        and obs.external_id
        and job.external_id
        and obs.external_id == job.external_id
    ):
        return True
    if same_posting_url(obs.url, job.url):
        if locations_conflict(obs.location, job.location):
            return False
        if obs.company and job.company and not same_employer(obs.company, job.company):
            return False
        return True
    if not obs.content_hash or obs.content_hash != job.content_hash:
        return False
    if urls_conflict(obs.url, job.url):
        return False
    return strong_field_match(
        company_a=obs.company,
        title_a=obs.title,
        location_a=obs.location,
        company_b=job.company,
        title_b=job.title,
        location_b=job.location,
    )


def case_is_captured(
    case: BenchmarkCase,
    jobs: tuple[ObservedJob, ...] | list[ObservedJob],
) -> bool:
    return any(
        observation_matches(obs, job) for obs in case.observations for job in jobs
    )


def _bucket() -> dict[str, int]:
    return {"relevant": 0, "matched": 0}


def _recall(matched: int, relevant: int) -> float | None:
    if relevant <= 0:
        return None
    return round(1000 * matched / relevant) / 10


def measure_recall(
    cases: tuple[BenchmarkCase, ...] | list[BenchmarkCase],
    jobs: tuple[ObservedJob, ...] | list[ObservedJob],
) -> RecallReport:
    """Unique relevant cases over stored jobs. Title similarity is not a match."""
    relevant_cases = [case for case in cases if eligible(case)]
    if not relevant_cases:
        return RecallReport(
            status="unavailable",
            relevant=0,
            matched=0,
            unmatched=0,
            recall=None,
            unmatched_ids=(),
            by_source={},
            by_family={},
        )
    unmatched: list[str] = []
    matched = 0
    by_source: dict[str, dict[str, int]] = {}
    by_family: dict[str, dict[str, int]] = {}
    for case in relevant_cases:
        captured = case_is_captured(case, jobs)
        if captured:
            matched += 1
        else:
            unmatched.append(case.case_id)
        family = case.role_family or "unlabeled"
        family_row = by_family.setdefault(family, _bucket())
        family_row["relevant"] += 1
        if captured:
            family_row["matched"] += 1
        seen_sources: set[str] = set()
        for obs in case.observations:
            if obs.source in seen_sources:
                continue
            seen_sources.add(obs.source)
            source_row = by_source.setdefault(obs.source, _bucket())
            source_row["relevant"] += 1
            if captured:
                source_row["matched"] += 1
    unmatched_ids = tuple(sorted(unmatched))
    return RecallReport(
        status="measured",
        relevant=len(relevant_cases),
        matched=matched,
        unmatched=len(unmatched_ids),
        recall=_recall(matched, len(relevant_cases)),
        unmatched_ids=unmatched_ids,
        by_source=by_source,
        by_family=by_family,
    )
