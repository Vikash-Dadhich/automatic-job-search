# Graph Report - Automatic job search  (2026-10-14)

## Corpus Check
- 219 files · ~190,178 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 12 file(s) not represented in the graph (top: (none) 8, .typ 2, .example 1)

## Summary
- 3997 nodes · 13801 edges · 140 communities (125 shown, 15 thin omitted)
- Extraction: 89% EXTRACTED · 11% INFERRED · 0% AMBIGUOUS · INFERRED: 1458 edges (avg confidence: 0.94)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `310fc3d1`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- json
- structured_jd.py
- test_false_negative.py
- test_phase0_baseline.py
- test_outcomes.py
- call_with_resilience
- test_career_intelligence.py
- fit.py
- test_discovery.py
- test_openai_run_usage.py
- evaluate
- workday_rest.py
- conftest.py
- models.py
- discovery_recall.py
- answers.py
- eligibility.py
- ingest.py
- get_job_by_id
- test_structured_jd.py
- pipeline.py
- TelegramClient
- test_resume.py
- scheduler.py
- test_monitoring.py
- diff.py
- test_company_intelligence.py
- settings.py
- test_pacing.py
- test_pipeline_order_and_aggregation
- test_ingest_resilience.py
- feedback.py
- test_calibration.py
- extract_company_signals
- test_eligibility.py
- targets.py
- Remaining Manual Setup
- linkedin_people.py
- SQLModel
- test_phase13_shortlist.py
- test_feedback.py
- pytest
- db.py
- compiler.py
- prep.py
- re
- test_workload_limits.py
- role_classify.py
- test_scorer.py
- Settings
- test_application_portfolio.py
- test_priority.py
- Phase 5 role classification
- test_application_deadline.py
- test_apply_url.py
- priority.py
- main.py
- test_vector_recovery.py
- Benchmark — Product Manager @ T-Mobile
- FakeTransport
- MonkeyPatch
- OpenAIClient
- test_application_tracker.py
- pathlib
- benchmark/engine.py
- get_health_report
- discovery_experiment.py
- Job
- test_company_intelligence_v2.py
- job-agent
- Profile
- AGENTS.md
- linkedin_jobspy.py
- phase10-false-negative-protection.md
- workday.py
- Phase 1 discovery architecture
- Phase 0 baseline
- test_webhook.py
- classify_role
- Priority 2.0
- WorkdaySubmitter
- _chat_ok
- runner.py
- run_service
- Discovery recall benchmark
- typing
- test_trial_workflow.py
- Career Intelligence
- test_main_cli.py
- Phase 8 company intelligence
- test_llm_provider.py
- correction1-recruiting-universe.md
- get_settings
- test_openai_request_gate.py
- company_intelligence.py
- load_monitoring_config
- Phase 16 feedback learning
- scorer/engine.py
- RawPosting
- run_pipeline
- calibration.py
- _persist_postings
- Phase 15 application tracker
- _build_doctor_report
- normalize_company_name
- 3. Hard filters (before any model)
- extract_company_facts
- FakeClient
- Job Agent
- calculate_priority
- Phase 12 priority ranking
- test_doctor.py
- generate_prep_pack
- Structured JD intelligence
- Company intelligence 2.0
- filters.py
- phase17-calibration-benchmark.md
- get_recently_applied_companies
- sort_by_priority
- vector-recovery.md
- test_posting_cap_is_safe_when_batches_arrive_together
- Multi-dimensional role classification
- _input_hash
- migrate_to_neon.py
- _Embeddings
- OpenAIRequestLedger
- configure_logging
- test_workday_locators.py
- test_role_weights.py
- clients.py
- build_parser
- CompanyIntelProvider
- FakeTransport
- _ShortEmbedder
- FakeClient
- Phase 7 role-family weighting
- 2. Where jobs come from
- ScoreRaw
- How jobs are found, filtered, scored, and sent

## God Nodes (most connected - your core abstractions)
1. `Job` - 385 edges
2. `Profile` - 333 edges
3. `session_scope()` - 323 edges
4. `Status` - 256 edges
5. `Source` - 226 edges
6. `get_settings()` - 186 edges
7. `get_job_by_id()` - 161 edges
8. `upsert_job()` - 143 edges
9. `TelegramClient` - 92 edges
10. `init_db()` - 89 edges

## Surprising Connections (you probably didn't know these)
- `Checklist (your remaining work)` --references--> `save_session()`  [INFERRED]
  SETUP.md → automation/login.py
- `Run review bot (Step 6)` --references--> `send_pending_alerts()`  [INFERRED]
  README.md → bot/alerts.py
- `What the profile contributes` --references--> `Profile`  [INFERRED]
  docs/phase9-visa-eligibility.md → config/profile.py
- `New architecture` --references--> `load_targets()`  [INFERRED]
  docs/phase1-discovery-architecture.md → config/targets.py
- `Application deadline` --references--> `init_db()`  [INFERRED]
  docs/structured-jd-intelligence.md → core/db.py

## Import Cycles
- None detected.

## Communities (140 total, 15 thin omitted)

### Community 0 - "json"
Cohesion: 0.08
Nodes (28): effective_baseline(), effective_config_hash(), fingerprint_profile(), profile_hash(), public_config(), write_effective_baseline(), _decide_vector(), _recovery_for() (+20 more)

