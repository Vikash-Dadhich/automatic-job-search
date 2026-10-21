---
source_file: "tests/test_llm_resilience.py"
type: "code"
community: "clients.py"
location: "L112"
tags:
  - graphify/code
  - graphify/EXTRACTED
  - community/clientspy
---

# test_call_with_resilience_raises_llm_error_when_all_fail()

## Connections
- [[LLMError]] - `uses` [INFERRED]
- [[always_down()]] - `indirect_call` [INFERRED]
- [[asyncio_7]] - `references` [EXTRACTED]
- [[call_with_resilience()]] - `calls` [EXTRACTED]
- [[pytest]] - `calls` [EXTRACTED]
- [[test_llm_resilience.py]] - `contains` [EXTRACTED]

#graphify/code #graphify/EXTRACTED #community/clientspy