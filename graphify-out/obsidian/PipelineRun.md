---
source_file: "core/db.py"
type: "code"
community: "test_monitoring.py"
location: "L597"
tags:
  - graphify/code
  - graphify/EXTRACTED
  - community/test_monitoringpy
---

# PipelineRun

## Connections
- [[One pipeline invocation. Observational only.]] - `rationale_for` [EXTRACTED]
- [[SQLModel]] - `inherits` [EXTRACTED]
- [[_repeated_failures()]] - `uses` [INFERRED]
- [[_run_view()]] - `uses` [INFERRED]
- [[close_pipeline_run()]] - `uses` [INFERRED]
- [[db.py]] - `contains` [EXTRACTED]
- [[get_health_report()]] - `uses` [INFERRED]
- [[health.py]] - `imports` [EXTRACTED]
- [[interrupt_stale_runs()]] - `uses` [INFERRED]
- [[list_pipeline_runs()]] - `uses` [INFERRED]
- [[monitoring.py]] - `imports` [EXTRACTED]
- [[open_pipeline_run()]] - `calls` [EXTRACTED]

#graphify/code #graphify/EXTRACTED #community/test_monitoringpy