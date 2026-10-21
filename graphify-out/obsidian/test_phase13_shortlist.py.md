---
source_file: "tests/test_phase13_shortlist.py"
type: "code"
community: "test_phase13_shortlist.py"
location: "L1"
tags:
  - graphify/code
  - graphify/EXTRACTED
  - community/test_phase13_shortlistpy
---

# test_phase13_shortlist.py

## Connections
- [[Application]] - `imports` [EXTRACTED]
- [[ApplyResult]] - `imports` [EXTRACTED]
- [[Job]] - `imports` [EXTRACTED]
- [[Review-queue selection. It orders staged jobs and does not discard the rest.]] - `rationale_for` [EXTRACTED]
- [[Source]] - `imports` [EXTRACTED]
- [[Status]] - `imports` [EXTRACTED]
- [[Tier]] - `imports` [EXTRACTED]
- [[_SpyApplicator]] - `contains` [EXTRACTED]
- [[_config()]] - `contains` [EXTRACTED]
- [[_job()_6]] - `contains` [EXTRACTED]
- [[apply_pending()]] - `imports` [EXTRACTED]
- [[apply_shortlist()]] - `imports` [EXTRACTED]
- [[config_hash()]] - `imports` [EXTRACTED]
- [[datetime_17]] - `imports_from` [EXTRACTED]
- [[db.py]] - `imports_from` [EXTRACTED]
- [[get_job_by_id()]] - `imports` [EXTRACTED]
- [[get_jobs_by_status()]] - `imports` [EXTRACTED]
- [[get_settings()]] - `imports` [EXTRACTED]
- [[get_unsent_pending_reviews()]] - `imports` [EXTRACTED]
- [[load_shortlist_config()]] - `imports` [EXTRACTED]
- [[pathlib]] - `imports_from` [EXTRACTED]
- [[pipeline.py]] - `imports_from` [EXTRACTED]
- [[pytest]] - `imports` [EXTRACTED]
- [[run_pipeline()]] - `imports` [EXTRACTED]
- [[runner.py]] - `imports_from` [EXTRACTED]
- [[select_shortlist()]] - `imports` [EXTRACTED]
- [[session_scope()]] - `imports` [EXTRACTED]
- [[settings.py]] - `imports_from` [EXTRACTED]
- [[shortlist.py]] - `imports_from` [EXTRACTED]
- [[sqlmodel_2]] - `imports_from` [EXTRACTED]
- [[test_apply_shortlist_is_idempotent_and_preserves_scores()]] - `contains` [EXTRACTED]
- [[test_diversity_respects_company_cap_and_ignores_secondary_family()]] - `contains` [EXTRACTED]
- [[test_family_diversity_is_a_soft_swap()]] - `contains` [EXTRACTED]
- [[test_low_priority_still_takes_an_open_seat()]] - `contains` [EXTRACTED]
- [[test_missing_dates_still_select()]] - `contains` [EXTRACTED]
- [[test_non_staged_jobs_are_ignored()]] - `contains` [EXTRACTED]
- [[test_pipeline_enriches_the_review_queue_and_apply_stays_on_staged()]] - `contains` [EXTRACTED]
- [[test_priority_order_and_phase12_ties()]] - `contains` [EXTRACTED]
- [[test_selection_does_not_score()]] - `contains` [EXTRACTED]
- [[test_selection_ignores_discovery_and_vector()]] - `contains` [EXTRACTED]
- [[test_shortlist_config_loads_and_rejects_invalid()]] - `contains` [EXTRACTED]
- [[test_size_and_company_cap()]] - `contains` [EXTRACTED]
- [[typing]] - `imports_from` [EXTRACTED]
- [[upsert_job()]] - `imports` [EXTRACTED]
- [[workday.py]] - `imports_from` [EXTRACTED]

#graphify/code #graphify/EXTRACTED #community/test_phase13_shortlistpy