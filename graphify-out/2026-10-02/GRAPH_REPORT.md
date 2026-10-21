# Graph Report - Automatic job search  (2026-10-02)

## Corpus Check
- 193 files · ~149,119 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 13 file(s) not represented in the graph (top: (none) 8, .typ 2, .mdc 1)

## Summary
- 3209 nodes · 10789 edges · 125 communities (115 shown, 10 thin omitted)
- Extraction: 89% EXTRACTED · 11% INFERRED · 0% AMBIGUOUS · INFERRED: 1181 edges (avg confidence: 0.94)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `880a14cd`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- TelegramClient
- structured_jd.py
- test_structured_jd.py
- test_eligibility.py
- feedback.py
- clients.py
- get_job_by_id
- test_fit.py
- test_discovery.py
- test_calibration.py
- Profile
- ingest.py
- test_feedback.py
- textclean.py
- test_application_portfolio.py
- prerank.py
- eligibility.py
- structlog
- alerts.py
- test_monitoring.py
- pipeline.py
- Any
- test_resume.py
- Settings
- workday_rest.py
- migrate_to_neon.py
- AnswerResolver
- review.py
- Any
- test_pipeline_order_and_aggregation
- test_doctor.py
- diff.py
- scheduler.py
- test_company_intelligence.py
- human_delay
- runner.py
- Remaining Manual Setup
- auto_discover_peers
- ScoreOnlyClient
- session_scope
- calibration.py
- answers.py
- workday.py
- compiler.py
- settings.py
- typing
- RawPosting
- benchmark/engine.py
- test_role_classify.py
- WorkdaySubmitter
- application_portfolio.py
- calculate_priority
- Phase 5 role classification
- test_phase13_shortlist.py
- diagnostics.py
- priority.py
- test_prep_builder.py
- Phase 2 search taxonomy
- Benchmark — Product Manager @ T-Mobile
- company_intelligence.py
- test_company_intelligence_v2.py
- test_vector_gate.py
- test_application_tracker.py
- get_jobs_by_status
- load_persisted_calibration
- get_recently_applied_companies
- init_db
- db.py
- Job
- job-agent
- monitoring.py
- shortlist.py
- linkedin_jobspy.py
- phase10-false-negative-protection.md
- _build_doctor_report
- Phase 1 discovery architecture
- vault.py
- _as_utc
- HttpCompanyIntelProvider
- Priority 2.0
- builder.py
- filters.py
- Structured JD intelligence
- job_identity.py
- test_workday_locators.py
- profile.py
- models.py
- Phase 8 company intelligence
- test_llm_provider.py
- correction1-recruiting-universe.md
- main.py
- test_cover_letter.py
- phase11-job-identity.md
- Phase 16 feedback learning
- get_settings
- 5. How fit is scored
- Phase 18 — Production reliability and monitoring
- Phase 15 application tracker
- CompanyIntelligence
- textmatch.py
- 3. Hard filters (before any model)
- linkedin_people.py
- 2. Where jobs come from
- Job Agent
- test_priority_v2.py
- Phase 12 priority ranking
- classify_role
- Phase 0 baseline
- Company intelligence 2.0
- suggest.py
- phase17-calibration-benchmark.md
- Phase 4 JD ingestion
- role_classify.py
- sort_by_priority
- targets.py
- Multi-dimensional role classification
- normalize_company_name
- 9. Pain points we have actually hit or spelled out
- 8. The weight discussion (not built)
- test_role_weights.py
- .total_years_experience
- How jobs are found, filtered, scored, and sent
- 6. What is sent to you
- LLMClient

## God Nodes (most connected - your core abstractions)
1. `Job` - 343 edges
2. `Profile` - 271 edges
3. `session_scope()` - 266 edges
4. `Status` - 227 edges
5. `Source` - 197 edges
6. `get_settings()` - 161 edges
7. `upsert_job()` - 133 edges
8. `get_job_by_id()` - 133 edges
9. `init_db()` - 85 edges
10. `TelegramClient` - 81 edges

## Surprising Connections (you probably didn't know these)
- `Checklist (your remaining work)` --references--> `save_session()`  [INFERRED]
  SETUP.md → automation/login.py
- `Run review bot (Step 6)` --references--> `send_pending_alerts()`  [INFERRED]
  README.md → bot/alerts.py
- `What the profile contributes` --references--> `Profile`  [INFERRED]
  docs/phase9-visa-eligibility.md → config/profile.py
- `New architecture` --references--> `load_targets()`  [INFERRED]
  docs/phase1-discovery-architecture.md → config/targets.py
- `Health states` --references--> `get_health_report()`  [INFERRED]
  docs/phase18-production-reliability-monitoring.md → orchestrator/health.py

## Import Cycles
- None detected.

## Communities (125 total, 10 thin omitted)

### Community 0 - "TelegramClient"
Cohesion: 0.04
Nodes (69): _decision_caption(), handle_callback(), handle_message(), _handle_outcome_callback(), _handle_suggest_callback(), _safe_answer(), build_outcome_keyboard(), button() (+61 more)

