"""Deterministic attention order. This does not filter jobs and does not rescore fit."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import UTC, datetime
from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml

from config.profile import Profile
from core.db import Job, Status
from scorer.engine import is_dream_company
from scorer.role_weights import get_role_family_weight, load_role_family_weights

PRIORITY_VERSION = "phase12-v1"
CONFIG_PATH = Path(__file__).resolve().parent.parent / "config" / "priority.yaml"
_COMPONENTS = (
    "fit",
    "role_family",
    "eligibility",
    "role_confidence",
    "jd_quality",
    "freshness",
    "dream_company",
    "workflow",
)
_OPEN = {
    Status.discovered,
    Status.scored,
    Status.staged,
    Status.pending_review,
    Status.manual_review,
}
_ACTED = {Status.submitted, Status.ignored}
_CLOSED = {Status.filtered_out, Status.error}


@dataclass(frozen=True, slots=True)
class PriorityDecision:
    score: int
    version: str
    reasons: list[str]
    components: dict[str, int | None]
    input_hash: str


def _require_int(name: str, value: object, *, upper: int = 100) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0 or value > upper:
        raise ValueError(f"{name} must be an integer from 0 through {upper}")
    return value


def _validate(raw: object) -> dict[str, Any]:
    if not isinstance(raw, dict):
        raise ValueError("priority config must be a mapping")
    if raw.get("version") != PRIORITY_VERSION:
        raise ValueError(f"priority version must be {PRIORITY_VERSION}")
    weights = raw.get("weights")
    if not isinstance(weights, dict) or set(weights) != set(_COMPONENTS):
        raise ValueError("priority weights must name each ranking component once")
    parsed = {name: _require_int(name, weights[name]) for name in _COMPONENTS}
    if sum(parsed.values()) != 100:
        raise ValueError("priority weights must sum to 100")
    scales = raw.get("scales")
    if not isinstance(scales, dict):
        raise ValueError("priority scales must be a mapping")
    return {"version": PRIORITY_VERSION, "weights": parsed, "scales": scales}


@lru_cache
def load_priority_config(path: str | None = None) -> dict[str, Any]:
    target = Path(path) if path else CONFIG_PATH
    with target.open(encoding="utf-8") as handle:
        raw: Any = yaml.safe_load(handle)
    return _validate(raw)


def _scale(config: dict[str, Any], group: str, key: str) -> int:
    scales = config["scales"]
    block = scales.get(group)
    if not isinstance(block, dict) or key not in block:
        raise ValueError(f"priority scale {group}.{key} is missing")
    return _require_int(f"{group}.{key}", block[key])


def _iso(value: datetime | None) -> str | None:
    stamp = _as_utc(value)
    if stamp is None:
        return None
    return stamp.isoformat()


def _as_utc(value: datetime | None) -> datetime | None:
    if value is None:
        return None
    if value.tzinfo is None:
        return value.replace(tzinfo=UTC)
    return value.astimezone(UTC)


def fit_component(job: Job) -> int | None:
    """Phase 6 fit number, unchanged. Missing fit is omitted, not zero."""
    if job.score is None:
        return None
    return max(0, min(100, int(job.score)))


def _half_up_ratio(numerator: int, denominator: int) -> int:
    """Divide and round halves up. 5/40 of 100 is 12.5, which becomes 13."""
    return (numerator + denominator // 2) // denominator


def role_family_component(job: Job) -> int:
    """Portfolio weight scaled so the top family is 100. Not a fit score."""
    weights = load_role_family_weights()
    top = max(weights.values()) or 1
    raw = get_role_family_weight(job.role_family)
    return max(0, min(100, _half_up_ratio(raw * 100, top)))


def eligibility_component(job: Job, config: dict[str, Any]) -> int | None:
    state = job.eligibility_state
    if not state:
        return None
    return _scale(config, "eligibility", state)


def role_confidence_component(job: Job, config: dict[str, Any]) -> int | None:
    level = (job.role_confidence or "").strip().lower()
    if level not in {"high", "medium", "low"}:
        return None
    return _scale(config, "role_confidence", level)


def jd_quality_component(job: Job, config: dict[str, Any]) -> int:
    if job.jd_truncated is True or job.jd_status == "truncated":
        return _scale(config, "jd_quality", "truncated")
    status = job.jd_status or ""
    if status in {"present", "suspicious", "missing"}:
        return _scale(config, "jd_quality", status)
    if not (job.description_clean or "").strip():
        return _scale(config, "jd_quality", "missing")
    return _scale(config, "jd_quality", "unknown")


def freshness_component(
    job: Job,
    config: dict[str, Any],
    *,
    now: datetime,
) -> int | None:
    stamp = _as_utc(job.posted_at) or _as_utc(job.discovered_at)
    if stamp is None:
        return None
    fresh = config["scales"]["freshness"]
    floor = _require_int("freshness.floor", fresh["floor"])
    horizon = _require_int("freshness.horizon_days", fresh["horizon_days"], upper=3650)
    if horizon <= 0:
        raise ValueError("freshness.horizon_days must be positive")
    days = max(0.0, (now - stamp).total_seconds() / 86400)
    span = 100 - floor
    score = 100 - span * min(days, float(horizon)) / float(horizon)
    return max(0, min(100, round(score)))


def dream_company_component(job: Job, profile: Profile) -> int | None:
    """Explicit user list only. An empty list is omitted, not a penalty."""
    dreams = [name for name in profile.preferences.dream_companies if name and name.strip()]
    if not dreams:
        return None
    return 100 if is_dream_company(job.company or "", profile) else 0


def workflow_component(job: Job, config: dict[str, Any]) -> int:
    status = job.status
    if status in _ACTED:
        return _scale(config, "workflow", "acted")
    if status in _CLOSED:
        return _scale(config, "workflow", "closed")
    if status in _OPEN or status is None:
        return _scale(config, "workflow", "open")
    return _scale(config, "workflow", "open")


def _components(
    job: Job,
    profile: Profile,
    config: dict[str, Any],
    *,
    now: datetime,
) -> dict[str, int | None]:
    return {
        "fit": fit_component(job),
        "role_family": role_family_component(job),
        "eligibility": eligibility_component(job, config),
        "role_confidence": role_confidence_component(job, config),
        "jd_quality": jd_quality_component(job, config),
        "freshness": freshness_component(job, config, now=now),
        "dream_company": dream_company_component(job, profile),
        "workflow": workflow_component(job, config),
    }


def _combine(components: dict[str, int | None], weights: dict[str, int]) -> int:
    available = {name: value for name, value in components.items() if value is not None}
    if not available:
        return 50
    weighted = sum(weights[name] * value for name, value in available.items())
    total_weight = sum(weights[name] for name in available)
    score = round(weighted / total_weight)
    return max(0, min(100, score))


def _reasons(job: Job, components: dict[str, int | None]) -> list[str]:
    lines: list[str] = []
    if components["fit"] is None:
        lines.append("Candidate-job fit is not available.")
    else:
        lines.append(f"Candidate-job fit is {components['fit']}.")
    family = job.role_family or "UNKNOWN"
    weight = get_role_family_weight(job.role_family)
    lines.append(f"Role family {family} has portfolio weight {weight}.")
    if components["eligibility"] is None:
        lines.append("Eligibility has not been recorded.")
    else:
        lines.append(f"Eligibility is {job.eligibility_state}.")
    if job.jd_truncated is True or job.jd_status == "truncated":
        lines.append("The job description is truncated.")
    elif job.jd_status == "missing" or not (job.description_clean or "").strip():
        lines.append("The job description is missing.")
    if components["freshness"] is None:
        lines.append("No posted or discovered time is available.")
    elif job.posted_at is not None:
        lines.append("Freshness uses the posted time.")
    else:
        lines.append("Freshness uses the discovery time because posted time is missing.")
    if components["dream_company"] == 100:
        lines.append("Company matches a configured dream company.")
    if job.status in _ACTED:
        lines.append(f"Workflow state is {job.status.value}.")
    return lines


def _freshness_day(now: datetime | None) -> str:
    """UTC calendar date used as the freshness cache key. Not the clock time."""
    moment = _as_utc(now) or datetime.now(UTC)
    return moment.date().isoformat()


def _input_hash(
    job: Job,
    profile: Profile,
    config: dict[str, Any],
    *,
    now: datetime | None = None,
) -> str:
    dreams = sorted(name.strip() for name in profile.preferences.dream_companies if name.strip())
    payload = {
        "version": PRIORITY_VERSION,
        "weights": config["weights"],
        "scales": config["scales"],
        "score": job.score,
        "role_family": job.role_family,
        "role_confidence": job.role_confidence,
        "eligibility_state": job.eligibility_state,
        "jd_status": job.jd_status,
        "jd_truncated": job.jd_truncated,
        "jd_char_count": job.jd_char_count,
        "posted_at": _iso(job.posted_at),
        "discovered_at": _iso(job.discovered_at),
        "company": job.company,
        "status": None if job.status is None else job.status.value,
        "dream_companies": dreams,
        "freshness_day": _freshness_day(now),
    }
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str)
    return hashlib.sha256(raw.encode()).hexdigest()


def priority_is_current(job: Job, profile: Profile, *, now: datetime | None = None) -> bool:
    config = load_priority_config()
    return bool(
        job.priority_score is not None
        and job.priority_version == PRIORITY_VERSION
        and job.priority_input_hash
        and job.priority_input_hash == _input_hash(job, profile, config, now=now)
        and job.priority_components
    )


def calculate_priority(
    job: Job,
    profile: Profile,
    *,
    now: datetime | None = None,
) -> PriorityDecision:
    """Rank one stored job. Does not write the row and does not change fit."""
    config = load_priority_config()
    moment = _as_utc(now) or datetime.now(UTC)
    parts = _components(job, profile, config, now=moment)
    return PriorityDecision(
        score=_combine(parts, config["weights"]),
        version=PRIORITY_VERSION,
        reasons=_reasons(job, parts),
        components=parts,
        input_hash=_input_hash(job, profile, config, now=moment),
    )


def apply_priority(
    job: Job,
    profile: Profile,
    *,
    now: datetime | None = None,
) -> PriorityDecision:
    """Store priority fields. Fit, eligibility, role, and status stay as they are.

    The same UTC calendar day reuses the stored score. A later day recomputes
    freshness. The hash stores that date, not the exact clock time.
    """
    if priority_is_current(job, profile, now=now):
        components = job.priority_components if isinstance(job.priority_components, dict) else {}
        return PriorityDecision(
            score=int(job.priority_score or 0),
            version=PRIORITY_VERSION,
            reasons=list(job.priority_reasons or []),
            components=components,
            input_hash=str(job.priority_input_hash or ""),
        )
    decision = calculate_priority(job, profile, now=now)
    job.priority_score = decision.score
    job.priority_version = decision.version
    job.priority_reasons = list(decision.reasons)
    job.priority_components = dict(decision.components)
    job.priority_input_hash = decision.input_hash
    return decision


def sort_by_priority(jobs: list[Job]) -> list[Job]:
    """Highest priority first. Fit, then recency, then id break ties."""

    def posted(job: Job) -> float:
        stamp = _as_utc(job.posted_at) or _as_utc(job.discovered_at)
        return stamp.timestamp() if stamp is not None else 0.0

    return sorted(
        jobs,
        key=lambda job: (
            -(job.priority_score if job.priority_score is not None else -1),
            -(job.score if job.score is not None else -1),
            -posted(job),
            job.id or 0,
        ),
    )
