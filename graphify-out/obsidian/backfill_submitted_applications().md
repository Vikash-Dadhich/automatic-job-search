---
source_file: "automation/tracker.py"
type: "code"
community: "tracker.py"
location: "L273"
tags:
  - graphify/code
  - graphify/EXTRACTED
  - community/trackerpy
---

# backfill_submitted_applications()

## Connections
- [[Create one application for each submitted job that does not have one. Uses…]] - `rationale_for` [EXTRACTED]
- [[Job]] - `uses` [INFERRED]
- [[Outcome]] - `calls` [EXTRACTED]
- [[Status]] - `uses` [INFERRED]
- [[_stamp()_1]] - `calls` [EXTRACTED]
- [[db.py]] - `imports` [EXTRACTED]
- [[get_application_for_job()]] - `calls` [EXTRACTED]
- [[init_db()]] - `calls` [EXTRACTED]
- [[record_outcome()]] - `calls` [EXTRACTED]
- [[record_submitted()]] - `calls` [EXTRACTED]
- [[session_scope()]] - `calls` [EXTRACTED]
- [[tracker.py]] - `contains` [EXTRACTED]

#graphify/code #graphify/EXTRACTED #community/trackerpy