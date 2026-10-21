---
source_file: "core/db.py"
type: "code"
community: "test_feedback.py"
location: "L493"
tags:
  - graphify/code
  - graphify/EXTRACTED
  - community/test_feedbackpy
---

# Application

## Connections
- [[One application lifecycle for a canonical job. Not created by discovery.]] - `rationale_for` [EXTRACTED]
- [[SQLModel]] - `inherits` [EXTRACTED]
- [[_add_event()]] - `uses` [INFERRED]
- [[_case_from_rows()]] - `uses` [INFERRED]
- [[_count()]] - `uses` [INFERRED]
- [[_get_or_create()]] - `calls` [EXTRACTED]
- [[db.py]] - `contains` [EXTRACTED]
- [[feedback.py]] - `imports` [EXTRACTED]
- [[get_application_by_id()]] - `references` [EXTRACTED]
- [[get_application_for_job()]] - `references` [EXTRACTED]
- [[list_submitted_applications()]] - `references` [EXTRACTED]
- [[test_a_new_run_does_not_duplicate_applications()]] - `calls` [EXTRACTED]
- [[test_application_tracker.py]] - `imports` [EXTRACTED]
- [[test_apply_shortlist_is_idempotent_and_preserves_scores()]] - `uses` [INFERRED]
- [[test_calibration.py]] - `imports` [EXTRACTED]
- [[test_feedback.py]] - `imports` [EXTRACTED]
- [[test_monitoring.py]] - `imports` [EXTRACTED]
- [[test_persisted_calibration_leaves_scores_and_events_unchanged()]] - `calls` [EXTRACTED]
- [[test_persisted_feedback_does_not_change_scores_or_history()]] - `calls` [EXTRACTED]
- [[test_phase13_shortlist.py]] - `imports` [EXTRACTED]
- [[tracker.py]] - `imports` [EXTRACTED]

#graphify/code #graphify/EXTRACTED #community/test_feedbackpy