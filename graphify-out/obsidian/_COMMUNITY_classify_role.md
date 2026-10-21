---
type: community
cohesion: 0.19
members: 23
---

# classify_role

**Cohesion:** 0.19 - loosely connected
**Members:** 23 nodes

## Members
- [[Classify the role from the posting. Discovery labels are not copied across.]] - rationale - scorer/role_classify.py
- [[MonkeyPatch_5]] - code
- [[Primary and secondary role families. Downstream decisions stay on the primary…]] - rationale - tests/test_role_secondary.py
- [[_jd()]] - code - tests/test_role_secondary.py
- [[classify_role()]] - code - scorer/role_classify.py
- [[complete()]] - code - tests/test_role_secondary.py
- [[complete()_1]] - code - tests/test_role_secondary.py
- [[counted()_1]] - code - tests/test_role_secondary.py
- [[test_cache_recomputes_only_when_hash_or_version_changes()]] - code - tests/test_role_secondary.py
- [[test_collaboration_responsibility_is_not_a_secondary_family()]] - code - tests/test_role_secondary.py
- [[test_hybrid_roles_keep_a_second_family()]] - code - tests/test_role_secondary.py
- [[test_interaction_evidence_from_the_model_is_rejected()]] - code - tests/test_role_secondary.py
- [[test_interaction_is_not_a_second_family()]] - code - tests/test_role_secondary.py
- [[test_llm_prompt_includes_structured_responsibilities()]] - code - tests/test_role_secondary.py
- [[test_one_phrase_needs_structured_confirmation()]] - code - tests/test_role_secondary.py
- [[test_pure_roles_have_no_secondary_family()]] - code - tests/test_role_secondary.py
- [[test_qualification_only_mention_is_not_a_secondary_family()]] - code - tests/test_role_secondary.py
- [[test_responsibility_evidence_still_marks_a_hybrid()]] - code - tests/test_role_secondary.py
- [[test_role_secondary.py]] - code - tests/test_role_secondary.py
- [[test_secondary_columns_exist_for_sqlite_and_postgres()]] - code - tests/test_role_secondary.py
- [[test_secondary_fields_persist_and_clear_when_the_jd_changes()]] - code - tests/test_role_secondary.py
- [[test_short_text_stays_unknown()]] - code - tests/test_role_secondary.py
- [[test_truncated_posting_has_no_secondary_family()]] - code - tests/test_role_secondary.py

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/classify_role
SORT file.name ASC
```

## Connections to other communities
- 13 edges to [[_COMMUNITY_test_role_classify.py]]
- 10 edges to [[_COMMUNITY_Source]]
- 8 edges to [[_COMMUNITY_role_classify.py]]
- 7 edges to [[_COMMUNITY_test_structured_jd.py]]
- 6 edges to [[_COMMUNITY_upsert_job]]
- 5 edges to [[_COMMUNITY_structured_jd.py]]
- 3 edges to [[_COMMUNITY_test_recruiting_universe.py]]
- 3 edges to [[_COMMUNITY_session_scope]]
- 1 edge to [[_COMMUNITY_test_fit.py]]
- 1 edge to [[_COMMUNITY_LLMClient]]
- 1 edge to [[_COMMUNITY_ingest.py]]
- 1 edge to [[_COMMUNITY_pytest]]
- 1 edge to [[_COMMUNITY_db.py]]

## Top bridge nodes
- [[test_role_secondary.py]] - degree 33, connects to 9 communities
- [[classify_role()]] - degree 37, connects to 6 communities
- [[test_cache_recomputes_only_when_hash_or_version_changes()]] - degree 12, connects to 4 communities
- [[test_secondary_fields_persist_and_clear_when_the_jd_changes()]] - degree 9, connects to 3 communities
- [[test_qualification_only_mention_is_not_a_secondary_family()]] - degree 6, connects to 2 communities