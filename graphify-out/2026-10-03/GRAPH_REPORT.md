# Graph Report - Automatic job search  (2026-10-03)

## Corpus Check
- 200 files · ~159,503 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 13 file(s) not represented in the graph (top: (none) 8, .typ 2, .mdc 1)

## Summary
- 3394 nodes · 11680 edges · 132 communities (121 shown, 11 thin omitted)
- Extraction: 89% EXTRACTED · 11% INFERRED · 0% AMBIGUOUS · INFERRED: 1299 edges (avg confidence: 0.94)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `91debcd9`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- test_outcomes.py
- structured_jd.py
- test_vector_recovery.py
- test_eligibility.py
- migrate_to_neon.py
- clients.py
- test_career_intelligence.py
- test_fit.py
- test_discovery.py
- benchmark/engine.py
- Profile
- ingest.py
- conftest.py
- textclean.py
- outreach.py
- vault.py
- eligibility.py
- coverage.py
- test_application_tracker.py
- test_structured_jd.py
- pipeline.py
- TelegramClient
- baseline.py
- Settings
- workday_rest.py
- diff.py
- test_company_intelligence.py
- get_job_by_id
- test_pacing.py
- dataclasses
- session_scope
- test_vector_gate.py
- scheduler.py
- company_intelligence.py
- handle_callback
- test_role_classify.py
- Remaining Manual Setup
- review.py
- list_stage_runs
- test_phase13_shortlist.py
- send_prep_pack
- test_prep_builder.py
- workday.py
- compiler.py
- test_monitoring.py
- skills.py
- test_answers.py
- vector_recovery.py
- typing
- test_workday_locators.py
- test_application_portfolio.py
- test_priority.py
- Phase 5 role classification
- test_company_intelligence_v2.py
- diagnostics.py
- priority.py
- main.py
- Phase 2 search taxonomy
- Benchmark — Product Manager @ T-Mobile
- get_health_report
- db.py
- test_cover_letter.py
- tracker.py
- classify_role
- test_webhook.py
- build_llm_client
- normalize_company_name
- answers.py
- prep.py
- job-agent
- alerts.py
- HttpCompanyIntelProvider
- linkedin_jobspy.py
- phase10-false-negative-protection.md
- telemetry.py
- Phase 1 discovery architecture
- FakeTransport
- Phase 18 — Production reliability and monitoring
- init_db
- Priority 2.0
- WorkdaySubmitter
- RawPosting
- test_apply_url.py
- Phase 14 application portfolio
- extract_company_facts
- feedback.py
- test_feedback.py
- profile.py
- OpenAIEmbedder
- Phase 8 company intelligence
- test_llm_provider.py
- correction1-recruiting-universe.md
- _input_hash
- test_scorer.py
- phase11-job-identity.md
- Phase 16 feedback learning
- scorer/engine.py
- LLMClient
- Phase 7 role-family weighting
- calibration.py
- Phase 15 application tracker
- get_settings
- 3. Hard filters (before any model)
- linkedin_people.py
- Tier
- Job Agent
- calculate_priority
- Phase 12 priority ranking
- test_calibration.py
- resolve_company
- Company intelligence 2.0
- Job
- phase17-calibration-benchmark.md
- role_classify.py
- vector-recovery.md
- targets.py
- Multi-dimensional role classification
- 5. How fit is scored
- How jobs are found, filtered, scored, and sent
- load_persisted_calibration
- test_role_weights.py
- Any
- 2. Where jobs come from
- 8. The weight discussion (not built)
- 9. Pain points we have actually hit or spelled out
- re
- 6. What is sent to you
- .total_years_experience
- Phase 9 visa and eligibility
- Phase 6 candidate fit
- test_robustness.py

## God Nodes (most connected - your core abstractions)
1. `Job` - 372 edges
2. `Profile` - 331 edges
3. `session_scope()` - 302 edges
4. `Status` - 244 edges
5. `Source` - 207 edges
6. `get_settings()` - 166 edges
7. `get_job_by_id()` - 161 edges
8. `upsert_job()` - 137 edges
9. `TelegramClient` - 92 edges
10. `init_db()` - 85 edges

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

## Communities (132 total, 11 thin omitted)

### Community 0 - "test_outcomes.py"
Cohesion: 0.10
Nodes (25): _handle_outcome_callback(), build_outcome_keyboard(), button(), outcome_label(), outcome_message_text(), OutcomePromptSummary, send_outcome_prompt(), send_pending_outcome_prompts() (+17 more)

### Community 1 - "structured_jd.py"
Cohesion: 0.13
Nodes (37): _authorization(), AuthorizationEvidence, _availability(), _clause_at(), _clauses(), _clip(), _degree_state(), _domain() (+29 more)

### Community 2 - "test_vector_recovery.py"
Cohesion: 0.29
Nodes (27): _enable(), _seed(), _assert_no_profile_text(), _doc(), _exclude_company(), _score(), _stamp(), _store_doc() (+19 more)

### Community 3 - "test_eligibility.py"
Cohesion: 0.15
Nodes (20): assign_eligibility(), attach_eligibility(), eligibility_column_types(), eligibility_is_current(), EligibilityDecision, evaluate_eligibility(), profile_eligibility_hash(), _job() (+12 more)

