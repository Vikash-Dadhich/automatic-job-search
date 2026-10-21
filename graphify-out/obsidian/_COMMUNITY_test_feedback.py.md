---
type: community
cohesion: 0.15
members: 27
---

# test_feedback.py

**Cohesion:** 0.15 - loosely connected
**Members:** 27 nodes

## Members
- [[Application]] - code - core/db.py
- [[ApplicationEvent]] - code - core/db.py
- [[Applications that have a submission time. The caller applies the cutoff.]] - rationale - core/db.py
- [[Feedback rates come from submitted applications and do not change scores.]] - rationale - tests/test_feedback.py
- [[One application lifecycle for a canonical job. Not created by discovery.]] - rationale - core/db.py
- [[One factual application transition. Pipeline stages are not events.]] - rationale - core/db.py
- [[Path_33]] - code
- [[Path_34]] - code
- [[Read Phase 15 rows. Cutoff filtering happens in build_feedback.]] - rationale - scorer/feedback.py
- [[_case()_3]] - code - tests/test_feedback.py
- [[_case_from_rows()]] - code - scorer/feedback.py
- [[_config()_1]] - code - tests/test_feedback.py
- [[_signal()_2]] - code - tests/test_feedback.py
- [[datetime_7]] - code
- [[get_application_by_id()]] - code - core/db.py
- [[get_application_events()]] - code - core/db.py
- [[list_events_for_applications()]] - code - core/db.py
- [[list_jobs_by_ids()]] - code - core/db.py
- [[list_submitted_applications()]] - code - core/db.py
- [[load_feedback_cases()]] - code - scorer/feedback.py
- [[test_bands_families_and_sparse_subfamily()]] - code - tests/test_feedback.py
- [[test_cutoff_hides_future_submissions_and_outcomes()]] - code - tests/test_feedback.py
- [[test_feedback.py]] - code - tests/test_feedback.py
- [[test_funnel_does_not_treat_unknown_as_rejection()]] - code - tests/test_feedback.py
- [[test_persisted_calibration_leaves_scores_and_events_unchanged()]] - code - tests/test_calibration.py
- [[test_persisted_feedback_does_not_change_scores_or_history()]] - code - tests/test_feedback.py
- [[test_shrinkage_and_adjustment_bounds()]] - code - tests/test_feedback.py

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/test_feedbackpy
SORT file.name ASC
```

## Connections to other communities
- 16 edges to [[_COMMUNITY_feedback.py]]
- 13 edges to [[_COMMUNITY_AsyncSession]]
- 10 edges to [[_COMMUNITY_session_scope]]
- 9 edges to [[_COMMUNITY_db.py]]
- 7 edges to [[_COMMUNITY_calibration.py]]
- 7 edges to [[_COMMUNITY_tracker.py]]
- 7 edges to [[_COMMUNITY_test_calibration.py]]
- 5 edges to [[_COMMUNITY_test_application_tracker.py]]
- 5 edges to [[_COMMUNITY_Job]]
- 4 edges to [[_COMMUNITY_pytest]]
- 3 edges to [[_COMMUNITY_test_monitoring.py]]
- 3 edges to [[_COMMUNITY_Source]]
- 3 edges to [[_COMMUNITY_upsert_job]]
- 2 edges to [[_COMMUNITY_test_phase13_shortlist.py]]
- 1 edge to [[_COMMUNITY_pathlib]]

## Top bridge nodes
- [[test_feedback.py]] - degree 32, connects to 11 communities
- [[Application]] - degree 21, connects to 8 communities
- [[test_persisted_calibration_leaves_scores_and_events_unchanged()]] - degree 14, connects to 7 communities
- [[test_persisted_feedback_does_not_change_scores_or_history()]] - degree 17, connects to 6 communities
- [[ApplicationEvent]] - degree 16, connects to 6 communities