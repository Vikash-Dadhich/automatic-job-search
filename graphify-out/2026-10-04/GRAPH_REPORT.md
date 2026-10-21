# Graph Report - Automatic job search  (2026-10-04)

## Corpus Check
- 210 files · ~175,135 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 12 file(s) not represented in the graph (top: (none) 8, .typ 2, .example 1)

## Summary
- 3604 nodes · 12525 edges · 140 communities (127 shown, 13 thin omitted)
- Extraction: 89% EXTRACTED · 11% INFERRED · 0% AMBIGUOUS · INFERRED: 1342 edges (avg confidence: 0.94)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `2b5e462c`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- test_outcomes.py
- structured_jd.py
- AsyncSession
- Profile
- get_health_report
- clients.py
- test_career_intelligence.py
- test_fit.py
- test_discovery.py
- benchmark/engine.py
- evaluate
- workday_rest.py
- conftest.py
- textclean.py
- discovery_recall.py
- get_settings
- eligibility.py
- test_discovery_observability.py
- test_resume.py
- test_structured_jd.py
- pipeline.py
- Any
- classify_role
- test_apply_url.py
- targets.py
- diff.py
- test_company_intelligence.py
- test_application_deadline.py
- test_pacing.py
- test_pipeline_order_and_aggregation
- feedback.py
- re
- pathlib
- company_intelligence.py
- _find_cross_source_job
- run_pipeline
- Remaining Manual Setup
- _input_hash
- ingest.py
- test_phase13_shortlist.py
- vector_recovery.py
- test_prep_builder.py
- workday.py
- compiler.py
- test_calibration.py
- typing
- test_answers.py
- apply_pending
- TelegramClient
- Settings
- test_pipeline_apply_receives_only_persisted_ids
- test_priority.py
- Phase 5 role classification
- test_company_intelligence_v2.py
- baseline.py
- priority.py
- main.py
- test_vector_recovery.py
- Benchmark — Product Manager @ T-Mobile
- monitoring.py
- test_feedback.py
- filters.py
- tracker.py
- Job
- test_webhook.py
- migrate_to_neon.py
- discovery_experiment.py
- AGENTS.md
- prep.py
- job-agent
- prerank.py
- telegram.py
- linkedin_jobspy.py
- phase10-false-negative-protection.md
- settings.py
- Phase 1 discovery architecture
- scorer/__init__.py
- Phase 18 — Production reliability and monitoring
- test_robustness.py
- Priority 2.0
- WorkdaySubmitter
- test_doctor.py
- session_scope
- role_classify.py
- Discovery recall benchmark
- LLMClient
- score
- pytest
- json
- Phase 8 company intelligence
- test_llm_provider.py
- correction1-recruiting-universe.md
- test_scorer.py
- extract_company_facts
- outreach.py
- LLMBillingError
- Phase 16 feedback learning
- scorer/engine.py
- Source
- runner.py
- calibration.py
- handlers.py
- Phase 15 application tracker
- test_monitoring.py
- answers.py
- 3. Hard filters (before any model)
- linkedin_people.py
- alerts.py
- Job Agent
- calculate_priority
- Phase 12 priority ranking
- test_vector_gate.py
- run_discovery_experiment
- application_portfolio.py
- Company intelligence 2.0
- test_discovery_experiment.py
- phase17-calibration-benchmark.md
- Structured JD intelligence
- extract_company_signals
- vector-recovery.md
- test_application_portfolio.py
- Multi-dimensional role classification
- FrozenPhrase
- db.py
- test_cover_letter.py
- scheduler.py
- get_recently_applied_companies
- ApplyResult
- test_role_weights.py
- Any
- normalize_database_url
- sort_by_priority
- normalize_company_name
- _company_key
- FakeClient
- test_workday_locators.py
- _Spy
- Phase 7 role-family weighting

## God Nodes (most connected - your core abstractions)
1. `Job` - 374 edges
2. `Profile` - 331 edges
3. `session_scope()` - 306 edges
4. `Status` - 246 edges
5. `Source` - 212 edges
6. `get_settings()` - 166 edges
7. `get_job_by_id()` - 161 edges
8. `upsert_job()` - 140 edges
9. `TelegramClient` - 92 edges
10. `init_db()` - 87 edges

## Surprising Connections (you probably didn't know these)
- `What still needs the user (before live runs)` --references--> `save_session()`  [INFERRED]
  AGENTS.md → automation/login.py
- `Deploy with Docker` --references--> `save_session()`  [INFERRED]
  README.md → automation/login.py
- `Checklist (your remaining work)` --references--> `save_session()`  [INFERRED]
  SETUP.md → automation/login.py
- `Run review bot (Step 6)` --references--> `send_pending_alerts()`  [INFERRED]
  README.md → bot/alerts.py
- `What the profile contributes` --references--> `Profile`  [INFERRED]
  docs/phase9-visa-eligibility.md → config/profile.py

## Import Cycles
- None detected.

## Communities (140 total, 13 thin omitted)

### Community 0 - "test_outcomes.py"
Cohesion: 0.11
Nodes (24): build_outcome_keyboard(), button(), outcome_label(), outcome_message_text(), OutcomePromptSummary, send_outcome_prompt(), send_pending_outcome_prompts(), decode_outcome_callback() (+16 more)

### Community 1 - "structured_jd.py"
Cohesion: 0.13
Nodes (37): _authorization(), AuthorizationEvidence, _availability(), _clause_at(), _clauses(), _clip(), _degree_state(), _domain() (+29 more)