### Community 1 - "structured_jd.py"
Cohesion: 0.13
Nodes (37): _authorization(), AuthorizationEvidence, _availability(), _clause_at(), _clauses(), _clip(), _degree_state(), _domain() (+29 more)

### Community 2 - "test_structured_jd.py"
Cohesion: 0.15
Nodes (17): StructuredJobDescription, attach_structured_jd(), extract_structured_jd(), get_structured_jd(), structured_jd_is_current(), _areas(), _job(), test_changed_upsert_drops_the_old_reading() (+9 more)

### Community 3 - "test_eligibility.py"
Cohesion: 0.15
Nodes (20): assign_eligibility(), attach_eligibility(), eligibility_column_types(), eligibility_is_current(), EligibilityDecision, evaluate_eligibility(), profile_eligibility_hash(), _job() (+12 more)

### Community 4 - "feedback.py"
Cohesion: 0.15
Nodes (21): FeedbackRun, get_feedback_run(), get_latest_feedback_run(), _adjustment(), _band(), build_feedback(), _counts(), FeedbackCase (+13 more)

### Community 5 - "clients.py"
Cohesion: 0.09
Nodes (20): _backoff_delay(), call_with_resilience(), is_permanent_account_error(), is_transient(), LLMBillingError, LLMError, _status_code(), suggested_delay() (+12 more)

### Community 6 - "get_job_by_id"
Cohesion: 0.23
Nodes (21): apply_pending(), _reload_job(), get_job_by_id(), _touch_vector_score(), FakeApplicator, _seed_job(), test_allocation_removed_before_execution_is_skipped(), test_apply_linkedin_with_workday_url() (+13 more)

### Community 7 - "test_fit.py"
Cohesion: 0.07
Nodes (40): approx_tokens(), cache_block(), compact_json_dumps(), minify_job(), build_fit_system_blocks(), build_fit_user(), cached_fit(), _Dimension (+32 more)

### Community 8 - "test_discovery.py"
Cohesion: 0.08
Nodes (33): Search allocation, allocate_units(), AllocItem, build_discovery_plan(), DiscoveryConfig, DiscoverySource, _enabled_queries(), enabled_query_texts() (+25 more)

### Community 9 - "test_calibration.py"
Cohesion: 0.22
Nodes (19): brier_score(), build_calibration(), CalibrationReport, load_calibration_config(), run_calibration(), load_feedback_config(), _calibration(), _case() (+11 more)

### Community 10 - "Profile"
Cohesion: 0.09
Nodes (42): Profile, evaluate(), max_acceptable_years(), sponsorship_signal(), test_sponsorship_and_false_friends(), test_missing_or_weak_evidence_does_not_filter(), _posting(), test_clearance_regex_pattern() (+34 more)

### Community 11 - "ingest.py"
Cohesion: 0.11
Nodes (16): _stamp_role_family_weight(), CoverageReport, fail_unrecorded(), log_coverage(), SearchObservation, write_coverage(), DiscoveryPlan, log_discovery_plan() (+8 more)

### Community 12 - "test_feedback.py"
Cohesion: 0.17
Nodes (16): ApplicationEvent, get_application_events(), list_events_for_applications(), list_jobs_by_ids(), list_submitted_applications(), _case_from_rows(), load_feedback_cases(), shrink_rate() (+8 more)

### Community 13 - "textclean.py"
Cohesion: 0.12
Nodes (21): content_hash(), _drop_boilerplate_lines(), _extract_body(), extract_sections(), html_to_text(), JdStatus, normalize_description(), _normalize_whitespace() (+13 more)

### Community 14 - "test_application_portfolio.py"
Cohesion: 0.11
Nodes (27): _job(), _NotStaged, _Spy, test_company_cap_is_per_run_and_suffix_aware(), test_config_rejects_a_bool_cap(), test_cooldown_blocks_the_company_and_leaves_scores(), test_daily_capacity_defers_the_rest(), test_ignored_job_does_not_consume_a_slot() (+19 more)

### Community 15 - "prerank.py"
Cohesion: 0.21
Nodes (11): prerank_jobs(), prerank_score(), _source_weight(), _job(), test_dream_company_boost(), test_intern_title_outranks_fulltime(), test_new_source_scored_without_error(), test_prerank_jobs_empty() (+3 more)

### Community 16 - "eligibility.py"
Cohesion: 0.15
Nodes (26): _ask_model(), _citizenship(), _clearance(), _current_student(), _dates(), _decision_from_job(), _dim(), DimensionResult (+18 more)

### Community 17 - "structlog"
Cohesion: 0.12
Nodes (23): build_coverage_report(), add_planned(), group_for(), GroupMetrics, _jsonable(), observe_search(), _planned_slots(), QueryMetrics (+15 more)

### Community 18 - "alerts.py"
Cohesion: 0.20
Nodes (10): AlertSummary, build_alert_caption(), _send_one(), send_pending_alerts(), get_unsent_alerts(), test_build_alert_caption(), test_scoring_error_does_not_alert(), test_send_pending_alerts_empty() (+2 more)

