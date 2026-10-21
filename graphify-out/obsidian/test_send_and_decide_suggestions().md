---
source_file: "tests/test_suggest.py"
type: "code"
community: "suggest.py"
location: "L128"
tags:
  - graphify/code
  - graphify/EXTRACTED
  - community/suggestpy
---

# test_send_and_decide_suggestions()

## Connections
- [[FakeTransport]] - `calls` [EXTRACTED]
- [[Job]] - `uses` [INFERRED]
- [[RoleBaseline]] - `uses` [INFERRED]
- [[SkillPlacement]] - `uses` [INFERRED]
- [[SkillProvenance]] - `uses` [INFERRED]
- [[SkillSuggestion]] - `uses` [INFERRED]
- [[Source]] - `uses` [INFERRED]
- [[Status]] - `uses` [INFERRED]
- [[SuggestAction]] - `uses` [INFERRED]
- [[SuggestionStatus]] - `uses` [INFERRED]
- [[TelegramClient]] - `uses` [INFERRED]
- [[asyncio_3]] - `references` [EXTRACTED]
- [[decide_suggestion()]] - `calls` [EXTRACTED]
- [[get_job_by_id()]] - `calls` [EXTRACTED]
- [[get_skill_suggestion_by_id()]] - `calls` [EXTRACTED]
- [[get_suggestions_for_job()]] - `calls` [EXTRACTED]
- [[send_pending_suggestions()]] - `calls` [EXTRACTED]
- [[session_scope()]] - `calls` [EXTRACTED]
- [[test_suggest.py]] - `contains` [EXTRACTED]
- [[upsert_job()]] - `calls` [EXTRACTED]

#graphify/code #graphify/EXTRACTED #community/suggestpy