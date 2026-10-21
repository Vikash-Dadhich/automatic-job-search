---
type: community
cohesion: 0.18
members: 47
---

# session_scope

**Cohesion:** 0.18 - loosely connected
**Members:** 47 nodes

## Members
- [[dot-__init__()_23]] - code - tests/test_apply_runner.py
- [[A dead outreach call must not push a valid Tier-1 job into Status.error.]] - rationale - tests/test_robustness.py
- [[FakeApplicator]] - code - tests/test_apply_runner.py
- [[First reload stays as stored. The reload immediately before apply is mutated.]] - rationale - tests/test_apply_runner.py
- [[LinkedIn-discovered roles that apply on Workday must be eligible.]] - rationale - tests/test_apply_runner.py
- [[Module-level entry point used by README  Step 7. ``job_ids`` limits the run to…]] - rationale - automation/runner.py
- [[MonkeyPatch_17]] - code
- [[Offline tests for apply_pending with FakeApplicator (no browser).]] - rationale - tests/test_apply_runner.py
- [[Path_35]] - code
- [[Status]] - code - core/db.py
- [[_cmd_list_apply()]] - code - main.py
- [[_reload_job()]] - code - automation/runner.py
- [[_reopen_job()]] - code - scorer/engine.py
- [[_script_reloads()]] - code - tests/test_apply_runner.py
- [[_seed_job()]] - code - tests/test_apply_runner.py
- [[apply_pending()]] - code - automation/runner.py
- [[asyncio_6]] - code
- [[get_job_by_id()]] - code - core/db.py
- [[mark()]] - code - tests/test_apply_runner.py
- [[sequenced()]] - code - tests/test_apply_runner.py
- [[session_scope()]] - code - core/db.py
- [[test_allocation_removed_before_execution_is_skipped()]] - code - tests/test_apply_runner.py
- [[test_apply_linkedin_with_workday_url()]] - code - tests/test_apply_runner.py
- [[test_apply_pending_blocker()]] - code - tests/test_apply_runner.py
- [[test_apply_pending_empty()]] - code - tests/test_apply_runner.py
- [[test_apply_pending_error()]] - code - tests/test_apply_runner.py
- [[test_apply_pending_success()]] - code - tests/test_apply_runner.py
- [[test_apply_runner.py]] - code - tests/test_apply_runner.py
- [[test_apply_skips_non_workday_and_missing_resume()]] - code - tests/test_apply_runner.py
- [[test_content_hash_change_clears_vector()]] - code - tests/test_vector_gate.py
- [[test_duplicate_explicit_ids_apply_once()]] - code - tests/test_apply_runner.py
- [[test_explicit_id_runs_only_when_allocated()]] - code - tests/test_apply_runner.py
- [[test_explicit_id_skips_blocked_company()]] - code - tests/test_apply_runner.py
- [[test_explicit_id_skips_clearly_ineligible()]] - code - tests/test_apply_runner.py
- [[test_explicit_id_skips_deferred()]] - code - tests/test_apply_runner.py
- [[test_explicit_id_skips_missing_portfolio_decision()]] - code - tests/test_apply_runner.py
- [[test_explicit_id_skips_non_staged_allocation()]] - code - tests/test_apply_runner.py
- [[test_final_reload_blocked_company_is_skipped()]] - code - tests/test_apply_runner.py
- [[test_final_reload_clearly_ineligible_is_skipped()]] - code - tests/test_apply_runner.py
- [[test_final_reload_non_staged_is_skipped()]] - code - tests/test_apply_runner.py
- [[test_final_reload_still_allocated_reaches_applicator()]] - code - tests/test_apply_runner.py
- [[test_outreach_failure_still_persists_tier_one_score()]] - code - tests/test_robustness.py
- [[test_pipeline_ids_require_current_allocation()]] - code - tests/test_apply_runner.py
- [[test_rewritten_jd_leaves_submitted_outcome_alone()]] - code - tests/test_robustness.py
- [[test_score_pending_marks_error()]] - code - tests/test_scorer.py
- [[test_unchanged_jd_keeps_staged_status()]] - code - tests/test_robustness.py
- [[test_unrestricted_apply_does_not_require_allocation()]] - code - tests/test_apply_runner.py

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/session_scope
SORT file.name ASC
```

## Connections to other communities
- 67 edges to [[_COMMUNITY_test_vector_recovery.py]]
- 39 edges to [[_COMMUNITY_test_application_portfolio.py]]
- 30 edges to [[_COMMUNITY_runner.py]]
- 30 edges to [[_COMMUNITY_Source]]
- 28 edges to [[_COMMUNITY_handlers.py]]
- 28 edges to [[_COMMUNITY_Job]]
- 27 edges to [[_COMMUNITY_upsert_job]]
- 27 edges to [[_COMMUNITY_test_monitoring.py]]
- 27 edges to [[_COMMUNITY_test_phase13_shortlist.py]]
- 26 edges to [[_COMMUNITY_handle_callback]]
- 25 edges to [[_COMMUNITY_test_application_tracker.py]]
- 23 edges to [[_COMMUNITY_suggest.py]]
- 22 edges to [[_COMMUNITY_get_settings]]
- 20 edges to [[_COMMUNITY_test_company_intelligence.py]]
- 19 edges to [[_COMMUNITY_scorerengine.py]]
- 19 edges to [[_COMMUNITY_test_career_intelligence.py]]
- 18 edges to [[_COMMUNITY_test_pacing.py]]
- 17 edges to [[_COMMUNITY_tracker.py]]
- 17 edges to [[_COMMUNITY_alerts.py]]
- 14 edges to [[_COMMUNITY_review.py]]
- 13 edges to [[_COMMUNITY_test_doctor.py]]
- 13 edges to [[_COMMUNITY_pathlib]]
- 11 edges to [[_COMMUNITY_Tier]]
- 11 edges to [[_COMMUNITY_send_prep_pack]]
- 10 edges to [[_COMMUNITY_test_feedback.py]]
- 9 edges to [[_COMMUNITY_db.py]]
- 8 edges to [[_COMMUNITY_baseline.py]]
- 8 edges to [[_COMMUNITY_test_priority.py]]
- 8 edges to [[_COMMUNITY_pytest]]
- 8 edges to [[_COMMUNITY_LLMClient]]
- 8 edges to [[_COMMUNITY_AsyncSession]]
- 7 edges to [[_COMMUNITY_pipeline.py]]
- 6 edges to [[_COMMUNITY_main.py]]
- 6 edges to [[_COMMUNITY_profile.py]]
- 6 edges to [[_COMMUNITY_test_fit.py]]
- 5 edges to [[_COMMUNITY_test_resume.py]]
- 5 edges to [[_COMMUNITY_test_structured_jd.py]]
- 5 edges to [[_COMMUNITY_benchmarkengine.py]]
- 4 edges to [[_COMMUNITY_test_application_deadline.py]]
- 4 edges to [[_COMMUNITY_test_company_intelligence_v2.py]]
- 4 edges to [[_COMMUNITY_diff.py]]
- 4 edges to [[_COMMUNITY_test_eligibility.py]]
- 4 edges to [[_COMMUNITY_filters.py]]
- 4 edges to [[_COMMUNITY_calculate_priority]]
- 4 edges to [[_COMMUNITY_test_recruiting_universe.py]]
- 4 edges to [[_COMMUNITY_test_scorer.py]]
- 3 edges to [[_COMMUNITY_test_calibration.py]]
- 3 edges to [[_COMMUNITY_test_cover_letter.py]]
- 3 edges to [[_COMMUNITY_classify_role]]
- 3 edges to [[_COMMUNITY_test_role_classify.py]]
- 2 edges to [[_COMMUNITY_Profile]]
- 2 edges to [[_COMMUNITY_ingest.py]]
- 2 edges to [[_COMMUNITY_test_pipeline_order_and_aggregation]]
- 2 edges to [[_COMMUNITY_typing]]
- 2 edges to [[_COMMUNITY_test_apply_url.py]]
- 1 edge to [[_COMMUNITY_ScoreOnlyClient]]
- 1 edge to [[_COMMUNITY_priority.py]]
- 1 edge to [[_COMMUNITY_re]]
- 1 edge to [[_COMMUNITY_calibration.py]]
- 1 edge to [[_COMMUNITY_feedback.py]]
- 1 edge to [[_COMMUNITY_test_discovery.py]]
- 1 edge to [[_COMMUNITY_textclean.py]]
- 1 edge to [[_COMMUNITY_vault.py]]
- 1 edge to [[_COMMUNITY_workday.py]]

## Top bridge nodes
- [[session_scope()]] - degree 304, connects to 53 communities
- [[Status]] - degree 246, connects to 50 communities
- [[get_job_by_id()]] - degree 161, connects to 30 communities
- [[apply_pending()]] - degree 46, connects to 9 communities
- [[test_apply_runner.py]] - degree 38, connects to 8 communities