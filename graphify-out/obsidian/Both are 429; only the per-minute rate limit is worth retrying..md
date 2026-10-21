---
source_file: "tests/test_llm_resilience.py"
type: "rationale"
community: "clients.py"
location: "L41"
tags:
  - graphify/rationale
  - graphify/EXTRACTED
  - community/clientspy
---

# Both are 429; only the per-minute rate limit is worth retrying.

## Connections
- [[test_rate_limit_and_depleted_credits_are_distinguished()]] - `rationale_for` [EXTRACTED]

#graphify/rationale #graphify/EXTRACTED #community/clientspy