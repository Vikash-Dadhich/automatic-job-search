---
source_file: "core/db.py"
type: "code"
community: "upsert_job"
location: "L1202"
tags:
  - graphify/code
  - graphify/EXTRACTED
  - community/upsert_job
---

# get_job_by_source_id()

## Connections
- [[AsyncSession_1]] - `references` [EXTRACTED]
- [[Job]] - `references` [EXTRACTED]
- [[Source]] - `references` [EXTRACTED]
- [[Status lifecycle]] - `references` [INFERRED]
- [[_apply_role_classification()]] - `calls` [EXTRACTED]
- [[db.py]] - `contains` [EXTRACTED]
- [[ingest.py]] - `imports` [EXTRACTED]
- [[test_classification_persists_and_does_not_filter()]] - `calls` [EXTRACTED]
- [[test_compile_pending_skips_existing()]] - `calls` [EXTRACTED]
- [[test_cover_letter.py]] - `imports` [EXTRACTED]
- [[test_cover_letter_failure_still_stages()]] - `calls` [EXTRACTED]
- [[test_db_ingest.py]] - `imports` [EXTRACTED]
- [[test_discovered_job_keeps_provenance()]] - `calls` [EXTRACTED]
- [[test_discovery.py]] - `imports` [EXTRACTED]
- [[test_eligibility.py]] - `imports` [EXTRACTED]
- [[test_first_discovery_provenance_is_immutable()]] - `calls` [EXTRACTED]
- [[test_jd_ingest.py]] - `imports` [EXTRACTED]
- [[test_job_identity.py]] - `imports` [EXTRACTED]
- [[test_recruiting_universe.py]] - `imports` [EXTRACTED]
- [[test_resume.py]] - `imports` [EXTRACTED]
- [[test_role_classify.py]] - `imports` [EXTRACTED]
- [[test_role_secondary.py]] - `imports` [EXTRACTED]
- [[test_same_source_identity_and_cross_source_url()]] - `calls` [EXTRACTED]
- [[test_score_pending_persists_tier_one_letter_only()]] - `calls` [EXTRACTED]
- [[test_score_pending_skips_cooldown_company()]] - `calls` [EXTRACTED]
- [[test_score_pending_tiers_and_outreach()]] - `calls` [EXTRACTED]
- [[test_scorer.py]] - `imports` [EXTRACTED]
- [[test_secondary_fields_persist_and_clear_when_the_jd_changes()]] - `calls` [EXTRACTED]
- [[test_sqlite_persistence_and_upsert()]] - `calls` [EXTRACTED]
- [[test_tier_one_drafts_stay_off_unless_enabled()]] - `calls` [EXTRACTED]
- [[test_unchanged_jd_keeps_classification_and_a_change_replaces_it()]] - `calls` [EXTRACTED]
- [[test_upsert_idempotent_and_status_refresh()]] - `calls` [EXTRACTED]
- [[test_upsert_keeps_good_jd_and_clears_stale_embedding()]] - `calls` [EXTRACTED]

#graphify/code #graphify/EXTRACTED #community/upsert_job