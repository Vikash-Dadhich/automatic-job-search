---
type: community
cohesion: 0.23
members: 16
---

# alerts.py

**Cohesion:** 0.23 - loosely connected
**Members:** 16 nodes

## Members
- [[AlertSummary]] - code - bot/alerts.py
- [[Caption for a blocker  error alert.]] - rationale - bot/alerts.py
- [[Notify on unsent manual_review  error jobs (screenshot + reason).]] - rationale - bot/alerts.py
- [[Offline tests for blockererror Telegram alerts.]] - rationale - tests/test_alerts.py
- [[Path_3]] - code
- [[Telegram alerts for blocked  errored jobs (not pending_review cards).]] - rationale - bot/alerts.py
- [[_send_one()]] - code - bot/alerts.py
- [[_tiny_png()]] - code - tests/test_alerts.py
- [[alerts.py]] - code - bot/alerts.py
- [[build_alert_caption()]] - code - bot/alerts.py
- [[send_pending_alerts()]] - code - bot/alerts.py
- [[test_alerts.py]] - code - tests/test_alerts.py
- [[test_build_alert_caption()]] - code - tests/test_alerts.py
- [[test_scoring_error_does_not_alert()]] - code - tests/test_alerts.py
- [[test_send_pending_alerts_empty()]] - code - tests/test_alerts.py
- [[test_send_pending_alerts_photo_and_skip()]] - code - tests/test_alerts.py

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/alertspy
SORT file.name ASC
```

## Connections to other communities
- 17 edges to [[_COMMUNITY_session_scope]]
- 9 edges to [[_COMMUNITY_pathlib]]
- 7 edges to [[_COMMUNITY_TelegramClient]]
- 7 edges to [[_COMMUNITY_Job]]
- 6 edges to [[_COMMUNITY_db.py]]
- 4 edges to [[_COMMUNITY_Source]]
- 3 edges to [[_COMMUNITY_bot__init__.py]]
- 3 edges to [[_COMMUNITY_upsert_job]]
- 2 edges to [[_COMMUNITY_pipeline.py]]
- 1 edge to [[_COMMUNITY_Job Agent]]
- 1 edge to [[_COMMUNITY_ingest.py]]
- 1 edge to [[_COMMUNITY_test_resume.py]]
- 1 edge to [[_COMMUNITY_baseline.py]]

## Top bridge nodes
- [[alerts.py]] - degree 21, connects to 10 communities
- [[test_alerts.py]] - degree 21, connects to 7 communities
- [[send_pending_alerts()]] - degree 15, connects to 6 communities
- [[test_send_pending_alerts_photo_and_skip()]] - degree 12, connects to 6 communities
- [[test_scoring_error_does_not_alert()]] - degree 11, connects to 6 communities