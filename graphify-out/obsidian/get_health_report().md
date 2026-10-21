---
source_file: "orchestrator/health.py"
type: "code"
community: "test_monitoring.py"
location: "L23"
tags:
  - graphify/code
  - graphify/EXTRACTED
  - community/test_monitoringpy
---

# get_health_report()

## Connections
- [[Health states]] - `references` [INFERRED]
- [[PipelineRun]] - `uses` [INFERRED]
- [[PipelineStageRun]] - `uses` [INFERRED]
- [[Read operational state. Optional pieces that fail become explicit unknowns.]] - `rationale_for` [EXTRACTED]
- [[Status]] - `uses` [INFERRED]
- [[_as_utc()_1]] - `calls` [EXTRACTED]
- [[_cmd_health()]] - `calls` [EXTRACTED]
- [[_recent_failures()]] - `calls` [EXTRACTED]
- [[_repeated_failures()]] - `calls` [EXTRACTED]
- [[_run_view()]] - `calls` [EXTRACTED]
- [[_stages()]] - `calls` [EXTRACTED]
- [[_status()_1]] - `calls` [EXTRACTED]
- [[_thresholds()]] - `calls` [EXTRACTED]
- [[_utcnow()]] - `calls` [EXTRACTED]
- [[count_jobs_by_status()]] - `calls` [EXTRACTED]
- [[count_stale_jobs()]] - `calls` [EXTRACTED]
- [[database_reachable()]] - `calls` [EXTRACTED]
- [[datetime_9]] - `references` [EXTRACTED]
- [[health.py]] - `contains` [EXTRACTED]
- [[init_db()]] - `calls` [EXTRACTED]
- [[interrupt_stale_runs()]] - `calls` [EXTRACTED]
- [[main.py]] - `imports` [EXTRACTED]
- [[session_scope()]] - `calls` [EXTRACTED]
- [[test_backlog_and_stale_jobs()]] - `calls` [EXTRACTED]
- [[test_health_is_degraded_after_a_partial_run()]] - `calls` [EXTRACTED]
- [[test_health_is_healthy_with_no_runs()]] - `calls` [EXTRACTED]
- [[test_health_is_unhealthy_after_repeated_failures()]] - `calls` [EXTRACTED]
- [[test_health_marks_a_stale_run()]] - `calls` [EXTRACTED]
- [[test_health_reports_database_failure()]] - `calls` [EXTRACTED]
- [[test_health_reports_invalid_configuration()]] - `calls` [EXTRACTED]
- [[test_monitoring.py]] - `imports` [EXTRACTED]
- [[validate_operational_config()]] - `calls` [EXTRACTED]

#graphify/code #graphify/EXTRACTED #community/test_monitoringpy