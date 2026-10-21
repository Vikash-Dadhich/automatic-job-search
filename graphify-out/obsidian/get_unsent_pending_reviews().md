---
source_file: "core/db.py"
type: "code"
community: "db.py"
location: "L1235"
tags:
  - graphify/code
  - graphify/EXTRACTED
  - community/dbpy
---

# get_unsent_pending_reviews()

## Connections
- [[AsyncSession_1]] - `references` [EXTRACTED]
- [[Job]] - `references` [EXTRACTED]
- [[Status lifecycle]] - `references` [INFERRED]
- [[db.py]] - `contains` [EXTRACTED]
- [[pending_review jobs that have not yet been sent to Telegram.]] - `rationale_for` [EXTRACTED]
- [[review.py]] - `imports` [EXTRACTED]
- [[send_pending_reviews()]] - `calls` [EXTRACTED]
- [[test_phase13_shortlist.py]] - `imports` [EXTRACTED]
- [[test_pipeline_enriches_the_review_queue_and_apply_stays_on_staged()]] - `calls` [EXTRACTED]

#graphify/code #graphify/EXTRACTED #community/dbpy