### Community 4 - "migrate_to_neon.py"
Cohesion: 0.13
Nodes (12): _absolute_sqlite_url(), normalize_database_url(), _cell(), _copy_table(), _counts(), main(), _reset_sequences(), _row() (+4 more)

### Community 5 - "clients.py"
Cohesion: 0.10
Nodes (19): LLM client layer (`scorer/clients.py`), _backoff_delay(), call_with_resilience(), is_permanent_account_error(), is_transient(), LLMBillingError, LLMError, _status_code() (+11 more)

### Community 6 - "test_career_intelligence.py"
Cohesion: 0.08
Nodes (52): CareerIntelligence, _apply_reading(), assess_career(), attach_career_intelligence(), career_input_hash(), CareerReading, _clause(), _clip() (+44 more)

### Community 7 - "test_fit.py"
Cohesion: 0.11
Nodes (31): build_fit_system_blocks(), build_fit_user(), cached_fit(), _Dimension, evaluate_fit(), fit_context_block(), fit_is_current(), FitDecision (+23 more)

### Community 8 - "test_discovery.py"
Cohesion: 0.08
Nodes (32): load_targets(), build_discovery_plan(), DiscoveryConfig, DiscoverySource, _enabled_queries(), enabled_query_texts(), _family_spillover(), load_discovery() (+24 more)

### Community 9 - "benchmark/engine.py"
Cohesion: 0.13
Nodes (17): BenchmarkReport, BenchmarkSummary, build_benchmark(), _derive_seniority(), DimensionScore, _education_rank(), _median(), _norm() (+9 more)

### Community 10 - "Profile"
Cohesion: 0.10
Nodes (38): Profile, evaluate(), sponsorship_signal(), test_sponsorship_and_false_friends(), _posting(), test_clearance_regex_pattern(), test_exclude_clearance_keyword(), test_exclude_high_yoe_requirement() (+30 more)

### Community 11 - "ingest.py"
Cohesion: 0.11
Nodes (15): _stamp_role_family_weight(), CoverageReport, fail_unrecorded(), _jsonable(), log_coverage(), SearchObservation, write_coverage(), log_discovery_plan() (+7 more)

### Community 12 - "conftest.py"
Cohesion: 0.18
Nodes (6): Testing conventions, db_ready(), _disable_apply_pacing(), _disable_vector_gate(), _internship_only_off(), tmp_db()

### Community 13 - "textclean.py"
Cohesion: 0.05
Nodes (40): Cache, Career Intelligence, Dimensions, Failures, Overall score, How to read it, Limits, Phase 3 discovery coverage (+32 more)

### Community 14 - "outreach.py"
Cohesion: 0.29
Nodes (4): contains_banned(), _fallback_outreach(), generate_outreach(), strip_banned_sentences()

### Community 15 - "vault.py"
Cohesion: 0.15
Nodes (13): CredentialsFile, get_tenant_credentials(), has_saved_session(), load_credentials(), _load_yaml(), reload_credentials(), session_state_path(), TenantCredentials (+5 more)

### Community 16 - "eligibility.py"
Cohesion: 0.17
Nodes (25): _ask_model(), _citizenship(), _clearance(), _current_student(), _dates(), _decision_from_job(), _dim(), DimensionResult (+17 more)

### Community 17 - "coverage.py"
Cohesion: 0.12
Nodes (25): build_coverage_report(), add_planned(), group_for(), GroupMetrics, observe_search(), _planned_slots(), QueryMetrics, result_identity() (+17 more)

### Community 18 - "test_application_tracker.py"
Cohesion: 0.19
Nodes (16): application_history(), ApplyResult, SubmitResult, get_application_for_job(), _Blocker, _count(), _job(), _Prefill (+8 more)

### Community 19 - "test_structured_jd.py"
Cohesion: 0.11
Nodes (19): StructuredJobDescription, attach_structured_jd(), extract_structured_jd(), get_structured_jd(), structured_jd_is_current(), _areas(), _job(), test_changed_upsert_drops_the_old_reading() (+11 more)

### Community 20 - "pipeline.py"
Cohesion: 0.10
Nodes (19): _allocated_ids(), _benchmark_tier_one_stage(), _generate_suggestions_stage(), _note_skipped(), PipelineSummary, _portfolio_stage(), _prepare_shortlisted_resumes(), _run_opened_pipeline() (+11 more)

### Community 21 - "TelegramClient"
Cohesion: 0.13
Nodes (3): HttpxTransport, TelegramClient, TelegramTransport

### Community 22 - "baseline.py"
Cohesion: 0.11
Nodes (15): get_jobs_for_role(), build_baseline_resume_data(), _normalize(), _slugify_role(), _synthetic_job_for_role(), build_resume_data(), extract_job_terms(), _grounded_summary() (+7 more)

### Community 24 - "workday_rest.py"
Cohesion: 0.11
Nodes (19): _as_text(), _company_name(), _one(), _fetch_detail(), _fetch_listing_page(), fetch_workday(), _is_recent_posted_on(), _parse_json() (+11 more)

### Community 25 - "diff.py"
Cohesion: 0.07
Nodes (39): apply_decided_suggestions(), _format_card(), send_pending_suggestions(), _suggestion_keyboard(), SuggestSummary, get_pending_suggestions_for_job(), get_role_baseline_by_id(), get_role_baseline_by_role() (+31 more)

