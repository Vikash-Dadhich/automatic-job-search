---
source_file: "tests/test_application_tracker.py"
type: "code"
community: "test_application_tracker.py"
location: "L250"
tags:
  - graphify/code
  - graphify/EXTRACTED
  - community/test_application_trackerpy
---

# test_each_outcome_is_stored_once()

## Connections
- [[FakeTransport_1]] - `uses` [INFERRED]
- [[Outcome]] - `uses` [INFERRED]
- [[Path_54]] - `references` [EXTRACTED]
- [[Status]] - `uses` [INFERRED]
- [[TelegramClient]] - `uses` [INFERRED]
- [[_job()_17]] - `calls` [EXTRACTED]
- [[application_history()]] - `calls` [EXTRACTED]
- [[encode_outcome_callback()]] - `calls` [EXTRACTED]
- [[get_application_for_job()]] - `calls` [EXTRACTED]
- [[get_job_by_id()]] - `calls` [EXTRACTED]
- [[handle_callback()]] - `calls` [EXTRACTED]
- [[init_db()]] - `calls` [EXTRACTED]
- [[parametrize_5]] - `references` [EXTRACTED]
- [[record_outcome()]] - `calls` [EXTRACTED]
- [[session_scope()]] - `calls` [EXTRACTED]
- [[test_application_tracker.py]] - `contains` [EXTRACTED]
- [[upsert_job()]] - `calls` [EXTRACTED]

#graphify/code #graphify/EXTRACTED #community/test_application_trackerpy