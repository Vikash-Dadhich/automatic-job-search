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

PRIORITY_VERSION = "phase12-v2"
CONFIG_PATH = Path(__file__).resolve().parent.parent / "config" / "priority.yaml"
_COMPONENTS = (
    "fit",
    "primary_role_alignment",
    "secondary_role_bonus",
    "eligibility",
    "role_confidence",
    "jd_evidence_quality",
    "program_evidence",
    "company_domain_relevance",
    "freshness",
    "dream_company",
    "workflow",
)
_PROGRAM_LEVELS = {
    "mba_internship_program": 100,
    "full_time_mba_recruiting": 100,
    "mba_recruiting": 100,
    "business_school_recruiting": 100,
    "summer_internship_program": 70,
    "graduate_internship_program": 70,
    "us_internship_program": 70,
    "internship_program": 40,
    "us_operations": 50,
    "us_office": 50,
    "us_headquarters": 50,
    "us_careers": 40,
    "us_recruiting": 40,
}
_NO_ROLE_BONUS = frozenset({"OTHER", "UNKNOWN", ""})
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
    domains = raw.get("domains")
    if not isinstance(scales, dict) or not isinstance(domains, dict):
        raise ValueError("priority scales and domains must be mappings")
    return {
        "version": PRIORITY_VERSION,
        "weights": parsed,
        "scales": scales,
        "domains": domains,
    }


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


def primary_role_alignment(job: Job, config: dict[str, Any]) -> int | None:
    """Target-search alignment of the primary family. Not the portfolio weight."""
    family = (job.role_family or "").strip()
    if family in _NO_ROLE_BONUS:
        return None
    block = config["scales"].get("primary_role")
    if not isinstance(block, dict) or family not in block:
        return None
    return _require_int(f"primary_role.{family}", block[family])


def secondary_role_bonus(job: Job, config: dict[str, Any]) -> int | None:
    """Small extra for a second function the role performs. Not a second full weight."""
    family = (job.role_secondary_family or "").strip()
    primary = (job.role_family or "").strip()
    if family in _NO_ROLE_BONUS or family == primary:
        return None
    block = config["scales"].get("primary_role")
    if not isinstance(block, dict) or family not in block:
        return None
    return 100


def jd_evidence_quality_component(
    job: Job,
    config: dict[str, Any],
    structured: Any = None,
) -> int:
    """Evidence completeness. A long description is not automatically better."""
    if job.jd_truncated is True or job.jd_status == "truncated":
        return _scale(config, "jd_quality", "truncated")
    status = job.jd_status or ""
    if status in {"suspicious", "missing"}:
        return _scale(config, "jd_quality", status)
    if not (job.description_clean or "").strip():
        return _scale(config, "jd_quality", "missing")
    explicit = _explicit_sections(structured)
    if explicit is None:
        return 80
    return max(80, min(100, 80 + _half_up_ratio(20 * explicit, 7)))


def _explicit_sections(structured: Any) -> int | None:
    if structured is None or getattr(structured, "availability", None) == "unavailable":
        return None
    names = (
        "responsibilities",
        "qualifications",
        "experience",
        "education",
        "functional",
        "program",
        "work_model",
    )
    count = 0
    for name in names:
        section = getattr(structured, name, None)
        if getattr(section, "state", None) == "explicit":
            count += 1
    return count


def program_evidence_component(job: Job, structured: Any, company: Any) -> int | None:
    """Strongest internship or U.S. program fact. Related facts are not added together."""
    del job
    level: int | None = None
    for item in _company_signals(company):
        name = str(item.get("signal") or "")
        if name in _PROGRAM_LEVELS and item.get("value") is True:
            level = max(level or 0, _PROGRAM_LEVELS[name])
        if name in _PROGRAM_LEVELS and item.get("value") is False:
            continue
    program = getattr(structured, "program", None)
    if getattr(program, "mba_internship", None) is True:
        level = max(level or 0, 100)
    elif getattr(program, "summer_internship", None) is True:
        level = max(level or 0, 70)
    elif getattr(program, "internship", None) is True:
        level = max(level or 0, 40)
    return level