### Community 1 - "structured_jd.py"
Cohesion: 0.12
Nodes (38): _application_deadline(), _authorization(), AuthorizationEvidence, _availability(), _clause_at(), _clauses(), _clip(), _degree_state() (+30 more)

### Community 2 - "test_false_negative.py"
Cohesion: 0.14
Nodes (13): citizenship_restriction(), clearance_requirement(), _matches_any(), max_acceptable_years(), _posting(), test_clearance_words_must_be_about_clearance(), test_explicit_internship_title_survives_seniority_words(), test_missing_or_weak_evidence_does_not_filter() (+5 more)

### Community 3 - "test_phase0_baseline.py"
Cohesion: 0.17
Nodes (13): _enable_internship_only(), _posting(), test_experience_span_is_about_five_years_and_not_summed(), test_friendly_sponsorship_stays_eligible(), test_hostile_sponsorship_is_rejected(), test_internship_only_code_default_is_false(), test_internship_only_drops_non_internship_titles(), test_internship_only_keeps_internship_titles() (+5 more)

### Community 4 - "test_outcomes.py"
Cohesion: 0.10
Nodes (23): _handle_outcome_callback(), build_outcome_keyboard(), button(), outcome_label(), outcome_message_text(), OutcomePromptSummary, send_outcome_prompt(), send_pending_outcome_prompts() (+15 more)

### Community 5 - "call_with_resilience"
Cohesion: 0.08
Nodes (22): _backoff_delay(), call_with_resilience(), is_permanent_account_error(), is_transient(), LLMBillingError, LLMError, _attempt(), _create() (+14 more)

### Community 6 - "test_career_intelligence.py"
Cohesion: 0.08
Nodes (50): CareerIntelligence, _apply_reading(), assess_career(), attach_career_intelligence(), career_input_hash(), CareerReading, _clause(), _clip() (+42 more)

### Community 7 - "fit.py"
Cohesion: 0.11
Nodes (31): build_fit_system_blocks(), build_fit_user(), cached_fit(), _Dimension, evaluate_fit(), fit_context_block(), fit_is_current(), FitDecision (+23 more)

### Community 8 - "test_discovery.py"
Cohesion: 0.08
Nodes (37): load_targets(), allocate_units(), AllocItem, build_discovery_plan(), DiscoveryConfig, DiscoverySource, _enabled_queries(), enabled_query_texts() (+29 more)

### Community 9 - "test_openai_run_usage.py"
Cohesion: 0.09
Nodes (29): emit_openai_run_usage(), pop_openai_operation(), push_openai_operation(), _Chat, _ChatHolder, _ChatResponse, _ChatUsage, _Choice (+21 more)

### Community 10 - "evaluate"
Cohesion: 0.15
Nodes (25): evaluate(), sponsorship_signal(), test_sponsorship_and_false_friends(), _posting(), test_clearance_regex_pattern(), test_exclude_clearance_keyword(), test_exclude_high_yoe_requirement(), test_exclude_off_target_location() (+17 more)

### Community 11 - "workday_rest.py"
Cohesion: 0.07
Nodes (27): WorkdayTenant, redact_error(), _as_text(), _company_name(), fetch_all_workday(), _one(), _fetch_detail(), _fetch_listing_page() (+19 more)

### Community 12 - "conftest.py"
Cohesion: 0.13
Nodes (11): Testing conventions, reset_engine(), accept_or_reject(), profile_vec(), db_ready(), _disable_apply_pacing(), _disable_vector_gate(), _internship_only_off() (+3 more)

### Community 13 - "models.py"
Cohesion: 0.09
Nodes (25): Flow, Hash and upsert, Limits, Normalization, Phase 4 JD ingestion, content_hash(), _drop_boilerplate_lines(), _extract_body() (+17 more)

### Community 14 - "discovery_recall.py"
Cohesion: 0.05
Nodes (58): _find_cross_source_job(), canonicalize_job_url(), _is_tracking_param(), locations_agree(), locations_conflict(), normalize_title(), same_employer(), same_posting_url() (+50 more)

### Community 15 - "answers.py"
Cohesion: 0.08
Nodes (26): AnswerResolver, one(), answers_to_payload(), AnswerSource, _discovery_channel(), is_open_ended(), _latest_education(), _matches() (+18 more)

### Community 16 - "eligibility.py"
Cohesion: 0.17
Nodes (25): _ask_model(), _citizenship(), _clearance(), _current_student(), _dates(), _decision_from_job(), _dim(), DimensionResult (+17 more)

### Community 17 - "ingest.py"
Cohesion: 0.05
Nodes (48): _safe_close_stage(), build_coverage_report(), add_planned(), group_for(), CoverageReport, discovery_evidence(), fail_unrecorded(), GroupMetrics (+40 more)

### Community 18 - "get_job_by_id"
Cohesion: 0.21
Nodes (26): apply_pending(), get_job_by_id(), _touch_vector_score(), FakeApplicator, _script_reloads(), _seed_job(), test_allocation_removed_before_execution_is_skipped(), test_apply_linkedin_with_workday_url() (+18 more)

### Community 19 - "test_structured_jd.py"
Cohesion: 0.15
Nodes (17): StructuredJobDescription, attach_structured_jd(), extract_structured_jd(), get_structured_jd(), structured_jd_is_current(), _areas(), _job(), test_changed_upsert_drops_the_old_reading() (+9 more)

