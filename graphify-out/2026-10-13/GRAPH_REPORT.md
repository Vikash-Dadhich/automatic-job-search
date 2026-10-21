# Graph Report - Automatic job search  (2026-10-05)

## Corpus Check
- 213 files · ~180,100 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 12 file(s) not represented in the graph (top: (none) 8, .typ 2, .example 1)

## Summary
- 3728 nodes · 12858 edges · 142 communities (123 shown, 19 thin omitted)
- Extraction: 90% EXTRACTED · 10% INFERRED · 0% AMBIGUOUS · INFERRED: 1341 edges (avg confidence: 0.94)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `a93a9e4f`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- telegram.py
- structured_jd.py
- test_vector_gate.py
- test_phase0_baseline.py
- test_outcomes.py
- clients.py
- test_career_intelligence.py
- json
- discovery.py
- test_feedback.py
- evaluate
- workday_rest.py
- pathlib
- models.py
- discovery_recall.py
- AnswerResolver
- eligibility.py
- ingest.py
- selector.py
- test_structured_jd.py
- pipeline.py
- Any
- classify_role
- Application
- test_monitoring.py
- diff.py
- test_company_intelligence.py
- vault.py
- runner.py
- dataclasses
- test_ingest_resilience.py
- feedback.py
- test_calibration.py
- company_intelligence.py
- test_eligibility.py
- parse_workday_url
- Remaining Manual Setup
- benchmark/engine.py
- init_db
- test_phase13_shortlist.py
- test_company_intelligence_v2.py
- profile.py
- workday.py
- compiler.py
- vector_recovery.py
- typing
- answers.py
- HttpCompanyIntelProvider
- application_deadline.py
- Settings
- test_application_portfolio.py
- test_priority.py
- Phase 5 role classification
- test_application_deadline.py
- test_discovery.py
- priority.py
- main.py
- test_vector_recovery.py
- Benchmark — Product Manager @ T-Mobile
- monitoring.py
- SearchBucket
- FeedbackRun
- tracker.py
- bot/__init__.py
- normalize_company_name
- datetime
- discovery_experiment.py
- build_llm_client
- prep.py
- job-agent
- Profile
- outreach.py
- linkedin_jobspy.py
- phase10-false-negative-protection.md
- get_settings
- Phase 1 discovery architecture
- compute_tier
- test_webhook.py
- _posting
- Priority 2.0
- WorkdaySubmitter
- OpenAIEmbedder
- test_application_tracker.py
- CompanyLookupResult
- Discovery recall benchmark
- scorer/__init__.py
- Phase 9 visa and eligibility
- Career Intelligence
- 5. How fit is scored
- Phase 8 company intelligence
- pytest
- correction1-recruiting-universe.md
- test_scorer.py
- LLMClient
- filters.py
- extract_company_signals
- Phase 16 feedback learning
- scorer/engine.py
- Job
- reset_engine
- calibration.py
- get_job_by_id
- Phase 15 application tracker
- run_pipeline
- extract_company_facts
- 3. Hard filters (before any model)
- linkedin_people.py
- TelegramClient
- Job Agent
- calculate_priority
- Phase 12 priority ranking
- Structured JD intelligence
- builder.py
- redact_error
- Company intelligence 2.0
- test_false_negative.py
- phase17-calibration-benchmark.md
- RawPosting
- SearchConfig
- vector-recovery.md
- CompanyIntelProvider
- Multi-dimensional role classification
- db.py
- test_cover_letter.py
- asyncio
- Phase 6 candidate fit
- test_role_weights.py
- Any
- test_doctor.py
- How jobs are found, filtered, scored, and sent
- 2. Where jobs come from
- 8. The weight discussion (not built)
- 9. Pain points we have actually hit or spelled out
- 6. What is sent to you
- Phase 7 role-family weighting
- test_workday_locators.py

## God Nodes (most connected - your core abstractions)
1. `Job` - 374 edges
2. `Profile` - 327 edges
3. `session_scope()` - 317 edges
4. `Status` - 244 edges
5. `Source` - 212 edges
6. `get_settings()` - 168 edges
7. `get_job_by_id()` - 161 edges
8. `upsert_job()` - 140 edges
9. `TelegramClient` - 92 edges
10. `init_db()` - 87 edges

## Surprising Connections (you probably didn't know these)
- `What the profile contributes` --references--> `Profile`  [INFERRED]
  docs/phase9-visa-eligibility.md → config/profile.py
- `9.1 Discovery` --references--> `test_internship_only_rejects_international_substring()`  [INFERRED]
  docs/how-jobs-are-found-scored-and-sent.md → tests/test_filters.py
- `Run review bot (Step 6)` --references--> `send_pending_alerts()`  [INFERRED]
  README.md → bot/alerts.py
- `Output` --references--> `score()`  [INFERRED]
  docs/phase6-candidate-fit.md → tests/test_priority_v2.py
- `Four different questions` --references--> `score()`  [INFERRED]
  docs/phase7-role-family-weighting.md → tests/test_priority_v2.py

