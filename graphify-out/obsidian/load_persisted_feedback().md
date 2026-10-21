---
source_file: "scorer/feedback.py"
type: "code"
community: "AsyncSession"
location: "L497"
tags:
  - graphify/code
  - graphify/EXTRACTED
  - community/AsyncSession
---

# load_persisted_feedback()

## Connections
- [[FeedbackRun]] - `uses` [INFERRED]
- [[FeedbackSignal]] - `uses` [INFERRED]
- [[feedback.py]] - `contains` [EXTRACTED]
- [[get_feedback_run()]] - `calls` [EXTRACTED]
- [[get_feedback_signals()]] - `calls` [EXTRACTED]
- [[init_db()]] - `calls` [EXTRACTED]
- [[session_scope()]] - `calls` [EXTRACTED]
- [[test_feedback.py]] - `imports` [EXTRACTED]
- [[test_persisted_feedback_does_not_change_scores_or_history()]] - `calls` [EXTRACTED]

#graphify/code #graphify/EXTRACTED #community/AsyncSession