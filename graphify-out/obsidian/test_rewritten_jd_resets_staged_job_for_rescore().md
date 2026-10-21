---
source_file: "tests/test_robustness.py"
type: "code"
community: "Tier"
location: "L172"
tags:
  - graphify/code
  - graphify/EXTRACTED
  - community/Tier
---

# test_rewritten_jd_resets_staged_job_for_rescore()

## Connections
- [[Job]] - `uses` [INFERRED]
- [[Source]] - `uses` [INFERRED]
- [[Status]] - `uses` [INFERRED]
- [[Tier]] - `uses` [INFERRED]
- [[asyncio_6]] - `references` [EXTRACTED]
- [[get_job_by_id()]] - `calls` [EXTRACTED]
- [[session_scope()]] - `calls` [EXTRACTED]
- [[test_robustness.py]] - `contains` [EXTRACTED]
- [[upsert_job()]] - `calls` [EXTRACTED]

#graphify/code #graphify/EXTRACTED #community/Tier