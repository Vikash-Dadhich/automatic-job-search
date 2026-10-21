# Graph Report - Automatic job search  (2026-10-20)

## Corpus Check
- 219 files · ~192,000 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 13 file(s) not represented in the graph (top: (none) 8, .typ 2, .example 1)

## Summary
- 4039 nodes · 13942 edges · 152 communities (136 shown, 16 thin omitted)
- Extraction: 89% EXTRACTED · 11% INFERRED · 0% AMBIGUOUS · INFERRED: 1479 edges (avg confidence: 0.94)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `5b877dd3`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- job_identity.py
- structured_jd.py
- Profile
- test_recruiting_universe.py
- handlers.py
- call_with_resilience
- test_career_intelligence.py
- test_feedback.py
- test_discovery.py
- test_openai_run_usage.py
- evaluate
- workday_rest.py
- conftest.py
- textclean.py
- discovery_recall.py
- answers.py
- eligibility.py
- ingest.py
- apply_pending
- test_structured_jd.py
- pipeline.py
- TelegramClient
- test_resume.py
- scheduler.py
- FakeTransport
- diff.py
- test_company_intelligence.py
- classify_role
- pacing.py
- test_pipeline.py
- test_ingest_resilience.py
- get_job_by_id
- test_calibration.py
- LLMClient
- test_eligibility.py
- test_company_intelligence_v2.py
- Remaining Manual Setup
- pytest
- test_monitoring.py
- test_phase13_shortlist.py
- Status
- profile.py
- load_persisted_calibration
- compiler.py
- test_phase0_baseline.py
- skills.py
- test_workload_limits.py
- role_classify.py
- Settings
- AGENTS.md
- test_application_portfolio.py
- test_priority.py
- Phase 5 role classification
- scorer/__init__.py
- test_apply_url.py
- priority.py
- main.py
- session_scope
- Benchmark — Product Manager @ T-Mobile
- test_false_negative.py
- score_pending
- OpenAIClient
- tracker.py
- review.py
- migrate_to_neon.py
- 5. How fit is scored
- discovery_experiment.py
- test_trial_workflow.py
- db.py
- job-agent
- prerank_score
- get_settings
- linkedin_jobspy.py
- phase10-false-negative-protection.md
- benchmark/engine.py
- Phase 1 discovery architecture
- Phase 0 baseline
- test_webhook.py
- test_role_classify.py
- Priority 2.0
- How jobs are found, filtered, scored, and sent
- vault.py
- runner.py
- application_deadline.py
- Discovery recall benchmark
- telegram.py
- 2. Where jobs come from
- 8. The weight discussion (not built)
- test_pacing.py
- Phase 8 company intelligence
- test_llm_provider.py
- correction1-recruiting-universe.md
- typing
- test_openai_request_gate.py
- company_intelligence.py
- feedback.py
- Phase 16 feedback learning
- scorer/engine.py
- test_application_deadline.py
- MonkeyPatch
- calibration.py
- test_cover_letter.py
- Phase 15 application tracker
- json
- CompanyIntelligence
- 3. Hard filters (before any model)
- get_recently_applied_companies
- 9. Pain points we have actually hit or spelled out
- Job Agent
- calculate_priority
- Phase 12 priority ranking
- Phase 6 candidate fit
- test_prep_builder.py
- get_health_report
- Company intelligence 2.0
- filters.py
- phase17-calibration-benchmark.md
- webhook.py
- HttpCompanyIntelProvider
- vector-recovery.md
- Phase 18 — Production reliability and monitoring
- Multi-dimensional role classification
- 6. What is sent to you
- dataclasses
- _input_hash
- OpenAIRequestLedger
- Job
- upsert_job
- test_role_weights.py
- clients.py
- service.py
- pathlib
- normalize_company_name
- test_doctor.py
- Source
- extract_company_facts
- Career Intelligence
- OpenAI usage summary
- Phase 9 visa and eligibility
- Phase 4 JD ingestion
- Phase 7 role-family weighting
- test_workday_locators.py
- re
- is_pace_blocker
- baseline.py

## God Nodes (most connected - your core abstractions)
1. `Job` - 385 edges
2. `Profile` - 337 edges
3. `session_scope()` - 324 edges
4. `Status` - 257 edges
5. `Source` - 227 edges
6. `get_settings()` - 187 edges
7. `get_job_by_id()` - 162 edges
8. `upsert_job()` - 144 edges
9. `TelegramClient` - 92 edges
10. `init_db()` - 90 edges

## Surprising Connections (you probably didn't know these)
- `What the profile contributes` --references--> `Profile`  [INFERRED]
  docs/phase9-visa-eligibility.md → config/profile.py
- `9.1 Discovery` --references--> `test_internship_only_rejects_international_substring()`  [INFERRED]
  docs/how-jobs-are-found-scored-and-sent.md → tests/test_filters.py
- `Four different questions` --references--> `score()`  [INFERRED]
  docs/phase7-role-family-weighting.md → tests/test_priority_v2.py
- `Application deadline` --references--> `init_db()`  [INFERRED]
  docs/structured-jd-intelligence.md → core/db.py
- `Run review bot (Step 6)` --references--> `send_pending_alerts()`  [INFERRED]
  README.md → bot/alerts.py

## Import Cycles
- None detected.

## Communities (152 total, 16 thin omitted)

### Community 0 - "job_identity.py"
Cohesion: 0.15
Nodes (13): _assign_canonical_url(), _find_cross_source_job(), canonicalize_job_url(), _is_tracking_param(), locations_agree(), locations_conflict(), normalize_title(), same_employer() (+5 more)

### Community 1 - "structured_jd.py"
Cohesion: 0.13
Nodes (37): _authorization(), AuthorizationEvidence, _availability(), _clause_at(), _clauses(), _clip(), _degree_state(), _domain() (+29 more)

