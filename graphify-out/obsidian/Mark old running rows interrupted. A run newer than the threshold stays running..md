---
source_file: "orchestrator/monitoring.py"
type: "rationale"
community: "test_monitoring.py"
location: "L270"
tags:
  - graphify/rationale
  - graphify/EXTRACTED
  - community/test_monitoringpy
---

# Mark old running rows interrupted. A run newer than the threshold stays running.

## Connections
- [[interrupt_stale_runs()]] - `rationale_for` [EXTRACTED]

#graphify/rationale #graphify/EXTRACTED #community/test_monitoringpy