## Import Cycles
- None detected.

## Communities (142 total, 19 thin omitted)

### Community 0 - "telegram.py"
Cohesion: 0.08
Nodes (17): _decision_caption(), handle_message(), _handle_outcome_callback(), _handle_suggest_callback(), _safe_answer(), decide_suggestion(), decode_suggest_callback(), encode_suggest_callback() (+9 more)

### Community 1 - "structured_jd.py"
Cohesion: 0.13
Nodes (37): _authorization(), AuthorizationEvidence, _availability(), _clause_at(), _clauses(), _clip(), _degree_state(), _domain() (+29 more)

### Community 2 - "test_vector_gate.py"
Cohesion: 0.19
Nodes (20): job_embed_text(), profile_embed_text(), profile_hash(), score_pending(), FakeClient, FakeEmbedder, _map(), test_budget_skips_tail_after_a_reject() (+12 more)

### Community 3 - "test_phase0_baseline.py"
Cohesion: 0.16
Nodes (14): _enable_internship_only(), _posting(), test_experience_span_is_about_five_years_and_not_summed(), test_friendly_sponsorship_stays_eligible(), test_hostile_sponsorship_is_rejected(), test_internship_only_code_default_is_false(), test_internship_only_drops_non_internship_titles(), test_internship_only_keeps_internship_titles() (+6 more)

### Community 4 - "test_outcomes.py"
Cohesion: 0.09
Nodes (26): build_outcome_keyboard(), button(), outcome_label(), outcome_message_text(), OutcomePromptSummary, send_outcome_prompt(), send_pending_outcome_prompts(), decode_outcome_callback() (+18 more)

### Community 5 - "clients.py"
Cohesion: 0.10
Nodes (18): _backoff_delay(), call_with_resilience(), is_permanent_account_error(), is_transient(), LLMBillingError, LLMError, _status_code(), suggested_delay() (+10 more)

### Community 6 - "test_career_intelligence.py"
Cohesion: 0.08
Nodes (51): CareerIntelligence, _apply_reading(), assess_career(), attach_career_intelligence(), career_input_hash(), CareerReading, _clause(), _clip() (+43 more)

### Community 7 - "json"
Cohesion: 0.06
Nodes (44): effective_baseline(), effective_config_hash(), fingerprint_profile(), profile_hash(), public_config(), write_effective_baseline(), build_fit_system_blocks(), build_fit_user() (+36 more)

### Community 8 - "discovery.py"
Cohesion: 0.11
Nodes (19): load_targets(), New architecture, build_discovery_plan(), DiscoveryConfig, _enabled_queries(), enabled_query_texts(), load_discovery(), _load_yaml() (+11 more)

### Community 9 - "test_feedback.py"
Cohesion: 0.24
Nodes (12): ApplicationEvent, get_application_events(), list_events_for_applications(), shrink_rate(), _case(), _config(), _signal(), test_bands_families_and_sparse_subfamily() (+4 more)

### Community 10 - "evaluate"
Cohesion: 0.15
Nodes (25): evaluate(), sponsorship_signal(), test_sponsorship_and_false_friends(), _posting(), test_clearance_regex_pattern(), test_exclude_clearance_keyword(), test_exclude_high_yoe_requirement(), test_exclude_off_target_location() (+17 more)

### Community 11 - "workday_rest.py"
Cohesion: 0.07
Nodes (24): WorkdayParts, WorkdayTenant, _as_text(), _company_name(), fetch_all_workday(), _one(), _fetch_detail(), _fetch_listing_page() (+16 more)

### Community 12 - "pathlib"
Cohesion: 0.08
Nodes (10): Testing conventions, load_profile(), _load_yaml(), reload_profile(), reload_targets(), db_ready(), _disable_apply_pacing(), _disable_vector_gate() (+2 more)

### Community 13 - "models.py"
Cohesion: 0.09
Nodes (26): Flow, Hash and upsert, Limits, Normalization, Phase 4 JD ingestion, hash_fallback(), content_hash(), _drop_boilerplate_lines() (+18 more)

### Community 14 - "discovery_recall.py"
Cohesion: 0.05
Nodes (57): _find_cross_source_job(), canonicalize_job_url(), _is_tracking_param(), locations_agree(), locations_conflict(), normalize_title(), same_employer(), same_posting_url() (+49 more)

### Community 15 - "AnswerResolver"
Cohesion: 0.13
Nodes (10): AnswerResolver, one(), AnswerSource, WorkdayApplicator, FakeAnswerClient, test_cover_letter_field_uses_stored_text(), test_resolver_banned_word_retry(), test_resolver_blank_for_unknown_closed() (+2 more)

### Community 16 - "eligibility.py"
Cohesion: 0.16
Nodes (25): _ask_model(), _citizenship(), _clearance(), _current_student(), _dates(), _decision_from_job(), _dim(), DimensionResult (+17 more)

### Community 17 - "ingest.py"
Cohesion: 0.05
Nodes (48): _safe_close_stage(), build_coverage_report(), add_planned(), group_for(), CoverageReport, discovery_evidence(), fail_unrecorded(), GroupMetrics (+40 more)

