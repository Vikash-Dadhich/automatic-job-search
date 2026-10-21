---
type: community
cohesion: 0.11
members: 37
---

# pytest

**Cohesion:** 0.11 - loosely connected
**Members:** 37 nodes

## Members
- [[Any_10]] - code
- [[Load the portfolio weights. Raises if the file does not match Phase 5 families.]] - rationale - scorer/role_weights.py
- [[Path_5]] - code
- [[Path_6]] - code
- [[Phase 7 portfolio weights. They do not change fit, tier, status, or search…]] - rationale - tests/test_role_weights.py
- [[Portfolio weight for a Phase 5 primary family. Missing or unknown names use…]] - rationale - scorer/role_weights.py
- [[Strategic weight of a classified role family. Not fit and not search capacity.]] - rationale - scorer/role_weights.py
- [[Subfamilies use their primary family's weight. They do not have their own.]] - rationale - scorer/role_weights.py
- [[_job()_1]] - code - tests/test_role_weights.py
- [[_load_yaml()]] - code - config/profile.py
- [[_posting()_3]] - code - tests/test_role_weights.py
- [[_validate()_1]] - code - scorer/role_weights.py
- [[_write_weights()]] - code - tests/test_role_weights.py
- [[get_role_family_weight()]] - code - scorer/role_weights.py
- [[load_role_family_weights()]] - code - scorer/role_weights.py
- [[parametrize]] - code
- [[pytest]] - concept
- [[role_weights.py]] - code - scorer/role_weights.py
- [[test_company_and_vector_are_not_weight_inputs()]] - code - tests/test_role_weights.py
- [[test_cosine_identical_and_orthogonal()]] - code - tests/test_vector_gate.py
- [[test_discovery_capacity_stays_independent()]] - code - tests/test_role_weights.py
- [[test_discovery_labels_do_not_choose_the_weight()]] - code - tests/test_role_weights.py
- [[test_every_phase5_primary_family_has_a_weight()]] - code - tests/test_role_weights.py
- [[test_feedback_config_keeps_priority_integration_off()]] - code - tests/test_feedback.py
- [[test_malformed_weight_is_rejected()]] - code - tests/test_role_weights.py
- [[test_missing_or_extra_family_is_rejected()]] - code - tests/test_role_weights.py
- [[test_missing_role_family_uses_unknown_weight()]] - code - tests/test_role_weights.py
- [[test_prerank_ignores_role_family_weight()]] - code - tests/test_role_weights.py
- [[test_primary_family_weights()]] - code - tests/test_role_weights.py
- [[test_provenance_and_company_do_not_change_weight()]] - code - tests/test_role_weights.py
- [[test_role_weights.py]] - code - tests/test_role_weights.py
- [[test_same_fit_keeps_separate_portfolio_weights()]] - code - tests/test_role_weights.py
- [[test_seven_weights_are_not_required_to_sum_to_100()]] - code - tests/test_role_weights.py
- [[test_subfamilies_inherit_the_primary_family_weight()]] - code - tests/test_role_weights.py
- [[test_unrecognized_role_family_uses_unknown_weight()]] - code - tests/test_role_weights.py
- [[weight_for_subfamily()]] - code - scorer/role_weights.py
- [[yaml]] - concept

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/pytest
SORT file.name ASC
```

## Connections to other communities
- 11 edges to [[_COMMUNITY_Tier]]
- 9 edges to [[_COMMUNITY_Source]]
- 8 edges to [[_COMMUNITY_session_scope]]
- 8 edges to [[_COMMUNITY_test_discovery.py]]
- 7 edges to [[_COMMUNITY_targets.py]]
- 6 edges to [[_COMMUNITY_test_application_portfolio.py]]
- 5 edges to [[_COMMUNITY_test_vector_recovery.py]]
- 5 edges to [[_COMMUNITY_pathlib]]
- 4 edges to [[_COMMUNITY_upsert_job]]
- 4 edges to [[_COMMUNITY_test_company_intelligence.py]]
- 4 edges to [[_COMMUNITY_test_feedback.py]]
- 4 edges to [[_COMMUNITY_priority.py]]
- 4 edges to [[_COMMUNITY_discovery_recall.py]]
- 4 edges to [[_COMMUNITY_scheduler.py]]
- 4 edges to [[_COMMUNITY_clients.py]]
- 4 edges to [[_COMMUNITY_vault.py]]
- 3 edges to [[_COMMUNITY_Job]]
- 3 edges to [[_COMMUNITY_suggest.py]]
- 3 edges to [[_COMMUNITY_profile.py]]
- 3 edges to [[_COMMUNITY_test_priority.py]]
- 3 edges to [[_COMMUNITY_test_recruiting_universe.py]]
- 3 edges to [[_COMMUNITY_prerank.py]]
- 3 edges to [[_COMMUNITY_test_phase13_shortlist.py]]
- 3 edges to [[_COMMUNITY_test_llm_provider.py]]
- 2 edges to [[_COMMUNITY_calibration.py]]
- 2 edges to [[_COMMUNITY_test_calibration.py]]
- 2 edges to [[_COMMUNITY_linkedin_people.py]]
- 2 edges to [[_COMMUNITY_db.py]]
- 2 edges to [[_COMMUNITY_scorerengine.py]]
- 2 edges to [[_COMMUNITY_get_settings]]
- 2 edges to [[_COMMUNITY_skills.py]]
- 2 edges to [[_COMMUNITY_role_classify.py]]
- 2 edges to [[_COMMUNITY_typing]]
- 2 edges to [[_COMMUNITY_test_monitoring.py]]
- 2 edges to [[_COMMUNITY_test_career_intelligence.py]]
- 1 edge to [[_COMMUNITY_Phase 7 role-family weighting]]
- 1 edge to [[_COMMUNITY_Profile]]
- 1 edge to [[_COMMUNITY_asyncio]]
- 1 edge to [[_COMMUNITY_calculate_priority]]
- 1 edge to [[_COMMUNITY_conftest.py]]
- 1 edge to [[_COMMUNITY_test_workday_locators.py]]
- 1 edge to [[_COMMUNITY_test_resume.py]]
- 1 edge to [[_COMMUNITY_test_structured_jd.py]]
- 1 edge to [[_COMMUNITY_classify_role]]
- 1 edge to [[_COMMUNITY_diff.py]]
- 1 edge to [[_COMMUNITY_test_pacing.py]]
- 1 edge to [[_COMMUNITY_test_pipeline_order_and_aggregation]]
- 1 edge to [[_COMMUNITY_test_eligibility.py]]
- 1 edge to [[_COMMUNITY_test_phase0_baseline.py]]
- 1 edge to [[_COMMUNITY_test_application_deadline.py]]
- 1 edge to [[_COMMUNITY_json]]
- 1 edge to [[_COMMUNITY_workday.py]]
- 1 edge to [[_COMMUNITY_test_company_intelligence_v2.py]]
- 1 edge to [[_COMMUNITY_baseline.py]]
- 1 edge to [[_COMMUNITY_send_prep_pack]]
- 1 edge to [[_COMMUNITY_feedback.py]]
- 1 edge to [[_COMMUNITY_test_role_classify.py]]
- 1 edge to [[_COMMUNITY_WorkdaySubmitter]]
- 1 edge to [[_COMMUNITY_test_application_tracker.py]]

## Top bridge nodes
- [[pytest]] - degree 70, connects to 44 communities
- [[yaml]] - degree 28, connects to 15 communities
- [[test_role_weights.py]] - degree 45, connects to 12 communities
- [[get_role_family_weight()]] - degree 29, connects to 10 communities
- [[role_weights.py]] - degree 16, connects to 9 communities