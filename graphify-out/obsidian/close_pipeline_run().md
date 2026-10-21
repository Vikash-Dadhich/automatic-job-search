---
source_file: "orchestrator/monitoring.py"
type: "code"
community: "test_monitoring.py"
location: "L179"
tags:
  - graphify/code
  - graphify/EXTRACTED
  - community/test_monitoringpy
---

# close_pipeline_run()

## Connections
- [[PipelineRun]] - `uses` [INFERRED]
- [[_as_utc()_1]] - `calls` [EXTRACTED]
- [[_moment()]] - `calls` [EXTRACTED]
- [[_safe_close_run()]] - `calls` [EXTRACTED]
- [[datetime_10]] - `references` [EXTRACTED]
- [[monitoring.py]] - `contains` [EXTRACTED]
- [[pipeline.py]] - `imports` [EXTRACTED]
- [[session_scope()]] - `calls` [EXTRACTED]
- [[test_health_is_degraded_after_a_partial_run()]] - `calls` [EXTRACTED]
- [[test_health_is_unhealthy_after_repeated_failures()]] - `calls` [EXTRACTED]
- [[test_monitoring.py]] - `imports` [EXTRACTED]
- [[test_successful_run_records_duration()]] - `calls` [EXTRACTED]

#graphify/code #graphify/EXTRACTED #community/test_monitoringpy