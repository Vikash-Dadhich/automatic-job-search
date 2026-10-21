---
source_file: "tests/test_apply_runner.py"
type: "code"
community: "session_scope"
location: "L288"
tags:
  - graphify/code
  - graphify/EXTRACTED
  - community/session_scope
---

# test_final_reload_still_allocated_reaches_applicator()

## Connections
- [[FakeApplicator]] - `calls` [EXTRACTED]
- [[Job]] - `uses` [INFERRED]
- [[MonkeyPatch_17]] - `references` [EXTRACTED]
- [[Path_35]] - `references` [EXTRACTED]
- [[_script_reloads()]] - `calls` [EXTRACTED]
- [[_seed_job()]] - `calls` [EXTRACTED]
- [[apply_pending()]] - `calls` [EXTRACTED]
- [[mark()]] - `indirect_call` [INFERRED]
- [[test_apply_runner.py]] - `contains` [EXTRACTED]

#graphify/code #graphify/EXTRACTED #community/session_scope