### Community 2 - "Profile"
Cohesion: 0.10
Nodes (38): Profile, build_fit_system_blocks(), build_fit_user(), cached_fit(), _Dimension, evaluate_fit(), fit_context_block(), fit_is_current() (+30 more)

### Community 3 - "test_recruiting_universe.py"
Cohesion: 0.39
Nodes (6): _family(), _jd(), test_first_discovery_provenance_is_immutable(), test_marketing_is_separate_from_product_marketing_and_other(), test_mba_summer_associate_is_an_internship_signal(), test_technology_strategy_is_not_technology_consulting()

### Community 4 - "handlers.py"
Cohesion: 0.09
Nodes (28): _decision_caption(), _handle_outcome_callback(), _safe_answer(), build_outcome_keyboard(), button(), outcome_label(), outcome_message_text(), OutcomePromptSummary (+20 more)

### Community 5 - "call_with_resilience"
Cohesion: 0.08
Nodes (22): LLM client layer (`scorer/clients.py`), _backoff_delay(), call_with_resilience(), is_permanent_account_error(), is_transient(), LLMBillingError, LLMError, OpenAIRequestBlocked (+14 more)

### Community 6 - "test_career_intelligence.py"
Cohesion: 0.08
Nodes (51): CareerIntelligence, _apply_reading(), assess_career(), attach_career_intelligence(), career_input_hash(), CareerReading, _clause(), _clip() (+43 more)

### Community 7 - "test_feedback.py"
Cohesion: 0.14
Nodes (18): Application, ApplicationEvent, get_application_by_id(), get_application_events(), list_events_for_applications(), list_jobs_by_ids(), list_submitted_applications(), load_feedback_cases() (+10 more)

### Community 8 - "test_discovery.py"
Cohesion: 0.08
Nodes (36): load_targets(), allocate_units(), AllocItem, build_discovery_plan(), DiscoveryConfig, DiscoverySource, _enabled_queries(), enabled_query_texts() (+28 more)

### Community 9 - "test_openai_run_usage.py"
Cohesion: 0.09
Nodes (29): emit_openai_run_usage(), pop_openai_operation(), push_openai_operation(), _Chat, _ChatHolder, _ChatResponse, _ChatUsage, _Choice (+21 more)

### Community 10 - "evaluate"
Cohesion: 0.15
Nodes (25): evaluate(), sponsorship_signal(), test_sponsorship_and_false_friends(), _posting(), test_clearance_regex_pattern(), test_exclude_clearance_keyword(), test_exclude_high_yoe_requirement(), test_exclude_off_target_location() (+17 more)

### Community 11 - "workday_rest.py"
Cohesion: 0.05
Nodes (35): reload_profile(), _load_yaml(), parse_workday_url(), reload_targets(), WorkdayParts, WorkdayTenant, _as_text(), _company_name() (+27 more)

### Community 12 - "conftest.py"
Cohesion: 0.18
Nodes (7): Testing conventions, db_ready(), _disable_apply_pacing(), _disable_vector_gate(), _internship_only_off(), _reset_openai_request_ledger_between_tests(), tmp_db()

### Community 13 - "textclean.py"
Cohesion: 0.11
Nodes (19): Flow, _drop_boilerplate_lines(), _extract_body(), extract_sections(), html_to_text(), JdStatus, normalize_description(), _normalize_whitespace() (+11 more)

### Community 14 - "discovery_recall.py"
Cohesion: 0.14
Nodes (29): _verified_benchmark_hits(), BenchmarkCase, _bucket(), _case(), case_is_captured(), eligible(), _identity_conflict(), load_benchmark() (+21 more)

### Community 15 - "answers.py"
Cohesion: 0.08
Nodes (26): AnswerResolver, one(), answers_to_payload(), AnswerSource, _discovery_channel(), is_open_ended(), _latest_education(), _matches() (+18 more)

### Community 16 - "eligibility.py"
Cohesion: 0.17
Nodes (25): _ask_model(), _citizenship(), _clearance(), _current_student(), _dates(), _decision_from_job(), _dim(), DimensionResult (+17 more)

### Community 17 - "ingest.py"
Cohesion: 0.05
Nodes (56): close_stage_run(), list_stage_runs(), open_stage_run(), _safe_close_stage(), build_coverage_report(), add_planned(), group_for(), CoverageReport (+48 more)

### Community 18 - "apply_pending"
Cohesion: 0.21
Nodes (24): apply_pending(), FakeApplicator, _script_reloads(), _seed_job(), test_allocation_removed_before_execution_is_skipped(), test_apply_linkedin_with_workday_url(), test_apply_pending_blocker(), test_apply_pending_empty() (+16 more)

### Community 19 - "test_structured_jd.py"
Cohesion: 0.10
Nodes (24): StructuredJobDescription, Application deadline, Cache, Limits, Structured JD intelligence, What is stored, attach_structured_jd(), extract_structured_jd() (+16 more)

### Community 20 - "pipeline.py"
Cohesion: 0.10
Nodes (21): _allocated_ids(), _benchmark_tier_one_stage(), _generate_suggestions_stage(), _ingest_stage(), _note_skipped(), _pipeline_status(), PipelineSummary, _portfolio_stage() (+13 more)

### Community 21 - "TelegramClient"
Cohesion: 0.13
Nodes (3): HttpxTransport, TelegramClient, TelegramTransport

### Community 22 - "test_resume.py"
Cohesion: 0.12
Nodes (18): build_resume_data(), extract_job_terms(), _grounded_summary(), RankedBullet, reorder_skills(), score_bullet(), select_bullets(), SelectedExperience (+10 more)

### Community 23 - "scheduler.py"
Cohesion: 0.15
Nodes (8): build_scheduler(), parse_hhmm(), _noop(), test_build_scheduler_invalid_timezone(), test_build_scheduler_registers_jobs(), test_build_scheduler_skips_invalid_times(), test_parse_hhmm(), test_parse_hhmm_invalid()