### Community 2 - "AsyncSession"
Cohesion: 0.18
Nodes (11): CalibrationMetric, CalibrationRun, _drop_structured_jd(), get_application_by_id(), get_calibration_metrics(), get_calibration_run(), get_pending_suggestions_for_job(), get_session_factory() (+3 more)

### Community 3 - "Profile"
Cohesion: 0.12
Nodes (25): Profile, assign_eligibility(), attach_eligibility(), eligibility_column_types(), eligibility_is_current(), evaluate_eligibility(), profile_eligibility_hash(), _job() (+17 more)

### Community 4 - "get_health_report"
Cohesion: 0.16
Nodes (13): _as_utc(), PipelineRun, _brief(), format_health_report(), get_health_report(), _recent_failures(), _repeated_failures(), _run_view() (+5 more)

### Community 5 - "clients.py"
Cohesion: 0.10
Nodes (18): _backoff_delay(), call_with_resilience(), is_permanent_account_error(), is_transient(), LLMError, _lower_thinking(), _status_code(), suggested_delay() (+10 more)

### Community 6 - "test_career_intelligence.py"
Cohesion: 0.08
Nodes (51): CareerIntelligence, _apply_reading(), assess_career(), attach_career_intelligence(), career_input_hash(), CareerReading, _clause(), _clip() (+43 more)

### Community 7 - "test_fit.py"
Cohesion: 0.11
Nodes (33): build_fit_system_blocks(), build_fit_user(), cached_fit(), _Dimension, evaluate_fit(), fit_context_block(), fit_is_current(), FitDecision (+25 more)

### Community 8 - "test_discovery.py"
Cohesion: 0.08
Nodes (34): allocate_units(), AllocItem, build_discovery_plan(), DiscoveryConfig, DiscoverySource, _enabled_queries(), enabled_query_texts(), _family_spillover() (+26 more)

### Community 9 - "benchmark/engine.py"
Cohesion: 0.12
Nodes (17): BenchmarkReport, BenchmarkSummary, build_benchmark(), _derive_seniority(), DimensionScore, _education_rank(), _median(), _norm() (+9 more)

### Community 10 - "evaluate"
Cohesion: 0.10
Nodes (34): evaluate(), sponsorship_signal(), _posting(), test_clearance_regex_pattern(), test_exclude_clearance_keyword(), test_exclude_high_yoe_requirement(), test_exclude_off_target_location(), test_exclude_seniority_title() (+26 more)

### Community 11 - "workday_rest.py"
Cohesion: 0.07
Nodes (25): WorkdayParts, WorkdayTenant, _as_text(), _company_name(), _one(), _fetch_detail(), _fetch_listing_page(), fetch_workday() (+17 more)

### Community 12 - "conftest.py"
Cohesion: 0.21
Nodes (4): _disable_apply_pacing(), _disable_vector_gate(), _internship_only_off(), tmp_db()

### Community 13 - "textclean.py"
Cohesion: 0.08
Nodes (29): Cache, Career Intelligence, Dimensions, Failures, Overall score, Flow, Hash and upsert, Limits (+21 more)

### Community 14 - "discovery_recall.py"
Cohesion: 0.14
Nodes (29): _verified_benchmark_hits(), BenchmarkCase, _bucket(), _case(), case_is_captured(), eligible(), _identity_conflict(), load_benchmark() (+21 more)

### Community 15 - "get_settings"
Cohesion: 0.16
Nodes (7): launch_context(), _new_context(), new_page(), save_storage_state(), save_session(), get_settings(), save_linkedin_session()

### Community 16 - "eligibility.py"
Cohesion: 0.13
Nodes (28): _ask_model(), _citizenship(), _clearance(), _current_student(), _dates(), _decision_from_job(), _dim(), DimensionResult (+20 more)

### Community 17 - "test_discovery_observability.py"
Cohesion: 0.11
Nodes (30): build_coverage_report(), add_planned(), group_for(), GroupMetrics, observe_search(), _planned_slots(), QueryMetrics, result_identity() (+22 more)

### Community 18 - "test_resume.py"
Cohesion: 0.13
Nodes (15): build_resume_data(), extract_job_terms(), _grounded_summary(), RankedBullet, reorder_skills(), score_bullet(), select_bullets(), SelectedExperience (+7 more)

### Community 19 - "test_structured_jd.py"
Cohesion: 0.11
Nodes (19): StructuredJobDescription, attach_structured_jd(), extract_structured_jd(), get_structured_jd(), structured_jd_is_current(), _areas(), _job(), test_changed_upsert_drops_the_old_reading() (+11 more)

### Community 20 - "pipeline.py"
Cohesion: 0.10
Nodes (19): stage_counters(), _allocated_ids(), _generate_suggestions_stage(), _note_skipped(), PipelineSummary, _portfolio_stage(), _prepare_shortlisted_resumes(), _run_opened_pipeline() (+11 more)

### Community 22 - "classify_role"
Cohesion: 0.11
Nodes (25): classification_is_current(), classify_role(), _apply_role_classification(), _FakeClient, _jd(), test_classifier_version_bump_invalidates_phase5_v1(), test_invalid_confidence_is_unknown(), test_invalid_model_output_falls_back_to_unknown() (+17 more)

### Community 23 - "test_apply_url.py"
Cohesion: 0.22
Nodes (11): ApplyKind, classify_apply_url(), _host(), is_automateable_apply_url(), is_workday_url(), workday_parts(), _cmd_list_apply(), test_classify_company_site() (+3 more)

