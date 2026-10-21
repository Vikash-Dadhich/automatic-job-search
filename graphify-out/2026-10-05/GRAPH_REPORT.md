# Graph Report - Automatic job search  (2026-10-05)

## Corpus Check
- 213 files · ~180,100 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 12 file(s) not represented in the graph (top: (none) 8, .typ 2, .example 1)

## Summary
- 3709 nodes · 12873 edges · 141 communities (129 shown, 12 thin omitted)
- Extraction: 89% EXTRACTED · 11% INFERRED · 0% AMBIGUOUS · INFERRED: 1388 edges (avg confidence: 0.94)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `02d35847`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- telegram.py
- structured_jd.py
- test_vector_gate.py
- test_phase0_baseline.py
- test_pacing.py
- clients.py
- test_career_intelligence.py
- json
- test_discovery.py
- test_feedback.py
- evaluate
- workday_rest.py
- conftest.py
- textclean.py
- discovery_recall.py
- textmatch.py
- eligibility.py
- coverage.py
- selector.py
- test_structured_jd.py
- pipeline.py
- TelegramClient
- classify_role
- Application
- job_identity.py
- diff.py
- test_company_intelligence.py
- session_state_path
- apply_pending
- dataclasses
- test_ingest_resilience.py
- feedback.py
- test_calibration.py
- company_intelligence.py
- test_eligibility.py
- test_apply_url.py
- Remaining Manual Setup
- benchmark/engine.py
- ingest.py
- test_phase13_shortlist.py
- test_company_intelligence_v2.py
- profile.py
- workday.py
- compiler.py
- vector_recovery.py
- baseline.py
- answers.py
- HttpCompanyIntelProvider
- FakeTransport
- Settings
- test_application_portfolio.py
- test_priority.py
- Phase 5 role classification
- diagnostics.py
- human_delay
- priority.py
- main.py
- test_vector_recovery.py
- Benchmark — Product Manager @ T-Mobile
- monitoring.py
- test_discovery_observability.py
- asyncio
- tracker.py
- datetime
- normalize_company_name
- migrate_to_neon.py
- discovery_experiment.py
- AGENTS.md
- prep.py
- job-agent
- Profile
- re
- linkedin_jobspy.py
- phase10-false-negative-protection.md
- typing
- Phase 1 discovery architecture
- Phase 0 baseline
- Phase 18 — Production reliability and monitoring
- Tier
- role_family_component
- WorkdaySubmitter
- OpenAIEmbedder
- test_application_tracker.py
- role_classify.py
- Discovery recall benchmark
- scorer/__init__.py
- Phase 9 visa and eligibility
- Career Intelligence
- 5. How fit is scored
- Phase 8 company intelligence
- pytest
- correction1-recruiting-universe.md
- token_optimizer.py
- run_service
- test_recruiting_universe.py
- extract_company_signals
- Phase 16 feedback learning
- scorer/engine.py
- session_scope
- runner.py
- calibration.py
- get_job_by_id
- Phase 15 application tracker
- test_monitoring.py
- extract_company_facts
- 3. Hard filters (before any model)
- linkedin_people.py
- Job
- Job Agent
- calculate_priority
- Phase 12 priority ranking
- test_gemini_client_falls_back_when_model_unavailable
- test_prep_builder.py
- is_pace_blocker
- Company intelligence 2.0
- filters.py
- phase17-calibration-benchmark.md
- Source
- targets.py
- vector-recovery.md
- get_settings
- Multi-dimensional role classification
- .total_years_experience
- init_db
- test_cover_letter.py
- scheduler.py
- Phase 6 candidate fit
- has_internship_signal
- test_role_weights.py
- Any
- test_doctor.py
- How jobs are found, filtered, scored, and sent
- _input_hash
- 2. Where jobs come from
- 8. The weight discussion (not built)
- 9. Pain points we have actually hit or spelled out
- 6. What is sent to you
- Phase 7 role-family weighting
- test_workday_locators.py

## God Nodes (most connected - your core abstractions)
1. `Job` - 377 edges
2. `Profile` - 332 edges
3. `session_scope()` - 317 edges
4. `Status` - 246 edges
5. `Source` - 220 edges
6. `get_settings()` - 168 edges
7. `get_job_by_id()` - 161 edges
8. `upsert_job()` - 140 edges
9. `TelegramClient` - 92 edges
10. `init_db()` - 87 edges

## Surprising Connections (you probably didn't know these)
- `Run review bot (Step 6)` --references--> `send_pending_alerts()`  [INFERRED]
  README.md → bot/alerts.py
- `What the profile contributes` --references--> `Profile`  [INFERRED]
  docs/phase9-visa-eligibility.md → config/profile.py
- `New architecture` --references--> `load_targets()`  [INFERRED]
  docs/phase1-discovery-architecture.md → config/targets.py
- `What counts as a recent application` --references--> `get_recently_applied_companies()`  [INFERRED]
  docs/phase14-application-portfolio.md → core/db.py
- `Health states` --references--> `get_health_report()`  [INFERRED]
  docs/phase18-production-reliability-monitoring.md → orchestrator/health.py

## Import Cycles
- None detected.

## Communities (141 total, 12 thin omitted)

### Community 0 - "telegram.py"
Cohesion: 0.07
Nodes (32): _decision_caption(), handle_message(), _handle_outcome_callback(), _handle_suggest_callback(), _safe_answer(), build_outcome_keyboard(), button(), outcome_label() (+24 more)