### Community 24 - "FakeTransport"
Cohesion: 0.10
Nodes (24): send_prep_pack(), _should_retry_telegram(), FakeClient, test_send_prep_pack_empty(), test_send_prep_pack_marks_jobs(), FakeTransport, _enable_brief(), _insert() (+16 more)

### Community 25 - "diff.py"
Cohesion: 0.10
Nodes (28): apply_decided_suggestions(), get_role_baseline_by_id(), get_role_baseline_by_role(), get_suggestions_for_job(), RoleBaseline, SkillPlacement, SkillProvenance, SkillSuggestion (+20 more)

### Community 26 - "test_company_intelligence.py"
Cohesion: 0.25
Nodes (17): attach_company_intelligence(), resolve_company(), FakeProvider, _job(), _posting(), test_ambiguous_names_stay_separate(), test_company_facts_do_not_change_scoring_signals(), test_company_sources_accumulate_and_a_failed_refresh_keeps_them() (+9 more)

### Community 27 - "classify_role"
Cohesion: 0.19
Nodes (15): classify_role(), _jd(), test_cache_recomputes_only_when_hash_or_version_changes(), test_collaboration_responsibility_is_not_a_secondary_family(), test_hybrid_roles_keep_a_second_family(), test_interaction_evidence_from_the_model_is_rejected(), test_interaction_is_not_a_second_family(), test_llm_prompt_includes_structured_responsibilities() (+7 more)

### Community 28 - "pacing.py"
Cohesion: 0.16
Nodes (11): acquire(), AcquireResult, _clamp_multiplier(), _clock(), end_of_local_day(), gap_seconds(), note_pace_block(), note_success() (+3 more)

### Community 29 - "test_pipeline.py"
Cohesion: 0.09
Nodes (22): _FakeSummary, test_pipeline_order_and_aggregation(), fake_alerts(), fake_apply(), fake_ingestion(), fake_outcomes(), fake_prep(), fake_resume() (+14 more)

### Community 30 - "test_ingest_resilience.py"
Cohesion: 0.05
Nodes (50): Targets, SearchStatus, run_ingestion(), _accept(), _run_jobspy(), _run_workday(), kill_process_group(), LineWorker (+42 more)

### Community 31 - "get_job_by_id"
Cohesion: 0.11
Nodes (24): handle_callback(), process_updates(), run_polling(), build_keyboard(), Submitter, decode_callback(), encode_callback(), ReviewAction (+16 more)

### Community 32 - "test_calibration.py"
Cohesion: 0.21
Nodes (20): brier_score(), build_calibration(), CalibrationFold, CalibrationReport, load_calibration_config(), run_calibration(), load_feedback_config(), _calibration() (+12 more)

### Community 33 - "LLMClient"
Cohesion: 0.10
Nodes (12): is_openai_safety_error(), LLMClient, _attach_priority(), _attach_usage_summary(), _emit_usage_summary(), _JobOutcome, _priority_evidence(), Scorer (+4 more)

### Community 34 - "test_eligibility.py"
Cohesion: 0.15
Nodes (20): assign_eligibility(), attach_eligibility(), eligibility_column_types(), eligibility_is_current(), EligibilityDecision, evaluate_eligibility(), profile_eligibility_hash(), _job() (+12 more)

### Community 35 - "test_company_intelligence_v2.py"
Cohesion: 0.17
Nodes (9): CompanyIntelProvider, CompanyLookupResult, CompanySourceDocument, refresh_company_intelligence(), _one(), _Provider, _signals(), test_changed_page_replaces_that_source_and_keeps_another() (+1 more)

### Community 36 - "Remaining Manual Setup"
Cohesion: 0.08
Nodes (25): 2a. Find a Workday URL, 2b. Edit `config/targets.yaml`, 3a. Run the save-session helper, 3b. What you do in the browser, 4a. Discover jobs (LinkedIn / Indeed + any real Workday tenants), 4b. Score with Gemini, 4c. Attach your base resume to staged jobs, 4d. Send LinkedIn/Indeed application prep pack (Telegram) (+17 more)

### Community 37 - "pytest"
Cohesion: 0.06
Nodes (28): SessionMissingError, auto_discover_peers(), _crawl(), BlockerError, build_people_search_url(), _detect_blocker(), discover_peers(), extract_profile_urls() (+20 more)

### Community 38 - "test_monitoring.py"
Cohesion: 0.12
Nodes (27): close_pipeline_run(), count_stale_jobs(), interrupt_stale_runs(), list_pipeline_runs(), load_monitoring_config(), _moment(), monitoring_config_hash(), open_pipeline_run() (+19 more)

### Community 39 - "test_phase13_shortlist.py"
Cohesion: 0.09
Nodes (33): get_jobs_by_status(), apply_shortlist(), _close_enough(), _company_key(), _company_ok(), config_hash(), _diversify(), _family() (+25 more)

### Community 40 - "Status"
Cohesion: 0.24
Nodes (15): application_history(), SubmitResult, get_application_for_job(), Status, _count(), _job(), _Prefill, _Submitter (+7 more)

### Community 41 - "profile.py"
Cohesion: 0.16
Nodes (27): Address, Education, Exclusions, Experience, Identity, Preferences, WorkAuthorization, _make_base_pdf() (+19 more)

### Community 42 - "load_persisted_calibration"
Cohesion: 0.36
Nodes (7): CalibrationMetric, CalibrationRun, get_calibration_metrics(), get_calibration_run(), save_calibration_run(), load_persisted_calibration(), persist_calibration()

### Community 43 - "compiler.py"
Cohesion: 0.09
Nodes (22): load_profile(), _load_yaml(), apply_fit_caps(), _baseline_pdf_for_job(), clean_name(), compile_for_job(), compile_pending(), compile_resume() (+14 more)

