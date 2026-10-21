---
type: community
cohesion: 0.15
members: 40
---

# calibration.py

**Cohesion:** 0.15 - loosely connected
**Members:** 40 nodes

## Members
- [[Any_2]] - code
- [[Benchmark stored application history. Does not write job or application rows.]] - rationale - scorer/calibration.py
- [[CalibrationFold]] - code - scorer/calibration.py
- [[CalibrationMetricRow]] - code - scorer/calibration.py
- [[CalibrationReport]] - code - scorer/calibration.py
- [[FeedbackCase]] - code - scorer/feedback.py
- [[FeedbackObservation]] - code - scorer/feedback.py
- [[One submitted application and the events visible to the caller.]] - rationale - scorer/feedback.py
- [[Score Phase 16 feedback on later applications. Training cannot see those…]] - rationale - scorer/calibration.py
- [[Score one outcome definition. Strong-positive keeps the shrunk rate.]] - rationale - scorer/calibration.py
- [[Segment label Phase 16 uses. Empty subfamilies return None.]] - rationale - scorer/feedback.py
- [[Temporal check of Phase 16 feedback. This does not change scores or ranking.]] - rationale - scorer/calibration.py
- [[_append_buckets()]] - code - scorer/calibration.py
- [[_append_short_target()]] - code - scorer/calibration.py
- [[_append_slice()]] - code - scorer/calibration.py
- [[_append_target_metrics()]] - code - scorer/calibration.py
- [[_append_topk()]] - code - scorer/calibration.py
- [[_bucket_name()]] - code - scorer/calibration.py
- [[_direction()]] - code - scorer/calibration.py
- [[_events_in_window()]] - code - scorer/calibration.py
- [[_family_adjustment()]] - code - scorer/calibration.py
- [[_hit()]] - code - scorer/calibration.py
- [[_lookup()]] - code - scorer/calibration.py
- [[_matured()]] - code - scorer/calibration.py
- [[_named()]] - code - scorer/calibration.py
- [[_ordered()]] - code - scorer/calibration.py
- [[_predict()]] - code - scorer/calibration.py
- [[_rate()]] - code - scorer/calibration.py
- [[_rate_direction()]] - code - scorer/calibration.py
- [[_require_int()]] - code - scorer/calibration.py
- [[_stored_rate()]] - code - scorer/calibration.py
- [[_topk_count()]] - code - scorer/calibration.py
- [[_validate()]] - code - scorer/calibration.py
- [[_windows()]] - code - scorer/calibration.py
- [[build_calibration()]] - code - scorer/calibration.py
- [[calibration.py]] - code - scorer/calibration.py
- [[datetime]] - code
- [[load_calibration_config()]] - code - scorer/calibration.py
- [[run_calibration()]] - code - scorer/calibration.py
- [[segment_for()]] - code - scorer/feedback.py

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/calibrationpy
SORT file.name ASC
```

## Connections to other communities
- 24 edges to [[_COMMUNITY_test_calibration.py]]
- 17 edges to [[_COMMUNITY_feedback.py]]
- 8 edges to [[_COMMUNITY_AsyncSession]]
- 7 edges to [[_COMMUNITY_test_feedback.py]]
- 6 edges to [[_COMMUNITY_json]]
- 6 edges to [[_COMMUNITY_test_monitoring.py]]
- 2 edges to [[_COMMUNITY_pytest]]
- 2 edges to [[_COMMUNITY_db.py]]
- 1 edge to [[_COMMUNITY_session_scope]]
- 1 edge to [[_COMMUNITY_pathlib]]
- 1 edge to [[_COMMUNITY_typing]]
- 1 edge to [[_COMMUNITY_test_resume.py]]
- 1 edge to [[_COMMUNITY_targets.py]]

## Top bridge nodes
- [[calibration.py]] - degree 60, connects to 13 communities
- [[build_calibration()]] - degree 28, connects to 4 communities
- [[FeedbackCase]] - degree 29, connects to 3 communities
- [[segment_for()]] - degree 10, connects to 2 communities
- [[run_calibration()]] - degree 9, connects to 2 communities