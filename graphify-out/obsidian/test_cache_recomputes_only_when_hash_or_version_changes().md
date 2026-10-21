---
source_file: "tests/test_role_secondary.py"
type: "code"
community: "classify_role"
location: "L395"
tags:
  - graphify/code
  - graphify/EXTRACTED
  - community/classify_role
---

# test_cache_recomputes_only_when_hash_or_version_changes()

## Connections
- [[MonkeyPatch_5]] - `references` [EXTRACTED]
- [[RawPosting]] - `calls` [EXTRACTED]
- [[Source]] - `uses` [INFERRED]
- [[_apply_role_classification()]] - `calls` [EXTRACTED]
- [[_jd()]] - `calls` [EXTRACTED]
- [[classification_is_current()]] - `calls` [EXTRACTED]
- [[classify_role()]] - `indirect_call` [INFERRED]
- [[counted()_1]] - `indirect_call` [INFERRED]
- [[session_scope()]] - `calls` [EXTRACTED]
- [[test_role_secondary.py]] - `contains` [EXTRACTED]
- [[to_job()]] - `calls` [EXTRACTED]
- [[upsert_job()]] - `calls` [EXTRACTED]

#graphify/code #graphify/EXTRACTED #community/classify_role