### Community 1 - "structured_jd.py"
Cohesion: 0.06
Nodes (65): ApplicationDeadline, _clip(), empty_application_deadline(), _excluded(), extract_application_deadline(), _from_match(), _named(), _parse_date() (+57 more)

### Community 2 - "test_vector_gate.py"
Cohesion: 0.19
Nodes (20): job_embed_text(), profile_embed_text(), profile_hash(), score_pending(), FakeClient, FakeEmbedder, _map(), test_budget_skips_tail_after_a_reject() (+12 more)

### Community 3 - "test_phase0_baseline.py"
Cohesion: 0.16
Nodes (14): _enable_internship_only(), _posting(), test_experience_span_is_about_five_years_and_not_summed(), test_friendly_sponsorship_stays_eligible(), test_hostile_sponsorship_is_rejected(), test_internship_only_code_default_is_false(), test_internship_only_drops_non_internship_titles(), test_internship_only_keeps_internship_titles() (+6 more)

### Community 4 - "test_pacing.py"
Cohesion: 0.21
Nodes (19): end_of_local_day(), note_pace_block(), _Applicator, _enable(), _row(), _seed(), _Sleep, test_acquire_after_blackout_keeps_multiplier() (+11 more)

### Community 5 - "clients.py"
Cohesion: 0.10
Nodes (18): _backoff_delay(), call_with_resilience(), is_permanent_account_error(), is_transient(), LLMBillingError, LLMError, _status_code(), suggested_delay() (+10 more)

### Community 6 - "test_career_intelligence.py"
Cohesion: 0.08
Nodes (51): CareerIntelligence, _apply_reading(), assess_career(), attach_career_intelligence(), career_input_hash(), CareerReading, _clause(), _clip() (+43 more)

### Community 7 - "json"
Cohesion: 0.11
Nodes (32): build_fit_user(), cached_fit(), _Dimension, evaluate_fit(), fit_context_block(), fit_is_current(), FitDecision, _FitPayload (+24 more)

### Community 8 - "test_discovery.py"
Cohesion: 0.08
Nodes (37): load_targets(), allocate_units(), AllocItem, build_discovery_plan(), DiscoveryConfig, DiscoverySource, _enabled_queries(), enabled_query_texts() (+29 more)

### Community 9 - "test_feedback.py"
Cohesion: 0.38
Nodes (8): shrink_rate(), _case(), _config(), _signal(), test_bands_families_and_sparse_subfamily(), test_cutoff_hides_future_submissions_and_outcomes(), test_funnel_does_not_treat_unknown_as_rejection(), test_shrinkage_and_adjustment_bounds()

### Community 10 - "evaluate"
Cohesion: 0.15
Nodes (25): evaluate(), sponsorship_signal(), test_sponsorship_and_false_friends(), _posting(), test_clearance_regex_pattern(), test_exclude_clearance_keyword(), test_exclude_high_yoe_requirement(), test_exclude_off_target_location() (+17 more)

### Community 11 - "workday_rest.py"
Cohesion: 0.11
Nodes (20): _as_text(), _company_name(), _one(), _fetch_detail(), _fetch_listing_page(), fetch_workday(), _is_recent_posted_on(), _parse_json() (+12 more)

### Community 12 - "conftest.py"
Cohesion: 0.10
Nodes (14): Testing conventions, reset_engine(), run_one(), db_ready(), _disable_apply_pacing(), _disable_vector_gate(), _internship_only_off(), profile() (+6 more)

### Community 13 - "textclean.py"
Cohesion: 0.09
Nodes (23): Flow, Hash and upsert, Limits, Normalization, Phase 4 JD ingestion, _drop_boilerplate_lines(), _extract_body(), extract_sections() (+15 more)

### Community 14 - "discovery_recall.py"
Cohesion: 0.16
Nodes (27): _verified_benchmark_hits(), BenchmarkCase, _bucket(), _case(), case_is_captured(), eligible(), load_benchmark(), measure_recall() (+19 more)

### Community 15 - "textmatch.py"
Cohesion: 0.12
Nodes (16): _city_state(), company_matches(), company_tokens(), contains_phrase(), is_remote_location(), location_matches(), normalize_text(), truncate_middle() (+8 more)

### Community 16 - "eligibility.py"
Cohesion: 0.17
Nodes (25): _ask_model(), _citizenship(), _clearance(), _current_student(), _dates(), _decision_from_job(), _dim(), DimensionResult (+17 more)

### Community 17 - "coverage.py"
Cohesion: 0.07
Nodes (38): build_coverage_report(), add_planned(), group_for(), CoverageReport, fail_unrecorded(), GroupMetrics, _jsonable(), log_coverage() (+30 more)

### Community 18 - "selector.py"
Cohesion: 0.17
Nodes (10): build_resume_data(), extract_job_terms(), _grounded_summary(), RankedBullet, reorder_skills(), score_bullet(), select_bullets(), SelectedExperience (+2 more)

### Community 19 - "test_structured_jd.py"
Cohesion: 0.14
Nodes (17): StructuredJobDescription, attach_structured_jd(), extract_structured_jd(), get_structured_jd(), structured_jd_is_current(), _areas(), _job(), test_changed_upsert_drops_the_old_reading() (+9 more)

### Community 20 - "pipeline.py"
Cohesion: 0.12
Nodes (15): _allocated_ids(), _benchmark_tier_one_stage(), _generate_suggestions_stage(), _note_skipped(), PipelineSummary, _portfolio_stage(), _prepare_shortlisted_resumes(), _run_opened_pipeline() (+7 more)

