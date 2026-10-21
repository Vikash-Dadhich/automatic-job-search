---
source_file: "scorer/cover_letter.py"
type: "code"
community: "test_scorer.py"
location: "L52"
tags:
  - graphify/code
  - graphify/EXTRACTED
  - community/test_scorerpy
---

# generate_cover_letter()

## Connections
- [[Draft a short cover letter; retry once if banned words appear.]] - `rationale_for` [EXTRACTED]
- [[Job]] - `uses` [INFERRED]
- [[LLMClient_1]] - `uses` [INFERRED]
- [[Profile]] - `uses` [INFERRED]
- [[_fallback_cover_letter()]] - `calls` [EXTRACTED]
- [[build_cover_letter_user()]] - `calls` [EXTRACTED]
- [[cap_cover_letter()]] - `calls` [EXTRACTED]
- [[contains_banned()]] - `calls` [EXTRACTED]
- [[cover_letter.py]] - `contains` [EXTRACTED]
- [[get_settings()]] - `calls` [EXTRACTED]
- [[run_one()]] - `indirect_call` [INFERRED]
- [[scorerengine.py]] - `imports` [EXTRACTED]
- [[strip_banned_sentences()]] - `calls` [EXTRACTED]
- [[test_cover_letter.py]] - `imports` [EXTRACTED]
- [[test_generate_cover_letter_falls_back_when_strip_empties()]] - `calls` [EXTRACTED]
- [[test_generate_cover_letter_retries_banned_words()]] - `calls` [EXTRACTED]

#graphify/code #graphify/EXTRACTED #community/test_scorerpy