### Community 24 - "targets.py"
Cohesion: 0.09
Nodes (14): reload_profile(), load_targets(), _load_yaml(), reload_targets(), SearchConfig, Targets, test_load_targets_defaults(), test_parse_cxs_api_path() (+6 more)

### Community 25 - "diff.py"
Cohesion: 0.08
Nodes (35): apply_decided_suggestions(), decide_suggestion(), _format_card(), send_pending_suggestions(), _suggestion_keyboard(), SuggestSummary, get_role_baseline_by_id(), get_skill_suggestion_by_id() (+27 more)

### Community 26 - "test_company_intelligence.py"
Cohesion: 0.20
Nodes (18): attach_company_intelligence(), trustworthy_company_source(), FakeProvider, _job(), _posting(), test_ambiguous_names_stay_separate(), test_company_facts_do_not_change_scoring_signals(), test_company_sources_accumulate_and_a_failed_refresh_keeps_them() (+10 more)

### Community 27 - "test_application_deadline.py"
Cohesion: 0.09
Nodes (28): ApplicationDeadline, _clip(), empty_application_deadline(), _excluded(), extract_application_deadline(), _from_match(), _named(), _parse_date() (+20 more)

### Community 28 - "test_pacing.py"
Cohesion: 0.12
Nodes (26): acquire(), AcquireResult, _clamp_multiplier(), _clock(), end_of_local_day(), gap_seconds(), note_pace_block(), note_success() (+18 more)

### Community 29 - "test_pipeline_order_and_aggregation"
Cohesion: 0.12
Nodes (17): _FakeSummary, test_pipeline_order_and_aggregation(), fake_alerts(), fake_apply(), fake_ingestion(), fake_outcomes(), fake_prep(), fake_resume() (+9 more)

### Community 30 - "feedback.py"
Cohesion: 0.14
Nodes (25): FeedbackRun, FeedbackSignal, get_feedback_run(), get_feedback_signals(), get_latest_feedback_run(), save_feedback_run(), _adjustment(), _band() (+17 more)

### Community 31 - "re"
Cohesion: 0.11
Nodes (20): locations_agree(), locations_conflict(), _city_state(), company_matches(), company_tokens(), contains_phrase(), is_remote_location(), location_matches() (+12 more)

### Community 32 - "pathlib"
Cohesion: 0.16
Nodes (3): run_service(), test_run_service_stops_without_poller(), test_run_service_with_poller_respects_stop()

### Community 33 - "company_intelligence.py"
Cohesion: 0.13
Nodes (20): CompanyIntelligence, _accumulate_sources(), _apply_context(), _apply_facts(), _by_key(), _clear_facts(), _confidence_for(), _context_from() (+12 more)

### Community 34 - "_find_cross_source_job"
Cohesion: 0.17
Nodes (10): _find_cross_source_job(), canonicalize_job_url(), _is_tracking_param(), normalize_title(), same_employer(), same_posting_url(), strong_field_match(), url_identifies_posting() (+2 more)

### Community 35 - "run_pipeline"
Cohesion: 0.12
Nodes (12): Architecture, Pipeline run lifecycle, run_pipeline(), test_health_command_prints_no_secrets(), test_health_reports_database_failure(), test_health_reports_invalid_configuration(), test_pipeline_failure_outside_a_stage_is_failed(), boom() (+4 more)

### Community 36 - "Remaining Manual Setup"
Cohesion: 0.08
Nodes (25): 2a. Find a Workday URL, 2b. Edit `config/targets.yaml`, 3a. Run the save-session helper, 3b. What you do in the browser, 4a. Discover jobs (LinkedIn / Indeed + any real Workday tenants), 4b. Score with Gemini, 4c. Attach your base resume to staged jobs, 4d. Send LinkedIn/Indeed application prep pack (Telegram) (+17 more)

### Community 37 - "_input_hash"
Cohesion: 0.43
Nodes (6): _as_utc(), freshness_component(), _freshness_day(), _input_hash(), _iso(), _structured_view()

### Community 38 - "ingest.py"
Cohesion: 0.08
Nodes (18): _stamp_role_family_weight(), HttpCompanyIntelProvider, CoverageReport, discovery_evidence(), fail_unrecorded(), _jsonable(), log_coverage(), SearchObservation (+10 more)

### Community 39 - "test_phase13_shortlist.py"
Cohesion: 0.09
Nodes (33): get_jobs_by_status(), apply_shortlist(), _close_enough(), _company_key(), _company_ok(), config_hash(), _diversify(), _family() (+25 more)

### Community 40 - "vector_recovery.py"
Cohesion: 0.18
Nodes (17): _compiled(), _confidence(), config_hash(), evaluate_recovery(), _family_group(), load_recovery_config(), _mba_program(), _names() (+9 more)

### Community 41 - "test_prep_builder.py"
Cohesion: 0.12
Nodes (14): _answer_item(), build_job_section(), compile_prep_pdf(), generate_prep_pack(), PrepPackResult, render_markdown(), FakeClient, _job() (+6 more)

### Community 42 - "workday.py"
Cohesion: 0.10
Nodes (18): action_delay_bounds(), human_delay(), type_like_human(), typing_delay_bounds(), click_by_role(), click_next(), _collect_labeled_fields(), detect_blocker() (+10 more)