### Community 44 - "test_phase0_baseline.py"
Cohesion: 0.17
Nodes (13): _enable_internship_only(), _posting(), test_experience_span_is_about_five_years_and_not_summed(), test_friendly_sponsorship_stays_eligible(), test_hostile_sponsorship_is_rejected(), test_internship_only_code_default_is_false(), test_internship_only_drops_non_internship_titles(), test_internship_only_keeps_internship_titles() (+5 more)

### Community 45 - "skills.py"
Cohesion: 0.08
Nodes (23): aggregate_role_skills(), AggregatedSkill, _categorize(), extract_top_skills(), extract_top_skills_deterministic(), JdSkill, parse_skills_json(), _repair_truncated_json_array() (+15 more)

### Community 46 - "test_workload_limits.py"
Cohesion: 0.07
Nodes (45): ScoringSafetyHalt, IngestSummary, test_safety_halt_does_not_send_or_apply(), halt(), ingest(), _Chat, _chat_ok(), _ChatHolder (+37 more)

### Community 47 - "role_classify.py"
Cohesion: 0.14
Nodes (19): _clause_containing(), _clip_items(), _deterministic(), _is_interaction(), _item_text(), _ModelLabel, _parse_model(), _phrase_hits() (+11 more)

### Community 49 - "AGENTS.md"
Cohesion: 0.11
Nodes (10): Build order and status, Coding conventions, Commands, Confirmed product decisions, Project, Repository layout, Scoring specifics (Step 3), What still needs the user (before live runs) (+2 more)

### Community 50 - "test_application_portfolio.py"
Cohesion: 0.06
Nodes (54): Configuration, Phase 13 shortlist, Pipeline, Selection, allocate_portfolio(), can_take(), identity(), take() (+46 more)

### Community 51 - "test_priority.py"
Cohesion: 0.16
Nodes (20): apply_priority(), load_priority_config(), priority_is_current(), PriorityDecision, role_family_component(), _job(), test_dream_company_is_only_a_configured_boost(), test_eligibility_unknown_is_not_ineligible() (+12 more)

### Community 52 - "Phase 5 role classification"
Cohesion: 0.29
Nodes (6): Inputs, Limits, Output, Phase 5 role classification, Taxonomy, When it runs again

### Community 54 - "test_apply_url.py"
Cohesion: 0.22
Nodes (11): ApplyKind, classify_apply_url(), _host(), is_automateable_apply_url(), is_workday_url(), workday_parts(), _cmd_list_apply(), test_classify_company_site() (+3 more)

### Community 55 - "priority.py"
Cohesion: 0.13
Nodes (23): _combine(), company_domain_component(), _company_signals(), _components(), dream_company_component(), eligibility_component(), _explicit_sections(), fit_component() (+15 more)

### Community 56 - "main.py"
Cohesion: 0.10
Nodes (26): build_parser(), _cmd_benchmark(), _cmd_build_baseline(), _cmd_health(), _cmd_poll(), _cmd_prep_pack(), _cmd_run_once(), _cmd_save_linkedin_session() (+18 more)

### Community 57 - "session_scope"
Cohesion: 0.26
Nodes (32): session_scope(), get_career_intelligence(), _enable(), _seed(), _assert_no_profile_text(), _bare_job(), _doc(), _exclude_company() (+24 more)

### Community 58 - "Benchmark — Product Manager @ T-Mobile"
Cohesion: 0.33
Nodes (5): Benchmark — Product Manager @ T-Mobile, Dimensions, Gaps, Recommendations, Strengths

### Community 59 - "test_false_negative.py"
Cohesion: 0.19
Nodes (10): citizenship_restriction(), clearance_requirement(), _matches_any(), max_acceptable_years(), _posting(), test_clearance_words_must_be_about_clearance(), test_explicit_internship_title_survives_seniority_words(), test_missing_or_weak_evidence_does_not_filter() (+2 more)

### Community 60 - "score_pending"
Cohesion: 0.11
Nodes (27): job_embed_text(), profile_embed_text(), profile_hash(), score_pending(), FakeClient, test_score_pending_marks_error(), test_score_pending_skips_cooldown_company(), test_score_pending_stop_after_staged() (+19 more)

### Community 61 - "OpenAIClient"
Cohesion: 0.14
Nodes (27): OpenAIClient, test_openai_client_scores_json(), create(), _Chat, _chat_attempts(), _Choice, _complete(), _CompletionDetails (+19 more)

### Community 62 - "tracker.py"
Cohesion: 0.21
Nodes (15): _add_event(), application_method(), backfill_submitted_applications(), _event_exists(), _get_or_create(), record_manual_review(), record_outcome(), record_prefill() (+7 more)

### Community 63 - "review.py"
Cohesion: 0.16
Nodes (12): build_review_caption(), format_answers_message(), format_cover_letter_message(), ReviewSummary, _send_one(), send_pending_reviews(), get_unsent_pending_reviews(), test_build_keyboard_and_caption() (+4 more)

### Community 64 - "migrate_to_neon.py"
Cohesion: 0.24
Nodes (6): _cell(), _copy_table(), _counts(), main(), _reset_sequences(), _row()

### Community 65 - "5. How fit is scored"
Cohesion: 0.22
Nodes (7): 10. File map, 5.1 What the model is, 5.2 The two inputs, 5.3 The rubric, verbatim in meaning, 5.4 What the code does with the score, 5.5 What a number means, 5. How fit is scored

### Community 66 - "discovery_experiment.py"
Cohesion: 0.06
Nodes (61): account_executions(), _baseline_slot_reason(), _baseline_slots(), build_schedule(), _classify_incremental(), compare_arms(), _execute(), _execute_phrase() (+53 more)

