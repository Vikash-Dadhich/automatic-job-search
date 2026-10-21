---
source_file: "tests/test_robustness.py"
type: "code"
community: "session_scope"
location: "L221"
tags:
  - graphify/code
  - graphify/EXTRACTED
  - community/session_scope
---

# test_unchanged_jd_keeps_staged_status()

## Connections
- [[Job]] - `uses` [INFERRED]
- [[Source]] - `uses` [INFERRED]
- [[Status]] - `uses` [INFERRED]
- [[asyncio_6]] - `references` [EXTRACTED]
- [[get_job_by_id()]] - `calls` [EXTRACTED]
- [[session_scope()]] - `calls` [EXTRACTED]
- [[test_robustness.py]] - `contains` [EXTRACTED]
- [[upsert_job()]] - `calls` [EXTRACTED]

#graphify/code #graphify/EXTRACTED #community/session_scope