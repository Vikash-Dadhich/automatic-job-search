---
source_file: "tests/test_application_tracker.py"
type: "code"
community: "test_application_tracker.py"
location: "L186"
tags:
  - graphify/code
  - graphify/EXTRACTED
  - community/test_application_trackerpy
---

# test_submit_is_idempotent_and_discard_without_an_attempt_is_empty()

## Connections
- [[FakeTransport_1]] - `calls` [EXTRACTED]
- [[Path_54]] - `references` [EXTRACTED]
- [[ReviewAction]] - `uses` [INFERRED]
- [[Status]] - `uses` [INFERRED]
- [[TelegramClient]] - `calls` [EXTRACTED]
- [[_Submitter]] - `calls` [EXTRACTED]
- [[_job()_17]] - `calls` [EXTRACTED]
- [[_tap()]] - `calls` [EXTRACTED]
- [[application_history()]] - `calls` [EXTRACTED]
- [[get_application_for_job()]] - `calls` [EXTRACTED]
- [[get_job_by_id()]] - `calls` [EXTRACTED]
- [[handle_callback()]] - `calls` [EXTRACTED]
- [[record_submitted()]] - `calls` [EXTRACTED]
- [[session_scope()]] - `calls` [EXTRACTED]
- [[test_application_tracker.py]] - `contains` [EXTRACTED]
- [[upsert_job()]] - `calls` [EXTRACTED]

#graphify/code #graphify/EXTRACTED #community/test_application_trackerpy