### Community 19 - "test_monitoring.py"
Cohesion: 0.11
Nodes (23): close_pipeline_run(), list_pipeline_runs(), open_pipeline_run(), _job(), test_a_new_run_does_not_duplicate_applications(), test_backlog_and_stale_jobs(), test_fresh_running_run_is_not_stale(), test_health_command_prints_no_secrets() (+15 more)

### Community 20 - "pipeline.py"
Cohesion: 0.11
Nodes (19): stage_counters(), _allocated_ids(), _note_skipped(), PipelineSummary, _portfolio_stage(), _prepare_shortlisted_resumes(), _run_opened_pipeline(), _apply_allocated() (+11 more)

### Community 22 - "test_resume.py"
Cohesion: 0.12
Nodes (19): clean_name(), compile_resume(), build_resume_data(), extract_job_terms(), _grounded_summary(), RankedBullet, reorder_skills(), score_bullet() (+11 more)

### Community 23 - "Settings"
Cohesion: 0.13
Nodes (4): Settings, test_fallback_models_empty_for_anthropic(), test_fallback_models_exclude_primary(), test_settings_defaults_provider_gemini()

### Community 24 - "workday_rest.py"
Cohesion: 0.08
Nodes (22): WorkdayTenant, _as_text(), _company_name(), _one(), _fetch_detail(), _fetch_listing_page(), fetch_workday(), _is_recent_posted_on() (+14 more)

### Community 25 - "migrate_to_neon.py"
Cohesion: 0.13
Nodes (12): _absolute_sqlite_url(), normalize_database_url(), _cell(), _copy_table(), _counts(), main(), _reset_sequences(), _row() (+4 more)

### Community 26 - "AnswerResolver"
Cohesion: 0.17
Nodes (9): AnswerResolver, one(), AnswerSource, FakeAnswerClient, test_cover_letter_field_uses_stored_text(), test_resolver_banned_word_retry(), test_resolver_blank_for_unknown_closed(), test_resolver_deterministic_path() (+1 more)

### Community 27 - "review.py"
Cohesion: 0.14
Nodes (13): build_keyboard(), build_review_caption(), format_answers_message(), format_cover_letter_message(), ReviewSummary, _send_one(), send_pending_reviews(), get_unsent_pending_reviews() (+5 more)

### Community 28 - "Any"
Cohesion: 0.11
Nodes (10): AnthropicClient, _attempt(), _as_int(), _finish_reason(), _attempt(), _lower_thinking(), _attempt(), system_blocks_to_text() (+2 more)

### Community 29 - "test_pipeline_order_and_aggregation"
Cohesion: 0.12
Nodes (17): _FakeSummary, test_pipeline_order_and_aggregation(), fake_alerts(), fake_apply(), fake_ingestion(), fake_outcomes(), fake_prep(), fake_resume() (+9 more)

### Community 30 - "test_doctor.py"
Cohesion: 0.44
Nodes (7): _cmd_doctor(), _job(), test_doctor_cooldown(), test_doctor_empty_db(), test_doctor_outcomes(), test_doctor_vector_gate(), test_doctor_with_jobs()

### Community 31 - "diff.py"
Cohesion: 0.15
Nodes (18): RoleBaseline, SkillPlacement, SkillProvenance, apply_approved_suggestions_to_resume_data(), _baseline_skill_keys(), classify_provenance(), diff_against_baseline(), diff_against_baseline_async() (+10 more)

### Community 32 - "scheduler.py"
Cohesion: 0.07
Nodes (13): configure_logging(), _cmd_serve(), build_scheduler(), parse_hhmm(), run_service(), _noop(), test_build_scheduler_invalid_timezone(), test_build_scheduler_registers_jobs() (+5 more)

### Community 33 - "test_company_intelligence.py"
Cohesion: 0.18
Nodes (19): attach_company_intelligence(), extract_company_facts(), merge_company_facts(), resolve_company(), FakeProvider, test_ambiguous_names_stay_separate(), test_company_sources_accumulate_and_a_failed_refresh_keeps_them(), test_complete_record_and_ignored_claims() (+11 more)

### Community 34 - "human_delay"
Cohesion: 0.16
Nodes (8): action_delay_bounds(), human_delay(), type_like_human(), typing_delay_bounds(), test_delay_bounds_from_settings(), test_delay_bounds_swap_when_inverted(), test_human_delay_jitter_in_range(), test_human_delay_respects_explicit_bounds()

### Community 35 - "runner.py"
Cohesion: 0.05
Nodes (48): acquire(), AcquireResult, _clamp_multiplier(), _clock(), end_of_local_day(), gap_seconds(), is_pace_blocker(), note_pace_block() (+40 more)

### Community 36 - "Remaining Manual Setup"
Cohesion: 0.08
Nodes (25): 2a. Find a Workday URL, 2b. Edit `config/targets.yaml`, 3a. Run the save-session helper, 3b. What you do in the browser, 4a. Discover jobs (LinkedIn / Indeed + any real Workday tenants), 4b. Score with Gemini, 4c. Attach your base resume to staged jobs, 4d. Send LinkedIn/Indeed application prep pack (Telegram) (+17 more)

