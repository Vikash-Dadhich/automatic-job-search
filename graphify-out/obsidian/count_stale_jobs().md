---
source_file: "orchestrator/monitoring.py"
type: "code"
community: "test_monitoring.py"
location: "L324"
tags:
  - graphify/code
  - graphify/EXTRACTED
  - community/test_monitoringpy
---

# count_stale_jobs()

## Connections
- [[Job]] - `uses` [INFERRED]
- [[Status]] - `uses` [INFERRED]
- [[_moment()]] - `calls` [EXTRACTED]
- [[datetime_10]] - `references` [EXTRACTED]
- [[get_health_report()]] - `calls` [EXTRACTED]
- [[health.py]] - `imports` [EXTRACTED]
- [[monitoring.py]] - `contains` [EXTRACTED]
- [[session_scope()]] - `calls` [EXTRACTED]

#graphify/code #graphify/EXTRACTED #community/test_monitoringpy