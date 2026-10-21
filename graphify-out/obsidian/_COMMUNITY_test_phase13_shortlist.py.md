---
type: community
cohesion: 0.10
members: 50
---

# test_phase13_shortlist.py

**Cohesion:** 0.10 - loosely connected
**Members:** 50 nodes

## Members
- [[Any_24]] - code
- [[Any_25]] - code
- [[Choose which staged jobs enter review. This does not score or discard a job.…]] - rationale - scorer/shortlist.py
- [[MonkeyPatch_14]] - code
- [[Move the selected staged jobs to pending_review. Other statuses stay as they…]] - rationale - scorer/shortlist.py
- [[Normalized employer tokens. A blank name is not treated as one shared company.]] - rationale - scorer/shortlist.py
- [[Path_24]] - code
- [[Pick staged jobs that already have a priority score. Does not write or rescore.]] - rationale - scorer/shortlist.py
- [[Primary family only. A secondary family does not count as its own seat.]] - rationale - scorer/shortlist.py
- [[Replace a tail seat when one family holds more than half and a close…]] - rationale - scorer/shortlist.py
- [[Return jobs with the given status, oldest first.]] - rationale - core/db.py
- [[Review-queue selection. It orders staged jobs and does not discard the rest.]] - rationale - tests/test_phase13_shortlist.py
- [[ShortlistPick]] - code - scorer/shortlist.py
- [[ShortlistSummary]] - code - scorer/shortlist.py
- [[_boom()_1]] - code - tests/test_phase13_shortlist.py
- [[_close_enough()]] - code - scorer/shortlist.py
- [[_company_key()]] - code - scorer/shortlist.py
- [[_company_ok()]] - code - scorer/shortlist.py
- [[_config()]] - code - tests/test_phase13_shortlist.py
- [[_diversify()]] - code - scorer/shortlist.py
- [[_family()]] - code - scorer/shortlist.py
- [[_identity()]] - code - scorer/shortlist.py
- [[_job()_6]] - code - tests/test_phase13_shortlist.py
- [[_require_int()_1]] - code - scorer/shortlist.py
- [[_targeted()]] - code - scorer/shortlist.py
- [[_targets()]] - code - scorer/shortlist.py
- [[_validate()_2]] - code - scorer/shortlist.py
- [[apply_shortlist()]] - code - scorer/shortlist.py
- [[config_hash()]] - code - scorer/shortlist.py
- [[fake_benchmark()_1]] - code - tests/test_phase13_shortlist.py
- [[fake_suggest()]] - code - tests/test_phase13_shortlist.py
- [[get_jobs_by_status()]] - code - core/db.py
- [[load_shortlist_config()]] - code - scorer/shortlist.py
- [[noop()]] - code - tests/test_phase13_shortlist.py
- [[record_prepare()]] - code - tests/test_phase13_shortlist.py
- [[select_shortlist()]] - code - scorer/shortlist.py
- [[shortlist.py]] - code - scorer/shortlist.py
- [[test_apply_shortlist_is_idempotent_and_preserves_scores()]] - code - tests/test_phase13_shortlist.py
- [[test_diversity_respects_company_cap_and_ignores_secondary_family()]] - code - tests/test_phase13_shortlist.py
- [[test_family_diversity_is_a_soft_swap()]] - code - tests/test_phase13_shortlist.py
- [[test_low_priority_still_takes_an_open_seat()]] - code - tests/test_phase13_shortlist.py
- [[test_missing_dates_still_select()]] - code - tests/test_phase13_shortlist.py
- [[test_non_staged_jobs_are_ignored()]] - code - tests/test_phase13_shortlist.py
- [[test_phase13_shortlist.py]] - code - tests/test_phase13_shortlist.py
- [[test_pipeline_enriches_the_review_queue_and_apply_stays_on_staged()]] - code - tests/test_phase13_shortlist.py
- [[test_priority_order_and_phase12_ties()]] - code - tests/test_phase13_shortlist.py
- [[test_selection_does_not_score()]] - code - tests/test_phase13_shortlist.py
- [[test_selection_ignores_discovery_and_vector()]] - code - tests/test_phase13_shortlist.py
- [[test_shortlist_config_loads_and_rejects_invalid()]] - code - tests/test_phase13_shortlist.py
- [[test_size_and_company_cap()]] - code - tests/test_phase13_shortlist.py

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/test_phase13_shortlistpy
SORT file.name ASC
```

## Connections to other communities
- 27 edges to [[_COMMUNITY_session_scope]]
- 13 edges to [[_COMMUNITY_Job]]
- 8 edges to [[_COMMUNITY_db.py]]
- 7 edges to [[_COMMUNITY_runner.py]]
- 5 edges to [[_COMMUNITY_pipeline.py]]
- 4 edges to [[_COMMUNITY_get_settings]]
- 4 edges to [[_COMMUNITY_json]]
- 3 edges to [[_COMMUNITY_Source]]
- 3 edges to [[_COMMUNITY_discovery_recall.py]]
- 3 edges to [[_COMMUNITY_upsert_job]]
- 3 edges to [[_COMMUNITY_test_career_intelligence.py]]
- 3 edges to [[_COMMUNITY_send_prep_pack]]
- 3 edges to [[_COMMUNITY_sort_by_priority]]
- 3 edges to [[_COMMUNITY_pytest]]
- 3 edges to [[_COMMUNITY_typing]]
- 2 edges to [[_COMMUNITY_test_feedback.py]]
- 2 edges to [[_COMMUNITY_Tier]]
- 2 edges to [[_COMMUNITY_test_application_portfolio.py]]
- 2 edges to [[_COMMUNITY_baseline.py]]
- 2 edges to [[_COMMUNITY_pathlib]]
- 1 edge to [[_COMMUNITY_LLMClient]]
- 1 edge to [[_COMMUNITY_main.py]]
- 1 edge to [[_COMMUNITY_scorerengine.py]]
- 1 edge to [[_COMMUNITY_AsyncSession]]
- 1 edge to [[_COMMUNITY_test_resume.py]]
- 1 edge to [[_COMMUNITY_targets.py]]
- 1 edge to [[_COMMUNITY_priority.py]]
- 1 edge to [[_COMMUNITY_test_monitoring.py]]
- 1 edge to [[_COMMUNITY_workday.py]]

## Top bridge nodes
- [[test_phase13_shortlist.py]] - degree 45, connects to 16 communities
- [[shortlist.py]] - degree 39, connects to 15 communities
- [[get_jobs_by_status()]] - degree 22, connects to 10 communities
- [[test_pipeline_enriches_the_review_queue_and_apply_stays_on_staged()]] - degree 19, connects to 7 communities
- [[apply_shortlist()]] - degree 20, connects to 5 communities