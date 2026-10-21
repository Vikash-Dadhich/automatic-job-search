---
type: community
cohesion: 0.29
members: 18
---

# test_calibration.py

**Cohesion:** 0.29 - loosely connected
**Members:** 18 nodes

## Members
- [[Mean squared error of predicted rates against 01 outcomes.]] - rationale - scorer/calibration.py
- [[Temporal checks of feedback. They do not change scores or application history.]] - rationale - tests/test_calibration.py
- [[_calibration()]] - code - tests/test_calibration.py
- [[_case()]] - code - tests/test_calibration.py
- [[_feedback()]] - code - tests/test_calibration.py
- [[_rows()]] - code - tests/test_calibration.py
- [[brier_score()]] - code - scorer/calibration.py
- [[load_feedback_config()]] - code - scorer/feedback.py
- [[test_brier_score_is_mean_squared_error()]] - code - tests/test_calibration.py
- [[test_calibration.py]] - code - tests/test_calibration.py
- [[test_calibration_defaults_stay_off_the_production_path()]] - code - tests/test_calibration.py
- [[test_feedback_brier_beats_baseline_without_naming_a_winner()]] - code - tests/test_calibration.py
- [[test_folds_are_chronological_and_do_not_overlap()]] - code - tests/test_calibration.py
- [[test_future_outcomes_and_unknowns_do_not_count_as_failures()]] - code - tests/test_calibration.py
- [[test_immature_applications_and_sparse_segments_fall_back()]] - code - tests/test_calibration.py
- [[test_offer_is_scored_separately_from_interview()]] - code - tests/test_calibration.py
- [[test_sparse_offer_rate_falls_back_to_the_training_baseline()]] - code - tests/test_calibration.py
- [[test_too_little_history_is_a_report_not_a_failure()]] - code - tests/test_calibration.py

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/test_calibrationpy
SORT file.name ASC
```

## Connections to other communities
- 24 edges to [[_COMMUNITY_calibration.py]]
- 7 edges to [[_COMMUNITY_test_feedback.py]]
- 5 edges to [[_COMMUNITY_feedback.py]]
- 4 edges to [[_COMMUNITY_AsyncSession]]
- 3 edges to [[_COMMUNITY_session_scope]]
- 2 edges to [[_COMMUNITY_pytest]]
- 1 edge to [[_COMMUNITY_Source]]
- 1 edge to [[_COMMUNITY_Job]]
- 1 edge to [[_COMMUNITY_upsert_job]]
- 1 edge to [[_COMMUNITY_baseline.py]]
- 1 edge to [[_COMMUNITY_pathlib]]
- 1 edge to [[_COMMUNITY_db.py]]

## Top bridge nodes
- [[test_calibration.py]] - degree 39, connects to 11 communities
- [[load_feedback_config()]] - degree 15, connects to 4 communities
- [[test_offer_is_scored_separately_from_interview()]] - degree 10, connects to 3 communities
- [[_case()]] - degree 9, connects to 1 community
- [[_calibration()]] - degree 8, connects to 1 community