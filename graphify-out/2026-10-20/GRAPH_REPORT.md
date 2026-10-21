# Graph Report - Automatic job search  (2026-10-20)

## Corpus Check
- 219 files · ~192,000 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 13 file(s) not represented in the graph (top: (none) 8, .typ 2, .example 1)

## Summary
- 4034 nodes · 13943 edges · 142 communities (133 shown, 9 thin omitted)
- Extraction: 89% EXTRACTED · 11% INFERRED · 0% AMBIGUOUS · INFERRED: 1480 edges (avg confidence: 0.94)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `548ea678`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- vector_recovery.py
- structured_jd.py
- test_fit.py
- RawPosting
- handlers.py
- call_with_resilience
- test_career_intelligence.py
- test_feedback.py
- test_discovery.py
- test_openai_run_usage.py
- Profile
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
- test_discovery_observability.py
- pacing.py
- run_pipeline
- test_ingest_resilience.py
- typing
- test_calibration.py
- LLMClient
- test_eligibility.py
- settings.py
- Remaining Manual Setup
- linkedin_people.py
- monitoring.py
- test_phase13_shortlist.py
- Status
- profile.py
- load_persisted_calibration
- compiler.py
- test_jobspy_exception_keeps_earlier_observations
- skills.py
- test_workload_limits.py
- role_classify.py
- get_job_by_id
- Settings
- test_application_portfolio.py
- test_priority.py
- Phase 5 role classification
- ScoreRaw
- models.py
- priority.py
- main.py
- test_vector_recovery.py
- Benchmark — Product Manager @ T-Mobile
- asyncio
- score_pending
- OpenAIClient
- tracker.py
- datetime
- migrate_to_neon.py
- 5. How fit is scored
- discovery_experiment.py
- test_trial_workflow.py
- db.py
- job-agent
- prerank_score
- browser.py
- linkedin_jobspy.py
- phase10-false-negative-protection.md
- benchmark/engine.py
- Phase 1 discovery architecture
- Phase 0 baseline
- test_webhook.py
- classify_role
- Priority 2.0
- How jobs are found, filtered, scored, and sent
- vault.py
- runner.py
- application_deadline.py
- Discovery recall benchmark
- suggest.py
- 2. Where jobs come from
- 8. The weight discussion (not built)
- test_pacing.py
- Phase 8 company intelligence
- pytest
- correction1-recruiting-universe.md
- outreach.py
- test_openai_request_gate.py
- company_intelligence.py
- feedback.py
- Phase 16 feedback learning
- scorer/engine.py
- test_application_deadline.py
- test_monitoring.py
- calibration.py
- test_cover_letter.py
- Phase 15 application tracker
- json
- WorkdaySubmitter
- 3. Hard filters (before any model)
- _persist_postings
- 9. Pain points we have actually hit or spelled out
- Job Agent
- calculate_priority
- Phase 12 priority ranking
- Phase 6 candidate fit
- test_prep_builder.py
- init_db
- Company intelligence 2.0
- filters.py
- phase17-calibration-benchmark.md
- telegram_webhook
- Job
- vector-recovery.md
- Phase 18 — Production reliability and monitoring
- Multi-dimensional role classification
- 6. What is sent to you
- alerts.py
- sort_by_priority
- get_settings
- prep.py
- Tier
- test_role_weights.py
- clients.py
- service.py
- workday.py
- FakeClient
- test_doctor.py
- session_scope
- Phase 9 visa and eligibility
- Phase 7 role-family weighting
- _build_doctor_report
- re
- is_pace_blocker
- test_baseline.py

## God Nodes (most connected - your core abstractions)
1. `Job` - 386 edges
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
- `Run review bot (Step 6)` --references--> `send_pending_alerts()`  [INFERRED]
  README.md → bot/alerts.py
- `What the profile contributes` --references--> `Profile`  [INFERRED]
  docs/phase9-visa-eligibility.md → config/profile.py
- `New architecture` --references--> `load_targets()`  [INFERRED]
  docs/phase1-discovery-architecture.md → config/targets.py
- `Health states` --references--> `get_health_report()`  [INFERRED]
  docs/phase18-production-reliability-monitoring.md → orchestrator/health.py
- `Pipeline` --references--> `prepare_pending()`  [INFERRED]
  docs/phase13-shortlist.md → resume/compiler.py

## Import Cycles
- None detected.

## Communities (142 total, 9 thin omitted)

### Community 0 - "vector_recovery.py"
Cohesion: 0.22
Nodes (14): _compiled(), _confidence(), config_hash(), evaluate_recovery(), _family_group(), load_recovery_config(), _mba_program(), _names() (+6 more)

### Community 1 - "structured_jd.py"
Cohesion: 0.13
Nodes (37): _authorization(), AuthorizationEvidence, _availability(), _clause_at(), _clauses(), _clip(), _degree_state(), _domain() (+29 more)

### Community 2 - "test_fit.py"
Cohesion: 0.09
Nodes (37): build_fit_system_blocks(), build_fit_user(), cached_fit(), _Dimension, evaluate_fit(), fit_context_block(), fit_is_current(), FitDecision (+29 more)

### Community 3 - "RawPosting"
Cohesion: 0.11
Nodes (14): _dedupe(), RawPosting, test_company_enrichment_failure_does_not_stop_ingestion(), one_posting(), test_within_run_duplicates_are_counted_separately(), test_provider_failure_does_not_break_ingestion(), one_posting(), _family() (+6 more)

