---
source_file: "orchestrator/monitoring.py"
type: "code"
community: "test_monitoring.py"
location: "L265"
tags:
  - graphify/code
  - graphify/EXTRACTED
  - community/test_monitoringpy
---

# interrupt_stale_runs()

## Connections
- [[Mark old running rows interrupted. A run newer than the threshold stays running.]] - `rationale_for` [EXTRACTED]
- [[PipelineRun]] - `uses` [INFERRED]
- [[_as_utc()_1]] - `calls` [EXTRACTED]
- [[_moment()]] - `calls` [EXTRACTED]
- [[_safe_open_run()]] - `calls` [EXTRACTED]
- [[datetime_10]] - `references` [EXTRACTED]
- [[get_health_report()]] - `calls` [EXTRACTED]
- [[health.py]] - `imports` [EXTRACTED]
- [[load_monitoring_config()]] - `calls` [EXTRACTED]
- [[monitoring.py]] - `contains` [EXTRACTED]
- [[pipeline.py]] - `imports` [EXTRACTED]
- [[session_scope()]] - `calls` [EXTRACTED]
- [[test_fresh_running_run_is_not_stale()]] - `calls` [EXTRACTED]
- [[test_monitoring.py]] - `imports` [EXTRACTED]
- [[test_old_running_run_becomes_interrupted()]] - `calls` [EXTRACTED]
- [[test_stale_threshold_is_configurable()]] - `calls` [EXTRACTED]

#graphify/code #graphify/EXTRACTED #community/test_monitoringpy