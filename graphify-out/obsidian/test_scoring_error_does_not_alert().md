---
source_file: "tests/test_alerts.py"
type: "code"
community: "alerts.py"
location: "L79"
tags:
  - graphify/code
  - graphify/EXTRACTED
  - community/alertspy
---

# test_scoring_error_does_not_alert()

## Connections
- [[FakeTransport_1]] - `calls` [EXTRACTED]
- [[Job]] - `calls` [EXTRACTED]
- [[Path_3]] - `references` [EXTRACTED]
- [[Source]] - `uses` [INFERRED]
- [[Status]] - `uses` [INFERRED]
- [[TelegramClient]] - `calls` [EXTRACTED]
- [[get_job_by_id()]] - `calls` [EXTRACTED]
- [[send_pending_alerts()]] - `calls` [EXTRACTED]
- [[session_scope()]] - `calls` [EXTRACTED]
- [[test_alerts.py]] - `contains` [EXTRACTED]
- [[upsert_job()]] - `calls` [EXTRACTED]

#graphify/code #graphify/EXTRACTED #community/alertspy