### Community 4 - "handlers.py"
Cohesion: 0.10
Nodes (24): _decision_caption(), _handle_outcome_callback(), _safe_answer(), build_outcome_keyboard(), outcome_label(), outcome_message_text(), OutcomePromptSummary, send_outcome_prompt() (+16 more)

### Community 5 - "call_with_resilience"
Cohesion: 0.09
Nodes (19): _backoff_delay(), call_with_resilience(), is_permanent_account_error(), is_transient(), LLMBillingError, LLMError, _status_code(), suggested_delay() (+11 more)

### Community 6 - "test_career_intelligence.py"
Cohesion: 0.08
Nodes (51): CareerIntelligence, _apply_reading(), assess_career(), attach_career_intelligence(), career_input_hash(), CareerReading, _clause(), _clip() (+43 more)

### Community 7 - "test_feedback.py"
Cohesion: 0.20
Nodes (16): build_feedback(), _counts(), _group_hit(), _in_cohort(), _rate(), _rates(), shrink_rate(), _strong_count() (+8 more)

### Community 8 - "test_discovery.py"
Cohesion: 0.07
Nodes (38): load_targets(), allocate_units(), AllocItem, build_discovery_plan(), DiscoveryConfig, DiscoverySource, _enabled_queries(), enabled_query_texts() (+30 more)

### Community 9 - "test_openai_run_usage.py"
Cohesion: 0.09
Nodes (29): emit_openai_run_usage(), pop_openai_operation(), push_openai_operation(), _Chat, _ChatHolder, _ChatResponse, _ChatUsage, _Choice (+21 more)

### Community 10 - "Profile"
Cohesion: 0.09
Nodes (43): Profile, evaluate(), max_acceptable_years(), sponsorship_signal(), test_internship_signal_matches_the_existing_gate(), test_sponsorship_and_false_friends(), test_missing_or_weak_evidence_does_not_filter(), _posting() (+35 more)

### Community 11 - "workday_rest.py"
Cohesion: 0.07
Nodes (27): WorkdayTenant, redact_error(), _as_text(), _company_name(), fetch_all_workday(), _one(), _fetch_detail(), _fetch_listing_page() (+19 more)

### Community 12 - "conftest.py"
Cohesion: 0.18
Nodes (7): Testing conventions, db_ready(), _disable_apply_pacing(), _disable_vector_gate(), _internship_only_off(), _reset_openai_request_ledger_between_tests(), tmp_db()

### Community 13 - "textclean.py"
Cohesion: 0.07
Nodes (30): Cache, Career Intelligence, Dimensions, Failures, Overall score, Flow, Hash and upsert, Limits (+22 more)

### Community 14 - "discovery_recall.py"
Cohesion: 0.08
Nodes (40): _assign_canonical_url(), _find_cross_source_job(), canonicalize_job_url(), _is_tracking_param(), normalize_title(), same_employer(), same_posting_url(), strong_field_match() (+32 more)

### Community 15 - "answers.py"
Cohesion: 0.08
Nodes (25): AnswerResolver, one(), answers_to_payload(), AnswerSource, _discovery_channel(), is_open_ended(), _latest_education(), _matches() (+17 more)

### Community 16 - "eligibility.py"
Cohesion: 0.15
Nodes (27): _ask_model(), _citizenship(), _clearance(), _current_student(), _dates(), _decision_from_job(), _dim(), DimensionResult (+19 more)

### Community 17 - "ingest.py"
Cohesion: 0.07
Nodes (38): build_coverage_report(), add_planned(), group_for(), CoverageReport, discovery_evidence(), fail_unrecorded(), GroupMetrics, _jsonable() (+30 more)

### Community 18 - "apply_pending"
Cohesion: 0.21
Nodes (24): apply_pending(), FakeApplicator, _script_reloads(), _seed_job(), test_allocation_removed_before_execution_is_skipped(), test_apply_linkedin_with_workday_url(), test_apply_pending_blocker(), test_apply_pending_empty() (+16 more)

### Community 19 - "test_structured_jd.py"
Cohesion: 0.15
Nodes (17): StructuredJobDescription, attach_structured_jd(), extract_structured_jd(), get_structured_jd(), structured_jd_is_current(), _areas(), _job(), test_changed_upsert_drops_the_old_reading() (+9 more)

### Community 20 - "pipeline.py"
Cohesion: 0.10
Nodes (19): _allocated_ids(), _benchmark_tier_one_stage(), _generate_suggestions_stage(), _ingest_stage(), _note_skipped(), _pipeline_status(), PipelineSummary, _portfolio_stage() (+11 more)

### Community 21 - "TelegramClient"
Cohesion: 0.10
Nodes (8): HttpxTransport, TelegramClient, TelegramTransport, test_answer_callback(), test_chat_id_property(), test_get_updates_extends_http_timeout(), test_send_document_builds_payload(), test_send_photo_builds_payload()

### Community 22 - "test_resume.py"
Cohesion: 0.10
Nodes (20): build_baseline_resume_data(), _normalize(), _slugify_role(), _synthetic_job_for_role(), build_resume_data(), extract_job_terms(), _grounded_summary(), RankedBullet (+12 more)

