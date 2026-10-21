---
source_file: "tests/test_outcomes.py"
type: "code"
community: "handle_callback"
location: "L169"
tags:
  - graphify/code
  - graphify/EXTRACTED
  - community/handle_callback
---

# test_approve_still_submits()

## Connections
- [[FakeSubmitter]] - `calls` [EXTRACTED]
- [[FakeTransport_1]] - `calls` [EXTRACTED]
- [[Job]] - `calls` [EXTRACTED]
- [[Path]] - `references` [EXTRACTED]
- [[ReviewAction]] - `uses` [INFERRED]
- [[Source]] - `uses` [INFERRED]
- [[Status]] - `uses` [INFERRED]
- [[TelegramClient]] - `calls` [EXTRACTED]
- [[_callback_update()]] - `calls` [EXTRACTED]
- [[get_job_by_id()]] - `calls` [EXTRACTED]
- [[handle_callback()]] - `calls` [EXTRACTED]
- [[session_scope()]] - `calls` [EXTRACTED]
- [[test_outcomes.py]] - `contains` [EXTRACTED]
- [[upsert_job()]] - `calls` [EXTRACTED]

#graphify/code #graphify/EXTRACTED #community/handle_callback