### Community 37 - "auto_discover_peers"
Cohesion: 0.14
Nodes (9): auto_discover_peers(), _crawl(), BlockerError, build_people_search_url(), _detect_blocker(), extract_profile_urls(), test_build_people_search_url_encodes_keywords(), test_extract_profile_urls_dedupes_and_caps() (+1 more)

### Community 39 - "session_scope"
Cohesion: 0.06
Nodes (73): Data model (core/db.py), Status lifecycle, get_job_by_source_id(), session_scope(), Source, Status, Tier, upsert_job() (+65 more)

### Community 40 - "calibration.py"
Cohesion: 0.16
Nodes (25): _append_buckets(), _append_short_target(), _append_slice(), _append_target_metrics(), _append_topk(), _bucket_name(), calibration_config_hash(), CalibrationFold (+17 more)

### Community 41 - "answers.py"
Cohesion: 0.11
Nodes (16): answers_to_payload(), _discovery_channel(), is_open_ended(), _latest_education(), _matches(), needs_human_review(), _norm(), resolve_deterministic() (+8 more)

### Community 42 - "workday.py"
Cohesion: 0.18
Nodes (9): click_by_role(), click_next(), _collect_labeled_fields(), detect_blocker(), _fill_field(), is_review_page(), safe_click(), screenshot() (+1 more)

### Community 43 - "compiler.py"
Cohesion: 0.10
Nodes (17): apply_fit_caps(), _baseline_pdf_for_job(), compile_for_job(), compile_pending(), compile_resume_data(), FitReport, _job_resume_output(), _next_fit_state() (+9 more)

### Community 44 - "settings.py"
Cohesion: 0.13
Nodes (8): What still needs the user (before live runs), launch_context(), _new_context(), new_page(), save_storage_state(), save_session(), Deploy with Docker, save_linkedin_session()

### Community 45 - "typing"
Cohesion: 0.07
Nodes (27): build_baseline_resume_data(), _normalize(), _slugify_role(), _synthetic_job_for_role(), aggregate_role_skills(), AggregatedSkill, _categorize(), extract_top_skills() (+19 more)

### Community 46 - "RawPosting"
Cohesion: 0.15
Nodes (8): RawPosting, test_company_enrichment_failure_does_not_stop_ingestion(), one_posting(), test_internship_signal_matches_the_existing_gate(), test_provider_failure_does_not_break_ingestion(), one_posting(), test_structured_jd_failure_does_not_stop_ingestion(), one_posting()

### Community 47 - "benchmark/engine.py"
Cohesion: 0.14
Nodes (16): BenchmarkReport, BenchmarkSummary, build_benchmark(), _derive_seniority(), DimensionScore, _education_rank(), _median(), _norm() (+8 more)

### Community 48 - "test_role_classify.py"
Cohesion: 0.23
Nodes (10): classification_is_current(), _FakeClient, _jd(), test_classifier_version_bump_invalidates_phase5_v1(), test_invalid_confidence_is_unknown(), test_invalid_model_output_falls_back_to_unknown(), test_role_families_follow_the_job(), test_short_or_ambiguous_text_is_unknown_without_a_model() (+2 more)

### Community 49 - "WorkdaySubmitter"
Cohesion: 0.18
Nodes (7): SessionMissingError, WorkdaySubmitter, test_submit_generic_exception(), test_submit_missing_url(), test_submit_session_missing(), boom_launch(), test_submit_unparseable_without_tenant()

### Community 50 - "application_portfolio.py"
Cohesion: 0.14
Nodes (20): Decisions, allocate_portfolio(), can_take(), identity(), take(), allocated_jobs(), apply_portfolio(), _bucket() (+12 more)

### Community 51 - "calculate_priority"
Cohesion: 0.16
Nodes (22): apply_priority(), calculate_priority(), _combine(), load_priority_config(), priority_is_current(), PriorityDecision, _reasons(), role_family_component() (+14 more)

### Community 52 - "Phase 5 role classification"
Cohesion: 0.29
Nodes (6): Inputs, Limits, Output, Phase 5 role classification, Taxonomy, When it runs again

### Community 53 - "test_phase13_shortlist.py"
Cohesion: 0.35
Nodes (11): select_shortlist(), _config(), _job(), test_apply_shortlist_is_idempotent_and_preserves_scores(), test_diversity_respects_company_cap_and_ignores_secondary_family(), test_family_diversity_is_a_soft_swap(), test_missing_dates_still_select(), test_non_staged_jobs_are_ignored() (+3 more)

### Community 54 - "diagnostics.py"
Cohesion: 0.16
Nodes (9): effective_baseline(), effective_config_hash(), profile_hash(), public_config(), write_effective_baseline(), test_baseline_file_has_no_secrets(), test_config_hash_changes_when_internship_only_changes(), test_effective_baseline_matches_public_fields() (+1 more)

### Community 55 - "priority.py"
Cohesion: 0.12
Nodes (26): is_dream_company(), _as_utc(), company_domain_component(), _company_signals(), _components(), dream_company_component(), eligibility_component(), _explicit_sections() (+18 more)