### Community 43 - "compiler.py"
Cohesion: 0.10
Nodes (23): load_profile(), apply_fit_caps(), _baseline_pdf_for_job(), clean_name(), compile_for_job(), compile_pending(), compile_resume(), compile_resume_data() (+15 more)

### Community 44 - "test_calibration.py"
Cohesion: 0.22
Nodes (20): brier_score(), build_calibration(), CalibrationFold, CalibrationReport, load_calibration_config(), run_calibration(), load_feedback_config(), _calibration() (+12 more)

### Community 45 - "typing"
Cohesion: 0.09
Nodes (21): aggregate_role_skills(), AggregatedSkill, _categorize(), extract_top_skills(), extract_top_skills_deterministic(), JdSkill, parse_skills_json(), _repair_truncated_json_array() (+13 more)

### Community 46 - "test_answers.py"
Cohesion: 0.10
Nodes (16): AnswerResolver, one(), answers_to_payload(), AnswerSource, ResolvedAnswer, WorkdayApplicator, FakeAnswerClient, test_answers_to_payload() (+8 more)

### Community 47 - "apply_pending"
Cohesion: 0.21
Nodes (24): apply_pending(), FakeApplicator, _script_reloads(), _seed_job(), test_allocation_removed_before_execution_is_skipped(), test_apply_linkedin_with_workday_url(), test_apply_pending_blocker(), test_apply_pending_empty() (+16 more)

### Community 48 - "TelegramClient"
Cohesion: 0.11
Nodes (26): send_prep_pack(), TelegramClient, test_career_reading_does_not_change_telegram_order(), test_run_polling_max_iterations(), __init__(), FakeClient, test_send_prep_pack_empty(), test_send_prep_pack_marks_jobs() (+18 more)

### Community 50 - "test_pipeline_apply_receives_only_persisted_ids"
Cohesion: 0.14
Nodes (17): _NotStaged, test_allocation_does_not_rescore(), test_config_rejects_a_bool_cap(), test_mixed_persist_returns_only_the_saved_allocation(), skip_lost(), test_persisted_allocation_is_returned(), test_pipeline_applies_only_allocated_staged_jobs(), noop() (+9 more)

### Community 51 - "test_priority.py"
Cohesion: 0.17
Nodes (19): apply_priority(), load_priority_config(), priority_is_current(), role_family_component(), _job(), test_dream_company_is_only_a_configured_boost(), test_eligibility_unknown_is_not_ineligible(), test_fit_and_role_family_order_attention() (+11 more)

### Community 52 - "Phase 5 role classification"
Cohesion: 0.29
Nodes (6): Inputs, Limits, Output, Phase 5 role classification, Taxonomy, When it runs again

### Community 53 - "test_company_intelligence_v2.py"
Cohesion: 0.18
Nodes (9): CompanyIntelProvider, CompanyLookupResult, CompanySourceDocument, refresh_company_intelligence(), _one(), _Provider, _signals(), test_changed_page_replaces_that_source_and_keeps_another() (+1 more)

### Community 54 - "baseline.py"
Cohesion: 0.13
Nodes (13): get_jobs_for_role(), get_role_baseline_by_role(), build_baseline_resume_data(), build_role_baseline(), _normalize(), _slugify_role(), _synthetic_job_for_role(), RoleSkillProfile (+5 more)

### Community 55 - "priority.py"
Cohesion: 0.13
Nodes (22): _combine(), company_domain_component(), _company_signals(), _components(), dream_company_component(), eligibility_component(), _explicit_sections(), fit_component() (+14 more)

### Community 56 - "main.py"
Cohesion: 0.09
Nodes (26): configure_logging(), build_parser(), _cmd_benchmark(), _cmd_build_baseline(), _cmd_health(), _cmd_poll(), _cmd_prep_pack(), _cmd_run_once() (+18 more)

### Community 57 - "test_vector_recovery.py"
Cohesion: 0.29
Nodes (27): _enable(), _seed(), _assert_no_profile_text(), _doc(), _exclude_company(), _score(), _stamp(), _store_doc() (+19 more)

### Community 58 - "Benchmark — Product Manager @ T-Mobile"
Cohesion: 0.33
Nodes (5): Benchmark — Product Manager @ T-Mobile, Dimensions, Gaps, Recommendations, Strengths

### Community 59 - "monitoring.py"
Cohesion: 0.20
Nodes (17): PipelineStageRun, close_stage_run(), count_stale_jobs(), list_stage_runs(), load_monitoring_config(), _moment(), monitoring_config_hash(), open_stage_run() (+9 more)

### Community 60 - "test_feedback.py"
Cohesion: 0.15
Nodes (17): Application, ApplicationEvent, get_application_events(), list_events_for_applications(), list_jobs_by_ids(), list_submitted_applications(), load_feedback_cases(), shrink_rate() (+9 more)

### Community 61 - "filters.py"
Cohesion: 0.10
Nodes (18): citizenship_restriction(), _clearance_clauses(), clearance_requirement(), evaluate_job(), FilterResult, has_internship_signal(), _haystack(), _mandatory_years() (+10 more)

### Community 62 - "tracker.py"
Cohesion: 0.19
Nodes (15): _add_event(), application_method(), backfill_submitted_applications(), _event_exists(), _get_or_create(), record_manual_review(), record_outcome(), record_prefill() (+7 more)

### Community 63 - "Job"
Cohesion: 0.07
Nodes (44): Data model (core/db.py), Status lifecycle, build_keyboard(), build_review_caption(), format_answers_message(), format_cover_letter_message(), ReviewSummary, _send_one() (+36 more)

