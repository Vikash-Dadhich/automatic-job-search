"""Choose which staged jobs enter review. This does not score or discard a job."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import UTC, datetime
from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml

from core.db import Job, Status, get_job_by_id, get_jobs_by_status, init_db, session_scope
from core.textmatch import company_tokens
from scorer.priority import sort_by_priority
from scorer.role_weights import get_role_family_weight

SHORTLIST_VERSION = "phase13-v1"
CONFIG_PATH = Path(__file__).resolve().parent.parent / "config" / "shortlist.yaml"
SELECTED_BY_PRIORITY = "selected_by_priority"
SELECTED_FOR_PORTFOLIO_DIVERSITY = "selected_for_portfolio_diversity"
_KEYS = ("max_size", "max_per_company", "diversity_margin")


@dataclass(frozen=True, slots=True)
class ShortlistPick:
    job: Job
    rank: int
    reason: str


@dataclass(frozen=True, slots=True)
class ShortlistSummary:
    selected: int
    considered: int
    already_pending: int
    version: str
    config_hash: str
    selected_ids: tuple[int, ...] = ()


def _require_int(name: str, value: object, *, lower: int, upper: int) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < lower or value > upper:
        raise ValueError(f"{name} must be an integer from {lower} through {upper}")
    return value


def _validate(raw: object) -> dict[str, Any]:
    if not isinstance(raw, dict):
        raise ValueError("shortlist config must be a mapping")
    if raw.get("version") != SHORTLIST_VERSION:
        raise ValueError(f"shortlist version must be {SHORTLIST_VERSION}")
    block = raw.get("shortlist")
    if not isinstance(block, dict) or set(block) != set(_KEYS):
        raise ValueError(
            "shortlist config must set max_size, max_per_company, and diversity_margin"
        )
    parsed = {
        "max_size": _require_int("max_size", block["max_size"], lower=0, upper=1000),
        "max_per_company": _require_int(
            "max_per_company",
            block["max_per_company"],
            lower=1,
            upper=1000,
        ),
        "diversity_margin": _require_int(
            "diversity_margin",
            block["diversity_margin"],
            lower=0,
            upper=100,
        ),
    }
    return {"version": SHORTLIST_VERSION, "shortlist": parsed}


@lru_cache
def load_shortlist_config(path: str | None = None) -> dict[str, Any]:
    target = Path(path) if path else CONFIG_PATH
    with target.open(encoding="utf-8") as handle:
        raw: Any = yaml.safe_load(handle)
    return _validate(raw)


def config_hash(config: dict[str, Any]) -> str:
    raw = json.dumps(config, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(raw.encode()).hexdigest()


def _identity(job: Job) -> int:
    return job.id if job.id is not None else id(job)


def _family(job: Job) -> str:
    name = (job.role_family or "").strip()
    return name or "UNKNOWN"


def _company_key(job: Job) -> tuple[str, ...] | None:
    """Normalized employer tokens. A blank name is not treated as one shared company."""
    tokens = company_tokens(job.company)
    return tokens or None


def _company_ok(jobs: list[Job], cap: int) -> bool:
    counts: dict[tuple[str, ...], int] = {}
    for job in jobs:
        key = _company_key(job)
        if key is None:
            continue
        counts[key] = counts.get(key, 0) + 1
        if counts[key] > cap:
            return False
    return True


def _targeted(job: Job) -> bool:
    """Families above the UNKNOWN portfolio weight may fill a diversity seat."""
    return get_role_family_weight(job.role_family) > get_role_family_weight("UNKNOWN")


def _close_enough(candidate: Job, displaced: Job, margin: int) -> bool:
    if candidate.priority_score is None:
        return False
    if displaced.priority_score is None:
        return True
    return candidate.priority_score >= displaced.priority_score - margin


def _diversify(
    selected: list[Job],
    pool: list[Job],
    reasons: dict[int, str],
    *,
    cap: int,
    margin: int,
) -> list[Job]:
    """Replace a tail seat when one family holds more than half and a close alternative exists."""
    chosen = list(selected)
    for _ in range(len(chosen)):
        if len(chosen) < 2:
            break
        counts: dict[str, int] = {}
        for job in chosen:
            family = _family(job)
            counts[family] = counts.get(family, 0) + 1
        dominant = max(counts, key=lambda name: (counts[name], name))
        if counts[dominant] * 2 <= len(chosen):
            break
        displaced = next(job for job in reversed(chosen) if _family(job) == dominant)
        chosen_ids = {_identity(job) for job in chosen}
        replacement: Job | None = None
        waiting = [job for job in pool if _identity(job) not in chosen_ids]
        for candidate in sort_by_priority(waiting):
            if _family(candidate) == dominant or not _targeted(candidate):
                continue
            if (
                displaced.priority_score is not None
                and candidate.priority_score is not None
                and candidate.priority_score < displaced.priority_score - margin
            ):
                break
            if candidate.priority_score is None:
                break
            if not _close_enough(candidate, displaced, margin):
                continue
            trial = [job for job in chosen if job is not displaced] + [candidate]
            if not _company_ok(trial, cap):
                continue
            replacement = candidate
            break
        if replacement is None:
            break
        reasons.pop(_identity(displaced), None)
        reasons[_identity(replacement)] = SELECTED_FOR_PORTFOLIO_DIVERSITY
        chosen = sort_by_priority([job for job in chosen if job is not displaced] + [replacement])
    return chosen


def select_shortlist(
    jobs: list[Job],
    *,
    config: dict[str, Any] | None = None,
    occupied: int = 0,
) -> list[ShortlistPick]:
    """Pick staged jobs in Phase 12 order. Does not write status or priority."""
    settings = config if config is not None else load_shortlist_config()
    block = settings["shortlist"]
    open_slots = max(0, int(block["max_size"]) - max(0, occupied))
    if open_slots == 0:
        return []
    pool = [job for job in jobs if job.status == Status.staged]
    ordered = sort_by_priority(pool)
    cap = int(block["max_per_company"])
    counts: dict[tuple[str, ...], int] = {}
    selected: list[Job] = []
    reasons: dict[int, str] = {}
    for job in ordered:
        if len(selected) >= open_slots:
            break
        key = _company_key(job)
        if key is not None and counts.get(key, 0) >= cap:
            continue
        selected.append(job)
        reasons[_identity(job)] = SELECTED_BY_PRIORITY
        if key is not None:
            counts[key] = counts.get(key, 0) + 1
    selected = _diversify(
        selected,
        ordered,
        reasons,
        cap=cap,
        margin=int(block["diversity_margin"]),
    )
    selected = sort_by_priority(selected)
    return [
        ShortlistPick(job=job, rank=index, reason=reasons[_identity(job)])
        for index, job in enumerate(selected, start=1)
    ]


async def apply_shortlist(*, config: dict[str, Any] | None = None) -> ShortlistSummary:
    """Move the selected staged jobs to pending_review. Other statuses stay as they are."""
    await init_db()
    settings = config if config is not None else load_shortlist_config()
    digest = config_hash(settings)
    async with session_scope() as session:
        staged = await get_jobs_by_status(session, Status.staged)
        pending = await get_jobs_by_status(session, Status.pending_review)
    picks = select_shortlist(staged, config=settings, occupied=len(pending))
    now = datetime.now(UTC)
    chosen: list[int] = []
    for pick in picks:
        if pick.job.id is None:
            continue
        async with session_scope() as session:
            target = await get_job_by_id(session, pick.job.id)
            if target is None or target.status != Status.staged:
                continue
            target.status = Status.pending_review
            target.shortlist_version = SHORTLIST_VERSION
            target.shortlist_rank = pick.rank
            target.shortlist_reason = pick.reason
            target.shortlist_config_hash = digest
            target.updated_at = now
            session.add(target)
            chosen.append(pick.job.id)
    return ShortlistSummary(
        selected=len(chosen),
        considered=len(staged),
        already_pending=len(pending),
        version=SHORTLIST_VERSION,
        config_hash=digest,
        selected_ids=tuple(chosen),
    )