### Community 21 - "TelegramClient"
Cohesion: 0.11
Nodes (4): HttpxTransport, TelegramClient, TelegramTransport, telegram_webhook()

### Community 22 - "classify_role"
Cohesion: 0.10
Nodes (30): _role_classification_current(), classification_is_current(), classify_role(), _apply_role_classification(), _FakeClient, _jd(), test_classification_persists_and_does_not_filter(), test_classifier_version_bump_invalidates_phase5_v1() (+22 more)

### Community 23 - "Application"
Cohesion: 0.14
Nodes (16): Application, ApplicationEvent, CalibrationMetric, CalibrationRun, get_application_events(), get_calibration_metrics(), get_calibration_run(), list_events_for_applications() (+8 more)

### Community 24 - "job_identity.py"
Cohesion: 0.13
Nodes (14): _find_cross_source_job(), canonicalize_job_url(), _is_tracking_param(), locations_agree(), locations_conflict(), normalize_title(), same_employer(), same_posting_url() (+6 more)

### Community 25 - "diff.py"
Cohesion: 0.11
Nodes (22): get_suggestions_for_job(), SkillPlacement, SkillProvenance, SkillSuggestion, SuggestionStatus, apply_approved_suggestions_to_resume_data(), _baseline_skill_keys(), classify_provenance() (+14 more)

### Community 26 - "test_company_intelligence.py"
Cohesion: 0.21
Nodes (17): get_recently_applied_companies(), attach_company_intelligence(), FakeProvider, _job(), _posting(), test_ambiguous_names_stay_separate(), test_company_facts_do_not_change_scoring_signals(), test_company_sources_accumulate_and_a_failed_refresh_keeps_them() (+9 more)

### Community 27 - "session_state_path"
Cohesion: 0.14
Nodes (13): CredentialsFile, get_tenant_credentials(), has_saved_session(), load_credentials(), _load_yaml(), reload_credentials(), session_state_path(), TenantCredentials (+5 more)

### Community 28 - "apply_pending"
Cohesion: 0.21
Nodes (24): apply_pending(), FakeApplicator, _script_reloads(), _seed_job(), test_allocation_removed_before_execution_is_skipped(), test_apply_linkedin_with_workday_url(), test_apply_pending_blocker(), test_apply_pending_empty() (+16 more)

### Community 29 - "dataclasses"
Cohesion: 0.12
Nodes (17): _FakeSummary, test_pipeline_order_and_aggregation(), fake_alerts(), fake_apply(), fake_ingestion(), fake_outcomes(), fake_prep(), fake_resume() (+9 more)

### Community 30 - "test_ingest_resilience.py"
Cohesion: 0.05
Nodes (44): get_job_by_source_id(), run_ingestion(), _accept(), _run_jobspy(), _run_workday(), kill_process_group(), LineWorker, QueryTimeoutError (+36 more)

### Community 31 - "feedback.py"
Cohesion: 0.14
Nodes (25): FeedbackRun, FeedbackSignal, get_feedback_run(), get_feedback_signals(), get_latest_feedback_run(), save_feedback_run(), _adjustment(), _band() (+17 more)

### Community 32 - "test_calibration.py"
Cohesion: 0.22
Nodes (20): brier_score(), build_calibration(), CalibrationFold, CalibrationReport, load_calibration_config(), run_calibration(), load_feedback_config(), _calibration() (+12 more)

### Community 33 - "company_intelligence.py"
Cohesion: 0.14
Nodes (20): CompanyIntelligence, _accumulate_sources(), _apply_context(), _apply_facts(), _by_key(), _clear_facts(), _confidence_for(), _context_from() (+12 more)

### Community 34 - "test_eligibility.py"
Cohesion: 0.15
Nodes (19): assign_eligibility(), attach_eligibility(), eligibility_column_types(), eligibility_is_current(), EligibilityDecision, evaluate_eligibility(), profile_eligibility_hash(), _job() (+11 more)

### Community 35 - "test_apply_url.py"
Cohesion: 0.20
Nodes (11): ApplyKind, classify_apply_url(), _host(), is_automateable_apply_url(), is_workday_url(), workday_parts(), _cmd_list_apply(), test_classify_company_site() (+3 more)

### Community 36 - "Remaining Manual Setup"
Cohesion: 0.08
Nodes (24): 2a. Find a Workday URL, 2b. Edit `config/targets.yaml`, 3a. Run the save-session helper, 3b. What you do in the browser, 4a. Discover jobs (LinkedIn / Indeed + any real Workday tenants), 4b. Score with Gemini, 4c. Attach your base resume to staged jobs, 4d. Send LinkedIn/Indeed application prep pack (Telegram) (+16 more)

### Community 37 - "benchmark/engine.py"
Cohesion: 0.12
Nodes (19): BenchmarkReport, BenchmarkSummary, build_benchmark(), _derive_seniority(), DimensionScore, _education_rank(), _median(), _norm() (+11 more)

### Community 38 - "ingest.py"
Cohesion: 0.19
Nodes (6): _stamp_role_family_weight(), log_discovery_plan(), IngestSummary, _load_role_client(), _persist_postings(), _PersistCounts

### Community 39 - "test_phase13_shortlist.py"
Cohesion: 0.09
Nodes (33): get_jobs_by_status(), apply_shortlist(), _close_enough(), _company_key(), _company_ok(), config_hash(), _diversify(), _family() (+25 more)

