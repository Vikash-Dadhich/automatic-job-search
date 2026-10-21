# Graph Report - Automatic job search  (2026-09-29)

## Corpus Check
- 165 files · ~114,051 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 13 file(s) not represented in the graph (top: (none) 8, .typ 2, .mdc 1)

## Summary
- 2541 nodes · 8353 edges · 112 communities (107 shown, 5 thin omitted)
- Extraction: 89% EXTRACTED · 11% INFERRED · 0% AMBIGUOUS · INFERRED: 916 edges (avg confidence: 0.94)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `8aa6b2cc`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- test_webhook.py
- test_pacing.py
- get_job_by_id
- test_eligibility.py
- test_targets.py
- clients.py
- bot/__init__.py
- test_fit.py
- test_discovery.py
- skills.py
- evaluate
- FakeTransport
- test_role_classify.py
- textclean.py
- test_apply_url.py
- re
- eligibility.py
- coverage.py
- telegram.py
- browser.py
- Job
- TelegramClient
- pipeline.py
- vault.py
- workday_rest.py
- telemetry.py
- linkedin_jobspy.py
- init_db
- Any
- test_pipeline_order_and_aggregation
- session_scope
- diff.py
- build_scheduler
- handle_callback
- workday.py
- get_settings
- Remaining Manual Setup
- handlers.py
- profile.py
- ingest.py
- Source
- db.py
- runner.py
- test_false_negative.py
- run_service
- test_llm_provider.py
- answers.py
- benchmark/engine.py
- test_prep_builder.py
- job_identity.py
- OpenAIEmbedder
- Profile
- Phase 5 role classification
- _build_doctor_report
- Job Agent
- Status
- alerts.py
- Phase 2 search taxonomy
- Benchmark — Product Manager @ T-Mobile
- review.py
- json
- Scorer
- .total_years_experience
- test_cover_letter.py
- linkedin_people.py
- test_company_intelligence.py
- LLMClient
- Phase 1 discovery architecture
- prep.py
- job-agent
- Phase 6 candidate fit
- test_gemini_client_falls_back_when_model_unavailable
- test_role_weights.py
- phase10-false-negative-protection.md
- Settings
- Phase 0 baseline
- test_scorer.py
- prerank.py
- Phase 9 visa and eligibility
- compiler.py
- filters.py
- test_resume.py
- WorkdaySubmitter
- test_base_resume.py
- test_answers.py
- pytest
- apply_pending
- FakeClient
- baseline.py
- Phase 8 company intelligence
- build_llm_client
- correction1-recruiting-universe.md
- db_ready
- 3. Hard filters (before any model)
- migrate_to_neon.py
- phase11-job-identity.md
- scorer/__init__.py
- scorer/engine.py
- AGENTS.md
- normalize_database_url
- 5. How fit is scored
- main.py
- test_score_pending_persists_tier_one_letter_only
- How jobs are found, filtered, scored, and sent
- test_workday_pairing.py
- 2. Where jobs come from
- 8. The weight discussion (not built)
- 9. Pain points we have actually hit or spelled out
- _handle_suggest_callback
- 6. What is sent to you
- Phase 12 priority ranking

## God Nodes (most connected - your core abstractions)
1. `Job` - 278 edges
2. `Profile` - 262 edges
3. `session_scope()` - 186 edges
4. `Source` - 164 edges
5. `Status` - 161 edges
6. `get_settings()` - 152 edges
7. `upsert_job()` - 101 edges
8. `get_job_by_id()` - 93 edges
9. `TelegramClient` - 76 edges
10. `Tier` - 58 edges

## Surprising Connections (you probably didn't know these)
- `What still needs the user (before live runs)` --references--> `save_session()`  [INFERRED]
  AGENTS.md → automation/login.py
- `Deploy with Docker` --references--> `save_session()`  [INFERRED]
  README.md → automation/login.py
- `Checklist (your remaining work)` --references--> `save_session()`  [INFERRED]
  SETUP.md → automation/login.py
- `Run review bot (Step 6)` --references--> `send_pending_alerts()`  [INFERRED]
  README.md → bot/alerts.py
- `6.2 The shortlist rule` --references--> `select_shortlist()`  [INFERRED]
  docs/how-jobs-are-found-scored-and-sent.md → bot/prep.py

## Import Cycles
- None detected.

## Communities (112 total, 5 thin omitted)

### Community 0 - "test_webhook.py"
Cohesion: 0.26
Nodes (11): fastapi_testclient, TestClient, client(), fixture, MonkeyPatch, Offline tests for FastAPI Telegram webhook., test_health(), test_webhook_ignored_without_callback() (+3 more)

### Community 1 - "test_pacing.py"
Cohesion: 0.10
Nodes (46): acquire(), AcquireResult, _clamp_multiplier(), _clock(), end_of_local_day(), gap_seconds(), is_pace_blocker(), note_pace_block() (+38 more)

### Community 2 - "get_job_by_id"
Cohesion: 0.24
Nodes (27): get_job_by_id(), profile_embed_text(), Head of the cacheable candidate block. Same cap as a job description., Module-level entry point used by README / Step 7., score_pending(), FakeClient, Any, Deterministic LLM stand-in for offline tests. (+19 more)