### Community 20 - "pipeline.py"
Cohesion: 0.10
Nodes (19): _allocated_ids(), _benchmark_tier_one_stage(), _generate_suggestions_stage(), _ingest_stage(), _note_skipped(), _pipeline_status(), PipelineSummary, _portfolio_stage() (+11 more)

### Community 21 - "TelegramClient"
Cohesion: 0.13
Nodes (3): HttpxTransport, TelegramClient, TelegramTransport

### Community 22 - "test_resume.py"
Cohesion: 0.14
Nodes (16): build_resume_data(), extract_job_terms(), _grounded_summary(), RankedBullet, reorder_skills(), score_bullet(), select_bullets(), SelectedExperience (+8 more)

### Community 23 - "scheduler.py"
Cohesion: 0.14
Nodes (8): build_scheduler(), parse_hhmm(), _noop(), test_build_scheduler_invalid_timezone(), test_build_scheduler_registers_jobs(), test_build_scheduler_skips_invalid_times(), test_parse_hhmm(), test_parse_hhmm_invalid()

### Community 24 - "test_monitoring.py"
Cohesion: 0.15
Nodes (27): _as_utc(), close_pipeline_run(), close_stage_run(), count_stale_jobs(), interrupt_stale_runs(), list_pipeline_runs(), list_stage_runs(), _moment() (+19 more)

### Community 25 - "diff.py"
Cohesion: 0.10
Nodes (30): apply_decided_suggestions(), load_profile(), _load_yaml(), get_role_baseline_by_role(), get_suggestions_for_job(), RoleBaseline, SkillPlacement, SkillProvenance (+22 more)

### Community 26 - "test_company_intelligence.py"
Cohesion: 0.26
Nodes (15): attach_company_intelligence(), FakeProvider, _job(), _posting(), test_ambiguous_names_stay_separate(), test_company_facts_do_not_change_scoring_signals(), test_company_sources_accumulate_and_a_failed_refresh_keeps_them(), test_complete_record_and_ignored_claims() (+7 more)

### Community 27 - "settings.py"
Cohesion: 0.08
Nodes (21): What still needs the user (before live runs), launch_context(), _new_context(), new_page(), save_storage_state(), save_session(), CredentialsFile, get_tenant_credentials() (+13 more)

### Community 28 - "test_pacing.py"
Cohesion: 0.11
Nodes (29): acquire(), AcquireResult, _clamp_multiplier(), _clock(), end_of_local_day(), gap_seconds(), is_pace_blocker(), note_pace_block() (+21 more)

### Community 29 - "test_pipeline_order_and_aggregation"
Cohesion: 0.09
Nodes (22): _FakeSummary, test_pipeline_order_and_aggregation(), fake_alerts(), fake_apply(), fake_ingestion(), fake_outcomes(), fake_prep(), fake_resume() (+14 more)

### Community 30 - "test_ingest_resilience.py"
Cohesion: 0.06
Nodes (38): _load_role_client(), run_ingestion(), _accept(), _run_jobspy(), _run_workday(), kill_process_group(), LineWorker, QueryTimeoutError (+30 more)

### Community 31 - "feedback.py"
Cohesion: 0.17
Nodes (21): list_events_for_applications(), _adjustment(), _band(), build_feedback(), _case_from_rows(), _counts(), feedback_config_hash(), FeedbackCase (+13 more)

### Community 32 - "test_calibration.py"
Cohesion: 0.29
Nodes (17): build_calibration(), CalibrationReport, load_calibration_config(), run_calibration(), load_feedback_config(), _calibration(), _case(), _feedback() (+9 more)

### Community 33 - "extract_company_signals"
Cohesion: 0.38
Nodes (5): _compact(), extract_company_signals(), _signal(), _snippet(), test_signals_are_explicit_and_multi_valued()

### Community 34 - "test_eligibility.py"
Cohesion: 0.11
Nodes (23): assign_eligibility(), attach_eligibility(), eligibility_column_types(), eligibility_is_current(), EligibilityDecision, evaluate_eligibility(), profile_eligibility_hash(), _job() (+15 more)

### Community 35 - "targets.py"
Cohesion: 0.06
Nodes (24): _load_yaml(), parse_workday_url(), reload_targets(), SearchConfig, Targets, WorkdayParts, test_current_config_dry_run_states_adapter_call_counts(), test_dry_run_does_not_fetch_or_write() (+16 more)

### Community 36 - "Remaining Manual Setup"
Cohesion: 0.08
Nodes (25): 2a. Find a Workday URL, 2b. Edit `config/targets.yaml`, 3a. Run the save-session helper, 3b. What you do in the browser, 4a. Discover jobs (LinkedIn / Indeed + any real Workday tenants), 4b. Score with Gemini, 4c. Attach your base resume to staged jobs, 4d. Send LinkedIn/Indeed application prep pack (Telegram) (+17 more)

### Community 37 - "linkedin_people.py"
Cohesion: 0.07
Nodes (25): auto_discover_peers(), _crawl(), BlockerError, build_people_search_url(), _detect_blocker(), discover_peers(), extract_profile_urls(), _heuristic_parse() (+17 more)

