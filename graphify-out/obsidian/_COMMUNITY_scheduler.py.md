---
type: community
cohesion: 0.14
members: 23
---

# scheduler.py

**Cohesion:** 0.14 - loosely connected
**Members:** 23 nodes

## Members
- [[APScheduler construction for the 3xday pipeline.]] - rationale - orchestrator/scheduler.py
- [[Any_21]] - code
- [[AsyncIOScheduler]] - code
- [[Build (but do not start) an AsyncIOScheduler with one job per HHMM. Jobs use…]] - rationale - orchestrator/scheduler.py
- [[MonkeyPatch_10]] - code
- [[Offline tests for APScheduler construction (never started).]] - rationale - tests/test_scheduler.py
- [[Orchestration package (Step 7).]] - rationale - orchestrator/__init__.py
- [[Parse 'HHMM' into (hour, minute). Raises ValueError on bad input.]] - rationale - orchestrator/scheduler.py
- [[_noop()]] - code - tests/test_scheduler.py
- [[apscheduler_schedulers_asyncio]] - concept
- [[apscheduler_triggers_cron]] - concept
- [[build_scheduler()]] - code - orchestrator/scheduler.py
- [[collections_abc]] - concept
- [[orchestrator__init__.py]] - code - orchestrator/__init__.py
- [[parse_hhmm()]] - code - orchestrator/scheduler.py
- [[scheduler.py]] - code - orchestrator/scheduler.py
- [[test_build_scheduler_invalid_timezone()]] - code - tests/test_scheduler.py
- [[test_build_scheduler_registers_jobs()]] - code - tests/test_scheduler.py
- [[test_build_scheduler_skips_invalid_times()]] - code - tests/test_scheduler.py
- [[test_parse_hhmm()]] - code - tests/test_scheduler.py
- [[test_parse_hhmm_invalid()]] - code - tests/test_scheduler.py
- [[test_scheduler.py]] - code - tests/test_scheduler.py
- [[zoneinfo]] - concept

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/schedulerpy
SORT file.name ASC
```

## Connections to other communities
- 5 edges to [[_COMMUNITY_pipeline.py]]
- 5 edges to [[_COMMUNITY_asyncio]]
- 4 edges to [[_COMMUNITY_test_monitoring.py]]
- 4 edges to [[_COMMUNITY_pytest]]
- 3 edges to [[_COMMUNITY_get_settings]]
- 2 edges to [[_COMMUNITY_test_pacing.py]]
- 2 edges to [[_COMMUNITY_typing]]
- 1 edge to [[_COMMUNITY_conftest.py]]
- 1 edge to [[_COMMUNITY_browser.py]]
- 1 edge to [[_COMMUNITY_runner.py]]
- 1 edge to [[_COMMUNITY_ingest.py]]
- 1 edge to [[_COMMUNITY_re]]
- 1 edge to [[_COMMUNITY_db.py]]
- 1 edge to [[_COMMUNITY_main.py]]

## Top bridge nodes
- [[scheduler.py]] - degree 18, connects to 7 communities
- [[collections_abc]] - degree 8, connects to 7 communities
- [[build_scheduler()]] - degree 13, connects to 2 communities
- [[test_scheduler.py]] - degree 12, connects to 2 communities
- [[orchestrator__init__.py]] - degree 9, connects to 2 communities