### Community 26 - "test_company_intelligence.py"
Cohesion: 0.27
Nodes (14): attach_company_intelligence(), FakeProvider, _job(), _posting(), test_company_facts_do_not_change_scoring_signals(), test_company_sources_accumulate_and_a_failed_refresh_keeps_them(), test_complete_record_and_ignored_claims(), test_cooldown_set_is_unchanged() (+6 more)

### Community 27 - "get_job_by_id"
Cohesion: 0.23
Nodes (25): apply_pending(), get_job_by_id(), FakeApplicator, _script_reloads(), _seed_job(), test_allocation_removed_before_execution_is_skipped(), test_apply_linkedin_with_workday_url(), test_apply_pending_blocker() (+17 more)

### Community 28 - "test_pacing.py"
Cohesion: 0.10
Nodes (29): acquire(), AcquireResult, _clamp_multiplier(), _clock(), end_of_local_day(), gap_seconds(), is_pace_blocker(), note_pace_block() (+21 more)

### Community 29 - "dataclasses"
Cohesion: 0.12
Nodes (17): _FakeSummary, test_pipeline_order_and_aggregation(), fake_alerts(), fake_apply(), fake_ingestion(), fake_outcomes(), fake_prep(), fake_resume() (+9 more)

### Community 30 - "session_scope"
Cohesion: 0.07
Nodes (55): get_job_by_source_id(), session_scope(), Source, Status, upsert_job(), _reopen_job(), hash_fallback(), to_job() (+47 more)

### Community 31 - "test_vector_gate.py"
Cohesion: 0.19
Nodes (20): job_embed_text(), profile_embed_text(), profile_hash(), score_pending(), FakeClient, FakeEmbedder, _map(), test_budget_skips_tail_after_a_reject() (+12 more)

### Community 32 - "scheduler.py"
Cohesion: 0.16
Nodes (8): build_scheduler(), parse_hhmm(), _noop(), test_build_scheduler_invalid_timezone(), test_build_scheduler_registers_jobs(), test_build_scheduler_skips_invalid_times(), test_parse_hhmm(), test_parse_hhmm_invalid()

### Community 33 - "company_intelligence.py"
Cohesion: 0.11
Nodes (18): _accumulate_sources(), _apply_context(), _compact(), _confidence_for(), _context_from(), extract_company_signals(), merge_company_signals(), _prefer_signal() (+10 more)

### Community 34 - "handle_callback"
Cohesion: 0.22
Nodes (17): _decision_caption(), handle_callback(), decode_callback(), encode_callback(), ReviewAction, _callback_update(), FakeSubmitter, _seed_pending() (+9 more)

### Community 35 - "test_role_classify.py"
Cohesion: 0.18
Nodes (14): classification_is_current(), _apply_role_classification(), _FakeClient, _jd(), test_classification_persists_and_does_not_filter(), test_classifier_version_bump_invalidates_phase5_v1(), test_invalid_confidence_is_unknown(), test_invalid_model_output_falls_back_to_unknown() (+6 more)

### Community 36 - "Remaining Manual Setup"
Cohesion: 0.08
Nodes (25): 2a. Find a Workday URL, 2b. Edit `config/targets.yaml`, 3a. Run the save-session helper, 3b. What you do in the browser, 4a. Discover jobs (LinkedIn / Indeed + any real Workday tenants), 4b. Score with Gemini, 4c. Attach your base resume to staged jobs, 4d. Send LinkedIn/Indeed application prep pack (Telegram) (+17 more)

### Community 37 - "review.py"
Cohesion: 0.14
Nodes (13): build_keyboard(), build_review_caption(), format_answers_message(), format_cover_letter_message(), ReviewSummary, _send_one(), send_pending_reviews(), get_unsent_pending_reviews() (+5 more)

### Community 38 - "list_stage_runs"
Cohesion: 0.15
Nodes (9): list_stage_runs(), test_health_reports_database_failure(), test_health_reports_invalid_configuration(), test_pipeline_failure_outside_a_stage_is_failed(), boom(), test_pipeline_partial_when_a_stage_fails(), ok(), test_pre_stage_setup_failure_marks_the_run_failed() (+1 more)

### Community 39 - "test_phase13_shortlist.py"
Cohesion: 0.09
Nodes (33): get_jobs_by_status(), apply_shortlist(), _close_enough(), _company_key(), _company_ok(), config_hash(), _diversify(), _family() (+25 more)

### Community 40 - "send_prep_pack"
Cohesion: 0.26
Nodes (13): send_prep_pack(), _enable_brief(), _insert(), _RaisingClient, _row(), test_card_shows_stored_fields_without_changing_them(), test_duplicate_job_id_is_rendered_once(), test_empty_shortlist_sends_no_cards() (+5 more)

### Community 41 - "test_prep_builder.py"
Cohesion: 0.12
Nodes (13): _answer_item(), build_job_section(), compile_prep_pdf(), generate_prep_pack(), PrepPackResult, render_markdown(), FakeClient, _job() (+5 more)