### Community 38 - "SQLModel"
Cohesion: 0.22
Nodes (10): ApplicationEvent, CalibrationMetric, CalibrationRun, get_application_events(), get_calibration_metrics(), get_calibration_run(), save_calibration_run(), load_persisted_calibration() (+2 more)

### Community 39 - "test_phase13_shortlist.py"
Cohesion: 0.09
Nodes (34): get_jobs_by_status(), _cmd_list_apply(), apply_shortlist(), _close_enough(), _company_key(), _company_ok(), config_hash(), _diversify() (+26 more)

### Community 40 - "test_feedback.py"
Cohesion: 0.38
Nodes (8): shrink_rate(), _case(), _config(), _signal(), test_bands_families_and_sparse_subfamily(), test_cutoff_hides_future_submissions_and_outcomes(), test_funnel_does_not_treat_unknown_as_rejection(), test_shrinkage_and_adjustment_bounds()

### Community 41 - "pytest"
Cohesion: 0.14
Nodes (26): Address, Education, Exclusions, Experience, Identity, Preferences, WorkAuthorization, _make_base_pdf() (+18 more)

### Community 42 - "db.py"
Cohesion: 0.05
Nodes (41): _absolute_sqlite_url(), _company_name(), _dialect_name(), _drop_structured_jd(), _ensure_company_columns(), _ensure_job_columns(), _ensure_pipeline_stage_columns(), FeedbackRun (+33 more)

### Community 43 - "compiler.py"
Cohesion: 0.10
Nodes (20): apply_fit_caps(), _baseline_pdf_for_job(), clean_name(), compile_for_job(), compile_pending(), compile_resume(), compile_resume_data(), FitReport (+12 more)

### Community 44 - "prep.py"
Cohesion: 0.09
Nodes (31): _dedupe(), _fit_lines(), _load_canonical_shortlist(), _mark_sent(), _notify_empty(), PrepSummary, render_job_card(), render_shortlist() (+23 more)

### Community 45 - "re"
Cohesion: 0.07
Nodes (28): build_baseline_resume_data(), _normalize(), _slugify_role(), _synthetic_job_for_role(), aggregate_role_skills(), AggregatedSkill, _categorize(), extract_top_skills() (+20 more)

### Community 46 - "test_workload_limits.py"
Cohesion: 0.24
Nodes (18): _ChatHolder, _EmbedHolder, _env(), _FitClient, _rows(), _seed_jobs(), test_embed_cap_limits_cumulative_inputs_across_batches(), test_inflight_score_persists_and_later_jobs_do_not_start() (+10 more)

### Community 47 - "role_classify.py"
Cohesion: 0.15
Nodes (18): _clause_containing(), _clip_items(), _deterministic(), _is_interaction(), _item_text(), _ModelLabel, _parse_model(), _phrase_hits() (+10 more)

### Community 48 - "test_scorer.py"
Cohesion: 0.13
Nodes (13): approx_tokens(), parse_score(), build_scoring_user(), test_parse_score_handles_braces_inside_strings(), test_parse_score_rejects_non_numeric_score(), test_compute_tier_thresholds(), test_minify_job_keeps_head_and_tail(), test_parse_score_clamps() (+5 more)

### Community 50 - "test_application_portfolio.py"
Cohesion: 0.07
Nodes (49): allocate_portfolio(), can_take(), identity(), take(), allocated_jobs(), apply_portfolio(), _bucket(), bucket_weights() (+41 more)

### Community 51 - "test_priority.py"
Cohesion: 0.19
Nodes (17): apply_priority(), priority_is_current(), PriorityDecision, role_family_component(), _job(), test_dream_company_is_only_a_configured_boost(), test_eligibility_unknown_is_not_ineligible(), test_fit_and_role_family_order_attention() (+9 more)

### Community 52 - "Phase 5 role classification"
Cohesion: 0.29
Nodes (6): Inputs, Limits, Output, Phase 5 role classification, Taxonomy, When it runs again

### Community 53 - "test_application_deadline.py"
Cohesion: 0.09
Nodes (28): _structured_view(), ApplicationDeadline, _clip(), empty_application_deadline(), _excluded(), extract_application_deadline(), _from_match(), _named() (+20 more)

### Community 54 - "test_apply_url.py"
Cohesion: 0.23
Nodes (10): ApplyKind, classify_apply_url(), _host(), is_automateable_apply_url(), is_workday_url(), workday_parts(), test_classify_company_site(), test_classify_linkedin_listing() (+2 more)

### Community 55 - "priority.py"
Cohesion: 0.15
Nodes (20): company_domain_component(), _company_signals(), _components(), dream_company_component(), eligibility_component(), _explicit_sections(), fit_component(), freshness_component() (+12 more)

### Community 56 - "main.py"
Cohesion: 0.24
Nodes (12): _cmd_benchmark(), _cmd_build_baseline(), _cmd_health(), _cmd_poll(), _cmd_prep_pack(), _cmd_run_once(), _cmd_save_linkedin_session(), _cmd_send_reviews() (+4 more)

### Community 57 - "test_vector_recovery.py"
Cohesion: 0.14
Nodes (49): profile_embed_text(), profile_hash(), score_pending(), FakeClient, _enable(), FakeEmbedder, _map(), _seed() (+41 more)

