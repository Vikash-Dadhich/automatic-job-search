---
type: community
cohesion: 0.25
members: 21
---

# test_application_tracker.py

**Cohesion:** 0.25 - loosely connected
**Members:** 21 nodes

## Members
- [[dot-__init__()_33]] - code - tests/test_application_tracker.py
- [[dot-apply()_7]] - code - tests/test_application_tracker.py
- [[dot-submit()_3]] - code - tests/test_application_tracker.py
- [[Application history starts only when an application does.]] - rationale - tests/test_application_tracker.py
- [[Path_54]] - code
- [[SubmitResult]] - code - bot/submit.py
- [[_Prefill]] - code - tests/test_application_tracker.py
- [[_Submitter]] - code - tests/test_application_tracker.py
- [[_count()]] - code - tests/test_application_tracker.py
- [[_job()_17]] - code - tests/test_application_tracker.py
- [[_tap()]] - code - tests/test_application_tracker.py
- [[application_history()]] - code - automation/tracker.py
- [[get_application_for_job()]] - code - core/db.py
- [[parametrize_5]] - code
- [[test_a_later_outcome_keeps_the_earlier_event()]] - code - tests/test_application_tracker.py
- [[test_application_tracker.py]] - code - tests/test_application_tracker.py
- [[test_blocker_and_manual_takeover_are_not_submissions()]] - code - tests/test_application_tracker.py
- [[test_each_outcome_is_stored_once()]] - code - tests/test_application_tracker.py
- [[test_prefill_starts_an_application_without_submitting()]] - code - tests/test_application_tracker.py
- [[test_staging_and_portfolio_do_not_create_an_application()]] - code - tests/test_application_tracker.py
- [[test_submit_is_idempotent_and_discard_without_an_attempt_is_empty()]] - code - tests/test_application_tracker.py

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/test_application_trackerpy
SORT file.name ASC
```

## Connections to other communities
- 25 edges to [[_COMMUNITY_session_scope]]
- 11 edges to [[_COMMUNITY_handle_callback]]
- 10 edges to [[_COMMUNITY_pathlib]]
- 10 edges to [[_COMMUNITY_tracker.py]]
- 8 edges to [[_COMMUNITY_handlers.py]]
- 8 edges to [[_COMMUNITY_runner.py]]
- 7 edges to [[_COMMUNITY_upsert_job]]
- 5 edges to [[_COMMUNITY_TelegramClient]]
- 5 edges to [[_COMMUNITY_test_feedback.py]]
- 5 edges to [[_COMMUNITY_Source]]
- 5 edges to [[_COMMUNITY_Job]]
- 4 edges to [[_COMMUNITY_workday.py]]
- 4 edges to [[_COMMUNITY_db.py]]
- 2 edges to [[_COMMUNITY_bot__init__.py]]
- 1 edge to [[_COMMUNITY_AsyncSession]]
- 1 edge to [[_COMMUNITY_pytest]]
- 1 edge to [[_COMMUNITY_baseline.py]]
- 1 edge to [[_COMMUNITY_test_monitoring.py]]

## Top bridge nodes
- [[test_application_tracker.py]] - degree 48, connects to 16 communities
- [[test_each_outcome_is_stored_once()]] - degree 17, connects to 8 communities
- [[test_blocker_and_manual_takeover_are_not_submissions()]] - degree 17, connects to 7 communities
- [[test_submit_is_idempotent_and_discard_without_an_attempt_is_empty()]] - degree 16, connects to 6 communities
- [[test_a_later_outcome_keeps_the_earlier_event()]] - degree 14, connects to 6 communities