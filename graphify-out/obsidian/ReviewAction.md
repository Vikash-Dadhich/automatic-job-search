---
source_file: "bot/telegram.py"
type: "code"
community: "handle_callback"
location: "L27"
tags:
  - graphify/code
  - graphify/INFERRED
  - community/handle_callback
---

# ReviewAction

## Connections
- [[StrEnum_2]] - `inherits` [EXTRACTED]
- [[_callback_update()]] - `uses` [INFERRED]
- [[_tap()]] - `uses` [INFERRED]
- [[bot__init__.py]] - `imports` [EXTRACTED]
- [[build_keyboard()]] - `uses` [INFERRED]
- [[decode_callback()]] - `calls` [EXTRACTED]
- [[encode_callback()]] - `calls` [EXTRACTED]
- [[handle_callback()]] - `uses` [INFERRED]
- [[handlers.py]] - `imports` [EXTRACTED]
- [[review.py]] - `imports` [EXTRACTED]
- [[telegram.py]] - `contains` [EXTRACTED]
- [[test_already_decided()]] - `uses` [INFERRED]
- [[test_application_tracker.py]] - `imports` [EXTRACTED]
- [[test_approve_blocker_manual()]] - `uses` [INFERRED]
- [[test_approve_still_submits()]] - `uses` [INFERRED]
- [[test_approve_submits()]] - `uses` [INFERRED]
- [[test_blocker_and_manual_takeover_are_not_submissions()]] - `uses` [INFERRED]
- [[test_decode_invalid()]] - `uses` [INFERRED]
- [[test_discard()]] - `uses` [INFERRED]
- [[test_encode_decode_roundtrip()]] - `uses` [INFERRED]
- [[test_handlers.py]] - `imports` [EXTRACTED]
- [[test_manual_takeover()]] - `uses` [INFERRED]
- [[test_outcomes.py]] - `imports` [EXTRACTED]
- [[test_poller.py]] - `imports` [EXTRACTED]
- [[test_process_updates_routes_callback()]] - `uses` [INFERRED]
- [[test_submit_is_idempotent_and_discard_without_an_attempt_is_empty()]] - `uses` [INFERRED]
- [[test_telegram.py]] - `imports` [EXTRACTED]
- [[test_unknown_job()]] - `uses` [INFERRED]

#graphify/code #graphify/INFERRED #community/handle_callback