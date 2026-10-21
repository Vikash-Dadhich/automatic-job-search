---
source_file: "scraper/models.py"
type: "code"
community: "Source"
location: "L58"
tags:
  - graphify/code
  - graphify/EXTRACTED
  - community/Source
---

# to_job()

## Connections
- [[Job]] - `calls` [EXTRACTED]
- [[Map a RawPosting to a Job row, computing content_hash.]] - `rationale_for` [EXTRACTED]
- [[RawPosting]] - `references` [EXTRACTED]
- [[Status]] - `uses` [INFERRED]
- [[_job()_4]] - `calls` [EXTRACTED]
- [[_job()_5]] - `calls` [EXTRACTED]
- [[_job()_1]] - `calls` [EXTRACTED]
- [[content_hash()]] - `calls` [EXTRACTED]
- [[hash_fallback()]] - `calls` [EXTRACTED]
- [[ingest.py]] - `imports` [EXTRACTED]
- [[models.py]] - `contains` [EXTRACTED]
- [[run_ingestion()]] - `calls` [EXTRACTED]
- [[scraper__init__.py]] - `imports` [EXTRACTED]
- [[test_apply_url.py]] - `imports` [EXTRACTED]
- [[test_cache_recomputes_only_when_hash_or_version_changes()]] - `calls` [EXTRACTED]
- [[test_classification_persists_and_does_not_filter()]] - `calls` [EXTRACTED]
- [[test_company_facts_do_not_change_job_decisions()]] - `calls` [EXTRACTED]
- [[test_company_intelligence.py]] - `imports` [EXTRACTED]
- [[test_company_intelligence_v2.py]] - `imports` [EXTRACTED]
- [[test_company_sources_accumulate_and_a_failed_refresh_keeps_them()]] - `calls` [EXTRACTED]
- [[test_db_ingest.py]] - `imports` [EXTRACTED]
- [[test_discovered_job_keeps_provenance()]] - `calls` [EXTRACTED]
- [[test_discovery.py]] - `imports` [EXTRACTED]
- [[test_eligibility.py]] - `imports` [EXTRACTED]
- [[test_first_discovery_provenance_is_immutable()]] - `calls` [EXTRACTED]
- [[test_homepage_query_does_not_merge_across_sources()]] - `calls` [EXTRACTED]
- [[test_jd_ingest.py]] - `imports` [EXTRACTED]
- [[test_job_identity.py]] - `imports` [EXTRACTED]
- [[test_jobsy_and_workday_descriptions_and_provenance()]] - `calls` [EXTRACTED]
- [[test_material_description_change_still_clears_fit()]] - `calls` [EXTRACTED]
- [[test_recruiting_universe.py]] - `imports` [EXTRACTED]
- [[test_role_classify.py]] - `imports` [EXTRACTED]
- [[test_role_secondary.py]] - `imports` [EXTRACTED]
- [[test_role_weights.py]] - `imports` [EXTRACTED]
- [[test_same_place_and_text_can_merge_without_using_fit()]] - `calls` [EXTRACTED]
- [[test_same_source_identity_and_cross_source_url()]] - `calls` [EXTRACTED]
- [[test_secondary_fields_persist_and_clear_when_the_jd_changes()]] - `calls` [EXTRACTED]
- [[test_stale_classifier_version_is_replaced_on_reprocess()]] - `calls` [EXTRACTED]
- [[test_to_job_maps_fields_and_hash()]] - `calls` [EXTRACTED]
- [[test_to_job_stamps_workday_tenant_from_linkedin_url()]] - `calls` [EXTRACTED]
- [[test_unchanged_jd_keeps_classification_and_a_change_replaces_it()]] - `calls` [EXTRACTED]
- [[test_upsert_idempotent_and_status_refresh()]] - `calls` [EXTRACTED]
- [[test_upsert_keeps_good_jd_and_clears_stale_embedding()]] - `calls` [EXTRACTED]
- [[test_weak_similarity_does_not_merge()]] - `calls` [EXTRACTED]
- [[workday_parts()]] - `calls` [EXTRACTED]

#graphify/code #graphify/EXTRACTED #community/Source