### Community 64 - "test_webhook.py"
Cohesion: 0.26
Nodes (5): client(), test_health(), test_webhook_ignored_without_callback(), test_webhook_rejects_bad_secret(), test_webhook_routes_callback()

### Community 65 - "migrate_to_neon.py"
Cohesion: 0.22
Nodes (6): _cell(), _copy_table(), _counts(), main(), _reset_sequences(), _row()

### Community 66 - "discovery_experiment.py"
Cohesion: 0.20
Nodes (16): _baseline_slot_reason(), _classify_incremental(), _execute(), _execute_phrase(), _expected_slots(), format_summary(), _from_observation(), _identities() (+8 more)

### Community 67 - "AGENTS.md"
Cohesion: 0.11
Nodes (10): Build order and status, Coding conventions, Commands, Confirmed product decisions, Project, Repository layout, Scoring specifics (Step 3), What still needs the user (before live runs) (+2 more)

### Community 68 - "prep.py"
Cohesion: 0.09
Nodes (25): _dedupe(), _fit_lines(), _load_canonical_shortlist(), _mark_sent(), _notify_empty(), PrepSummary, render_job_card(), render_shortlist() (+17 more)

### Community 71 - "prerank.py"
Cohesion: 0.19
Nodes (12): prerank_jobs(), prerank_score(), _source_weight(), _job(), test_dream_company_boost(), test_intern_title_outranks_fulltime(), test_new_source_scored_without_error(), test_prerank_jobs_empty() (+4 more)

### Community 72 - "telegram.py"
Cohesion: 0.13
Nodes (19): SubmitResult, decode_callback(), encode_callback(), ReviewAction, _should_retry_telegram(), _callback_update(), FakeSubmitter, _seed_pending() (+11 more)

### Community 73 - "linkedin_jobspy.py"
Cohesion: 0.14
Nodes (14): PlannedSearch, _dataframe_to_postings(), _effective_windows(), _explicit_company_url(), _external_id(), fetch_linkedin_indeed(), _google_search_term(), _jobspy_observations() (+6 more)

### Community 75 - "settings.py"
Cohesion: 0.12
Nodes (13): CredentialsFile, get_tenant_credentials(), has_saved_session(), load_credentials(), _load_yaml(), reload_credentials(), session_state_path(), TenantCredentials (+5 more)

### Community 76 - "Phase 1 discovery architecture"
Cohesion: 0.11
Nodes (16): 40/40/15/5 priority model, Current problem, New architecture, Phase 1 discovery architecture, Provenance, Purpose, Role families, Search allocation (+8 more)

### Community 78 - "Phase 18 — Production reliability and monitoring"
Cohesion: 0.15
Nodes (12): Backlog diagnostics, CLI, Configuration, Failure isolation, Health states, Logging, Phase 18 — Production reliability and monitoring, Purpose (+4 more)

### Community 79 - "test_robustness.py"
Cohesion: 0.09
Nodes (20): Candidate baseline, Discovery baseline, Local versus production, Phase 0 baseline, Production baseline, Scoring baseline, Sponsorship behavior locked by tests, Tests (+12 more)

### Community 80 - "Priority 2.0"
Cohesion: 0.29
Nodes (6): Freshness, dream company, and workflow, Hash, Priority 2.0, Program and domain evidence, Role alignment, Weights

### Community 81 - "WorkdaySubmitter"
Cohesion: 0.18
Nodes (7): SessionMissingError, WorkdaySubmitter, test_submit_generic_exception(), test_submit_missing_url(), test_submit_session_missing(), boom_launch(), test_submit_unparseable_without_tenant()

### Community 82 - "test_doctor.py"
Cohesion: 0.22
Nodes (11): _build_doctor_report(), _cmd_doctor(), _count_jobs(), _print_doctor_report(), _unwrap(), _job(), test_doctor_cooldown(), test_doctor_empty_db() (+3 more)

### Community 83 - "session_scope"
Cohesion: 0.21
Nodes (19): _reload_job(), application_history(), get_application_for_job(), get_job_by_id(), session_scope(), _refresh_recovery_reject(), _reopen_job(), _reopen_recovered() (+11 more)

### Community 84 - "role_classify.py"
Cohesion: 0.15
Nodes (18): _clause_containing(), _clip_items(), _deterministic(), _is_interaction(), _item_text(), _ModelLabel, _parse_model(), _phrase_hits() (+10 more)

### Community 85 - "Discovery recall benchmark"
Cohesion: 0.10
Nodes (17): Discovery recall benchmark, Label corrections on 2026-10-04, Limits, Matching, Reproduce, What is checked in, Discovery run observability, Recency (+9 more)

### Community 86 - "LLMClient"
Cohesion: 0.16
Nodes (5): LLMClient, _attach_priority(), _JobOutcome, _priority_evidence(), Scorer

### Community 87 - "score"
Cohesion: 0.12
Nodes (14): Dimensions, Not in this phase, Output, Phase 6 candidate fit, When the model is not called, Four different questions, Cache and storage, Education, graduation, experience, location, dates (+6 more)

### Community 88 - "pytest"
Cohesion: 0.12
Nodes (30): Address, Education, Exclusions, Experience, Identity, Preferences, WorkAuthorization, _make_base_pdf() (+22 more)

