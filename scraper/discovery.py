"""Role-family discovery plan. Weights allocate search capacity, not fit scores."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from functools import lru_cache
from pathlib import Path
from typing import Any

import structlog
import yaml
from pydantic import BaseModel, Field, field_validator, model_validator

log = structlog.get_logger(__name__)

DISCOVERY_PATH = Path(__file__).resolve().parent.parent / "config" / "discovery.yaml"
_WEIGHT_QUANTUM = Decimal("0.01")
_ONE = Decimal("1.00")


class SearchBucket(BaseModel):
    id: str
    name: str
    enabled: bool = True
    queries: list[str] = Field(default_factory=list)
    title_variants: list[str] = Field(default_factory=list)

    @field_validator("id", "name")
    @classmethod
    def _strip_required(cls, value: str) -> str:
        text = value.strip()
        if not text:
            raise ValueError("bucket id and name must be non-empty")
        return text

    @field_validator("queries", "title_variants")
    @classmethod
    def _clean_phrases(cls, value: list[str]) -> list[str]:
        return [item.strip() for item in value if item and item.strip()]


class RoleFamily(BaseModel):
    id: str
    name: str
    weight: Decimal
    enabled: bool = True
    buckets: list[SearchBucket] = Field(default_factory=list)

    @field_validator("id", "name")
    @classmethod
    def _strip_required(cls, value: str) -> str:
        text = value.strip()
        if not text:
            raise ValueError("family id and name must be non-empty")
        return text

    @field_validator("weight", mode="before")
    @classmethod
    def _quantize_weight(cls, value: object) -> Decimal:
        weight = Decimal(str(value)).quantize(_WEIGHT_QUANTUM)
        if weight < 0:
            raise ValueError("family weight must be >= 0")
        return weight


class DiscoverySource(BaseModel):
    id: str
    name: str
    enabled: bool = True

    @field_validator("id", "name")
    @classmethod
    def _strip_required(cls, value: str) -> str:
        text = value.strip()
        if not text:
            raise ValueError("source id and name must be non-empty")
        return text


class DiscoveryConfig(BaseModel):
    """What to search. How a source runs stays in targets.yaml."""

    families: list[RoleFamily] = Field(min_length=1)
    sources: list[DiscoverySource] = Field(min_length=1)

    @model_validator(mode="after")
    def _validate_structure(self) -> DiscoveryConfig:
        family_ids = [family.id for family in self.families]
        if len(family_ids) != len(set(family_ids)):
            raise ValueError("role family ids must be unique")

        bucket_ids: list[str] = []
        queries: list[str] = []
        for family in self.families:
            for bucket in family.buckets:
                bucket_ids.append(bucket.id)
                if bucket.enabled and not bucket.queries:
                    raise ValueError(f"enabled bucket {bucket.id} has no queries")
                queries.extend(bucket.queries)
        if len(bucket_ids) != len(set(bucket_ids)):
            raise ValueError("search bucket ids must be unique")
        folded = [query.casefold() for query in queries]
        if len(folded) != len(set(folded)):
            raise ValueError("search queries must be unique across buckets")

        source_ids = [source.id for source in self.sources]
        if len(source_ids) != len(set(source_ids)):
            raise ValueError("discovery source ids must be unique")

        enabled = [family for family in self.families if family.enabled]
        if not enabled:
            raise ValueError("at least one role family must be enabled")
        total = sum((family.weight for family in enabled), Decimal("0"))
        if total != _ONE:
            raise ValueError(f"enabled family weights must sum to 1.00, got {total}")
        return self


@dataclass(frozen=True, slots=True)
class AllocItem:
    id: str
    weight: Decimal
    available: int


@dataclass(frozen=True, slots=True)
class PlannedSearch:
    family_id: str
    bucket_id: str
    query: str


@dataclass(frozen=True, slots=True)
class FamilyAllocation:
    family_id: str
    weight: Decimal
    available: int
    ideal: Decimal
    assigned: int

    @property
    def spillover(self) -> int:
        """Units received above the uncapped ideal, after capacity caps."""
        above = self.assigned - int(self.ideal)
        return above if above > 0 else 0


@dataclass(frozen=True, slots=True)
class DiscoveryPlan:
    capacity_requested: int
    capacity_assigned: int
    families: tuple[FamilyAllocation, ...]
    bucket_assigned: dict[str, int]
    searches: tuple[PlannedSearch, ...]
    jobspy_sites: tuple[str, ...]
    workday_enabled: bool

    def provenance_for(self, query: str) -> PlannedSearch | None:
        for search in self.searches:
            if search.query == query:
                return search
        return None


def _largest_remainder(
    shares: list[tuple[AllocItem, int, Decimal]],
    total: int,
) -> dict[str, int]:
    """Split ``total`` by ideal share, capped by each item's room."""
    floors: list[int] = []
    for _item, room, ideal in shares:
        floors.append(min(room, int(ideal)))
    left = total - sum(floors)
    order = sorted(
        range(len(shares)),
        key=lambda index: (
            -(shares[index][2] - Decimal(floors[index])),
            -shares[index][0].weight,
            shares[index][0].id,
        ),
    )
    extra = [0] * len(shares)
    for index in order:
        if left <= 0:
            break
        item, room, _ideal = shares[index]
        if floors[index] < room:
            extra[index] = 1
            left -= 1
    return {
        shares[index][0].id: floors[index] + extra[index] for index in range(len(shares))
    }