### Community 40 - "test_company_intelligence_v2.py"
Cohesion: 0.14
Nodes (11): CompanyIntelProvider, CompanyLookupResult, CompanySourceDocument, merge_company_signals(), refresh_company_intelligence(), _one(), _Provider, _signals() (+3 more)

### Community 41 - "profile.py"
Cohesion: 0.14
Nodes (28): Address, Education, Exclusions, Experience, Identity, Preferences, WorkAuthorization, _make_base_pdf() (+20 more)

### Community 42 - "workday.py"
Cohesion: 0.18
Nodes (10): new_page(), click_by_role(), click_next(), _collect_labeled_fields(), detect_blocker(), _fill_field(), is_review_page(), safe_click() (+2 more)

### Community 43 - "compiler.py"
Cohesion: 0.10
Nodes (19): apply_fit_caps(), _baseline_pdf_for_job(), clean_name(), compile_pending(), compile_resume(), compile_resume_data(), FitReport, _job_resume_output() (+11 more)

### Community 44 - "vector_recovery.py"
Cohesion: 0.17
Nodes (16): fingerprint_profile(), _compiled(), _confidence(), config_hash(), evaluate_recovery(), _family_group(), load_recovery_config(), _mba_program() (+8 more)

### Community 45 - "baseline.py"
Cohesion: 0.06
Nodes (34): get_role_baseline_by_role(), RoleBaseline, build_baseline_resume_data(), build_role_baseline(), _normalize(), _slugify_role(), _synthetic_job_for_role(), aggregate_role_skills() (+26 more)

### Community 46 - "answers.py"
Cohesion: 0.07
Nodes (26): AnswerResolver, one(), answers_to_payload(), AnswerSource, _discovery_channel(), is_open_ended(), _latest_education(), _matches() (+18 more)

### Community 47 - "HttpCompanyIntelProvider"
Cohesion: 0.24
Nodes (4): HttpCompanyIntelProvider, test_http_provider_handles_timeout_and_malformed_pages(), ok(), test_http_provider_keeps_the_caller_source_type()

### Community 48 - "FakeTransport"
Cohesion: 0.13
Nodes (21): send_prep_pack(), _should_retry_telegram(), FakeTransport, _enable_brief(), _insert(), _RaisingClient, _row(), test_card_shows_stored_fields_without_changing_them() (+13 more)

### Community 50 - "test_application_portfolio.py"
Cohesion: 0.05
Nodes (61): Configuration, Phase 13 shortlist, Pipeline, Selection, Capacity, Decisions, Phase 14 application portfolio, Pipeline (+53 more)

### Community 51 - "test_priority.py"
Cohesion: 0.19
Nodes (17): apply_priority(), load_priority_config(), priority_is_current(), PriorityDecision, _job(), test_dream_company_is_only_a_configured_boost(), test_eligibility_unknown_is_not_ineligible(), test_fit_and_role_family_order_attention() (+9 more)

### Community 52 - "Phase 5 role classification"
Cohesion: 0.29
Nodes (6): Inputs, Limits, Output, Phase 5 role classification, Taxonomy, When it runs again

### Community 53 - "diagnostics.py"
Cohesion: 0.16
Nodes (9): effective_baseline(), effective_config_hash(), profile_hash(), public_config(), write_effective_baseline(), test_baseline_file_has_no_secrets(), test_config_hash_changes_when_internship_only_changes(), test_effective_baseline_matches_public_fields() (+1 more)

### Community 54 - "human_delay"
Cohesion: 0.17
Nodes (9): action_delay_bounds(), human_delay(), type_like_human(), typing_delay_bounds(), _crawl(), test_delay_bounds_from_settings(), test_delay_bounds_swap_when_inverted(), test_human_delay_jitter_in_range() (+1 more)

### Community 55 - "priority.py"
Cohesion: 0.15
Nodes (21): is_dream_company(), company_domain_component(), _company_signals(), _components(), dream_company_component(), eligibility_component(), _explicit_sections(), fit_component() (+13 more)

### Community 56 - "main.py"
Cohesion: 0.06
Nodes (34): apply_decided_suggestions(), load_profile(), _load_yaml(), configure_logging(), _build_doctor_report(), build_parser(), _cmd_benchmark(), _cmd_build_baseline() (+26 more)

### Community 57 - "test_vector_recovery.py"
Cohesion: 0.25
Nodes (30): _enable(), _seed(), _assert_no_profile_text(), _bare_job(), _doc(), _exclude_company(), _score(), _stamp() (+22 more)

### Community 58 - "Benchmark — Product Manager @ T-Mobile"
Cohesion: 0.33
Nodes (5): Benchmark — Product Manager @ T-Mobile, Dimensions, Gaps, Recommendations, Strengths

### Community 59 - "monitoring.py"
Cohesion: 0.10
Nodes (28): _as_utc(), PipelineRun, PipelineStageRun, _cmd_health(), _brief(), format_health_report(), get_health_report(), _recent_failures() (+20 more)

### Community 60 - "test_discovery_observability.py"
Cohesion: 0.15
Nodes (11): list_stage_runs(), open_stage_run(), _safe_close_stage(), _safe_open_stage(), discovery_evidence(), possible_result_cap(), _Frame, test_evidence_failure_does_not_hide_the_ingest_result() (+3 more)

### Community 61 - "asyncio"
Cohesion: 0.17
Nodes (5): process_updates(), run_polling(), Submitter, test_run_polling_max_iterations(), __init__()