### Community 3 - "test_eligibility.py"
Cohesion: 0.15
Nodes (25): assign_eligibility(), attach_eligibility(), eligibility_column_types(), eligibility_is_current(), EligibilityDecision, evaluate_eligibility(), profile_eligibility_hash(), Hash of the profile facts this engine reads. Dream companies are excluded. (+17 more)

### Community 4 - "test_targets.py"
Cohesion: 0.12
Nodes (14): BaseModel, field_validator, model_validator, Skip placeholder tenants until the user fills real URLs., SearchConfig, Targets, Tests for Workday URL parsing and targets loading., test_parse_cxs_api_path() (+6 more)

### Community 5 - "clients.py"
Cohesion: 0.10
Nodes (33): random, _backoff_delay(), call_with_resilience(), is_permanent_account_error(), is_transient(), LLMBillingError, LLMError, BaseException (+25 more)

### Community 6 - "bot/__init__.py"
Cohesion: 0.13
Nodes (18): handle_message(), Handle incoming text messages — specifically force_reply captures for pending…, Telegram review bot (Step 6)., process_updates(), Any, Event, Long-polling loop for Telegram callback_query updates., Route a batch of updates; return the next offset (last update_id + 1). (+10 more)

### Community 7 - "test_fit.py"
Cohesion: 0.11
Nodes (42): build_fit_system_blocks(), build_fit_user(), cached_fit(), _Dimension, evaluate_fit(), fit_context_block(), fit_is_current(), FitDecision (+34 more)

### Community 8 - "test_discovery.py"
Cohesion: 0.07
Nodes (55): load_targets(), _load_yaml(), Any, Path, Load and validate targets.yaml. Cached after first successful load., Decimal, allocate_units(), AllocItem (+47 more)

### Community 9 - "skills.py"
Cohesion: 0.08
Nodes (39): collections, aggregate_role_skills(), AggregatedSkill, _categorize(), extract_top_skills(), extract_top_skills_deterministic(), JdSkill, parse_skills_json() (+31 more)

### Community 10 - "evaluate"
Cohesion: 0.15
Nodes (30): evaluate(), Return whether a posting should proceed to scoring., Classify a JD's stance on visa sponsorship without a profile dependency.…, sponsorship_signal(), test_sponsorship_and_false_friends(), _posting(), MonkeyPatch, Tests for the negative pre-filter. (+22 more)

### Community 11 - "FakeTransport"
Cohesion: 0.11
Nodes (24): decode_callback(), encode_callback(), BaseException, Encode inline-keyboard callback_data: v1|<action>|<job_id> (<=64 bytes)., Decode callback_data into (action, job_id)., Retry transport errors and HTTP 5xx; never retry 4xx client errors., _should_retry_telegram(), Path (+16 more)

### Community 12 - "test_role_classify.py"
Cohesion: 0.13
Nodes (29): classification_is_current(), classify_role(), _deterministic(), _ModelLabel, _parse_model(), BaseModel, Classify what a job is. This does not score whether the candidate should apply., True when the stored label was produced for this exact description. (+21 more)

### Community 13 - "textclean.py"
Cohesion: 0.07
Nodes (39): How to read it, Limits, Phase 3 discovery coverage, What a number means, Flow, Hash and upsert, Limits, Normalization (+31 more)

### Community 14 - "test_apply_url.py"
Cohesion: 0.19
Nodes (20): _eligible(), Workday source OR any source whose URL is a Workday company apply link., ApplyKind, classify_apply_url(), _host(), is_automateable_apply_url(), is_workday_url(), StrEnum (+12 more)

### Community 15 - "re"
Cohesion: 0.12
Nodes (27): _city_state(), company_matches(), company_tokens(), contains_phrase(), is_remote_location(), location_matches(), normalize_text(), Shared matching + truncation helpers used by filters, scoring, and answers.… (+19 more)

### Community 16 - "eligibility.py"
Cohesion: 0.17
Nodes (30): _ask_model(), _citizenship(), _clearance(), _current_student(), _dates(), _decision_from_job(), _dim(), DimensionResult (+22 more)

### Community 17 - "coverage.py"
Cohesion: 0.13
Nodes (30): build_coverage_report(), add_planned(), group_for(), GroupMetrics, observe_search(), _planned_slots(), StrEnum, QueryMetrics (+22 more)

### Community 18 - "telegram.py"
Cohesion: 0.11
Nodes (33): decide_suggestion(), _format_card(), Any, Telegram delivery and apply path for skill suggestions., Mark a suggestion approved/rejected/edited and maybe recompile., Send Telegram cards for jobs with unsent pending suggestions., send_pending_suggestions(), _suggestion_keyboard() (+25 more)

### Community 19 - "browser.py"
Cohesion: 0.17
Nodes (20): asyncio, launch_context(), _new_context(), new_page(), Page, Path, Stealth Playwright browser context using saved Workday sessions., Launch Chromium with stealth patches and optional saved storage_state. Yields… (+12 more)

### Community 20 - "Job"
Cohesion: 0.10
Nodes (32): _assign_canonical_url(), Job, Core job record threaded through discovery → scoring → application., Set the portfolio weight from the classified family. Fit and status stay put., Insert a job or update mutable fields when the posting is already stored. The…, _role_classification_current(), _stamp_role_family_weight(), upsert_job() (+24 more)