### Community 23 - "scheduler.py"
Cohesion: 0.14
Nodes (8): build_scheduler(), parse_hhmm(), _noop(), test_build_scheduler_invalid_timezone(), test_build_scheduler_registers_jobs(), test_build_scheduler_skips_invalid_times(), test_parse_hhmm(), test_parse_hhmm_invalid()

### Community 24 - "FakeTransport"
Cohesion: 0.21
Nodes (15): send_prep_pack(), test_shortlist_document_marks_sent(), FakeTransport, _enable_brief(), _insert(), _RaisingClient, _row(), test_card_shows_stored_fields_without_changing_them() (+7 more)

### Community 25 - "diff.py"
Cohesion: 0.11
Nodes (27): get_role_baseline_by_role(), get_suggestions_for_job(), RoleBaseline, SkillPlacement, SkillProvenance, SkillSuggestion, SuggestionStatus, _cmd_tailor_resume() (+19 more)

### Community 26 - "test_company_intelligence.py"
Cohesion: 0.12
Nodes (23): attach_company_intelligence(), extract_company_facts(), HttpCompanyIntelProvider, merge_company_facts(), FakeProvider, _job(), _posting(), test_company_facts_do_not_change_scoring_signals() (+15 more)

### Community 27 - "test_discovery_observability.py"
Cohesion: 0.17
Nodes (8): list_stage_runs(), _safe_close_stage(), possible_result_cap(), _Frame, test_evidence_failure_does_not_hide_the_ingest_result(), test_jobspy_location_counts_and_cap_warning(), test_two_runs_keep_separate_evidence(), test_workday_counts_recency_drops()

### Community 28 - "pacing.py"
Cohesion: 0.21
Nodes (7): acquire(), AcquireResult, _clamp_multiplier(), _clock(), gap_seconds(), note_success(), PlatformPacing

### Community 29 - "run_pipeline"
Cohesion: 0.07
Nodes (30): Bounded trial, Comparing with the OpenAI dashboard, OpenAI usage summary, What the line contains, Architecture, Pipeline run lifecycle, run_pipeline(), _safe_open_run() (+22 more)

### Community 30 - "test_ingest_resilience.py"
Cohesion: 0.05
Nodes (51): Targets, SearchStatus, run_ingestion(), _accept(), _run_jobspy(), _run_workday(), kill_process_group(), LineWorker (+43 more)

### Community 31 - "typing"
Cohesion: 0.10
Nodes (10): process_updates(), Submitter, decode_callback(), encode_callback(), _should_retry_telegram(), health(), test_process_updates_routes_callback(), test_decode_invalid() (+2 more)

### Community 32 - "test_calibration.py"
Cohesion: 0.22
Nodes (20): brier_score(), build_calibration(), CalibrationFold, CalibrationReport, load_calibration_config(), run_calibration(), load_feedback_config(), _calibration() (+12 more)

### Community 33 - "LLMClient"
Cohesion: 0.13
Nodes (9): is_openai_safety_error(), LLMClient, _attach_usage_summary(), _emit_usage_summary(), _JobOutcome, _priority_evidence(), Scorer, run_one() (+1 more)

### Community 34 - "test_eligibility.py"
Cohesion: 0.16
Nodes (17): assign_eligibility(), eligibility_column_types(), eligibility_is_current(), evaluate_eligibility(), profile_eligibility_hash(), _job(), _Model, test_cache_identity() (+9 more)

### Community 35 - "settings.py"
Cohesion: 0.18
Nodes (5): approx_tokens(), cache_block(), compact_json_dumps(), minify_job(), test_token_optimizer_helpers()

### Community 36 - "Remaining Manual Setup"
Cohesion: 0.08
Nodes (24): 2a. Find a Workday URL, 2b. Edit `config/targets.yaml`, 3a. Run the save-session helper, 3b. What you do in the browser, 4a. Discover jobs (LinkedIn / Indeed + any real Workday tenants), 4b. Score with Gemini, 4c. Attach your base resume to staged jobs, 4d. Send LinkedIn/Indeed application prep pack (Telegram) (+16 more)

### Community 37 - "linkedin_people.py"
Cohesion: 0.07
Nodes (26): auto_discover_peers(), _crawl(), BlockerError, build_people_search_url(), _detect_blocker(), discover_peers(), extract_profile_urls(), _heuristic_parse() (+18 more)

### Community 38 - "monitoring.py"
Cohesion: 0.12
Nodes (33): _as_utc(), PipelineRun, PipelineStageRun, get_health_report(), _recent_failures(), _repeated_failures(), _run_view(), _stages() (+25 more)

### Community 39 - "test_phase13_shortlist.py"
Cohesion: 0.14
Nodes (18): get_jobs_by_status(), get_unsent_pending_reviews(), select_shortlist(), _config(), _job(), _SpyApplicator, test_apply_shortlist_is_idempotent_and_preserves_scores(), test_diversity_respects_company_cap_and_ignores_secondary_family() (+10 more)

### Community 40 - "Status"
Cohesion: 0.19
Nodes (18): application_history(), button(), SubmitResult, encode_outcome_callback(), get_application_for_job(), Status, _count(), _job() (+10 more)

### Community 41 - "profile.py"
Cohesion: 0.13
Nodes (29): Address, Education, Exclusions, Experience, Identity, Preferences, WorkAuthorization, _make_base_pdf() (+21 more)