### Community 58 - "Benchmark — Product Manager @ T-Mobile"
Cohesion: 0.33
Nodes (5): Benchmark — Product Manager @ T-Mobile, Dimensions, Gaps, Recommendations, Strengths

### Community 59 - "FakeTransport"
Cohesion: 0.10
Nodes (29): _decision_caption(), handle_callback(), decode_callback(), encode_callback(), ReviewAction, _should_retry_telegram(), _callback_update(), FakeSubmitter (+21 more)

### Community 60 - "MonkeyPatch"
Cohesion: 0.13
Nodes (9): test_health_command_prints_no_secrets(), test_health_reports_database_failure(), test_health_reports_invalid_configuration(), test_pipeline_failure_outside_a_stage_is_failed(), boom(), test_pipeline_partial_when_a_stage_fails(), ok(), test_pre_stage_setup_failure_marks_the_run_failed() (+1 more)

### Community 61 - "OpenAIClient"
Cohesion: 0.12
Nodes (24): OpenAIClient, test_openai_client_scores_json(), create(), _Chat, _Choice, _complete(), _CompletionDetails, _Completions (+16 more)

### Community 62 - "test_application_tracker.py"
Cohesion: 0.11
Nodes (26): _add_event(), application_history(), application_method(), backfill_submitted_applications(), _event_exists(), _get_or_create(), record_manual_review(), record_outcome() (+18 more)

### Community 63 - "pathlib"
Cohesion: 0.14
Nodes (10): build_keyboard(), build_review_caption(), format_answers_message(), format_cover_letter_message(), ReviewSummary, _send_one(), send_pending_reviews(), get_unsent_pending_reviews() (+2 more)

### Community 64 - "benchmark/engine.py"
Cohesion: 0.13
Nodes (17): BenchmarkReport, BenchmarkSummary, build_benchmark(), _derive_seniority(), DimensionScore, _education_rank(), _median(), _norm() (+9 more)

### Community 65 - "get_health_report"
Cohesion: 0.18
Nodes (14): PipelineRun, PipelineStageRun, _brief(), format_health_report(), get_health_report(), _recent_failures(), _repeated_failures(), _run_view() (+6 more)

### Community 66 - "discovery_experiment.py"
Cohesion: 0.07
Nodes (55): account_executions(), _baseline_slot_reason(), _baseline_slots(), build_schedule(), _classify_incremental(), compare_arms(), _execute(), _execute_phrase() (+47 more)

### Community 67 - "Job"
Cohesion: 0.06
Nodes (75): Data model (core/db.py), Status lifecycle, build_alert_caption(), _send_one(), send_pending_alerts(), _assign_canonical_url(), _incoming_description_unusable(), Job (+67 more)

### Community 68 - "test_company_intelligence_v2.py"
Cohesion: 0.16
Nodes (10): CompanyLookupResult, CompanySourceDocument, merge_company_signals(), refresh_company_intelligence(), _one(), _Provider, _signals(), test_authoritative_source_wins_a_contradiction() (+2 more)

### Community 71 - "Profile"
Cohesion: 0.12
Nodes (18): Profile, reload_profile(), compute_tier(), is_dream_company(), prerank_jobs(), prerank_score(), _source_weight(), _job() (+10 more)

### Community 72 - "AGENTS.md"
Cohesion: 0.11
Nodes (10): Build order and status, Coding conventions, Commands, Confirmed product decisions, Project, Repository layout, Scoring specifics (Step 3), Tech stack (+2 more)

### Community 73 - "linkedin_jobspy.py"
Cohesion: 0.10
Nodes (18): How to read it, main(), _one(), _records(), _dataframe_to_postings(), _effective_windows(), _explicit_company_url(), _external_id() (+10 more)

### Community 75 - "workday.py"
Cohesion: 0.11
Nodes (17): action_delay_bounds(), human_delay(), type_like_human(), typing_delay_bounds(), click_by_role(), click_next(), _collect_labeled_fields(), detect_blocker() (+9 more)

### Community 76 - "Phase 1 discovery architecture"
Cohesion: 0.11
Nodes (16): 40/40/15/5 priority model, Current problem, New architecture, Phase 1 discovery architecture, Provenance, Purpose, Role families, Search allocation (+8 more)

### Community 77 - "Phase 0 baseline"
Cohesion: 0.22
Nodes (8): Candidate baseline, Discovery baseline, Local versus production, Phase 0 baseline, Production baseline, Scoring baseline, Sponsorship behavior locked by tests, Tests

### Community 78 - "test_webhook.py"
Cohesion: 0.26
Nodes (5): client(), test_health(), test_webhook_ignored_without_callback(), test_webhook_rejects_bad_secret(), test_webhook_routes_callback()

### Community 79 - "classify_role"
Cohesion: 0.10
Nodes (30): get_job_by_source_id(), classification_is_current(), classify_role(), _apply_role_classification(), _FakeClient, _jd(), test_classification_persists_and_does_not_filter(), test_classifier_version_bump_invalidates_phase5_v1() (+22 more)

### Community 80 - "Priority 2.0"
Cohesion: 0.29
Nodes (6): Freshness, dream company, and workflow, Hash, Priority 2.0, Program and domain evidence, Role alignment, Weights

