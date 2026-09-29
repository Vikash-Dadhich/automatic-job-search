"""Discovery coverage metrics. No live job boards."""

from __future__ import annotations

from decimal import Decimal

from config.targets import load_targets
from scraper.coverage import (
    SearchStatus,
    build_coverage_report,
    observe_search,
    result_identity,
)
from scraper.discovery import (
    DiscoveryPlan,
    FamilyAllocation,
    PlannedSearch,
    build_discovery_plan,
    enabled_query_texts,
    load_discovery,
)

_WEIGHTS = {
    "PRODUCT_MANAGEMENT": Decimal("0.40"),
    "CONSULTING": Decimal("0.40"),
    "STRATEGY_TRANSFORMATION": Decimal("0.15"),
    "OTHER": Decimal("0.05"),
}


def _plan(*queries: tuple[str, str, str], sites: tuple[str, ...] = ("linkedin",)) -> DiscoveryPlan:
    searches = tuple(
        PlannedSearch(family_id=family, bucket_id=bucket, query=query)
        for family, bucket, query in queries
    )
    families = []
    seen: set[str] = set()
    for family, _bucket, _query in queries:
        if family in seen:
            continue
        seen.add(family)
        families.append(
            FamilyAllocation(
                family_id=family,
                weight=Decimal("1.00"),
                available=1,
                ideal=Decimal("1"),
                assigned=1,
                spillover=0,
            )
        )
    return DiscoveryPlan(
        capacity_requested=len(searches),
        capacity_usable=len(searches),
        capacity_assigned=len(searches),
        families=tuple(families),
        bucket_assigned={},
        searches=searches,
        jobspy_sites=sites,
        workday_enabled=False,
    )


def test_catalog_weights_and_phrase_count_unchanged() -> None:
    config = load_discovery()
    found = {family.id: family.weight for family in config.families}
    assert found == _WEIGHTS
    texts = enabled_query_texts(config)
    assert len(texts) == 111
    assert "MBA Summer Associate" in texts
    assert "Marketing Intern" in texts
    assert "Technology Strategy Intern" in texts
    variants = [
        variant
        for family in config.families
        for bucket in family.buckets
        for variant in bucket.title_variants
    ]
    assert variants
    assert "Product Lead Intern" in variants


def test_results_empty_and_failed_stay_distinct() -> None:
    plan = _plan(("PRODUCT_MANAGEMENT", "PM_CORE", "Product Manager Intern"))
    observations = [
        observe_search(
            family_id="PRODUCT_MANAGEMENT",
            bucket_id="PM_CORE",
            query="Product Manager Intern",
            source="linkedin",
            hits=("linkedin:1",),
        ),
        observe_search(
            family_id="PRODUCT_MANAGEMENT",
            bucket_id="PM_CORE",
            query="Other",
            source="linkedin",
            hits=(),
        ),
        observe_search(
            family_id="PRODUCT_MANAGEMENT",
            bucket_id="PM_CORE",
            query="Broken",
            source="linkedin",
            failed=True,
            error="timeout",
        ),
    ]
    # Only the first query is planned; the other two are extra executions.
    report = build_coverage_report(plan, observations)
    by_query = {row.query: row for row in report.queries}
    assert by_query["Product Manager Intern"].status is SearchStatus.results
    assert by_query["Other"].status is SearchStatus.empty
    assert by_query["Broken"].status is SearchStatus.failed
    assert report.with_results == 1
    assert report.zero_result == 1
    assert report.failed == 1
    assert report.zero_result_rate == 0.5
    assert by_query["Broken"].error == "timeout"


