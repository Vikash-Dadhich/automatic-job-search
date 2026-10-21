---
source_file: "scorer/calibration.py"
type: "code"
community: "AsyncSession"
location: "L799"
tags:
  - graphify/code
  - graphify/EXTRACTED
  - community/AsyncSession
---

# load_persisted_calibration()

## Connections
- [[CalibrationMetric]] - `uses` [INFERRED]
- [[CalibrationRun]] - `uses` [INFERRED]
- [[calibration.py]] - `contains` [EXTRACTED]
- [[get_calibration_metrics()]] - `calls` [EXTRACTED]
- [[get_calibration_run()]] - `calls` [EXTRACTED]
- [[init_db()]] - `calls` [EXTRACTED]
- [[session_scope()]] - `calls` [EXTRACTED]
- [[test_calibration.py]] - `imports` [EXTRACTED]
- [[test_offer_is_scored_separately_from_interview()]] - `calls` [EXTRACTED]
- [[test_persisted_calibration_leaves_scores_and_events_unchanged()]] - `calls` [EXTRACTED]

#graphify/code #graphify/EXTRACTED #community/AsyncSession