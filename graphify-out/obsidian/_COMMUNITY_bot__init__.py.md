---
type: community
cohesion: 0.15
members: 18
---

# bot/__init__.py

**Cohesion:** 0.15 - loosely connected
**Members:** 18 nodes

## Members
- [[dot-submit()]] - code - bot/submit.py
- [[Any_3]] - code
- [[Event]] - code
- [[Injectable submitter used by handlers (mockable offline).]] - rationale - bot/submit.py
- [[Long-poll Telegram getUpdates until stop_event is set (or max_iterations).…]] - rationale - bot/poller.py
- [[Long-polling loop for Telegram callback_query updates.]] - rationale - bot/poller.py
- [[Protocol]] - code
- [[ReviewSummary]] - code - bot/review.py
- [[Route a batch of updates; return the next offset (last update_id + 1).]] - rationale - bot/poller.py
- [[Submitter]] - code - bot/submit.py
- [[Telegram review bot (Step 6).]] - rationale - bot/__init__.py
- [[__init__()]] - code - tests/test_poller.py
- [[bot__init__.py]] - code - bot/__init__.py
- [[poller.py]] - code - bot/poller.py
- [[post()_1]] - code - tests/test_poller.py
- [[process_updates()]] - code - bot/poller.py
- [[run_polling()]] - code - bot/poller.py
- [[test_run_polling_max_iterations()]] - code - tests/test_poller.py

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/bot/__init__py
SORT file.name ASC
```

## Connections to other communities
- 10 edges to [[_COMMUNITY_pathlib]]
- 8 edges to [[_COMMUNITY_suggest.py]]
- 6 edges to [[_COMMUNITY_handle_callback]]
- 6 edges to [[_COMMUNITY_TelegramClient]]
- 6 edges to [[_COMMUNITY_asyncio]]
- 4 edges to [[_COMMUNITY_review.py]]
- 4 edges to [[_COMMUNITY_Job]]
- 3 edges to [[_COMMUNITY_handlers.py]]
- 3 edges to [[_COMMUNITY_workday.py]]
- 3 edges to [[_COMMUNITY_alerts.py]]
- 3 edges to [[_COMMUNITY_WorkdaySubmitter]]
- 2 edges to [[_COMMUNITY_test_application_tracker.py]]
- 2 edges to [[_COMMUNITY_main.py]]
- 2 edges to [[_COMMUNITY_typing]]
- 1 edge to [[_COMMUNITY_conftest.py]]
- 1 edge to [[_COMMUNITY_send_prep_pack]]
- 1 edge to [[_COMMUNITY_ingest.py]]

## Top bridge nodes
- [[bot__init__.py]] - degree 32, connects to 13 communities
- [[poller.py]] - degree 17, connects to 10 communities
- [[run_polling()]] - degree 16, connects to 6 communities
- [[process_updates()]] - degree 11, connects to 4 communities
- [[Submitter]] - degree 11, connects to 4 communities