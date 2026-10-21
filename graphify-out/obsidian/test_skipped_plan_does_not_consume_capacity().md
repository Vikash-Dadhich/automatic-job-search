---
source_file: "tests/test_application_portfolio.py"
type: "code"
community: "test_application_portfolio.py"
location: "L732"
tags:
  - graphify/code
  - graphify/EXTRACTED
  - community/test_application_portfoliopy
---

# test_skipped_plan_does_not_consume_capacity()

## Connections
- [[MonkeyPatch_18]] - `references` [EXTRACTED]
- [[Path_38]] - `references` [EXTRACTED]
- [[_workday()]] - `calls` [EXTRACTED]
- [[apply_portfolio()]] - `calls` [EXTRACTED]
- [[get_job_by_id()]] - `indirect_call` [INFERRED]
- [[session_scope()]] - `calls` [EXTRACTED]
- [[skip_first()]] - `indirect_call` [INFERRED]
- [[test_application_portfolio.py]] - `contains` [EXTRACTED]
- [[upsert_job()]] - `calls` [EXTRACTED]

#graphify/code #graphify/EXTRACTED #community/test_application_portfoliopy