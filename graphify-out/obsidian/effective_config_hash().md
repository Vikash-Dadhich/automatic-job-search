---
source_file: "config/diagnostics.py"
type: "code"
community: "json"
location: "L66"
tags:
  - graphify/code
  - graphify/EXTRACTED
  - community/json
---

# effective_config_hash()

## Connections
- [[SHA-256 of ``public_config``. Changes when an effective setting changes.]] - `rationale_for` [EXTRACTED]
- [[Settings]] - `uses` [INFERRED]
- [[diagnostics.py]] - `contains` [EXTRACTED]
- [[effective_baseline()]] - `calls` [EXTRACTED]
- [[hashlib]] - `calls` [EXTRACTED]
- [[json]] - `calls` [EXTRACTED]
- [[monitoring.py]] - `imports` [EXTRACTED]
- [[operational_config_hash()]] - `calls` [EXTRACTED]
- [[public_config()]] - `calls` [EXTRACTED]
- [[test_baseline_file_has_no_secrets()]] - `calls` [EXTRACTED]
- [[test_config_hash_changes_when_internship_only_changes()]] - `calls` [EXTRACTED]
- [[test_diagnostics.py]] - `imports` [EXTRACTED]

#graphify/code #graphify/EXTRACTED #community/json