### Community 56 - "test_prep_builder.py"
Cohesion: 0.29
Nodes (6): FakeClient, _job(), test_build_job_section_filters_banned_words(), test_build_job_section_identity_and_essays(), test_compile_prep_pdf(), test_generate_prep_pack_writes_files()

### Community 57 - "Phase 2 search taxonomy"
Cohesion: 0.50
Nodes (3): Ambiguous phrases, Phase 2 search taxonomy, What was added

### Community 58 - "Benchmark — Product Manager @ T-Mobile"
Cohesion: 0.33
Nodes (5): Benchmark — Product Manager @ T-Mobile, Dimensions, Gaps, Recommendations, Strengths

### Community 59 - "company_intelligence.py"
Cohesion: 0.12
Nodes (18): _accumulate_sources(), _apply_context(), _compact(), _confidence_for(), _context_from(), extract_company_signals(), merge_company_signals(), _prefer_signal() (+10 more)

### Community 60 - "test_company_intelligence_v2.py"
Cohesion: 0.14
Nodes (9): CompanyIntelProvider, CompanyLookupResult, CompanySourceDocument, refresh_company_intelligence(), _one(), _Provider, _signals(), test_changed_page_replaces_that_source_and_keeps_another() (+1 more)

### Community 61 - "test_vector_gate.py"
Cohesion: 0.24
Nodes (21): profile_embed_text(), profile_hash(), score_pending(), FakeClient, _enable(), FakeEmbedder, _map(), _seed() (+13 more)

### Community 62 - "test_application_tracker.py"
Cohesion: 0.08
Nodes (33): _add_event(), application_history(), application_method(), backfill_submitted_applications(), _event_exists(), _get_or_create(), record_manual_review(), record_outcome() (+25 more)

### Community 63 - "get_jobs_by_status"
Cohesion: 0.20
Nodes (4): get_jobs_by_status(), _SpyApplicator, test_pipeline_enriches_the_review_queue_and_apply_stays_on_staged(), record_prepare()

### Community 64 - "load_persisted_calibration"
Cohesion: 0.36
Nodes (7): CalibrationMetric, CalibrationRun, get_calibration_metrics(), get_calibration_run(), save_calibration_run(), load_persisted_calibration(), persist_calibration()

### Community 65 - "get_recently_applied_companies"
Cohesion: 0.22
Nodes (7): get_recently_applied_companies(), Capacity, Phase 14 application portfolio, Pipeline, Role-family mix, What counts as a recent application, Who can be allocated

### Community 66 - "init_db"
Cohesion: 0.11
Nodes (15): Testing conventions, get_engine(), init_db(), _is_postgres_url(), _is_sqlite_url(), reset_engine(), database_reachable(), db_ready() (+7 more)

### Community 67 - "db.py"
Cohesion: 0.10
Nodes (18): _company_name(), _dialect_name(), _drop_structured_jd(), _ensure_company_columns(), _ensure_job_columns(), FeedbackSignal, get_application_by_id(), get_feedback_signals() (+10 more)

### Community 68 - "Job"
Cohesion: 0.07
Nodes (27): _load_scored(), _mark_sent(), PrepSummary, render_shortlist(), select_shortlist(), send_prep_pack(), _send_shortlist_document(), shortlist_caption() (+19 more)

### Community 71 - "monitoring.py"
Cohesion: 0.11
Nodes (28): PipelineRun, PipelineStageRun, _cmd_health(), _brief(), format_health_report(), get_health_report(), _recent_failures(), _repeated_failures() (+20 more)

### Community 72 - "shortlist.py"
Cohesion: 0.14
Nodes (16): apply_shortlist(), _close_enough(), _company_key(), _company_ok(), config_hash(), _diversify(), _family(), _identity() (+8 more)

### Community 73 - "linkedin_jobspy.py"
Cohesion: 0.14
Nodes (12): SearchConfig, PlannedSearch, _dataframe_to_postings(), _effective_windows(), _explicit_company_url(), _external_id(), fetch_linkedin_indeed(), _google_search_term() (+4 more)

### Community 75 - "_build_doctor_report"
Cohesion: 0.36
Nodes (4): _build_doctor_report(), _count_jobs(), _print_doctor_report(), _unwrap()

### Community 76 - "Phase 1 discovery architecture"
Cohesion: 0.15
Nodes (12): 40/40/15/5 priority model, Current problem, New architecture, Phase 1 discovery architecture, Provenance, Purpose, Role families, Search buckets (+4 more)

### Community 77 - "vault.py"
Cohesion: 0.15
Nodes (13): CredentialsFile, get_tenant_credentials(), has_saved_session(), load_credentials(), _load_yaml(), reload_credentials(), session_state_path(), TenantCredentials (+5 more)

### Community 78 - "_as_utc"
Cohesion: 0.43
Nodes (5): _as_utc(), _events_in_window(), _matured(), _ordered(), _windows()

### Community 79 - "HttpCompanyIntelProvider"
Cohesion: 0.25
Nodes (4): HttpCompanyIntelProvider, test_http_provider_handles_timeout_and_malformed_pages(), ok(), test_http_provider_keeps_the_caller_source_type()