def allocate_units(items: list[AllocItem], capacity: int) -> dict[str, int]:
    """Give ``capacity`` search units to families or buckets.

    Caps at each item's available units and redistributes the unused remainder
    by the relative weights of items that still have room. Fit scores are not
    an input.
    """
    assigned = {item.id: 0 for item in items}
    demand = min(max(capacity, 0), sum(item.available for item in items))
    guard = 0
    while demand > 0 and guard <= len(items) + 1:
        guard += 1
        active = [
            item
            for item in items
            if item.weight > 0 and assigned[item.id] < item.available
        ]
        if not active:
            break
        weight_sum = sum((item.weight for item in active), Decimal("0"))
        shares: list[tuple[AllocItem, int, Decimal]] = []
        uncapped = True
        for item in active:
            room = item.available - assigned[item.id]
            ideal = Decimal(demand) * item.weight / weight_sum
            if ideal > Decimal(room):
                uncapped = False
            shares.append((item, room, min(Decimal(room), ideal)))
        if uncapped:
            grants = _largest_remainder(shares, demand)
            for item_id, grant in grants.items():
                assigned[item_id] += grant
            demand = 0
            break
        given = 0
        for item, room, capped in shares:
            grant = min(room, int(capped))
            assigned[item.id] += grant
            given += grant
        if given == 0:
            grants = _largest_remainder(
                [
                    (
                        item,
                        room,
                        Decimal(demand) * item.weight / weight_sum,
                    )
                    for item, room, _capped in shares
                ],
                demand,
            )
            for item_id, grant in grants.items():
                room = next(item.available for item in items if item.id == item_id)
                take = min(grant, room - assigned[item_id])
                assigned[item_id] += take
                demand -= take
            break
        demand -= given
    return assigned


def _enabled_queries(bucket: SearchBucket) -> list[str]:
    if not bucket.enabled:
        return []
    return list(bucket.queries)


def _load_yaml(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"Discovery config not found: {path}")
    with path.open(encoding="utf-8") as handle:
        data = yaml.safe_load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"Discovery YAML must be a mapping, got {type(data).__name__}")
    return data


@lru_cache
def load_discovery(path: str | None = None) -> DiscoveryConfig:
    discovery_path = Path(path) if path else DISCOVERY_PATH
    return DiscoveryConfig.model_validate(_load_yaml(discovery_path))


def reload_discovery(path: str | None = None) -> DiscoveryConfig:
    load_discovery.cache_clear()
    return load_discovery(path)


