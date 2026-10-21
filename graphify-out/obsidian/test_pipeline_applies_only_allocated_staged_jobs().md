---
source_file: "tests/test_application_portfolio.py"
type: "code"
community: "test_application_portfolio.py"
location: "L426"
tags:
  - graphify/code
  - graphify/EXTRACTED
  - community/test_application_portfoliopy
---

# test_pipeline_applies_only_allocated_staged_jobs()

## Connections
- [[MonkeyPatch_18]] - `references` [EXTRACTED]
- [[Path_38]] - `references` [EXTRACTED]
- [[Source]] - `uses` [INFERRED]
- [[Status]] - `uses` [INFERRED]
- [[_Spy]] - `calls` [EXTRACTED]
- [[_job()_8]] - `calls` [EXTRACTED]
- [[apply_pending()]] - `calls` [EXTRACTED]
- [[get_job_by_id()]] - `calls` [EXTRACTED]
- [[noop()_1]] - `indirect_call` [INFERRED]
- [[noop_stage()]] - `indirect_call` [INFERRED]
- [[record_apply()]] - `indirect_call` [INFERRED]
- [[run_pipeline()]] - `calls` [EXTRACTED]
- [[session_scope()]] - `calls` [EXTRACTED]
- [[test_application_portfolio.py]] - `contains` [EXTRACTED]
- [[upsert_job()]] - `calls` [EXTRACTED]

#graphify/code #graphify/EXTRACTED #community/test_application_portfoliopy