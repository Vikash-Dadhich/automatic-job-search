---
type: community
cohesion: 0.15
members: 27
---

# calculate_priority

**Cohesion:** 0.15 - loosely connected
**Members:** 27 nodes

## Members
- [[Cache and storage]] - document - docs/phase9-visa-eligibility.md
- [[Four different questions]] - document - docs/phase7-role-family-weighting.md
- [[MonkeyPatch_2]] - code
- [[Priority 2.0 attention order. Fit, eligibility, and portfolio stay separate.]] - rationale - tests/test_priority_v2.py
- [[Rank one stored job. Does not write the row and does not change fit.]] - rationale - scorer/priority.py
- [[__init__()_1]] - code - tests/test_priority_v2.py
- [[_boom()]] - code - tests/test_priority_v2.py
- [[_combine()]] - code - scorer/priority.py
- [[_job()]] - code - tests/test_priority_v2.py
- [[_reasons()]] - code - scorer/priority.py
- [[_signal()]] - code - tests/test_priority_v2.py
- [[calculate_priority()]] - code - scorer/priority.py
- [[score()]] - code - tests/test_priority_v2.py
- [[test_confidence_and_structured_evidence()]] - code - tests/test_priority_v2.py
- [[test_domains_are_capped_and_irrelevant_domains_add_nothing()]] - code - tests/test_priority_v2.py
- [[test_eligibility_order_and_unknown()]] - code - tests/test_priority_v2.py
- [[test_missing_jd_is_omitted_and_truncated_stays_lower()]] - code - tests/test_priority_v2.py
- [[test_priority_does_not_call_a_model()]] - code - tests/test_priority_v2.py
- [[test_priority_is_deterministic_and_bounded()]] - code - tests/test_priority.py
- [[test_priority_stays_bounded_and_fit_is_only_an_input()]] - code - tests/test_priority_v2.py
- [[test_priority_v2.py]] - code - tests/test_priority_v2.py
- [[test_program_evidence_is_capped_and_not_mba_by_default()]] - code - tests/test_priority_v2.py
- [[test_role_alignment_and_bounded_secondary()]] - code - tests/test_priority_v2.py
- [[test_role_evidence_changes_the_priority_hash()]] - code - tests/test_priority_v2.py
- [[test_secondary_role_must_be_a_different_target_family()]] - code - tests/test_priority_v2.py
- [[test_submitted_is_not_treated_as_untouched()]] - code - tests/test_priority.py
- [[test_us_presence_does_not_change_eligibility()]] - code - tests/test_priority_v2.py

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/calculate_priority
SORT file.name ASC
```

## Connections to other communities
- 15 edges to [[_COMMUNITY_Profile]]
- 15 edges to [[_COMMUNITY_test_priority.py]]
- 9 edges to [[_COMMUNITY_priority.py]]
- 4 edges to [[_COMMUNITY_session_scope]]
- 4 edges to [[_COMMUNITY_Job]]
- 2 edges to [[_COMMUNITY_Source]]
- 2 edges to [[_COMMUNITY_db.py]]
- 1 edge to [[_COMMUNITY_scorerengine.py]]
- 1 edge to [[_COMMUNITY_Phase 6 candidate fit]]
- 1 edge to [[_COMMUNITY_pytest]]
- 1 edge to [[_COMMUNITY_profile.py]]
- 1 edge to [[_COMMUNITY_baseline.py]]
- 1 edge to [[_COMMUNITY_Phase 7 role-family weighting]]
- 1 edge to [[_COMMUNITY_Phase 9 visa and eligibility]]

## Top bridge nodes
- [[test_priority_v2.py]] - degree 26, connects to 10 communities
- [[calculate_priority()]] - degree 35, connects to 4 communities
- [[_job()]] - degree 16, connects to 3 communities
- [[score()]] - degree 8, connects to 3 communities
- [[test_submitted_is_not_treated_as_untouched()]] - degree 5, connects to 3 communities