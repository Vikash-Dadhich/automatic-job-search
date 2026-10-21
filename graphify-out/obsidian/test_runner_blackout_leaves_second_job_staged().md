---
source_file: "tests/test_pacing.py"
type: "code"
community: "test_pacing.py"
location: "L234"
tags:
  - graphify/code
  - graphify/EXTRACTED
  - community/test_pacingpy
---

# test_runner_blackout_leaves_second_job_staged()

## Connections
- [[MonkeyPatch_7]] - `references` [EXTRACTED]
- [[Status]] - `uses` [INFERRED]
- [[_Applicator]] - `calls` [EXTRACTED]
- [[_Sleep]] - `calls` [EXTRACTED]
- [[_enable()]] - `calls` [EXTRACTED]
- [[_seed()]] - `calls` [EXTRACTED]
- [[apply_pending()]] - `calls` [EXTRACTED]
- [[get_job_by_id()]] - `calls` [EXTRACTED]
- [[session_scope()]] - `calls` [EXTRACTED]
- [[test_pacing.py]] - `contains` [EXTRACTED]

#graphify/code #graphify/EXTRACTED #community/test_pacingpy