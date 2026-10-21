---
source_file: "tests/test_monitoring.py"
type: "code"
community: "MonkeyPatch"
location: "L125"
tags:
  - graphify/code
  - graphify/EXTRACTED
  - community/MonkeyPatch
---

# test_pipeline_partial_when_a_stage_fails()

## Connections
- [[MonkeyPatch_12]] - `references` [EXTRACTED]
- [[fail()]] - `indirect_call` [INFERRED]
- [[list_pipeline_runs()]] - `calls` [EXTRACTED]
- [[list_stage_runs()]] - `calls` [EXTRACTED]
- [[ok()_2]] - `contains` [EXTRACTED]
- [[run_pipeline()]] - `calls` [EXTRACTED]
- [[test_monitoring.py]] - `contains` [EXTRACTED]

#graphify/code #graphify/EXTRACTED #community/MonkeyPatch