### Community 42 - "load_persisted_calibration"
Cohesion: 0.36
Nodes (7): CalibrationMetric, CalibrationRun, get_calibration_metrics(), get_calibration_run(), save_calibration_run(), load_persisted_calibration(), persist_calibration()

### Community 43 - "compiler.py"
Cohesion: 0.09
Nodes (24): apply_decided_suggestions(), load_profile(), get_role_baseline_by_id(), apply_fit_caps(), _baseline_pdf_for_job(), clean_name(), compile_for_job(), compile_pending() (+16 more)

### Community 44 - "test_jobspy_exception_keeps_earlier_observations"
Cohesion: 0.22
Nodes (7): test_dry_run_does_not_fetch_or_write(), test_jobspy_exception_keeps_earlier_observations(), jobspy(), test_keyboard_interrupt_is_not_a_complete_report(), test_live_fake_attributes_only_the_requested_phrase(), jobspy(), workday()

### Community 45 - "skills.py"
Cohesion: 0.09
Nodes (22): aggregate_role_skills(), AggregatedSkill, _categorize(), extract_top_skills(), extract_top_skills_deterministic(), parse_skills_json(), _repair_truncated_json_array(), RoleSkillProfile (+14 more)

### Community 46 - "test_workload_limits.py"
Cohesion: 0.08
Nodes (37): OpenAIEmbedder, _Chat, _chat_ok(), _ChatHolder, _ChatResponse, _Choice, _Completions, _Embeddings (+29 more)

### Community 47 - "role_classify.py"
Cohesion: 0.14
Nodes (18): _clause_containing(), _clip_items(), _deterministic(), _is_interaction(), _item_text(), _ModelLabel, _parse_model(), _phrase_hits() (+10 more)

### Community 48 - "get_job_by_id"
Cohesion: 0.37
Nodes (13): handle_callback(), ReviewAction, get_job_by_id(), _callback_update(), FakeSubmitter, _seed_pending(), test_already_decided(), test_approve_blocker_manual() (+5 more)

### Community 49 - "Settings"
Cohesion: 0.08
Nodes (11): Build order and status, Coding conventions, Commands, Confirmed product decisions, Project, Repository layout, Scoring specifics (Step 3), Workflow for implementing a step (+3 more)

### Community 50 - "test_application_portfolio.py"
Cohesion: 0.06
Nodes (57): get_recently_applied_companies(), Capacity, Decisions, Phase 14 application portfolio, Pipeline, Role-family mix, What counts as a recent application, Who can be allocated (+49 more)

### Community 51 - "test_priority.py"
Cohesion: 0.16
Nodes (18): _attach_priority(), apply_priority(), priority_is_current(), PriorityDecision, role_family_component(), _job(), test_dream_company_is_only_a_configured_boost(), test_eligibility_unknown_is_not_ineligible() (+10 more)

### Community 52 - "Phase 5 role classification"
Cohesion: 0.29
Nodes (6): Inputs, Limits, Output, Phase 5 role classification, Taxonomy, When it runs again

### Community 54 - "models.py"
Cohesion: 0.07
Nodes (23): reload_profile(), _load_yaml(), parse_workday_url(), reload_targets(), WorkdayParts, ApplyKind, classify_apply_url(), _host() (+15 more)

### Community 55 - "priority.py"
Cohesion: 0.13
Nodes (25): _as_utc(), company_domain_component(), _company_signals(), _components(), dream_company_component(), eligibility_component(), _explicit_sections(), fit_component() (+17 more)

### Community 56 - "main.py"
Cohesion: 0.10
Nodes (24): build_parser(), _cmd_benchmark(), _cmd_build_baseline(), _cmd_health(), _cmd_prep_pack(), _cmd_run_once(), _cmd_save_linkedin_session(), _cmd_send_reviews() (+16 more)

### Community 57 - "test_vector_recovery.py"
Cohesion: 0.25
Nodes (30): _enable(), _seed(), _assert_no_profile_text(), _bare_job(), _doc(), _exclude_company(), _score(), _stamp() (+22 more)

### Community 58 - "Benchmark — Product Manager @ T-Mobile"
Cohesion: 0.33
Nodes (5): Benchmark — Product Manager @ T-Mobile, Dimensions, Gaps, Recommendations, Strengths

### Community 59 - "asyncio"
Cohesion: 0.22
Nodes (4): run_polling(), _cmd_poll(), test_run_polling_max_iterations(), __init__()

### Community 60 - "score_pending"
Cohesion: 0.17
Nodes (20): job_embed_text(), profile_embed_text(), profile_hash(), score_pending(), FakeClient, test_no_score_budget_scores_every_eligible_job(), FakeEmbedder, _map() (+12 more)

### Community 61 - "OpenAIClient"
Cohesion: 0.13
Nodes (28): OpenAIClient, test_openai_client_scores_json(), create(), _Chat, _chat_attempts(), _Choice, _complete(), _CompletionDetails (+20 more)

### Community 62 - "tracker.py"
Cohesion: 0.19
Nodes (15): _add_event(), application_method(), backfill_submitted_applications(), _event_exists(), _get_or_create(), record_manual_review(), record_outcome(), record_prefill() (+7 more)

