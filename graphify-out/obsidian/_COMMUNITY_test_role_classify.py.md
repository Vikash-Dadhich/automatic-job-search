---
type: community
cohesion: 0.17
members: 22
---

# test_role_classify.py

**Cohesion:** 0.17 - loosely connected
**Members:** 22 nodes

## Members
- [[dot-__init__()_29]] - code - tests/test_role_classify.py
- [[dot-complete()_15]] - code - tests/test_role_classify.py
- [[Label the role from the normalized JD. Does not change job status.]] - rationale - scraper/ingest.py
- [[Path_46]] - code
- [[Role classification from the posting. No candidate profile and no live model.]] - rationale - tests/test_role_classify.py
- [[True when the stored label was produced for this exact description.]] - rationale - scorer/role_classify.py
- [[_FakeClient]] - code - tests/test_role_classify.py
- [[_apply_role_classification()]] - code - scraper/ingest.py
- [[_jd()_1]] - code - tests/test_role_classify.py
- [[_role_classification_current()]] - code - core/db.py
- [[classification_is_current()]] - code - scorer/role_classify.py
- [[parametrize_4]] - code
- [[test_classifier_version_bump_invalidates_phase5_v1()]] - code - tests/test_role_classify.py
- [[test_invalid_confidence_is_unknown()]] - code - tests/test_role_classify.py
- [[test_invalid_model_output_falls_back_to_unknown()]] - code - tests/test_role_classify.py
- [[test_role_classify.py]] - code - tests/test_role_classify.py
- [[test_role_families_follow_the_job()]] - code - tests/test_role_classify.py
- [[test_short_or_ambiguous_text_is_unknown_without_a_model()]] - code - tests/test_role_classify.py
- [[test_stale_classifier_version_is_replaced_on_reprocess()]] - code - tests/test_role_classify.py
- [[test_truncated_jd_stays_conservative()]] - code - tests/test_role_classify.py
- [[test_unchanged_jd_keeps_classification_and_a_change_replaces_it()]] - code - tests/test_role_classify.py
- [[test_valid_model_output_is_accepted_when_rules_do_not_decide()]] - code - tests/test_role_classify.py

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/test_role_classifypy
SORT file.name ASC
```

## Connections to other communities
- 13 edges to [[_COMMUNITY_classify_role]]
- 11 edges to [[_COMMUNITY_Source]]
- 10 edges to [[_COMMUNITY_upsert_job]]
- 3 edges to [[_COMMUNITY_session_scope]]
- 3 edges to [[_COMMUNITY_db.py]]
- 2 edges to [[_COMMUNITY_Job]]
- 2 edges to [[_COMMUNITY_ingest.py]]
- 2 edges to [[_COMMUNITY_role_classify.py]]
- 1 edge to [[_COMMUNITY_structured_jd.py]]
- 1 edge to [[_COMMUNITY_LLMClient]]
- 1 edge to [[_COMMUNITY_test_structured_jd.py]]
- 1 edge to [[_COMMUNITY_pytest]]
- 1 edge to [[_COMMUNITY_pathlib]]

## Top bridge nodes
- [[test_role_classify.py]] - degree 27, connects to 8 communities
- [[_apply_role_classification()]] - degree 14, connects to 8 communities
- [[classification_is_current()]] - degree 11, connects to 4 communities
- [[test_unchanged_jd_keeps_classification_and_a_change_replaces_it()]] - degree 11, connects to 4 communities
- [[test_stale_classifier_version_is_replaced_on_reprocess()]] - degree 9, connects to 3 communities