### Community 81 - "WorkdaySubmitter"
Cohesion: 0.18
Nodes (7): SessionMissingError, WorkdaySubmitter, test_submit_generic_exception(), test_submit_missing_url(), test_submit_session_missing(), boom_launch(), test_submit_unparseable_without_tenant()

### Community 82 - "_chat_ok"
Cohesion: 0.16
Nodes (8): _Chat, _chat_ok(), _ChatResponse, _Choice, _Completions, _InFlightCompletions, _Msg, _Usage

### Community 83 - "runner.py"
Cohesion: 0.10
Nodes (11): ApplyRunner, ApplySummary, _eligible(), _ensure_tenant(), _log_explicit_skip(), _ready_for_explicit_apply(), _reload_job(), Applicator (+3 more)

### Community 84 - "run_service"
Cohesion: 0.17
Nodes (4): _cmd_serve(), run_service(), test_run_service_stops_without_poller(), test_run_service_with_poller_respects_stop()

### Community 85 - "Discovery recall benchmark"
Cohesion: 0.10
Nodes (16): Discovery recall benchmark, Label corrections on 2026-10-04, Limits, Matching, Reproduce, What is checked in, Discovery run observability, Query timeout and incremental save (+8 more)

### Community 86 - "typing"
Cohesion: 0.06
Nodes (24): AlertSummary, handle_message(), _handle_suggest_callback(), _safe_answer(), process_updates(), run_polling(), Submitter, decide_suggestion() (+16 more)

### Community 87 - "test_trial_workflow.py"
Cohesion: 0.13
Nodes (12): ScoringSafetyHalt, test_safety_halt_does_not_send_or_apply(), halt(), ingest(), test_trial_env_matches_the_settings_parser(), test_trial_sqlite_url_creates_the_schema(), test_trial_workflow_is_manual_and_isolated(), _trial_text() (+4 more)

### Community 88 - "Career Intelligence"
Cohesion: 0.33
Nodes (5): Cache, Career Intelligence, Dimensions, Failures, Overall score

### Community 89 - "test_main_cli.py"
Cohesion: 0.15
Nodes (9): test_default_command_is_serve(), test_doctor_cli(), test_poll_invokes_run_polling(), test_prep_pack_cli(), test_run_once_invokes_pipeline(), test_send_reviews_invokes_once(), test_serve_invokes_run_service(), test_tailor_resume_cli() (+1 more)

### Community 90 - "Phase 8 company intelligence"
Cohesion: 0.29
Nodes (6): Names and reuse, Phase 8 company intelligence, Schema, Sources, What it is, What this phase does not change

### Community 91 - "test_llm_provider.py"
Cohesion: 0.10
Nodes (21): LLM client layer (`scorer/clients.py`), build_llm_client(), GeminiClient, _FakeAio, _FakeAsyncModels, _FakeCandidate, _FakeGenaiClient, _FakeGenerateResponse (+13 more)

### Community 93 - "get_settings"
Cohesion: 0.06
Nodes (22): get_settings(), cache_block(), compact_json_dumps(), minify_job(), cap_cover_letter(), _fallback_cover_letter(), generate_cover_letter(), _vectors_from_response() (+14 more)

### Community 94 - "test_openai_request_gate.py"
Cohesion: 0.11
Nodes (31): get_openai_request_ledger(), OpenAIBudgetExceeded, reset_openai_request_ledger(), _Chat, _ChatClient, _ChatResponse, _Choice, _complete() (+23 more)

### Community 95 - "company_intelligence.py"
Cohesion: 0.17
Nodes (17): CompanyIntelligence, _accumulate_sources(), _apply_context(), _apply_facts(), _by_key(), _clear_facts(), _confidence_for(), _context_from() (+9 more)

### Community 96 - "load_monitoring_config"
Cohesion: 0.36
Nodes (6): load_monitoring_config(), monitoring_config_hash(), _require_int(), _validate(), validate_operational_config(), test_monitoring_config_is_versioned()

### Community 97 - "Phase 16 feedback learning"
Cohesion: 0.33
Nodes (5): Evidence and shrinkage, Phase 16 feedback learning, Rates, Segments, Who is counted

### Community 98 - "scorer/engine.py"
Cohesion: 0.05
Nodes (32): is_openai_safety_error(), LLMClient, build_embedder(), _cache_path(), clears_threshold(), cosine(), Embedder, EmbedInputLimitReached (+24 more)

### Community 99 - "RawPosting"
Cohesion: 0.08
Nodes (28): hash_fallback(), RawPosting, to_job(), test_to_job_stamps_workday_tenant_from_linkedin_url(), test_company_enrichment_failure_does_not_stop_ingestion(), one_posting(), _posting(), test_run_ingestion_noop() (+20 more)

### Community 100 - "run_pipeline"
Cohesion: 0.09
Nodes (20): Bounded trial, Comparing with the OpenAI dashboard, OpenAI usage summary, What the line contains, Architecture, Backlog diagnostics, CLI, Configuration (+12 more)

### Community 101 - "calibration.py"
Cohesion: 0.13
Nodes (29): _append_buckets(), _append_short_target(), _append_slice(), _append_target_metrics(), _append_topk(), brier_score(), _bucket_name(), calibration_config_hash() (+21 more)

