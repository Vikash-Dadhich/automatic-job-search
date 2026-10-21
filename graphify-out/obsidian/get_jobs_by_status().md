---
source_file: "core/db.py"
type: "code"
community: "test_phase13_shortlist.py"
location: "L1221"
tags:
  - graphify/code
  - graphify/EXTRACTED
  - community/test_phase13_shortlistpy
---

# get_jobs_by_status()

## Connections
- [[dot-apply_pending()]] - `calls` [EXTRACTED]
- [[dot-score_pending()]] - `calls` [EXTRACTED]
- [[AsyncSession_1]] - `references` [EXTRACTED]
- [[Job]] - `references` [EXTRACTED]
- [[Return jobs with the given status, oldest first.]] - `rationale_for` [EXTRACTED]
- [[Status]] - `references` [EXTRACTED]
- [[Status lifecycle]] - `references` [INFERRED]
- [[_cmd_list_apply()]] - `calls` [EXTRACTED]
- [[application_portfolio.py]] - `imports` [EXTRACTED]
- [[apply_portfolio()]] - `calls` [EXTRACTED]
- [[apply_shortlist()]] - `calls` [EXTRACTED]
- [[compile_pending()]] - `calls` [EXTRACTED]
- [[compiler.py]] - `imports` [EXTRACTED]
- [[db.py]] - `contains` [EXTRACTED]
- [[main.py]] - `imports` [EXTRACTED]
- [[prepare_pending()]] - `calls` [EXTRACTED]
- [[record_prepare()]] - `calls` [EXTRACTED]
- [[runner.py]] - `imports` [EXTRACTED]
- [[scorerengine.py]] - `imports` [EXTRACTED]
- [[shortlist.py]] - `imports` [EXTRACTED]
- [[test_phase13_shortlist.py]] - `imports` [EXTRACTED]
- [[test_pipeline_enriches_the_review_queue_and_apply_stays_on_staged()]] - `calls` [EXTRACTED]

#graphify/code #graphify/EXTRACTED #community/test_phase13_shortlistpy