### Community 80 - "Priority 2.0"
Cohesion: 0.29
Nodes (6): Freshness, dream company, and workflow, Hash, Priority 2.0, Program and domain evidence, Role alignment, Weights

### Community 81 - "builder.py"
Cohesion: 0.16
Nodes (7): _answer_item(), build_job_section(), compile_prep_pdf(), generate_prep_pack(), PrepPackResult, render_markdown(), test_render_markdown_includes_jobs_and_manual()

### Community 82 - "filters.py"
Cohesion: 0.11
Nodes (16): citizenship_restriction(), _clearance_clauses(), clearance_requirement(), FilterResult, has_internship_signal(), _haystack(), _location_ok(), _mandatory_years() (+8 more)

### Community 83 - "Structured JD intelligence"
Cohesion: 0.40
Nodes (4): Cache, Limits, Structured JD intelligence, What is stored

### Community 86 - "job_identity.py"
Cohesion: 0.14
Nodes (12): _find_cross_source_job(), canonicalize_job_url(), _is_tracking_param(), locations_agree(), locations_conflict(), normalize_title(), same_employer(), same_posting_url() (+4 more)

### Community 88 - "profile.py"
Cohesion: 0.12
Nodes (29): Address, Education, Exclusions, Experience, Identity, Preferences, WorkAuthorization, _make_base_pdf() (+21 more)

### Community 89 - "models.py"
Cohesion: 0.31
Nodes (6): hash_fallback(), _family(), _jd(), test_marketing_is_separate_from_product_marketing_and_other(), test_mba_summer_associate_is_an_internship_signal(), test_technology_strategy_is_not_technology_consulting()

### Community 90 - "Phase 8 company intelligence"
Cohesion: 0.29
Nodes (6): Names and reuse, Phase 8 company intelligence, Schema, Sources, What it is, What this phase does not change

### Community 91 - "test_llm_provider.py"
Cohesion: 0.07
Nodes (29): Build order and status, Coding conventions, Commands, Confirmed product decisions, LLM client layer (`scorer/clients.py`), Project, Repository layout, Scoring specifics (Step 3) (+21 more)

### Community 93 - "main.py"
Cohesion: 0.08
Nodes (30): load_profile(), _load_yaml(), reload_profile(), get_role_baseline_by_role(), build_parser(), _cmd_benchmark(), _cmd_build_baseline(), _cmd_poll() (+22 more)

### Community 95 - "test_cover_letter.py"
Cohesion: 0.07
Nodes (22): cap_cover_letter(), _fallback_cover_letter(), generate_cover_letter(), run_one(), contains_banned(), _fallback_outreach(), generate_outreach(), strip_banned_sentences() (+14 more)

### Community 97 - "Phase 16 feedback learning"
Cohesion: 0.33
Nodes (5): Evidence and shrinkage, Phase 16 feedback learning, Rates, Segments, Who is counted

### Community 98 - "get_settings"
Cohesion: 0.07
Nodes (27): get_settings(), _benchmark_tier_one_stage(), _generate_suggestions_stage(), build_embedder(), _cache_path(), clears_threshold(), cosine(), Embedder (+19 more)

### Community 101 - "5. How fit is scored"
Cohesion: 0.22
Nodes (7): 10. File map, 5.1 What the model is, 5.2 The two inputs, 5.3 The rubric, verbatim in meaning, 5.4 What the code does with the score, 5.5 What a number means, 5. How fit is scored

### Community 102 - "Phase 18 — Production reliability and monitoring"
Cohesion: 0.13
Nodes (14): Architecture, Backlog diagnostics, CLI, Configuration, Failure isolation, Health states, Logging, Phase 18 — Production reliability and monitoring (+6 more)

### Community 103 - "Phase 15 application tracker"
Cohesion: 0.33
Nodes (5): Method and time, Phase 15 application tracker, States and outcomes, What this is not, When a row is created

### Community 104 - "CompanyIntelligence"
Cohesion: 0.26
Nodes (8): CompanyIntelligence, _apply_facts(), _by_key(), _clear_facts(), empty_company_context(), get_company_intelligence(), _new_row(), _store_failure()

### Community 105 - "textmatch.py"
Cohesion: 0.13
Nodes (16): _city_state(), company_matches(), company_tokens(), contains_phrase(), is_remote_location(), location_matches(), normalize_text(), truncate_middle() (+8 more)

### Community 106 - "3. Hard filters (before any model)"
Cohesion: 0.18
Nodes (11): 3.10 What a survivor looks like, 3.1 Company blocklist, 3.2 Exclusion keywords, 3.3 Clearance language, 3.4 Staffing agencies, 3.5 Internship gate, 3.6 Seniority filter (separate from the internship gate), 3.7 Years of experience (+3 more)

### Community 107 - "linkedin_people.py"
Cohesion: 0.11
Nodes (17): discover_peers(), _heuristic_parse(), LLMClient, parse_profile(), parse_profile_html(), parse_profile_json(), PeerProfileData, RawProfile (+9 more)

