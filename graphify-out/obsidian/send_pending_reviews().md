---
source_file: "bot/review.py"
type: "code"
community: "review.py"
location: "L121"
tags:
  - graphify/code
  - graphify/EXTRACTED
  - community/reviewpy
---

# send_pending_reviews()

## Connections
- [[ReviewSummary]] - `calls` [EXTRACTED]
- [[Send Telegram review cards for unsent pending_review jobs.]] - `rationale_for` [EXTRACTED]
- [[TelegramClient]] - `calls` [EXTRACTED]
- [[_cmd_send_reviews()]] - `calls` [EXTRACTED]
- [[_send_one()_1]] - `calls` [EXTRACTED]
- [[bot__init__.py]] - `imports` [EXTRACTED]
- [[get_unsent_pending_reviews()]] - `calls` [EXTRACTED]
- [[init_db()]] - `calls` [EXTRACTED]
- [[main.py]] - `imports` [EXTRACTED]
- [[pipeline.py]] - `indirect_call` [INFERRED]
- [[review.py]] - `contains` [EXTRACTED]
- [[session_scope()]] - `calls` [EXTRACTED]
- [[test_review.py]] - `imports` [EXTRACTED]
- [[test_send_pending_reviews_empty()]] - `calls` [EXTRACTED]
- [[test_send_pending_reviews_persists_message_id()]] - `calls` [EXTRACTED]

#graphify/code #graphify/EXTRACTED #community/reviewpy