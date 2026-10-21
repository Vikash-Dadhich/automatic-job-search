---
source_file: "tests/test_llm_resilience.py"
type: "code"
community: "clients.py"
location: "L40"
tags:
  - graphify/code
  - graphify/EXTRACTED
  - community/clientspy
---

# test_rate_limit_and_depleted_credits_are_distinguished()

## Connections
- [[Both are 429; only the per-minute rate limit is worth retrying.]] - `rationale_for` [EXTRACTED]
- [[is_permanent_account_error()]] - `calls` [EXTRACTED]
- [[is_transient()]] - `calls` [EXTRACTED]
- [[test_llm_resilience.py]] - `contains` [EXTRACTED]

#graphify/code #graphify/EXTRACTED #community/clientspy