### Community 67 - "test_trial_workflow.py"
Cohesion: 0.14
Nodes (10): _absolute_sqlite_url(), normalize_database_url(), test_normalize_drops_prisma_connection_limit(), test_normalize_keeps_sqlite(), test_normalize_upgrades_postgres_scheme(), test_normalize_upgrades_postgresql(), test_trial_env_matches_the_settings_parser(), test_trial_sqlite_url_creates_the_schema() (+2 more)

### Community 68 - "db.py"
Cohesion: 0.08
Nodes (23): _company_name(), _dialect_name(), _drop_structured_jd(), _ensure_company_columns(), _ensure_job_columns(), _ensure_pipeline_stage_columns(), get_engine(), get_session_factory() (+15 more)

### Community 71 - "prerank_score"
Cohesion: 0.21
Nodes (12): prerank_jobs(), prerank_score(), _source_weight(), _job(), test_dream_company_boost(), test_intern_title_outranks_fulltime(), test_new_source_scored_without_error(), test_prerank_jobs_empty() (+4 more)

### Community 72 - "get_settings"
Cohesion: 0.14
Nodes (6): launch_context(), _new_context(), save_storage_state(), save_session(), get_settings(), save_linkedin_session()

### Community 73 - "linkedin_jobspy.py"
Cohesion: 0.09
Nodes (19): SearchConfig, main(), _one(), _records(), _dataframe_to_postings(), _effective_windows(), _explicit_company_url(), _external_id() (+11 more)

### Community 75 - "benchmark/engine.py"
Cohesion: 0.13
Nodes (18): BenchmarkReport, BenchmarkSummary, build_benchmark(), _derive_seniority(), DimensionScore, _education_rank(), _median(), _norm() (+10 more)

### Community 76 - "Phase 1 discovery architecture"
Cohesion: 0.11
Nodes (16): 40/40/15/5 priority model, Current problem, New architecture, Phase 1 discovery architecture, Provenance, Purpose, Role families, Search allocation (+8 more)

### Community 77 - "Phase 0 baseline"
Cohesion: 0.22
Nodes (8): Candidate baseline, Discovery baseline, Local versus production, Phase 0 baseline, Production baseline, Scoring baseline, Sponsorship behavior locked by tests, Tests

### Community 78 - "test_webhook.py"
Cohesion: 0.26
Nodes (5): client(), test_health(), test_webhook_ignored_without_callback(), test_webhook_rejects_bad_secret(), test_webhook_routes_callback()

### Community 79 - "test_role_classify.py"
Cohesion: 0.17
Nodes (15): _role_classification_current(), classification_is_current(), _apply_role_classification(), _FakeClient, _jd(), test_classification_persists_and_does_not_filter(), test_classifier_version_bump_invalidates_phase5_v1(), test_invalid_confidence_is_unknown() (+7 more)

### Community 80 - "Priority 2.0"
Cohesion: 0.29
Nodes (6): Freshness, dream company, and workflow, Hash, Priority 2.0, Program and domain evidence, Role alignment, Weights

### Community 81 - "How jobs are found, filtered, scored, and sent"
Cohesion: 0.25
Nodes (7): 1. What a run is, 4.1 Pre-score rank (`prerank_score`), 4.2 Embedding gate (this does drop jobs), 4.3 Fit-model cap, 4. How results are prioritised today, 7. Statuses, in one pass, How jobs are found, filtered, scored, and sent

### Community 82 - "vault.py"
Cohesion: 0.15
Nodes (13): CredentialsFile, get_tenant_credentials(), has_saved_session(), load_credentials(), _load_yaml(), reload_credentials(), session_state_path(), TenantCredentials (+5 more)

### Community 83 - "runner.py"
Cohesion: 0.10
Nodes (11): ApplyRunner, ApplySummary, _eligible(), _ensure_tenant(), _log_explicit_skip(), _ready_for_explicit_apply(), _reload_job(), Applicator (+3 more)

### Community 84 - "application_deadline.py"
Cohesion: 0.15
Nodes (13): ApplicationDeadline, _clip(), empty_application_deadline(), _excluded(), extract_application_deadline(), _from_match(), _named(), _parse_date() (+5 more)

### Community 85 - "Discovery recall benchmark"
Cohesion: 0.10
Nodes (18): Discovery recall benchmark, Label corrections on 2026-10-04, Limits, Matching, Reproduce, What is checked in, Discovery run observability, Query timeout and incremental save (+10 more)

### Community 86 - "telegram.py"
Cohesion: 0.11
Nodes (17): _handle_suggest_callback(), decide_suggestion(), _format_card(), send_pending_suggestions(), _suggestion_keyboard(), SuggestSummary, decode_suggest_callback(), encode_suggest_callback() (+9 more)

### Community 87 - "2. Where jobs come from"
Cohesion: 0.29
Nodes (7): 2.1 Search terms, 2.2 Sites and the exact JobSpy arguments, 2.3 How each site treats "posted in the last 36 hours", 2.4 What is kept from a JobSpy row, 2.5 Workday, separately from LinkedIn, 2.6 Save and dedupe, 2. Where jobs come from

### Community 88 - "8. The weight discussion (not built)"
Cohesion: 0.33
Nodes (6): 8.1 What you asked for, 8.2 Decisions you agreed with, 8.3 A weight table we used as a sketch, 8.4 What we said the rubric should do for career-switch roles, 8.5 How that would sit on the current pipeline, 8. The weight discussion (not built)

### Community 89 - "test_pacing.py"
Cohesion: 0.28
Nodes (15): _Applicator, _enable(), _row(), _seed(), _Sleep, test_acquire_after_blackout_keeps_multiplier(), test_acquire_skips_during_blackout(), test_block_doubles_until_cap_and_resets_streak() (+7 more)