### Community 18 - "selector.py"
Cohesion: 0.16
Nodes (11): build_resume_data(), extract_job_terms(), _grounded_summary(), RankedBullet, reorder_skills(), score_bullet(), select_bullets(), SelectedExperience (+3 more)

### Community 19 - "test_structured_jd.py"
Cohesion: 0.13
Nodes (19): StructuredJobDescription, attach_structured_jd(), extract_structured_jd(), get_structured_jd(), structured_jd_is_current(), _areas(), _job(), test_changed_upsert_drops_the_old_reading() (+11 more)

### Community 20 - "pipeline.py"
Cohesion: 0.12
Nodes (16): _allocated_ids(), _benchmark_tier_one_stage(), _generate_suggestions_stage(), _note_skipped(), PipelineSummary, _portfolio_stage(), _prepare_shortlisted_resumes(), _run_opened_pipeline() (+8 more)

### Community 22 - "classify_role"
Cohesion: 0.06
Nodes (47): classification_is_current(), classify_role(), _clause_containing(), _clip_items(), _deterministic(), _is_interaction(), _item_text(), _ModelLabel (+39 more)

### Community 23 - "Application"
Cohesion: 0.18
Nodes (11): Application, Benchmark, CalibrationMetric, CalibrationRun, get_application_by_id(), get_calibration_metrics(), get_calibration_run(), save_calibration_run() (+3 more)

### Community 24 - "test_monitoring.py"
Cohesion: 0.17
Nodes (18): close_pipeline_run(), interrupt_stale_runs(), list_pipeline_runs(), open_pipeline_run(), stage_counters(), _safe_open_run(), _job(), test_a_new_run_does_not_duplicate_applications() (+10 more)

### Community 25 - "diff.py"
Cohesion: 0.08
Nodes (35): apply_decided_suggestions(), _format_card(), send_pending_suggestions(), _suggestion_keyboard(), SuggestSummary, get_pending_suggestions_for_job(), get_role_baseline_by_id(), get_role_baseline_by_role() (+27 more)

### Community 26 - "test_company_intelligence.py"
Cohesion: 0.23
Nodes (16): attach_company_intelligence(), is_dream_company(), FakeProvider, _job(), _posting(), test_ambiguous_names_stay_separate(), test_company_facts_do_not_change_scoring_signals(), test_company_sources_accumulate_and_a_failed_refresh_keeps_them() (+8 more)

### Community 27 - "vault.py"
Cohesion: 0.15
Nodes (12): CredentialsFile, get_tenant_credentials(), has_saved_session(), load_credentials(), _load_yaml(), reload_credentials(), TenantCredentials, test_get_tenant_credentials_placeholder_skip() (+4 more)

### Community 28 - "runner.py"
Cohesion: 0.05
Nodes (61): acquire(), AcquireResult, _clamp_multiplier(), _clock(), end_of_local_day(), gap_seconds(), is_pace_blocker(), note_pace_block() (+53 more)

### Community 29 - "dataclasses"
Cohesion: 0.12
Nodes (17): _FakeSummary, test_pipeline_order_and_aggregation(), fake_alerts(), fake_apply(), fake_ingestion(), fake_outcomes(), fake_prep(), fake_resume() (+9 more)

### Community 30 - "test_ingest_resilience.py"
Cohesion: 0.06
Nodes (38): run_ingestion(), _accept(), _run_jobspy(), _run_workday(), kill_process_group(), LineWorker, QueryTimeoutError, _read_json_line() (+30 more)

### Community 31 - "feedback.py"
Cohesion: 0.15
Nodes (22): list_jobs_by_ids(), list_submitted_applications(), _adjustment(), _band(), build_feedback(), _case_from_rows(), _counts(), FeedbackCase (+14 more)

### Community 32 - "test_calibration.py"
Cohesion: 0.29
Nodes (15): brier_score(), load_feedback_config(), _calibration(), _case(), _feedback(), _rows(), test_brier_score_is_mean_squared_error(), test_calibration_defaults_stay_off_the_production_path() (+7 more)

### Community 33 - "company_intelligence.py"
Cohesion: 0.15
Nodes (19): CompanyIntelligence, _accumulate_sources(), _apply_context(), _apply_facts(), _by_key(), _clear_facts(), _confidence_for(), _context_from() (+11 more)

### Community 34 - "test_eligibility.py"
Cohesion: 0.15
Nodes (20): assign_eligibility(), attach_eligibility(), eligibility_column_types(), eligibility_is_current(), EligibilityDecision, evaluate_eligibility(), profile_eligibility_hash(), _job() (+12 more)

### Community 35 - "parse_workday_url"
Cohesion: 0.11
Nodes (21): _eligible(), parse_workday_url(), ApplyKind, classify_apply_url(), _host(), is_automateable_apply_url(), is_workday_url(), workday_parts() (+13 more)