### Community 89 - "json"
Cohesion: 0.15
Nodes (12): effective_baseline(), effective_config_hash(), fingerprint_profile(), profile_hash(), public_config(), write_effective_baseline(), calibration_config_hash(), feedback_config_hash() (+4 more)

### Community 90 - "Phase 8 company intelligence"
Cohesion: 0.29
Nodes (6): Names and reuse, Phase 8 company intelligence, Schema, Sources, What it is, What this phase does not change

### Community 91 - "test_llm_provider.py"
Cohesion: 0.09
Nodes (20): Tech stack, build_llm_client(), OpenAIClient, _FakeAio, _FakeAsyncModels, _FakeCandidate, _FakeGenaiClient, _FakeGenerateResponse (+12 more)

### Community 93 - "test_scorer.py"
Cohesion: 0.09
Nodes (20): approx_tokens(), cache_block(), compact_json_dumps(), minify_job(), _extract_json_object(), parse_score(), build_outreach_user(), build_scoring_system_blocks() (+12 more)

### Community 94 - "extract_company_facts"
Cohesion: 0.17
Nodes (8): extract_company_facts(), merge_company_facts(), test_extractor_keeps_unstated_facts_null(), test_http_provider_handles_timeout_and_malformed_pages(), ok(), test_http_provider_keeps_the_caller_source_type(), test_merge_company_facts_keeps_omitted_fields(), test_prestige_language_is_not_a_fact()

### Community 95 - "outreach.py"
Cohesion: 0.17
Nodes (9): _fallback_cover_letter(), generate_cover_letter(), run_one(), contains_banned(), _fallback_outreach(), generate_outreach(), strip_banned_sentences(), build_cover_letter_user() (+1 more)

### Community 96 - "LLMBillingError"
Cohesion: 0.27
Nodes (4): LLM client layer (`scorer/clients.py`), LLMBillingError, OpenAIEmbedder, _vectors_from_response()

### Community 97 - "Phase 16 feedback learning"
Cohesion: 0.33
Nodes (5): Evidence and shrinkage, Phase 16 feedback learning, Rates, Segments, Who is counted

### Community 98 - "scorer/engine.py"
Cohesion: 0.07
Nodes (27): build_embedder(), _cache_path(), clears_threshold(), cosine(), Embedder, jd_vector(), load_profile_embedding(), save_profile_embedding() (+19 more)

### Community 99 - "Source"
Cohesion: 0.10
Nodes (34): get_job_by_source_id(), Source, hash_fallback(), RawPosting, to_job(), test_to_job_stamps_workday_tenant_from_linkedin_url(), test_company_enrichment_failure_does_not_stop_ingestion(), one_posting() (+26 more)

### Community 100 - "runner.py"
Cohesion: 0.12
Nodes (10): is_pace_blocker(), ApplyRunner, ApplySummary, _eligible(), _ensure_tenant(), _log_explicit_skip(), _ready_for_explicit_apply(), Applicator (+2 more)

### Community 101 - "calibration.py"
Cohesion: 0.16
Nodes (27): _append_buckets(), _append_short_target(), _append_slice(), _append_target_metrics(), _append_topk(), _bucket_name(), CalibrationMetricRow, _direction() (+19 more)

### Community 102 - "handlers.py"
Cohesion: 0.08
Nodes (17): _decision_caption(), handle_callback(), handle_message(), _handle_outcome_callback(), _handle_suggest_callback(), _safe_answer(), process_updates(), run_polling() (+9 more)

### Community 103 - "Phase 15 application tracker"
Cohesion: 0.33
Nodes (5): Method and time, Phase 15 application tracker, States and outcomes, What this is not, When a row is created

### Community 104 - "test_monitoring.py"
Cohesion: 0.21
Nodes (15): close_pipeline_run(), interrupt_stale_runs(), list_pipeline_runs(), open_pipeline_run(), _safe_open_run(), _job(), test_a_new_run_does_not_duplicate_applications(), test_backlog_and_stale_jobs() (+7 more)

### Community 105 - "answers.py"
Cohesion: 0.15
Nodes (10): _discovery_channel(), is_open_ended(), _latest_education(), _matches(), needs_human_review(), _norm(), resolve_deterministic(), _split_name() (+2 more)

### Community 106 - "3. Hard filters (before any model)"
Cohesion: 0.04
Nodes (44): 10. File map, 1. What a run is, 2.1 Search terms, 2.2 Sites and the exact JobSpy arguments, 2.3 How each site treats "posted in the last 36 hours", 2.4 What is kept from a JobSpy row, 2.5 Workday, separately from LinkedIn, 2.6 Save and dedupe (+36 more)

### Community 107 - "linkedin_people.py"
Cohesion: 0.07
Nodes (26): auto_discover_peers(), _crawl(), BlockerError, build_people_search_url(), _detect_blocker(), discover_peers(), extract_profile_urls(), _heuristic_parse() (+18 more)

### Community 108 - "alerts.py"
Cohesion: 0.20
Nodes (10): AlertSummary, build_alert_caption(), _send_one(), send_pending_alerts(), get_unsent_alerts(), test_build_alert_caption(), test_scoring_error_does_not_alert(), test_send_pending_alerts_empty() (+2 more)

### Community 109 - "Job Agent"
Cohesion: 0.12
Nodes (15): Application prep packs (LinkedIn / Indeed), Deploy with Docker, Job Agent, Layout, LinkedIn peer benchmarking (optional, off by default), Resumes (Step 4), Run automation (Step 5), Run ingestion (Step 2) (+7 more)

