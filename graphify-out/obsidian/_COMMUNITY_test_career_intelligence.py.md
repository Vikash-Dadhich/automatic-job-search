---
type: community
cohesion: 0.08
members: 67
---

# test_career_intelligence.py

**Cohesion:** 0.08 - loosely connected
**Members:** 67 nodes

## Members
- [[dot-evidence_document()]] - code - scorer/career_intelligence.py
- [[Any_41]] - code
- [[Career Intelligence is a separate reading. It does not change fit or shortlist.]] - rationale - tests/test_career_intelligence.py
- [[Career-opportunity reading for one job. This is not a fit score. Unknown…]] - rationale - scorer/career_intelligence.py
- [[CareerIntelligence]] - code - core/db.py
- [[CareerReading]] - code - scorer/career_intelligence.py
- [[Deterministic career reading. Does not call a model or read fit.]] - rationale - scorer/career_intelligence.py
- [[Identity of this reading. The raw profile is not included.]] - rationale - scorer/career_intelligence.py
- [[Match_3]] - code
- [[MonkeyPatch_21]] - code
- [[One current career-opportunity reading for a job. Not a fit score.]] - rationale - core/db.py
- [[Path_40]] - code
- [[Pattern_1]] - code
- [[Store one current reading. Does not write fit, priority, status, or shortlist.]] - rationale - scorer/career_intelligence.py
- [[_Dimension]] - code - scorer/career_intelligence.py
- [[_apply_reading()]] - code - scorer/career_intelligence.py
- [[_boom()_4]] - code - tests/test_career_intelligence.py
- [[_boom()_5]] - code - tests/test_career_intelligence.py
- [[_clause()]] - code - scorer/career_intelligence.py
- [[_clip()_2]] - code - scorer/career_intelligence.py
- [[_company_signals()_1]] - code - scorer/career_intelligence.py
- [[_competitiveness()]] - code - scorer/career_intelligence.py
- [[_doc()_1]] - code - tests/test_career_intelligence.py
- [[_dump()]] - code - scorer/career_intelligence.py
- [[_effort()]] - code - scorer/career_intelligence.py
- [[_internship()_1]] - code - scorer/career_intelligence.py
- [[_job()_11]] - code - tests/test_career_intelligence.py
- [[_match_groups()]] - code - scorer/career_intelligence.py
- [[_mba_signal()]] - code - scorer/career_intelligence.py
- [[_overall()_1]] - code - scorer/career_intelligence.py
- [[_read()_2]] - code - tests/test_career_intelligence.py
- [[_require_int()_6]] - code - scorer/career_intelligence.py
- [[_save()]] - code - tests/test_career_intelligence.py
- [[_signal_in_text()]] - code - scorer/career_intelligence.py
- [[_signal_score()]] - code - scorer/career_intelligence.py
- [[_state_for_count()]] - code - scorer/career_intelligence.py
- [[_story()]] - code - scorer/career_intelligence.py
- [[_texts()]] - code - scorer/career_intelligence.py
- [[_themes()]] - code - scorer/career_intelligence.py
- [[_transition()]] - code - scorer/career_intelligence.py
- [[_usable()]] - code - scorer/career_intelligence.py
- [[_validate()_7]] - code - scorer/career_intelligence.py
- [[assess_career()]] - code - scorer/career_intelligence.py
- [[attach_career_intelligence()]] - code - scorer/career_intelligence.py
- [[career_input_hash()]] - code - scorer/career_intelligence.py
- [[career_intelligence.py]] - code - scorer/career_intelligence.py
- [[config_hash()_2]] - code - scorer/career_intelligence.py
- [[get_career_intelligence()]] - code - scorer/career_intelligence.py
- [[load_career_config()]] - code - scorer/career_intelligence.py
- [[parametrize_3]] - code
- [[test_application_effort_is_stored_and_not_an_overall_penalty()]] - code - tests/test_career_intelligence.py
- [[test_assess_does_not_call_the_fit_model()]] - code - tests/test_career_intelligence.py
- [[test_cache_reuses_and_invalidates()]] - code - tests/test_career_intelligence.py
- [[test_career_intelligence.py]] - code - tests/test_career_intelligence.py
- [[test_career_reading_does_not_change_telegram_order()]] - code - tests/test_career_intelligence.py
- [[test_competitiveness_does_not_treat_unknown_or_title_as_failure()]] - code - tests/test_career_intelligence.py
- [[test_conversion_requires_explicit_language()]] - code - tests/test_career_intelligence.py
- [[test_failure_does_not_change_fit_priority_or_shortlist()]] - code - tests/test_career_intelligence.py
- [[test_learning_and_quality_ignore_prestige()]] - code - tests/test_career_intelligence.py
- [[test_mba_internship_is_recognized_without_inventing_quality()]] - code - tests/test_career_intelligence.py
- [[test_overall_score_omits_unknown_dimensions()]] - code - tests/test_career_intelligence.py
- [[test_product_and_strategy_and_consulting_are_positive()]] - code - tests/test_career_intelligence.py
- [[test_record_is_versioned_and_unique()]] - code - tests/test_career_intelligence.py
- [[test_role_and_company_inputs_change_the_hash()]] - code - tests/test_career_intelligence.py
- [[test_secondary_role_fields_change_the_input_hash()]] - code - tests/test_career_intelligence.py
- [[test_technology_bridge_needs_posting_evidence()]] - code - tests/test_career_intelligence.py
- [[test_unrelated_work_is_not_given_transition_credit()]] - code - tests/test_career_intelligence.py

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/test_career_intelligencepy
SORT file.name ASC
```

## Connections to other communities
- 23 edges to [[_COMMUNITY_Profile]]
- 19 edges to [[_COMMUNITY_session_scope]]
- 9 edges to [[_COMMUNITY_Job]]
- 6 edges to [[_COMMUNITY_pathlib]]
- 5 edges to [[_COMMUNITY_json]]
- 4 edges to [[_COMMUNITY_company_intelligence.py]]
- 4 edges to [[_COMMUNITY_test_vector_recovery.py]]
- 3 edges to [[_COMMUNITY_db.py]]
- 3 edges to [[_COMMUNITY_Source]]
- 3 edges to [[_COMMUNITY_test_phase13_shortlist.py]]
- 2 edges to [[_COMMUNITY_TelegramClient]]
- 2 edges to [[_COMMUNITY_test_structured_jd.py]]
- 2 edges to [[_COMMUNITY_upsert_job]]
- 2 edges to [[_COMMUNITY_scorerengine.py]]
- 2 edges to [[_COMMUNITY_send_prep_pack]]
- 2 edges to [[_COMMUNITY_pytest]]
- 2 edges to [[_COMMUNITY_typing]]
- 2 edges to [[_COMMUNITY_test_monitoring.py]]
- 2 edges to [[_COMMUNITY_profile.py]]
- 1 edge to [[_COMMUNITY_AsyncSession]]
- 1 edge to [[_COMMUNITY_get_settings]]
- 1 edge to [[_COMMUNITY_LLMClient]]
- 1 edge to [[_COMMUNITY_structured_jd.py]]
- 1 edge to [[_COMMUNITY_re]]
- 1 edge to [[_COMMUNITY_test_resume.py]]
- 1 edge to [[_COMMUNITY_baseline.py]]
- 1 edge to [[_COMMUNITY_targets.py]]
- 1 edge to [[_COMMUNITY_test_scorer.py]]

## Top bridge nodes
- [[test_career_intelligence.py]] - degree 54, connects to 19 communities
- [[career_intelligence.py]] - degree 52, connects to 17 communities
- [[attach_career_intelligence()]] - degree 18, connects to 7 communities
- [[test_failure_does_not_change_fit_priority_or_shortlist()]] - degree 15, connects to 6 communities
- [[test_career_reading_does_not_change_telegram_order()]] - degree 13, connects to 5 communities