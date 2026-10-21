---
source_file: "automation/pacing.py"
type: "rationale"
community: "test_pacing.py"
location: "L52"
tags:
  - graphify/rationale
  - graphify/EXTRACTED
  - community/test_pacingpy
---

# 23:59:59 in ``tz_name``, returned as UTC. Unknown zones fall back to UTC.

## Connections
- [[end_of_local_day()]] - `rationale_for` [EXTRACTED]

#graphify/rationale #graphify/EXTRACTED #community/test_pacingpy