---
source_file: "orchestrator/monitoring.py"
type: "code"
community: "test_monitoring.py"
location: "L292"
tags:
  - graphify/code
  - graphify/EXTRACTED
  - community/test_monitoringpy
---

# list_pipeline_runs()

## Connections
- [[PipelineRun]] - `uses` [INFERRED]
- [[init_db()]] - `calls` [EXTRACTED]
- [[monitoring.py]] - `contains` [EXTRACTED]
- [[session_scope()]] - `calls` [EXTRACTED]
- [[test_a_new_run_does_not_duplicate_applications()]] - `calls` [EXTRACTED]
- [[test_fresh_running_run_is_not_stale()]] - `calls` [EXTRACTED]
- [[test_monitoring.py]] - `imports` [EXTRACTED]
- [[test_old_running_run_becomes_interrupted()]] - `calls` [EXTRACTED]
- [[test_pipeline_failure_outside_a_stage_is_failed()]] - `calls` [EXTRACTED]
- [[test_pipeline_partial_when_a_stage_fails()]] - `calls` [EXTRACTED]
- [[test_pre_stage_setup_failure_marks_the_run_failed()]] - `calls` [EXTRACTED]
- [[test_successful_run_records_duration()]] - `calls` [EXTRACTED]

#graphify/code #graphify/EXTRACTED #community/test_monitoringpy