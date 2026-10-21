---
type: community
cohesion: 0.08
members: 60
---

# test_discovery.py

**Cohesion:** 0.08 - loosely connected
**Members:** 60 nodes

## Members
- [[dot-_clean_phrases()]] - code - scraper/discovery.py
- [[dot-_quantize_weight()]] - code - scraper/discovery.py
- [[dot-_strip_required()]] - code - scraper/discovery.py
- [[dot-_strip_required()_1]] - code - scraper/discovery.py
- [[dot-_strip_required()_2]] - code - scraper/discovery.py
- [[dot-_validate_structure()]] - code - scraper/discovery.py
- [[AllocItem]] - code - scraper/discovery.py
- [[Any_47]] - code
- [[BaseModel_11]] - code
- [[Decimal]] - code
- [[DiscoveryConfig]] - code - scraper/discovery.py
- [[DiscoverySource]] - code - scraper/discovery.py
- [[Enabled queries in family, then bucket, config order.]] - rationale - scraper/discovery.py
- [[Give ``capacity`` search units to families or buckets. Caps at each item's…]] - rationale - scraper/discovery.py
- [[Load and validate targets.yaml. Cached after first successful load.]] - rationale - config/targets.py
- [[One-pass search plan. ``capacity`` is a count of query executions. ``None``…]] - rationale - scraper/discovery.py
- [[Path_51]] - code
- [[Phase 1 discovery plan families, allocation, migrated queries, provenance.]] - rationale - tests/test_discovery.py
- [[Primary queries, then title variants. Both run once when the bucket is on.]] - rationale - scraper/discovery.py
- [[Role-family discovery plan. Weights allocate search capacity, not fit scores.]] - rationale - scraper/discovery.py
- [[RoleFamily]] - code - scraper/discovery.py
- [[SearchBucket]] - code - scraper/discovery.py
- [[Split ``total`` by ideal share, capped by each item's room.]] - rationale - scraper/discovery.py
- [[Units this family received from another family's unused share. When the request…]] - rationale - scraper/discovery.py
- [[What to search. How a source runs stays in targets.yaml.]] - rationale - scraper/discovery.py
- [[_Sites]] - code - tests/test_discovery.py
- [[_Targets]] - code - tests/test_discovery.py
- [[_catalog()]] - code - tests/test_discovery.py
- [[_enabled_queries()]] - code - scraper/discovery.py
- [[_family_spillover()]] - code - scraper/discovery.py
- [[_items()]] - code - tests/test_discovery.py
- [[_largest_remainder()]] - code - scraper/discovery.py
- [[_load_yaml()_3]] - code - scraper/discovery.py
- [[allocate_units()]] - code - scraper/discovery.py
- [[build_discovery_plan()]] - code - scraper/discovery.py
- [[discovery.py]] - code - scraper/discovery.py
- [[enabled_query_texts()]] - code - scraper/discovery.py
- [[field_validator_3]] - code
- [[load_discovery()]] - code - scraper/discovery.py
- [[load_targets()]] - code - config/targets.py
- [[model_validator_1]] - code
- [[reload_discovery()]] - code - scraper/discovery.py
- [[test_allocation_is_deterministic()]] - code - tests/test_discovery.py
- [[test_allocation_never_exceeds_available_queries()]] - code - tests/test_discovery.py
- [[test_allocation_of_100_matches_weights()]] - code - tests/test_discovery.py
- [[test_buckets_belong_to_families_and_ids_are_unique()]] - code - tests/test_discovery.py
- [[test_catalog_weights_and_phrase_count_unchanged()]] - code - tests/test_coverage.py
- [[test_current_queries_were_migrated()]] - code - tests/test_discovery.py
- [[test_discovery.py]] - code - tests/test_discovery.py
- [[test_discovery_plan_includes_controlled_mba_vocabulary()]] - code - tests/test_recruiting_universe.py
- [[test_enabled_weights_must_sum_to_one()]] - code - tests/test_discovery.py
- [[test_family_shortage_reports_genuine_spillover()]] - code - tests/test_discovery.py
- [[test_full_plan_keeps_sources_separate_from_families()]] - code - tests/test_discovery.py
- [[test_global_shortage_is_not_spillover()]] - code - tests/test_discovery.py
- [[test_load_targets_defaults()]] - code - tests/test_targets.py
- [[test_phase2_vocabulary_is_unique_and_searched()]] - code - tests/test_discovery.py
- [[test_plan_diagnostics_are_deterministic()]] - code - tests/test_discovery.py
- [[test_role_families_and_weights()]] - code - tests/test_discovery.py
- [[test_spillover_when_other_has_two_units()]] - code - tests/test_discovery.py
- [[test_sufficient_capacity_has_no_spillover()]] - code - tests/test_discovery.py

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/test_discoverypy
SORT file.name ASC
```

## Connections to other communities
- 19 edges to [[_COMMUNITY_ingest.py]]
- 10 edges to [[_COMMUNITY_targets.py]]
- 8 edges to [[_COMMUNITY_pytest]]
- 7 edges to [[_COMMUNITY_Source]]
- 5 edges to [[_COMMUNITY_test_recruiting_universe.py]]
- 3 edges to [[_COMMUNITY_linkedin_jobspy.py]]
- 3 edges to [[_COMMUNITY_test_company_intelligence.py]]
- 2 edges to [[_COMMUNITY_upsert_job]]
- 2 edges to [[_COMMUNITY_Phase 1 discovery architecture]]
- 2 edges to [[_COMMUNITY_pathlib]]
- 1 edge to [[_COMMUNITY_session_scope]]
- 1 edge to [[_COMMUNITY_conftest.py]]
- 1 edge to [[_COMMUNITY_db.py]]
- 1 edge to [[_COMMUNITY_linkedin_people.py]]
- 1 edge to [[_COMMUNITY_test_resume.py]]
- 1 edge to [[_COMMUNITY_typing]]

## Top bridge nodes
- [[discovery.py]] - degree 35, connects to 10 communities
- [[test_discovery.py]] - degree 43, connects to 7 communities
- [[load_targets()]] - degree 22, connects to 6 communities
- [[build_discovery_plan()]] - degree 25, connects to 4 communities
- [[load_discovery()]] - degree 19, connects to 4 communities