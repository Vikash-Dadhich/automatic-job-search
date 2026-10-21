---
source_file: "bot/outcomes.py"
type: "code"
community: "handlers.py"
location: "L127"
tags:
  - graphify/code
  - graphify/EXTRACTED
  - community/handlerspy
---

# send_pending_outcome_prompts()

## Connections
- [[Backfill outcome keyboards for submitted jobs that never got one.]] - `rationale_for` [EXTRACTED]
- [[OutcomePromptSummary]] - `calls` [EXTRACTED]
- [[TelegramClient]] - `calls` [EXTRACTED]
- [[get_jobs_needing_outcome_prompt()]] - `calls` [EXTRACTED]
- [[init_db()]] - `calls` [EXTRACTED]
- [[outcomes.py]] - `contains` [EXTRACTED]
- [[pipeline.py]] - `indirect_call` [INFERRED]
- [[send_outcome_prompt()]] - `calls` [EXTRACTED]
- [[session_scope()]] - `calls` [EXTRACTED]

#graphify/code #graphify/EXTRACTED #community/handlerspy