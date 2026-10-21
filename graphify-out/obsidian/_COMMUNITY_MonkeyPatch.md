---
type: community
cohesion: 0.13
members: 18
---

# MonkeyPatch

**Cohesion:** 0.13 - loosely connected
**Members:** 18 nodes

## Members
- [[CaptureFixture]] - code
- [[MonkeyPatch_12]] - code
- [[boom()_1]] - code - tests/test_monitoring.py
- [[boom()_2]] - code - tests/test_monitoring.py
- [[down()]] - code - tests/test_monitoring.py
- [[explode()]] - code - tests/test_monitoring.py
- [[fail()]] - code - tests/test_monitoring.py
- [[ok()_1]] - code - tests/test_monitoring.py
- [[ok()_2]] - code - tests/test_monitoring.py
- [[ok()_3]] - code - tests/test_monitoring.py
- [[scheduler_must_not_start()]] - code - tests/test_monitoring.py
- [[test_health_command_prints_no_secrets()]] - code - tests/test_monitoring.py
- [[test_health_reports_database_failure()]] - code - tests/test_monitoring.py
- [[test_health_reports_invalid_configuration()]] - code - tests/test_monitoring.py
- [[test_pipeline_failure_outside_a_stage_is_failed()]] - code - tests/test_monitoring.py
- [[test_pipeline_partial_when_a_stage_fails()]] - code - tests/test_monitoring.py
- [[test_pre_stage_setup_failure_marks_the_run_failed()]] - code - tests/test_monitoring.py
- [[test_telemetry_failure_does_not_stop_the_pipeline()]] - code - tests/test_monitoring.py

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/MonkeyPatch
SORT file.name ASC
```

## Connections to other communities
- 13 edges to [[_COMMUNITY_test_monitoring.py]]
- 4 edges to [[_COMMUNITY_pipeline.py]]
- 1 edge to [[_COMMUNITY_main.py]]
- 1 edge to [[_COMMUNITY_db.py]]

## Top bridge nodes
- [[test_health_command_prints_no_secrets()]] - degree 6, connects to 3 communities
- [[test_pipeline_failure_outside_a_stage_is_failed()]] - degree 7, connects to 2 communities
- [[test_pipeline_partial_when_a_stage_fails()]] - degree 7, connects to 2 communities
- [[test_pre_stage_setup_failure_marks_the_run_failed()]] - degree 6, connects to 2 communities
- [[test_telemetry_failure_does_not_stop_the_pipeline()]] - degree 6, connects to 2 communities