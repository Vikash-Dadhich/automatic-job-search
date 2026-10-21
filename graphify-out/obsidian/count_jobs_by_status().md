---
source_file: "orchestrator/monitoring.py"
type: "code"
community: "test_monitoring.py"
location: "L312"
tags:
  - graphify/code
  - graphify/EXTRACTED
  - community/test_monitoringpy
---

# count_jobs_by_status()

## Connections
- [[Job]] - `uses` [INFERRED]
- [[Status]] - `uses` [INFERRED]
- [[get_health_report()]] - `calls` [EXTRACTED]
- [[health.py]] - `imports` [EXTRACTED]
- [[init_db()]] - `calls` [EXTRACTED]
- [[monitoring.py]] - `contains` [EXTRACTED]
- [[session_scope()]] - `calls` [EXTRACTED]

#graphify/code #graphify/EXTRACTED #community/test_monitoringpy