### Community 42 - "workday.py"
Cohesion: 0.14
Nodes (12): human_delay(), BlockerError, click_by_role(), click_next(), _collect_labeled_fields(), detect_blocker(), _fill_field(), is_review_page() (+4 more)

### Community 43 - "compiler.py"
Cohesion: 0.07
Nodes (24): load_profile(), _load_yaml(), apply_fit_caps(), _baseline_pdf_for_job(), clean_name(), compile_for_job(), compile_pending(), compile_resume() (+16 more)

### Community 44 - "test_monitoring.py"
Cohesion: 0.13
Nodes (28): close_pipeline_run(), close_stage_run(), count_stale_jobs(), interrupt_stale_runs(), list_pipeline_runs(), load_monitoring_config(), _moment(), monitoring_config_hash() (+20 more)

### Community 45 - "skills.py"
Cohesion: 0.09
Nodes (22): aggregate_role_skills(), AggregatedSkill, _categorize(), extract_top_skills(), extract_top_skills_deterministic(), parse_skills_json(), _repair_truncated_json_array(), RoleSkillProfile (+14 more)

### Community 46 - "test_answers.py"
Cohesion: 0.13
Nodes (15): AnswerResolver, one(), answers_to_payload(), AnswerSource, is_open_ended(), ResolvedAnswer, FakeAnswerClient, test_answers_to_payload() (+7 more)

### Community 47 - "vector_recovery.py"
Cohesion: 0.18
Nodes (17): _compiled(), _confidence(), config_hash(), evaluate_recovery(), _family_group(), load_recovery_config(), _mba_program(), _names() (+9 more)

### Community 48 - "typing"
Cohesion: 0.07
Nodes (17): handle_message(), _handle_suggest_callback(), _safe_answer(), process_updates(), run_polling(), Submitter, decide_suggestion(), decode_suggest_callback() (+9 more)

### Community 50 - "test_application_portfolio.py"
Cohesion: 0.06
Nodes (54): Configuration, Phase 13 shortlist, Pipeline, Selection, allocate_portfolio(), can_take(), identity(), take() (+46 more)

### Community 51 - "test_priority.py"
Cohesion: 0.16
Nodes (20): apply_priority(), load_priority_config(), priority_is_current(), PriorityDecision, role_family_component(), _job(), test_dream_company_is_only_a_configured_boost(), test_eligibility_unknown_is_not_ineligible() (+12 more)

### Community 52 - "Phase 5 role classification"
Cohesion: 0.29
Nodes (6): Inputs, Limits, Output, Phase 5 role classification, Taxonomy, When it runs again

### Community 53 - "test_company_intelligence_v2.py"
Cohesion: 0.17
Nodes (9): CompanyIntelProvider, CompanyLookupResult, CompanySourceDocument, refresh_company_intelligence(), _one(), _Provider, _signals(), test_changed_page_replaces_that_source_and_keeps_another() (+1 more)

### Community 54 - "diagnostics.py"
Cohesion: 0.15
Nodes (10): effective_baseline(), effective_config_hash(), fingerprint_profile(), profile_hash(), public_config(), write_effective_baseline(), test_baseline_file_has_no_secrets(), test_config_hash_changes_when_internship_only_changes() (+2 more)

### Community 55 - "priority.py"
Cohesion: 0.13
Nodes (23): _combine(), company_domain_component(), _company_signals(), _components(), dream_company_component(), eligibility_component(), _explicit_sections(), fit_component() (+15 more)

### Community 56 - "main.py"
Cohesion: 0.06
Nodes (32): configure_logging(), _build_doctor_report(), build_parser(), _cmd_benchmark(), _cmd_build_baseline(), _cmd_health(), _cmd_poll(), _cmd_prep_pack() (+24 more)

### Community 57 - "Phase 2 search taxonomy"
Cohesion: 0.50
Nodes (3): Ambiguous phrases, Phase 2 search taxonomy, What was added

### Community 58 - "Benchmark — Product Manager @ T-Mobile"
Cohesion: 0.33
Nodes (5): Benchmark — Product Manager @ T-Mobile, Dimensions, Gaps, Recommendations, Strengths

### Community 59 - "get_health_report"
Cohesion: 0.16
Nodes (14): PipelineRun, PipelineStageRun, _brief(), format_health_report(), get_health_report(), _recent_failures(), _repeated_failures(), _run_view() (+6 more)

### Community 60 - "db.py"
Cohesion: 0.10
Nodes (17): _company_name(), _dialect_name(), _drop_structured_jd(), _ensure_company_columns(), _ensure_job_columns(), get_recently_applied_companies(), get_session_factory(), _incoming_description_unusable() (+9 more)

### Community 61 - "test_cover_letter.py"
Cohesion: 0.16
Nodes (10): cap_cover_letter(), _fallback_cover_letter(), generate_cover_letter(), build_cover_letter_user(), _job(), _ScriptedClient, test_cap_cover_letter_cuts_on_sentence_boundary(), test_cap_cover_letter_hard_slice_without_punctuation() (+2 more)

### Community 62 - "tracker.py"
Cohesion: 0.20
Nodes (15): _add_event(), application_method(), backfill_submitted_applications(), _event_exists(), _get_or_create(), record_manual_review(), record_outcome(), record_prefill() (+7 more)