### Community 110 - "calculate_priority"
Cohesion: 0.23
Nodes (14): calculate_priority(), _job(), _signal(), test_confidence_and_structured_evidence(), test_domains_are_capped_and_irrelevant_domains_add_nothing(), test_eligibility_order_and_unknown(), test_missing_jd_is_omitted_and_truncated_stays_lower(), test_priority_does_not_call_a_model() (+6 more)

### Community 111 - "Phase 12 priority ranking"
Cohesion: 0.50
Nodes (3): Components, Phase 12 priority ranking, Version

### Community 112 - "test_vector_gate.py"
Cohesion: 0.20
Nodes (19): job_embed_text(), profile_embed_text(), profile_hash(), score_pending(), FakeClient, FakeEmbedder, _map(), test_budget_skips_tail_after_a_reject() (+11 more)

### Community 113 - "run_discovery_experiment"
Cohesion: 0.15
Nodes (10): ExperimentRefusal, _persist(), run_discovery_experiment(), test_dry_run_does_not_fetch_or_write(), test_jobspy_exception_keeps_earlier_observations(), jobspy(), test_live_fake_attributes_only_the_requested_phrase(), jobspy() (+2 more)

### Community 114 - "application_portfolio.py"
Cohesion: 0.19
Nodes (12): Decisions, allocated_jobs(), apply_portfolio(), bucket_weights(), load_portfolio_config(), portfolio_config_hash(), PortfolioDecision, PortfolioSummary (+4 more)

### Community 115 - "Company intelligence 2.0"
Cohesion: 0.33
Nodes (5): Company intelligence 2.0, Company versus job, Sources and refresh, What it does not store, What it stores

### Community 116 - "test_discovery_experiment.py"
Cohesion: 0.24
Nodes (11): compare_arms(), _execution(), test_baseline_failure_blocks_confirmed_vocabulary(), test_comparison_math_keeps_failures_out_of_yield(), test_complete_baseline_confirms_treatment_only_candidate(), test_failed_hits_are_not_attributed(), test_incomplete_run_has_no_confirmed_vocabulary(), test_missing_baseline_slot_blocks_confirmed_vocabulary() (+3 more)

### Community 118 - "Structured JD intelligence"
Cohesion: 0.33
Nodes (5): Application deadline, Cache, Limits, Structured JD intelligence, What is stored

### Community 119 - "extract_company_signals"
Cohesion: 0.38
Nodes (5): _compact(), extract_company_signals(), _signal(), _snippet(), test_signals_are_explicit_and_multi_valued()

### Community 121 - "test_application_portfolio.py"
Cohesion: 0.29
Nodes (13): allocate_portfolio(), _job(), test_blank_companies_do_not_share_a_cap(), test_company_cap_is_per_run_and_suffix_aware(), test_cooldown_blocks_the_company_and_leaves_scores(), test_daily_capacity_defers_the_rest(), test_ignored_job_does_not_consume_a_slot(), test_ineligible_and_review_jobs_are_not_candidates() (+5 more)

### Community 122 - "Multi-dimensional role classification"
Cohesion: 0.29
Nodes (6): Cache, Contract, Function versus interaction, Multi-dimensional role classification, Non-goals, What the classifier reads

### Community 123 - "FrozenPhrase"
Cohesion: 0.18
Nodes (13): _baseline_slots(), build_schedule(), FrozenPhrase, load_arms(), load_frozen_catalog(), _payload(), _phrase_row(), _require_phrase() (+5 more)

### Community 124 - "db.py"
Cohesion: 0.10
Nodes (23): Testing conventions, _dialect_name(), _ensure_company_columns(), _ensure_job_columns(), _ensure_pipeline_stage_columns(), get_engine(), _incoming_description_unusable(), init_db() (+15 more)

### Community 125 - "test_cover_letter.py"
Cohesion: 0.23
Nodes (7): cap_cover_letter(), _job(), _ScriptedClient, test_cap_cover_letter_cuts_on_sentence_boundary(), test_cap_cover_letter_hard_slice_without_punctuation(), test_generate_cover_letter_falls_back_when_strip_empties(), test_generate_cover_letter_retries_banned_words()

### Community 126 - "scheduler.py"
Cohesion: 0.18
Nodes (8): build_scheduler(), parse_hhmm(), _noop(), test_build_scheduler_invalid_timezone(), test_build_scheduler_registers_jobs(), test_build_scheduler_skips_invalid_times(), test_parse_hhmm(), test_parse_hhmm_invalid()

### Community 127 - "get_recently_applied_companies"
Cohesion: 0.18
Nodes (8): _company_name(), get_recently_applied_companies(), Capacity, Phase 14 application portfolio, Pipeline, Role-family mix, What counts as a recent application, Who can be allocated

### Community 128 - "ApplyResult"
Cohesion: 0.29
Nodes (3): ApplyResult, BlockerError, _Blocker

### Community 129 - "test_role_weights.py"
Cohesion: 0.12
Nodes (19): _load_yaml(), get_role_family_weight(), load_role_family_weights(), _validate(), weight_for_subfamily(), test_feedback_config_keeps_priority_integration_off(), test_company_and_vector_are_not_weight_inputs(), test_discovery_capacity_stays_independent() (+11 more)

### Community 130 - "Any"
Cohesion: 0.11
Nodes (11): AnthropicClient, _attempt(), _as_int(), _finish_reason(), GeminiClient, _attempt(), _attempt(), system_blocks_to_text() (+3 more)