def enabled_query_texts(config: DiscoveryConfig | None = None) -> list[str]:
    """Enabled queries in family, then bucket, config order."""
    catalog = config or load_discovery()
    texts: list[str] = []
    for family in catalog.families:
        if not family.enabled:
            continue
        for bucket in family.buckets:
            texts.extend(_enabled_queries(bucket))
    return texts


def build_discovery_plan(
    targets: Any,
    *,
    capacity: int | None = None,
    config: DiscoveryConfig | None = None,
) -> DiscoveryPlan:
    """One-pass search plan. ``capacity`` is a count of query executions.

    ``None`` runs every enabled query once. The same inputs always return the
    same plan. Downstream fit scores are not consulted.
    """
    catalog = config or load_discovery()
    family_items: list[AllocItem] = []
    available_by_family: dict[str, int] = {}
    for family in catalog.families:
        if not family.enabled:
            available_by_family[family.id] = 0
            family_items.append(AllocItem(family.id, Decimal("0"), 0))
            continue
        available = sum(len(_enabled_queries(bucket)) for bucket in family.buckets)
        available_by_family[family.id] = available
        family_items.append(AllocItem(family.id, family.weight, available))

    total_available = sum(available_by_family.values())
    requested = total_available if capacity is None else max(capacity, 0)
    assigned = allocate_units(family_items, requested)

    enabled = [item for item in family_items if item.weight > 0 and item.available > 0]
    weight_sum = sum((item.weight for item in enabled), Decimal("0"))
    ideals = {
        item.id: (Decimal(requested) * item.weight / weight_sum if weight_sum else Decimal("0"))
        for item in family_items
    }

    bucket_assigned: dict[str, int] = {}
    searches: list[PlannedSearch] = []
    for family in catalog.families:
        slots = assigned.get(family.id, 0)
        buckets = [bucket for bucket in family.buckets if family.enabled and bucket.enabled]
        bucket_items = [
            AllocItem(
                bucket.id,
                Decimal(len(_enabled_queries(bucket))),
                len(_enabled_queries(bucket)),
            )
            for bucket in buckets
        ]
        bucket_grants = allocate_units(bucket_items, slots) if bucket_items else {}
        for bucket in family.buckets:
            grant = bucket_grants.get(bucket.id, 0)
            bucket_assigned[bucket.id] = grant
            if not family.enabled or not bucket.enabled:
                continue
            for query in _enabled_queries(bucket)[:grant]:
                searches.append(
                    PlannedSearch(
                        family_id=family.id,
                        bucket_id=bucket.id,
                        query=query,
                    )
                )

    enabled_sources = {source.id for source in catalog.sources if source.enabled}
    sites = tuple(
        site for site in getattr(targets.search, "sites", ()) if site in enabled_sources
    )
    families = tuple(
        FamilyAllocation(
            family_id=family.id,
            weight=family.weight,
            available=available_by_family.get(family.id, 0),
            ideal=ideals.get(family.id, Decimal("0")),
            assigned=assigned.get(family.id, 0),
        )
        for family in catalog.families
    )
    return DiscoveryPlan(
        capacity_requested=requested,
        capacity_assigned=sum(assigned.values()),
        families=families,
        bucket_assigned=bucket_assigned,
        searches=tuple(searches),
        jobspy_sites=sites,
        workday_enabled="workday" in enabled_sources,
    )


def log_discovery_plan(plan: DiscoveryPlan) -> None:
    """Secret-free summary of one search plan."""
    log.info(
        "discovery_plan",
        capacity_requested=plan.capacity_requested,
        capacity_assigned=plan.capacity_assigned,
        families=[
            {
                "id": family.family_id,
                "weight": str(family.weight),
                "available": family.available,
                "ideal": str(family.ideal),
                "assigned": family.assigned,
                "spillover": family.spillover,
            }
            for family in plan.families
        ],
        buckets=plan.bucket_assigned,
        searches=len(plan.searches),
        jobspy_sites=list(plan.jobspy_sites),
        workday_enabled=plan.workday_enabled,
    )
