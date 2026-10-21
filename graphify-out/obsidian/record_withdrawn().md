---
source_file: "automation/tracker.py"
type: "code"
community: "tracker.py"
location: "L203"
tags:
  - graphify/code
  - graphify/EXTRACTED
  - community/trackerpy
---

# record_withdrawn()

## Connections
- [[Abandon an attempt that already exists. A discard with no attempt is ignored.]] - `rationale_for` [EXTRACTED]
- [[ApplicationEventType]] - `uses` [INFERRED]
- [[ApplicationState]] - `uses` [INFERRED]
- [[_add_event()]] - `calls` [EXTRACTED]
- [[_stamp()_1]] - `calls` [EXTRACTED]
- [[_utcnow()]] - `calls` [EXTRACTED]
- [[datetime_11]] - `references` [EXTRACTED]
- [[get_application_for_job()]] - `calls` [EXTRACTED]
- [[get_job_by_id()]] - `calls` [EXTRACTED]
- [[handle_callback()]] - `calls` [EXTRACTED]
- [[handlers.py]] - `imports` [EXTRACTED]
- [[session_scope()]] - `calls` [EXTRACTED]
- [[tracker.py]] - `contains` [EXTRACTED]

#graphify/code #graphify/EXTRACTED #community/trackerpy