### Community 90 - "Phase 8 company intelligence"
Cohesion: 0.29
Nodes (6): Names and reuse, Phase 8 company intelligence, Schema, Sources, What it is, What this phase does not change

### Community 91 - "test_llm_provider.py"
Cohesion: 0.11
Nodes (20): Tech stack, build_llm_client(), _FakeAio, _FakeAsyncModels, _FakeCandidate, _FakeGenaiClient, _FakeGenerateResponse, test_active_models_ignore_anthropic_names() (+12 more)

### Community 93 - "typing"
Cohesion: 0.07
Nodes (25): approx_tokens(), cache_block(), compact_json_dumps(), minify_job(), _fallback_cover_letter(), generate_cover_letter(), parse_score(), contains_banned() (+17 more)

### Community 94 - "test_openai_request_gate.py"
Cohesion: 0.10
Nodes (32): get_openai_request_ledger(), OpenAIBillingHalted, OpenAIBudgetExceeded, reset_openai_request_ledger(), _Chat, _ChatClient, _ChatResponse, _Choice (+24 more)

### Community 95 - "company_intelligence.py"
Cohesion: 0.12
Nodes (18): _accumulate_sources(), _apply_context(), _compact(), _confidence_for(), _context_from(), extract_company_signals(), merge_company_signals(), _prefer_signal() (+10 more)

### Community 96 - "feedback.py"
Cohesion: 0.12
Nodes (27): FeedbackRun, FeedbackSignal, get_feedback_run(), get_feedback_signals(), get_latest_feedback_run(), save_feedback_run(), calibration_config_hash(), _adjustment() (+19 more)

### Community 97 - "Phase 16 feedback learning"
Cohesion: 0.33
Nodes (5): Evidence and shrinkage, Phase 16 feedback learning, Rates, Segments, Who is counted

### Community 98 - "scorer/engine.py"
Cohesion: 0.07
Nodes (31): build_embedder(), _cache_path(), clears_threshold(), cosine(), Embedder, EmbedInputLimitReached, jd_vector(), load_profile_embedding() (+23 more)

### Community 99 - "test_application_deadline.py"
Cohesion: 0.19
Nodes (15): _pad(), _read(), test_deadline_failure_does_not_drop_the_rest_of_the_reading(), test_internship_and_graduation_dates_are_not_deadlines(), test_interview_deadline_is_not_an_application_deadline(), test_invalid_calendar_date_is_ambiguous(), test_markdown_split_year_is_kept(), test_meet_deadlines_is_not_an_application_deadline() (+7 more)

### Community 100 - "MonkeyPatch"
Cohesion: 0.11
Nodes (12): test_fresh_sqlite_health_check_does_not_warn_about_a_missing_table(), test_fresh_sqlite_opens_a_run_without_a_missing_table_warning(), _warn(), test_health_command_prints_no_secrets(), test_health_reports_database_failure(), test_health_reports_invalid_configuration(), test_pipeline_failure_outside_a_stage_is_failed(), boom() (+4 more)

### Community 101 - "calibration.py"
Cohesion: 0.15
Nodes (28): _as_utc(), _append_buckets(), _append_short_target(), _append_slice(), _append_target_metrics(), _append_topk(), _bucket_name(), CalibrationMetricRow (+20 more)

### Community 102 - "test_cover_letter.py"
Cohesion: 0.13
Nodes (10): cap_cover_letter(), _job(), _ScriptedClient, test_cap_cover_letter_cuts_on_sentence_boundary(), test_cap_cover_letter_hard_slice_without_punctuation(), test_cover_letter_failure_still_stages(), test_generate_cover_letter_falls_back_when_strip_empties(), test_generate_cover_letter_retries_banned_words() (+2 more)

### Community 103 - "Phase 15 application tracker"
Cohesion: 0.33
Nodes (5): Method and time, Phase 15 application tracker, States and outcomes, What this is not, When a row is created

### Community 104 - "json"
Cohesion: 0.09
Nodes (24): effective_baseline(), effective_config_hash(), fingerprint_profile(), profile_hash(), public_config(), write_effective_baseline(), _compiled(), _confidence() (+16 more)

### Community 105 - "CompanyIntelligence"
Cohesion: 0.26
Nodes (8): CompanyIntelligence, _apply_facts(), _by_key(), _clear_facts(), empty_company_context(), get_company_intelligence(), _new_row(), _store_failure()

### Community 106 - "3. Hard filters (before any model)"
Cohesion: 0.18
Nodes (11): 3.10 What a survivor looks like, 3.1 Company blocklist, 3.2 Exclusion keywords, 3.3 Clearance language, 3.4 Staffing agencies, 3.5 Internship gate, 3.6 Seniority filter (separate from the internship gate), 3.7 Years of experience (+3 more)

### Community 107 - "get_recently_applied_companies"
Cohesion: 0.20
Nodes (8): get_recently_applied_companies(), Capacity, Decisions, Phase 14 application portfolio, Pipeline, Role-family mix, What counts as a recent application, Who can be allocated

### Community 108 - "9. Pain points we have actually hit or spelled out"
Cohesion: 0.33
Nodes (6): 9.1 Discovery, 9.2 Filters, 9.3 Scoring, 9.4 What you receive, 9.5 Operations, 9. Pain points we have actually hit or spelled out

### Community 109 - "Job Agent"
Cohesion: 0.12
Nodes (15): Application prep packs (LinkedIn / Indeed), Deploy with Docker, Job Agent, Layout, LinkedIn peer benchmarking (optional, off by default), Resumes (Step 4), Run automation (Step 5), Run ingestion (Step 2) (+7 more)

### Community 110 - "calculate_priority"
Cohesion: 0.19
Nodes (17): Output, Cache and storage, calculate_priority(), _job(), _signal(), test_confidence_and_structured_evidence(), test_domains_are_capped_and_irrelevant_domains_add_nothing(), test_eligibility_order_and_unknown() (+9 more)