### Community 62 - "tracker.py"
Cohesion: 0.21
Nodes (15): _add_event(), application_method(), backfill_submitted_applications(), _event_exists(), _get_or_create(), record_manual_review(), record_outcome(), record_prefill() (+7 more)

### Community 63 - "datetime"
Cohesion: 0.15
Nodes (12): build_keyboard(), build_review_caption(), format_answers_message(), format_cover_letter_message(), ReviewSummary, _send_one(), send_pending_reviews(), test_build_keyboard_and_caption() (+4 more)

### Community 64 - "normalize_company_name"
Cohesion: 0.29
Nodes (6): canonical_company_name(), normalize_company_name(), _without_trailing_suffix(), test_legal_suffixes_do_not_collapse_distinct_names(), test_normalization_is_deterministic(), test_version_and_normalization_stay_explicit()

### Community 65 - "migrate_to_neon.py"
Cohesion: 0.13
Nodes (12): _absolute_sqlite_url(), normalize_database_url(), _cell(), _copy_table(), _counts(), main(), _reset_sequences(), _row() (+4 more)

### Community 66 - "discovery_experiment.py"
Cohesion: 0.06
Nodes (56): account_executions(), _baseline_slot_reason(), _baseline_slots(), build_schedule(), _classify_incremental(), compare_arms(), _execute(), _execute_phrase() (+48 more)

### Community 67 - "AGENTS.md"
Cohesion: 0.22
Nodes (7): Build order and status, Coding conventions, Commands, Confirmed product decisions, Project, Repository layout, Workflow for implementing a step

### Community 68 - "prep.py"
Cohesion: 0.13
Nodes (17): _dedupe(), _fit_lines(), _load_canonical_shortlist(), _mark_sent(), _notify_empty(), PrepSummary, render_job_card(), render_shortlist() (+9 more)

### Community 71 - "Profile"
Cohesion: 0.10
Nodes (19): Profile, LLMClient, _attach_priority(), _JobOutcome, _priority_evidence(), _record_career_intelligence(), Scorer, prerank_jobs() (+11 more)

### Community 72 - "re"
Cohesion: 0.22
Nodes (6): contains_banned(), _fallback_outreach(), generate_outreach(), strip_banned_sentences(), build_outreach_user(), test_generate_outreach_retries_on_banned()

### Community 73 - "linkedin_jobspy.py"
Cohesion: 0.11
Nodes (17): location_acceptable(), main(), _one(), _records(), _dataframe_to_postings(), _effective_windows(), _explicit_company_url(), _external_id() (+9 more)

### Community 75 - "typing"
Cohesion: 0.09
Nodes (9): What still needs the user (before live runs), launch_context(), _new_context(), save_storage_state(), save_session(), health(), Deploy with Docker, save_linkedin_session() (+1 more)

### Community 76 - "Phase 1 discovery architecture"
Cohesion: 0.11
Nodes (16): 40/40/15/5 priority model, Current problem, New architecture, Phase 1 discovery architecture, Provenance, Purpose, Role families, Search allocation (+8 more)

### Community 77 - "Phase 0 baseline"
Cohesion: 0.22
Nodes (8): Candidate baseline, Discovery baseline, Local versus production, Phase 0 baseline, Production baseline, Scoring baseline, Sponsorship behavior locked by tests, Tests

### Community 78 - "Phase 18 — Production reliability and monitoring"
Cohesion: 0.15
Nodes (12): Backlog diagnostics, CLI, Configuration, Failure isolation, Health states, Logging, Phase 18 — Production reliability and monitoring, Purpose (+4 more)

### Community 79 - "Tier"
Cohesion: 0.09
Nodes (22): Tier, compute_tier(), parse_score(), _posting(), ScoreOnlyClient, test_company_blocklist_does_not_match_lookalikes(), test_dream_company_match_tolerates_suffix(), test_parse_score_handles_braces_inside_strings() (+14 more)

### Community 80 - "role_family_component"
Cohesion: 0.17
Nodes (10): Freshness, dream company, and workflow, Hash, Priority 2.0, Program and domain evidence, Role alignment, Weights, _half_up_ratio(), role_family_component() (+2 more)

### Community 81 - "WorkdaySubmitter"
Cohesion: 0.18
Nodes (7): SessionMissingError, WorkdaySubmitter, test_submit_generic_exception(), test_submit_missing_url(), test_submit_session_missing(), boom_launch(), test_submit_unparseable_without_tenant()

### Community 83 - "test_application_tracker.py"
Cohesion: 0.23
Nodes (12): application_history(), SubmitResult, get_application_for_job(), _job(), _Prefill, _Submitter, _tap(), test_a_later_outcome_keeps_the_earlier_event() (+4 more)

### Community 84 - "role_classify.py"
Cohesion: 0.15
Nodes (18): _clause_containing(), _clip_items(), _deterministic(), _is_interaction(), _item_text(), _ModelLabel, _parse_model(), _phrase_hits() (+10 more)

### Community 85 - "Discovery recall benchmark"
Cohesion: 0.10
Nodes (18): Discovery recall benchmark, Label corrections on 2026-10-04, Limits, Matching, Reproduce, What is checked in, Discovery run observability, Query timeout and incremental save (+10 more)

### Community 86 - "scorer/__init__.py"
Cohesion: 0.20
Nodes (3): ScoreSummary, Evaluation, ScoreRaw

