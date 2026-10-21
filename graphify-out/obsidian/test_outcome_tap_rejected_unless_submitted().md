---
source_file: "tests/test_outcomes.py"
type: "code"
community: "handlers.py"
location: "L148"
tags:
  - graphify/code
  - graphify/EXTRACTED
  - community/handlerspy
---

# test_outcome_tap_rejected_unless_submitted()

## Connections
- [[FakeTransport_1]] - `calls` [EXTRACTED]
- [[Job]] - `calls` [EXTRACTED]
- [[Outcome]] - `uses` [INFERRED]
- [[Path]] - `references` [EXTRACTED]
- [[Source]] - `uses` [INFERRED]
- [[Status]] - `uses` [INFERRED]
- [[TelegramClient]] - `calls` [EXTRACTED]
- [[_outcome_update()]] - `calls` [EXTRACTED]
- [[get_job_by_id()]] - `calls` [EXTRACTED]
- [[handle_callback()]] - `calls` [EXTRACTED]
- [[session_scope()]] - `calls` [EXTRACTED]
- [[test_outcomes.py]] - `contains` [EXTRACTED]
- [[upsert_job()]] - `calls` [EXTRACTED]

#graphify/code #graphify/EXTRACTED #community/handlerspy