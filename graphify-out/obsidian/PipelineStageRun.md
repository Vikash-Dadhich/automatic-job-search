---
source_file: "core/db.py"
type: "code"
community: "test_monitoring.py"
location: "L615"
tags:
  - graphify/code
  - graphify/EXTRACTED
  - community/test_monitoringpy
---

# PipelineStageRun

## Connections
- [[One stage inside a pipeline run. No job text or secrets.]] - `rationale_for` [EXTRACTED]
- [[SQLModel]] - `inherits` [EXTRACTED]
- [[_recent_failures()]] - `uses` [INFERRED]
- [[_stages()]] - `uses` [INFERRED]
- [[close_stage_run()]] - `uses` [INFERRED]
- [[db.py]] - `contains` [EXTRACTED]
- [[get_health_report()]] - `uses` [INFERRED]
- [[health.py]] - `imports` [EXTRACTED]
- [[list_stage_runs()]] - `uses` [INFERRED]
- [[monitoring.py]] - `imports` [EXTRACTED]
- [[open_stage_run()]] - `calls` [EXTRACTED]
- [[record_skipped_stage()]] - `calls` [EXTRACTED]

#graphify/code #graphify/EXTRACTED #community/test_monitoringpy