### Community 36 - "Remaining Manual Setup"
Cohesion: 0.08
Nodes (24): 2a. Find a Workday URL, 2b. Edit `config/targets.yaml`, 3a. Run the save-session helper, 3b. What you do in the browser, 4a. Discover jobs (LinkedIn / Indeed + any real Workday tenants), 4b. Score with Gemini, 4c. Attach your base resume to staged jobs, 4d. Send LinkedIn/Indeed application prep pack (Telegram) (+16 more)

### Community 37 - "benchmark/engine.py"
Cohesion: 0.15
Nodes (15): BenchmarkReport, BenchmarkSummary, build_benchmark(), _derive_seniority(), DimensionScore, _education_rank(), _median(), _norm() (+7 more)

### Community 38 - "init_db"
Cohesion: 0.19
Nodes (13): init_db(), PipelineRun, _brief(), format_health_report(), get_health_report(), _recent_failures(), _repeated_failures(), _run_view() (+5 more)

### Community 39 - "test_phase13_shortlist.py"
Cohesion: 0.09
Nodes (33): get_jobs_by_status(), apply_shortlist(), _close_enough(), _company_key(), _company_ok(), config_hash(), _diversify(), _family() (+25 more)

### Community 40 - "test_company_intelligence_v2.py"
Cohesion: 0.31
Nodes (5): refresh_company_intelligence(), _one(), _signals(), test_changed_page_replaces_that_source_and_keeps_another(), test_profile_signals_persist_with_evidence()

### Community 41 - "profile.py"
Cohesion: 0.12
Nodes (28): Address, Education, Exclusions, Experience, Identity, Preferences, WorkAuthorization, _profile() (+20 more)

### Community 42 - "workday.py"
Cohesion: 0.11
Nodes (17): action_delay_bounds(), human_delay(), type_like_human(), typing_delay_bounds(), click_by_role(), click_next(), _collect_labeled_fields(), detect_blocker() (+9 more)

### Community 43 - "compiler.py"
Cohesion: 0.08
Nodes (31): apply_fit_caps(), _baseline_pdf_for_job(), clean_name(), compile_for_job(), compile_pending(), compile_resume(), compile_resume_data(), FitReport (+23 more)

### Community 44 - "vector_recovery.py"
Cohesion: 0.18
Nodes (17): _compiled(), _confidence(), config_hash(), evaluate_recovery(), _family_group(), load_recovery_config(), _mba_program(), _names() (+9 more)

### Community 45 - "typing"
Cohesion: 0.06
Nodes (30): get_jobs_for_role(), build_baseline_resume_data(), build_role_baseline(), _normalize(), _slugify_role(), _synthetic_job_for_role(), aggregate_role_skills(), AggregatedSkill (+22 more)

### Community 46 - "answers.py"
Cohesion: 0.11
Nodes (16): answers_to_payload(), _discovery_channel(), is_open_ended(), _latest_education(), _matches(), needs_human_review(), _norm(), resolve_deterministic() (+8 more)

### Community 47 - "HttpCompanyIntelProvider"
Cohesion: 0.25
Nodes (4): HttpCompanyIntelProvider, test_http_provider_handles_timeout_and_malformed_pages(), ok(), test_http_provider_keeps_the_caller_source_type()

### Community 48 - "application_deadline.py"
Cohesion: 0.16
Nodes (12): ApplicationDeadline, _clip(), empty_application_deadline(), _excluded(), extract_application_deadline(), _from_match(), _named(), _parse_date() (+4 more)

### Community 50 - "test_application_portfolio.py"
Cohesion: 0.05
Nodes (63): get_recently_applied_companies(), Configuration, Phase 13 shortlist, Pipeline, Selection, Capacity, Decisions, Phase 14 application portfolio (+55 more)

### Community 51 - "test_priority.py"
Cohesion: 0.16
Nodes (18): apply_priority(), _half_up_ratio(), priority_is_current(), PriorityDecision, role_family_component(), _job(), test_dream_company_is_only_a_configured_boost(), test_eligibility_unknown_is_not_ineligible() (+10 more)

### Community 52 - "Phase 5 role classification"
Cohesion: 0.29
Nodes (6): Inputs, Limits, Output, Phase 5 role classification, Taxonomy, When it runs again

### Community 53 - "test_application_deadline.py"
Cohesion: 0.18
Nodes (16): _pad(), _read(), test_deadline_failure_does_not_drop_the_rest_of_the_reading(), test_empty_and_unusable_descriptions(), test_internship_and_graduation_dates_are_not_deadlines(), test_interview_deadline_is_not_an_application_deadline(), test_invalid_calendar_date_is_ambiguous(), test_markdown_split_year_is_kept() (+8 more)

### Community 54 - "test_discovery.py"
Cohesion: 0.23
Nodes (10): allocate_units(), AllocItem, _family_spillover(), _largest_remainder(), _items(), _Sites, test_allocation_is_deterministic(), test_allocation_never_exceeds_available_queries() (+2 more)

### Community 55 - "priority.py"
Cohesion: 0.13
Nodes (26): _as_utc(), _combine(), company_domain_component(), _company_signals(), _components(), dream_company_component(), eligibility_component(), _explicit_sections() (+18 more)

