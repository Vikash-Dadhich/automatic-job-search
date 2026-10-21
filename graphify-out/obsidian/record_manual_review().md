---
source_file: "automation/tracker.py"
type: "code"
community: "tracker.py"
location: "L170"
tags:
  - graphify/code
  - graphify/EXTRACTED
  - community/trackerpy
---

# record_manual_review()

## Connections
- [[dot-_persist_blocker()]] - `calls` [EXTRACTED]
- [[ApplicationEventType]] - `uses` [INFERRED]
- [[ApplicationState]] - `uses` [INFERRED]
- [[Hand-off or a blocked submit. Does not mark the application submitted.]] - `rationale_for` [EXTRACTED]
- [[_add_event()]] - `calls` [EXTRACTED]
- [[_get_or_create()]] - `calls` [EXTRACTED]
- [[_stamp()_1]] - `calls` [EXTRACTED]
- [[_utcnow()]] - `calls` [EXTRACTED]
- [[datetime_11]] - `references` [EXTRACTED]
- [[get_job_by_id()]] - `calls` [EXTRACTED]
- [[handle_callback()]] - `calls` [EXTRACTED]
- [[handlers.py]] - `imports` [EXTRACTED]
- [[runner.py]] - `imports` [EXTRACTED]
- [[session_scope()]] - `calls` [EXTRACTED]
- [[tracker.py]] - `contains` [EXTRACTED]

#graphify/code #graphify/EXTRACTED #community/trackerpy