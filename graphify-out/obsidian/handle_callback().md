---
source_file: "bot/handlers.py"
type: "code"
community: "handle_callback"
location: "L272"
tags:
  - graphify/code
  - graphify/EXTRACTED
  - community/handle_callback
---

# handle_callback()

## Connections
- [[Any]] - `references` [EXTRACTED]
- [[Handle one Telegram update containing a callback_query. Returns the resulting…]] - `rationale_for` [EXTRACTED]
- [[ReviewAction]] - `uses` [INFERRED]
- [[Status]] - `uses` [INFERRED]
- [[Submitter]] - `uses` [INFERRED]
- [[TelegramClient]] - `calls` [EXTRACTED]
- [[WorkdaySubmitter]] - `calls` [EXTRACTED]
- [[_decision_caption()]] - `calls` [EXTRACTED]
- [[_handle_outcome_callback()]] - `calls` [EXTRACTED]
- [[_handle_suggest_callback()]] - `calls` [EXTRACTED]
- [[_safe_answer()]] - `calls` [EXTRACTED]
- [[bot__init__.py]] - `imports` [EXTRACTED]
- [[decode_callback()]] - `calls` [EXTRACTED]
- [[get_job_by_id()]] - `calls` [EXTRACTED]
- [[handlers.py]] - `contains` [EXTRACTED]
- [[init_db()]] - `calls` [EXTRACTED]
- [[is_outcome_callback()]] - `calls` [EXTRACTED]
- [[is_suggest_callback()]] - `calls` [EXTRACTED]
- [[poller.py]] - `imports` [EXTRACTED]
- [[process_updates()]] - `calls` [EXTRACTED]
- [[record_manual_review()]] - `calls` [EXTRACTED]
- [[record_submitted()]] - `calls` [EXTRACTED]
- [[record_withdrawn()]] - `calls` [EXTRACTED]
- [[send_outcome_prompt()]] - `calls` [EXTRACTED]
- [[session_scope()]] - `calls` [EXTRACTED]
- [[telegram_webhook()]] - `calls` [EXTRACTED]
- [[test_a_later_outcome_keeps_the_earlier_event()]] - `calls` [EXTRACTED]
- [[test_already_decided()]] - `calls` [EXTRACTED]
- [[test_application_tracker.py]] - `imports` [EXTRACTED]
- [[test_approve_blocker_manual()]] - `calls` [EXTRACTED]
- [[test_approve_still_submits()]] - `calls` [EXTRACTED]
- [[test_approve_submits()]] - `calls` [EXTRACTED]
- [[test_blocker_and_manual_takeover_are_not_submissions()]] - `calls` [EXTRACTED]
- [[test_discard()]] - `calls` [EXTRACTED]
- [[test_each_outcome_is_stored_once()]] - `calls` [EXTRACTED]
- [[test_handlers.py]] - `imports` [EXTRACTED]
- [[test_manual_takeover()]] - `calls` [EXTRACTED]
- [[test_outcome_tap_does_not_move_decided_at()]] - `calls` [EXTRACTED]
- [[test_outcome_tap_rejected_unless_submitted()]] - `calls` [EXTRACTED]
- [[test_outcomes.py]] - `imports` [EXTRACTED]
- [[test_submit_is_idempotent_and_discard_without_an_attempt_is_empty()]] - `calls` [EXTRACTED]
- [[test_unknown_job()]] - `calls` [EXTRACTED]
- [[webhook.py]] - `imports` [EXTRACTED]

#graphify/code #graphify/EXTRACTED #community/handle_callback