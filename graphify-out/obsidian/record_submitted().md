---
source_file: "automation/tracker.py"
type: "code"
community: "tracker.py"
location: "L129"
tags:
  - graphify/code
  - graphify/EXTRACTED
  - community/trackerpy
---

# record_submitted()

## Connections
- [[ApplicationEventType]] - `uses` [INFERRED]
- [[ApplicationState]] - `uses` [INFERRED]
- [[Record a real submission. The first submitted_at is kept.]] - `rationale_for` [EXTRACTED]
- [[_add_event()]] - `calls` [EXTRACTED]
- [[_get_or_create()]] - `calls` [EXTRACTED]
- [[_stamp()_1]] - `calls` [EXTRACTED]
- [[_utcnow()]] - `calls` [EXTRACTED]
- [[backfill_submitted_applications()]] - `calls` [EXTRACTED]
- [[datetime_11]] - `references` [EXTRACTED]
- [[get_job_by_id()]] - `calls` [EXTRACTED]
- [[handle_callback()]] - `calls` [EXTRACTED]
- [[handlers.py]] - `imports` [EXTRACTED]
- [[session_scope()]] - `calls` [EXTRACTED]
- [[test_application_tracker.py]] - `imports` [EXTRACTED]
- [[test_submit_is_idempotent_and_discard_without_an_attempt_is_empty()]] - `calls` [EXTRACTED]
- [[tracker.py]] - `contains` [EXTRACTED]

#graphify/code #graphify/EXTRACTED #community/trackerpy