def company_domain_component(job: Job, config: dict[str, Any], company: Any) -> int | None:
    """One capped point if a factual domain matches the target families. Not quality."""
    allowed = _relevant_domains(job, config)
    if not allowed:
        return None
    found = {
        str(item.get("value"))
        for item in _company_signals(company)
        if str(item.get("signal") or "").startswith("domain:")
    }
    if not found & allowed:
        return None
    return 100


def _relevant_domains(job: Job, config: dict[str, Any]) -> set[str]:
    mapping = config.get("domains")
    if not isinstance(mapping, dict):
        return set()
    names = {job.role_family, job.role_secondary_family}
    found: set[str] = set()
    for name in names:
        values = mapping.get(name)
        if isinstance(values, list):
            found.update(str(item) for item in values)
    return found


def _company_signals(company: Any) -> list[dict[str, Any]]:
    if not isinstance(company, dict):
        return []
    raw = company.get("signals")
    if not isinstance(raw, list):
        return []
    return [item for item in raw if isinstance(item, dict)]


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
    structured: Any = None,
    company_context: Any = None,
) -> dict[str, int | None]:
    return {
        "fit": fit_component(job),
        "primary_role_alignment": primary_role_alignment(job, config),
        "secondary_role_bonus": secondary_role_bonus(job, config),
        "eligibility": eligibility_component(job, config),
        "role_confidence": role_confidence_component(job, config),
        "jd_evidence_quality": jd_evidence_quality_component(job, config, structured),
        "program_evidence": program_evidence_component(job, structured, company_context),
        "company_domain_relevance": company_domain_component(job, config, company_context),
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
    fit = components["fit"]
    if fit is None:
        lines.append("Candidate-job fit is not available.")
    elif fit >= 75:
        lines.append("Strong candidate-job fit.")
    else:
        lines.append(f"Candidate-job fit is {fit}.")
    alignment = components["primary_role_alignment"]
    if alignment == 100:
        lines.append("Tier 1 target role family.")
    elif alignment == 70:
        lines.append("Tier 2 target role family.")
    elif alignment is not None:
        lines.append("Additional target role family.")
    if components["secondary_role_bonus"] is not None:
        lines.append(f"Secondary {job.role_secondary_family} responsibility.")
    state = job.eligibility_state
    if state == "CONFIRMED_ELIGIBLE":
        lines.append("Eligibility confirmed.")
    elif state == "UNKNOWN":
        lines.append("Eligibility unknown.")
    elif state == "CLEARLY_INELIGIBLE":
        lines.append("Eligibility is clearly ineligible.")
    elif state:
        lines.append(f"Eligibility is {state}.")
    if components["role_confidence"] == 100:
        lines.append("High-confidence role classification.")
    program = components["program_evidence"]
    if program == 100:
        lines.append("Explicit MBA internship program evidence.")
    elif program is not None and program >= 70:
        lines.append("Explicit internship program evidence.")
    elif program is not None:
        lines.append("General internship program evidence.")
    if components["company_domain_relevance"] == 100:
        lines.append("Relevant company domain evidence.")
    if components["jd_evidence_quality"] is not None and components["jd_evidence_quality"] <= 40:
        lines.append("Limited JD evidence.")
    if job.jd_truncated is True or job.jd_status == "truncated":
        lines.append("The job description is truncated.")
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


def _relevant_company_signals(company: Any) -> list[dict[str, Any]]:
    kept: list[dict[str, Any]] = []
    for item in _company_signals(company):
        name = str(item.get("signal") or "")
        if name.startswith("domain:") or name in _PROGRAM_LEVELS:
            kept.append({"signal": name, "value": item.get("value")})
    return sorted(kept, key=lambda item: (item["signal"], str(item["value"])))


def _structured_view(structured: Any) -> dict[str, Any] | None:
    if structured is None:
        return None
    sections = {}
    for name in (
        "responsibilities",
        "qualifications",
        "experience",
        "education",
        "functional",
        "program",
        "work_model",
    ):
        section = getattr(structured, name, None)
        sections[name] = getattr(section, "state", None)
    program = getattr(structured, "program", None)
    return {
        "version": getattr(structured, "version", None),
        "availability": getattr(structured, "availability", None),
        "sections": sections,
        "mba_internship": getattr(program, "mba_internship", None),
        "summer_internship": getattr(program, "summer_internship", None),
        "internship": getattr(program, "internship", None),
    }


def _input_hash(
    job: Job,
    profile: Profile,
    config: dict[str, Any],
    *,
    now: datetime | None = None,
    structured: Any = None,
    company_context: Any = None,
) -> str:
    dreams = sorted(name.strip() for name in profile.preferences.dream_companies if name.strip())
    payload = {
        "version": PRIORITY_VERSION,
        "weights": config["weights"],
        "scales": config["scales"],
        "domains": config.get("domains"),
        "score": job.score,
        "fit_version": job.fit_version,
        "role_family": job.role_family,
        "role_subfamily": job.role_subfamily,
        "role_confidence": job.role_confidence,
        "role_classifier_version": job.role_classifier_version,
        "role_secondary_family": job.role_secondary_family,
        "role_secondary_subfamily": job.role_secondary_subfamily,
        "role_secondary_confidence": job.role_secondary_confidence,
        "eligibility_state": job.eligibility_state,
        "eligibility_version": job.eligibility_version,
        "jd_status": job.jd_status,
        "jd_truncated": job.jd_truncated,
        "structured": _structured_view(structured),
        "company_signals": _relevant_company_signals(company_context),
        "posted_at": _iso(job.posted_at),
        "discovered_at": _iso(job.discovered_at),
        "company": job.company,
        "status": None if job.status is None else job.status.value,
        "dream_companies": dreams,
        "freshness_day": _freshness_day(now),
    }
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str)
    return hashlib.sha256(raw.encode()).hexdigest()