def test_incremental_unique_and_duplicate_follow_plan_order() -> None:
    plan = _plan(
        ("PRODUCT_MANAGEMENT", "PM_CORE", "First"),
        ("CONSULTING", "MANAGEMENT_CONSULTING", "Second"),
        ("PRODUCT_MANAGEMENT", "PM_CORE", "Third"),
        sites=("linkedin", "indeed"),
    )
    # Input order is reversed on purpose. Metrics follow the plan.
    observations = [
        observe_search(
            family_id="PRODUCT_MANAGEMENT",
            bucket_id="PM_CORE",
            query="Third",
            source="linkedin",
            hits=("linkedin:a",),
        ),
        observe_search(
            family_id="CONSULTING",
            bucket_id="MANAGEMENT_CONSULTING",
            query="Second",
            source="linkedin",
            hits=("linkedin:a", "linkedin:b"),
        ),
        observe_search(
            family_id="PRODUCT_MANAGEMENT",
            bucket_id="PM_CORE",
            query="First",
            source="linkedin",
            hits=("linkedin:a", "linkedin:a"),
        ),
    ]
    report = build_coverage_report(plan, observations)
    linkedin = [row for row in report.queries if row.source == "linkedin" and row.query != ""]
    by_query = {row.query: row for row in linkedin}
    assert by_query["First"].raw == 2
    assert by_query["First"].unique == 1
    assert by_query["First"].incremental == 1
    assert by_query["First"].duplicate == 1
    assert by_query["Second"].unique == 2
    assert by_query["Second"].incremental == 1
    assert by_query["Second"].duplicate == 0
    assert by_query["Third"].incremental == 0
    assert report.raw == 5
    assert report.unique == 2
    assert report.duplicate == 3
    assert report.searches_with_incremental == 2
    families = {row.name: row for row in report.families}
    assert families["PRODUCT_MANAGEMENT"].incremental == 1
    assert families["CONSULTING"].incremental == 1
    assert sum(row.incremental for row in report.families) == report.unique


def test_query_duplicate_counts_repeats_inside_the_search() -> None:
    plan = _plan(
        ("PRODUCT_MANAGEMENT", "PM_CORE", "Earlier"),
        ("CONSULTING", "MANAGEMENT_CONSULTING", "Repeated"),
        ("CONSULTING", "MANAGEMENT_CONSULTING", "Repeated with copy"),
    )
    observations = [
        observe_search(
            family_id="PRODUCT_MANAGEMENT",
            bucket_id="PM_CORE",
            query="Earlier",
            source="linkedin",
            hits=("linkedin:job1", "linkedin:job2"),
        ),
        observe_search(
            family_id="CONSULTING",
            bucket_id="MANAGEMENT_CONSULTING",
            query="Repeated",
            source="linkedin",
            hits=("linkedin:job1", "linkedin:job2"),
        ),
        observe_search(
            family_id="CONSULTING",
            bucket_id="MANAGEMENT_CONSULTING",
            query="Repeated with copy",
            source="linkedin",
            hits=("linkedin:job1", "linkedin:job2", "linkedin:job2"),
        ),
    ]
    report = build_coverage_report(plan, observations)
    by_query = {row.query: row for row in report.queries if row.source == "linkedin"}
    repeated = by_query["Repeated"]
    assert repeated.raw == 2
    assert repeated.unique == 2
    assert repeated.incremental == 0
    assert repeated.duplicate == 0
    copied = by_query["Repeated with copy"]
    assert copied.raw == 3
    assert copied.unique == 2
    assert copied.incremental == 0
    assert copied.duplicate == 1


def test_same_external_id_on_two_sources_stays_two_discoveries() -> None:
    plan = _plan(
        ("PRODUCT_MANAGEMENT", "PM_CORE", "Product Manager Intern"),
        sites=("linkedin", "indeed"),
    )
    observations = [
        observe_search(
            family_id="PRODUCT_MANAGEMENT",
            bucket_id="PM_CORE",
            query="Product Manager Intern",
            source="linkedin",
            hits=(result_identity("linkedin", "same-job"),),
        ),
        observe_search(
            family_id="PRODUCT_MANAGEMENT",
            bucket_id="PM_CORE",
            query="Product Manager Intern",
            source="indeed",
            hits=(result_identity("indeed", "same-job"),),
        ),
    ]
    report = build_coverage_report(plan, observations)
    assert report.identity_scope == "source_and_external_id"
    assert report.raw == 2
    assert report.unique == 2
    assert report.duplicate == 0
    sources = {row.name: row.incremental for row in report.sources}
    assert sources == {"linkedin": 1, "indeed": 1}