### Community 63 - "classify_role"
Cohesion: 0.19
Nodes (14): classify_role(), _jd(), test_cache_recomputes_only_when_hash_or_version_changes(), test_collaboration_responsibility_is_not_a_secondary_family(), test_hybrid_roles_keep_a_second_family(), test_interaction_evidence_from_the_model_is_rejected(), test_interaction_is_not_a_second_family(), test_llm_prompt_includes_structured_responsibilities() (+6 more)

### Community 64 - "test_webhook.py"
Cohesion: 0.26
Nodes (5): client(), test_health(), test_webhook_ignored_without_callback(), test_webhook_rejects_bad_secret(), test_webhook_routes_callback()

### Community 65 - "build_llm_client"
Cohesion: 0.10
Nodes (12): Build order and status, Coding conventions, Commands, Confirmed product decisions, Project, Repository layout, Scoring specifics (Step 3), Tech stack (+4 more)

### Community 66 - "normalize_company_name"
Cohesion: 0.29
Nodes (6): canonical_company_name(), normalize_company_name(), _without_trailing_suffix(), test_legal_suffixes_do_not_collapse_distinct_names(), test_normalization_is_deterministic(), test_version_and_normalization_stay_explicit()

### Community 67 - "answers.py"
Cohesion: 0.15
Nodes (10): _discovery_channel(), _latest_education(), _matches(), needs_human_review(), _norm(), resolve_deterministic(), _split_name(), test_deterministic_eeo_decline() (+2 more)

### Community 68 - "prep.py"
Cohesion: 0.13
Nodes (17): _dedupe(), _fit_lines(), _load_canonical_shortlist(), _mark_sent(), _notify_empty(), PrepSummary, render_job_card(), render_shortlist() (+9 more)

### Community 71 - "alerts.py"
Cohesion: 0.20
Nodes (10): AlertSummary, build_alert_caption(), _send_one(), send_pending_alerts(), get_unsent_alerts(), test_build_alert_caption(), test_scoring_error_does_not_alert(), test_send_pending_alerts_empty() (+2 more)

### Community 72 - "HttpCompanyIntelProvider"
Cohesion: 0.25
Nodes (4): HttpCompanyIntelProvider, test_http_provider_handles_timeout_and_malformed_pages(), ok(), test_http_provider_keeps_the_caller_source_type()

### Community 73 - "linkedin_jobspy.py"
Cohesion: 0.19
Nodes (10): _dataframe_to_postings(), _effective_windows(), _explicit_company_url(), _external_id(), fetch_linkedin_indeed(), _google_search_term(), _location_matches(), _parse_posted_at() (+2 more)

### Community 75 - "telemetry.py"
Cohesion: 0.18
Nodes (7): action_delay_bounds(), type_like_human(), typing_delay_bounds(), test_delay_bounds_from_settings(), test_delay_bounds_swap_when_inverted(), test_human_delay_jitter_in_range(), test_human_delay_respects_explicit_bounds()

### Community 76 - "Phase 1 discovery architecture"
Cohesion: 0.10
Nodes (21): 40/40/15/5 priority model, Current problem, New architecture, Phase 1 discovery architecture, Provenance, Purpose, Role families, Search allocation (+13 more)

### Community 77 - "FakeTransport"
Cohesion: 0.19
Nodes (8): _should_retry_telegram(), FakeTransport, test_answer_callback(), test_chat_id_property(), test_get_updates_extends_http_timeout(), test_send_document_builds_payload(), test_send_photo_builds_payload(), test_should_retry_telegram()

### Community 78 - "Phase 18 — Production reliability and monitoring"
Cohesion: 0.13
Nodes (14): Architecture, Backlog diagnostics, CLI, Configuration, Failure isolation, Health states, Logging, Phase 18 — Production reliability and monitoring (+6 more)

### Community 79 - "init_db"
Cohesion: 0.20
Nodes (7): get_engine(), init_db(), reset_engine(), database_reachable(), test_context_column_is_added_to_an_existing_table(), test_ensure_job_columns_on_legacy_table(), test_health_command_prints_no_secrets()

### Community 80 - "Priority 2.0"
Cohesion: 0.29
Nodes (6): Freshness, dream company, and workflow, Hash, Priority 2.0, Program and domain evidence, Role alignment, Weights

### Community 81 - "WorkdaySubmitter"
Cohesion: 0.18
Nodes (7): SessionMissingError, WorkdaySubmitter, test_submit_generic_exception(), test_submit_missing_url(), test_submit_session_missing(), boom_launch(), test_submit_unparseable_without_tenant()

### Community 82 - "RawPosting"
Cohesion: 0.06
Nodes (28): citizenship_restriction(), _clearance_clauses(), clearance_requirement(), evaluate_job(), FilterResult, has_internship_signal(), _haystack(), location_acceptable() (+20 more)

### Community 83 - "test_apply_url.py"
Cohesion: 0.20
Nodes (12): ApplyKind, classify_apply_url(), _host(), is_automateable_apply_url(), is_workday_url(), workday_parts(), _cmd_list_apply(), test_classify_company_site() (+4 more)

### Community 84 - "Phase 14 application portfolio"
Cohesion: 0.29
Nodes (6): Capacity, Decisions, Phase 14 application portfolio, Pipeline, Role-family mix, Who can be allocated

