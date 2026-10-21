---
source_file: "scorer/eligibility.py"
type: "code"
community: "test_eligibility.py"
location: "L511"
tags:
  - graphify/code
  - graphify/EXTRACTED
  - community/test_eligibilitypy
---

# evaluate_eligibility()

## Connections
- [[EligibilityDecision]] - `calls` [EXTRACTED]
- [[Job]] - `uses` [INFERRED]
- [[LLMClient_1]] - `uses` [INFERRED]
- [[Profile]] - `uses` [INFERRED]
- [[Return a cached decision, or compute one. Model failure stays UNKNOWN.]] - `rationale_for` [EXTRACTED]
- [[_ask_model()]] - `calls` [EXTRACTED]
- [[_decision_from_job()]] - `calls` [EXTRACTED]
- [[_posting_text()]] - `calls` [EXTRACTED]
- [[attach_eligibility()]] - `calls` [EXTRACTED]
- [[eligibility.py]] - `contains` [EXTRACTED]
- [[eligibility_is_current()]] - `calls` [EXTRACTED]
- [[evaluate_eligibility_sync()]] - `calls` [EXTRACTED]
- [[test_cache_identity()]] - `calls` [EXTRACTED]
- [[test_citizenship_clearance_and_eeo()]] - `calls` [EXTRACTED]
- [[test_education_graduation_and_experience()]] - `calls` [EXTRACTED]
- [[test_eligibility.py]] - `imports` [EXTRACTED]
- [[test_explicit_sponsorship_paths()]] - `calls` [EXTRACTED]
- [[test_false_negative.py]] - `imports` [EXTRACTED]
- [[test_first_discovery_provenance_is_immutable()]] - `calls` [EXTRACTED]
- [[test_hostile_language_wins_and_false_friends_do_not()]] - `calls` [EXTRACTED]
- [[test_location_is_not_a_seattle_gate()]] - `calls` [EXTRACTED]
- [[test_malformed_model_stays_unknown()]] - `calls` [EXTRACTED]
- [[test_recruiting_universe.py]] - `imports` [EXTRACTED]
- [[test_signals_do_not_change_eligibility()]] - `calls` [EXTRACTED]
- [[test_unknown_authorization_and_dates()]] - `calls` [EXTRACTED]
- [[test_unknown_eligibility_is_not_a_rejection()]] - `calls` [EXTRACTED]

#graphify/code #graphify/EXTRACTED #community/test_eligibilitypy