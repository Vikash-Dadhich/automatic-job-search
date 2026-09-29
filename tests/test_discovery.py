"""Phase 1 discovery plan: families, allocation, migrated queries, provenance."""

from __future__ import annotations

from decimal import Decimal
from pathlib import Path

import pytest

from config.targets import load_targets
from core.db import Source, get_job_by_source_id, session_scope, upsert_job
from scraper.discovery import (
    AllocItem,
    DiscoveryConfig,
    DiscoverySource,
    RoleFamily,
    SearchBucket,
    allocate_units,
    build_discovery_plan,
    load_discovery,
)
from scraper.models import RawPosting, to_job

_MIGRATED = (
    "Product Manager Intern",
    "MBA Product Manager Intern",
    "Program Manager Intern",
    "Project Manager Intern",
    "Product Marketing Intern",
    "Strategy Intern",
    "Go-to-Market Intern",
    "Product Operations Intern",
    "Customer Success Intern",
    "Management Consultant Intern",
)

_WEIGHTS = {
    "PRODUCT_MANAGEMENT": Decimal("0.40"),
    "CONSULTING": Decimal("0.40"),
    "STRATEGY_TRANSFORMATION": Decimal("0.15"),
    "OTHER": Decimal("0.05"),
}


def _items() -> list[AllocItem]:
    return [
        AllocItem("PRODUCT_MANAGEMENT", Decimal("0.40"), 100),
        AllocItem("CONSULTING", Decimal("0.40"), 100),
        AllocItem("STRATEGY_TRANSFORMATION", Decimal("0.15"), 100),
        AllocItem("OTHER", Decimal("0.05"), 100),
    ]


def test_role_families_and_weights() -> None:
    config = load_discovery()
    found = {family.id: family for family in config.families}
    assert set(found) == set(_WEIGHTS)
    for family_id, weight in _WEIGHTS.items():
        assert found[family_id].enabled is True
        assert found[family_id].weight == weight
    enabled = [family.weight for family in config.families if family.enabled]
    assert sum(enabled, Decimal("0")) == Decimal("1.00")


def test_buckets_belong_to_families_and_ids_are_unique() -> None:
    config = load_discovery()
    seen: set[str] = set()
    for family in config.families:
        enabled = [bucket for bucket in family.buckets if bucket.enabled]
        assert enabled
        for bucket in family.buckets:
            assert bucket.id not in seen
            seen.add(bucket.id)
            assert bucket.queries


def test_current_queries_were_migrated() -> None:
    config = load_discovery()
    queries = {
        query
        for family in config.families
        for bucket in family.buckets
        if bucket.enabled
        for query in bucket.queries
    }
    assert set(_MIGRATED) <= queries


def test_allocation_of_100_matches_weights() -> None:
    assigned = allocate_units(_items(), 100)
    assert assigned == {
        "PRODUCT_MANAGEMENT": 40,
        "CONSULTING": 40,
        "STRATEGY_TRANSFORMATION": 15,
        "OTHER": 5,
    }
    assert sum(assigned.values()) == 100


def test_spillover_when_other_has_two_units() -> None:
    items = [
        AllocItem("PRODUCT_MANAGEMENT", Decimal("0.40"), 100),
        AllocItem("CONSULTING", Decimal("0.40"), 100),
        AllocItem("STRATEGY_TRANSFORMATION", Decimal("0.15"), 100),
        AllocItem("OTHER", Decimal("0.05"), 2),
    ]
    assigned = allocate_units(items, 100)
    assert assigned["OTHER"] == 2
    assert assigned["PRODUCT_MANAGEMENT"] == 41
    assert assigned["CONSULTING"] == 41
    assert assigned["STRATEGY_TRANSFORMATION"] == 16
    assert sum(assigned.values()) == 100
    for item in items:
        assert assigned[item.id] <= item.available


def test_allocation_is_deterministic() -> None:
    items = _items()
    assert allocate_units(items, 100) == allocate_units(items, 100)
    assert allocate_units(items, 37) == allocate_units(list(reversed(items)), 37)


def test_allocation_never_exceeds_available_queries() -> None:
    items = [
        AllocItem("PRODUCT_MANAGEMENT", Decimal("0.40"), 5),
        AllocItem("CONSULTING", Decimal("0.40"), 5),
        AllocItem("STRATEGY_TRANSFORMATION", Decimal("0.15"), 5),
        AllocItem("OTHER", Decimal("0.05"), 4),
    ]
    assigned = allocate_units(items, 1000)
    assert assigned == {item.id: item.available for item in items}
    assert sum(assigned.values()) == 19


def test_full_plan_keeps_sources_separate_from_families() -> None:
    load_targets.cache_clear()
    targets = load_targets()
    plan = build_discovery_plan(targets)
    assert plan.jobspy_sites == ("linkedin", "indeed", "google", "zip_recruiter")
    assert plan.workday_enabled is True
    queries = [search.query for search in plan.searches]
    assert set(_MIGRATED) <= set(queries)
    assert len(queries) == len(set(queries))
    for search in plan.searches:
        assert search.family_id
        assert search.bucket_id
        assert not hasattr(search, "sites")
    assert "Product Manager Intern" in targets.search.terms
    load_targets.cache_clear()


def test_enabled_weights_must_sum_to_one() -> None:
    bucket = SearchBucket(id="PM_CORE", name="PM", queries=["Product Manager Intern"])
    family = RoleFamily(
        id="PRODUCT_MANAGEMENT",
        name="Product Management",
        weight=Decimal("0.50"),
        buckets=[bucket],
    )
    with pytest.raises(ValueError, match="1.00"):
        DiscoveryConfig(
            families=[family],
            sources=[DiscoverySource(id="linkedin", name="LinkedIn")],
        )


async def test_discovered_job_keeps_provenance(db_ready: Path) -> None:
    del db_ready
    posting = RawPosting(
        source=Source.linkedin,
        external_id="phase1-provenance",
        title="Product Strategy Intern",
        company="GoodCo",
        location="Remote",
        url="https://example.com/phase1",
        description_clean="Summer internship on the product strategy team.",
        discovery_family="PRODUCT_MANAGEMENT",
        discovery_bucket="PRODUCT_STRATEGY",
        discovery_query="Product Strategy Intern",
    )
    async with session_scope() as session:
        await upsert_job(session, to_job(posting))
    async with session_scope() as session:
        saved = await get_job_by_source_id(session, Source.linkedin, "phase1-provenance")
    assert saved is not None
    assert saved.source == Source.linkedin
    assert saved.discovery_family == "PRODUCT_MANAGEMENT"
    assert saved.discovery_bucket == "PRODUCT_STRATEGY"
    assert saved.discovery_query == "Product Strategy Intern"