### Community 56 - "main.py"
Cohesion: 0.08
Nodes (29): _build_doctor_report(), build_parser(), _cmd_benchmark(), _cmd_build_baseline(), _cmd_health(), _cmd_poll(), _cmd_prep_pack(), _cmd_run_once() (+21 more)

### Community 57 - "test_vector_recovery.py"
Cohesion: 0.29
Nodes (27): _enable(), _seed(), _assert_no_profile_text(), _doc(), _exclude_company(), _score(), _stamp(), _store_doc() (+19 more)

### Community 58 - "Benchmark — Product Manager @ T-Mobile"
Cohesion: 0.33
Nodes (5): Benchmark — Product Manager @ T-Mobile, Dimensions, Gaps, Recommendations, Strengths

### Community 59 - "monitoring.py"
Cohesion: 0.18
Nodes (19): get_engine(), _is_postgres_url(), PipelineStageRun, close_stage_run(), count_stale_jobs(), list_stage_runs(), load_monitoring_config(), _moment() (+11 more)

### Community 60 - "SearchBucket"
Cohesion: 0.22
Nodes (8): DiscoverySource, RoleFamily, SearchBucket, _catalog(), _Targets, test_enabled_weights_must_sum_to_one(), test_family_shortage_reports_genuine_spillover(), test_sufficient_capacity_has_no_spillover()

### Community 61 - "FeedbackRun"
Cohesion: 0.26
Nodes (9): FeedbackRun, FeedbackSignal, get_feedback_run(), get_feedback_signals(), get_latest_feedback_run(), save_feedback_run(), latest_feedback_run(), load_persisted_feedback() (+1 more)

### Community 62 - "tracker.py"
Cohesion: 0.20
Nodes (15): _add_event(), application_method(), backfill_submitted_applications(), _event_exists(), _get_or_create(), record_manual_review(), record_outcome(), record_prefill() (+7 more)

### Community 63 - "bot/__init__.py"
Cohesion: 0.11
Nodes (16): build_keyboard(), build_review_caption(), format_answers_message(), format_cover_letter_message(), ReviewSummary, _send_one(), send_pending_reviews(), decode_callback() (+8 more)

### Community 64 - "normalize_company_name"
Cohesion: 0.29
Nodes (6): canonical_company_name(), normalize_company_name(), _without_trailing_suffix(), test_legal_suffixes_do_not_collapse_distinct_names(), test_normalization_is_deterministic(), test_version_and_normalization_stay_explicit()

### Community 65 - "datetime"
Cohesion: 0.14
Nodes (12): _absolute_sqlite_url(), normalize_database_url(), _cell(), _copy_table(), _counts(), main(), _reset_sequences(), _row() (+4 more)

### Community 66 - "discovery_experiment.py"
Cohesion: 0.07
Nodes (56): Targets, account_executions(), _baseline_slot_reason(), _baseline_slots(), build_schedule(), _classify_incremental(), compare_arms(), _execute() (+48 more)

### Community 67 - "build_llm_client"
Cohesion: 0.10
Nodes (13): Build order and status, Coding conventions, Commands, Confirmed product decisions, LLM client layer (`scorer/clients.py`), Project, Repository layout, Scoring specifics (Step 3) (+5 more)

### Community 68 - "prep.py"
Cohesion: 0.09
Nodes (31): _dedupe(), _fit_lines(), _load_canonical_shortlist(), _mark_sent(), _notify_empty(), PrepSummary, render_job_card(), render_shortlist() (+23 more)

### Community 71 - "Profile"
Cohesion: 0.20
Nodes (13): Profile, prerank_jobs(), prerank_score(), _source_weight(), _job(), test_dream_company_boost(), test_intern_title_outranks_fulltime(), test_new_source_scored_without_error() (+5 more)

### Community 72 - "outreach.py"
Cohesion: 0.27
Nodes (5): contains_banned(), _fallback_outreach(), generate_outreach(), strip_banned_sentences(), test_generate_outreach_retries_on_banned()

### Community 73 - "linkedin_jobspy.py"
Cohesion: 0.07
Nodes (20): _dataframe_to_postings(), _effective_windows(), _explicit_company_url(), _external_id(), fetch_linkedin_indeed(), run_query(), _google_search_term(), _jobspy_observations() (+12 more)

### Community 75 - "get_settings"
Cohesion: 0.14
Nodes (12): What still needs the user (before live runs), launch_context(), _new_context(), new_page(), save_storage_state(), save_session(), session_state_path(), get_settings() (+4 more)

### Community 76 - "Phase 1 discovery architecture"
Cohesion: 0.12
Nodes (15): 40/40/15/5 priority model, Current problem, Phase 1 discovery architecture, Provenance, Purpose, Role families, Search allocation, Search buckets (+7 more)

### Community 77 - "compute_tier"
Cohesion: 0.14
Nodes (12): Candidate baseline, Discovery baseline, Local versus production, Phase 0 baseline, Production baseline, Scoring baseline, Sponsorship behavior locked by tests, Tests (+4 more)