### Community 131 - "normalize_database_url"
Cohesion: 0.29
Nodes (6): _absolute_sqlite_url(), normalize_database_url(), test_normalize_drops_prisma_connection_limit(), test_normalize_keeps_sqlite(), test_normalize_upgrades_postgres_scheme(), test_normalize_upgrades_postgresql()

### Community 132 - "sort_by_priority"
Cohesion: 0.29
Nodes (6): Configuration, Phase 13 shortlist, Pipeline, Selection, sort_by_priority(), posted()

### Community 133 - "normalize_company_name"
Cohesion: 0.29
Nodes (6): canonical_company_name(), normalize_company_name(), _without_trailing_suffix(), test_legal_suffixes_do_not_collapse_distinct_names(), test_normalization_is_deterministic(), test_version_and_normalization_stay_explicit()

### Community 134 - "_company_key"
Cohesion: 0.40
Nodes (5): can_take(), identity(), take(), _bucket(), _company_key()

### Community 143 - "Phase 7 role-family weighting"
Cohesion: 0.25
Nodes (7): Canonical portfolio, Configuration, Phase 7 role-family weighting, Unknown classification, What is stored, What this phase does not do, Where the family comes from

## Knowledge Gaps
- **180 isolated node(s):** `job-agent`, `ScrapeSummary`, `_Sites`, `_FakeAio`, `Project` (+175 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 1133 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **13 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Job` connect `Job` to `test_outcomes.py`, `structured_jd.py`, `ApplyResult`, `Profile`, `get_health_report`, `sort_by_priority`, `_company_key`, `test_career_intelligence.py`, `test_fit.py`, `benchmark/engine.py`, `_Spy`, `test_role_weights.py`, `eligibility.py`, `test_resume.py`, `test_structured_jd.py`, `classify_role`, `diff.py`, `test_company_intelligence.py`, `test_application_deadline.py`, `test_pacing.py`, `feedback.py`, `re`, `company_intelligence.py`, `_find_cross_source_job`, `_input_hash`, `ingest.py`, `test_phase13_shortlist.py`, `vector_recovery.py`, `test_prep_builder.py`, `workday.py`, `compiler.py`, `test_calibration.py`, `typing`, `test_answers.py`, `apply_pending`, `TelegramClient`, `test_pipeline_apply_receives_only_persisted_ids`, `test_priority.py`, `baseline.py`, `priority.py`, `main.py`, `test_vector_recovery.py`, `monitoring.py`, `test_feedback.py`, `filters.py`, `tracker.py`, `migrate_to_neon.py`, `prep.py`, `prerank.py`, `telegram.py`, `test_robustness.py`, `WorkdaySubmitter`, `test_doctor.py`, `session_scope`, `LLMClient`, `pytest`, `test_scorer.py`, `outreach.py`, `scorer/engine.py`, `Source`, `runner.py`, `calibration.py`, `handlers.py`, `test_monitoring.py`, `answers.py`, `alerts.py`, `calculate_priority`, `test_vector_gate.py`, `application_portfolio.py`, `test_application_portfolio.py`, `db.py`, `test_cover_letter.py`?**
  _High betweenness centrality (0.135) - this node is a cross-community bridge._
- **Are the 175 inferred relationships involving `Job` (e.g. with `Data model (core/db.py)` and `AnswerResolver`) actually correct?**
  _`Job` has 175 INFERRED edges - model-reasoned connections that need verification._
- **What connects `job-agent`, `ScrapeSummary`, `_Sites` to the rest of the system?**
  _180 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `test_outcomes.py` be split into smaller, more focused modules?**
  _Cohesion score 0.1064102564102564 - nodes in this community are weakly interconnected._
- **Why does `get_settings()` connect `get_settings` to `Any`, `Profile`, `clients.py`, `test_career_intelligence.py`, `benchmark/engine.py`, `evaluate`, `conftest.py`, `textclean.py`, `test_resume.py`, `pipeline.py`, `Any`, `targets.py`, `diff.py`, `test_pacing.py`, `re`, `pathlib`, `run_pipeline`, `test_phase13_shortlist.py`, `test_prep_builder.py`, `workday.py`, `compiler.py`, `typing`, `test_answers.py`, `TelegramClient`, `Settings`, `test_company_intelligence_v2.py`, `baseline.py`, `main.py`, `test_vector_recovery.py`, `monitoring.py`, `filters.py`, `Job`, `test_webhook.py`, `migrate_to_neon.py`, `prep.py`, `telegram.py`, `settings.py`, `test_robustness.py`, `test_doctor.py`, `LLMClient`, `pytest`, `json`, `test_llm_provider.py`, `test_scorer.py`, `outreach.py`, `LLMBillingError`, `scorer/engine.py`, `Source`, `runner.py`, `handlers.py`, `test_monitoring.py`, `answers.py`, `linkedin_people.py`, `test_vector_gate.py`, `application_portfolio.py`, `test_application_portfolio.py`, `db.py`, `scheduler.py`?**
  _High betweenness centrality (0.114) - this node is a cross-community bridge._
- **Are the 259 inferred relationships involving `Profile` (e.g. with `AnswerResolver` and `_latest_education()`) actually correct?**
  _`Profile` has 259 INFERRED edges - model-reasoned connections that need verification._
- **Should `structured_jd.py` be split into smaller, more focused modules?**
  _Cohesion score 0.12513842746400886 - nodes in this community are weakly interconnected._