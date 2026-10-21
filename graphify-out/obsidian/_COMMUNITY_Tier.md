---
type: community
cohesion: 0.13
members: 24
---

# Tier

**Cohesion:** 0.13 - loosely connected
**Members:** 24 nodes

## Members
- [[A garbage score must error, not silently become 0  Tier 3.]] - rationale - tests/test_robustness.py
- [[Deterministic tier from score + dream-company override (thresholds in settings).]] - rationale - scorer/engine.py
- [[Dream-company match tolerant of legal suffixes ('Google' == 'Google LLC').]] - rationale - scorer/engine.py
- [[Extract compact {s,t,r} JSON from model output (tolerant).]] - rationale - scorer/engine.py
- [[First brace-balanced JSON object, ignoring braces inside string literals.]] - rationale - scorer/engine.py
- [[Regression tests for scoring isolation, profile-aware filters, and re-scoring.]] - rationale - tests/test_robustness.py
- [[Tier]] - code - core/db.py
- [[_extract_json_object()]] - code - scorer/engine.py
- [[compute_tier()]] - code - scorer/engine.py
- [[is_dream_company()]] - code - scorer/engine.py
- [[parse_score()]] - code - scorer/engine.py
- [[test_compute_tier_dream_company()]] - code - tests/test_scorer.py
- [[test_compute_tier_thresholds()]] - code - tests/test_scorer.py
- [[test_dream_company_match_tolerates_suffix()]] - code - tests/test_robustness.py
- [[test_parse_score_clamps()]] - code - tests/test_scorer.py
- [[test_parse_score_code_fenced()]] - code - tests/test_scorer.py
- [[test_parse_score_handles_braces_inside_strings()]] - code - tests/test_robustness.py
- [[test_parse_score_plain_json()]] - code - tests/test_scorer.py
- [[test_parse_score_rejects_non_numeric_score()]] - code - tests/test_robustness.py
- [[test_parse_score_with_prose()]] - code - tests/test_scorer.py
- [[test_rewritten_jd_resets_staged_job_for_rescore()]] - code - tests/test_robustness.py
- [[test_robustness.py]] - code - tests/test_robustness.py
- [[test_tier_function_ignores_role_family_weight()]] - code - tests/test_role_weights.py
- [[test_tier_thresholds_come_from_settings()]] - code - tests/test_robustness.py

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/Tier
SORT file.name ASC
```

## Connections to other communities
- 13 edges to [[_COMMUNITY_Profile]]
- 11 edges to [[_COMMUNITY_session_scope]]
- 11 edges to [[_COMMUNITY_pytest]]
- 9 edges to [[_COMMUNITY_test_company_intelligence.py]]
- 9 edges to [[_COMMUNITY_test_scorer.py]]
- 8 edges to [[_COMMUNITY_scorerengine.py]]
- 6 edges to [[_COMMUNITY_test_doctor.py]]
- 5 edges to [[_COMMUNITY_Job]]
- 5 edges to [[_COMMUNITY_scorer__init__.py]]
- 5 edges to [[_COMMUNITY_LLMClient]]
- 5 edges to [[_COMMUNITY_upsert_job]]
- 4 edges to [[_COMMUNITY_Source]]
- 3 edges to [[_COMMUNITY_profile.py]]
- 3 edges to [[_COMMUNITY_review.py]]
- 3 edges to [[_COMMUNITY_db.py]]
- 3 edges to [[_COMMUNITY_get_settings]]
- 2 edges to [[_COMMUNITY_pipeline.py]]
- 2 edges to [[_COMMUNITY_test_application_portfolio.py]]
- 2 edges to [[_COMMUNITY_handle_callback]]
- 2 edges to [[_COMMUNITY_test_phase13_shortlist.py]]
- 2 edges to [[_COMMUNITY_pathlib]]
- 2 edges to [[_COMMUNITY_test_recruiting_universe.py]]
- 2 edges to [[_COMMUNITY_test_vector_recovery.py]]
- 2 edges to [[_COMMUNITY_priority.py]]
- 2 edges to [[_COMMUNITY_Settings]]
- 2 edges to [[_COMMUNITY_typing]]
- 1 edge to [[_COMMUNITY_ScoreOnlyClient]]
- 1 edge to [[_COMMUNITY_main.py]]
- 1 edge to [[_COMMUNITY_test_cover_letter.py]]
- 1 edge to [[_COMMUNITY_tracker.py]]
- 1 edge to [[_COMMUNITY_discovery_recall.py]]
- 1 edge to [[_COMMUNITY_suggest.py]]
- 1 edge to [[_COMMUNITY_Phase 0 baseline]]
- 1 edge to [[_COMMUNITY_filters.py]]
- 1 edge to [[_COMMUNITY_baseline.py]]

## Top bridge nodes
- [[Tier]] - degree 62, connects to 23 communities
- [[test_robustness.py]] - degree 40, connects to 16 communities
- [[compute_tier()]] - degree 20, connects to 9 communities
- [[is_dream_company()]] - degree 12, connects to 5 communities
- [[parse_score()]] - degree 14, connects to 4 communities