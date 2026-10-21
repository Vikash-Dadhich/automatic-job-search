---
source_file: "tests/test_company_intelligence.py"
type: "code"
community: "test_company_intelligence.py"
location: "L1"
tags:
  - graphify/code
  - graphify/EXTRACTED
  - community/test_company_intelligencepy
---

# test_company_intelligence.py

## Connections
- [[CompanyLookupResult]] - `imports` [EXTRACTED]
- [[CompanySourceDocument]] - `imports` [EXTRACTED]
- [[FakeProvider]] - `contains` [EXTRACTED]
- [[HttpCompanyIntelProvider]] - `imports` [EXTRACTED]
- [[Job]] - `imports` [EXTRACTED]
- [[Phase 8 company facts. They do not change fit, weight, tier, status, or…]] - `rationale_for` [EXTRACTED]
- [[RawPosting]] - `imports` [EXTRACTED]
- [[Source]] - `imports` [EXTRACTED]
- [[Status]] - `imports` [EXTRACTED]
- [[Tier]] - `imports` [EXTRACTED]
- [[_explicit_company_url()]] - `imports` [EXTRACTED]
- [[_job()_4]] - `contains` [EXTRACTED]
- [[_posting()_4]] - `contains` [EXTRACTED]
- [[attach_company_intelligence()]] - `imports` [EXTRACTED]
- [[canonical_company_name()]] - `imports` [EXTRACTED]
- [[company_intelligence.py]] - `imports_from` [EXTRACTED]
- [[compute_tier()]] - `imports` [EXTRACTED]
- [[datetime_17]] - `imports_from` [EXTRACTED]
- [[db.py]] - `imports_from` [EXTRACTED]
- [[discovery.py]] - `imports_from` [EXTRACTED]
- [[extract_company_facts()]] - `imports` [EXTRACTED]
- [[get_recently_applied_companies()]] - `imports` [EXTRACTED]
- [[get_role_family_weight()]] - `imports` [EXTRACTED]
- [[httpx]] - `imports` [EXTRACTED]
- [[is_dream_company()]] - `imports` [EXTRACTED]
- [[linkedin_jobspy.py]] - `imports_from` [EXTRACTED]
- [[load_discovery()]] - `imports` [EXTRACTED]
- [[merge_company_facts()]] - `imports` [EXTRACTED]
- [[models.py]] - `imports_from` [EXTRACTED]
- [[normalize_company_name()]] - `imports` [EXTRACTED]
- [[pathlib]] - `imports_from` [EXTRACTED]
- [[refresh_company_intelligence()]] - `imports` [EXTRACTED]
- [[resolve_company()]] - `imports` [EXTRACTED]
- [[role_weights.py]] - `imports_from` [EXTRACTED]
- [[scorerengine.py]] - `imports_from` [EXTRACTED]
- [[session_scope()]] - `imports` [EXTRACTED]
- [[test_ambiguous_names_stay_separate()]] - `contains` [EXTRACTED]
- [[test_company_facts_do_not_change_scoring_signals()]] - `contains` [EXTRACTED]
- [[test_company_sources_accumulate_and_a_failed_refresh_keeps_them()]] - `contains` [EXTRACTED]
- [[test_company_url_is_not_guessed_or_taken_from_the_job_page()]] - `contains` [EXTRACTED]
- [[test_complete_record_and_ignored_claims()]] - `contains` [EXTRACTED]
- [[test_cooldown_set_is_unchanged()]] - `contains` [EXTRACTED]
- [[test_explicit_refresh_calls_the_provider_again()]] - `contains` [EXTRACTED]
- [[test_extractor_keeps_unstated_facts_null()]] - `contains` [EXTRACTED]
- [[test_http_provider_handles_timeout_and_malformed_pages()]] - `contains` [EXTRACTED]
- [[test_http_provider_keeps_the_caller_source_type()]] - `contains` [EXTRACTED]
- [[test_legal_suffixes_do_not_collapse_distinct_names()]] - `contains` [EXTRACTED]
- [[test_merge_company_facts_keeps_omitted_fields()]] - `contains` [EXTRACTED]
- [[test_normalization_is_deterministic()]] - `contains` [EXTRACTED]
- [[test_persisted_source_type_matches_the_caller()]] - `contains` [EXTRACTED]
- [[test_prestige_language_is_not_a_fact()]] - `contains` [EXTRACTED]
- [[test_provider_failures_do_not_change_the_job()]] - `contains` [EXTRACTED]
- [[test_same_company_is_reused_without_merging_jobs()]] - `contains` [EXTRACTED]
- [[test_source_grounded_partial_record()]] - `contains` [EXTRACTED]
- [[test_sparse_refresh_does_not_erase_known_facts()]] - `contains` [EXTRACTED]
- [[test_unknown_without_a_source_stays_null()]] - `contains` [EXTRACTED]
- [[to_job()]] - `imports` [EXTRACTED]
- [[trustworthy_company_source()]] - `imports` [EXTRACTED]
- [[upsert_job()]] - `imports` [EXTRACTED]

#graphify/code #graphify/EXTRACTED #community/test_company_intelligencepy