### Community 87 - "Phase 9 visa and eligibility"
Cohesion: 0.25
Nodes (7): Cache and storage, Education, graduation, experience, location, dates, Phase 9 visa and eligibility, Sponsorship, citizenship, and clearance, States, What the profile contributes, What this phase does not do

### Community 88 - "Career Intelligence"
Cohesion: 0.33
Nodes (5): Cache, Career Intelligence, Dimensions, Failures, Overall score

### Community 89 - "5. How fit is scored"
Cohesion: 0.22
Nodes (7): 10. File map, 5.1 What the model is, 5.2 The two inputs, 5.3 The rubric, verbatim in meaning, 5.4 What the code does with the score, 5.5 What a number means, 5. How fit is scored

### Community 90 - "Phase 8 company intelligence"
Cohesion: 0.29
Nodes (6): Names and reuse, Phase 8 company intelligence, Schema, Sources, What it is, What this phase does not change

### Community 91 - "pytest"
Cohesion: 0.10
Nodes (21): LLM client layer (`scorer/clients.py`), Scoring specifics (Step 3), Tech stack, build_llm_client(), OpenAIClient, _FakeAio, _FakeAsyncModels, _FakeCandidate (+13 more)

### Community 93 - "token_optimizer.py"
Cohesion: 0.14
Nodes (9): approx_tokens(), cache_block(), compact_json_dumps(), minify_job(), build_fit_system_blocks(), build_scoring_system_blocks(), build_scoring_user(), test_prompt_builders_cache_and_content() (+1 more)

### Community 94 - "run_service"
Cohesion: 0.21
Nodes (3): run_service(), test_run_service_stops_without_poller(), test_run_service_with_poller_respects_stop()

### Community 95 - "test_recruiting_universe.py"
Cohesion: 0.39
Nodes (6): _family(), _jd(), test_first_discovery_provenance_is_immutable(), test_marketing_is_separate_from_product_marketing_and_other(), test_mba_summer_associate_is_an_internship_signal(), test_technology_strategy_is_not_technology_consulting()

### Community 96 - "extract_company_signals"
Cohesion: 0.38
Nodes (5): _compact(), extract_company_signals(), _signal(), _snippet(), test_signals_are_explicit_and_multi_valued()

### Community 97 - "Phase 16 feedback learning"
Cohesion: 0.33
Nodes (5): Evidence and shrinkage, Phase 16 feedback learning, Rates, Segments, Who is counted

### Community 98 - "scorer/engine.py"
Cohesion: 0.08
Nodes (28): build_embedder(), _cache_path(), clears_threshold(), cosine(), Embedder, jd_vector(), load_profile_embedding(), save_profile_embedding() (+20 more)

### Community 99 - "session_scope"
Cohesion: 0.08
Nodes (39): session_scope(), Status, upsert_job(), _status_for_tier(), _count(), test_staging_and_portfolio_do_not_create_an_application(), test_compile_for_job_overwrites(), test_prepare_pending_missing_base_no_crash() (+31 more)

### Community 100 - "runner.py"
Cohesion: 0.11
Nodes (10): ApplyRunner, ApplySummary, _eligible(), _ensure_tenant(), _log_explicit_skip(), _ready_for_explicit_apply(), Applicator, ApplyResult (+2 more)

### Community 101 - "calibration.py"
Cohesion: 0.15
Nodes (28): _append_buckets(), _append_short_target(), _append_slice(), _append_target_metrics(), _append_topk(), _bucket_name(), calibration_config_hash(), CalibrationMetricRow (+20 more)

### Community 102 - "get_job_by_id"
Cohesion: 0.13
Nodes (30): _reload_job(), handle_callback(), send_outcome_prompt(), decode_callback(), encode_callback(), ReviewAction, claim_outcome_prompt(), get_job_by_id() (+22 more)

### Community 103 - "Phase 15 application tracker"
Cohesion: 0.33
Nodes (5): Method and time, Phase 15 application tracker, States and outcomes, What this is not, When a row is created

### Community 104 - "test_monitoring.py"
Cohesion: 0.09
Nodes (29): Architecture, Pipeline run lifecycle, close_pipeline_run(), interrupt_stale_runs(), list_pipeline_runs(), open_pipeline_run(), stage_counters(), run_pipeline() (+21 more)

### Community 105 - "extract_company_facts"
Cohesion: 0.29
Nodes (5): extract_company_facts(), merge_company_facts(), test_extractor_keeps_unstated_facts_null(), test_merge_company_facts_keeps_omitted_fields(), test_prestige_language_is_not_a_fact()

### Community 106 - "3. Hard filters (before any model)"
Cohesion: 0.18
Nodes (11): 3.10 What a survivor looks like, 3.1 Company blocklist, 3.2 Exclusion keywords, 3.3 Clearance language, 3.4 Staffing agencies, 3.5 Internship gate, 3.6 Seniority filter (separate from the internship gate), 3.7 Years of experience (+3 more)

### Community 107 - "linkedin_people.py"
Cohesion: 0.07
Nodes (25): auto_discover_peers(), BlockerError, build_people_search_url(), _detect_blocker(), discover_peers(), extract_profile_urls(), _heuristic_parse(), LLMClient (+17 more)

### Community 108 - "Job"
Cohesion: 0.08
Nodes (26): AlertSummary, build_alert_caption(), _send_one(), send_pending_alerts(), _assign_canonical_url(), _drop_structured_jd(), finish_outcome_prompt(), get_application_by_id() (+18 more)