### Community 78 - "test_webhook.py"
Cohesion: 0.26
Nodes (5): client(), test_health(), test_webhook_ignored_without_callback(), test_webhook_rejects_bad_secret(), test_webhook_routes_callback()

### Community 79 - "_posting"
Cohesion: 0.20
Nodes (5): _posting(), ScoreOnlyClient, test_company_blocklist_does_not_match_lookalikes(), test_yoe_ceiling_follows_profile(), test_yoe_keeps_job_when_a_lower_band_is_reachable()

### Community 80 - "Priority 2.0"
Cohesion: 0.29
Nodes (6): Freshness, dream company, and workflow, Hash, Priority 2.0, Program and domain evidence, Role alignment, Weights

### Community 81 - "WorkdaySubmitter"
Cohesion: 0.20
Nodes (7): SessionMissingError, WorkdaySubmitter, test_submit_generic_exception(), test_submit_missing_url(), test_submit_session_missing(), boom_launch(), test_submit_unparseable_without_tenant()

### Community 83 - "test_application_tracker.py"
Cohesion: 0.23
Nodes (14): application_history(), SubmitResult, get_application_for_job(), _count(), _job(), _Prefill, _Submitter, _tap() (+6 more)

### Community 84 - "CompanyLookupResult"
Cohesion: 0.23
Nodes (6): CompanyLookupResult, CompanySourceDocument, _reliable_source_url(), trustworthy_company_source(), test_company_url_is_not_guessed_or_taken_from_the_job_page(), _Provider

### Community 85 - "Discovery recall benchmark"
Cohesion: 0.10
Nodes (18): Discovery recall benchmark, Label corrections on 2026-10-04, Limits, Matching, Reproduce, What is checked in, Discovery run observability, Query timeout and incremental save (+10 more)

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
Nodes (18): _FakeAio, _FakeAsyncModels, _FakeCandidate, _FakeGenaiClient, _FakeGenerateResponse, test_active_models_ignore_anthropic_names(), test_active_models_ignore_other_providers(), test_build_llm_client_always_openai() (+10 more)

### Community 93 - "test_scorer.py"
Cohesion: 0.09
Nodes (20): approx_tokens(), cache_block(), compact_json_dumps(), minify_job(), _extract_json_object(), parse_score(), build_outreach_user(), build_scoring_system_blocks() (+12 more)

### Community 95 - "filters.py"
Cohesion: 0.11
Nodes (16): _clearance_clauses(), evaluate_job(), FilterResult, has_internship_signal(), _haystack(), location_acceptable(), _location_ok(), _mandatory_years() (+8 more)

### Community 96 - "extract_company_signals"
Cohesion: 0.38
Nodes (5): _compact(), extract_company_signals(), _signal(), _snippet(), test_signals_are_explicit_and_multi_valued()

### Community 97 - "Phase 16 feedback learning"
Cohesion: 0.33
Nodes (5): Evidence and shrinkage, Phase 16 feedback learning, Rates, Segments, Who is counted

### Community 98 - "scorer/engine.py"
Cohesion: 0.06
Nodes (35): Tech stack, build_embedder(), _cache_path(), clears_threshold(), cosine(), Embedder, jd_vector(), load_profile_embedding() (+27 more)

### Community 99 - "Job"
Cohesion: 0.08
Nodes (63): Data model (core/db.py), Status lifecycle, _reload_job(), _assign_canonical_url(), get_job_by_source_id(), get_unsent_prep_pack_jobs(), Job, _role_classification_current() (+55 more)

### Community 101 - "calibration.py"
Cohesion: 0.13
Nodes (32): _as_utc(), _append_buckets(), _append_short_target(), _append_slice(), _append_target_metrics(), _append_topk(), _bucket_name(), build_calibration() (+24 more)

### Community 102 - "get_job_by_id"
Cohesion: 0.31
Nodes (14): _ensure_tenant(), handle_callback(), ReviewAction, get_job_by_id(), _callback_update(), FakeSubmitter, _seed_pending(), test_already_decided() (+6 more)

### Community 103 - "Phase 15 application tracker"
Cohesion: 0.33
Nodes (5): Method and time, Phase 15 application tracker, States and outcomes, What this is not, When a row is created

### Community 104 - "run_pipeline"
Cohesion: 0.07
Nodes (24): Architecture, Backlog diagnostics, CLI, Configuration, Failure isolation, Health states, Logging, Phase 18 — Production reliability and monitoring (+16 more)

### Community 105 - "extract_company_facts"
Cohesion: 0.29
Nodes (5): extract_company_facts(), merge_company_facts(), test_extractor_keeps_unstated_facts_null(), test_merge_company_facts_keeps_omitted_fields(), test_prestige_language_is_not_a_fact()

### Community 106 - "3. Hard filters (before any model)"
Cohesion: 0.18
Nodes (11): 3.10 What a survivor looks like, 3.1 Company blocklist, 3.2 Exclusion keywords, 3.3 Clearance language, 3.4 Staffing agencies, 3.5 Internship gate, 3.6 Seniority filter (separate from the internship gate), 3.7 Years of experience (+3 more)

