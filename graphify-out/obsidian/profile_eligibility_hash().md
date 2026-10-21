---
source_file: "scorer/eligibility.py"
type: "code"
community: "test_eligibility.py"
location: "L134"
tags:
  - graphify/code
  - graphify/EXTRACTED
  - community/test_eligibilitypy
---

# profile_eligibility_hash()

## Connections
- [[Hash of the profile facts this engine reads. Dream companies are excluded.]] - `rationale_for` [EXTRACTED]
- [[Profile]] - `uses` [INFERRED]
- [[eligibility.py]] - `contains` [EXTRACTED]
- [[eligibility_is_current()]] - `calls` [EXTRACTED]
- [[evaluate_eligibility_sync()]] - `calls` [EXTRACTED]
- [[hashlib]] - `calls` [EXTRACTED]
- [[json]] - `calls` [EXTRACTED]
- [[test_eligibility.py]] - `imports` [EXTRACTED]
- [[test_signals_do_not_change_eligibility()]] - `calls` [EXTRACTED]

#graphify/code #graphify/EXTRACTED #community/test_eligibilitypy