---
source_file: "tests/test_monitoring.py"
type: "code"
community: "MonkeyPatch"
location: "L161"
tags:
  - graphify/code
  - graphify/EXTRACTED
  - community/MonkeyPatch
---

# test_pipeline_failure_outside_a_stage_is_failed()

## Connections
- [[MonkeyPatch_12]] - `references` [EXTRACTED]
- [[boom()_1]] - `indirect_call` [INFERRED]
- [[list_pipeline_runs()]] - `calls` [EXTRACTED]
- [[ok()_1]] - `contains` [EXTRACTED]
- [[ok()_2]] - `indirect_call` [INFERRED]
- [[run_pipeline()]] - `calls` [EXTRACTED]
- [[test_monitoring.py]] - `contains` [EXTRACTED]

#graphify/code #graphify/EXTRACTED #community/MonkeyPatch