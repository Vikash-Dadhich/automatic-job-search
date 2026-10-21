---
type: community
cohesion: 0.08
members: 58
---

# ingest.py

**Cohesion:** 0.08 - loosely connected
**Members:** 58 nodes

## Members
- [[dot-__post_init__()]] - code - scraper/coverage.py
- [[dot-finish()]] - code - scraper/coverage.py
- [[dot-identities()]] - code - scraper/coverage.py
- [[dot-raw_count()]] - code - scraper/coverage.py
- [[dot-spillover()]] - code - scraper/discovery.py
- [[dot-to_dict()]] - code - scraper/coverage.py
- [[dot-unidentified_count()]] - code - scraper/coverage.py
- [[Aggregate a run. Incremental counts follow plan order, not finish order.]] - rationale - scraper/coverage.py
- [[Aggregate coverage only. Query rows stay in the JSON file.]] - rationale - scraper/coverage.py
- [[Build an observation. Failure stays failure even when nothing came back.]] - rationale - scraper/coverage.py
- [[CoverageReport]] - code - scraper/coverage.py
- [[Database identity. Blank ids are raw results we cannot count as unique.]] - rationale - scraper/coverage.py
- [[Discovery coverage diagnostics. These measure searches, not candidate fit.…]] - rationale - scraper/coverage.py
- [[Discovery coverage metrics. No live job boards.]] - rationale - tests/test_coverage.py
- [[DiscoveryPlan]] - code - scraper/discovery.py
- [[FamilyAllocation]] - code - scraper/discovery.py
- [[GroupMetrics]] - code - scraper/coverage.py
- [[IngestSummary]] - code - scraper/ingest.py
- [[Ingestion orchestrator fetch → clean → filter → upsert.]] - rationale - scraper/ingest.py
- [[Internal discovery coverage. Not a share of the internship market.]] - rationale - scraper/coverage.py
- [[Mark planned searches that never reported in as failures, not empty results.]] - rationale - scraper/coverage.py
- [[One executed search on one source. Hits keep result order.]] - rationale - scraper/coverage.py
- [[Path_12]] - code
- [[QueryMetrics]] - code - scraper/coverage.py
- [[SearchObservation]] - code - scraper/coverage.py
- [[SearchStatus]] - code - scraper/coverage.py
- [[Secret-free summary of one search plan.]] - rationale - scraper/discovery.py
- [[StrEnum_1]] - code
- [[Units redistributed because a family could not fill its share. A request larger…]] - rationale - scraper/discovery.py
- [[_Slot]] - code - scraper/coverage.py
- [[_Tally]] - code - scraper/coverage.py
- [[_attach_coverage()]] - code - scraper/ingest.py
- [[_jsonable()]] - code - scraper/coverage.py
- [[_mark_source_failed()]] - code - scraper/ingest.py
- [[_plan()]] - code - tests/test_coverage.py
- [[_planned_slots()]] - code - scraper/coverage.py
- [[_slot_key()]] - code - scraper/coverage.py
- [[add_planned()]] - code - scraper/coverage.py
- [[build_coverage_report()]] - code - scraper/coverage.py
- [[coverage.py]] - code - scraper/coverage.py
- [[fail_unrecorded()]] - code - scraper/coverage.py
- [[group_for()]] - code - scraper/coverage.py
- [[ingest.py]] - code - scraper/ingest.py
- [[log_coverage()]] - code - scraper/coverage.py
- [[log_discovery_plan()]] - code - scraper/discovery.py
- [[observe_search()]] - code - scraper/coverage.py
- [[result_identity()]] - code - scraper/coverage.py
- [[structlog]] - concept
- [[test_bucket_and_source_rollups()]] - code - tests/test_coverage.py
- [[test_coverage.py]] - code - tests/test_coverage.py
- [[test_coverage_is_deterministic()]] - code - tests/test_coverage.py
- [[test_full_plan_and_capacity_limit_change_only_what_was_planned()]] - code - tests/test_coverage.py
- [[test_incremental_unique_and_duplicate_follow_plan_order()]] - code - tests/test_coverage.py
- [[test_missing_identity_is_raw_but_not_unique()]] - code - tests/test_coverage.py
- [[test_query_duplicate_counts_repeats_inside_the_search()]] - code - tests/test_coverage.py
- [[test_results_empty_and_failed_stay_distinct()]] - code - tests/test_coverage.py
- [[test_same_external_id_on_two_sources_stays_two_discoveries()]] - code - tests/test_coverage.py
- [[write_coverage()]] - code - scraper/coverage.py

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/ingestpy
SORT file.name ASC
```

## Connections to other communities
- 19 edges to [[_COMMUNITY_test_discovery.py]]
- 16 edges to [[_COMMUNITY_linkedin_jobspy.py]]
- 14 edges to [[_COMMUNITY_workday_rest.py]]
- 11 edges to [[_COMMUNITY_Source]]
- 3 edges to [[_COMMUNITY_structured_jd.py]]
- 3 edges to [[_COMMUNITY_targets.py]]
- 3 edges to [[_COMMUNITY_diff.py]]
- 3 edges to [[_COMMUNITY_upsert_job]]
- 3 edges to [[_COMMUNITY_company_intelligence.py]]
- 3 edges to [[_COMMUNITY_browser.py]]
- 3 edges to [[_COMMUNITY_pipeline.py]]
- 2 edges to [[_COMMUNITY_Profile]]
- 2 edges to [[_COMMUNITY_session_scope]]
- 2 edges to [[_COMMUNITY_Job]]
- 2 edges to [[_COMMUNITY_json]]
- 2 edges to [[_COMMUNITY_test_structured_jd.py]]
- 2 edges to [[_COMMUNITY_suggest.py]]
- 2 edges to [[_COMMUNITY_test_eligibility.py]]
- 2 edges to [[_COMMUNITY_db.py]]
- 2 edges to [[_COMMUNITY_main.py]]
- 2 edges to [[_COMMUNITY_test_role_classify.py]]
- 2 edges to [[_COMMUNITY_handlers.py]]
- 2 edges to [[_COMMUNITY_asyncio]]
- 2 edges to [[_COMMUNITY_eligibility.py]]
- 2 edges to [[_COMMUNITY_test_resume.py]]
- 2 edges to [[_COMMUNITY_skills.py]]
- 2 edges to [[_COMMUNITY_pathlib]]
- 2 edges to [[_COMMUNITY_typing]]
- 2 edges to [[_COMMUNITY_clients.py]]
- 2 edges to [[_COMMUNITY_workday.py]]
- 2 edges to [[_COMMUNITY_test_scorer.py]]
- 2 edges to [[_COMMUNITY_scorerengine.py]]
- 1 edge to [[_COMMUNITY_HttpCompanyIntelProvider]]
- 1 edge to [[_COMMUNITY_LLMClient]]
- 1 edge to [[_COMMUNITY_classify_role]]
- 1 edge to [[_COMMUNITY_test_company_intelligence.py]]
- 1 edge to [[_COMMUNITY_bot__init__.py]]
- 1 edge to [[_COMMUNITY_linkedin_people.py]]
- 1 edge to [[_COMMUNITY_alerts.py]]
- 1 edge to [[_COMMUNITY_filters.py]]
- 1 edge to [[_COMMUNITY_profile.py]]
- 1 edge to [[_COMMUNITY_runner.py]]
- 1 edge to [[_COMMUNITY_test_pacing.py]]
- 1 edge to [[_COMMUNITY_scheduler.py]]
- 1 edge to [[_COMMUNITY_builder.py]]
- 1 edge to [[_COMMUNITY_get_settings]]
- 1 edge to [[_COMMUNITY_re]]
- 1 edge to [[_COMMUNITY_review.py]]
- 1 edge to [[_COMMUNITY_baseline.py]]
- 1 edge to [[_COMMUNITY_test_monitoring.py]]
- 1 edge to [[_COMMUNITY_tracker.py]]
- 1 edge to [[_COMMUNITY_vault.py]]
- 1 edge to [[_COMMUNITY_benchmarkengine.py]]

## Top bridge nodes
- [[structlog]] - degree 45, connects to 36 communities
- [[ingest.py]] - degree 65, connects to 28 communities
- [[coverage.py]] - degree 29, connects to 8 communities
- [[test_coverage.py]] - degree 26, connects to 3 communities
- [[SearchObservation]] - degree 19, connects to 3 communities