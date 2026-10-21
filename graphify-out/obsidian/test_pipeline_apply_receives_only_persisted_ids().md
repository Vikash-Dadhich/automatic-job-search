---
source_file: "tests/test_application_portfolio.py"
type: "code"
community: "test_application_portfolio.py"
location: "L681"
tags:
  - graphify/code
  - graphify/EXTRACTED
  - community/test_application_portfoliopy
---

# test_pipeline_apply_receives_only_persisted_ids()

## Connections
- [[MonkeyPatch_18]] - `references` [EXTRACTED]
- [[Path_38]] - `references` [EXTRACTED]
- [[_workday()]] - `calls` [EXTRACTED]
- [[get_job_by_id()]] - `indirect_call` [INFERRED]
- [[noop()_2]] - `contains` [EXTRACTED]
- [[noop()_1]] - `indirect_call` [INFERRED]
- [[noop_stage()_1]] - `contains` [EXTRACTED]
- [[noop_stage()]] - `indirect_call` [INFERRED]
- [[record_apply()_1]] - `contains` [EXTRACTED]
- [[record_apply()]] - `indirect_call` [INFERRED]
- [[run_pipeline()]] - `calls` [EXTRACTED]
- [[session_scope()]] - `calls` [EXTRACTED]
- [[skip_lost()_1]] - `contains` [EXTRACTED]
- [[skip_lost()]] - `indirect_call` [INFERRED]
- [[test_application_portfolio.py]] - `contains` [EXTRACTED]
- [[upsert_job()]] - `calls` [EXTRACTED]

#graphify/code #graphify/EXTRACTED #community/test_application_portfoliopy