### Community 111 - "Phase 12 priority ranking"
Cohesion: 0.50
Nodes (3): Components, Phase 12 priority ranking, Version

### Community 112 - "Phase 6 candidate fit"
Cohesion: 0.40
Nodes (4): Dimensions, Not in this phase, Phase 6 candidate fit, When the model is not called

### Community 113 - "test_prep_builder.py"
Cohesion: 0.12
Nodes (13): _answer_item(), build_job_section(), compile_prep_pdf(), generate_prep_pack(), PrepPackResult, render_markdown(), FakeClient, _job() (+5 more)

### Community 114 - "get_health_report"
Cohesion: 0.19
Nodes (13): PipelineRun, PipelineStageRun, _brief(), format_health_report(), get_health_report(), _recent_failures(), _repeated_failures(), _run_view() (+5 more)

### Community 115 - "Company intelligence 2.0"
Cohesion: 0.33
Nodes (5): Company intelligence 2.0, Company versus job, Sources and refresh, What it does not store, What it stores

### Community 116 - "filters.py"
Cohesion: 0.13
Nodes (12): _clearance_clauses(), evaluate_job(), FilterResult, has_internship_signal(), _haystack(), location_acceptable(), _location_ok(), _mandatory_years() (+4 more)

### Community 118 - "webhook.py"
Cohesion: 0.17
Nodes (3): handle_message(), health(), telegram_webhook()

### Community 119 - "HttpCompanyIntelProvider"
Cohesion: 0.25
Nodes (4): HttpCompanyIntelProvider, test_http_provider_handles_timeout_and_malformed_pages(), ok(), test_http_provider_keeps_the_caller_source_type()

### Community 121 - "Phase 18 — Production reliability and monitoring"
Cohesion: 0.13
Nodes (14): Architecture, Backlog diagnostics, CLI, Configuration, Failure isolation, Health states, Logging, Phase 18 — Production reliability and monitoring (+6 more)

### Community 122 - "Multi-dimensional role classification"
Cohesion: 0.29
Nodes (6): Cache, Contract, Function versus interaction, Multi-dimensional role classification, Non-goals, What the classifier reads

### Community 123 - "6. What is sent to you"
Cohesion: 0.40
Nodes (5): 6.1 Who is eligible, 6.2 The shortlist rule, 6.3 Each line, 6.4 If brief mode is turned off, 6. What is sent to you

### Community 124 - "dataclasses"
Cohesion: 0.13
Nodes (13): Data model (core/db.py), Status lifecycle, AlertSummary, build_alert_caption(), _send_one(), send_pending_alerts(), get_unsent_alerts(), get_unsent_prep_pack_jobs() (+5 more)

### Community 125 - "_input_hash"
Cohesion: 0.48
Nodes (5): _as_utc(), _freshness_day(), _input_hash(), _iso(), posted()

### Community 127 - "Job"
Cohesion: 0.08
Nodes (30): _dedupe(), _fit_lines(), _load_canonical_shortlist(), _mark_sent(), _notify_empty(), PrepSummary, render_job_card(), render_shortlist() (+22 more)

### Community 128 - "upsert_job"
Cohesion: 0.11
Nodes (18): _stamp_role_family_weight(), Tier, upsert_job(), compute_tier(), is_dream_company(), _posting(), ScoreOnlyClient, test_company_blocklist_does_not_match_lookalikes() (+10 more)

### Community 129 - "test_role_weights.py"
Cohesion: 0.13
Nodes (21): get_role_family_weight(), load_role_family_weights(), _validate(), weight_for_subfamily(), test_feedback_config_keeps_priority_integration_off(), _job(), _posting(), test_company_and_vector_are_not_weight_inputs() (+13 more)

### Community 130 - "clients.py"
Cohesion: 0.06
Nodes (29): _add_measured(), _add_token(), AnthropicClient, _attempt(), _Attempt, _blank_bucket(), _chat_usage(), _embedding_usage() (+21 more)

### Community 131 - "service.py"
Cohesion: 0.13
Nodes (4): configure_logging(), run_service(), test_run_service_stops_without_poller(), test_run_service_with_poller_respects_stop()

### Community 132 - "pathlib"
Cohesion: 0.10
Nodes (18): new_page(), action_delay_bounds(), human_delay(), type_like_human(), typing_delay_bounds(), click_by_role(), click_next(), _collect_labeled_fields() (+10 more)

### Community 133 - "normalize_company_name"
Cohesion: 0.29
Nodes (6): canonical_company_name(), normalize_company_name(), _without_trailing_suffix(), test_legal_suffixes_do_not_collapse_distinct_names(), test_normalization_is_deterministic(), test_version_and_normalization_stay_explicit()

### Community 134 - "test_doctor.py"
Cohesion: 0.22
Nodes (11): _build_doctor_report(), _cmd_doctor(), _count_jobs(), _print_doctor_report(), _unwrap(), _job(), test_doctor_cooldown(), test_doctor_empty_db() (+3 more)

### Community 135 - "Source"
Cohesion: 0.09
Nodes (31): get_job_by_source_id(), Source, _dedupe(), _persist_postings(), hash_fallback(), RawPosting, to_job(), test_to_job_stamps_workday_tenant_from_linkedin_url() (+23 more)

### Community 136 - "extract_company_facts"
Cohesion: 0.29
Nodes (5): extract_company_facts(), merge_company_facts(), test_extractor_keeps_unstated_facts_null(), test_merge_company_facts_keeps_omitted_fields(), test_prestige_language_is_not_a_fact()

### Community 137 - "Career Intelligence"
Cohesion: 0.33
Nodes (5): Cache, Career Intelligence, Dimensions, Failures, Overall score