### Community 102 - "_persist_postings"
Cohesion: 0.13
Nodes (9): HttpCompanyIntelProvider, _reliable_source_url(), trustworthy_company_source(), _persist_postings(), _PersistCounts, test_company_url_is_not_guessed_or_taken_from_the_job_page(), test_http_provider_handles_timeout_and_malformed_pages(), ok() (+1 more)

### Community 103 - "Phase 15 application tracker"
Cohesion: 0.33
Nodes (5): Method and time, Phase 15 application tracker, States and outcomes, What this is not, When a row is created

### Community 104 - "_build_doctor_report"
Cohesion: 0.36
Nodes (4): _build_doctor_report(), _count_jobs(), _print_doctor_report(), _unwrap()

### Community 105 - "normalize_company_name"
Cohesion: 0.29
Nodes (6): canonical_company_name(), normalize_company_name(), _without_trailing_suffix(), test_legal_suffixes_do_not_collapse_distinct_names(), test_normalization_is_deterministic(), test_version_and_normalization_stay_explicit()

### Community 106 - "3. Hard filters (before any model)"
Cohesion: 0.18
Nodes (11): 3.10 What a survivor looks like, 3.1 Company blocklist, 3.2 Exclusion keywords, 3.3 Clearance language, 3.4 Staffing agencies, 3.5 Internship gate, 3.6 Seniority filter (separate from the internship gate), 3.7 Years of experience (+3 more)

### Community 107 - "extract_company_facts"
Cohesion: 0.29
Nodes (5): extract_company_facts(), merge_company_facts(), test_extractor_keeps_unstated_facts_null(), test_merge_company_facts_keeps_omitted_fields(), test_prestige_language_is_not_a_fact()

### Community 109 - "Job Agent"
Cohesion: 0.13
Nodes (14): Application prep packs (LinkedIn / Indeed), Job Agent, Layout, LinkedIn peer benchmarking (optional, off by default), Resumes (Step 4), Run automation (Step 5), Run ingestion (Step 2), Run review bot (Step 6) (+6 more)

### Community 110 - "calculate_priority"
Cohesion: 0.17
Nodes (19): calculate_priority(), _combine(), load_priority_config(), _reasons(), test_weights_sum_to_100(), _job(), _signal(), test_confidence_and_structured_evidence() (+11 more)

### Community 111 - "Phase 12 priority ranking"
Cohesion: 0.50
Nodes (3): Components, Phase 12 priority ranking, Version

### Community 112 - "test_doctor.py"
Cohesion: 0.44
Nodes (7): _cmd_doctor(), _job(), test_doctor_cooldown(), test_doctor_empty_db(), test_doctor_outcomes(), test_doctor_vector_gate(), test_doctor_with_jobs()

### Community 113 - "generate_prep_pack"
Cohesion: 0.10
Nodes (13): _answer_item(), build_job_section(), compile_prep_pdf(), generate_prep_pack(), PrepPackResult, render_markdown(), FakeClient, _job() (+5 more)

### Community 114 - "Structured JD intelligence"
Cohesion: 0.33
Nodes (5): Application deadline, Cache, Limits, Structured JD intelligence, What is stored

### Community 115 - "Company intelligence 2.0"
Cohesion: 0.33
Nodes (5): Company intelligence 2.0, Company versus job, Sources and refresh, What it does not store, What it stores

### Community 116 - "filters.py"
Cohesion: 0.15
Nodes (10): _clearance_clauses(), FilterResult, has_internship_signal(), _haystack(), location_acceptable(), _location_ok(), _mandatory_years(), _qualifier_is_mandatory() (+2 more)

### Community 118 - "get_recently_applied_companies"
Cohesion: 0.20
Nodes (8): get_recently_applied_companies(), Capacity, Decisions, Phase 14 application portfolio, Pipeline, Role-family mix, What counts as a recent application, Who can be allocated

### Community 119 - "sort_by_priority"
Cohesion: 0.29
Nodes (6): Configuration, Phase 13 shortlist, Pipeline, Selection, sort_by_priority(), posted()

### Community 121 - "test_posting_cap_is_safe_when_batches_arrive_together"
Cohesion: 0.38
Nodes (7): _posting(), test_posting_cap_does_not_persist_or_classify_the_next_row(), fetch(), spy_classify(), test_posting_cap_is_safe_when_batches_arrive_together(), fetch(), spy_classify()

### Community 122 - "Multi-dimensional role classification"
Cohesion: 0.29
Nodes (6): Cache, Contract, Function versus interaction, Multi-dimensional role classification, Non-goals, What the classifier reads

### Community 123 - "_input_hash"
Cohesion: 0.60
Nodes (4): _as_utc(), _freshness_day(), _input_hash(), _iso()

### Community 124 - "migrate_to_neon.py"
Cohesion: 0.22
Nodes (6): _cell(), _copy_table(), _counts(), main(), _reset_sequences(), _row()

### Community 125 - "_Embeddings"
Cohesion: 0.33
Nodes (3): _Embeddings, _EmbedItem, _EmbedResponse

### Community 126 - "OpenAIRequestLedger"
Cohesion: 0.13
Nodes (3): OpenAIBillingHalted, OpenAIRequestBlocked, OpenAIRequestLedger