### Community 108 - "2. Where jobs come from"
Cohesion: 0.29
Nodes (7): 2.1 Search terms, 2.2 Sites and the exact JobSpy arguments, 2.3 How each site treats "posted in the last 36 hours", 2.4 What is kept from a JobSpy row, 2.5 Workday, separately from LinkedIn, 2.6 Save and dedupe, 2. Where jobs come from

### Community 109 - "Job Agent"
Cohesion: 0.13
Nodes (14): Application prep packs (LinkedIn / Indeed), Job Agent, Layout, LinkedIn peer benchmarking (optional, off by default), Resumes (Step 4), Run automation (Step 5), Run ingestion (Step 2), Run review bot (Step 6) (+6 more)

### Community 110 - "test_priority_v2.py"
Cohesion: 0.10
Nodes (23): Dimensions, Not in this phase, Output, Phase 6 candidate fit, When the model is not called, Cache and storage, Education, graduation, experience, location, dates, Phase 9 visa and eligibility (+15 more)

### Community 111 - "Phase 12 priority ranking"
Cohesion: 0.50
Nodes (3): Components, Phase 12 priority ranking, Version

### Community 112 - "classify_role"
Cohesion: 0.17
Nodes (15): classify_role(), _apply_role_classification(), _jd(), test_cache_recomputes_only_when_hash_or_version_changes(), test_collaboration_responsibility_is_not_a_secondary_family(), test_hybrid_roles_keep_a_second_family(), test_interaction_evidence_from_the_model_is_rejected(), test_interaction_is_not_a_second_family() (+7 more)

### Community 114 - "Phase 0 baseline"
Cohesion: 0.22
Nodes (8): Candidate baseline, Discovery baseline, Local versus production, Phase 0 baseline, Production baseline, Scoring baseline, Sponsorship behavior locked by tests, Tests

### Community 115 - "Company intelligence 2.0"
Cohesion: 0.33
Nodes (5): Company intelligence 2.0, Company versus job, Sources and refresh, What it does not store, What it stores

### Community 116 - "suggest.py"
Cohesion: 0.12
Nodes (15): apply_decided_suggestions(), decide_suggestion(), _format_card(), send_pending_suggestions(), _suggestion_keyboard(), SuggestSummary, get_pending_suggestions_for_job(), get_skill_suggestion_by_id() (+7 more)

### Community 118 - "Phase 4 JD ingestion"
Cohesion: 0.14
Nodes (10): How to read it, Limits, Phase 3 discovery coverage, What a number means, Flow, Hash and upsert, Limits, Normalization (+2 more)

### Community 119 - "role_classify.py"
Cohesion: 0.15
Nodes (18): _clause_containing(), _clip_items(), _deterministic(), _is_interaction(), _item_text(), _ModelLabel, _parse_model(), _phrase_hits() (+10 more)

### Community 120 - "sort_by_priority"
Cohesion: 0.29
Nodes (6): Configuration, Phase 13 shortlist, Pipeline, Selection, sort_by_priority(), posted()

### Community 121 - "targets.py"
Cohesion: 0.08
Nodes (16): load_targets(), _load_yaml(), parse_workday_url(), reload_targets(), Targets, WorkdayParts, test_full_plan_and_capacity_limit_change_only_what_was_planned(), test_full_plan_keeps_sources_separate_from_families() (+8 more)

### Community 122 - "Multi-dimensional role classification"
Cohesion: 0.29
Nodes (6): Cache, Contract, Function versus interaction, Multi-dimensional role classification, Non-goals, What the classifier reads

### Community 123 - "normalize_company_name"
Cohesion: 0.29
Nodes (6): canonical_company_name(), normalize_company_name(), _without_trailing_suffix(), test_legal_suffixes_do_not_collapse_distinct_names(), test_normalization_is_deterministic(), test_version_and_normalization_stay_explicit()

### Community 125 - "9. Pain points we have actually hit or spelled out"
Cohesion: 0.33
Nodes (6): 9.1 Discovery, 9.2 Filters, 9.3 Scoring, 9.4 What you receive, 9.5 Operations, 9. Pain points we have actually hit or spelled out

### Community 127 - "8. The weight discussion (not built)"
Cohesion: 0.33
Nodes (6): 8.1 What you asked for, 8.2 Decisions you agreed with, 8.3 A weight table we used as a sketch, 8.4 What we said the rubric should do for career-switch roles, 8.5 How that would sit on the current pipeline, 8. The weight discussion (not built)

### Community 129 - "test_role_weights.py"
Cohesion: 0.09
Nodes (27): Canonical portfolio, Configuration, Four different questions, Phase 7 role-family weighting, Unknown classification, What is stored, What this phase does not do, Where the family comes from (+19 more)

### Community 131 - "How jobs are found, filtered, scored, and sent"
Cohesion: 0.25
Nodes (7): 1. What a run is, 4.1 Pre-score rank (`prerank_score`), 4.2 Embedding gate (this does drop jobs), 4.3 Fit-model cap, 4. How results are prioritised today, 7. Statuses, in one pass, How jobs are found, filtered, scored, and sent