def test_missing_identity_is_raw_but_not_unique() -> None:
    plan = _plan(("OTHER", "OTHER_ADJACENT_MBA_ROLES", "Customer Success Intern"))
    observations = [
        observe_search(
            family_id="OTHER",
            bucket_id="OTHER_ADJACENT_MBA_ROLES",
            query="Customer Success Intern",
            source="linkedin",
            hits=(None, None),
        )
    ]
    report = build_coverage_report(plan, observations)
    row = next(item for item in report.queries if item.status is SearchStatus.results)
    assert row.raw == 2
    assert row.unique == 0
    assert row.incremental == 0
    assert row.unidentified == 2
    assert report.unique == 0
    assert report.unidentified == 2
    assert result_identity("linkedin", "  ") is None


def test_coverage_is_deterministic() -> None:
    plan = _plan(
        ("PRODUCT_MANAGEMENT", "PM_CORE", "One"),
        ("CONSULTING", "MANAGEMENT_CONSULTING", "Two"),
    )
    observations = [
        observe_search(
            family_id="CONSULTING",
            bucket_id="MANAGEMENT_CONSULTING",
            query="Two",
            source="linkedin",
            hits=("linkedin:2",),
        ),
        observe_search(
            family_id="PRODUCT_MANAGEMENT",
            bucket_id="PM_CORE",
            query="One",
            source="linkedin",
            hits=("linkedin:1",),
        ),
    ]
    first = build_coverage_report(plan, observations)
    second = build_coverage_report(plan, list(reversed(observations)))
    assert first == second


def test_full_plan_and_capacity_limit_change_only_what_was_planned() -> None:
    load_targets.cache_clear()
    targets = load_targets()
    full = build_discovery_plan(targets)
    limited = build_discovery_plan(targets, capacity=4)
    full_report = build_coverage_report(full, [], workday_tenants=("NVIDIA",))
    limited_report = build_coverage_report(limited, [])
    assert full_report.searches_planned == len(full.searches) * (len(full.jobspy_sites) + 1)
    assert limited_report.searches_planned == len(limited.searches) * len(limited.jobspy_sites)
    assert limited_report.searches_planned < full_report.searches_planned
    assert full_report.not_executed == full_report.searches_planned
    assert full_report.zero_result == 0
    assert full_report.failed == 0
    assert {row.name for row in full_report.families} >= set(_WEIGHTS)
    load_targets.cache_clear()


def test_bucket_and_source_rollups() -> None:
    plan = _plan(
        ("STRATEGY_TRANSFORMATION", "GTM_STRATEGY", "GTM Strategy Intern"),
        ("STRATEGY_TRANSFORMATION", "CORPORATE_STRATEGY", "Strategy Intern"),
        sites=("linkedin", "google"),
    )
    observations = [
        observe_search(
            family_id="STRATEGY_TRANSFORMATION",
            bucket_id="GTM_STRATEGY",
            query="GTM Strategy Intern",
            source="linkedin",
            hits=("linkedin:1",),
        ),
        observe_search(
            family_id="STRATEGY_TRANSFORMATION",
            bucket_id="CORPORATE_STRATEGY",
            query="Strategy Intern",
            source="google",
            failed=True,
            error="blocked",
        ),
    ]
    report = build_coverage_report(plan, observations)
    buckets = {row.name: row for row in report.buckets}
    assert buckets["GTM_STRATEGY"].with_results == 1
    assert buckets["GTM_STRATEGY"].incremental == 1
    assert buckets["CORPORATE_STRATEGY"].failed == 1
    assert buckets["CORPORATE_STRATEGY"].zero_result == 0
    sources = {row.name: row for row in report.sources}
    assert sources["linkedin"].raw == 1
    assert sources["google"].failed == 1
