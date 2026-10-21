---
source_file: "core/db.py"
type: "code"
community: "test_application_tracker.py"
location: "L1521"
tags:
  - graphify/code
  - graphify/EXTRACTED
  - community/test_application_trackerpy
---

# get_application_for_job()

## Connections
- [[Application]] - `references` [EXTRACTED]
- [[AsyncSession_1]] - `references` [EXTRACTED]
- [[_get_or_create()]] - `calls` [EXTRACTED]
- [[application_history()]] - `calls` [EXTRACTED]
- [[backfill_submitted_applications()]] - `calls` [EXTRACTED]
- [[db.py]] - `contains` [EXTRACTED]
- [[record_withdrawn()]] - `calls` [EXTRACTED]
- [[test_a_later_outcome_keeps_the_earlier_event()]] - `calls` [EXTRACTED]
- [[test_application_tracker.py]] - `imports` [EXTRACTED]
- [[test_blocker_and_manual_takeover_are_not_submissions()]] - `calls` [EXTRACTED]
- [[test_each_outcome_is_stored_once()]] - `calls` [EXTRACTED]
- [[test_prefill_starts_an_application_without_submitting()]] - `calls` [EXTRACTED]
- [[test_submit_is_idempotent_and_discard_without_an_attempt_is_empty()]] - `calls` [EXTRACTED]
- [[tracker.py]] - `imports` [EXTRACTED]

#graphify/code #graphify/EXTRACTED #community/test_application_trackerpy