### Community 63 - "datetime"
Cohesion: 0.15
Nodes (12): build_keyboard(), build_review_caption(), format_answers_message(), format_cover_letter_message(), ReviewSummary, _send_one(), send_pending_reviews(), test_build_keyboard_and_caption() (+4 more)

### Community 64 - "migrate_to_neon.py"
Cohesion: 0.13
Nodes (12): _absolute_sqlite_url(), normalize_database_url(), _cell(), _copy_table(), _counts(), main(), _reset_sequences(), _row() (+4 more)

### Community 65 - "5. How fit is scored"
Cohesion: 0.22
Nodes (7): 10. File map, 5.1 What the model is, 5.2 The two inputs, 5.3 The rubric, verbatim in meaning, 5.4 What the code does with the score, 5.5 What a number means, 5. How fit is scored

### Community 66 - "discovery_experiment.py"
Cohesion: 0.07
Nodes (55): account_executions(), _baseline_slot_reason(), _baseline_slots(), build_schedule(), _classify_incremental(), compare_arms(), _execute(), _execute_phrase() (+47 more)

### Community 67 - "test_trial_workflow.py"
Cohesion: 0.14
Nodes (13): ScoringSafetyHalt, IngestSummary, test_safety_halt_does_not_send_or_apply(), halt(), ingest(), test_trial_env_matches_the_settings_parser(), test_trial_sqlite_url_creates_the_schema(), test_trial_workflow_is_manual_and_isolated() (+5 more)

### Community 68 - "db.py"
Cohesion: 0.08
Nodes (21): _company_name(), _dialect_name(), _drop_structured_jd(), _ensure_company_columns(), _ensure_job_columns(), _ensure_pipeline_stage_columns(), get_jobs_needing_outcome_prompt(), get_pending_suggestions_for_job() (+13 more)

### Community 71 - "prerank_score"
Cohesion: 0.20
Nodes (11): prerank_jobs(), prerank_score(), _source_weight(), _job(), test_dream_company_boost(), test_intern_title_outranks_fulltime(), test_new_source_scored_without_error(), test_prerank_jobs_empty() (+3 more)

### Community 72 - "browser.py"
Cohesion: 0.13
Nodes (9): What still needs the user (before live runs), launch_context(), _new_context(), new_page(), save_storage_state(), save_session(), Deploy with Docker, save_linkedin_session() (+1 more)

### Community 73 - "linkedin_jobspy.py"
Cohesion: 0.11
Nodes (16): SearchConfig, main(), _one(), _records(), _dataframe_to_postings(), _effective_windows(), _explicit_company_url(), _external_id() (+8 more)

### Community 75 - "benchmark/engine.py"
Cohesion: 0.13
Nodes (17): BenchmarkReport, BenchmarkSummary, build_benchmark(), _derive_seniority(), DimensionScore, _education_rank(), _median(), _norm() (+9 more)

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
Nodes (28): _role_classification_current(), classification_is_current(), classify_role(), _apply_role_classification(), _FakeClient, _jd(), test_classifier_version_bump_invalidates_phase5_v1(), test_invalid_confidence_is_unknown() (+20 more)

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
Cohesion: 0.16
Nodes (12): ApplicationDeadline, _clip(), empty_application_deadline(), _excluded(), extract_application_deadline(), _from_match(), _named(), _parse_date() (+4 more)

### Community 85 - "Discovery recall benchmark"
Cohesion: 0.10
Nodes (18): Discovery recall benchmark, Label corrections on 2026-10-04, Limits, Matching, Reproduce, What is checked in, Discovery run observability, Query timeout and incremental save (+10 more)

### Community 86 - "suggest.py"
Cohesion: 0.11
Nodes (17): handle_message(), _handle_suggest_callback(), decide_suggestion(), _format_card(), send_pending_suggestions(), _suggestion_keyboard(), SuggestSummary, decode_suggest_callback() (+9 more)

### Community 87 - "2. Where jobs come from"
Cohesion: 0.29
Nodes (7): 2.1 Search terms, 2.2 Sites and the exact JobSpy arguments, 2.3 How each site treats "posted in the last 36 hours", 2.4 What is kept from a JobSpy row, 2.5 Workday, separately from LinkedIn, 2.6 Save and dedupe, 2. Where jobs come from

### Community 88 - "8. The weight discussion (not built)"
Cohesion: 0.33
Nodes (6): 8.1 What you asked for, 8.2 Decisions you agreed with, 8.3 A weight table we used as a sketch, 8.4 What we said the rubric should do for career-switch roles, 8.5 How that would sit on the current pipeline, 8. The weight discussion (not built)

### Community 89 - "test_pacing.py"
Cohesion: 0.21
Nodes (19): end_of_local_day(), note_pace_block(), _Applicator, _enable(), _row(), _seed(), _Sleep, test_acquire_after_blackout_keeps_multiplier() (+11 more)

### Community 90 - "Phase 8 company intelligence"
Cohesion: 0.29
Nodes (6): Names and reuse, Phase 8 company intelligence, Schema, Sources, What it is, What this phase does not change

### Community 91 - "pytest"
Cohesion: 0.08
Nodes (23): Tech stack, build_llm_client(), _load_role_client(), _FakeAio, _FakeAsyncModels, _FakeCandidate, _FakeGenaiClient, _FakeGenerateResponse (+15 more)

