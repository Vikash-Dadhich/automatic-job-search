---
source_file: "core/db.py"
type: "code"
community: "test_feedback.py"
location: "L513"
tags:
  - graphify/code
  - graphify/EXTRACTED
  - community/test_feedbackpy
---

# ApplicationEvent

## Connections
- [[One factual application transition. Pipeline stages are not events.]] - `rationale_for` [EXTRACTED]
- [[SQLModel]] - `inherits` [EXTRACTED]
- [[_add_event()]] - `calls` [EXTRACTED]
- [[_case_from_rows()]] - `uses` [INFERRED]
- [[_event_exists()]] - `uses` [INFERRED]
- [[application_history()]] - `uses` [INFERRED]
- [[db.py]] - `contains` [EXTRACTED]
- [[feedback.py]] - `imports` [EXTRACTED]
- [[get_application_events()]] - `references` [EXTRACTED]
- [[list_events_for_applications()]] - `references` [EXTRACTED]
- [[load_feedback_cases()]] - `uses` [INFERRED]
- [[test_calibration.py]] - `imports` [EXTRACTED]
- [[test_feedback.py]] - `imports` [EXTRACTED]
- [[test_persisted_calibration_leaves_scores_and_events_unchanged()]] - `calls` [EXTRACTED]
- [[test_persisted_feedback_does_not_change_scores_or_history()]] - `calls` [EXTRACTED]
- [[tracker.py]] - `imports` [EXTRACTED]

#graphify/code #graphify/EXTRACTED #community/test_feedbackpy