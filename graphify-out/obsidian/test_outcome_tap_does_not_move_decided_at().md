---
source_file: "tests/test_outcomes.py"
type: "code"
community: "handlers.py"
location: "L118"
tags:
  - graphify/code
  - graphify/EXTRACTED
  - community/handlerspy
---

# test_outcome_tap_does_not_move_decided_at()

## Connections
- [[FakeTransport_1]] - `calls` [EXTRACTED]
- [[Outcome]] - `uses` [INFERRED]
- [[Path]] - `references` [EXTRACTED]
- [[Status]] - `uses` [INFERRED]
- [[TelegramClient]] - `calls` [EXTRACTED]
- [[_outcome_update()]] - `calls` [EXTRACTED]
- [[_submitted()]] - `calls` [EXTRACTED]
- [[get_job_by_id()]] - `calls` [EXTRACTED]
- [[handle_callback()]] - `calls` [EXTRACTED]
- [[session_scope()]] - `calls` [EXTRACTED]
- [[test_outcomes.py]] - `contains` [EXTRACTED]

#graphify/code #graphify/EXTRACTED #community/handlerspy