---
source_file: "scraper/coverage.py"
type: "code"
community: "ingest.py"
location: "L244"
tags:
  - graphify/code
  - graphify/EXTRACTED
  - community/ingestpy
---

# build_coverage_report()

## Connections
- [[Aggregate a run. Incremental counts follow plan order, not finish order.]] - `rationale_for` [EXTRACTED]
- [[CoverageReport]] - `calls` [EXTRACTED]
- [[DiscoveryPlan]] - `uses` [INFERRED]
- [[QueryMetrics]] - `calls` [EXTRACTED]
- [[SearchObservation]] - `references` [EXTRACTED]
- [[_Tally]] - `calls` [EXTRACTED]
- [[_attach_coverage()]] - `calls` [EXTRACTED]
- [[_planned_slots()]] - `calls` [EXTRACTED]
- [[_slot_key()]] - `calls` [EXTRACTED]
- [[add_planned()]] - `contains` [EXTRACTED]
- [[coverage.py]] - `contains` [EXTRACTED]
- [[group_for()]] - `contains` [EXTRACTED]
- [[ingest.py]] - `imports` [EXTRACTED]
- [[test_bucket_and_source_rollups()]] - `calls` [EXTRACTED]
- [[test_coverage.py]] - `imports` [EXTRACTED]
- [[test_coverage_is_deterministic()]] - `calls` [EXTRACTED]
- [[test_full_plan_and_capacity_limit_change_only_what_was_planned()]] - `calls` [EXTRACTED]
- [[test_incremental_unique_and_duplicate_follow_plan_order()]] - `calls` [EXTRACTED]
- [[test_missing_identity_is_raw_but_not_unique()]] - `calls` [EXTRACTED]
- [[test_query_duplicate_counts_repeats_inside_the_search()]] - `calls` [EXTRACTED]
- [[test_results_empty_and_failed_stay_distinct()]] - `calls` [EXTRACTED]
- [[test_same_external_id_on_two_sources_stays_two_discoveries()]] - `calls` [EXTRACTED]

#graphify/code #graphify/EXTRACTED #community/ingestpy