---
source_file: "scorer/role_classify.py"
type: "code"
community: "classify_role"
location: "L654"
tags:
  - graphify/code
  - graphify/EXTRACTED
  - community/classify_role
---

# classify_role()

## Connections
- [[Any_6]] - `references` [EXTRACTED]
- [[Classify the role from the posting. Discovery labels are not copied across.]] - `rationale_for` [EXTRACTED]
- [[LLMClient_1]] - `uses` [INFERRED]
- [[RoleClassification]] - `references` [EXTRACTED]
- [[_apply_role_classification()]] - `calls` [EXTRACTED]
- [[_deterministic()]] - `calls` [EXTRACTED]
- [[_family()_1]] - `calls` [EXTRACTED]
- [[_parse_model()]] - `calls` [EXTRACTED]
- [[_structured_prompt()]] - `calls` [EXTRACTED]
- [[_unknown()]] - `calls` [EXTRACTED]
- [[ingest.py]] - `imports` [EXTRACTED]
- [[role_classify.py]] - `contains` [EXTRACTED]
- [[test_cache_recomputes_only_when_hash_or_version_changes()]] - `indirect_call` [INFERRED]
- [[test_classification_persists_and_does_not_filter()]] - `calls` [EXTRACTED]
- [[test_collaboration_responsibility_is_not_a_secondary_family()]] - `calls` [EXTRACTED]
- [[test_hybrid_roles_keep_a_second_family()]] - `calls` [EXTRACTED]
- [[test_interaction_evidence_from_the_model_is_rejected()]] - `calls` [EXTRACTED]
- [[test_interaction_is_not_a_second_family()]] - `calls` [EXTRACTED]
- [[test_invalid_confidence_is_unknown()]] - `calls` [EXTRACTED]
- [[test_invalid_model_output_falls_back_to_unknown()]] - `calls` [EXTRACTED]
- [[test_llm_prompt_includes_structured_responsibilities()]] - `calls` [EXTRACTED]
- [[test_one_phrase_needs_structured_confirmation()]] - `calls` [EXTRACTED]
- [[test_pure_roles_have_no_secondary_family()]] - `calls` [EXTRACTED]
- [[test_qualification_only_mention_is_not_a_secondary_family()]] - `calls` [EXTRACTED]
- [[test_recruiting_universe.py]] - `imports` [EXTRACTED]
- [[test_responsibility_evidence_still_marks_a_hybrid()]] - `calls` [EXTRACTED]
- [[test_role_classify.py]] - `imports` [EXTRACTED]
- [[test_role_families_follow_the_job()]] - `calls` [EXTRACTED]
- [[test_role_secondary.py]] - `imports` [EXTRACTED]
- [[test_secondary_fields_persist_and_clear_when_the_jd_changes()]] - `calls` [EXTRACTED]
- [[test_short_or_ambiguous_text_is_unknown_without_a_model()]] - `calls` [EXTRACTED]
- [[test_short_text_stays_unknown()]] - `calls` [EXTRACTED]
- [[test_technology_strategy_is_not_technology_consulting()]] - `calls` [EXTRACTED]
- [[test_truncated_jd_stays_conservative()]] - `calls` [EXTRACTED]
- [[test_truncated_posting_has_no_secondary_family()]] - `calls` [EXTRACTED]
- [[test_unchanged_jd_keeps_classification_and_a_change_replaces_it()]] - `calls` [EXTRACTED]
- [[test_valid_model_output_is_accepted_when_rules_do_not_decide()]] - `calls` [EXTRACTED]

#graphify/code #graphify/EXTRACTED #community/classify_role