### Community 134 - "6. What is sent to you"
Cohesion: 0.40
Nodes (5): 6.1 Who is eligible, 6.2 The shortlist rule, 6.3 Each line, 6.4 If brief mode is turned off, 6. What is sent to you

### Community 136 - "LLMClient"
Cohesion: 0.08
Nodes (9): LLMClient, _attach_priority(), _JobOutcome, _priority_evidence(), Scorer, ScoreSummary, _status_for_tier(), Evaluation (+1 more)

## Knowledge Gaps
- **168 isolated node(s):** `job-agent`, `ScrapeSummary`, `_Sites`, `_FakeAio`, `Project` (+163 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 1044 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **10 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Job` connect `Job` to `TelegramClient`, `structured_jd.py`, `test_structured_jd.py`, `test_eligibility.py`, `feedback.py`, `test_role_weights.py`, `get_job_by_id`, `test_fit.py`, `LLMClient`, `test_calibration.py`, `ingest.py`, `test_feedback.py`, `test_application_portfolio.py`, `prerank.py`, `eligibility.py`, `alerts.py`, `test_monitoring.py`, `test_resume.py`, `migrate_to_neon.py`, `AnswerResolver`, `review.py`, `test_doctor.py`, `diff.py`, `test_company_intelligence.py`, `runner.py`, `session_scope`, `answers.py`, `workday.py`, `compiler.py`, `typing`, `benchmark/engine.py`, `WorkdaySubmitter`, `application_portfolio.py`, `calculate_priority`, `test_phase13_shortlist.py`, `priority.py`, `test_prep_builder.py`, `company_intelligence.py`, `test_vector_gate.py`, `test_application_tracker.py`, `get_jobs_by_status`, `db.py`, `monitoring.py`, `shortlist.py`, `_build_doctor_report`, `builder.py`, `filters.py`, `job_identity.py`, `profile.py`, `models.py`, `main.py`, `test_cover_letter.py`, `get_settings`, `test_priority_v2.py`, `classify_role`, `suggest.py`, `sort_by_priority`?**
  _High betweenness centrality (0.136) - this node is a cross-community bridge._
- **Why does `get_settings()` connect `get_settings` to `TelegramClient`, `test_eligibility.py`, `clients.py`, `test_fit.py`, `LLMClient`, `Profile`, `textclean.py`, `test_application_portfolio.py`, `test_monitoring.py`, `pipeline.py`, `Any`, `test_resume.py`, `Settings`, `migrate_to_neon.py`, `AnswerResolver`, `Any`, `diff.py`, `scheduler.py`, `human_delay`, `runner.py`, `auto_discover_peers`, `session_scope`, `answers.py`, `workday.py`, `compiler.py`, `settings.py`, `typing`, `benchmark/engine.py`, `application_portfolio.py`, `test_phase13_shortlist.py`, `diagnostics.py`, `test_company_intelligence_v2.py`, `test_vector_gate.py`, `init_db`, `db.py`, `Job`, `monitoring.py`, `_build_doctor_report`, `vault.py`, `builder.py`, `filters.py`, `profile.py`, `models.py`, `test_llm_provider.py`, `main.py`, `test_cover_letter.py`, `textmatch.py`, `linkedin_people.py`, `suggest.py`, `targets.py`?**
  _High betweenness centrality (0.113) - this node is a cross-community bridge._
- **Why does `Profile` connect `Profile` to `.total_years_experience`, `test_eligibility.py`, `get_job_by_id`, `test_fit.py`, `LLMClient`, `ingest.py`, `prerank.py`, `eligibility.py`, `test_resume.py`, `AnswerResolver`, `diff.py`, `runner.py`, `session_scope`, `answers.py`, `workday.py`, `compiler.py`, `typing`, `RawPosting`, `benchmark/engine.py`, `calculate_priority`, `priority.py`, `test_prep_builder.py`, `test_vector_gate.py`, `Job`, `linkedin_jobspy.py`, `builder.py`, `filters.py`, `profile.py`, `main.py`, `test_cover_letter.py`, `get_settings`, `5. How fit is scored`, `test_priority_v2.py`, `suggest.py`, `targets.py`?**
  _High betweenness centrality (0.092) - this node is a cross-community bridge._
- **Are the 157 inferred relationships involving `Job` (e.g. with `Data model (core/db.py)` and `AnswerResolver`) actually correct?**
  _`Job` has 157 INFERRED edges - model-reasoned connections that need verification._
- **Are the 204 inferred relationships involving `Profile` (e.g. with `AnswerResolver` and `_latest_education()`) actually correct?**
  _`Profile` has 204 INFERRED edges - model-reasoned connections that need verification._
- **Are the 164 inferred relationships involving `Status` (e.g. with `Data model (core/db.py)` and `ApplyRunner`) actually correct?**
  _`Status` has 164 INFERRED edges - model-reasoned connections that need verification._
- **Are the 131 inferred relationships involving `Source` (e.g. with `Data model (core/db.py)` and `_eligible()`) actually correct?**
  _`Source` has 131 INFERRED edges - model-reasoned connections that need verification._