"""Allocate limited apply capacity. This does not score jobs or change workflow status."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import UTC, datetime
from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml

from automation.runner import _eligible
from config.settings import get_settings
from core.db import (
    Job,
    Status,
    get_job_by_id,
    get_jobs_by_status,
    get_recently_applied_companies,
    init_db,
    session_scope,
)
from core.textmatch import company_matches, company_tokens
from scorer.priority import sort_by_priority
from scorer.role_weights import get_role_family_weight

PORTFOLIO_VERSION = "phase14-v1"
CONFIG_PATH = Path(__file__).resolve().parent.parent / "config" / "application_portfolio.yaml"
ALLOCATED = "ALLOCATED"
DEFERRED = "DEFERRED"
BLOCKED_COMPANY = "BLOCKED_COMPANY"
BLOCKED_CAPACITY = "BLOCKED_CAPACITY"
_BUCKETS = ("PRODUCT_MANAGEMENT", "CONSULTING", "STRATEGY_TRANSFORMATION", "OTHER")
_NAMED = set(_BUCKETS) - {"OTHER"}


@dataclass(frozen=True, slots=True)
class PortfolioDecision:
    job: Job
    decision: str
    reason: str


@dataclass(frozen=True, slots=True)
class PortfolioSummary:
    allocated: int
    deferred: int
    blocked_company: int
    blocked_capacity: int
    allocated_ids: tuple[int, ...]
    version: str
    config_hash: str


def _require_int(name: str, value: object, *, lower: int, upper: int) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < lower or value > upper:
        raise ValueError(f"{name} must be an integer from {lower} through {upper}")
    return value


def _validate(raw: object) -> dict[str, Any]:
    if not isinstance(raw, dict):
        raise ValueError("portfolio config must be a mapping")
    if raw.get("version") != PORTFOLIO_VERSION:
        raise ValueError(f"portfolio version must be {PORTFOLIO_VERSION}")
    block = raw.get("portfolio")
    if not isinstance(block, dict):
        raise ValueError("portfolio config must contain a portfolio mapping")
    if set(block) != {"enabled", "max_applications_per_company"}:
        raise ValueError("portfolio config must set enabled and max_applications_per_company")
    enabled = block.get("enabled")
    if not isinstance(enabled, bool):
        raise ValueError("portfolio.enabled must be true or false")
    cap = _require_int(
        "max_applications_per_company",
        block["max_applications_per_company"],
        lower=1,
        upper=100,
    )
    return {
        "version": PORTFOLIO_VERSION,
        "portfolio": {"enabled": enabled, "max_applications_per_company": cap},
    }


@lru_cache
def load_portfolio_config(path: str | None = None) -> dict[str, Any]:
    target = Path(path) if path else CONFIG_PATH
    with target.open(encoding="utf-8") as handle:
        raw: Any = yaml.safe_load(handle)
    return _validate(raw)


def bucket_weights() -> dict[str, int]:
    """Phase 7 weights. Other families share the stored OTHER weight of 5."""
    return {
        "PRODUCT_MANAGEMENT": get_role_family_weight("PRODUCT_MANAGEMENT"),
        "CONSULTING": get_role_family_weight("CONSULTING"),
        "STRATEGY_TRANSFORMATION": get_role_family_weight("STRATEGY_TRANSFORMATION"),
        "OTHER": get_role_family_weight("OTHER"),
    }


def portfolio_config_hash(
    *,
    max_per_company: int,
    capacity: int,
    cooldown_days: int,
) -> str:
    payload = {
        "version": PORTFOLIO_VERSION,
        "max_applications_per_company": max_per_company,
        "capacity": capacity,
        "cooldown_days": cooldown_days,
        "weights": bucket_weights(),
    }
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(raw.encode()).hexdigest()


def _bucket(job: Job) -> str:
    family = (job.role_family or "").strip()
    if family in _NAMED:
        return family
    return "OTHER"


def _company_key(job: Job) -> tuple[str, ...] | None:
    tokens = company_tokens(job.company)
    return tokens or None


def _on_cooldown(job: Job, companies: set[str]) -> bool:
    return any(company_matches(job.company, name) for name in companies)


def _seat_targets(capacity: int, weights: dict[str, int]) -> dict[str, int]:
    """Largest remainder. A tied fraction goes to the bucket with fewer seats."""
    floors: dict[str, int] = {}
    fractions: dict[str, int] = {}
    for name, weight in weights.items():
        product = weight * capacity
        floors[name] = product // 100
        fractions[name] = product % 100
    left = capacity - sum(floors.values())
    order = sorted(weights, key=lambda name: (-fractions[name], floors[name], -weights[name], name))
    for name in order:
        if left <= 0:
            break
        floors[name] += 1
        left -= 1
    return floors


def _is_candidate(job: Job) -> bool:
    if job.status != Status.staged:
        return False
    return job.eligibility_state != "CLEARLY_INELIGIBLE"


def allocate_portfolio(
    jobs: list[Job],
    *,
    cooldown_companies: set[str],
    capacity: int,
    max_per_company: int,
) -> list[PortfolioDecision]:
    """Choose staged candidates. Does not write status, fit, or priority."""
    weights = bucket_weights()
    candidates = [job for job in jobs if _is_candidate(job)]
    ordered = sort_by_priority(candidates)
    cooled = [job for job in ordered if _on_cooldown(job, cooldown_companies)]
    cooled_ids = {id(job) for job in cooled}
    open_jobs = [job for job in ordered if id(job) not in cooled_ids]
    if capacity <= 0:
        blocked = [
            PortfolioDecision(job=job, decision=BLOCKED_CAPACITY, reason="blocked_capacity")
            for job in open_jobs
        ]
        blocked.extend(
            PortfolioDecision(job=job, decision=BLOCKED_COMPANY, reason="blocked_company_cooldown")
            for job in cooled
        )
        return blocked

    targets = _seat_targets(capacity, weights)
    by_bucket: dict[str, list[Job]] = {name: [] for name in _BUCKETS}
    for job in open_jobs:
        by_bucket[_bucket(job)].append(job)
    counts: dict[tuple[str, ...], int] = {}
    chosen: list[tuple[Job, str]] = []
    chosen_ids: set[int] = set()

    def identity(job: Job) -> int:
        return job.id if job.id is not None else id(job)

    def can_take(job: Job) -> bool:
        key = _company_key(job)
        if key is None:
            return True
        return counts.get(key, 0) < max_per_company

    def take(job: Job, reason: str) -> None:
        chosen.append((job, reason))
        chosen_ids.add(identity(job))
        key = _company_key(job)
        if key is not None:
            counts[key] = counts.get(key, 0) + 1

    bucket_order = sorted(_BUCKETS, key=lambda name: (-targets[name], -weights[name], name))
    for name in bucket_order:
        for job in by_bucket[name]:
            if len(chosen) >= capacity or targets[name] <= 0:
                break
            if sum(1 for item, _reason in chosen if _bucket(item) == name) >= targets[name]:
                break
            if not can_take(job):
                continue
            take(job, "allocated_for_role_family_target")
    for job in open_jobs:
        if len(chosen) >= capacity:
            break
        if identity(job) in chosen_ids or not can_take(job):
            continue
        take(job, "allocated_by_priority")

    decisions = [
        PortfolioDecision(job=job, decision=ALLOCATED, reason=reason) for job, reason in chosen
    ]
    allocated = {identity(job) for job, _reason in chosen}
    for job in open_jobs:
        if identity(job) in allocated:
            continue
        if can_take(job):
            decisions.append(
                PortfolioDecision(job=job, decision=DEFERRED, reason="deferred_capacity")
            )
        else:
            decisions.append(
                PortfolioDecision(
                    job=job,
                    decision=BLOCKED_COMPANY,
                    reason="blocked_company_concentration",
                )
            )
    decisions.extend(
        PortfolioDecision(job=job, decision=BLOCKED_COMPANY, reason="blocked_company_cooldown")
        for job in cooled
    )
    return decisions


def allocated_jobs(decisions: list[PortfolioDecision]) -> list[Job]:
    chosen = [item.job for item in decisions if item.decision == ALLOCATED]
    return sort_by_priority(chosen)


async def apply_portfolio(*, config: dict[str, Any] | None = None) -> PortfolioSummary:
    """Record allocation on staged apply candidates. Status and scores stay put."""
    await init_db()
    settings = get_settings()
    loaded = config if config is not None else load_portfolio_config()
    empty = PortfolioSummary(0, 0, 0, 0, (), PORTFOLIO_VERSION, "")
    if not loaded["portfolio"]["enabled"]:
        return empty
    capacity = settings.apply_limit
    window = settings.company_cooldown_days
    per_company = int(loaded["portfolio"]["max_applications_per_company"])
    digest = portfolio_config_hash(
        max_per_company=per_company,
        capacity=capacity,
        cooldown_days=window,
    )
    async with session_scope() as session:
        staged = await get_jobs_by_status(session, Status.staged)
        cooldown = await get_recently_applied_companies(session, cooldown_days=window)
    candidates = [job for job in staged if _eligible(job)]
    decisions = allocate_portfolio(
        candidates,
        cooldown_companies=cooldown,
        capacity=capacity,
        max_per_company=per_company,
    )
    now = datetime.now(UTC)
    for item in decisions:
        if item.job.id is None:
            continue
        async with session_scope() as session:
            target = await get_job_by_id(session, item.job.id)
            if target is None or target.status != Status.staged:
                continue
            target.portfolio_version = PORTFOLIO_VERSION
            target.portfolio_decision = item.decision
            target.portfolio_reason = item.reason
            target.portfolio_config_hash = digest
            target.updated_at = now
            session.add(target)
    chosen = allocated_jobs(decisions)
    counts = {ALLOCATED: 0, DEFERRED: 0, BLOCKED_COMPANY: 0, BLOCKED_CAPACITY: 0}
    for item in decisions:
        counts[item.decision] = counts.get(item.decision, 0) + 1
    return PortfolioSummary(
        allocated=counts[ALLOCATED],
        deferred=counts[DEFERRED],
        blocked_company=counts[BLOCKED_COMPANY],
        blocked_capacity=counts[BLOCKED_CAPACITY],
        allocated_ids=tuple(job.id for job in chosen if job.id is not None),
        version=PORTFOLIO_VERSION,
        config_hash=digest,
    )