### Community 85 - "extract_company_facts"
Cohesion: 0.29
Nodes (5): extract_company_facts(), merge_company_facts(), test_extractor_keeps_unstated_facts_null(), test_merge_company_facts_keeps_omitted_fields(), test_prestige_language_is_not_a_fact()

### Community 86 - "feedback.py"
Cohesion: 0.11
Nodes (23): Application, ApplicationEvent, FeedbackRun, FeedbackSignal, get_application_by_id(), get_application_events(), get_feedback_run(), get_feedback_signals() (+15 more)

### Community 87 - "test_feedback.py"
Cohesion: 0.14
Nodes (24): _adjustment(), build_feedback(), _counts(), _group_hit(), _half_up(), _in_cohort(), load_feedback_config(), _minimum() (+16 more)

### Community 88 - "profile.py"
Cohesion: 0.10
Nodes (34): Address, Education, Exclusions, Experience, Identity, Preferences, WorkAuthorization, _make_base_pdf() (+26 more)

### Community 90 - "Phase 8 company intelligence"
Cohesion: 0.29
Nodes (6): Names and reuse, Phase 8 company intelligence, Schema, Sources, What it is, What this phase does not change

### Community 91 - "test_llm_provider.py"
Cohesion: 0.10
Nodes (19): GeminiClient, _FakeAio, _FakeAsyncModels, _FakeCandidate, _FakeGenaiClient, _FakeGenerateResponse, test_active_models_ignore_anthropic_names(), test_active_models_ignore_other_providers() (+11 more)

### Community 93 - "_input_hash"
Cohesion: 0.48
Nodes (5): _as_utc(), _freshness_day(), _input_hash(), _iso(), posted()

### Community 95 - "test_scorer.py"
Cohesion: 0.09
Nodes (20): approx_tokens(), cache_block(), compact_json_dumps(), minify_job(), parse_score(), build_outreach_user(), build_scoring_system_blocks(), build_scoring_user() (+12 more)

### Community 97 - "Phase 16 feedback learning"
Cohesion: 0.33
Nodes (5): Evidence and shrinkage, Phase 16 feedback learning, Rates, Segments, Who is counted

### Community 98 - "scorer/engine.py"
Cohesion: 0.08
Nodes (27): build_embedder(), _cache_path(), clears_threshold(), cosine(), Embedder, jd_vector(), load_profile_embedding(), save_profile_embedding() (+19 more)

### Community 99 - "LLMClient"
Cohesion: 0.09
Nodes (9): LLMClient, _attach_priority(), _JobOutcome, _priority_evidence(), Scorer, run_one(), ScoreSummary, Evaluation (+1 more)

### Community 100 - "Phase 7 role-family weighting"
Cohesion: 0.22
Nodes (8): Canonical portfolio, Configuration, Four different questions, Phase 7 role-family weighting, Unknown classification, What is stored, What this phase does not do, Where the family comes from

### Community 101 - "calibration.py"
Cohesion: 0.13
Nodes (34): _as_utc(), _append_buckets(), _append_short_target(), _append_slice(), _append_target_metrics(), _append_topk(), _bucket_name(), build_calibration() (+26 more)

### Community 103 - "Phase 15 application tracker"
Cohesion: 0.33
Nodes (5): Method and time, Phase 15 application tracker, States and outcomes, What this is not, When a row is created

### Community 104 - "get_settings"
Cohesion: 0.12
Nodes (7): launch_context(), _new_context(), new_page(), save_storage_state(), save_session(), get_settings(), save_linkedin_session()

### Community 106 - "3. Hard filters (before any model)"
Cohesion: 0.18
Nodes (11): 3.10 What a survivor looks like, 3.1 Company blocklist, 3.2 Exclusion keywords, 3.3 Clearance language, 3.4 Staffing agencies, 3.5 Internship gate, 3.6 Seniority filter (separate from the internship gate), 3.7 Years of experience (+3 more)

### Community 107 - "linkedin_people.py"
Cohesion: 0.07
Nodes (26): auto_discover_peers(), _crawl(), BlockerError, build_people_search_url(), _detect_blocker(), discover_peers(), extract_profile_urls(), _heuristic_parse() (+18 more)

### Community 108 - "Tier"
Cohesion: 0.23
Nodes (13): Data model (core/db.py), Status lifecycle, get_unsent_prep_pack_jobs(), Tier, _cmd_doctor(), _save_vector(), _status_for_tier(), _job() (+5 more)

### Community 109 - "Job Agent"
Cohesion: 0.12
Nodes (15): Application prep packs (LinkedIn / Indeed), Deploy with Docker, Job Agent, Layout, LinkedIn peer benchmarking (optional, off by default), Resumes (Step 4), Run automation (Step 5), Run ingestion (Step 2) (+7 more)

### Community 110 - "calculate_priority"
Cohesion: 0.19
Nodes (17): Output, Cache and storage, calculate_priority(), _job(), _signal(), test_confidence_and_structured_evidence(), test_domains_are_capped_and_irrelevant_domains_add_nothing(), test_eligibility_order_and_unknown() (+9 more)

### Community 111 - "Phase 12 priority ranking"
Cohesion: 0.50
Nodes (3): Components, Phase 12 priority ranking, Version

