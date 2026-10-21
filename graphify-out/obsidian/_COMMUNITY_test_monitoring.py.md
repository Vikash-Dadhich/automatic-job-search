---
type: community
cohesion: 0.09
members: 65
---

# test_monitoring.py

**Cohesion:** 0.09 - loosely connected
**Members:** 65 nodes

## Members
- [[Actionable configuration problems. Empty means the checked settings are usable.]] - rationale - orchestrator/monitoring.py
- [[Any_40]] - code
- [[Compact text. Counts and statuses only.]] - rationale - orchestrator/health.py
- [[Durable pipeline history. A failure here must not stop the pipeline.]] - rationale - orchestrator/monitoring.py
- [[Mark old running rows interrupted. A run newer than the threshold stays running.]] - rationale - orchestrator/monitoring.py
- [[One pipeline invocation. Observational only.]] - rationale - core/db.py
- [[One stage inside a pipeline run. No job text or secrets.]] - rationale - core/db.py
- [[Operational history and health. No network and no scheduler.]] - rationale - tests/test_monitoring.py
- [[Operational snapshot. It does not score, rank, or apply to jobs.]] - rationale - orchestrator/health.py
- [[PipelineRun]] - code - core/db.py
- [[PipelineStageRun]] - code - core/db.py
- [[Read operational state. Optional pieces that fail become explicit unknowns.]] - rationale - orchestrator/health.py
- [[SQLite returns naive datetimes; attach UTC before any comparison.]] - rationale - core/db.py
- [[Small integers already returned by a stage. Lists and text are ignored.]] - rationale - orchestrator/monitoring.py
- [[_as_utc()_1]] - code - core/db.py
- [[_brief()]] - code - orchestrator/health.py
- [[_job()_10]] - code - tests/test_monitoring.py
- [[_moment()]] - code - orchestrator/monitoring.py
- [[_recent_failures()]] - code - orchestrator/health.py
- [[_repeated_failures()]] - code - orchestrator/health.py
- [[_require_int()_5]] - code - orchestrator/monitoring.py
- [[_run_view()]] - code - orchestrator/health.py
- [[_stages()]] - code - orchestrator/health.py
- [[_status()_1]] - code - orchestrator/health.py
- [[_thresholds()]] - code - orchestrator/health.py
- [[_validate()_6]] - code - orchestrator/monitoring.py
- [[close_pipeline_run()]] - code - orchestrator/monitoring.py
- [[close_stage_run()]] - code - orchestrator/monitoring.py
- [[count_jobs_by_status()]] - code - orchestrator/monitoring.py
- [[count_stale_jobs()]] - code - orchestrator/monitoring.py
- [[database_reachable()]] - code - orchestrator/monitoring.py
- [[datetime_9]] - code
- [[datetime_10]] - code
- [[format_health_report()]] - code - orchestrator/health.py
- [[get_health_report()]] - code - orchestrator/health.py
- [[health.py]] - code - orchestrator/health.py
- [[interrupt_stale_runs()]] - code - orchestrator/monitoring.py
- [[list_pipeline_runs()]] - code - orchestrator/monitoring.py
- [[list_stage_runs()]] - code - orchestrator/monitoring.py
- [[load_monitoring_config()]] - code - orchestrator/monitoring.py
- [[monitoring.py]] - code - orchestrator/monitoring.py
- [[monitoring_config_hash()]] - code - orchestrator/monitoring.py
- [[open_pipeline_run()]] - code - orchestrator/monitoring.py
- [[open_stage_run()]] - code - orchestrator/monitoring.py
- [[operational_config_hash()]] - code - orchestrator/monitoring.py
- [[record_skipped_stage()]] - code - orchestrator/monitoring.py
- [[sqlmodel_2]] - concept
- [[stage_counters()]] - code - orchestrator/monitoring.py
- [[test_a_new_run_does_not_duplicate_applications()]] - code - tests/test_monitoring.py
- [[test_backlog_and_stale_jobs()]] - code - tests/test_monitoring.py
- [[test_counters_keep_known_integers_only()]] - code - tests/test_monitoring.py
- [[test_fresh_running_run_is_not_stale()]] - code - tests/test_monitoring.py
- [[test_health_is_degraded_after_a_partial_run()]] - code - tests/test_monitoring.py
- [[test_health_is_healthy_with_no_runs()]] - code - tests/test_monitoring.py
- [[test_health_is_unhealthy_after_repeated_failures()]] - code - tests/test_monitoring.py
- [[test_health_marks_a_stale_run()]] - code - tests/test_monitoring.py
- [[test_monitoring.py]] - code - tests/test_monitoring.py
- [[test_monitoring_config_is_versioned()]] - code - tests/test_monitoring.py
- [[test_old_running_run_becomes_interrupted()]] - code - tests/test_monitoring.py
- [[test_operational_tables_compile_for_sqlite_and_postgres()]] - code - tests/test_monitoring.py
- [[test_stage_rows_keep_status_error_and_counters()]] - code - tests/test_monitoring.py
- [[test_stale_threshold_is_configurable()]] - code - tests/test_monitoring.py
- [[test_successful_run_records_duration()]] - code - tests/test_monitoring.py
- [[uuid]] - concept
- [[validate_operational_config()]] - code - orchestrator/monitoring.py

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/test_monitoringpy
SORT file.name ASC
```

## Connections to other communities
- 27 edges to [[_COMMUNITY_session_scope]]
- 19 edges to [[_COMMUNITY_db.py]]
- 16 edges to [[_COMMUNITY_pipeline.py]]
- 13 edges to [[_COMMUNITY_MonkeyPatch]]
- 9 edges to [[_COMMUNITY_test_pacing.py]]
- 7 edges to [[_COMMUNITY_Job]]
- 7 edges to [[_COMMUNITY_tracker.py]]
- 6 edges to [[_COMMUNITY_calibration.py]]
- 6 edges to [[_COMMUNITY_main.py]]
- 5 edges to [[_COMMUNITY_json]]
- 4 edges to [[_COMMUNITY_scheduler.py]]
- 4 edges to [[_COMMUNITY_feedback.py]]
- 3 edges to [[_COMMUNITY_test_feedback.py]]
- 3 edges to [[_COMMUNITY_get_settings]]
- 3 edges to [[_COMMUNITY_test_structured_jd.py]]
- 3 edges to [[_COMMUNITY_typing]]
- 2 edges to [[_COMMUNITY_AsyncSession]]
- 2 edges to [[_COMMUNITY_Source]]
- 2 edges to [[_COMMUNITY_pytest]]
- 2 edges to [[_COMMUNITY_test_career_intelligence.py]]
- 1 edge to [[_COMMUNITY_Phase 18 — Production reliability and monitoring]]
- 1 edge to [[_COMMUNITY_structured_jd.py]]
- 1 edge to [[_COMMUNITY_company_intelligence.py]]
- 1 edge to [[_COMMUNITY_test_phase13_shortlist.py]]
- 1 edge to [[_COMMUNITY_test_company_intelligence_v2.py]]
- 1 edge to [[_COMMUNITY_ingest.py]]
- 1 edge to [[_COMMUNITY_pathlib]]
- 1 edge to [[_COMMUNITY_targets.py]]
- 1 edge to [[_COMMUNITY_asyncio]]
- 1 edge to [[_COMMUNITY_baseline.py]]
- 1 edge to [[_COMMUNITY_test_application_tracker.py]]
- 1 edge to [[_COMMUNITY_scorerengine.py]]

## Top bridge nodes
- [[test_monitoring.py]] - degree 58, connects to 14 communities
- [[monitoring.py]] - degree 48, connects to 11 communities
- [[sqlmodel_2]] - degree 16, connects to 11 communities
- [[get_health_report()]] - degree 32, connects to 6 communities
- [[_as_utc()_1]] - degree 31, connects to 6 communities