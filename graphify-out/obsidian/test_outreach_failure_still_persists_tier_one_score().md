---
source_file: "tests/test_robustness.py"
type: "code"
community: "session_scope"
location: "L133"
tags:
  - graphify/code
  - graphify/EXTRACTED
  - community/session_scope
---

# test_outreach_failure_still_persists_tier_one_score()

## Connections
- [[A dead outreach call must not push a valid Tier-1 job into Status.error.]] - `rationale_for` [EXTRACTED]
- [[Job]] - `uses` [INFERRED]
- [[ScoreOnlyClient]] - `calls` [EXTRACTED]
- [[Scorer]] - `uses` [INFERRED]
- [[Source]] - `uses` [INFERRED]
- [[Status]] - `uses` [INFERRED]
- [[Tier]] - `uses` [INFERRED]
- [[asyncio_6]] - `references` [EXTRACTED]
- [[get_job_by_id()]] - `calls` [EXTRACTED]
- [[load_profile()]] - `calls` [EXTRACTED]
- [[session_scope()]] - `calls` [EXTRACTED]
- [[test_robustness.py]] - `contains` [EXTRACTED]
- [[upsert_job()]] - `calls` [EXTRACTED]

#graphify/code #graphify/EXTRACTED #community/session_scope