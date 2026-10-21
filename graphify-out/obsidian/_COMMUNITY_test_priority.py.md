---
type: community
cohesion: 0.17
members: 23
---

# test_priority.py

**Cohesion:** 0.17 - loosely connected
**Members:** 23 nodes

## Members
- [[Path_39]] - code
- [[Portfolio weight scaled so the top family is 100. Not a fit score.]] - rationale - scorer/priority.py
- [[Priority orders stored jobs. It does not change fit or remove a job.]] - rationale - tests/test_priority.py
- [[PriorityDecision]] - code - scorer/priority.py
- [[Store priority fields. Fit, eligibility, role, and status stay as they are. The…]] - rationale - scorer/priority.py
- [[_job()_9]] - code - tests/test_priority.py
- [[apply_priority()]] - code - scorer/priority.py
- [[load_priority_config()]] - code - scorer/priority.py
- [[priority_is_current()]] - code - scorer/priority.py
- [[role_family_component()]] - code - scorer/priority.py
- [[scaled()]] - code - tests/test_priority.py
- [[test_dream_company_is_only_a_configured_boost()]] - code - tests/test_priority.py
- [[test_eligibility_unknown_is_not_ineligible()]] - code - tests/test_priority.py
- [[test_fit_and_role_family_order_attention()]] - code - tests/test_priority.py
- [[test_freshness_cache_refreshes_on_a_later_utc_day()]] - code - tests/test_priority.py
- [[test_jd_and_freshness_do_not_discard()]] - code - tests/test_priority.py
- [[test_priority.py]] - code - tests/test_priority.py
- [[test_priority_ignores_discovery_and_vector()]] - code - tests/test_priority.py
- [[test_priority_persists_and_reuses_until_inputs_change()]] - code - tests/test_priority.py
- [[test_role_family_scale_is_half_up()]] - code - tests/test_priority.py
- [[test_ties_break_on_fit_then_recency_then_id()]] - code - tests/test_priority.py
- [[test_weights_are_the_documented_allocation()]] - code - tests/test_priority_v2.py
- [[test_weights_sum_to_100()]] - code - tests/test_priority.py

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/test_prioritypy
SORT file.name ASC
```

## Connections to other communities
- 15 edges to [[_COMMUNITY_calculate_priority]]
- 14 edges to [[_COMMUNITY_priority.py]]
- 11 edges to [[_COMMUNITY_Profile]]
- 8 edges to [[_COMMUNITY_session_scope]]
- 5 edges to [[_COMMUNITY_Job]]
- 3 edges to [[_COMMUNITY_pytest]]
- 3 edges to [[_COMMUNITY_upsert_job]]
- 2 edges to [[_COMMUNITY_Source]]
- 2 edges to [[_COMMUNITY_sort_by_priority]]
- 1 edge to [[_COMMUNITY_LLMClient]]
- 1 edge to [[_COMMUNITY_scorerengine.py]]
- 1 edge to [[_COMMUNITY_Priority 2.0]]
- 1 edge to [[_COMMUNITY_db.py]]
- 1 edge to [[_COMMUNITY_baseline.py]]
- 1 edge to [[_COMMUNITY_pathlib]]
- 1 edge to [[_COMMUNITY_profile.py]]

## Top bridge nodes
- [[test_priority.py]] - degree 31, connects to 12 communities
- [[apply_priority()]] - degree 15, connects to 6 communities
- [[_job()_9]] - degree 16, connects to 4 communities
- [[role_family_component()]] - degree 11, connects to 4 communities
- [[priority_is_current()]] - degree 11, connects to 3 communities