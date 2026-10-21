---
source_file: "tests/test_llm_resilience.py"
type: "rationale"
community: "clients.py"
location: "L50"
tags:
  - graphify/rationale
  - graphify/EXTRACTED
  - community/clientspy
---

# Burning the whole fallback chain on a dead account wastes ~2 minutes.

## Connections
- [[test_depleted_credits_fail_fast_without_fallback()]] - `rationale_for` [EXTRACTED]

#graphify/rationale #graphify/EXTRACTED #community/clientspy