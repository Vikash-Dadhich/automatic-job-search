---
source_file: "tests/test_role_classify.py"
type: "code"
community: "test_role_classify.py"
location: "L1"
tags:
  - graphify/code
  - graphify/EXTRACTED
  - community/test_role_classifypy
---

# test_role_classify.py

## Connections
- [[RawPosting]] - `imports` [EXTRACTED]
- [[Role classification from the posting. No candidate profile and no live model.]] - `rationale_for` [EXTRACTED]
- [[Source]] - `imports` [EXTRACTED]
- [[_FakeClient]] - `contains` [EXTRACTED]
- [[_apply_role_classification()]] - `imports` [EXTRACTED]
- [[_jd()_1]] - `contains` [EXTRACTED]
- [[classification_is_current()]] - `imports` [EXTRACTED]
- [[classify_role()]] - `imports` [EXTRACTED]
- [[db.py]] - `imports_from` [EXTRACTED]
- [[get_job_by_source_id()]] - `imports` [EXTRACTED]
- [[models.py]] - `imports_from` [EXTRACTED]
- [[pathlib]] - `imports_from` [EXTRACTED]
- [[pytest]] - `imports` [EXTRACTED]
- [[role_classify.py]] - `imports_from` [EXTRACTED]
- [[session_scope()]] - `imports` [EXTRACTED]
- [[test_classification_persists_and_does_not_filter()]] - `contains` [EXTRACTED]
- [[test_classifier_version_bump_invalidates_phase5_v1()]] - `contains` [EXTRACTED]
- [[test_invalid_confidence_is_unknown()]] - `contains` [EXTRACTED]
- [[test_invalid_model_output_falls_back_to_unknown()]] - `contains` [EXTRACTED]
- [[test_role_families_follow_the_job()]] - `contains` [EXTRACTED]
- [[test_short_or_ambiguous_text_is_unknown_without_a_model()]] - `contains` [EXTRACTED]
- [[test_stale_classifier_version_is_replaced_on_reprocess()]] - `contains` [EXTRACTED]
- [[test_truncated_jd_stays_conservative()]] - `contains` [EXTRACTED]
- [[test_unchanged_jd_keeps_classification_and_a_change_replaces_it()]] - `contains` [EXTRACTED]
- [[test_valid_model_output_is_accepted_when_rules_do_not_decide()]] - `contains` [EXTRACTED]
- [[to_job()]] - `imports` [EXTRACTED]
- [[upsert_job()]] - `imports` [EXTRACTED]

#graphify/code #graphify/EXTRACTED #community/test_role_classifypy