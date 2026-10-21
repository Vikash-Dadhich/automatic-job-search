---
source_file: "automation/tracker.py"
type: "code"
community: "tracker.py"
location: "L227"
tags:
  - graphify/code
  - graphify/EXTRACTED
  - community/trackerpy
---

# record_outcome()

## Connections
- [[ApplicationEventType]] - `uses` [INFERRED]
- [[ApplicationState]] - `uses` [INFERRED]
- [[Copy a post-submission outcome onto the application and keep the prior event.]] - `rationale_for` [EXTRACTED]
- [[Outcome]] - `uses` [INFERRED]
- [[Status]] - `uses` [INFERRED]
- [[_add_event()]] - `calls` [EXTRACTED]
- [[_get_or_create()]] - `calls` [EXTRACTED]
- [[_handle_outcome_callback()]] - `calls` [EXTRACTED]
- [[_stamp()_1]] - `calls` [EXTRACTED]
- [[_utcnow()]] - `calls` [EXTRACTED]
- [[backfill_submitted_applications()]] - `calls` [EXTRACTED]
- [[datetime_11]] - `references` [EXTRACTED]
- [[get_job_by_id()]] - `calls` [EXTRACTED]
- [[handlers.py]] - `imports` [EXTRACTED]
- [[session_scope()]] - `calls` [EXTRACTED]
- [[test_application_tracker.py]] - `imports` [EXTRACTED]
- [[test_each_outcome_is_stored_once()]] - `calls` [EXTRACTED]
- [[tracker.py]] - `contains` [EXTRACTED]

#graphify/code #graphify/EXTRACTED #community/trackerpy