### Community 21 - "TelegramClient"
Cohesion: 0.13
Nodes (12): HttpxTransport, Any, Path, Protocol, retry, High-level Telegram helpers used by review / handlers / poller., Configured default chat id (may be None until set in .env)., Edit a text message. Outcome cards are text, not photos. (+4 more)

### Community 22 - "pipeline.py"
Cohesion: 0.15
Nodes (16): get_jobs_by_status(), get_suggestions_for_job(), Return jobs with the given status, oldest first., Orchestration package (Step 7)., _benchmark_tier_one_stage(), _generate_suggestions_stage(), PipelineSummary, Any (+8 more)

### Community 23 - "vault.py"
Cohesion: 0.15
Nodes (23): CredentialsFile, get_tenant_credentials(), has_saved_session(), load_credentials(), _load_yaml(), Any, BaseModel, Path (+15 more)

### Community 24 - "workday_rest.py"
Cohesion: 0.10
Nodes (37): WorkdayParts, WorkdayTenant, Response, _as_text(), _company_name(), _one(), _fetch_detail(), _fetch_listing_page() (+29 more)

### Community 25 - "telemetry.py"
Cohesion: 0.18
Nodes (15): action_delay_bounds(), Locator, Human-like delay and typing helpers for browser automation., Return (min_ms, max_ms) for between-action pauses., Return (min_ms, max_ms) for per-keystroke typing delay., Clear and type text with per-keystroke jitter (accessibility-friendly)., type_like_human(), typing_delay_bounds() (+7 more)

### Community 26 - "linkedin_jobspy.py"
Cohesion: 0.19
Nodes (19): math, _dataframe_to_postings(), _effective_windows(), _explicit_company_url(), _external_id(), fetch_linkedin_indeed(), _google_search_term(), _location_matches() (+11 more)

### Community 27 - "init_db"
Cohesion: 0.17
Nodes (16): apply_decided_suggestions(), If all suggestions for a job are decided, recompile resume with approvals.…, load_profile(), _load_yaml(), Any, Path, Load and validate profile.yaml. Cached after first successful load., Clear cache and reload (useful after editing profile.yaml). (+8 more)

### Community 28 - "Any"
Cohesion: 0.10
Nodes (18): LLM client layer (`scorer/clients.py`), AnthropicClient, _attempt(), _as_int(), _finish_reason(), GeminiClient, _attempt(), _lower_thinking() (+10 more)

### Community 29 - "test_pipeline_order_and_aggregation"
Cohesion: 0.15
Nodes (17): _FakeSummary, MonkeyPatch, Offline tests for orchestrator.pipeline (monkeypatched stages)., test_pipeline_order_and_aggregation(), fake_alerts(), fake_apply(), fake_ingestion(), fake_outcomes() (+9 more)

### Community 30 - "session_scope"
Cohesion: 0.51
Nodes (9): session_scope(), _posting(), Path, One posting, one job. Uncertain matches stay separate., test_homepage_query_does_not_merge_across_sources(), test_material_description_change_still_clears_fit(), test_same_place_and_text_can_merge_without_using_fit(), test_same_source_identity_and_cross_source_url() (+1 more)

### Community 31 - "diff.py"
Cohesion: 0.14
Nodes (34): get_role_baseline_by_role(), StrEnum, Per-role baseline resume built from aggregating ~15-20 JDs., RoleBaseline, SkillPlacement, SkillProvenance, SuggestionStatus, apply_approved_suggestions_to_resume_data() (+26 more)

### Community 32 - "build_scheduler"
Cohesion: 0.23
Nodes (14): AsyncIOScheduler, build_scheduler(), parse_hhmm(), Any, Parse 'HH:MM' into (hour, minute). Raises ValueError on bad input., Build (but do not start) an AsyncIOScheduler with one job per HH:MM. Jobs use…, _noop(), MonkeyPatch (+6 more)

### Community 33 - "handle_callback"
Cohesion: 0.29
Nodes (18): handle_callback(), Handle one Telegram update containing a callback_query. Returns the resulting…, SubmitResult, is_outcome_callback(), ReviewAction, _callback_update(), FakeSubmitter, Any (+10 more)

### Community 34 - "workday.py"
Cohesion: 0.18
Nodes (23): human_delay(), Sleep a jittered duration; return the seconds slept., click_by_role(), click_next(), _collect_labeled_fields(), detect_blocker(), _fill_field(), is_review_page() (+15 more)

### Community 35 - "get_settings"
Cohesion: 0.09
Nodes (27): apscheduler_schedulers_asyncio, apscheduler_triggers_cron, health(), FastAPI webhook for Telegram (ready for Step 7 production)., collections_abc, Public config exports., get_settings(), Typed application settings loaded from environment / .env. (+19 more)

### Community 36 - "Remaining Manual Setup"
Cohesion: 0.08
Nodes (25): 2a. Find a Workday URL, 2b. Edit `config/targets.yaml`, 3a. Run the save-session helper, 3b. What you do in the browser, 4a. Discover jobs (LinkedIn / Indeed + any real Workday tenants), 4b. Score with Gemini, 4c. Attach your base resume to staged jobs, 4d. Send LinkedIn/Indeed application prep pack (Telegram) (+17 more)