### Community 138 - "OpenAI usage summary"
Cohesion: 0.40
Nodes (4): Bounded trial, Comparing with the OpenAI dashboard, OpenAI usage summary, What the line contains

### Community 139 - "Phase 9 visa and eligibility"
Cohesion: 0.29
Nodes (6): Education, graduation, experience, location, dates, Phase 9 visa and eligibility, Sponsorship, citizenship, and clearance, States, What the profile contributes, What this phase does not do

### Community 140 - "Phase 4 JD ingestion"
Cohesion: 0.40
Nodes (4): Hash and upsert, Limits, Normalization, Phase 4 JD ingestion

### Community 141 - "Phase 7 role-family weighting"
Cohesion: 0.22
Nodes (8): Canonical portfolio, Configuration, Four different questions, Phase 7 role-family weighting, Unknown classification, What is stored, What this phase does not do, Where the family comes from

### Community 147 - "re"
Cohesion: 0.12
Nodes (16): _city_state(), company_matches(), company_tokens(), contains_phrase(), is_remote_location(), location_matches(), normalize_text(), truncate_middle() (+8 more)

### Community 153 - "is_pace_blocker"
Cohesion: 0.50
Nodes (3): is_pace_blocker(), test_pace_hints_ignore_mfa_and_empty(), test_pace_hints_match()

### Community 160 - "baseline.py"
Cohesion: 0.15
Nodes (9): get_jobs_for_role(), build_baseline_resume_data(), _normalize(), _slugify_role(), _synthetic_job_for_role(), FakeClient, Path_exists(), test_build_role_baseline_persists() (+1 more)

## Knowledge Gaps
- **184 isolated node(s):** `ScrapeSummary`, `_Sites`, `_FakeAio`, `Method and time`, `States and outcomes` (+179 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 1254 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **16 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Job` connect `Job` to `job_identity.py`, `upsert_job`, `Profile`, `structured_jd.py`, `pathlib`, `handlers.py`, `test_doctor.py`, `Source`, `test_feedback.py`, `test_career_intelligence.py`, `test_openai_run_usage.py`, `test_role_weights.py`, `answers.py`, `eligibility.py`, `ingest.py`, `apply_pending`, `re`, `test_structured_jd.py`, `test_resume.py`, `FakeTransport`, `diff.py`, `test_company_intelligence.py`, `test_ingest_resilience.py`, `get_job_by_id`, `baseline.py`, `LLMClient`, `test_eligibility.py`, `test_calibration.py`, `test_monitoring.py`, `test_phase13_shortlist.py`, `Status`, `profile.py`, `compiler.py`, `skills.py`, `test_workload_limits.py`, `test_application_portfolio.py`, `test_priority.py`, `priority.py`, `main.py`, `session_scope`, `test_false_negative.py`, `score_pending`, `OpenAIClient`, `tracker.py`, `review.py`, `migrate_to_neon.py`, `db.py`, `prerank_score`, `benchmark/engine.py`, `test_role_classify.py`, `runner.py`, `telegram.py`, `test_pacing.py`, `typing`, `company_intelligence.py`, `feedback.py`, `scorer/engine.py`, `test_application_deadline.py`, `calibration.py`, `test_cover_letter.py`, `json`, `calculate_priority`, `test_prep_builder.py`, `get_health_report`, `filters.py`, `dataclasses`, `_input_hash`?**
  _High betweenness centrality (0.150) - this node is a cross-community bridge._
- **Are the 179 inferred relationships involving `Job` (e.g. with `Data model (core/db.py)` and `AnswerResolver`) actually correct?**
  _`Job` has 179 INFERRED edges - model-reasoned connections that need verification._
- **What connects `ScrapeSummary`, `_Sites`, `_FakeAio` to the rest of the system?**
  _184 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `job_identity.py` be split into smaller, more focused modules?**
  _Cohesion score 0.14855072463768115 - nodes in this community are weakly interconnected._
- **Why does `get_settings()` connect `get_settings` to `upsert_job`, `clients.py`, `service.py`, `pathlib`, `call_with_resilience`, `test_doctor.py`, `test_career_intelligence.py`, `test_recruiting_universe.py`, `test_openai_run_usage.py`, `evaluate`, `workday_rest.py`, `conftest.py`, `textclean.py`, `answers.py`, `ingest.py`, `re`, `pipeline.py`, `TelegramClient`, `test_resume.py`, `scheduler.py`, `FakeTransport`, `diff.py`, `classify_role`, `pacing.py`, `test_ingest_resilience.py`, `baseline.py`, `LLMClient`, `test_eligibility.py`, `test_company_intelligence_v2.py`, `pytest`, `test_monitoring.py`, `test_phase13_shortlist.py`, `profile.py`, `compiler.py`, `test_phase0_baseline.py`, `skills.py`, `test_workload_limits.py`, `role_classify.py`, `Settings`, `test_application_portfolio.py`, `main.py`, `session_scope`, `test_false_negative.py`, `score_pending`, `migrate_to_neon.py`, `test_trial_workflow.py`, `db.py`, `linkedin_jobspy.py`, `benchmark/engine.py`, `test_webhook.py`, `vault.py`, `runner.py`, `telegram.py`, `test_pacing.py`, `test_llm_provider.py`, `typing`, `test_openai_request_gate.py`, `scorer/engine.py`, `json`, `test_prep_builder.py`, `filters.py`, `webhook.py`, `OpenAIRequestLedger`, `Job`?**
  _High betweenness centrality (0.091) - this node is a cross-community bridge._
- **Are the 264 inferred relationships involving `Profile` (e.g. with `AnswerResolver` and `_latest_education()`) actually correct?**
  _`Profile` has 264 INFERRED edges - model-reasoned connections that need verification._
- **Should `structured_jd.py` be split into smaller, more focused modules?**
  _Cohesion score 0.12513842746400886 - nodes in this community are weakly interconnected._