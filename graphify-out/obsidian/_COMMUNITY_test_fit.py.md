---
type: community
cohesion: 0.11
members: 47
---

# test_fit.py

**Cohesion:** 0.11 - loosely connected
**Members:** 47 nodes

## Members
- [[dot-__init__()_30]] - code - tests/test_fit.py
- [[dot-complete()_16]] - code - tests/test_fit.py
- [[Any_44]] - code
- [[BaseModel_8]] - code
- [[Candidate facts used for fit. Contact details and visa status stay out.]] - rationale - scorer/fit.py
- [[Candidate-to-JD fit. Mocked model, no network.]] - rationale - tests/test_fit.py
- [[Candidate-to-JD fit. This is not a rank, a visa decision, or a discovery label.]] - rationale - scorer/fit.py
- [[Drop lines that name a specific fact absent from the profile and the JD.]] - rationale - scorer/fit.py
- [[Fit one job. Short or missing descriptions do not call the model.]] - rationale - scorer/fit.py
- [[FitDecision]] - code - scorer/fit.py
- [[Hash of the fit candidate block. Contact and visa edits do not change it.]] - rationale - scorer/fit.py
- [[Job text plus role classification. Discovery query is omitted on purpose.]] - rationale - scorer/fit.py
- [[Parse a fit payload. None means the output is not usable.]] - rationale - scorer/fit.py
- [[Path_48]] - code
- [[_Client]] - code - tests/test_fit.py
- [[_Dimension_1]] - code - scorer/fit.py
- [[_FitPayload]] - code - scorer/fit.py
- [[_dims()]] - code - tests/test_fit.py
- [[_ground()]] - code - scorer/fit.py
- [[_insufficient()]] - code - scorer/fit.py
- [[_job()_14]] - code - tests/test_fit.py
- [[_legacy()_1]] - code - scorer/fit.py
- [[_lines()]] - code - scorer/fit.py
- [[_payload()]] - code - tests/test_fit.py
- [[_unavailable()]] - code - scorer/fit.py
- [[build_fit_system_blocks()]] - code - scorer/fit.py
- [[build_fit_user()]] - code - scorer/fit.py
- [[cached_fit()]] - code - scorer/fit.py
- [[evaluate_fit()]] - code - scorer/fit.py
- [[fit.py]] - code - scorer/fit.py
- [[fit_context_block()]] - code - scorer/fit.py
- [[fit_is_current()]] - code - scorer/fit.py
- [[parse_fit()]] - code - scorer/fit.py
- [[profile_fit_hash()]] - code - scorer/fit.py
- [[test_company_and_vector_do_not_change_fit_score()]] - code - tests/test_fit.py
- [[test_fit.py]] - code - tests/test_fit.py
- [[test_fit_blocks_include_the_profile()]] - code - tests/test_fit.py
- [[test_fit_cache_tracks_jd_profile_and_version()]] - code - tests/test_fit.py
- [[test_fit_context_keeps_match_facts_and_drops_contact_details()]] - code - tests/test_fit.py
- [[test_fit_hash_tracks_match_facts_only()]] - code - tests/test_fit.py
- [[test_fit_prompt_uses_profile_and_role_not_discovery()]] - code - tests/test_fit.py
- [[test_insufficient_fit_is_not_stored_as_zero()]] - code - tests/test_fit.py
- [[test_invalid_payload_and_invented_skill()]] - code - tests/test_fit.py
- [[test_phase6_v1_fit_is_stale()]] - code - tests/test_fit.py
- [[test_preferred_gap_required_gap_and_conflict()]] - code - tests/test_fit.py
- [[test_short_jd_skips_the_model()]] - code - tests/test_fit.py
- [[test_truncated_jd_does_not_receive_a_fit_score()]] - code - tests/test_fit.py

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/test_fitpy
SORT file.name ASC
```

## Connections to other communities
- 23 edges to [[_COMMUNITY_Profile]]
- 12 edges to [[_COMMUNITY_Job]]
- 7 edges to [[_COMMUNITY_json]]
- 6 edges to [[_COMMUNITY_session_scope]]
- 5 edges to [[_COMMUNITY_LLMClient]]
- 3 edges to [[_COMMUNITY_Source]]
- 3 edges to [[_COMMUNITY_filters.py]]
- 3 edges to [[_COMMUNITY_test_scorer.py]]
- 3 edges to [[_COMMUNITY_re]]
- 2 edges to [[_COMMUNITY_upsert_job]]
- 2 edges to [[_COMMUNITY_skills.py]]
- 2 edges to [[_COMMUNITY_scorerengine.py]]
- 2 edges to [[_COMMUNITY_db.py]]
- 2 edges to [[_COMMUNITY_profile.py]]
- 1 edge to [[_COMMUNITY_classify_role]]
- 1 edge to [[_COMMUNITY_clients.py]]
- 1 edge to [[_COMMUNITY_linkedin_people.py]]
- 1 edge to [[_COMMUNITY_test_resume.py]]
- 1 edge to [[_COMMUNITY_typing]]
- 1 edge to [[_COMMUNITY_pathlib]]

## Top bridge nodes
- [[fit.py]] - degree 34, connects to 14 communities
- [[test_fit.py]] - degree 37, connects to 11 communities
- [[test_insufficient_fit_is_not_stored_as_zero()]] - degree 12, connects to 6 communities
- [[parse_fit()]] - degree 15, connects to 5 communities
- [[evaluate_fit()]] - degree 22, connects to 4 communities