### Community 37 - "handlers.py"
Cohesion: 0.10
Nodes (41): _decision_caption(), _handle_outcome_callback(), Dispatch Telegram callback_query decisions for pending_review jobs and skill…, Record a post-submit label. Does not change status or decided_at., build_outcome_keyboard(), button(), outcome_label(), outcome_message_text() (+33 more)

### Community 38 - "profile.py"
Cohesion: 0.13
Nodes (34): Address, Education, Exclusions, Experience, Identity, Preferences, BaseModel, field_validator (+26 more)

### Community 39 - "ingest.py"
Cohesion: 0.11
Nodes (26): CoverageReport, fail_unrecorded(), _jsonable(), log_coverage(), Path, Internal discovery coverage. Not a share of the internship market., One executed search on one source. Hits keep result order., Mark planned searches that never reported in as failures, not empty results. (+18 more)

### Community 40 - "Source"
Cohesion: 0.10
Nodes (46): Data model (core/db.py), Status lifecycle, get_job_by_source_id(), Source, evaluate_job(), Apply the same hard-negative rules to a persisted Job (scoring backlog guard)., hash_fallback(), BaseModel (+38 more)

### Community 41 - "db.py"
Cohesion: 0.09
Nodes (33): async_sessionmaker, _company_name(), _dialect_name(), _ensure_job_columns(), get_engine(), get_recently_applied_companies(), get_session_factory(), _incoming_description_unusable() (+25 more)

