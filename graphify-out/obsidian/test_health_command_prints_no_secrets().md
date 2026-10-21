---
source_file: "tests/test_monitoring.py"
type: "code"
community: "MonkeyPatch"
location: "L365"
tags:
  - graphify/code
  - graphify/EXTRACTED
  - community/MonkeyPatch
---

# test_health_command_prints_no_secrets()

## Connections
- [[CaptureFixture]] - `references` [EXTRACTED]
- [[MonkeyPatch_12]] - `references` [EXTRACTED]
- [[main()]] - `calls` [EXTRACTED]
- [[reset_engine()]] - `calls` [EXTRACTED]
- [[scheduler_must_not_start()]] - `indirect_call` [INFERRED]
- [[test_monitoring.py]] - `contains` [EXTRACTED]

#graphify/code #graphify/EXTRACTED #community/MonkeyPatch