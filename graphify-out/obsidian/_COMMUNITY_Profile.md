---
type: community
cohesion: 0.12
members: 43
---

# Profile

**Cohesion:** 0.12 - loosely connected
**Members:** 43 nodes

## Members
- [[Classify a JD's stance on visa sponsorship without a profile dependency.…]] - rationale - scraper/filters.py
- [[Highest demanded YOE still worth scoring, derived from the candidate.]] - rationale - scraper/filters.py
- [[JDs often list a reachable minimum plus an aspirational 'preferred'.]] - rationale - tests/test_robustness.py
- [[MonkeyPatch]] - code
- [[Profile]] - code - config/profile.py
- [[Reject only when the lowest mandatory experience floor is out of reach.…]] - rationale - scraper/filters.py
- [[Return whether a posting should proceed to scoring.]] - rationale - scraper/filters.py
- [[Single Source of Truth for candidate facts. No LLM invention beyond this.]] - rationale - config/profile.py
- [[Tests for the negative pre-filter.]] - rationale - tests/test_filters.py
- [[_posting()]] - code - tests/test_filters.py
- [[_posting()_1]] - code - tests/test_robustness.py
- [[_yoe_reason()]] - code - scraper/filters.py
- [[evaluate()]] - code - scraper/filters.py
- [[international' must not satisfy the intern word-boundary gate.]] - rationale - tests/test_filters.py
- [[max_acceptable_years()]] - code - scraper/filters.py
- [[sponsorship_signal()]] - code - scraper/filters.py
- [[test_clearance_regex_pattern()]] - code - tests/test_filters.py
- [[test_company_blocklist_does_not_match_lookalikes()]] - code - tests/test_robustness.py
- [[test_exclude_clearance_keyword()]] - code - tests/test_filters.py
- [[test_exclude_high_yoe_requirement()]] - code - tests/test_filters.py
- [[test_exclude_off_target_location()]] - code - tests/test_filters.py
- [[test_exclude_seniority_title()]] - code - tests/test_filters.py
- [[test_exclude_sponsorship_hostile_when_needed()]] - code - tests/test_filters.py
- [[test_exclude_staffing_company()]] - code - tests/test_filters.py
- [[test_filters.py]] - code - tests/test_filters.py
- [[test_internship_only_off_by_default()]] - code - tests/test_filters.py
- [[test_internship_only_passes_intern_title()]] - code - tests/test_filters.py
- [[test_internship_only_rejects_fulltime()]] - code - tests/test_filters.py
- [[test_internship_only_rejects_international_substring()]] - code - tests/test_filters.py
- [[test_missing_or_weak_evidence_does_not_filter()]] - code - tests/test_false_negative.py
- [[test_pass_mid_level_pm()]] - code - tests/test_filters.py
- [[test_pass_remote_role()]] - code - tests/test_filters.py
- [[test_sponsorship_and_false_friends()]] - code - tests/test_eligibility.py
- [[test_sponsorship_signal_friendly_explicit()]] - code - tests/test_filters.py
- [[test_sponsorship_signal_friendly_opt_cpt()]] - code - tests/test_filters.py
- [[test_sponsorship_signal_hostile_beats_friendly()]] - code - tests/test_filters.py
- [[test_sponsorship_signal_hostile_citizenship_required()]] - code - tests/test_filters.py
- [[test_sponsorship_signal_hostile_no_sponsorship()]] - code - tests/test_filters.py
- [[test_sponsorship_signal_sponsor_events_is_not_friendly()]] - code - tests/test_filters.py
- [[test_sponsorship_signal_unknown_no_mention()]] - code - tests/test_filters.py
- [[test_yoe_ceiling_follows_profile()]] - code - tests/test_robustness.py
- [[test_yoe_counts_only_a_mandatory_minimum()]] - code - tests/test_filters.py
- [[test_yoe_keeps_job_when_a_lower_band_is_reachable()]] - code - tests/test_robustness.py

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/Profile
SORT file.name ASC
```

## Connections to other communities
- 42 edges to [[_COMMUNITY_test_vector_recovery.py]]
- 29 edges to [[_COMMUNITY_filters.py]]
- 23 edges to [[_COMMUNITY_test_career_intelligence.py]]
- 23 edges to [[_COMMUNITY_test_fit.py]]
- 19 edges to [[_COMMUNITY_test_phase0_baseline.py]]
- 18 edges to [[_COMMUNITY_test_eligibility.py]]
- 15 edges to [[_COMMUNITY_eligibility.py]]
- 15 edges to [[_COMMUNITY_calculate_priority]]
- 13 edges to [[_COMMUNITY_get_settings]]
- 13 edges to [[_COMMUNITY_test_scorer.py]]
- 13 edges to [[_COMMUNITY_Tier]]
- 13 edges to [[_COMMUNITY_Source]]
- 12 edges to [[_COMMUNITY_profile.py]]
- 11 edges to [[_COMMUNITY_prerank.py]]
- 11 edges to [[_COMMUNITY_test_priority.py]]
- 9 edges to [[_COMMUNITY_re]]
- 8 edges to [[_COMMUNITY_test_resume.py]]
- 8 edges to [[_COMMUNITY_diff.py]]
- 8 edges to [[_COMMUNITY_scorerengine.py]]
- 8 edges to [[_COMMUNITY_LLMClient]]
- 7 edges to [[_COMMUNITY_upsert_job]]
- 6 edges to [[_COMMUNITY_suggest.py]]
- 5 edges to [[_COMMUNITY_linkedin_jobspy.py]]
- 4 edges to [[_COMMUNITY_benchmarkengine.py]]
- 4 edges to [[_COMMUNITY_baseline.py]]
- 4 edges to [[_COMMUNITY_priority.py]]
- 4 edges to [[_COMMUNITY_discovery_recall.py]]
- 3 edges to [[_COMMUNITY_runner.py]]
- 3 edges to [[_COMMUNITY_builder.py]]
- 3 edges to [[_COMMUNITY_test_cover_letter.py]]
- 2 edges to [[_COMMUNITY_json]]
- 2 edges to [[_COMMUNITY_ingest.py]]
- 2 edges to [[_COMMUNITY_session_scope]]
- 2 edges to [[_COMMUNITY_test_recruiting_universe.py]]
- 1 edge to [[_COMMUNITY_workday.py]]
- 1 edge to [[_COMMUNITY_Job]]
- 1 edge to [[_COMMUNITY_targets.py]]
- 1 edge to [[_COMMUNITY_pathlib]]
- 1 edge to [[_COMMUNITY_dot-total_years_experience]]
- 1 edge to [[_COMMUNITY_5. How fit is scored]]
- 1 edge to [[_COMMUNITY_Phase 9 visa and eligibility]]
- 1 edge to [[_COMMUNITY_send_prep_pack]]
- 1 edge to [[_COMMUNITY_3. Hard filters (before any model)]]
- 1 edge to [[_COMMUNITY_9. Pain points we have actually hit or spelled out]]
- 1 edge to [[_COMMUNITY_ScoreOnlyClient]]
- 1 edge to [[_COMMUNITY_pytest]]
- 1 edge to [[_COMMUNITY_db.py]]

## Top bridge nodes
- [[Profile]] - degree 331, connects to 41 communities
- [[evaluate()]] - degree 54, connects to 11 communities
- [[test_filters.py]] - degree 35, connects to 6 communities
- [[max_acceptable_years()]] - degree 16, connects to 5 communities
- [[sponsorship_signal()]] - degree 16, connects to 3 communities