---
type: community
cohesion: 0.09
members: 41
---

# clients.py

**Cohesion:** 0.09 - loosely connected
**Members:** 41 nodes

## Members
- [[Account has no credit  invalid key — retrying and failing over is pointless.]] - rationale - scorer/clients.py
- [[BaseException_1]] - code
- [[Both are 429; only the per-minute rate limit is worth retrying.]] - rationale - tests/test_llm_resilience.py
- [[Burning the whole fallback chain on a dead account wastes ~2 minutes.]] - rationale - tests/test_llm_resilience.py
- [[LLM client layer (`scorerclients.py`)]] - document - AGENTS.md
- [[LLM client layer provider clients, transient-error retries, model fallback.…]] - rationale - scorer/clients.py
- [[LLMBillingError]] - code - scorer/clients.py
- [[LLMError]] - code - scorer/clients.py
- [[Model hit max_output_tokens before producing a usable answer.]] - rationale - scorer/clients.py
- [[Raised when a completion cannot be obtained from any candidate model.]] - rationale - scorer/clients.py
- [[Run attempt_fn(model) across candidate models, retrying transient errors. Each…]] - rationale - scorer/clients.py
- [[RuntimeError_2]] - code
- [[Server-provided retryDelay, when the API supplies one.]] - rationale - scorer/clients.py
- [[Step thinking down so a retry spends its budget on the answer, not reasoning.]] - rationale - scorer/clients.py
- [[Tests for transient-error classification and the retryfallback wrapper.]] - rationale - tests/test_llm_resilience.py
- [[True for rate limits, overload, and server-side hiccups worth retrying.]] - rationale - scorer/clients.py
- [[TruncatedCompletionError]] - code - scorer/clients.py
- [[_attempt()_2]] - code - scorer/clients.py
- [[_backoff_delay()]] - code - scorer/clients.py
- [[_lower_thinking()]] - code - scorer/clients.py
- [[_status_code()]] - code - scorer/clients.py
- [[always_down()]] - code - tests/test_llm_resilience.py
- [[asyncio_7]] - code
- [[bad_request()]] - code - tests/test_llm_resilience.py
- [[broke()]] - code - tests/test_llm_resilience.py
- [[call_with_resilience()]] - code - scorer/clients.py
- [[clients.py]] - code - scorer/clients.py
- [[flaky()]] - code - tests/test_llm_resilience.py
- [[is_transient()]] - code - scorer/clients.py
- [[only_second_works()]] - code - tests/test_llm_resilience.py
- [[suggested_delay()]] - code - scorer/clients.py
- [[test_call_with_resilience_falls_through_to_next_model()]] - code - tests/test_llm_resilience.py
- [[test_call_with_resilience_raises_llm_error_when_all_fail()]] - code - tests/test_llm_resilience.py
- [[test_call_with_resilience_reraises_permanent_error()]] - code - tests/test_llm_resilience.py
- [[test_call_with_resilience_retries_then_succeeds()]] - code - tests/test_llm_resilience.py
- [[test_depleted_credits_fail_fast_without_fallback()]] - code - tests/test_llm_resilience.py
- [[test_is_transient_covers_rate_limit_and_overload()]] - code - tests/test_llm_resilience.py
- [[test_is_transient_excludes_permanent_errors()]] - code - tests/test_llm_resilience.py
- [[test_llm_resilience.py]] - code - tests/test_llm_resilience.py
- [[test_rate_limit_and_depleted_credits_are_distinguished()]] - code - tests/test_llm_resilience.py
- [[test_suggested_delay_reads_server_hint()]] - code - tests/test_llm_resilience.py

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/clientspy
SORT file.name ASC
```

## Connections to other communities
- 15 edges to [[_COMMUNITY_scorerengine.py]]
- 13 edges to [[_COMMUNITY_Any_1]]
- 4 edges to [[_COMMUNITY_pytest]]
- 3 edges to [[_COMMUNITY_TokenUsage]]
- 3 edges to [[_COMMUNITY_test_llm_provider.py]]
- 3 edges to [[_COMMUNITY_re]]
- 2 edges to [[_COMMUNITY_diff.py]]
- 2 edges to [[_COMMUNITY_workday.py]]
- 2 edges to [[_COMMUNITY_asyncio]]
- 2 edges to [[_COMMUNITY_ingest.py]]
- 2 edges to [[_COMMUNITY_typing]]
- 2 edges to [[_COMMUNITY_test_scorer.py]]
- 1 edge to [[_COMMUNITY_LLMClient]]
- 1 edge to [[_COMMUNITY_get_settings]]
- 1 edge to [[_COMMUNITY_role_classify.py]]
- 1 edge to [[_COMMUNITY_conftest.py]]
- 1 edge to [[_COMMUNITY_eligibility.py]]
- 1 edge to [[_COMMUNITY_skills.py]]
- 1 edge to [[_COMMUNITY_test_resume.py]]
- 1 edge to [[_COMMUNITY_test_fit.py]]

## Top bridge nodes
- [[clients.py]] - degree 40, connects to 18 communities
- [[LLM client layer (`scorerclients.py`)]] - degree 7, connects to 5 communities
- [[call_with_resilience()]] - degree 19, connects to 3 communities
- [[test_llm_resilience.py]] - degree 19, connects to 2 communities
- [[is_transient()]] - degree 12, connects to 1 community