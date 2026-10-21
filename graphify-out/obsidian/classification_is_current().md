---
source_file: "scorer/role_classify.py"
type: "code"
community: "test_role_classify.py"
location: "L237"
tags:
  - graphify/code
  - graphify/EXTRACTED
  - community/test_role_classifypy
---

# classification_is_current()

## Connections
- [[True when the stored label was produced for this exact description.]] - `rationale_for` [EXTRACTED]
- [[_apply_role_classification()]] - `calls` [EXTRACTED]
- [[_role_classification_current()]] - `calls` [EXTRACTED]
- [[db.py]] - `imports` [EXTRACTED]
- [[ingest.py]] - `imports` [EXTRACTED]
- [[role_classify.py]] - `contains` [EXTRACTED]
- [[test_cache_recomputes_only_when_hash_or_version_changes()]] - `calls` [EXTRACTED]
- [[test_classifier_version_bump_invalidates_phase5_v1()]] - `calls` [EXTRACTED]
- [[test_role_classify.py]] - `imports` [EXTRACTED]
- [[test_role_secondary.py]] - `imports` [EXTRACTED]
- [[test_unchanged_jd_keeps_classification_and_a_change_replaces_it()]] - `calls` [EXTRACTED]

#graphify/code #graphify/EXTRACTED #community/test_role_classifypy