### Community 107 - "linkedin_people.py"
Cohesion: 0.07
Nodes (26): auto_discover_peers(), _crawl(), BlockerError, build_people_search_url(), _detect_blocker(), discover_peers(), extract_profile_urls(), _heuristic_parse() (+18 more)

### Community 108 - "TelegramClient"
Cohesion: 0.06
Nodes (27): AlertSummary, build_alert_caption(), _send_one(), send_pending_alerts(), process_updates(), run_polling(), Submitter, _should_retry_telegram() (+19 more)

### Community 109 - "Job Agent"
Cohesion: 0.13
Nodes (14): Application prep packs (LinkedIn / Indeed), Job Agent, Layout, LinkedIn peer benchmarking (optional, off by default), Resumes (Step 4), Run automation (Step 5), Run ingestion (Step 2), Run review bot (Step 6) (+6 more)

### Community 110 - "calculate_priority"
Cohesion: 0.19
Nodes (18): calculate_priority(), load_priority_config(), test_weights_sum_to_100(), _job(), _signal(), test_confidence_and_structured_evidence(), test_domains_are_capped_and_irrelevant_domains_add_nothing(), test_eligibility_order_and_unknown() (+10 more)

### Community 111 - "Phase 12 priority ranking"
Cohesion: 0.50
Nodes (3): Components, Phase 12 priority ranking, Version

### Community 112 - "Structured JD intelligence"
Cohesion: 0.33
Nodes (5): Application deadline, Cache, Limits, Structured JD intelligence, What is stored

### Community 113 - "builder.py"
Cohesion: 0.17
Nodes (7): _answer_item(), build_job_section(), compile_prep_pdf(), generate_prep_pack(), PrepPackResult, render_markdown(), test_render_markdown_includes_jobs_and_manual()

### Community 114 - "redact_error"
Cohesion: 0.33
Nodes (3): redact_error(), test_redact_error_covers_unlabeled_sk_and_basic_authorization(), test_redact_error_removes_representative_secrets()

### Community 115 - "Company intelligence 2.0"
Cohesion: 0.33
Nodes (5): Company intelligence 2.0, Company versus job, Sources and refresh, What it does not store, What it stores

### Community 116 - "test_false_negative.py"
Cohesion: 0.23
Nodes (9): citizenship_restriction(), clearance_requirement(), _matches_any(), max_acceptable_years(), _posting(), test_clearance_words_must_be_about_clearance(), test_explicit_internship_title_survives_seniority_words(), test_missing_or_weak_evidence_does_not_filter() (+1 more)

### Community 118 - "RawPosting"
Cohesion: 0.16
Nodes (8): RawPosting, test_to_job_stamps_workday_tenant_from_linkedin_url(), test_company_enrichment_failure_does_not_stop_ingestion(), one_posting(), test_internship_signal_matches_the_existing_gate(), test_provider_failure_does_not_break_ingestion(), one_posting(), test_jobsy_and_workday_descriptions_and_provenance()

### Community 119 - "SearchConfig"
Cohesion: 0.16
Nodes (8): SearchConfig, test_dry_run_does_not_fetch_or_write(), test_jobspy_exception_keeps_earlier_observations(), jobspy(), test_keyboard_interrupt_is_not_a_complete_report(), test_live_fake_attributes_only_the_requested_phrase(), jobspy(), workday()

### Community 122 - "Multi-dimensional role classification"
Cohesion: 0.29
Nodes (6): Cache, Contract, Function versus interaction, Multi-dimensional role classification, Non-goals, What the classifier reads

### Community 124 - "db.py"
Cohesion: 0.11
Nodes (15): _company_name(), _dialect_name(), _ensure_company_columns(), _ensure_job_columns(), _ensure_pipeline_stage_columns(), _incoming_description_unusable(), _is_sqlite_url(), _job_column_names() (+7 more)

### Community 125 - "test_cover_letter.py"
Cohesion: 0.16
Nodes (10): cap_cover_letter(), _fallback_cover_letter(), generate_cover_letter(), build_cover_letter_user(), _job(), _ScriptedClient, test_cap_cover_letter_cuts_on_sentence_boundary(), test_cap_cover_letter_hard_slice_without_punctuation() (+2 more)

### Community 126 - "asyncio"
Cohesion: 0.08
Nodes (12): configure_logging(), build_scheduler(), parse_hhmm(), run_service(), _noop(), test_build_scheduler_invalid_timezone(), test_build_scheduler_registers_jobs(), test_build_scheduler_skips_invalid_times() (+4 more)

### Community 127 - "Phase 6 candidate fit"
Cohesion: 0.33
Nodes (5): Dimensions, Not in this phase, Output, Phase 6 candidate fit, When the model is not called