### Community 112 - "test_calibration.py"
Cohesion: 0.33
Nodes (13): brier_score(), _calibration(), _case(), _feedback(), _rows(), test_brier_score_is_mean_squared_error(), test_feedback_brier_beats_baseline_without_naming_a_winner(), test_folds_are_chronological_and_do_not_overlap() (+5 more)

### Community 113 - "resolve_company"
Cohesion: 0.23
Nodes (11): CompanyIntelligence, _apply_facts(), _by_key(), _clear_facts(), empty_company_context(), get_company_intelligence(), _new_row(), resolve_company() (+3 more)

### Community 115 - "Company intelligence 2.0"
Cohesion: 0.33
Nodes (5): Company intelligence 2.0, Company versus job, Sources and refresh, What it does not store, What it stores

### Community 116 - "Job"
Cohesion: 0.12
Nodes (12): ApplyRunner, ApplySummary, _eligible(), _ensure_tenant(), _log_explicit_skip(), _ready_for_explicit_apply(), _reload_job(), Applicator (+4 more)

### Community 119 - "role_classify.py"
Cohesion: 0.15
Nodes (18): _clause_containing(), _clip_items(), _deterministic(), _is_interaction(), _item_text(), _ModelLabel, _parse_model(), _phrase_hits() (+10 more)

### Community 121 - "targets.py"
Cohesion: 0.07
Nodes (16): reload_profile(), _load_yaml(), parse_workday_url(), reload_targets(), SearchConfig, Targets, WorkdayParts, WorkdayTenant (+8 more)

### Community 122 - "Multi-dimensional role classification"
Cohesion: 0.29
Nodes (6): Cache, Contract, Function versus interaction, Multi-dimensional role classification, Non-goals, What the classifier reads

### Community 125 - "5. How fit is scored"
Cohesion: 0.22
Nodes (7): 10. File map, 5.1 What the model is, 5.2 The two inputs, 5.3 The rubric, verbatim in meaning, 5.4 What the code does with the score, 5.5 What a number means, 5. How fit is scored

### Community 127 - "How jobs are found, filtered, scored, and sent"
Cohesion: 0.25
Nodes (7): 1. What a run is, 4.1 Pre-score rank (`prerank_score`), 4.2 Embedding gate (this does drop jobs), 4.3 Fit-model cap, 4. How results are prioritised today, 7. Statuses, in one pass, How jobs are found, filtered, scored, and sent

### Community 128 - "load_persisted_calibration"
Cohesion: 0.36
Nodes (7): CalibrationMetric, CalibrationRun, get_calibration_metrics(), get_calibration_run(), save_calibration_run(), load_persisted_calibration(), persist_calibration()

### Community 129 - "test_role_weights.py"
Cohesion: 0.15
Nodes (17): get_role_family_weight(), load_role_family_weights(), _validate(), weight_for_subfamily(), test_company_and_vector_are_not_weight_inputs(), test_discovery_capacity_stays_independent(), test_discovery_labels_do_not_choose_the_weight(), test_every_phase5_primary_family_has_a_weight() (+9 more)

### Community 130 - "Any"
Cohesion: 0.11
Nodes (10): AnthropicClient, _attempt(), _as_int(), _finish_reason(), _attempt(), _lower_thinking(), _attempt(), system_blocks_to_text() (+2 more)

### Community 131 - "2. Where jobs come from"
Cohesion: 0.29
Nodes (7): 2.1 Search terms, 2.2 Sites and the exact JobSpy arguments, 2.3 How each site treats "posted in the last 36 hours", 2.4 What is kept from a JobSpy row, 2.5 Workday, separately from LinkedIn, 2.6 Save and dedupe, 2. Where jobs come from

### Community 132 - "8. The weight discussion (not built)"
Cohesion: 0.33
Nodes (6): 8.1 What you asked for, 8.2 Decisions you agreed with, 8.3 A weight table we used as a sketch, 8.4 What we said the rubric should do for career-switch roles, 8.5 How that would sit on the current pipeline, 8. The weight discussion (not built)

### Community 133 - "9. Pain points we have actually hit or spelled out"
Cohesion: 0.33
Nodes (6): 9.1 Discovery, 9.2 Filters, 9.3 Scoring, 9.4 What you receive, 9.5 Operations, 9. Pain points we have actually hit or spelled out

### Community 134 - "re"
Cohesion: 0.06
Nodes (39): _find_cross_source_job(), canonicalize_job_url(), _is_tracking_param(), locations_agree(), locations_conflict(), normalize_title(), same_employer(), same_posting_url() (+31 more)

### Community 136 - "6. What is sent to you"
Cohesion: 0.40
Nodes (5): 6.1 Who is eligible, 6.2 The shortlist rule, 6.3 Each line, 6.4 If brief mode is turned off, 6. What is sent to you

### Community 143 - "Phase 9 visa and eligibility"
Cohesion: 0.29
Nodes (6): Education, graduation, experience, location, dates, Phase 9 visa and eligibility, Sponsorship, citizenship, and clearance, States, What the profile contributes, What this phase does not do

### Community 145 - "Phase 6 candidate fit"
Cohesion: 0.40
Nodes (4): Dimensions, Not in this phase, Phase 6 candidate fit, When the model is not called

