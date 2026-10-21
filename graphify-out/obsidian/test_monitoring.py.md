---
source_file: "tests/test_monitoring.py"
type: "code"
community: "test_monitoring.py"
location: "L1"
tags:
  - graphify/code
  - graphify/EXTRACTED
  - community/test_monitoringpy
---

# test_monitoring.py

## Connections
- [[Application]] - `imports` [EXTRACTED]
- [[Job]] - `imports` [EXTRACTED]
- [[Operational history and health. No network and no scheduler.]] - `rationale_for` [EXTRACTED]
- [[Source]] - `imports` [EXTRACTED]
- [[Status]] - `imports` [EXTRACTED]
- [[_job()_10]] - `contains` [EXTRACTED]
- [[asyncio_11]] - `imports` [EXTRACTED]
- [[close_pipeline_run()]] - `imports` [EXTRACTED]
- [[close_stage_run()]] - `imports` [EXTRACTED]
- [[datetime_17]] - `imports_from` [EXTRACTED]
- [[db.py]] - `imports_from` [EXTRACTED]
- [[format_health_report()]] - `imports` [EXTRACTED]
- [[get_health_report()]] - `imports` [EXTRACTED]
- [[get_settings()]] - `imports` [EXTRACTED]
- [[health.py]] - `imports_from` [EXTRACTED]
- [[interrupt_stale_runs()]] - `imports` [EXTRACTED]
- [[list_pipeline_runs()]] - `imports` [EXTRACTED]
- [[list_stage_runs()]] - `imports` [EXTRACTED]
- [[load_monitoring_config()]] - `imports` [EXTRACTED]
- [[main()]] - `imports` [EXTRACTED]
- [[main.py]] - `imports_from` [EXTRACTED]
- [[monitoring.py]] - `imports_from` [EXTRACTED]
- [[open_pipeline_run()]] - `imports` [EXTRACTED]
- [[open_stage_run()]] - `imports` [EXTRACTED]
- [[pipeline.py]] - `imports_from` [EXTRACTED]
- [[pytest]] - `imports` [EXTRACTED]
- [[record_skipped_stage()]] - `imports` [EXTRACTED]
- [[reset_engine()]] - `imports` [EXTRACTED]
- [[run_pipeline()]] - `imports` [EXTRACTED]
- [[session_scope()]] - `imports` [EXTRACTED]
- [[settings.py]] - `imports_from` [EXTRACTED]
- [[sqlalchemy]] - `imports_from` [EXTRACTED]
- [[sqlalchemy_dialects]] - `imports_from` [EXTRACTED]
- [[sqlalchemy_schema]] - `imports_from` [EXTRACTED]
- [[sqlmodel_2]] - `imports_from` [EXTRACTED]
- [[stage_counters()]] - `imports` [EXTRACTED]
- [[test_a_new_run_does_not_duplicate_applications()]] - `contains` [EXTRACTED]
- [[test_backlog_and_stale_jobs()]] - `contains` [EXTRACTED]
- [[test_counters_keep_known_integers_only()]] - `contains` [EXTRACTED]
- [[test_fresh_running_run_is_not_stale()]] - `contains` [EXTRACTED]
- [[test_health_command_prints_no_secrets()]] - `contains` [EXTRACTED]
- [[test_health_is_degraded_after_a_partial_run()]] - `contains` [EXTRACTED]
- [[test_health_is_healthy_with_no_runs()]] - `contains` [EXTRACTED]
- [[test_health_is_unhealthy_after_repeated_failures()]] - `contains` [EXTRACTED]
- [[test_health_marks_a_stale_run()]] - `contains` [EXTRACTED]
- [[test_health_reports_database_failure()]] - `contains` [EXTRACTED]
- [[test_health_reports_invalid_configuration()]] - `contains` [EXTRACTED]
- [[test_monitoring_config_is_versioned()]] - `contains` [EXTRACTED]
- [[test_old_running_run_becomes_interrupted()]] - `contains` [EXTRACTED]
- [[test_operational_tables_compile_for_sqlite_and_postgres()]] - `contains` [EXTRACTED]
- [[test_pipeline_failure_outside_a_stage_is_failed()]] - `contains` [EXTRACTED]
- [[test_pipeline_partial_when_a_stage_fails()]] - `contains` [EXTRACTED]
- [[test_pre_stage_setup_failure_marks_the_run_failed()]] - `contains` [EXTRACTED]
- [[test_stage_rows_keep_status_error_and_counters()]] - `contains` [EXTRACTED]
- [[test_stale_threshold_is_configurable()]] - `contains` [EXTRACTED]
- [[test_successful_run_records_duration()]] - `contains` [EXTRACTED]
- [[test_telemetry_failure_does_not_stop_the_pipeline()]] - `contains` [EXTRACTED]
- [[validate_operational_config()]] - `imports` [EXTRACTED]

#graphify/code #graphify/EXTRACTED #community/test_monitoringpy