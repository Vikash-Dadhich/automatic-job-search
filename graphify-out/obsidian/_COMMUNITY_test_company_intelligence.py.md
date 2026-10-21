---
type: community
cohesion: 0.25
members: 23
---

# test_company_intelligence.py

**Cohesion:** 0.25 - loosely connected
**Members:** 23 nodes

## Members
- [[dot-__init__()_14]] - code - tests/test_company_intelligence.py
- [[FakeProvider]] - code - tests/test_company_intelligence.py
- [[Find or create factual intelligence. Provider errors stay on the company row.]] - rationale - scorer/company_intelligence.py
- [[Path_17]] - code
- [[Phase 8 company facts. They do not change fit, weight, tier, status, or…]] - rationale - tests/test_company_intelligence.py
- [[Point the job at a company record without changing score, weight, or status.]] - rationale - scorer/company_intelligence.py
- [[_job()_4]] - code - tests/test_company_intelligence.py
- [[_posting()_4]] - code - tests/test_company_intelligence.py
- [[attach_company_intelligence()]] - code - scorer/company_intelligence.py
- [[resolve_company()]] - code - scorer/company_intelligence.py
- [[test_ambiguous_names_stay_separate()]] - code - tests/test_company_intelligence.py
- [[test_company_facts_do_not_change_scoring_signals()]] - code - tests/test_company_intelligence.py
- [[test_company_intelligence.py]] - code - tests/test_company_intelligence.py
- [[test_company_sources_accumulate_and_a_failed_refresh_keeps_them()]] - code - tests/test_company_intelligence.py
- [[test_complete_record_and_ignored_claims()]] - code - tests/test_company_intelligence.py
- [[test_cooldown_set_is_unchanged()]] - code - tests/test_company_intelligence.py
- [[test_explicit_refresh_calls_the_provider_again()]] - code - tests/test_company_intelligence.py
- [[test_persisted_source_type_matches_the_caller()]] - code - tests/test_company_intelligence.py
- [[test_provider_failures_do_not_change_the_job()]] - code - tests/test_company_intelligence.py
- [[test_same_company_is_reused_without_merging_jobs()]] - code - tests/test_company_intelligence.py
- [[test_source_grounded_partial_record()]] - code - tests/test_company_intelligence.py
- [[test_sparse_refresh_does_not_erase_known_facts()]] - code - tests/test_company_intelligence.py
- [[test_unknown_without_a_source_stays_null()]] - code - tests/test_company_intelligence.py

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/test_company_intelligencepy
SORT file.name ASC
```

## Connections to other communities
- 24 edges to [[_COMMUNITY_company_intelligence.py]]
- 20 edges to [[_COMMUNITY_session_scope]]
- 15 edges to [[_COMMUNITY_Source]]
- 12 edges to [[_COMMUNITY_test_company_intelligence_v2.py]]
- 9 edges to [[_COMMUNITY_Tier]]
- 9 edges to [[_COMMUNITY_Any]]
- 5 edges to [[_COMMUNITY_upsert_job]]
- 4 edges to [[_COMMUNITY_Job]]
- 4 edges to [[_COMMUNITY_HttpCompanyIntelProvider]]
- 4 edges to [[_COMMUNITY_pytest]]
- 3 edges to [[_COMMUNITY_test_discovery.py]]
- 2 edges to [[_COMMUNITY_test_doctor.py]]
- 2 edges to [[_COMMUNITY_linkedin_jobspy.py]]
- 1 edge to [[_COMMUNITY_ingest.py]]
- 1 edge to [[_COMMUNITY_db.py]]
- 1 edge to [[_COMMUNITY_scorerengine.py]]
- 1 edge to [[_COMMUNITY_baseline.py]]
- 1 edge to [[_COMMUNITY_pathlib]]

## Top bridge nodes
- [[test_company_intelligence.py]] - degree 59, connects to 17 communities
- [[attach_company_intelligence()]] - degree 17, connects to 5 communities
- [[_job()_4]] - degree 12, connects to 5 communities
- [[test_company_facts_do_not_change_scoring_signals()]] - degree 12, connects to 4 communities
- [[test_same_company_is_reused_without_merging_jobs()]] - degree 9, connects to 4 communities