### Community 129 - "test_role_weights.py"
Cohesion: 0.11
Nodes (20): _load_yaml(), _stamp_role_family_weight(), get_role_family_weight(), load_role_family_weights(), _validate(), weight_for_subfamily(), test_feedback_config_keeps_priority_integration_off(), test_company_and_vector_are_not_weight_inputs() (+12 more)

### Community 130 - "Any"
Cohesion: 0.10
Nodes (11): AnthropicClient, _attempt(), _as_int(), _finish_reason(), GeminiClient, _attempt(), _lower_thinking(), _attempt() (+3 more)

### Community 131 - "test_doctor.py"
Cohesion: 0.44
Nodes (7): _cmd_doctor(), _job(), test_doctor_cooldown(), test_doctor_empty_db(), test_doctor_outcomes(), test_doctor_vector_gate(), test_doctor_with_jobs()

### Community 135 - "How jobs are found, filtered, scored, and sent"
Cohesion: 0.25
Nodes (7): 1. What a run is, 4.1 Pre-score rank (`prerank_score`), 4.2 Embedding gate (this does drop jobs), 4.3 Fit-model cap, 4. How results are prioritised today, 7. Statuses, in one pass, How jobs are found, filtered, scored, and sent

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
- **181 isolated node(s):** `Where it is stored`, `Query timeout and incremental save`, `Recency`, `What this cannot reconstruct`, `ScrapeSummary` (+176 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 1173 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **19 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Job` connect `Job` to `telegram.py`, `test_role_weights.py`, `test_vector_gate.py`, `structured_jd.py`, `test_outcomes.py`, `test_doctor.py`, `test_career_intelligence.py`, `json`, `test_feedback.py`, `models.py`, `discovery_recall.py`, `AnswerResolver`, `eligibility.py`, `ingest.py`, `selector.py`, `test_structured_jd.py`, `Application`, `test_monitoring.py`, `diff.py`, `test_company_intelligence.py`, `runner.py`, `test_ingest_resilience.py`, `feedback.py`, `test_calibration.py`, `company_intelligence.py`, `test_eligibility.py`, `parse_workday_url`, `benchmark/engine.py`, `init_db`, `test_phase13_shortlist.py`, `profile.py`, `workday.py`, `compiler.py`, `vector_recovery.py`, `typing`, `answers.py`, `test_application_portfolio.py`, `test_priority.py`, `test_application_deadline.py`, `priority.py`, `main.py`, `test_vector_recovery.py`, `monitoring.py`, `tracker.py`, `bot/__init__.py`, `datetime`, `prep.py`, `Profile`, `outreach.py`, `WorkdaySubmitter`, `test_application_tracker.py`, `test_scorer.py`, `LLMClient`, `filters.py`, `scorer/engine.py`, `get_job_by_id`, `TelegramClient`, `calculate_priority`, `builder.py`, `test_false_negative.py`, `db.py`, `test_cover_letter.py`?**
  _High betweenness centrality (0.156) - this node is a cross-community bridge._
- **Are the 174 inferred relationships involving `Job` (e.g. with `Data model (core/db.py)` and `AnswerResolver`) actually correct?**
  _`Job` has 174 INFERRED edges - model-reasoned connections that need verification._
- **What connects `Where it is stored`, `Query timeout and incremental save`, `Recency` to the rest of the system?**
  _181 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `telegram.py` be split into smaller, more focused modules?**
  _Cohesion score 0.07928118393234672 - nodes in this community are weakly interconnected._
- **Why does `get_settings()` connect `get_settings` to `telegram.py`, `Any`, `test_vector_gate.py`, `test_phase0_baseline.py`, `clients.py`, `test_career_intelligence.py`, `json`, `evaluate`, `pathlib`, `models.py`, `discovery_recall.py`, `AnswerResolver`, `pipeline.py`, `Any`, `test_monitoring.py`, `diff.py`, `vault.py`, `runner.py`, `test_eligibility.py`, `benchmark/engine.py`, `init_db`, `test_phase13_shortlist.py`, `test_company_intelligence_v2.py`, `profile.py`, `workday.py`, `compiler.py`, `typing`, `answers.py`, `Settings`, `test_application_portfolio.py`, `main.py`, `test_vector_recovery.py`, `monitoring.py`, `datetime`, `prep.py`, `outreach.py`, `linkedin_jobspy.py`, `compute_tier`, `test_webhook.py`, `OpenAIEmbedder`, `pytest`, `test_scorer.py`, `LLMClient`, `filters.py`, `scorer/engine.py`, `Job`, `run_pipeline`, `linkedin_people.py`, `TelegramClient`, `builder.py`, `test_false_negative.py`, `db.py`, `test_cover_letter.py`, `asyncio`?**
  _High betweenness centrality (0.111) - this node is a cross-community bridge._
- **Are the 255 inferred relationships involving `Profile` (e.g. with `AnswerResolver` and `_latest_education()`) actually correct?**
  _`Profile` has 255 INFERRED edges - model-reasoned connections that need verification._
- **Should `structured_jd.py` be split into smaller, more focused modules?**
  _Cohesion score 0.12513842746400886 - nodes in this community are weakly interconnected._