### Community 42 - "runner.py"
Cohesion: 0.11
Nodes (18): Workday application automation (Step 5)., ApplyRunner, ApplySummary, _ensure_tenant(), datetime, Batch runner: staged Workday-eligible jobs -> pending_review (or…, Stamp job.tenant from the Workday URL when missing (LinkedIn→Workday case)., Drive Workday pre-fill for staged jobs with injectable Applicator. (+10 more)

### Community 43 - "test_false_negative.py"
Cohesion: 0.12
Nodes (21): citizenship_restriction(), _clearance_clauses(), clearance_requirement(), _matches_any(), max_acceptable_years(), True when the posting explicitly limits applicants to U.S. citizens., Split so a later sentence cannot change an earlier clearance statement., ``required``, ``preferred``, or ``none``. Required or preferred is decided from… (+13 more)

### Community 44 - "run_service"
Cohesion: 0.22
Nodes (8): Event, Start the scheduler and (optionally) the Telegram poller until stopped.…, run_service(), MonkeyPatch, Path, Scheduler starts; preset stop_event exits cleanly with run_poller=False., test_run_service_stops_without_poller(), test_run_service_with_poller_respects_stop()

### Community 45 - "test_llm_provider.py"
Cohesion: 0.13
Nodes (15): _FakeAio, _FakeAsyncModels, _FakeCandidate, _FakeGenerateResponse, Any, MonkeyPatch, Offline tests for switchable LLM provider (Gemini default / Anthropic fallback)., test_active_models_ignore_anthropic_names() (+7 more)

### Community 46 - "answers.py"
Cohesion: 0.10
Nodes (26): one(), answers_to_payload(), _discovery_channel(), is_open_ended(), _latest_education(), _matches(), needs_human_review(), _norm() (+18 more)

### Community 47 - "benchmark/engine.py"
Cohesion: 0.13
Nodes (27): BenchmarkReport, BenchmarkSummary, build_benchmark(), _derive_seniority(), DimensionScore, _education_rank(), _median(), _norm() (+19 more)

### Community 48 - "test_prep_builder.py"
Cohesion: 0.13
Nodes (25): build_job_section(), compile_prep_pdf(), generate_prep_pack(), PrepPackResult, Any, LLMClient, Path, Compile prep-pack JSON via Typst template to PDF. (+17 more)

### Community 49 - "job_identity.py"
Cohesion: 0.15
Nodes (22): _find_cross_source_job(), Another source's row for this posting. Same-source ids are never folded…, canonicalize_job_url(), _is_tracking_param(), locations_agree(), locations_conflict(), normalize_title(), Deterministic posting identity. Uncertain matches stay separate jobs. (+14 more)

### Community 50 - "OpenAIEmbedder"
Cohesion: 0.38
Nodes (4): OpenAIEmbedder, Any, OpenAI embeddings. Width is ``vector_dimensions``., _vectors_from_response()

### Community 51 - "Profile"
Cohesion: 0.21
Nodes (17): Profile, Single Source of Truth for candidate facts. No LLM invention beyond this., _enable_internship_only(), _posting(), Any, MonkeyPatch, parametrize, Phase 0 locks: profile facts, experience span, internship gate, sponsorship. (+9 more)

### Community 52 - "Phase 5 role classification"
Cohesion: 0.29
Nodes (6): Inputs, Limits, Output, Phase 5 role classification, Taxonomy, When it runs again

### Community 53 - "_build_doctor_report"
Cohesion: 0.36
Nodes (8): _build_doctor_report(), _count_jobs(), _print_doctor_report(), Any, First element of a row tuple; scalars pass through., Read-only pipeline health snapshot. No LLM calls., Human-readable health report. JSON mode prints the dict instead., _unwrap()

### Community 54 - "Job Agent"
Cohesion: 0.12
Nodes (15): Application prep packs (LinkedIn / Indeed), Deploy with Docker, Job Agent, Layout, LinkedIn peer benchmarking (optional, off by default), Resumes (Step 4), Run automation (Step 5), Run ingestion (Step 2) (+7 more)

### Community 55 - "Status"
Cohesion: 0.20
Nodes (23): Status, Tier, Core persistence and shared utilities., _cmd_doctor(), compute_tier(), Deterministic tier from score + dream-company override (thresholds in settings)., _save_vector(), _job() (+15 more)

### Community 56 - "alerts.py"
Cohesion: 0.20
Nodes (16): AlertSummary, build_alert_caption(), Telegram alerts for blocked / errored jobs (not pending_review cards)., Caption for a blocker / error alert., Notify on unsent manual_review / error jobs (screenshot + reason)., _send_one(), send_pending_alerts(), get_unsent_alerts() (+8 more)

### Community 57 - "Phase 2 search taxonomy"
Cohesion: 0.50
Nodes (3): Ambiguous phrases, Phase 2 search taxonomy, What was added

### Community 58 - "Benchmark — Product Manager @ T-Mobile"
Cohesion: 0.33
Nodes (5): Benchmark — Product Manager @ T-Mobile, Dimensions, Gaps, Recommendations, Strengths

### Community 59 - "review.py"
Cohesion: 0.14
Nodes (23): build_keyboard(), build_review_caption(), format_answers_message(), format_cover_letter_message(), Any, Build and send Telegram review cards for pending_review jobs., Follow-up text with the stored cover letter, if one was drafted., Send Telegram review cards for unsent pending_review jobs. (+15 more)

### Community 60 - "json"
Cohesion: 0.16
Nodes (21): effective_baseline(), effective_config_hash(), profile_hash(), public_config(), Any, Path, Secret-free snapshot of the candidate profile version and effective config. The…, SHA-256 of the parsed profile facts. Comments and key order do not matter. (+13 more)

### Community 61 - "Scorer"
Cohesion: 0.19
Nodes (9): _attach_priority(), Record attention order. A failure here does not change fit, tier, or status., Score discovered jobs and persist tiered results., Score a single job and optionally draft Tier-1 outreach and a cover letter., Score one job and persist; never raises (returns error outcome)., Scorer, _status_for_tier(), test_insufficient_fit_is_not_stored_as_zero() (+1 more)

### Community 62 - ".total_years_experience"
Cohesion: 0.50
Nodes (4): _parse_month(), date, Approximate career length in years, spanning earliest start to latest end., Parse 'YYYY-MM' / 'YYYY'; 'Present' and unparseable values return None.

### Community 63 - "test_cover_letter.py"
Cohesion: 0.18
Nodes (15): cap_cover_letter(), generate_cover_letter(), Tier-1 cover letter drafting with the same anti-AI gate as outreach., Trim to the last sentence that fits, so a runaway letter stays usable., Draft a short cover letter; retry once if banned words appear., build_cover_letter_user(), User prompt for a Tier-1 cover letter. Phrase is matched by test fakes., _job() (+7 more)

### Community 64 - "linkedin_people.py"
Cohesion: 0.07
Nodes (45): auto_discover_peers(), _crawl(), BlockerError, build_people_search_url(), _detect_blocker(), discover_peers(), extract_profile_urls(), _heuristic_parse() (+37 more)

### Community 65 - "test_company_intelligence.py"
Cohesion: 0.06
Nodes (73): CompanyIntelligence, Factual employer record shared by jobs. Not a score and not a preference., httpx, _accumulate_sources(), _apply_facts(), attach_company_intelligence(), _by_key(), canonical_company_name() (+65 more)

### Community 66 - "LLMClient"
Cohesion: 0.13
Nodes (17): LLMClient, Protocol, Minimal async LLM interface (mockable for offline tests)., _fallback_cover_letter(), Deterministic letter used when the model keeps failing the style gate., contains_banned(), _fallback_outreach(), generate_outreach() (+9 more)

### Community 67 - "Phase 1 discovery architecture"
Cohesion: 0.14
Nodes (13): 40/40/15/5 priority model, Current problem, New architecture, Phase 1 discovery architecture, Provenance, Purpose, Role families, Search allocation (+5 more)

### Community 68 - "prep.py"
Cohesion: 0.10
Nodes (33): _load_scored(), _mark_sent(), PrepSummary, datetime, LLMClient, Generate and deliver LinkedIn/Indeed application prep packs via Telegram., One text file for the run. Empty input sends nothing., Build and send a prep pack for unsent staged LinkedIn/Indeed jobs. Brief mode… (+25 more)

### Community 71 - "Phase 6 candidate fit"
Cohesion: 0.33
Nodes (5): Dimensions, Not in this phase, Output, Phase 6 candidate fit, When the model is not called

### Community 72 - "test_gemini_client_falls_back_when_model_unavailable"
Cohesion: 0.38
Nodes (7): _FakeGenaiClient, asyncio, A 503 on the primary model must roll over to the configured fallback., Thinking can eat the whole budget; retry must raise max_output_tokens., test_gemini_client_complete_maps_system_blocks(), test_gemini_client_escalates_on_truncated_output(), test_gemini_client_falls_back_when_model_unavailable()

### Community 73 - "test_role_weights.py"
Cohesion: 0.05
Nodes (82): Canonical portfolio, Configuration, Four different questions, Phase 7 role-family weighting, Unknown classification, What is stored, What this phase does not do, Where the family comes from (+74 more)

### Community 75 - "Settings"
Cohesion: 0.20
Nodes (8): BaseSettings, Path, Central configuration for the job agent. Secrets and overrides come from…, Return an absolute path rooted at the project directory when relative., Fixed path for the candidate's personal resume PDF (default for applications)., Ordered alternates for a primary model (Gemini only), excluding duplicates., Settings, test_internship_only_code_default_is_false()

### Community 76 - "Phase 0 baseline"
Cohesion: 0.22
Nodes (8): Candidate baseline, Discovery baseline, Local versus production, Phase 0 baseline, Production baseline, Scoring baseline, Sponsorship behavior locked by tests, Tests

### Community 77 - "test_scorer.py"
Cohesion: 0.09
Nodes (34): approx_tokens(), cache_block(), compact_json_dumps(), minify_job(), Any, Payload compression, schema minification, and prompt-caching utilities., Build an Anthropic system content block with ephemeral prompt caching., Compact job description for scoring: title/company/location + cleaned JD. (+26 more)

### Community 78 - "prerank.py"
Cohesion: 0.21
Nodes (17): prerank_jobs(), prerank_score(), Deterministic, LLM-free pre-rank to order jobs before scoring. Recall/cost…, Return jobs ordered best-first by ``prerank_score`` (stable on ties)., Map a job source to a rank weight. Unknown values score as 1.0., Cheap 0..~100 heuristic; higher = score sooner. No network, no LLM., _source_weight(), _job() (+9 more)

### Community 79 - "Phase 9 visa and eligibility"
Cohesion: 0.25
Nodes (7): Cache and storage, Education, graduation, experience, location, dates, Phase 9 visa and eligibility, Sponsorship, citizenship, and clearance, States, What the profile contributes, What this phase does not do

### Community 80 - "compiler.py"
Cohesion: 0.11
Nodes (39): apply_fit_caps(), _baseline_pdf_for_job(), clean_name(), compile_pending(), compile_resume(), compile_resume_data(), FitReport, _job_resume_output() (+31 more)

### Community 81 - "filters.py"
Cohesion: 0.15
Nodes (18): FilterResult, has_internship_signal(), _haystack(), location_acceptable(), _location_ok(), _mandatory_years(), datetime, _qualifier_is_mandatory() (+10 more)

### Community 82 - "test_resume.py"
Cohesion: 0.12
Nodes (30): pikepdf, build_resume_data(), extract_job_terms(), _grounded_summary(), Any, RankedBullet, Deterministic JD-aware bullet and skill selection for resume tailoring., Lowercase tokens + bigrams from title and cleaned description. (+22 more)

### Community 83 - "WorkdaySubmitter"
Cohesion: 0.18
Nodes (14): RuntimeError, Raised when no reusable storage_state exists for a tenant., SessionMissingError, Path, Reopen saved session, reach review, click Submit once., WorkdaySubmitter, contextlib, MonkeyPatch (+6 more)

### Community 84 - "test_base_resume.py"
Cohesion: 0.37
Nodes (12): _make_base_pdf(), _profile(), Path, Tests for static base resume preparation and on-demand Typst tailoring., Create a valid PDF via Typst to stand in for the user's base resume., _sample_job(), test_base_resume_file_property(), test_compile_for_job_overwrites() (+4 more)

### Community 85 - "test_answers.py"
Cohesion: 0.24
Nodes (13): AnswerResolver, AnswerSource, StrEnum, Resolve form labels to answers; LLM only for open-ended unknowns., FakeAnswerClient, Any, Offline tests for AnswerResolver (deterministic + mock LLM)., test_cover_letter_field_uses_stored_text() (+5 more)

### Community 86 - "pytest"
Cohesion: 0.33
Nodes (4): pytest, asyncio, Optional Playwright locator smoke test against a local HTML fixture. Skipped…, test_accessibility_locators_on_fixture()

### Community 87 - "apply_pending"
Cohesion: 0.30
Nodes (14): apply_pending(), Random, Module-level entry point used by README / Step 7., FakeApplicator, Path, Offline tests for apply_pending with FakeApplicator (no browser)., LinkedIn-discovered roles that apply on Workday must be eligible., _seed_job() (+6 more)

### Community 88 - "FakeClient"
Cohesion: 0.40
Nodes (3): FakeClient, Any, Return different skills for baseline JDs vs the target posting.

### Community 89 - "baseline.py"
Cohesion: 0.19
Nodes (14): get_jobs_for_role(), Return recent jobs whose title matches any of the role title terms. Matching is…, datetime, build_baseline_resume_data(), build_role_baseline(), _normalize(), Any, LLMClient (+6 more)

### Community 90 - "Phase 8 company intelligence"
Cohesion: 0.29
Nodes (6): Names and reuse, Phase 8 company intelligence, Schema, Sources, What it is, What this phase does not change

### Community 91 - "build_llm_client"
Cohesion: 0.21
Nodes (11): Scoring specifics (Step 3), Tech stack, Model id used for scoring. Always the OpenAI scorer., Model id used for outreach / open-ended answers. Always OpenAI., build_llm_client(), OpenAIClient, OpenAI Chat Completions client. JSON scoring uses json_object mode., Scoring and writing always go through OpenAI. (+3 more)

### Community 93 - "db_ready"
Cohesion: 0.20
Nodes (14): Testing conventions, db_ready(), _disable_apply_pacing(), _disable_vector_gate(), _internship_only_off(), fixture, MonkeyPatch, Path (+6 more)

### Community 94 - "3. Hard filters (before any model)"
Cohesion: 0.18
Nodes (11): 3.10 What a survivor looks like, 3.1 Company blocklist, 3.2 Exclusion keywords, 3.3 Clearance language, 3.4 Staffing agencies, 3.5 Internship gate, 3.6 Seniority filter (separate from the internship gate), 3.7 Years of experience (+3 more)

### Community 95 - "migrate_to_neon.py"
Cohesion: 0.22
Nodes (13): enum, _cell(), _copy_table(), _counts(), main(), AsyncSession, SQLModel, Copy local SQLite rows into the Neon Postgres database. Reads… (+5 more)

### Community 97 - "scorer/__init__.py"
Cohesion: 0.22
Nodes (8): LLM match evaluator with tier triage and Tier-1 outreach., Evaluation, BaseModel, field_validator, Pydantic schemas for LLM scoring output., Tolerant raw score payload from the model: {"s","t","r"}., Normalized evaluation ready to persist on a Job row., ScoreRaw

### Community 98 - "scorer/engine.py"
Cohesion: 0.07
Nodes (48): build_embedder(), _cache_path(), clears_threshold(), cosine(), Embedder, jd_vector(), job_embed_text(), load_profile_embedding() (+40 more)

### Community 99 - "AGENTS.md"
Cohesion: 0.20
Nodes (8): Build order and status, Coding conventions, Commands, Confirmed product decisions, Project, Repository layout, What still needs the user (before live runs), Workflow for implementing a step

### Community 100 - "normalize_database_url"
Cohesion: 0.29
Nodes (9): _absolute_sqlite_url(), normalize_database_url(), Normalize DATABASE_URL for SQLAlchemy async engines. - Relative sqlite paths…, Make relative sqlite paths absolute so cwd does not matter., DATABASE_URL normalization for SQLite + Neon Postgres., test_normalize_drops_prisma_connection_limit(), test_normalize_keeps_sqlite(), test_normalize_upgrades_postgres_scheme() (+1 more)

### Community 101 - "5. How fit is scored"
Cohesion: 0.22
Nodes (8): Compact, cacheable candidate summary for LLM system prompts (Step 3)., 10. File map, 5.1 What the model is, 5.2 The two inputs, 5.3 The rubric, verbatim in meaning, 5.4 What the code does with the score, 5.5 What a number means, 5. How fit is scored

### Community 102 - "main.py"
Cohesion: 0.10
Nodes (28): argparse, ArgumentParser, configure_logging(), Central structlog configuration., Configure structlog + stdlib logging once at process start. Console renderer…, build_parser(), _cmd_build_baseline(), _cmd_poll() (+20 more)

### Community 103 - "test_score_pending_persists_tier_one_letter_only"
Cohesion: 0.22
Nodes (4): Path, test_cover_letter_failure_still_stages(), test_score_pending_persists_tier_one_letter_only(), test_tier_one_drafts_stay_off_unless_enabled()

### Community 104 - "How jobs are found, filtered, scored, and sent"
Cohesion: 0.25
Nodes (7): 1. What a run is, 4.1 Pre-score rank (`prerank_score`), 4.2 Embedding gate (this does drop jobs), 4.3 Fit-model cap, 4. How results are prioritised today, 7. Statuses, in one pass, How jobs are found, filtered, scored, and sent

### Community 105 - "test_workday_pairing.py"
Cohesion: 0.29
Nodes (5): asyncio, MonkeyPatch, Regression test: Workday detail responses must attach to the right listing., A listing without externalPath used to shift details onto the wrong jobs., test_details_pair_with_correct_listing()

### Community 106 - "2. Where jobs come from"
Cohesion: 0.29
Nodes (7): 2.1 Search terms, 2.2 Sites and the exact JobSpy arguments, 2.3 How each site treats "posted in the last 36 hours", 2.4 What is kept from a JobSpy row, 2.5 Workday, separately from LinkedIn, 2.6 Save and dedupe, 2. Where jobs come from

### Community 107 - "8. The weight discussion (not built)"
Cohesion: 0.33
Nodes (6): 8.1 What you asked for, 8.2 Decisions you agreed with, 8.3 A weight table we used as a sketch, 8.4 What we said the rubric should do for career-switch roles, 8.5 How that would sit on the current pipeline, 8. The weight discussion (not built)

### Community 108 - "9. Pain points we have actually hit or spelled out"
Cohesion: 0.33
Nodes (6): 9.1 Discovery, 9.2 Filters, 9.3 Scoring, 9.4 What you receive, 9.5 Operations, 9. Pain points we have actually hit or spelled out

### Community 109 - "_handle_suggest_callback"
Cohesion: 0.40
Nodes (5): _handle_suggest_callback(), Any, Ack a callback_query; never raise (expired/fake IDs return Telegram 400)., Handle s1|approve|id / edit / reject suggestion callbacks., _safe_answer()

### Community 110 - "6. What is sent to you"
Cohesion: 0.40
Nodes (5): 6.1 Who is eligible, 6.2 The shortlist rule, 6.3 Each line, 6.4 If brief mode is turned off, 6. What is sent to you

### Community 111 - "Phase 12 priority ranking"
Cohesion: 0.50
Nodes (3): Components, Phase 12 priority ranking, Version

## Knowledge Gaps
- **131 isolated node(s):** `job-agent`, `ScrapeSummary`, `_Sites`, `_FakeAio`, `Project` (+126 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 868 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **5 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Job` connect `Job` to `test_pacing.py`, `get_job_by_id`, `test_eligibility.py`, `bot/__init__.py`, `test_fit.py`, `skills.py`, `FakeTransport`, `test_role_classify.py`, `test_apply_url.py`, `eligibility.py`, `telegram.py`, `pipeline.py`, `diff.py`, `handle_callback`, `workday.py`, `get_settings`, `handlers.py`, `profile.py`, `ingest.py`, `Source`, `db.py`, `runner.py`, `test_false_negative.py`, `answers.py`, `benchmark/engine.py`, `test_prep_builder.py`, `job_identity.py`, `_build_doctor_report`, `Status`, `alerts.py`, `review.py`, `Scorer`, `test_cover_letter.py`, `test_company_intelligence.py`, `LLMClient`, `prep.py`, `test_role_weights.py`, `test_scorer.py`, `prerank.py`, `compiler.py`, `filters.py`, `test_resume.py`, `WorkdaySubmitter`, `test_base_resume.py`, `test_answers.py`, `apply_pending`, `baseline.py`, `migrate_to_neon.py`, `scorer/engine.py`, `main.py`, `test_score_pending_persists_tier_one_letter_only`?**
  _High betweenness centrality (0.145) - this node is a cross-community bridge._
- **Why does `Profile` connect `Profile` to `get_job_by_id`, `test_eligibility.py`, `test_fit.py`, `evaluate`, `eligibility.py`, `telegram.py`, `Job`, `linkedin_jobspy.py`, `init_db`, `diff.py`, `workday.py`, `get_settings`, `profile.py`, `ingest.py`, `Source`, `runner.py`, `test_false_negative.py`, `answers.py`, `benchmark/engine.py`, `test_prep_builder.py`, `Status`, `Scorer`, `.total_years_experience`, `test_cover_letter.py`, `LLMClient`, `prep.py`, `test_role_weights.py`, `test_scorer.py`, `prerank.py`, `Phase 9 visa and eligibility`, `compiler.py`, `filters.py`, `test_resume.py`, `test_base_resume.py`, `test_answers.py`, `apply_pending`, `baseline.py`, `scorer/engine.py`, `5. How fit is scored`, `test_score_pending_persists_tier_one_letter_only`?**
  _High betweenness centrality (0.124) - this node is a cross-community bridge._
- **Why does `get_settings()` connect `get_settings` to `test_webhook.py`, `test_pacing.py`, `get_job_by_id`, `test_eligibility.py`, `clients.py`, `bot/__init__.py`, `skills.py`, `evaluate`, `textclean.py`, `re`, `telegram.py`, `browser.py`, `Job`, `TelegramClient`, `pipeline.py`, `vault.py`, `telemetry.py`, `init_db`, `Any`, `diff.py`, `build_scheduler`, `workday.py`, `profile.py`, `Source`, `db.py`, `runner.py`, `test_false_negative.py`, `run_service`, `test_llm_provider.py`, `answers.py`, `benchmark/engine.py`, `test_prep_builder.py`, `OpenAIEmbedder`, `Profile`, `_build_doctor_report`, `Status`, `json`, `Scorer`, `test_cover_letter.py`, `linkedin_people.py`, `LLMClient`, `prep.py`, `Settings`, `test_scorer.py`, `compiler.py`, `filters.py`, `test_resume.py`, `test_base_resume.py`, `baseline.py`, `migrate_to_neon.py`, `scorer/engine.py`, `main.py`?**
  _High betweenness centrality (0.119) - this node is a cross-community bridge._
- **Are the 115 inferred relationships involving `Job` (e.g. with `Data model (core/db.py)` and `AnswerResolver`) actually correct?**
  _`Job` has 115 INFERRED edges - model-reasoned connections that need verification._
- **Are the 196 inferred relationships involving `Profile` (e.g. with `AnswerResolver` and `_latest_education()`) actually correct?**
  _`Profile` has 196 INFERRED edges - model-reasoned connections that need verification._
- **Are the 109 inferred relationships involving `Source` (e.g. with `Data model (core/db.py)` and `_eligible()`) actually correct?**
  _`Source` has 109 INFERRED edges - model-reasoned connections that need verification._
- **Are the 113 inferred relationships involving `Status` (e.g. with `Data model (core/db.py)` and `ApplyRunner`) actually correct?**
  _`Status` has 113 INFERRED edges - model-reasoned connections that need verification._