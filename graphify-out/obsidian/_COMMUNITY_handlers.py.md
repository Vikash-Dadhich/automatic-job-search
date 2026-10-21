---
type: community
cohesion: 0.09
members: 49
---

# handlers.py

**Cohesion:** 0.09 - loosely connected
**Members:** 49 nodes

## Members
- [[Ack a callback_query; never raise (expiredfake IDs return Telegram 400).]] - rationale - bot/handlers.py
- [[Any]] - code
- [[Any_1]] - code
- [[Backfill outcome keyboards for submitted jobs that never got one.]] - rationale - bot/outcomes.py
- [[Clear an in-progress send so the next run can retry.]] - rationale - core/db.py
- [[Decode outcome callback_data into (outcome, job_id).]] - rationale - bot/telegram.py
- [[Dispatch Telegram callback_query decisions for pending_review jobs and skill…]] - rationale - bot/handlers.py
- [[Encode outcome callback_data o1outcomejob_id (=64 bytes).]] - rationale - bot/telegram.py
- [[Handle s1approveid  edit  reject suggestion callbacks.]] - rationale - bot/handlers.py
- [[Offline tests for outcome labels, claim, and Telegram callbacks.]] - rationale - tests/test_outcomes.py
- [[Outcome]] - code - core/db.py
- [[OutcomePromptSummary]] - code - bot/outcomes.py
- [[Path]] - code
- [[Post-submission result. Stored as VARCHAR, validated in Python.]] - rationale - core/db.py
- [[Record a post-submit label. Does not change status or decided_at.]] - rationale - bot/handlers.py
- [[Send one outcome keyboard. Never raises. False when the claim loses or send…]] - rationale - bot/outcomes.py
- [[Store the Telegram message id. Only replaces the in-progress sentinel.]] - rationale - core/db.py
- [[Submitted jobs that have not been sent an outcome keyboard.]] - rationale - core/db.py
- [[Telegram outcome keyboards for jobs that were actually submitted.]] - rationale - bot/outcomes.py
- [[Two-row keyboard. Callbacks stay well under Telegram's 64-byte cap.]] - rationale - bot/outcomes.py
- [[_decision_caption()]] - code - bot/handlers.py
- [[_handle_outcome_callback()]] - code - bot/handlers.py
- [[_handle_suggest_callback()]] - code - bot/handlers.py
- [[_outcome_update()]] - code - tests/test_outcomes.py
- [[_safe_answer()]] - code - bot/handlers.py
- [[_submitted()]] - code - tests/test_outcomes.py
- [[build_outcome_keyboard()]] - code - bot/outcomes.py
- [[button()]] - code - bot/outcomes.py
- [[decode_outcome_callback()]] - code - bot/telegram.py
- [[encode_outcome_callback()]] - code - bot/telegram.py
- [[finish_outcome_prompt()]] - code - core/db.py
- [[get_jobs_needing_outcome_prompt()]] - code - core/db.py
- [[handlers.py]] - code - bot/handlers.py
- [[is_suggest_callback()]] - code - bot/telegram.py
- [[outcome_label()]] - code - bot/outcomes.py
- [[outcome_message_text()]] - code - bot/outcomes.py
- [[outcomes.py]] - code - bot/outcomes.py
- [[post()]] - code - tests/test_outcomes.py
- [[release_outcome_prompt()]] - code - core/db.py
- [[send_outcome_prompt()]] - code - bot/outcomes.py
- [[send_pending_outcome_prompts()]] - code - bot/outcomes.py
- [[test_claim_is_single_winner_and_release_retries()]] - code - tests/test_outcomes.py
- [[test_failed_send_releases_claim()]] - code - tests/test_outcomes.py
- [[test_outcome_callback_roundtrip()]] - code - tests/test_outcomes.py
- [[test_outcome_tap_does_not_move_decided_at()]] - code - tests/test_outcomes.py
- [[test_outcome_tap_rejected_unless_submitted()]] - code - tests/test_outcomes.py
- [[test_outcomes.py]] - code - tests/test_outcomes.py
- [[test_review_decoder_rejects_outcome_payload()]] - code - tests/test_outcomes.py
- [[update()]] - code - tests/test_application_tracker.py

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/handlerspy
SORT file.name ASC
```

## Connections to other communities
- 28 edges to [[_COMMUNITY_session_scope]]
- 19 edges to [[_COMMUNITY_handle_callback]]
- 17 edges to [[_COMMUNITY_pathlib]]
- 12 edges to [[_COMMUNITY_db.py]]
- 11 edges to [[_COMMUNITY_suggest.py]]
- 11 edges to [[_COMMUNITY_TelegramClient]]
- 10 edges to [[_COMMUNITY_Job]]
- 9 edges to [[_COMMUNITY_tracker.py]]
- 8 edges to [[_COMMUNITY_test_application_tracker.py]]
- 8 edges to [[_COMMUNITY_AsyncSession]]
- 4 edges to [[_COMMUNITY_typing]]
- 3 edges to [[_COMMUNITY_bot__init__.py]]
- 3 edges to [[_COMMUNITY_Source]]
- 3 edges to [[_COMMUNITY_upsert_job]]
- 2 edges to [[_COMMUNITY_pipeline.py]]
- 2 edges to [[_COMMUNITY_ingest.py]]
- 2 edges to [[_COMMUNITY_baseline.py]]
- 1 edge to [[_COMMUNITY_main.py]]
- 1 edge to [[_COMMUNITY_test_doctor.py]]
- 1 edge to [[_COMMUNITY_WorkdaySubmitter]]
- 1 edge to [[_COMMUNITY_workday.py]]
- 1 edge to [[_COMMUNITY_test_resume.py]]

## Top bridge nodes
- [[handlers.py]] - degree 45, connects to 15 communities
- [[test_outcomes.py]] - degree 38, connects to 11 communities
- [[outcomes.py]] - degree 27, connects to 10 communities
- [[test_outcome_tap_rejected_unless_submitted()]] - degree 13, connects to 7 communities
- [[Outcome]] - degree 25, connects to 6 communities