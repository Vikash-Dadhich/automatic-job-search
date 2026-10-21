---
source_file: "scraper/filters.py"
type: "code"
community: "Profile"
location: "L294"
tags:
  - graphify/code
  - graphify/EXTRACTED
  - community/Profile
---

# evaluate()

## Connections
- [[3. Hard filters (before any model)]] - `references` [INFERRED]
- [[FilterResult]] - `calls` [EXTRACTED]
- [[Profile]] - `uses` [INFERRED]
- [[RawPosting]] - `uses` [INFERRED]
- [[Return whether a posting should proceed to scoring.]] - `rationale_for` [EXTRACTED]
- [[_haystack()]] - `calls` [EXTRACTED]
- [[_location_ok()]] - `calls` [EXTRACTED]
- [[_seniority_reason()]] - `calls` [EXTRACTED]
- [[_yoe_reason()]] - `calls` [EXTRACTED]
- [[clearance_requirement()]] - `calls` [EXTRACTED]
- [[company_matches()]] - `calls` [EXTRACTED]
- [[contains_phrase()]] - `calls` [EXTRACTED]
- [[evaluate_job()]] - `calls` [EXTRACTED]
- [[filters.py]] - `contains` [EXTRACTED]
- [[get_settings()]] - `calls` [EXTRACTED]
- [[has_internship_signal()]] - `calls` [EXTRACTED]
- [[ingest.py]] - `imports` [EXTRACTED]
- [[re]] - `calls` [EXTRACTED]
- [[run_ingestion()]] - `calls` [EXTRACTED]
- [[sponsorship_signal()]] - `calls` [EXTRACTED]
- [[test_clearance_regex_pattern()]] - `calls` [EXTRACTED]
- [[test_clearance_words_must_be_about_clearance()]] - `calls` [EXTRACTED]
- [[test_company_blocklist_does_not_match_lookalikes()]] - `calls` [EXTRACTED]
- [[test_eligibility.py]] - `imports` [EXTRACTED]
- [[test_exclude_clearance_keyword()]] - `calls` [EXTRACTED]
- [[test_exclude_high_yoe_requirement()]] - `calls` [EXTRACTED]
- [[test_exclude_off_target_location()]] - `calls` [EXTRACTED]
- [[test_exclude_seniority_title()]] - `calls` [EXTRACTED]
- [[test_exclude_sponsorship_hostile_when_needed()]] - `calls` [EXTRACTED]
- [[test_exclude_staffing_company()]] - `calls` [EXTRACTED]
- [[test_explicit_internship_title_survives_seniority_words()]] - `calls` [EXTRACTED]
- [[test_false_negative.py]] - `imports` [EXTRACTED]
- [[test_filters.py]] - `imports` [EXTRACTED]
- [[test_friendly_sponsorship_stays_eligible()]] - `calls` [EXTRACTED]
- [[test_hostile_sponsorship_is_rejected()]] - `calls` [EXTRACTED]
- [[test_internship_only_drops_non_internship_titles()]] - `calls` [EXTRACTED]
- [[test_internship_only_keeps_internship_titles()]] - `calls` [EXTRACTED]
- [[test_internship_only_off_by_default()]] - `calls` [EXTRACTED]
- [[test_internship_only_passes_intern_title()]] - `calls` [EXTRACTED]
- [[test_internship_only_rejects_fulltime()]] - `calls` [EXTRACTED]
- [[test_internship_only_rejects_international_substring()]] - `calls` [EXTRACTED]
- [[test_internship_signal_matches_the_existing_gate()]] - `calls` [EXTRACTED]
- [[test_mba_summer_associate_is_an_internship_signal()]] - `calls` [EXTRACTED]
- [[test_missing_or_weak_evidence_does_not_filter()]] - `calls` [EXTRACTED]
- [[test_pass_mid_level_pm()]] - `calls` [EXTRACTED]
- [[test_pass_remote_role()]] - `calls` [EXTRACTED]
- [[test_phase0_baseline.py]] - `imports` [EXTRACTED]
- [[test_preferred_clearance_is_not_a_hard_rejection()]] - `calls` [EXTRACTED]
- [[test_recruiting_universe.py]] - `imports` [EXTRACTED]
- [[test_robustness.py]] - `imports` [EXTRACTED]
- [[test_unknown_sponsorship_stays_eligible()]] - `calls` [EXTRACTED]
- [[test_yoe_ceiling_follows_profile()]] - `calls` [EXTRACTED]
- [[test_yoe_counts_only_a_mandatory_minimum()]] - `calls` [EXTRACTED]
- [[test_yoe_keeps_job_when_a_lower_band_is_reachable()]] - `calls` [EXTRACTED]

#graphify/code #graphify/EXTRACTED #community/Profile