---
type: community
cohesion: 0.12
members: 29
---

# test_llm_provider.py

**Cohesion:** 0.12 - loosely connected
**Members:** 29 nodes

## Members
- [[dot-generate_content()]] - code - tests/test_llm_provider.py
- [[A 503 on the primary model must roll over to the configured fallback.]] - rationale - tests/test_llm_provider.py
- [[Any_52]] - code
- [[MonkeyPatch_30]] - code
- [[Offline tests for switchable LLM provider (Gemini default  Anthropic fallback).]] - rationale - tests/test_llm_provider.py
- [[OpenAI Chat Completions client. JSON scoring uses json_object mode.]] - rationale - scorer/clients.py
- [[OpenAIClient]] - code - scorer/clients.py
- [[Thinking can eat the whole budget; retry must raise max_output_tokens.]] - rationale - tests/test_llm_provider.py
- [[_FakeAio]] - code - tests/test_llm_provider.py
- [[_FakeAsyncModels]] - code - tests/test_llm_provider.py
- [[_FakeCandidate]] - code - tests/test_llm_provider.py
- [[_FakeGenaiClient]] - code - tests/test_llm_provider.py
- [[_FakeGenerateResponse]] - code - tests/test_llm_provider.py
- [[__init__()_5]] - code - tests/test_llm_provider.py
- [[asyncio_10]] - code
- [[create()]] - code - tests/test_llm_provider.py
- [[test_active_models_ignore_anthropic_names()]] - code - tests/test_llm_provider.py
- [[test_active_models_ignore_other_providers()]] - code - tests/test_llm_provider.py
- [[test_build_llm_client_always_openai()]] - code - tests/test_llm_provider.py
- [[test_build_llm_client_ignores_anthropic_provider()]] - code - tests/test_llm_provider.py
- [[test_build_llm_client_openai_requires_key()]] - code - tests/test_llm_provider.py
- [[test_build_llm_client_unknown_provider_still_openai()]] - code - tests/test_llm_provider.py
- [[test_gemini_client_complete_maps_system_blocks()]] - code - tests/test_llm_provider.py
- [[test_gemini_client_escalates_on_truncated_output()]] - code - tests/test_llm_provider.py
- [[test_gemini_client_falls_back_when_model_unavailable()]] - code - tests/test_llm_provider.py
- [[test_gemini_client_requires_api_key()]] - code - tests/test_llm_provider.py
- [[test_llm_provider.py]] - code - tests/test_llm_provider.py
- [[test_openai_client_scores_json()]] - code - tests/test_llm_provider.py
- [[test_system_blocks_to_text_joins_and_skips_empty()]] - code - tests/test_llm_provider.py

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/test_llm_providerpy
SORT file.name ASC
```

## Connections to other communities
- 6 edges to [[_COMMUNITY_Any_1]]
- 5 edges to [[_COMMUNITY_Settings]]
- 5 edges to [[_COMMUNITY_diff.py]]
- 3 edges to [[_COMMUNITY_clients.py]]
- 3 edges to [[_COMMUNITY_get_settings]]
- 3 edges to [[_COMMUNITY_pytest]]
- 2 edges to [[_COMMUNITY_TokenUsage]]
- 2 edges to [[_COMMUNITY_typing]]
- 1 edge to [[_COMMUNITY_scorerengine.py]]
- 1 edge to [[_COMMUNITY_test_resume.py]]

## Top bridge nodes
- [[test_llm_provider.py]] - degree 30, connects to 7 communities
- [[OpenAIClient]] - degree 14, connects to 5 communities
- [[test_build_llm_client_openai_requires_key()]] - degree 4, connects to 2 communities
- [[test_gemini_client_requires_api_key()]] - degree 4, connects to 2 communities
- [[test_gemini_client_falls_back_when_model_unavailable()]] - degree 6, connects to 1 community