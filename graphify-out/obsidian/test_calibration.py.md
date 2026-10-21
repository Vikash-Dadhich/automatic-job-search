---
source_file: "tests/test_calibration.py"
type: "code"
community: "test_calibration.py"
location: "L1"
tags:
  - graphify/code
  - graphify/EXTRACTED
  - community/test_calibrationpy
---

# test_calibration.py

## Connections
- [[Application]] - `imports` [EXTRACTED]
- [[ApplicationEvent]] - `imports` [EXTRACTED]
- [[CalibrationMetricRow]] - `imports` [EXTRACTED]
- [[CalibrationReport]] - `imports` [EXTRACTED]
- [[FeedbackCase]] - `imports` [EXTRACTED]
- [[Job]] - `imports` [EXTRACTED]
- [[Source]] - `imports` [EXTRACTED]
- [[Status]] - `imports` [EXTRACTED]
- [[Temporal checks of feedback. They do not change scores or application history.]] - `rationale_for` [EXTRACTED]
- [[_calibration()]] - `contains` [EXTRACTED]
- [[_case()]] - `contains` [EXTRACTED]
- [[_feedback()]] - `contains` [EXTRACTED]
- [[_rows()]] - `contains` [EXTRACTED]
- [[brier_score()]] - `imports` [EXTRACTED]
- [[build_calibration()]] - `imports` [EXTRACTED]
- [[calibration.py]] - `imports_from` [EXTRACTED]
- [[datetime_17]] - `imports_from` [EXTRACTED]
- [[db.py]] - `imports_from` [EXTRACTED]
- [[feedback.py]] - `imports_from` [EXTRACTED]
- [[get_application_events()]] - `imports` [EXTRACTED]
- [[get_job_by_id()]] - `imports` [EXTRACTED]
- [[load_calibration_config()]] - `imports` [EXTRACTED]
- [[load_feedback_config()]] - `imports` [EXTRACTED]
- [[load_persisted_calibration()]] - `imports` [EXTRACTED]
- [[pathlib]] - `imports_from` [EXTRACTED]
- [[persist_calibration()]] - `imports` [EXTRACTED]
- [[run_calibration()]] - `imports` [EXTRACTED]
- [[session_scope()]] - `imports` [EXTRACTED]
- [[test_brier_score_is_mean_squared_error()]] - `contains` [EXTRACTED]
- [[test_calibration_defaults_stay_off_the_production_path()]] - `contains` [EXTRACTED]
- [[test_feedback_brier_beats_baseline_without_naming_a_winner()]] - `contains` [EXTRACTED]
- [[test_folds_are_chronological_and_do_not_overlap()]] - `contains` [EXTRACTED]
- [[test_future_outcomes_and_unknowns_do_not_count_as_failures()]] - `contains` [EXTRACTED]
- [[test_immature_applications_and_sparse_segments_fall_back()]] - `contains` [EXTRACTED]
- [[test_offer_is_scored_separately_from_interview()]] - `contains` [EXTRACTED]
- [[test_persisted_calibration_leaves_scores_and_events_unchanged()]] - `contains` [EXTRACTED]
- [[test_sparse_offer_rate_falls_back_to_the_training_baseline()]] - `contains` [EXTRACTED]
- [[test_too_little_history_is_a_report_not_a_failure()]] - `contains` [EXTRACTED]
- [[upsert_job()]] - `imports` [EXTRACTED]

#graphify/code #graphify/EXTRACTED #community/test_calibrationpy