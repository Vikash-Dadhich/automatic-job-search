---
source_file: "automation/runner.py"
type: "code"
community: "session_scope"
location: "L303"
tags:
  - graphify/code
  - graphify/EXTRACTED
  - community/session_scope
---

# apply_pending()

## Connections
- [[Applicator]] - `uses` [INFERRED]
- [[ApplyRunner]] - `calls` [EXTRACTED]
- [[ApplySummary]] - `references` [EXTRACTED]
- [[Module-level entry point used by README  Step 7. ``job_ids`` limits the run to…]] - `rationale_for` [EXTRACTED]
- [[Profile]] - `uses` [INFERRED]
- [[Random]] - `references` [EXTRACTED]
- [[_cmd_list_apply()]] - `calls` [EXTRACTED]
- [[automation__init__.py]] - `imports` [EXTRACTED]
- [[datetime_3]] - `references` [EXTRACTED]
- [[main.py]] - `imports` [EXTRACTED]
- [[pipeline.py]] - `indirect_call` [INFERRED]
- [[record_apply()]] - `calls` [EXTRACTED]
- [[runner.py]] - `contains` [EXTRACTED]
- [[test_allocation_removed_before_execution_is_skipped()]] - `calls` [EXTRACTED]
- [[test_application_portfolio.py]] - `imports` [EXTRACTED]
- [[test_application_tracker.py]] - `imports` [EXTRACTED]
- [[test_apply_linkedin_with_workday_url()]] - `calls` [EXTRACTED]
- [[test_apply_pending_blocker()]] - `calls` [EXTRACTED]
- [[test_apply_pending_empty()]] - `calls` [EXTRACTED]
- [[test_apply_pending_error()]] - `calls` [EXTRACTED]
- [[test_apply_pending_success()]] - `calls` [EXTRACTED]
- [[test_apply_runner.py]] - `imports` [EXTRACTED]
- [[test_apply_skips_non_workday_and_missing_resume()]] - `calls` [EXTRACTED]
- [[test_blocker_and_manual_takeover_are_not_submissions()]] - `calls` [EXTRACTED]
- [[test_duplicate_explicit_ids_apply_once()]] - `calls` [EXTRACTED]
- [[test_explicit_id_runs_only_when_allocated()]] - `calls` [EXTRACTED]
- [[test_explicit_id_skips_blocked_company()]] - `calls` [EXTRACTED]
- [[test_explicit_id_skips_clearly_ineligible()]] - `calls` [EXTRACTED]
- [[test_explicit_id_skips_deferred()]] - `calls` [EXTRACTED]
- [[test_explicit_id_skips_missing_portfolio_decision()]] - `calls` [EXTRACTED]
- [[test_explicit_id_skips_non_staged_allocation()]] - `calls` [EXTRACTED]
- [[test_final_reload_blocked_company_is_skipped()]] - `calls` [EXTRACTED]
- [[test_final_reload_clearly_ineligible_is_skipped()]] - `calls` [EXTRACTED]
- [[test_final_reload_non_staged_is_skipped()]] - `calls` [EXTRACTED]
- [[test_final_reload_still_allocated_reaches_applicator()]] - `calls` [EXTRACTED]
- [[test_pacing.py]] - `imports` [EXTRACTED]
- [[test_phase13_shortlist.py]] - `imports` [EXTRACTED]
- [[test_pipeline_applies_only_allocated_staged_jobs()]] - `calls` [EXTRACTED]
- [[test_pipeline_enriches_the_review_queue_and_apply_stays_on_staged()]] - `calls` [EXTRACTED]
- [[test_pipeline_ids_require_current_allocation()]] - `calls` [EXTRACTED]
- [[test_prefill_starts_an_application_without_submitting()]] - `calls` [EXTRACTED]
- [[test_runner_blackout_leaves_second_job_staged()]] - `calls` [EXTRACTED]
- [[test_runner_mfa_does_not_black_out()]] - `calls` [EXTRACTED]
- [[test_runner_pacing_disabled_does_not_sleep()]] - `calls` [EXTRACTED]
- [[test_runner_waits_then_both_pending()]] - `calls` [EXTRACTED]
- [[test_unrestricted_apply_does_not_require_allocation()]] - `calls` [EXTRACTED]

#graphify/code #graphify/EXTRACTED #community/session_scope