### Community 93 - "outreach.py"
Cohesion: 0.14
Nodes (10): _fallback_cover_letter(), generate_cover_letter(), contains_banned(), _fallback_outreach(), generate_outreach(), strip_banned_sentences(), build_cover_letter_user(), build_outreach_user() (+2 more)

### Community 94 - "test_openai_request_gate.py"
Cohesion: 0.11
Nodes (31): get_openai_request_ledger(), OpenAIBudgetExceeded, reset_openai_request_ledger(), _Chat, _ChatClient, _ChatResponse, _Choice, _complete() (+23 more)

### Community 95 - "company_intelligence.py"
Cohesion: 0.06
Nodes (46): CompanyIntelligence, _accumulate_sources(), _apply_context(), _apply_facts(), _by_key(), canonical_company_name(), _clear_facts(), _compact() (+38 more)

### Community 96 - "feedback.py"
Cohesion: 0.10
Nodes (28): Application, ApplicationEvent, FeedbackRun, FeedbackSignal, get_application_by_id(), get_application_events(), get_feedback_run(), get_feedback_signals() (+20 more)

### Community 97 - "Phase 16 feedback learning"
Cohesion: 0.33
Nodes (5): Evidence and shrinkage, Phase 16 feedback learning, Rates, Segments, Who is counted

### Community 98 - "scorer/engine.py"
Cohesion: 0.06
Nodes (32): build_embedder(), _cache_path(), clears_threshold(), cosine(), Embedder, EmbedInputLimitReached, jd_vector(), load_profile_embedding() (+24 more)

### Community 99 - "test_application_deadline.py"
Cohesion: 0.18
Nodes (16): _pad(), _read(), test_deadline_failure_does_not_drop_the_rest_of_the_reading(), test_empty_and_unusable_descriptions(), test_internship_and_graduation_dates_are_not_deadlines(), test_interview_deadline_is_not_an_application_deadline(), test_invalid_calendar_date_is_ambiguous(), test_markdown_split_year_is_kept() (+8 more)

### Community 100 - "test_monitoring.py"
Cohesion: 0.08
Nodes (24): reset_engine(), _brief(), format_health_report(), list_pipeline_runs(), stage_counters(), _job(), test_a_new_run_does_not_duplicate_applications(), test_backlog_and_stale_jobs() (+16 more)

### Community 101 - "calibration.py"
Cohesion: 0.17
Nodes (26): _append_buckets(), _append_short_target(), _append_slice(), _append_target_metrics(), _append_topk(), _bucket_name(), CalibrationMetricRow, _direction() (+18 more)

### Community 102 - "test_cover_letter.py"
Cohesion: 0.23
Nodes (7): cap_cover_letter(), _job(), _ScriptedClient, test_cap_cover_letter_cuts_on_sentence_boundary(), test_cap_cover_letter_hard_slice_without_punctuation(), test_generate_cover_letter_falls_back_when_strip_empties(), test_generate_cover_letter_retries_banned_words()

### Community 103 - "Phase 15 application tracker"
Cohesion: 0.33
Nodes (5): Method and time, Phase 15 application tracker, States and outcomes, What this is not, When a row is created

### Community 104 - "json"
Cohesion: 0.15
Nodes (12): effective_baseline(), effective_config_hash(), fingerprint_profile(), profile_hash(), public_config(), write_effective_baseline(), calibration_config_hash(), feedback_config_hash() (+4 more)

### Community 105 - "WorkdaySubmitter"
Cohesion: 0.20
Nodes (7): SessionMissingError, WorkdaySubmitter, test_submit_generic_exception(), test_submit_missing_url(), test_submit_session_missing(), boom_launch(), test_submit_unparseable_without_tenant()

### Community 106 - "3. Hard filters (before any model)"
Cohesion: 0.18
Nodes (11): 3.10 What a survivor looks like, 3.1 Company blocklist, 3.2 Exclusion keywords, 3.3 Clearance language, 3.4 Staffing agencies, 3.5 Internship gate, 3.6 Seniority filter (separate from the internship gate), 3.7 Years of experience (+3 more)

### Community 107 - "_persist_postings"
Cohesion: 0.40
Nodes (3): _stamp_role_family_weight(), _persist_postings(), _PersistCounts

### Community 108 - "9. Pain points we have actually hit or spelled out"
Cohesion: 0.33
Nodes (6): 9.1 Discovery, 9.2 Filters, 9.3 Scoring, 9.4 What you receive, 9.5 Operations, 9. Pain points we have actually hit or spelled out

### Community 109 - "Job Agent"
Cohesion: 0.13
Nodes (14): Application prep packs (LinkedIn / Indeed), Job Agent, Layout, LinkedIn peer benchmarking (optional, off by default), Resumes (Step 4), Run automation (Step 5), Run ingestion (Step 2), Run review bot (Step 6) (+6 more)

### Community 110 - "calculate_priority"
Cohesion: 0.17
Nodes (20): calculate_priority(), _combine(), load_priority_config(), _reasons(), test_weights_sum_to_100(), _job(), _signal(), test_confidence_and_structured_evidence() (+12 more)

### Community 111 - "Phase 12 priority ranking"
Cohesion: 0.50
Nodes (3): Components, Phase 12 priority ranking, Version

