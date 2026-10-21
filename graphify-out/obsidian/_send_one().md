---
source_file: "bot/alerts.py"
type: "code"
community: "alerts.py"
location: "L91"
tags:
  - graphify/code
  - graphify/EXTRACTED
  - community/alertspy
---

# _send_one()

## Connections
- [[Job]] - `uses` [INFERRED]
- [[Status]] - `uses` [INFERRED]
- [[TelegramClient]] - `uses` [INFERRED]
- [[alerts.py]] - `contains` [EXTRACTED]
- [[build_alert_caption()]] - `calls` [EXTRACTED]
- [[get_job_by_id()]] - `calls` [EXTRACTED]
- [[send_pending_alerts()]] - `calls` [EXTRACTED]
- [[session_scope()]] - `calls` [EXTRACTED]

#graphify/code #graphify/EXTRACTED #community/alertspy