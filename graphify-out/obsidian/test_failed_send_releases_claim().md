---
source_file: "tests/test_outcomes.py"
type: "code"
community: "handlers.py"
location: "L82"
tags:
  - graphify/code
  - graphify/EXTRACTED
  - community/handlerspy
---

# test_failed_send_releases_claim()

## Connections
- [[FakeTransport_1]] - `uses` [INFERRED]
- [[Path]] - `references` [EXTRACTED]
- [[TelegramClient]] - `calls` [EXTRACTED]
- [[_submitted()]] - `calls` [EXTRACTED]
- [[get_job_by_id()]] - `calls` [EXTRACTED]
- [[post()]] - `contains` [EXTRACTED]
- [[send_outcome_prompt()]] - `calls` [EXTRACTED]
- [[session_scope()]] - `calls` [EXTRACTED]
- [[test_outcomes.py]] - `contains` [EXTRACTED]

#graphify/code #graphify/EXTRACTED #community/handlerspy