### Community 112 - "Phase 6 candidate fit"
Cohesion: 0.33
Nodes (5): Dimensions, Not in this phase, Output, Phase 6 candidate fit, When the model is not called

### Community 113 - "test_prep_builder.py"
Cohesion: 0.12
Nodes (14): _answer_item(), build_job_section(), compile_prep_pdf(), generate_prep_pack(), PrepPackResult, render_markdown(), FakeClient, _job() (+6 more)

### Community 114 - "init_db"
Cohesion: 0.15
Nodes (11): get_engine(), init_db(), Application deadline, Cache, Limits, Structured JD intelligence, What is stored, database_reachable() (+3 more)

### Community 115 - "Company intelligence 2.0"
Cohesion: 0.33
Nodes (5): Company intelligence 2.0, Company versus job, Sources and refresh, What it does not store, What it stores

### Community 116 - "filters.py"
Cohesion: 0.09
Nodes (20): citizenship_restriction(), _clearance_clauses(), clearance_requirement(), evaluate_job(), FilterResult, has_internship_signal(), _haystack(), _mandatory_years() (+12 more)

### Community 119 - "Job"
Cohesion: 0.13
Nodes (18): _load_yaml(), Job, apply_shortlist(), _close_enough(), _company_key(), _company_ok(), config_hash(), _diversify() (+10 more)

### Community 121 - "Phase 18 — Production reliability and monitoring"
Cohesion: 0.15
Nodes (12): Backlog diagnostics, CLI, Configuration, Failure isolation, Health states, Logging, Phase 18 — Production reliability and monitoring, Purpose (+4 more)

### Community 122 - "Multi-dimensional role classification"
Cohesion: 0.29
Nodes (6): Cache, Contract, Function versus interaction, Multi-dimensional role classification, Non-goals, What the classifier reads

### Community 123 - "6. What is sent to you"
Cohesion: 0.40
Nodes (5): 6.1 Who is eligible, 6.2 The shortlist rule, 6.3 Each line, 6.4 If brief mode is turned off, 6. What is sent to you

### Community 124 - "alerts.py"
Cohesion: 0.23
Nodes (9): AlertSummary, build_alert_caption(), _send_one(), send_pending_alerts(), test_build_alert_caption(), test_scoring_error_does_not_alert(), test_send_pending_alerts_empty(), test_send_pending_alerts_photo_and_skip() (+1 more)

### Community 125 - "sort_by_priority"
Cohesion: 0.29
Nodes (6): Configuration, Phase 13 shortlist, Pipeline, Selection, sort_by_priority(), posted()

### Community 126 - "get_settings"
Cohesion: 0.10
Nodes (5): get_settings(), OpenAIBillingHalted, OpenAIRequestBlocked, OpenAIRequestLedger, _vectors_from_response()

### Community 127 - "prep.py"
Cohesion: 0.13
Nodes (17): _dedupe(), _fit_lines(), _load_canonical_shortlist(), _mark_sent(), _notify_empty(), PrepSummary, render_job_card(), render_shortlist() (+9 more)

### Community 128 - "Tier"
Cohesion: 0.08
Nodes (24): Tier, compute_tier(), is_dream_company(), parse_score(), build_scoring_system_blocks(), build_scoring_user(), _posting(), ScoreOnlyClient (+16 more)

### Community 129 - "test_role_weights.py"
Cohesion: 0.12
Nodes (21): get_role_family_weight(), load_role_family_weights(), _validate(), weight_for_subfamily(), test_feedback_config_keeps_priority_integration_off(), _job(), _posting(), test_company_and_vector_are_not_weight_inputs() (+13 more)

### Community 130 - "clients.py"
Cohesion: 0.05
Nodes (31): LLM client layer (`scorer/clients.py`), _add_measured(), _add_token(), AnthropicClient, _attempt(), _Attempt, _blank_bucket(), _chat_usage() (+23 more)

### Community 131 - "service.py"
Cohesion: 0.13
Nodes (5): configure_logging(), _cmd_serve(), run_service(), test_run_service_stops_without_poller(), test_run_service_with_poller_respects_stop()

### Community 132 - "workday.py"
Cohesion: 0.10
Nodes (18): action_delay_bounds(), human_delay(), type_like_human(), typing_delay_bounds(), click_by_role(), click_next(), _collect_labeled_fields(), detect_blocker() (+10 more)

### Community 134 - "test_doctor.py"
Cohesion: 0.44
Nodes (7): _cmd_doctor(), _job(), test_doctor_cooldown(), test_doctor_empty_db(), test_doctor_outcomes(), test_doctor_vector_gate(), test_doctor_with_jobs()

### Community 135 - "session_scope"
Cohesion: 0.09
Nodes (42): Data model (core/db.py), Status lifecycle, get_job_by_source_id(), session_scope(), Source, upsert_job(), hash_fallback(), to_job() (+34 more)

### Community 139 - "Phase 9 visa and eligibility"
Cohesion: 0.25
Nodes (7): Cache and storage, Education, graduation, experience, location, dates, Phase 9 visa and eligibility, Sponsorship, citizenship, and clearance, States, What the profile contributes, What this phase does not do

### Community 141 - "Phase 7 role-family weighting"
Cohesion: 0.22
Nodes (8): Canonical portfolio, Configuration, Four different questions, Phase 7 role-family weighting, Unknown classification, What is stored, What this phase does not do, Where the family comes from

