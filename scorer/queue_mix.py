"""Fill the daily queue by role type: product, consulting, other business roles.

The split is applied to the job title (``scraper.title_family``), the same thing
the owner reads on a card. Within a group, the best fit score goes first. This
only chooses among jobs that already passed scoring; it never changes a score.
"""

from __future__ import annotations

import math
import re
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml

from core.db import Job, Status
from core.textmatch import company_tokens
from scorer.priority import sort_by_priority
from scraper.title_family import TARGET_FAMILIES, title_family

CONFIG_PATH = Path(__file__).resolve().parent.parent / "config" / "queue_mix.yaml"
SELECTED_BY_MIX = "selected_by_mix"
SELECTED_BY_SPILL = "selected_by_spill"


@dataclass(frozen=True, slots=True)
class MixGroup:
    name: str
    share: float
    families: frozenset[str]


@dataclass(frozen=True, slots=True)
class Mix:
    groups: tuple[MixGroup, ...]
    spill_order: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class MixPick:
    job: Job
    group: str
    reason: str


def _parse(raw: Any) -> Mix:
    if not isinstance(raw, dict) or not isinstance(raw.get("groups"), dict):
        raise ValueError("queue_mix.yaml must define groups")
    groups: list[MixGroup] = []
    seen: set[str] = set()
    for name, block in raw["groups"].items():
        if not isinstance(block, dict):
            raise ValueError(f"group {name} must be a mapping")
        share = block.get("share")
        families = block.get("families")
        if isinstance(share, bool) or not isinstance(share, int | float) or share < 0:
            raise ValueError(f"group {name} needs a share of 0 or more")
        if not isinstance(families, list) or not families:
            raise ValueError(f"group {name} needs a list of families")
        for family in families:
            if family not in TARGET_FAMILIES:
                raise ValueError(f"unknown family {family}")
            if family in seen:
                raise ValueError(f"family {family} is in two groups")
            seen.add(family)
        groups.append(MixGroup(str(name), float(share), frozenset(families)))
    total = sum(group.share for group in groups)
    if not math.isclose(total, 1.0, abs_tol=0.001):
        raise ValueError("group shares must add up to 1.0")
    names = [group.name for group in groups]
    spill = raw.get("spill_order", names)
    if not isinstance(spill, list) or sorted(spill) != sorted(names):
        raise ValueError("spill_order must list every group once")
    return Mix(tuple(groups), tuple(str(item) for item in spill))


@lru_cache
def load_mix(path: str | None = None) -> Mix:
    with Path(path or CONFIG_PATH).open(encoding="utf-8") as handle:
        return _parse(yaml.safe_load(handle))


def seat_plan(mix: Mix, seats: int) -> dict[str, int]:
    """Seats per group. Rounding leftovers go to the largest remainders, ties by order."""
    if seats <= 0:
        return {group.name: 0 for group in mix.groups}
    raw = {group.name: group.share * seats for group in mix.groups}
    plan = {name: int(math.floor(value)) for name, value in raw.items()}
    left = seats - sum(plan.values())
    order = sorted(mix.groups, key=lambda g: (-(raw[g.name] - plan[g.name]), -g.share))
    for group in order[:left]:
        plan[group.name] += 1
    return plan


def _group_of(job: Job, mix: Mix) -> str | None:
    family = title_family(job.title)
    if family is None:
        return None
    for group in mix.groups:
        if family in group.families:
            return group.name
    return None


def _norm_title(title: str | None) -> str:
    text = re.sub(r"\(.*?\)|\[.*?\]", " ", (title or "").lower())
    text = re.sub(r"\b(20\d\d|summer|intern(ship)?|mba)\b", " ", text)
    return re.sub(r"[^a-z]+", " ", text).strip()


def _fit_order(jobs: list[Job]) -> list[Job]:
    """Best fit first. Priority, then recency, break ties."""
    by_priority = {id(job): index for index, job in enumerate(sort_by_priority(jobs))}
    return sorted(jobs, key=lambda job: (-(job.score or 0), by_priority[id(job)]))


def select_mix(
    jobs: list[Job],
    *,
    seats: int,
    mix: Mix | None = None,
    max_per_company: int = 2,
    taken: list[Job] | None = None,
) -> list[MixPick]:
    """Choose up to ``seats`` staged jobs following the mix.

    ``taken`` are jobs already waiting in the queue; they count toward the company
    cap and duplicate check so the same role never shows up twice.
    """
    mix = mix or load_mix()
    if seats <= 0:
        return []
    pool = [
        job
        for job in jobs
        if job.status == Status.staged and job.score is not None and _group_of(job, mix)
    ]
    ordered = _fit_order(pool)
    counts: dict[tuple[str, ...], int] = {}
    titles: set[tuple[tuple[str, ...], str]] = set()
    for job in taken or []:
        key = company_tokens(job.company)
        if key:
            counts[key] = counts.get(key, 0) + 1
            titles.add((key, _norm_title(job.title)))

    picks: list[MixPick] = []
    chosen: set[int] = set()

    def _try(job: Job, group: str, reason: str) -> bool:
        key = company_tokens(job.company)
        if key:
            if counts.get(key, 0) >= max_per_company:
                return False
            if (key, _norm_title(job.title)) in titles:
                return False
        picks.append(MixPick(job=job, group=group, reason=reason))
        chosen.add(id(job))
        if key:
            counts[key] = counts.get(key, 0) + 1
            titles.add((key, _norm_title(job.title)))
        return True

    plan = seat_plan(mix, seats)
    for group in mix.groups:
        want = plan[group.name]
        for job in ordered:
            if want <= 0:
                break
            if id(job) in chosen or _group_of(job, mix) != group.name:
                continue
            if _try(job, group.name, SELECTED_BY_MIX):
                want -= 1

    for name in mix.spill_order:
        for job in ordered:
            if len(picks) >= seats:
                break
            if id(job) in chosen or _group_of(job, mix) != name:
                continue
            _try(job, name, SELECTED_BY_SPILL)
    group_rank = {group.name: index for index, group in enumerate(mix.groups)}
    return sorted(picks, key=lambda pick: (group_rank[pick.group], -(pick.job.score or 0)))


def queue_group(job: Job, mix: Mix | None = None) -> str | None:
    return _group_of(job, mix or load_mix())
