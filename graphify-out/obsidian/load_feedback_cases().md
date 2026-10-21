---
source_file: "scorer/feedback.py"
type: "code"
community: "test_feedback.py"
location: "L440"
tags:
  - graphify/code
  - graphify/EXTRACTED
  - community/test_feedbackpy
---

# load_feedback_cases()

## Connections
- [[ApplicationEvent]] - `uses` [INFERRED]
- [[FeedbackCase]] - `references` [EXTRACTED]
- [[Read Phase 15 rows. Cutoff filtering happens in build_feedback.]] - `rationale_for` [EXTRACTED]
- [[_case_from_rows()]] - `calls` [EXTRACTED]
- [[calibration.py]] - `imports` [EXTRACTED]
- [[feedback.py]] - `contains` [EXTRACTED]
- [[init_db()]] - `calls` [EXTRACTED]
- [[list_events_for_applications()]] - `calls` [EXTRACTED]
- [[list_jobs_by_ids()]] - `calls` [EXTRACTED]
- [[list_submitted_applications()]] - `calls` [EXTRACTED]
- [[run_calibration()]] - `calls` [EXTRACTED]
- [[session_scope()]] - `calls` [EXTRACTED]
- [[test_feedback.py]] - `imports` [EXTRACTED]
- [[test_persisted_feedback_does_not_change_scores_or_history()]] - `calls` [EXTRACTED]

#graphify/code #graphify/EXTRACTED #community/test_feedbackpy