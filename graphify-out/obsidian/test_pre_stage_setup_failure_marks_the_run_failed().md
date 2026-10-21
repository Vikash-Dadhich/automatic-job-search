---
source_file: "tests/test_monitoring.py"
type: "code"
community: "MonkeyPatch"
location: "L192"
tags:
  - graphify/code
  - graphify/EXTRACTED
  - community/MonkeyPatch
---

# test_pre_stage_setup_failure_marks_the_run_failed()

## Connections
- [[MonkeyPatch_12]] - `references` [EXTRACTED]
- [[boom()_2]] - `contains` [EXTRACTED]
- [[boom()_1]] - `indirect_call` [INFERRED]
- [[list_pipeline_runs()]] - `calls` [EXTRACTED]
- [[run_pipeline()]] - `calls` [EXTRACTED]
- [[test_monitoring.py]] - `contains` [EXTRACTED]

#graphify/code #graphify/EXTRACTED #community/MonkeyPatch