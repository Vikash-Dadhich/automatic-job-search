---
source_file: "tests/test_llm_resilience.py"
type: "code"
community: "clients.py"
location: "L1"
tags:
  - graphify/code
  - graphify/EXTRACTED
  - community/clientspy
---

# test_llm_resilience.py

## Connections
- [[LLMBillingError]] - `imports` [EXTRACTED]
- [[LLMError]] - `imports` [EXTRACTED]
- [[Tests for transient-error classification and the retryfallback wrapper.]] - `rationale_for` [EXTRACTED]
- [[TruncatedCompletionError]] - `imports` [EXTRACTED]
- [[call_with_resilience()]] - `imports` [EXTRACTED]
- [[clients.py]] - `imports_from` [EXTRACTED]
- [[is_permanent_account_error()]] - `imports` [EXTRACTED]
- [[is_transient()]] - `imports` [EXTRACTED]
- [[pytest]] - `imports` [EXTRACTED]
- [[suggested_delay()]] - `imports` [EXTRACTED]
- [[test_call_with_resilience_falls_through_to_next_model()]] - `contains` [EXTRACTED]
- [[test_call_with_resilience_raises_llm_error_when_all_fail()]] - `contains` [EXTRACTED]
- [[test_call_with_resilience_reraises_permanent_error()]] - `contains` [EXTRACTED]
- [[test_call_with_resilience_retries_then_succeeds()]] - `contains` [EXTRACTED]
- [[test_depleted_credits_fail_fast_without_fallback()]] - `contains` [EXTRACTED]
- [[test_is_transient_covers_rate_limit_and_overload()]] - `contains` [EXTRACTED]
- [[test_is_transient_excludes_permanent_errors()]] - `contains` [EXTRACTED]
- [[test_rate_limit_and_depleted_credits_are_distinguished()]] - `contains` [EXTRACTED]
- [[test_suggested_delay_reads_server_hint()]] - `contains` [EXTRACTED]

#graphify/code #graphify/EXTRACTED #community/clientspy