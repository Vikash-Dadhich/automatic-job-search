---
type: community
cohesion: 0.20
members: 28
---

# tracker.py

**Cohesion:** 0.20 - loosely connected
**Members:** 28 nodes

## Members
- [[A Workday pre-fill started. This is not a submission.]] - rationale - automation/tracker.py
- [[Abandon an attempt that already exists. A discard with no attempt is ignored.]] - rationale - automation/tracker.py
- [[ApplicationEventType]] - code - core/db.py
- [[ApplicationMethod]] - code - core/db.py
- [[ApplicationState]] - code - core/db.py
- [[AsyncSession_2]] - code
- [[Copy a post-submission outcome onto the application and keep the prior event.]] - rationale - automation/tracker.py
- [[Create one application for each submitted job that does not have one. Uses…]] - rationale - automation/tracker.py
- [[Hand-off or a blocked submit. Does not mark the application submitted.]] - rationale - automation/tracker.py
- [[Record a real submission. The first submitted_at is kept.]] - rationale - automation/tracker.py
- [[Record what happened to an application. This does not score or rank jobs.]] - rationale - automation/tracker.py
- [[StrEnum_5]] - code
- [[Where an actual application attempt stands. Not a job workflow status.]] - rationale - core/db.py
- [[Workday when the posting is a Workday application. Otherwise manual.]] - rationale - automation/tracker.py
- [[_add_event()]] - code - automation/tracker.py
- [[_event_exists()]] - code - automation/tracker.py
- [[_get_or_create()]] - code - automation/tracker.py
- [[_stamp()_1]] - code - automation/tracker.py
- [[_utcnow()]] - code - core/db.py
- [[application_method()]] - code - automation/tracker.py
- [[backfill_submitted_applications()]] - code - automation/tracker.py
- [[datetime_11]] - code
- [[record_manual_review()]] - code - automation/tracker.py
- [[record_outcome()]] - code - automation/tracker.py
- [[record_prefill()]] - code - automation/tracker.py
- [[record_submitted()]] - code - automation/tracker.py
- [[record_withdrawn()]] - code - automation/tracker.py
- [[tracker.py]] - code - automation/tracker.py

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/trackerpy
SORT file.name ASC
```

## Connections to other communities
- 17 edges to [[_COMMUNITY_session_scope]]
- 10 edges to [[_COMMUNITY_test_application_tracker.py]]
- 9 edges to [[_COMMUNITY_handlers.py]]
- 8 edges to [[_COMMUNITY_db.py]]
- 7 edges to [[_COMMUNITY_test_feedback.py]]
- 7 edges to [[_COMMUNITY_test_monitoring.py]]
- 4 edges to [[_COMMUNITY_Job]]
- 4 edges to [[_COMMUNITY_runner.py]]
- 3 edges to [[_COMMUNITY_Source]]
- 3 edges to [[_COMMUNITY_test_apply_url.py]]
- 3 edges to [[_COMMUNITY_handle_callback]]
- 2 edges to [[_COMMUNITY_diff.py]]
- 1 edge to [[_COMMUNITY_suggest.py]]
- 1 edge to [[_COMMUNITY_Tier]]
- 1 edge to [[_COMMUNITY_test_structured_jd.py]]
- 1 edge to [[_COMMUNITY_structured_jd.py]]
- 1 edge to [[_COMMUNITY_ingest.py]]
- 1 edge to [[_COMMUNITY_migrate_to_neon.py]]

## Top bridge nodes
- [[tracker.py]] - degree 36, connects to 11 communities
- [[StrEnum_5]] - degree 10, connects to 6 communities
- [[backfill_submitted_applications()]] - degree 12, connects to 5 communities
- [[record_submitted()]] - degree 16, connects to 4 communities
- [[record_manual_review()]] - degree 15, connects to 4 communities