### Community 109 - "Job Agent"
Cohesion: 0.13
Nodes (14): Application prep packs (LinkedIn / Indeed), Job Agent, Layout, LinkedIn peer benchmarking (optional, off by default), Resumes (Step 4), Run automation (Step 5), Run ingestion (Step 2), Run review bot (Step 6) (+6 more)

### Community 110 - "calculate_priority"
Cohesion: 0.19
Nodes (17): calculate_priority(), _combine(), _reasons(), _job(), _signal(), test_confidence_and_structured_evidence(), test_domains_are_capped_and_irrelevant_domains_add_nothing(), test_eligibility_order_and_unknown() (+9 more)

### Community 111 - "Phase 12 priority ranking"
Cohesion: 0.50
Nodes (3): Components, Phase 12 priority ranking, Version

### Community 112 - "test_gemini_client_falls_back_when_model_unavailable"
Cohesion: 0.38
Nodes (4): _FakeGenaiClient, test_gemini_client_complete_maps_system_blocks(), test_gemini_client_escalates_on_truncated_output(), test_gemini_client_falls_back_when_model_unavailable()

### Community 113 - "test_prep_builder.py"
Cohesion: 0.12
Nodes (13): _answer_item(), build_job_section(), compile_prep_pdf(), generate_prep_pack(), PrepPackResult, render_markdown(), FakeClient, _job() (+5 more)

### Community 114 - "is_pace_blocker"
Cohesion: 0.50
Nodes (3): is_pace_blocker(), test_pace_hints_ignore_mfa_and_empty(), test_pace_hints_match()

### Community 115 - "Company intelligence 2.0"
Cohesion: 0.33
Nodes (5): Company intelligence 2.0, Company versus job, Sources and refresh, What it does not store, What it stores

### Community 116 - "filters.py"
Cohesion: 0.13
Nodes (16): citizenship_restriction(), _clearance_clauses(), clearance_requirement(), FilterResult, _haystack(), _location_ok(), _mandatory_years(), _matches_any() (+8 more)

### Community 118 - "Source"
Cohesion: 0.09
Nodes (28): Data model (core/db.py), Status lifecycle, Source, _dedupe(), hash_fallback(), RawPosting, to_job(), content_hash() (+20 more)

### Community 119 - "targets.py"
Cohesion: 0.05
Nodes (26): reload_profile(), _load_yaml(), parse_workday_url(), reload_targets(), SearchConfig, Targets, WorkdayParts, WorkdayTenant (+18 more)

### Community 121 - "get_settings"
Cohesion: 0.17
Nodes (9): acquire(), AcquireResult, _clamp_multiplier(), _clock(), gap_seconds(), note_success(), get_settings(), PlatformPacing (+1 more)

### Community 122 - "Multi-dimensional role classification"
Cohesion: 0.29
Nodes (6): Cache, Contract, Function versus interaction, Multi-dimensional role classification, Non-goals, What the classifier reads

### Community 124 - "init_db"
Cohesion: 0.08
Nodes (22): _company_name(), _dialect_name(), _ensure_company_columns(), _ensure_job_columns(), _ensure_pipeline_stage_columns(), get_engine(), get_session_factory(), init_db() (+14 more)

### Community 125 - "test_cover_letter.py"
Cohesion: 0.16
Nodes (10): cap_cover_letter(), _fallback_cover_letter(), generate_cover_letter(), build_cover_letter_user(), _job(), _ScriptedClient, test_cap_cover_letter_cuts_on_sentence_boundary(), test_cap_cover_letter_hard_slice_without_punctuation() (+2 more)

### Community 126 - "scheduler.py"
Cohesion: 0.15
Nodes (8): build_scheduler(), parse_hhmm(), _noop(), test_build_scheduler_invalid_timezone(), test_build_scheduler_registers_jobs(), test_build_scheduler_skips_invalid_times(), test_parse_hhmm(), test_parse_hhmm_invalid()

### Community 127 - "Phase 6 candidate fit"
Cohesion: 0.33
Nodes (5): Dimensions, Not in this phase, Output, Phase 6 candidate fit, When the model is not called

### Community 129 - "test_role_weights.py"
Cohesion: 0.14
Nodes (18): get_role_family_weight(), load_role_family_weights(), _validate(), weight_for_subfamily(), test_feedback_config_keeps_priority_integration_off(), test_company_and_vector_are_not_weight_inputs(), test_discovery_capacity_stays_independent(), test_discovery_labels_do_not_choose_the_weight() (+10 more)

### Community 130 - "Any"
Cohesion: 0.10
Nodes (11): AnthropicClient, _attempt(), _as_int(), _finish_reason(), GeminiClient, _attempt(), _lower_thinking(), _attempt() (+3 more)

### Community 131 - "test_doctor.py"
Cohesion: 0.44
Nodes (7): _cmd_doctor(), _job(), test_doctor_cooldown(), test_doctor_empty_db(), test_doctor_outcomes(), test_doctor_vector_gate(), test_doctor_with_jobs()

### Community 135 - "How jobs are found, filtered, scored, and sent"
Cohesion: 0.25
Nodes (7): 1. What a run is, 4.1 Pre-score rank (`prerank_score`), 4.2 Embedding gate (this does drop jobs), 4.3 Fit-model cap, 4. How results are prioritised today, 7. Statuses, in one pass, How jobs are found, filtered, scored, and sent

### Community 136 - "_input_hash"
Cohesion: 0.48
Nodes (5): _as_utc(), _freshness_day(), _input_hash(), _iso(), posted()