### Community 148 - "test_robustness.py"
Cohesion: 0.09
Nodes (19): Candidate baseline, Discovery baseline, Local versus production, Phase 0 baseline, Production baseline, Scoring baseline, Sponsorship behavior locked by tests, Tests (+11 more)

## Knowledge Gaps
- **172 isolated node(s):** `job-agent`, `ScrapeSummary`, `_Sites`, `_FakeAio`, `Project` (+167 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 1080 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **11 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Job` connect `Job` to `test_outcomes.py`, `structured_jd.py`, `test_role_weights.py`, `test_eligibility.py`, `migrate_to_neon.py`, `test_vector_recovery.py`, `re`, `test_career_intelligence.py`, `test_fit.py`, `benchmark/engine.py`, `ingest.py`, `outreach.py`, `eligibility.py`, `test_application_tracker.py`, `test_structured_jd.py`, `test_robustness.py`, `baseline.py`, `diff.py`, `test_company_intelligence.py`, `get_job_by_id`, `test_pacing.py`, `session_scope`, `test_vector_gate.py`, `company_intelligence.py`, `handle_callback`, `test_role_classify.py`, `review.py`, `test_phase13_shortlist.py`, `send_prep_pack`, `test_prep_builder.py`, `workday.py`, `compiler.py`, `test_monitoring.py`, `skills.py`, `test_answers.py`, `vector_recovery.py`, `typing`, `test_application_portfolio.py`, `test_priority.py`, `priority.py`, `main.py`, `get_health_report`, `db.py`, `test_cover_letter.py`, `tracker.py`, `answers.py`, `prep.py`, `alerts.py`, `WorkdaySubmitter`, `RawPosting`, `feedback.py`, `test_feedback.py`, `profile.py`, `_input_hash`, `test_scorer.py`, `scorer/engine.py`, `LLMClient`, `Tier`, `calculate_priority`, `test_calibration.py`?**
  _High betweenness centrality (0.170) - this node is a cross-community bridge._
- **Why does `Profile` connect `Profile` to `test_vector_recovery.py`, `test_eligibility.py`, `test_career_intelligence.py`, `test_fit.py`, `re`, `benchmark/engine.py`, `ingest.py`, `.total_years_experience`, `outreach.py`, `Phase 9 visa and eligibility`, `eligibility.py`, `test_robustness.py`, `baseline.py`, `diff.py`, `get_job_by_id`, `session_scope`, `test_vector_gate.py`, `send_prep_pack`, `test_prep_builder.py`, `workday.py`, `compiler.py`, `test_answers.py`, `vector_recovery.py`, `test_priority.py`, `diagnostics.py`, `priority.py`, `test_cover_letter.py`, `answers.py`, `prep.py`, `linkedin_jobspy.py`, `RawPosting`, `profile.py`, `_input_hash`, `test_scorer.py`, `scorer/engine.py`, `LLMClient`, `calculate_priority`, `Job`, `targets.py`, `5. How fit is scored`?**
  _High betweenness centrality (0.105) - this node is a cross-community bridge._
- **Why does `get_settings()` connect `get_settings` to `Any`, `test_eligibility.py`, `migrate_to_neon.py`, `clients.py`, `test_career_intelligence.py`, `test_vector_recovery.py`, `test_discovery.py`, `benchmark/engine.py`, `Profile`, `conftest.py`, `textclean.py`, `outreach.py`, `vault.py`, `pipeline.py`, `TelegramClient`, `baseline.py`, `Settings`, `test_robustness.py`, `diff.py`, `test_pacing.py`, `session_scope`, `test_vector_gate.py`, `scheduler.py`, `test_phase13_shortlist.py`, `send_prep_pack`, `test_prep_builder.py`, `workday.py`, `compiler.py`, `test_monitoring.py`, `skills.py`, `test_answers.py`, `typing`, `test_application_portfolio.py`, `test_company_intelligence_v2.py`, `diagnostics.py`, `main.py`, `db.py`, `test_cover_letter.py`, `test_webhook.py`, `answers.py`, `prep.py`, `telemetry.py`, `init_db`, `RawPosting`, `profile.py`, `OpenAIEmbedder`, `test_llm_provider.py`, `test_scorer.py`, `scorer/engine.py`, `LLMClient`, `linkedin_people.py`, `Tier`, `Job`, `targets.py`?**
  _High betweenness centrality (0.103) - this node is a cross-community bridge._
- **Are the 175 inferred relationships involving `Job` (e.g. with `Data model (core/db.py)` and `AnswerResolver`) actually correct?**
  _`Job` has 175 INFERRED edges - model-reasoned connections that need verification._
- **Are the 259 inferred relationships involving `Profile` (e.g. with `AnswerResolver` and `_latest_education()`) actually correct?**
  _`Profile` has 259 INFERRED edges - model-reasoned connections that need verification._
- **Are the 179 inferred relationships involving `Status` (e.g. with `Data model (core/db.py)` and `ApplyRunner`) actually correct?**
  _`Status` has 179 INFERRED edges - model-reasoned connections that need verification._
- **Are the 138 inferred relationships involving `Source` (e.g. with `Data model (core/db.py)` and `_eligible()`) actually correct?**
  _`Source` has 138 INFERRED edges - model-reasoned connections that need verification._