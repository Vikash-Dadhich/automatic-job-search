---
source_file: "core/db.py"
type: "code"
community: "AsyncSession"
location: "L1487"
tags:
  - graphify/code
  - graphify/EXTRACTED
  - community/AsyncSession
---

# get_unsent_suggestion_jobs()

## Connections
- [[AsyncSession_1]] - `references` [EXTRACTED]
- [[Job]] - `references` [EXTRACTED]
- [[Jobs that have pending suggestions not yet sent to Telegram.]] - `rationale_for` [EXTRACTED]
- [[db.py]] - `contains` [EXTRACTED]
- [[get_job_by_id()]] - `calls` [EXTRACTED]
- [[send_pending_suggestions()]] - `calls` [EXTRACTED]
- [[suggest.py]] - `imports` [EXTRACTED]

#graphify/code #graphify/EXTRACTED #community/AsyncSession