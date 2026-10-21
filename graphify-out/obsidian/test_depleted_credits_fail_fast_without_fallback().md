---
source_file: "tests/test_llm_resilience.py"
type: "code"
community: "clients.py"
location: "L49"
tags:
  - graphify/code
  - graphify/EXTRACTED
  - community/clientspy
---

# test_depleted_credits_fail_fast_without_fallback()

## Connections
- [[Burning the whole fallback chain on a dead account wastes ~2 minutes.]] - `rationale_for` [EXTRACTED]
- [[LLMBillingError]] - `uses` [INFERRED]
- [[asyncio_7]] - `references` [EXTRACTED]
- [[broke()]] - `indirect_call` [INFERRED]
- [[call_with_resilience()]] - `calls` [EXTRACTED]
- [[pytest]] - `calls` [EXTRACTED]
- [[test_llm_resilience.py]] - `contains` [EXTRACTED]

#graphify/code #graphify/EXTRACTED #community/clientspy