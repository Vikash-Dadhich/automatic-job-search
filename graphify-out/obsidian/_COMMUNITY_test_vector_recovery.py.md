---
type: community
cohesion: 0.09
members: 84
---

# test_vector_recovery.py

**Cohesion:** 0.09 - loosely connected
**Members:** 84 nodes

## Members
- [[dot-__init__()_26]] - code - tests/test_vector_gate.py
- [[dot-complete()_12]] - code - tests/test_scorer.py
- [[dot-embed()]] - code - tests/test_vector_gate.py
- [[Any_38]] - code
- [[Any_39]] - code
- [[Decide whether a vector-gate reject may enter the normal scorer. This does not…]] - rationale - scorer/vector_recovery.py
- [[Deterministic LLM stand-in for offline tests.]] - rationale - tests/test_scorer.py
- [[FakeClient_3]] - code - tests/test_scorer.py
- [[FakeEmbedder]] - code - tests/test_vector_gate.py
- [[Head of the cacheable candidate block. Same cap as a job description.]] - rationale - scorer/embeddings.py
- [[Identity of the recovery rule and the inputs it reads.]] - rationale - scorer/vector_recovery.py
- [[Module-level entry point used by README  Step 7.]] - rationale - scorer/engine.py
- [[MonkeyPatch_19]] - code
- [[MonkeyPatch_20]] - code
- [[Offline tests for the embedding gate in front of the LLM scorer.]] - rationale - tests/test_vector_gate.py
- [[Pattern]] - code
- [[Return whether this vector reject may be scored. Never raises for job data.]] - rationale - scorer/vector_recovery.py
- [[ScoreSummary]] - code - scorer/engine.py
- [[Vector-gate rejects return to scoring only with independent role evidence.]] - rationale - tests/test_vector_recovery.py
- [[_assert_no_profile_text()]] - code - tests/test_vector_recovery.py
- [[_bare_job()]] - code - tests/test_vector_recovery.py
- [[_boom()_3]] - code - tests/test_vector_recovery.py
- [[_compiled()]] - code - scorer/vector_recovery.py
- [[_confidence()]] - code - scorer/vector_recovery.py
- [[_doc()]] - code - tests/test_vector_recovery.py
- [[_enable()_1]] - code - tests/test_vector_gate.py
- [[_exclude_company()]] - code - tests/test_vector_recovery.py
- [[_family_group()]] - code - scorer/vector_recovery.py
- [[_map()]] - code - tests/test_vector_gate.py
- [[_mba_program()]] - code - scorer/vector_recovery.py
- [[_names()]] - code - scorer/vector_recovery.py
- [[_phrases()]] - code - scorer/vector_recovery.py
- [[_reason()]] - code - scorer/vector_recovery.py
- [[_require_int()_4]] - code - scorer/vector_recovery.py
- [[_responsibility_group()]] - code - scorer/vector_recovery.py
- [[_score()]] - code - tests/test_vector_recovery.py
- [[_seed()_1]] - code - tests/test_vector_gate.py
- [[_stamp()]] - code - tests/test_vector_recovery.py
- [[_store_doc()]] - code - tests/test_vector_recovery.py
- [[_validate()_5]] - code - scorer/vector_recovery.py
- [[config_hash()_1]] - code - scorer/vector_recovery.py
- [[evaluate_recovery()]] - code - scorer/vector_recovery.py
- [[load_recovery_config()]] - code - scorer/vector_recovery.py
- [[profile_embed_text()]] - code - scorer/embeddings.py
- [[profile_hash()_1]] - code - scorer/embeddings.py
- [[recovery_input_hash()]] - code - scorer/vector_recovery.py
- [[score_pending()]] - code - scorer/engine.py
- [[test_budget_skips_tail_after_a_reject()]] - code - tests/test_vector_gate.py
- [[test_build_embedder_without_key_returns_none()]] - code - tests/test_vector_gate.py
- [[test_cached_embedding_skips_job_text()]] - code - tests/test_vector_gate.py
- [[test_clearance_is_not_embedded()]] - code - tests/test_vector_gate.py
- [[test_clearly_ineligible_cannot_be_recovered()]] - code - tests/test_vector_recovery.py
- [[test_config_change_reopens_a_stored_reject()]] - code - tests/test_vector_recovery.py
- [[test_dream_company_bypasses_low_cosine()]] - code - tests/test_vector_gate.py
- [[test_embedder_failure_scores_anyway()]] - code - tests/test_vector_gate.py
- [[test_embedder_failure_still_fails_open()]] - code - tests/test_vector_recovery.py
- [[test_gate_disabled_does_not_embed()]] - code - tests/test_vector_gate.py
- [[test_gate_rejects_orthogonal_and_scores_match()]] - code - tests/test_vector_gate.py
- [[test_hard_filter_cannot_be_recovered()]] - code - tests/test_vector_recovery.py
- [[test_irrelevant_reject_stays_rejected()]] - code - tests/test_vector_recovery.py
- [[test_mba_wording_alone_does_not_recover()]] - code - tests/test_vector_recovery.py
- [[test_profile_change_changes_the_recovery_hash()]] - code - tests/test_vector_recovery.py
- [[test_profile_change_reconsiders_a_reject_that_now_fails_the_hard_filter()]] - code - tests/test_vector_recovery.py
- [[test_profile_change_reuses_jd_vector()]] - code - tests/test_vector_gate.py
- [[test_profile_change_that_passes_the_hard_filter_can_recover()]] - code - tests/test_vector_recovery.py
- [[test_qualification_only_does_not_recover()]] - code - tests/test_vector_recovery.py
- [[test_recovery_does_not_change_priority_or_portfolio()]] - code - tests/test_vector_recovery.py
- [[test_recovery_failure_keeps_the_vector_reject()]] - code - tests/test_vector_recovery.py
- [[test_recovery_is_deterministic()]] - code - tests/test_vector_recovery.py
- [[test_reopen_stays_closed_when_still_below()]] - code - tests/test_vector_gate.py
- [[test_reopen_when_threshold_drops()]] - code - tests/test_vector_gate.py
- [[test_repeated_scoring_is_stable()]] - code - tests/test_vector_recovery.py
- [[test_secondary_and_responsibility_evidence_recovers()]] - code - tests/test_vector_recovery.py
- [[test_short_text_fails_open_without_embed()]] - code - tests/test_vector_gate.py
- [[test_stale_recovery_hash_is_reopened()]] - code - tests/test_vector_recovery.py
- [[test_strong_target_role_is_recovered()]] - code - tests/test_vector_recovery.py
- [[test_threshold_is_inclusive()]] - code - tests/test_vector_gate.py
- [[test_unchanged_profile_keeps_a_cached_reject()]] - code - tests/test_vector_recovery.py
- [[test_unchanged_profile_keeps_the_same_recovery_hash()]] - code - tests/test_vector_recovery.py
- [[test_vector_accept_still_scores()]] - code - tests/test_vector_recovery.py
- [[test_vector_gate.py]] - code - tests/test_vector_gate.py
- [[test_vector_recovery.py]] - code - tests/test_vector_recovery.py
- [[test_weak_keyword_does_not_recover()]] - code - tests/test_vector_recovery.py
- [[vector_recovery.py]] - code - scorer/vector_recovery.py

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/test_vector_recoverypy
SORT file.name ASC
```

## Connections to other communities
- 67 edges to [[_COMMUNITY_session_scope]]
- 42 edges to [[_COMMUNITY_Profile]]
- 31 edges to [[_COMMUNITY_scorerengine.py]]
- 17 edges to [[_COMMUNITY_Job]]
- 11 edges to [[_COMMUNITY_upsert_job]]
- 10 edges to [[_COMMUNITY_json]]
- 9 edges to [[_COMMUNITY_get_settings]]
- 5 edges to [[_COMMUNITY_test_scorer.py]]
- 5 edges to [[_COMMUNITY_Source]]
- 5 edges to [[_COMMUNITY_pytest]]
- 4 edges to [[_COMMUNITY_LLMClient]]
- 4 edges to [[_COMMUNITY_test_career_intelligence.py]]
- 3 edges to [[_COMMUNITY_filters.py]]
- 3 edges to [[_COMMUNITY_db.py]]
- 3 edges to [[_COMMUNITY_typing]]
- 3 edges to [[_COMMUNITY_profile.py]]
- 2 edges to [[_COMMUNITY_TokenUsage]]
- 2 edges to [[_COMMUNITY_test_structured_jd.py]]
- 2 edges to [[_COMMUNITY_scorer__init__.py]]
- 2 edges to [[_COMMUNITY_Tier]]
- 2 edges to [[_COMMUNITY_re]]
- 1 edge to [[_COMMUNITY_test_cover_letter.py]]
- 1 edge to [[_COMMUNITY_pipeline.py]]
- 1 edge to [[_COMMUNITY_test_resume.py]]
- 1 edge to [[_COMMUNITY_targets.py]]
- 1 edge to [[_COMMUNITY_pathlib]]

## Top bridge nodes
- [[test_vector_gate.py]] - degree 45, connects to 13 communities
- [[vector_recovery.py]] - degree 34, connects to 13 communities
- [[test_vector_recovery.py]] - degree 58, connects to 12 communities
- [[score_pending()]] - degree 38, connects to 10 communities
- [[FakeClient_3]] - degree 30, connects to 7 communities