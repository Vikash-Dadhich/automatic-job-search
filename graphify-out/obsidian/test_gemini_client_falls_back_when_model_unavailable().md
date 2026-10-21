---
source_file: "tests/test_llm_provider.py"
type: "code"
community: "test_llm_provider.py"
location: "L259"
tags:
  - graphify/code
  - graphify/EXTRACTED
  - community/test_llm_providerpy
---

# test_gemini_client_falls_back_when_model_unavailable()

## Connections
- [[A 503 on the primary model must roll over to the configured fallback.]] - `rationale_for` [EXTRACTED]
- [[GeminiClient]] - `calls` [EXTRACTED]
- [[MonkeyPatch_30]] - `references` [EXTRACTED]
- [[_FakeGenaiClient]] - `calls` [EXTRACTED]
- [[asyncio_10]] - `references` [EXTRACTED]
- [[test_llm_provider.py]] - `contains` [EXTRACTED]

#graphify/code #graphify/EXTRACTED #community/test_llm_providerpy