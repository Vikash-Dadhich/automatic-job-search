---
source_file: "scraper/ingest.py"
type: "code"
community: "test_role_classify.py"
location: "L59"
tags:
  - graphify/code
  - graphify/EXTRACTED
  - community/test_role_classifypy
---

# _apply_role_classification()

## Connections
- [[Job]] - `uses` [INFERRED]
- [[LLMClient_1]] - `uses` [INFERRED]
- [[Label the role from the normalized JD. Does not change job status.]] - `rationale_for` [EXTRACTED]
- [[StructuredJdDocument]] - `uses` [INFERRED]
- [[classification_is_current()]] - `calls` [EXTRACTED]
- [[classify_role()]] - `calls` [EXTRACTED]
- [[get_job_by_source_id()]] - `calls` [EXTRACTED]
- [[get_structured_jd()]] - `calls` [EXTRACTED]
- [[ingest.py]] - `contains` [EXTRACTED]
- [[run_ingestion()]] - `calls` [EXTRACTED]
- [[test_cache_recomputes_only_when_hash_or_version_changes()]] - `calls` [EXTRACTED]
- [[test_role_classify.py]] - `imports` [EXTRACTED]
- [[test_role_secondary.py]] - `imports` [EXTRACTED]
- [[test_stale_classifier_version_is_replaced_on_reprocess()]] - `calls` [EXTRACTED]

#graphify/code #graphify/EXTRACTED #community/test_role_classifypy