### Community 129 - "test_role_weights.py"
Cohesion: 0.14
Nodes (19): get_role_family_weight(), load_role_family_weights(), _validate(), weight_for_subfamily(), test_feedback_config_keeps_priority_integration_off(), test_company_and_vector_are_not_weight_inputs(), test_discovery_capacity_stays_independent(), test_discovery_labels_do_not_choose_the_weight() (+11 more)

### Community 130 - "clients.py"
Cohesion: 0.07
Nodes (21): _add_measured(), _add_token(), AnthropicClient, _attempt(), _Attempt, _blank_bucket(), _chat_usage(), _embedding_usage() (+13 more)

### Community 131 - "build_parser"
Cohesion: 0.50
Nodes (3): build_parser(), test_cli_defaults_to_dry_run(), test_build_parser_default_serve()

### Community 143 - "Phase 7 role-family weighting"
Cohesion: 0.08
Nodes (21): Dimensions, Not in this phase, Output, Phase 6 candidate fit, When the model is not called, Canonical portfolio, Configuration, Four different questions (+13 more)

### Community 146 - "2. Where jobs come from"
Cohesion: 0.29
Nodes (7): 2.1 Search terms, 2.2 Sites and the exact JobSpy arguments, 2.3 How each site treats "posted in the last 36 hours", 2.4 What is kept from a JobSpy row, 2.5 Workday, separately from LinkedIn, 2.6 Save and dedupe, 2. Where jobs come from

### Community 151 - "How jobs are found, filtered, scored, and sent"
Cohesion: 0.06
Nodes (31): 10. File map, 1. What a run is, 4.1 Pre-score rank (`prerank_score`), 4.2 Embedding gate (this does drop jobs), 4.3 Fit-model cap, 4. How results are prioritised today, 5.1 What the model is, 5.2 The two inputs (+23 more)

## Knowledge Gaps
- **184 isolated node(s):** `job-agent`, `ScrapeSummary`, `_Sites`, `_FakeAio`, `Project` (+179 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 1236 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **15 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Job` connect `Job` to `json`, `structured_jd.py`, `test_false_negative.py`, `test_role_weights.py`, `test_outcomes.py`, `test_career_intelligence.py`, `fit.py`, `test_openai_run_usage.py`, `models.py`, `discovery_recall.py`, `answers.py`, `eligibility.py`, `ingest.py`, `get_job_by_id`, `test_structured_jd.py`, `test_resume.py`, `test_monitoring.py`, `diff.py`, `test_company_intelligence.py`, `test_pacing.py`, `test_ingest_resilience.py`, `feedback.py`, `test_calibration.py`, `test_eligibility.py`, `SQLModel`, `test_phase13_shortlist.py`, `test_feedback.py`, `pytest`, `db.py`, `compiler.py`, `prep.py`, `re`, `test_workload_limits.py`, `test_scorer.py`, `test_application_portfolio.py`, `test_priority.py`, `test_application_deadline.py`, `priority.py`, `main.py`, `test_vector_recovery.py`, `FakeTransport`, `OpenAIClient`, `test_application_tracker.py`, `pathlib`, `benchmark/engine.py`, `get_health_report`, `Profile`, `workday.py`, `classify_role`, `WorkdaySubmitter`, `runner.py`, `typing`, `get_settings`, `company_intelligence.py`, `scorer/engine.py`, `RawPosting`, `_build_doctor_report`, `calculate_priority`, `test_doctor.py`, `generate_prep_pack`, `filters.py`, `sort_by_priority`, `_input_hash`, `migrate_to_neon.py`?**
  _High betweenness centrality (0.155) - this node is a cross-community bridge._
- **Are the 179 inferred relationships involving `Job` (e.g. with `Data model (core/db.py)` and `AnswerResolver`) actually correct?**
  _`Job` has 179 INFERRED edges - model-reasoned connections that need verification._
- **What connects `job-agent`, `ScrapeSummary`, `_Sites` to the rest of the system?**
  _184 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `json` be split into smaller, more focused modules?**
  _Cohesion score 0.08055152394775036 - nodes in this community are weakly interconnected._
- **Why does `Profile` connect `Profile` to `json`, `test_false_negative.py`, `test_phase0_baseline.py`, `test_career_intelligence.py`, `fit.py`, `evaluate`, `answers.py`, `Phase 7 role-family weighting`, `eligibility.py`, `get_job_by_id`, `ingest.py`, `test_resume.py`, `How jobs are found, filtered, scored, and sent`, `diff.py`, `test_ingest_resilience.py`, `test_eligibility.py`, `pytest`, `compiler.py`, `prep.py`, `re`, `test_scorer.py`, `test_priority.py`, `priority.py`, `test_vector_recovery.py`, `benchmark/engine.py`, `Job`, `AGENTS.md`, `linkedin_jobspy.py`, `workday.py`, `runner.py`, `typing`, `get_settings`, `scorer/engine.py`, `_persist_postings`, `calculate_priority`, `generate_prep_pack`, `filters.py`, `_input_hash`?**
  _High betweenness centrality (0.096) - this node is a cross-community bridge._
- **Are the 260 inferred relationships involving `Profile` (e.g. with `AnswerResolver` and `_latest_education()`) actually correct?**
  _`Profile` has 260 INFERRED edges - model-reasoned connections that need verification._
- **Should `structured_jd.py` be split into smaller, more focused modules?**
  _Cohesion score 0.11717171717171718 - nodes in this community are weakly interconnected._