---
type: community
cohesion: 0.07
members: 64
---

# test_application_portfolio.py

**Cohesion:** 0.07 - loosely connected
**Members:** 64 nodes

## Members
- [[dot-__init__()_24]] - code - tests/test_application_portfolio.py
- [[Allocate limited apply capacity. This does not score jobs or change workflow…]] - rationale - scorer/application_portfolio.py
- [[Any_34]] - code
- [[Application capacity. It does not score jobs or move them between statuses.]] - rationale - tests/test_application_portfolio.py
- [[Choose staged candidates. Does not write status, fit, or priority.]] - rationale - scorer/application_portfolio.py
- [[Largest remainder. A tied fraction goes to the bucket with fewer seats.]] - rationale - scorer/application_portfolio.py
- [[MonkeyPatch_18]] - code
- [[Path_38]] - code
- [[Phase 7 weights. Other families share the stored OTHER weight of 5.]] - rationale - scorer/application_portfolio.py
- [[PortfolioDecision]] - code - scorer/application_portfolio.py
- [[PortfolioSummary]] - code - scorer/application_portfolio.py
- [[Record allocation on staged apply candidates. Status and scores stay put.]] - rationale - scorer/application_portfolio.py
- [[_NotStaged]] - code - tests/test_application_portfolio.py
- [[_boom()_2]] - code - tests/test_application_portfolio.py
- [[_bucket()_1]] - code - scorer/application_portfolio.py
- [[_company_key()_1]] - code - scorer/application_portfolio.py
- [[_is_candidate()]] - code - scorer/application_portfolio.py
- [[_job()_8]] - code - tests/test_application_portfolio.py
- [[_on_cooldown()]] - code - scorer/application_portfolio.py
- [[_require_int()_2]] - code - scorer/application_portfolio.py
- [[_seat_targets()]] - code - scorer/application_portfolio.py
- [[_validate()_3]] - code - scorer/application_portfolio.py
- [[_workday()]] - code - tests/test_application_portfolio.py
- [[allocate_portfolio()]] - code - scorer/application_portfolio.py
- [[allocated_jobs()]] - code - scorer/application_portfolio.py
- [[application_portfolio.py]] - code - scorer/application_portfolio.py
- [[apply_portfolio()]] - code - scorer/application_portfolio.py
- [[batch()]] - code - tests/test_application_portfolio.py
- [[bucket_weights()]] - code - scorer/application_portfolio.py
- [[can_take()]] - code - scorer/application_portfolio.py
- [[identity()]] - code - scorer/application_portfolio.py
- [[load_portfolio_config()]] - code - scorer/application_portfolio.py
- [[noop()_1]] - code - tests/test_application_portfolio.py
- [[noop()_2]] - code - tests/test_application_portfolio.py
- [[noop_stage()]] - code - tests/test_application_portfolio.py
- [[noop_stage()_1]] - code - tests/test_application_portfolio.py
- [[portfolio_config_hash()]] - code - scorer/application_portfolio.py
- [[record_apply()]] - code - tests/test_application_portfolio.py
- [[record_apply()_1]] - code - tests/test_application_portfolio.py
- [[skip()]] - code - tests/test_application_portfolio.py
- [[skip_first()]] - code - tests/test_application_portfolio.py
- [[skip_lost()]] - code - tests/test_application_portfolio.py
- [[skip_lost()_1]] - code - tests/test_application_portfolio.py
- [[take()]] - code - scorer/application_portfolio.py
- [[test_allocation_does_not_rescore()]] - code - tests/test_application_portfolio.py
- [[test_application_portfolio.py]] - code - tests/test_application_portfolio.py
- [[test_blank_companies_do_not_share_a_cap()]] - code - tests/test_application_portfolio.py
- [[test_company_cap_is_per_run_and_suffix_aware()]] - code - tests/test_application_portfolio.py
- [[test_config_rejects_a_bool_cap()]] - code - tests/test_application_portfolio.py
- [[test_cooldown_blocks_the_company_and_leaves_scores()]] - code - tests/test_application_portfolio.py
- [[test_daily_capacity_defers_the_rest()]] - code - tests/test_application_portfolio.py
- [[test_ignored_job_does_not_consume_a_slot()]] - code - tests/test_application_portfolio.py
- [[test_ineligible_and_review_jobs_are_not_candidates()]] - code - tests/test_application_portfolio.py
- [[test_mixed_persist_returns_only_the_saved_allocation()]] - code - tests/test_application_portfolio.py
- [[test_persisted_allocation_is_returned()]] - code - tests/test_application_portfolio.py
- [[test_pipeline_applies_only_allocated_staged_jobs()]] - code - tests/test_application_portfolio.py
- [[test_pipeline_apply_receives_only_persisted_ids()]] - code - tests/test_application_portfolio.py
- [[test_portfolio_config_reuses_phase7_weights()]] - code - tests/test_application_portfolio.py
- [[test_priority_order_and_zero_capacity()]] - code - tests/test_application_portfolio.py
- [[test_real_cooldown_ignores_an_ignored_job()]] - code - tests/test_application_portfolio.py
- [[test_role_family_targets_are_soft()]] - code - tests/test_application_portfolio.py
- [[test_skipped_allocation_is_not_returned()]] - code - tests/test_application_portfolio.py
- [[test_skipped_plan_does_not_consume_capacity()]] - code - tests/test_application_portfolio.py
- [[test_unknown_eligibility_can_still_be_allocated()]] - code - tests/test_application_portfolio.py

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/test_application_portfoliopy
SORT file.name ASC
```

## Connections to other communities
- 39 edges to [[_COMMUNITY_session_scope]]
- 13 edges to [[_COMMUNITY_Job]]
- 8 edges to [[_COMMUNITY_runner.py]]
- 8 edges to [[_COMMUNITY_upsert_job]]
- 6 edges to [[_COMMUNITY_Source]]
- 6 edges to [[_COMMUNITY_pytest]]
- 6 edges to [[_COMMUNITY_pipeline.py]]
- 5 edges to [[_COMMUNITY_discovery_recall.py]]
- 4 edges to [[_COMMUNITY_db.py]]
- 4 edges to [[_COMMUNITY_sort_by_priority]]
- 4 edges to [[_COMMUNITY_json]]
- 3 edges to [[_COMMUNITY_get_settings]]
- 3 edges to [[_COMMUNITY_test_doctor.py]]
- 3 edges to [[_COMMUNITY_typing]]
- 2 edges to [[_COMMUNITY_Tier]]
- 2 edges to [[_COMMUNITY_test_phase13_shortlist.py]]
- 2 edges to [[_COMMUNITY_pathlib]]
- 2 edges to [[_COMMUNITY_baseline.py]]
- 1 edge to [[_COMMUNITY_linkedin_people.py]]
- 1 edge to [[_COMMUNITY_workday.py]]
- 1 edge to [[_COMMUNITY_priority.py]]
- 1 edge to [[_COMMUNITY_test_resume.py]]
- 1 edge to [[_COMMUNITY_targets.py]]

## Top bridge nodes
- [[application_portfolio.py]] - degree 44, connects to 17 communities
- [[test_application_portfolio.py]] - degree 51, connects to 14 communities
- [[apply_portfolio()]] - degree 26, connects to 9 communities
- [[_job()_8]] - degree 20, connects to 5 communities
- [[test_pipeline_applies_only_allocated_staged_jobs()]] - degree 15, connects to 5 communities