---
source_file: "tests/test_calibration.py"
type: "code"
community: "test_feedback.py"
location: "L299"
tags:
  - graphify/code
  - graphify/EXTRACTED
  - community/test_feedbackpy
---

# test_persisted_calibration_leaves_scores_and_events_unchanged()

## Connections
- [[Application]] - `calls` [EXTRACTED]
- [[ApplicationEvent]] - `calls` [EXTRACTED]
- [[Job]] - `calls` [EXTRACTED]
- [[Path_33]] - `references` [EXTRACTED]
- [[Source]] - `uses` [INFERRED]
- [[Status]] - `uses` [INFERRED]
- [[get_application_events()]] - `calls` [EXTRACTED]
- [[get_job_by_id()]] - `calls` [EXTRACTED]
- [[load_persisted_calibration()]] - `calls` [EXTRACTED]
- [[persist_calibration()]] - `calls` [EXTRACTED]
- [[run_calibration()]] - `calls` [EXTRACTED]
- [[session_scope()]] - `calls` [EXTRACTED]
- [[test_calibration.py]] - `contains` [EXTRACTED]
- [[upsert_job()]] - `calls` [EXTRACTED]

#graphify/code #graphify/EXTRACTED #community/test_feedbackpy