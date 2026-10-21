---
source_file: "tests/test_vector_gate.py"
type: "code"
community: "test_vector_recovery.py"
location: "L468"
tags:
  - graphify/code
  - graphify/EXTRACTED
  - community/test_vector_recoverypy
---

# test_profile_change_reuses_jd_vector()

## Connections
- [[FakeClient_3]] - `calls` [EXTRACTED]
- [[FakeEmbedder]] - `calls` [EXTRACTED]
- [[MonkeyPatch_19]] - `references` [EXTRACTED]
- [[Profile]] - `uses` [INFERRED]
- [[Status]] - `uses` [INFERRED]
- [[_enable()_1]] - `calls` [EXTRACTED]
- [[_seed()_1]] - `calls` [EXTRACTED]
- [[get_job_by_id()]] - `calls` [EXTRACTED]
- [[get_settings()]] - `calls` [EXTRACTED]
- [[job_embed_text()]] - `calls` [EXTRACTED]
- [[profile_embed_text()]] - `calls` [EXTRACTED]
- [[profile_hash()_1]] - `calls` [EXTRACTED]
- [[score_pending()]] - `calls` [EXTRACTED]
- [[session_scope()]] - `calls` [EXTRACTED]
- [[test_vector_gate.py]] - `contains` [EXTRACTED]

#graphify/code #graphify/EXTRACTED #community/test_vector_recoverypy