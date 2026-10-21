---
type: community
cohesion: 0.15
members: 28
---

# json

**Cohesion:** 0.15 - loosely connected
**Members:** 28 nodes

## Members
- [[Any_27]] - code
- [[MonkeyPatch_15]] - code
- [[Path_26]] - code
- [[Path_27]] - code
- [[Profile version plus the public config used for this process.]] - rationale - config/diagnostics.py
- [[SHA-256 of ``public_config``. Changes when an effective setting changes.]] - rationale - config/diagnostics.py
- [[SHA-256 of canonical profile facts. The raw profile is not returned.]] - rationale - config/diagnostics.py
- [[SHA-256 of the parsed profile facts. Comments and key order do not matter.]] - rationale - config/diagnostics.py
- [[Secret-free profile and config identity.]] - rationale - tests/test_diagnostics.py
- [[Secret-free snapshot of the candidate profile version and effective config. The…]] - rationale - config/diagnostics.py
- [[Settings that change discovery, scoring, or delivery. No secrets.]] - rationale - config/diagnostics.py
- [[Write the baseline JSON. The file is gitignored runtime output.]] - rationale - config/diagnostics.py
- [[calibration_config_hash()]] - code - scorer/calibration.py
- [[diagnostics.py]] - code - config/diagnostics.py
- [[effective_baseline()]] - code - config/diagnostics.py
- [[effective_config_hash()]] - code - config/diagnostics.py
- [[feedback_config_hash()]] - code - scorer/feedback.py
- [[fingerprint_profile()]] - code - config/diagnostics.py
- [[hashlib]] - concept
- [[json]] - concept
- [[profile_hash()]] - code - config/diagnostics.py
- [[public_config()]] - code - config/diagnostics.py
- [[test_baseline_file_has_no_secrets()]] - code - tests/test_diagnostics.py
- [[test_config_hash_changes_when_internship_only_changes()]] - code - tests/test_diagnostics.py
- [[test_diagnostics.py]] - code - tests/test_diagnostics.py
- [[test_effective_baseline_matches_public_fields()]] - code - tests/test_diagnostics.py
- [[test_profile_hash_is_stable()]] - code - tests/test_diagnostics.py
- [[write_effective_baseline()]] - code - config/diagnostics.py

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/json
SORT file.name ASC
```

## Connections to other communities
- 10 edges to [[_COMMUNITY_test_vector_recovery.py]]
- 7 edges to [[_COMMUNITY_test_fit.py]]
- 6 edges to [[_COMMUNITY_calibration.py]]
- 6 edges to [[_COMMUNITY_get_settings]]
- 5 edges to [[_COMMUNITY_pipeline.py]]
- 5 edges to [[_COMMUNITY_test_monitoring.py]]
- 5 edges to [[_COMMUNITY_test_career_intelligence.py]]
- 5 edges to [[_COMMUNITY_feedback.py]]
- 5 edges to [[_COMMUNITY_scorerengine.py]]
- 4 edges to [[_COMMUNITY_Settings]]
- 4 edges to [[_COMMUNITY_test_phase13_shortlist.py]]
- 4 edges to [[_COMMUNITY_test_application_portfolio.py]]
- 4 edges to [[_COMMUNITY_priority.py]]
- 3 edges to [[_COMMUNITY_typing]]
- 2 edges to [[_COMMUNITY_Profile]]
- 2 edges to [[_COMMUNITY_linkedin_people.py]]
- 2 edges to [[_COMMUNITY_filters.py]]
- 2 edges to [[_COMMUNITY_role_classify.py]]
- 2 edges to [[_COMMUNITY_textclean.py]]
- 2 edges to [[_COMMUNITY_ingest.py]]
- 2 edges to [[_COMMUNITY_suggest.py]]
- 2 edges to [[_COMMUNITY_diff.py]]
- 2 edges to [[_COMMUNITY_test_eligibility.py]]
- 2 edges to [[_COMMUNITY_builder.py]]
- 2 edges to [[_COMMUNITY_skills.py]]
- 2 edges to [[_COMMUNITY_baseline.py]]
- 2 edges to [[_COMMUNITY_Source]]
- 2 edges to [[_COMMUNITY_linkedin_jobspy.py]]
- 2 edges to [[_COMMUNITY_test_scorer.py]]
- 2 edges to [[_COMMUNITY_eligibility.py]]
- 2 edges to [[_COMMUNITY_pathlib]]
- 1 edge to [[_COMMUNITY_test_doctor.py]]
- 1 edge to [[_COMMUNITY_main.py]]
- 1 edge to [[_COMMUNITY_company_intelligence.py]]
- 1 edge to [[_COMMUNITY_profile.py]]
- 1 edge to [[_COMMUNITY_pytest]]

## Top bridge nodes
- [[json]] - degree 53, connects to 22 communities
- [[hashlib]] - degree 31, connects to 16 communities
- [[diagnostics.py]] - degree 22, connects to 11 communities
- [[test_diagnostics.py]] - degree 15, connects to 4 communities
- [[effective_baseline()]] - degree 14, connects to 4 communities