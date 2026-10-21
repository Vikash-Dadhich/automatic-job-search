---
source_file: "automation/tracker.py"
type: "code"
community: "test_application_tracker.py"
location: "L310"
tags:
  - graphify/code
  - graphify/EXTRACTED
  - community/test_application_trackerpy
---

# application_history()

## Connections
- [[ApplicationEvent]] - `uses` [INFERRED]
- [[get_application_events()]] - `calls` [EXTRACTED]
- [[get_application_for_job()]] - `calls` [EXTRACTED]
- [[session_scope()]] - `calls` [EXTRACTED]
- [[test_a_later_outcome_keeps_the_earlier_event()]] - `calls` [EXTRACTED]
- [[test_application_tracker.py]] - `imports` [EXTRACTED]
- [[test_each_outcome_is_stored_once()]] - `calls` [EXTRACTED]
- [[test_prefill_starts_an_application_without_submitting()]] - `calls` [EXTRACTED]
- [[test_submit_is_idempotent_and_discard_without_an_attempt_is_empty()]] - `calls` [EXTRACTED]
- [[tracker.py]] - `contains` [EXTRACTED]

#graphify/code #graphify/EXTRACTED #community/test_application_trackerpy