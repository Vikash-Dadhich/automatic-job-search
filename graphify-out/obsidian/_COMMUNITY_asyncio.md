---
type: community
cohesion: 0.18
members: 17
---

# asyncio

**Cohesion:** 0.18 - loosely connected
**Members:** 17 nodes

## Members
- [[Event_1]] - code
- [[Long-running service APScheduler + Telegram long-poll.]] - rationale - orchestrator/service.py
- [[MonkeyPatch_1]] - code
- [[Offline tests for run_service lifecycle (no real polling).]] - rationale - tests/test_service.py
- [[Path_1]] - code
- [[Scheduler starts; preset stop_event exits cleanly with run_poller=False.]] - rationale - tests/test_service.py
- [[Start the scheduler and (optionally) the Telegram poller until stopped.…]] - rationale - orchestrator/service.py
- [[_request_shutdown()]] - code - orchestrator/service.py
- [[asyncio_11]] - concept
- [[fake_polling()]] - code - tests/test_service.py
- [[run_service()]] - code - orchestrator/service.py
- [[service.py]] - code - orchestrator/service.py
- [[signal]] - concept
- [[stopper()]] - code - tests/test_service.py
- [[test_run_service_stops_without_poller()]] - code - tests/test_service.py
- [[test_run_service_with_poller_respects_stop()]] - code - tests/test_service.py
- [[test_service.py]] - code - tests/test_service.py

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/asyncio
SORT file.name ASC
```

## Connections to other communities
- 6 edges to [[_COMMUNITY_bot__init__.py]]
- 6 edges to [[_COMMUNITY_main.py]]
- 5 edges to [[_COMMUNITY_scheduler.py]]
- 4 edges to [[_COMMUNITY_workday_rest.py]]
- 3 edges to [[_COMMUNITY_get_settings]]
- 3 edges to [[_COMMUNITY_db.py]]
- 2 edges to [[_COMMUNITY_workday.py]]
- 2 edges to [[_COMMUNITY_clients.py]]
- 2 edges to [[_COMMUNITY_linkedin_jobspy.py]]
- 2 edges to [[_COMMUNITY_ingest.py]]
- 2 edges to [[_COMMUNITY_typing]]
- 2 edges to [[_COMMUNITY_pathlib]]
- 2 edges to [[_COMMUNITY_browser.py]]
- 2 edges to [[_COMMUNITY_scorerengine.py]]
- 1 edge to [[_COMMUNITY_Source]]
- 1 edge to [[_COMMUNITY_pytest]]
- 1 edge to [[_COMMUNITY_test_pacing.py]]
- 1 edge to [[_COMMUNITY_re]]
- 1 edge to [[_COMMUNITY_test_monitoring.py]]
- 1 edge to [[_COMMUNITY_migrate_to_neon.py]]

## Top bridge nodes
- [[asyncio_11]] - degree 28, connects to 15 communities
- [[service.py]] - degree 18, connects to 7 communities
- [[run_service()]] - degree 17, connects to 5 communities
- [[test_service.py]] - degree 9, connects to 3 communities