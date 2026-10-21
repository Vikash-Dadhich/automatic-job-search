---
type: community
cohesion: 0.11
members: 31
---

# AsyncSession

**Cohesion:** 0.11 - loosely connected
**Members:** 31 nodes

## Members
- [[AsyncSession_1]] - code
- [[Benchmark]] - code - core/db.py
- [[Benchmark of the candidate vs peers for one job.]] - rationale - core/db.py
- [[CalibrationMetric]] - code - core/db.py
- [[CalibrationRun]] - code - core/db.py
- [[Derived counts and rates for one segment. Not a fit or priority score.]] - rationale - core/db.py
- [[FeedbackRun]] - code - core/db.py
- [[FeedbackSignal]] - code - core/db.py
- [[Forget a derived JD reading when the normalized text changes.]] - rationale - core/db.py
- [[Jobs that have pending suggestions not yet sent to Telegram.]] - rationale - core/db.py
- [[Mark a submitted job as 'send in progress'. True only for the winner.]] - rationale - core/db.py
- [[One holdout comparison. Raw application rows are not copied.]] - rationale - core/db.py
- [[One recomputation of empirical feedback. Raw history stays on applications.]] - rationale - core/db.py
- [[One temporal benchmark of feedback. It does not change scores.]] - rationale - core/db.py
- [[SQLModel]] - code
- [[Store derived signals. Application rows are not copied.]] - rationale - scorer/feedback.py
- [[_drop_structured_jd()]] - code - core/db.py
- [[claim_outcome_prompt()]] - code - core/db.py
- [[get_calibration_metrics()]] - code - core/db.py
- [[get_calibration_run()]] - code - core/db.py
- [[get_feedback_run()]] - code - core/db.py
- [[get_feedback_signals()]] - code - core/db.py
- [[get_latest_feedback_run()]] - code - core/db.py
- [[get_unsent_suggestion_jobs()]] - code - core/db.py
- [[latest_feedback_run()]] - code - scorer/feedback.py
- [[load_persisted_calibration()]] - code - scorer/calibration.py
- [[load_persisted_feedback()]] - code - scorer/feedback.py
- [[persist_calibration()]] - code - scorer/calibration.py
- [[persist_feedback()]] - code - scorer/feedback.py
- [[save_calibration_run()]] - code - core/db.py
- [[save_feedback_run()]] - code - core/db.py

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/AsyncSession
SORT file.name ASC
```

## Connections to other communities
- 25 edges to [[_COMMUNITY_db.py]]
- 13 edges to [[_COMMUNITY_test_feedback.py]]
- 10 edges to [[_COMMUNITY_feedback.py]]
- 8 edges to [[_COMMUNITY_calibration.py]]
- 8 edges to [[_COMMUNITY_handlers.py]]
- 8 edges to [[_COMMUNITY_session_scope]]
- 7 edges to [[_COMMUNITY_suggest.py]]
- 4 edges to [[_COMMUNITY_test_calibration.py]]
- 3 edges to [[_COMMUNITY_benchmarkengine.py]]
- 3 edges to [[_COMMUNITY_upsert_job]]
- 2 edges to [[_COMMUNITY_test_monitoring.py]]
- 2 edges to [[_COMMUNITY_Job]]
- 2 edges to [[_COMMUNITY_baseline.py]]
- 1 edge to [[_COMMUNITY_test_structured_jd.py]]
- 1 edge to [[_COMMUNITY_diff.py]]
- 1 edge to [[_COMMUNITY_test_pacing.py]]
- 1 edge to [[_COMMUNITY_company_intelligence.py]]
- 1 edge to [[_COMMUNITY_migrate_to_neon.py]]
- 1 edge to [[_COMMUNITY_test_career_intelligence.py]]
- 1 edge to [[_COMMUNITY_discovery_recall.py]]
- 1 edge to [[_COMMUNITY_test_phase13_shortlist.py]]
- 1 edge to [[_COMMUNITY_test_doctor.py]]
- 1 edge to [[_COMMUNITY_test_application_tracker.py]]

## Top bridge nodes
- [[AsyncSession_1]] - degree 36, connects to 11 communities
- [[SQLModel]] - degree 18, connects to 11 communities
- [[load_persisted_calibration()]] - degree 10, connects to 5 communities
- [[persist_calibration()]] - degree 10, connects to 5 communities
- [[persist_feedback()]] - degree 10, connects to 4 communities