### Community 142 - "_build_doctor_report"
Cohesion: 0.36
Nodes (4): _build_doctor_report(), _count_jobs(), _print_doctor_report(), _unwrap()

### Community 147 - "re"
Cohesion: 0.11
Nodes (19): locations_agree(), locations_conflict(), _city_state(), company_matches(), company_tokens(), contains_phrase(), is_remote_location(), location_matches() (+11 more)

### Community 153 - "is_pace_blocker"
Cohesion: 0.50
Nodes (3): is_pace_blocker(), test_pace_hints_ignore_mfa_and_empty(), test_pace_hints_match()

### Community 160 - "test_baseline.py"
Cohesion: 0.25
Nodes (5): get_jobs_for_role(), FakeClient, Path_exists(), test_build_role_baseline_persists(), test_get_jobs_for_role_matches_title()

## Knowledge Gaps
- **184 isolated node(s):** `job-agent`, `ScrapeSummary`, `_Sites`, `_FakeAio`, `Project` (+179 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 1248 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **9 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Job` connect `Job` to `Tier`, `vector_recovery.py`, `test_fit.py`, `structured_jd.py`, `workday.py`, `handlers.py`, `test_career_intelligence.py`, `session_scope`, `test_doctor.py`, `test_feedback.py`, `test_openai_run_usage.py`, `test_role_weights.py`, `discovery_recall.py`, `answers.py`, `_build_doctor_report`, `eligibility.py`, `ingest.py`, `re`, `test_structured_jd.py`, `apply_pending`, `test_resume.py`, `FakeTransport`, `diff.py`, `test_company_intelligence.py`, `test_ingest_resilience.py`, `typing`, `test_baseline.py`, `LLMClient`, `test_eligibility.py`, `test_calibration.py`, `settings.py`, `monitoring.py`, `test_phase13_shortlist.py`, `Status`, `profile.py`, `compiler.py`, `skills.py`, `test_workload_limits.py`, `get_job_by_id`, `test_application_portfolio.py`, `test_priority.py`, `models.py`, `priority.py`, `main.py`, `test_vector_recovery.py`, `score_pending`, `OpenAIClient`, `tracker.py`, `datetime`, `migrate_to_neon.py`, `db.py`, `prerank_score`, `benchmark/engine.py`, `classify_role`, `runner.py`, `suggest.py`, `test_pacing.py`, `outreach.py`, `company_intelligence.py`, `feedback.py`, `scorer/engine.py`, `test_application_deadline.py`, `test_monitoring.py`, `test_cover_letter.py`, `WorkdaySubmitter`, `_persist_postings`, `calculate_priority`, `test_prep_builder.py`, `filters.py`, `alerts.py`, `sort_by_priority`, `get_settings`, `prep.py`?**
  _High betweenness centrality (0.135) - this node is a cross-community bridge._
- **Are the 180 inferred relationships involving `Job` (e.g. with `Data model (core/db.py)` and `AnswerResolver`) actually correct?**
  _`Job` has 180 INFERRED edges - model-reasoned connections that need verification._
- **What connects `job-agent`, `ScrapeSummary`, `_Sites` to the rest of the system?**
  _184 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `structured_jd.py` be split into smaller, more focused modules?**
  _Cohesion score 0.12513842746400886 - nodes in this community are weakly interconnected._
- **Why does `get_settings()` connect `get_settings` to `Tier`, `clients.py`, `service.py`, `workday.py`, `call_with_resilience`, `test_career_intelligence.py`, `RawPosting`, `test_openai_run_usage.py`, `Profile`, `conftest.py`, `textclean.py`, `_build_doctor_report`, `answers.py`, `ingest.py`, `re`, `pipeline.py`, `TelegramClient`, `test_resume.py`, `scheduler.py`, `FakeTransport`, `diff.py`, `pacing.py`, `run_pipeline`, `test_ingest_resilience.py`, `typing`, `test_baseline.py`, `LLMClient`, `test_eligibility.py`, `settings.py`, `linkedin_people.py`, `monitoring.py`, `test_phase13_shortlist.py`, `profile.py`, `compiler.py`, `skills.py`, `test_workload_limits.py`, `role_classify.py`, `Settings`, `test_application_portfolio.py`, `models.py`, `main.py`, `test_vector_recovery.py`, `asyncio`, `score_pending`, `migrate_to_neon.py`, `test_trial_workflow.py`, `db.py`, `browser.py`, `linkedin_jobspy.py`, `benchmark/engine.py`, `test_webhook.py`, `classify_role`, `vault.py`, `runner.py`, `suggest.py`, `test_pacing.py`, `pytest`, `outreach.py`, `test_openai_request_gate.py`, `company_intelligence.py`, `scorer/engine.py`, `test_monitoring.py`, `json`, `test_prep_builder.py`, `init_db`, `filters.py`, `telegram_webhook`, `prep.py`?**
  _High betweenness centrality (0.103) - this node is a cross-community bridge._
- **Are the 264 inferred relationships involving `Profile` (e.g. with `AnswerResolver` and `_latest_education()`) actually correct?**
  _`Profile` has 264 INFERRED edges - model-reasoned connections that need verification._
- **Should `test_fit.py` be split into smaller, more focused modules?**
  _Cohesion score 0.09415584415584416 - nodes in this community are weakly interconnected._