def priority_is_current(
    job: Job,
    profile: Profile,
    *,
    now: datetime | None = None,
    structured: Any = None,
    company_context: Any = None,
) -> bool:
    config = load_priority_config()
    return bool(
        job.priority_score is not None
        and job.priority_version == PRIORITY_VERSION
        and job.priority_input_hash
        and job.priority_input_hash
        == _input_hash(
            job,
            profile,
            config,
            now=now,
            structured=structured,
            company_context=company_context,
        )
        and job.priority_components
    )


def calculate_priority(
    job: Job,
    profile: Profile,
    *,
    now: datetime | None = None,
    structured: Any = None,
    company_context: Any = None,
) -> PriorityDecision:
    """Rank one stored job. Does not write the row and does not change fit."""
    config = load_priority_config()
    moment = _as_utc(now) or datetime.now(UTC)
    parts = _components(
        job,
        profile,
        config,
        now=moment,
        structured=structured,
        company_context=company_context,
    )
    return PriorityDecision(
        score=_combine(parts, config["weights"]),
        version=PRIORITY_VERSION,
        reasons=_reasons(job, parts),
        components=parts,
        input_hash=_input_hash(
            job,
            profile,
            config,
            now=moment,
            structured=structured,
            company_context=company_context,
        ),
    )


def apply_priority(
    job: Job,
    profile: Profile,
    *,
    now: datetime | None = None,
    structured: Any = None,
    company_context: Any = None,
) -> PriorityDecision:
    """Store priority fields. Fit, eligibility, role, and status stay as they are.

    The same UTC calendar day reuses the stored score. A later day recomputes
    freshness. The hash stores that date, not the exact clock time.
    """
    if priority_is_current(
        job,
        profile,
        now=now,
        structured=structured,
        company_context=company_context,
    ):
        components = job.priority_components if isinstance(job.priority_components, dict) else {}
        return PriorityDecision(
            score=int(job.priority_score or 0),
            version=PRIORITY_VERSION,
            reasons=list(job.priority_reasons or []),
            components=components,
            input_hash=str(job.priority_input_hash or ""),
        )
    decision = calculate_priority(
        job,
        profile,
        now=now,
        structured=structured,
        company_context=company_context,
    )
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
