---
source_file: "bot/alerts.py"
type: "code"
community: "alerts.py"
location: "L51"
tags:
  - graphify/code
  - graphify/EXTRACTED
  - community/alertspy
---

# send_pending_alerts()

## Connections
- [[AlertSummary]] - `calls` [EXTRACTED]
- [[Notify on unsent manual_review  error jobs (screenshot + reason).]] - `rationale_for` [EXTRACTED]
- [[Run review bot (Step 6)]] - `references` [INFERRED]
- [[TelegramClient]] - `calls` [EXTRACTED]
- [[_send_one()]] - `calls` [EXTRACTED]
- [[alerts.py]] - `contains` [EXTRACTED]
- [[bot__init__.py]] - `imports` [EXTRACTED]
- [[get_unsent_alerts()]] - `calls` [EXTRACTED]
- [[init_db()]] - `calls` [EXTRACTED]
- [[pipeline.py]] - `indirect_call` [INFERRED]
- [[session_scope()]] - `calls` [EXTRACTED]
- [[test_alerts.py]] - `imports` [EXTRACTED]
- [[test_scoring_error_does_not_alert()]] - `calls` [EXTRACTED]
- [[test_send_pending_alerts_empty()]] - `calls` [EXTRACTED]
- [[test_send_pending_alerts_photo_and_skip()]] - `calls` [EXTRACTED]

#graphify/code #graphify/EXTRACTED #community/alertspy