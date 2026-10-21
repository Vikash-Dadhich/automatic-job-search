---
type: community
cohesion: 0.10
members: 46
---

# Source

**Cohesion:** 0.10 - loosely connected
**Members:** 46 nodes

## Members
- [[Async tests for Job mapping, upsert idempotency, and ingest noop.]] - rationale - tests/test_db_ingest.py
- [[BaseModel_7]] - code
- [[Map a RawPosting to a Job row, computing content_hash.]] - rationale - scraper/models.py
- [[MonkeyPatch_23]] - code
- [[MonkeyPatch_24]] - code
- [[MonkeyPatch_25]] - code
- [[Normalized intermediate posting model and Job mapping.]] - rationale - scraper/models.py
- [[One posting, one job. Uncertain matches stay separate.]] - rationale - tests/test_job_identity.py
- [[Path_42]] - code
- [[Path_43]] - code
- [[Path_44]] - code
- [[Path_45]] - code
- [[RawPosting]] - code - scraper/models.py
- [[Run one full discovery cycle and persist results. ``search_capacity`` is how…]] - rationale - scraper/ingest.py
- [[Source]] - code - core/db.py
- [[Source-agnostic posting produced by scrapers before DB persistence.]] - rationale - scraper/models.py
- [[_dedupe()]] - code - scraper/ingest.py
- [[_posting()_6]] - code - tests/test_db_ingest.py
- [[_posting()_7]] - code - tests/test_job_identity.py
- [[boom()_4]] - code - tests/test_company_intelligence_v2.py
- [[boom()_5]] - code - tests/test_eligibility.py
- [[boom()_6]] - code - tests/test_structured_jd.py
- [[hash_fallback()]] - code - scraper/models.py
- [[models.py]] - code - scraper/models.py
- [[one_posting()]] - code - tests/test_company_intelligence_v2.py
- [[one_posting()_1]] - code - tests/test_eligibility.py
- [[one_posting()_2]] - code - tests/test_structured_jd.py
- [[run_ingestion()]] - code - scraper/ingest.py
- [[test_company_enrichment_failure_does_not_stop_ingestion()]] - code - tests/test_company_intelligence_v2.py
- [[test_company_facts_do_not_change_job_decisions()]] - code - tests/test_company_intelligence_v2.py
- [[test_db_ingest.py]] - code - tests/test_db_ingest.py
- [[test_discovered_job_keeps_provenance()]] - code - tests/test_discovery.py
- [[test_homepage_query_does_not_merge_across_sources()]] - code - tests/test_job_identity.py
- [[test_internship_signal_matches_the_existing_gate()]] - code - tests/test_eligibility.py
- [[test_job_identity.py]] - code - tests/test_job_identity.py
- [[test_material_description_change_still_clears_fit()]] - code - tests/test_job_identity.py
- [[test_provider_failure_does_not_break_ingestion()]] - code - tests/test_eligibility.py
- [[test_run_ingestion_noop()]] - code - tests/test_db_ingest.py
- [[test_same_place_and_text_can_merge_without_using_fit()]] - code - tests/test_job_identity.py
- [[test_same_source_identity_and_cross_source_url()]] - code - tests/test_job_identity.py
- [[test_structured_jd_failure_does_not_stop_ingestion()]] - code - tests/test_structured_jd.py
- [[test_to_job_maps_fields_and_hash()]] - code - tests/test_db_ingest.py
- [[test_to_job_stamps_workday_tenant_from_linkedin_url()]] - code - tests/test_apply_url.py
- [[test_upsert_idempotent_and_status_refresh()]] - code - tests/test_db_ingest.py
- [[test_weak_similarity_does_not_merge()]] - code - tests/test_job_identity.py
- [[to_job()]] - code - scraper/models.py

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/Source
SORT file.name ASC
```

## Connections to other communities
- 32 edges to [[_COMMUNITY_upsert_job]]
- 30 edges to [[_COMMUNITY_session_scope]]
- 15 edges to [[_COMMUNITY_filters.py]]
- 15 edges to [[_COMMUNITY_test_company_intelligence.py]]
- 15 edges to [[_COMMUNITY_textclean.py]]
- 14 edges to [[_COMMUNITY_test_eligibility.py]]
- 13 edges to [[_COMMUNITY_Profile]]
- 11 edges to [[_COMMUNITY_ingest.py]]
- 11 edges to [[_COMMUNITY_workday_rest.py]]
- 11 edges to [[_COMMUNITY_test_role_classify.py]]
- 10 edges to [[_COMMUNITY_classify_role]]
- 9 edges to [[_COMMUNITY_test_recruiting_universe.py]]
- 9 edges to [[_COMMUNITY_pytest]]
- 8 edges to [[_COMMUNITY_test_company_intelligence_v2.py]]
- 8 edges to [[_COMMUNITY_linkedin_jobspy.py]]
- 8 edges to [[_COMMUNITY_test_structured_jd.py]]
- 7 edges to [[_COMMUNITY_test_apply_url.py]]
- 7 edges to [[_COMMUNITY_test_discovery.py]]
- 6 edges to [[_COMMUNITY_test_application_portfolio.py]]
- 6 edges to [[_COMMUNITY_re]]
- 6 edges to [[_COMMUNITY_baseline.py]]
- 6 edges to [[_COMMUNITY_discovery_recall.py]]
- 6 edges to [[_COMMUNITY_pathlib]]
- 6 edges to [[_COMMUNITY_Job]]
- 6 edges to [[_COMMUNITY_db.py]]
- 5 edges to [[_COMMUNITY_prerank.py]]
- 5 edges to [[_COMMUNITY_test_application_tracker.py]]
- 5 edges to [[_COMMUNITY_get_settings]]
- 5 edges to [[_COMMUNITY_test_phase0_baseline.py]]
- 5 edges to [[_COMMUNITY_WorkdaySubmitter]]
- 5 edges to [[_COMMUNITY_test_vector_recovery.py]]
- 4 edges to [[_COMMUNITY_alerts.py]]
- 4 edges to [[_COMMUNITY_profile.py]]
- 4 edges to [[_COMMUNITY_review.py]]
- 4 edges to [[_COMMUNITY_Tier]]
- 4 edges to [[_COMMUNITY_test_scorer.py]]
- 4 edges to [[_COMMUNITY_suggest.py]]
- 4 edges to [[_COMMUNITY_send_prep_pack]]
- 3 edges to [[_COMMUNITY_company_intelligence.py]]
- 3 edges to [[_COMMUNITY_tracker.py]]
- 3 edges to [[_COMMUNITY_test_career_intelligence.py]]
- 3 edges to [[_COMMUNITY_test_feedback.py]]
- 3 edges to [[_COMMUNITY_test_fit.py]]
- 3 edges to [[_COMMUNITY_handle_callback]]
- 3 edges to [[_COMMUNITY_handlers.py]]
- 3 edges to [[_COMMUNITY_test_phase13_shortlist.py]]
- 3 edges to [[_COMMUNITY_test_resume.py]]
- 3 edges to [[_COMMUNITY_skills.py]]
- 2 edges to [[_COMMUNITY_runner.py]]
- 2 edges to [[_COMMUNITY_test_application_deadline.py]]
- 2 edges to [[_COMMUNITY_test_cover_letter.py]]
- 2 edges to [[_COMMUNITY_diff.py]]
- 2 edges to [[_COMMUNITY_test_doctor.py]]
- 2 edges to [[_COMMUNITY_test_monitoring.py]]
- 2 edges to [[_COMMUNITY_test_pacing.py]]
- 2 edges to [[_COMMUNITY_test_priority.py]]
- 2 edges to [[_COMMUNITY_calculate_priority]]
- 2 edges to [[_COMMUNITY_json]]
- 1 edge to [[_COMMUNITY_targets.py]]
- 1 edge to [[_COMMUNITY_test_calibration.py]]
- 1 edge to [[_COMMUNITY_benchmarkengine.py]]
- 1 edge to [[_COMMUNITY_LLMClient]]
- 1 edge to [[_COMMUNITY_HttpCompanyIntelProvider]]
- 1 edge to [[_COMMUNITY_asyncio]]
- 1 edge to [[_COMMUNITY_pipeline.py]]
- 1 edge to [[_COMMUNITY_linkedin_people.py]]

## Top bridge nodes
- [[Source]] - degree 210, connects to 58 communities
- [[models.py]] - degree 37, connects to 24 communities
- [[run_ingestion()]] - degree 41, connects to 20 communities
- [[RawPosting]] - degree 67, connects to 19 communities
- [[to_job()]] - degree 45, connects to 15 communities