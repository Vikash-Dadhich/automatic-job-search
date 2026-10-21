---
source_file: "tests/test_application_portfolio.py"
type: "code"
community: "test_application_portfolio.py"
location: "L1"
tags:
  - graphify/code
  - graphify/EXTRACTED
  - community/test_application_portfoliopy
---

# test_application_portfolio.py

## Connections
- [[Application capacity. It does not score jobs or move them between statuses.]] - `rationale_for` [EXTRACTED]
- [[ApplyResult]] - `imports` [EXTRACTED]
- [[Job]] - `imports` [EXTRACTED]
- [[Source]] - `imports` [EXTRACTED]
- [[Status]] - `imports` [EXTRACTED]
- [[Tier]] - `imports` [EXTRACTED]
- [[_NotStaged]] - `contains` [EXTRACTED]
- [[_Spy]] - `contains` [EXTRACTED]
- [[_job()_8]] - `contains` [EXTRACTED]
- [[_seat_targets()]] - `imports` [EXTRACTED]
- [[_workday()]] - `contains` [EXTRACTED]
- [[allocate_portfolio()]] - `imports` [EXTRACTED]
- [[allocated_jobs()]] - `imports` [EXTRACTED]
- [[application_portfolio.py]] - `imports_from` [EXTRACTED]
- [[apply_pending()]] - `imports` [EXTRACTED]
- [[apply_portfolio()]] - `imports` [EXTRACTED]
- [[bucket_weights()]] - `imports` [EXTRACTED]
- [[datetime_17]] - `imports_from` [EXTRACTED]
- [[db.py]] - `imports_from` [EXTRACTED]
- [[get_job_by_id()]] - `imports` [EXTRACTED]
- [[get_settings()]] - `imports` [EXTRACTED]
- [[load_portfolio_config()]] - `imports` [EXTRACTED]
- [[pathlib]] - `imports_from` [EXTRACTED]
- [[pipeline.py]] - `imports_from` [EXTRACTED]
- [[portfolio_config_hash()]] - `imports` [EXTRACTED]
- [[pytest]] - `imports` [EXTRACTED]
- [[run_pipeline()]] - `imports` [EXTRACTED]
- [[runner.py]] - `imports_from` [EXTRACTED]
- [[session_scope()]] - `imports` [EXTRACTED]
- [[settings.py]] - `imports_from` [EXTRACTED]
- [[test_allocation_does_not_rescore()]] - `contains` [EXTRACTED]
- [[test_blank_companies_do_not_share_a_cap()]] - `contains` [EXTRACTED]
- [[test_company_cap_is_per_run_and_suffix_aware()]] - `contains` [EXTRACTED]
- [[test_config_rejects_a_bool_cap()]] - `contains` [EXTRACTED]
- [[test_cooldown_blocks_the_company_and_leaves_scores()]] - `contains` [EXTRACTED]
- [[test_daily_capacity_defers_the_rest()]] - `contains` [EXTRACTED]
- [[test_ignored_job_does_not_consume_a_slot()]] - `contains` [EXTRACTED]
- [[test_ineligible_and_review_jobs_are_not_candidates()]] - `contains` [EXTRACTED]
- [[test_mixed_persist_returns_only_the_saved_allocation()]] - `contains` [EXTRACTED]
- [[test_persisted_allocation_is_returned()]] - `contains` [EXTRACTED]
- [[test_pipeline_applies_only_allocated_staged_jobs()]] - `contains` [EXTRACTED]
- [[test_pipeline_apply_receives_only_persisted_ids()]] - `contains` [EXTRACTED]
- [[test_portfolio_config_reuses_phase7_weights()]] - `contains` [EXTRACTED]
- [[test_priority_order_and_zero_capacity()]] - `contains` [EXTRACTED]
- [[test_real_cooldown_ignores_an_ignored_job()]] - `contains` [EXTRACTED]
- [[test_role_family_targets_are_soft()]] - `contains` [EXTRACTED]
- [[test_skipped_allocation_is_not_returned()]] - `contains` [EXTRACTED]
- [[test_skipped_plan_does_not_consume_capacity()]] - `contains` [EXTRACTED]
- [[test_unknown_eligibility_can_still_be_allocated()]] - `contains` [EXTRACTED]
- [[upsert_job()]] - `imports` [EXTRACTED]
- [[workday.py]] - `imports_from` [EXTRACTED]

#graphify/code #graphify/EXTRACTED #community/test_application_portfoliopy