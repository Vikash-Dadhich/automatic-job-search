---
source_file: "scorer/engine.py"
type: "code"
community: "test_vector_recovery.py"
location: "L1064"
tags:
  - graphify/code
  - graphify/EXTRACTED
  - community/test_vector_recoverypy
---

# score_pending()

## Connections
- [[Embedder]] - `uses` [INFERRED]
- [[LLMClient_1]] - `uses` [INFERRED]
- [[Module-level entry point used by README  Step 7.]] - `rationale_for` [EXTRACTED]
- [[Profile]] - `uses` [INFERRED]
- [[ScoreSummary]] - `references` [EXTRACTED]
- [[Scorer]] - `calls` [EXTRACTED]
- [[_score()]] - `calls` [EXTRACTED]
- [[pipeline.py]] - `indirect_call` [INFERRED]
- [[scorer__init__.py]] - `imports` [EXTRACTED]
- [[scorerengine.py]] - `contains` [EXTRACTED]
- [[test_budget_skips_tail_after_a_reject()]] - `calls` [EXTRACTED]
- [[test_cached_embedding_skips_job_text()]] - `calls` [EXTRACTED]
- [[test_career_intelligence.py]] - `imports` [EXTRACTED]
- [[test_clearance_is_not_embedded()]] - `calls` [EXTRACTED]
- [[test_config_change_reopens_a_stored_reject()]] - `calls` [EXTRACTED]
- [[test_cover_letter.py]] - `imports` [EXTRACTED]
- [[test_cover_letter_failure_still_stages()]] - `calls` [EXTRACTED]
- [[test_dream_company_bypasses_low_cosine()]] - `calls` [EXTRACTED]
- [[test_embedder_failure_scores_anyway()]] - `calls` [EXTRACTED]
- [[test_embedder_failure_still_fails_open()]] - `calls` [EXTRACTED]
- [[test_failure_does_not_change_fit_priority_or_shortlist()]] - `calls` [EXTRACTED]
- [[test_gate_disabled_does_not_embed()]] - `calls` [EXTRACTED]
- [[test_gate_rejects_orthogonal_and_scores_match()]] - `calls` [EXTRACTED]
- [[test_no_score_budget_scores_every_eligible_job()]] - `calls` [EXTRACTED]
- [[test_profile_change_reuses_jd_vector()]] - `calls` [EXTRACTED]
- [[test_reopen_stays_closed_when_still_below()]] - `calls` [EXTRACTED]
- [[test_reopen_when_threshold_drops()]] - `calls` [EXTRACTED]
- [[test_score_pending_persists_tier_one_letter_only()]] - `calls` [EXTRACTED]
- [[test_score_pending_skips_cooldown_company()]] - `calls` [EXTRACTED]
- [[test_score_pending_stop_after_staged()]] - `calls` [EXTRACTED]
- [[test_score_pending_tiers_and_outreach()]] - `calls` [EXTRACTED]
- [[test_score_pending_token_usage()]] - `calls` [EXTRACTED]
- [[test_scorer.py]] - `imports` [EXTRACTED]
- [[test_short_text_fails_open_without_embed()]] - `calls` [EXTRACTED]
- [[test_shortlist.py]] - `imports` [EXTRACTED]
- [[test_tier_one_drafts_stay_off_unless_enabled()]] - `calls` [EXTRACTED]
- [[test_vector_gate.py]] - `imports` [EXTRACTED]
- [[test_vector_recovery.py]] - `imports` [EXTRACTED]

#graphify/code #graphify/EXTRACTED #community/test_vector_recoverypy