### Community 139 - "2. Where jobs come from"
Cohesion: 0.29
Nodes (7): 2.1 Search terms, 2.2 Sites and the exact JobSpy arguments, 2.3 How each site treats "posted in the last 36 hours", 2.4 What is kept from a JobSpy row, 2.5 Workday, separately from LinkedIn, 2.6 Save and dedupe, 2. Where jobs come from

### Community 140 - "8. The weight discussion (not built)"
Cohesion: 0.33
Nodes (6): 8.1 What you asked for, 8.2 Decisions you agreed with, 8.3 A weight table we used as a sketch, 8.4 What we said the rubric should do for career-switch roles, 8.5 How that would sit on the current pipeline, 8. The weight discussion (not built)

### Community 141 - "9. Pain points we have actually hit or spelled out"
Cohesion: 0.33
Nodes (6): 9.1 Discovery, 9.2 Filters, 9.3 Scoring, 9.4 What you receive, 9.5 Operations, 9. Pain points we have actually hit or spelled out

### Community 142 - "6. What is sent to you"
Cohesion: 0.40
Nodes (5): 6.1 Who is eligible, 6.2 The shortlist rule, 6.3 Each line, 6.4 If brief mode is turned off, 6. What is sent to you

### Community 143 - "Phase 7 role-family weighting"
Cohesion: 0.22
Nodes (8): Canonical portfolio, Configuration, Four different questions, Phase 7 role-family weighting, Unknown classification, What is stored, What this phase does not do, Where the family comes from

## Knowledge Gaps
- **181 isolated node(s):** `job-agent`, `ScrapeSummary`, `_Sites`, `_FakeAio`, `Project` (+176 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 1162 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **12 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Job` connect `Job` to `telegram.py`, `structured_jd.py`, `test_vector_gate.py`, `test_doctor.py`, `test_pacing.py`, `test_role_weights.py`, `test_career_intelligence.py`, `json`, `_input_hash`, `test_feedback.py`, `textmatch.py`, `eligibility.py`, `selector.py`, `test_structured_jd.py`, `classify_role`, `Application`, `job_identity.py`, `diff.py`, `test_company_intelligence.py`, `apply_pending`, `test_ingest_resilience.py`, `feedback.py`, `test_calibration.py`, `company_intelligence.py`, `test_eligibility.py`, `benchmark/engine.py`, `ingest.py`, `test_phase13_shortlist.py`, `profile.py`, `workday.py`, `compiler.py`, `vector_recovery.py`, `baseline.py`, `answers.py`, `FakeTransport`, `test_application_portfolio.py`, `test_priority.py`, `priority.py`, `main.py`, `test_vector_recovery.py`, `monitoring.py`, `asyncio`, `tracker.py`, `datetime`, `migrate_to_neon.py`, `prep.py`, `Profile`, `re`, `typing`, `Tier`, `role_family_component`, `WorkdaySubmitter`, `test_application_tracker.py`, `token_optimizer.py`, `scorer/engine.py`, `session_scope`, `runner.py`, `get_job_by_id`, `test_monitoring.py`, `calculate_priority`, `test_prep_builder.py`, `filters.py`, `Source`, `test_cover_letter.py`?**
  _High betweenness centrality (0.118) - this node is a cross-community bridge._
- **Are the 177 inferred relationships involving `Job` (e.g. with `Data model (core/db.py)` and `AnswerResolver`) actually correct?**
  _`Job` has 177 INFERRED edges - model-reasoned connections that need verification._
- **What connects `job-agent`, `ScrapeSummary`, `_Sites` to the rest of the system?**
  _181 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `telegram.py` be split into smaller, more focused modules?**
  _Cohesion score 0.0673076923076923 - nodes in this community are weakly interconnected._
- **Why does `get_settings()` connect `get_settings` to `telegram.py`, `Any`, `test_vector_gate.py`, `test_pacing.py`, `clients.py`, `test_career_intelligence.py`, `test_phase0_baseline.py`, `evaluate`, `conftest.py`, `textclean.py`, `textmatch.py`, `pipeline.py`, `TelegramClient`, `diff.py`, `session_state_path`, `test_ingest_resilience.py`, `test_eligibility.py`, `benchmark/engine.py`, `test_phase13_shortlist.py`, `test_company_intelligence_v2.py`, `profile.py`, `workday.py`, `compiler.py`, `baseline.py`, `answers.py`, `FakeTransport`, `Settings`, `test_application_portfolio.py`, `diagnostics.py`, `human_delay`, `main.py`, `test_vector_recovery.py`, `monitoring.py`, `asyncio`, `migrate_to_neon.py`, `prep.py`, `Profile`, `re`, `linkedin_jobspy.py`, `typing`, `Tier`, `OpenAIEmbedder`, `pytest`, `token_optimizer.py`, `run_service`, `test_recruiting_universe.py`, `scorer/engine.py`, `session_scope`, `runner.py`, `test_monitoring.py`, `linkedin_people.py`, `Job`, `test_prep_builder.py`, `filters.py`, `targets.py`, `init_db`, `test_cover_letter.py`, `scheduler.py`?**
  _High betweenness centrality (0.103) - this node is a cross-community bridge._
- **Are the 260 inferred relationships involving `Profile` (e.g. with `AnswerResolver` and `_latest_education()`) actually correct?**
  _`Profile` has 260 INFERRED edges - model-reasoned connections that need verification._
- **Should `structured_jd.py` be split into smaller, more focused modules?**
  _Cohesion score 0.05700852189244784 - nodes in this community are weakly interconnected._