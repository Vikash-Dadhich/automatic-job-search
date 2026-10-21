---
source_file: "tests/test_phase13_shortlist.py"
type: "code"
community: "test_phase13_shortlist.py"
location: "L458"
tags:
  - graphify/code
  - graphify/EXTRACTED
  - community/test_phase13_shortlistpy
---

# test_pipeline_enriches_the_review_queue_and_apply_stays_on_staged()

## Connections
- [[MonkeyPatch_14]] - `references` [EXTRACTED]
- [[Path_24]] - `references` [EXTRACTED]
- [[Source]] - `uses` [INFERRED]
- [[Status]] - `uses` [INFERRED]
- [[Tier]] - `uses` [INFERRED]
- [[_SpyApplicator]] - `calls` [EXTRACTED]
- [[_job()_6]] - `calls` [EXTRACTED]
- [[apply_pending()]] - `calls` [EXTRACTED]
- [[fake_benchmark()_1]] - `indirect_call` [INFERRED]
- [[fake_suggest()]] - `indirect_call` [INFERRED]
- [[get_job_by_id()]] - `calls` [EXTRACTED]
- [[get_jobs_by_status()]] - `calls` [EXTRACTED]
- [[get_unsent_pending_reviews()]] - `calls` [EXTRACTED]
- [[noop()]] - `indirect_call` [INFERRED]
- [[record_prepare()]] - `indirect_call` [INFERRED]
- [[run_pipeline()]] - `calls` [EXTRACTED]
- [[session_scope()]] - `calls` [EXTRACTED]
- [[test_phase13_shortlist.py]] - `contains` [EXTRACTED]
- [[upsert_job()]] - `calls` [EXTRACTED]

#graphify/code #graphify/EXTRACTED #community/test_phase13_shortlistpy