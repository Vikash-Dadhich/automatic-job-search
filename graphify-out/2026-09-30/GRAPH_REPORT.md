# Graph Report - Automatic job search  (2026-09-30)

## Corpus Check
- 168 files · ~117,142 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 13 file(s) not represented in the graph (top: (none) 8, .typ 2, .mdc 1)

## Summary
- 2597 nodes · 8546 edges · 116 communities (109 shown, 7 thin omitted)
- Extraction: 89% EXTRACTED · 11% INFERRED · 0% AMBIGUOUS · INFERRED: 942 edges (avg confidence: 0.94)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `69e875ca`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- test_webhook.py
- RawPosting
- test_vector_gate.py
- Profile
- targets.py
- clients.py
- poller.py
- test_fit.py
- test_discovery.py
- baseline.py
- evaluate
- FakeTransport
- get_job_by_source_id
- textclean.py
- test_apply_url.py
- job_identity.py
- eligibility.py
- coverage.py
- get_job_by_id
- Settings
- session_scope
- TelegramClient
- pipeline.py
- get_settings
- workday_rest.py
- role_classify.py
- linkedin_jobspy.py
- bot/__init__.py
- Any
- test_pipeline_order_and_aggregation
- Tier
- diff.py
- build_scheduler
- profile.py
- workday.py
- alerts.py
- Remaining Manual Setup
- telegram.py
- test_prep_delivery.py
- ingest.py
- test_recruiting_universe.py
- db.py
- test_pacing.py
- _posting
- run_service
- shortlist.py
- test_answers.py
- linkedin_people.py
- test_prep_builder.py
- test_base_resume.py
- pytest
- test_phase0_baseline.py
- Phase 5 role classification
- AGENTS.md
- Job Agent
- _build_doctor_report
- answers.py
- Phase 2 search taxonomy
- Benchmark — Product Manager @ T-Mobile
- automation/__init__.py
- json
- LLMClient
- .total_years_experience
- test_cover_letter.py
- OpenAIEmbedder
- test_company_intelligence.py
- priority.py
- Phase 1 discovery architecture
- prep.py
- job-agent
- Phase 6 candidate fit
- token_optimizer.py
- test_role_weights.py
- phase10-false-negative-protection.md
- test_priority.py
- Phase 0 baseline
- test_scorer.py
- test_phase13_shortlist.py
- Phase 9 visa and eligibility
- compiler.py
- filters.py
- test_resume.py
- Job
- benchmark/engine.py
- test_main_cli.py
- scrape_profile
- test_linkedin_people.py
- Phase 7 role-family weighting
- parse_score
- Phase 8 company intelligence
- dataclasses
- correction1-recruiting-universe.md
- db_ready
- 3. Hard filters (before any model)
- test_linkedin_discover.py
- phase11-job-identity.md
- scorer/__init__.py
- scorer/engine.py
- sort_by_priority
- Embedder
- 5. How fit is scored
- main.py
- SQLModel
- How jobs are found, filtered, scored, and sent
- has_internship_signal
- 2. Where jobs come from
- 8. The weight discussion (not built)
- 9. Pain points we have actually hit or spelled out
- logging.py
- 6. What is sent to you
- Phase 12 priority ranking
- FakeClient
- BlockerError
- _half_up_ratio
- .complete

## God Nodes (most connected - your core abstractions)
1. `Job` - 290 edges
2. `Profile` - 263 edges
3. `session_scope()` - 191 edges
4. `Status` - 173 edges
5. `Source` - 166 edges
6. `get_settings()` - 152 edges
7. `upsert_job()` - 104 edges
8. `get_job_by_id()` - 97 edges
9. `TelegramClient` - 76 edges
10. `init_db()` - 60 edges

## Surprising Connections (you probably didn't know these)
- `Run review bot (Step 6)` --references--> `send_pending_alerts()`  [INFERRED]
  README.md → bot/alerts.py
- `What the profile contributes` --references--> `Profile`  [INFERRED]
  docs/phase9-visa-eligibility.md → config/profile.py
- `New architecture` --references--> `load_targets()`  [INFERRED]
  docs/phase1-discovery-architecture.md → config/targets.py
- `Pipeline` --references--> `prepare_pending()`  [INFERRED]
  docs/phase13-shortlist.md → resume/compiler.py
- `Confirmed product decisions` --references--> `compile_for_job()`  [INFERRED]
  AGENTS.md → resume/compiler.py

## Import Cycles
- None detected.

## Communities (116 total, 7 thin omitted)

### Community 0 - "test_webhook.py"
Cohesion: 0.29
Nodes (10): fastapi_testclient, TestClient, client(), fixture, MonkeyPatch, Offline tests for FastAPI Telegram webhook., test_health(), test_webhook_ignored_without_callback() (+2 more)

### Community 1 - "RawPosting"
Cohesion: 0.11
Nodes (31): hash_fallback(), BaseModel, Normalized intermediate posting model and Job mapping., Source-agnostic posting produced by scrapers before DB persistence., Map a RawPosting to a Job row, computing content_hash., RawPosting, to_job(), test_to_job_stamps_workday_tenant_from_linkedin_url() (+23 more)

### Community 2 - "test_vector_gate.py"
Cohesion: 0.27
Nodes (25): profile_embed_text(), Head of the cacheable candidate block. Same cap as a job description., Module-level entry point used by README / Step 7., score_pending(), FakeClient, Deterministic LLM stand-in for offline tests., _enable(), FakeEmbedder (+17 more)

### Community 3 - "Profile"
Cohesion: 0.16
Nodes (27): Profile, Single Source of Truth for candidate facts. No LLM invention beyond this., assign_eligibility(), attach_eligibility(), eligibility_column_types(), eligibility_is_current(), evaluate_eligibility(), profile_eligibility_hash() (+19 more)

### Community 4 - "targets.py"
Cohesion: 0.07
Nodes (31): Public config exports., _load_yaml(), parse_workday_url(), Any, BaseModel, field_validator, model_validator, Path (+23 more)

### Community 5 - "clients.py"
Cohesion: 0.10
Nodes (33): LLM client layer (`scorer/clients.py`), _backoff_delay(), call_with_resilience(), is_permanent_account_error(), is_transient(), LLMBillingError, LLMError, BaseException (+25 more)

### Community 6 - "poller.py"
Cohesion: 0.09
Nodes (23): handle_message(), Handle incoming text messages — specifically force_reply captures for pending…, process_updates(), Any, Event, Long-polling loop for Telegram callback_query updates., Route a batch of updates; return the next offset (last update_id + 1)., Long-poll Telegram getUpdates until stop_event is set (or max_iterations).… (+15 more)

### Community 7 - "test_fit.py"
Cohesion: 0.11
Nodes (43): build_fit_system_blocks(), build_fit_user(), cached_fit(), _Dimension, evaluate_fit(), fit_context_block(), fit_is_current(), FitDecision (+35 more)

### Community 8 - "test_discovery.py"
Cohesion: 0.09
Nodes (42): load_targets(), Load and validate targets.yaml. Cached after first successful load., Decimal, build_discovery_plan(), DiscoveryConfig, DiscoverySource, _enabled_queries(), enabled_query_texts() (+34 more)

### Community 9 - "baseline.py"
Cohesion: 0.08
Nodes (42): collections, get_jobs_for_role(), Return recent jobs whose title matches any of the role title terms. Matching is…, build_role_baseline(), LLMClient, Role baseline builder: aggregate ~15-20 JDs into a role-optimized resume., Pull role JDs from the DB, aggregate skills, compile a baseline PDF, persist., Build a lightweight Job so existing selector APIs can rank bullets. (+34 more)

### Community 10 - "evaluate"
Cohesion: 0.15
Nodes (29): evaluate(), Return whether a posting should proceed to scoring., Classify a JD's stance on visa sponsorship without a profile dependency.…, sponsorship_signal(), _posting(), MonkeyPatch, Tests for the negative pre-filter., international' must not satisfy the intern word-boundary gate. (+21 more)

### Community 11 - "FakeTransport"
Cohesion: 0.15
Nodes (17): decode_callback(), BaseException, Decode callback_data into (action, job_id)., Retry transport errors and HTTP 5xx; never retry 4xx client errors., _should_retry_telegram(), FakeTransport, Any, Path (+9 more)

### Community 12 - "get_job_by_source_id"
Cohesion: 0.18
Nodes (23): get_job_by_source_id(), _role_classification_current(), classification_is_current(), classify_role(), True when the stored label was produced for this exact description., Classify the role from the posting. Discovery labels are not copied across., _apply_role_classification(), Label the role from the normalized JD. Does not change job status. (+15 more)

### Community 13 - "textclean.py"
Cohesion: 0.07
Nodes (41): How to read it, Limits, Phase 3 discovery coverage, What a number means, Flow, Hash and upsert, Limits, Normalization (+33 more)

### Community 14 - "test_apply_url.py"
Cohesion: 0.20
Nodes (19): _ensure_tenant(), Stamp job.tenant from the Workday URL when missing (LinkedIn→Workday case)., ApplyKind, classify_apply_url(), _host(), is_automateable_apply_url(), is_workday_url(), StrEnum (+11 more)

### Community 15 - "job_identity.py"
Cohesion: 0.06
Nodes (68): _assign_canonical_url(), _find_cross_source_job(), Another source's row for this posting. Same-source ids are never folded…, canonicalize_job_url(), _is_tracking_param(), locations_agree(), locations_conflict(), normalize_title() (+60 more)

### Community 16 - "eligibility.py"
Cohesion: 0.16
Nodes (31): _ask_model(), _citizenship(), _clearance(), _current_student(), _dates(), _decision_from_job(), _dim(), DimensionResult (+23 more)

### Community 17 - "coverage.py"
Cohesion: 0.13
Nodes (28): build_coverage_report(), add_planned(), group_for(), GroupMetrics, _jsonable(), observe_search(), _planned_slots(), StrEnum (+20 more)

### Community 18 - "get_job_by_id"
Cohesion: 0.25
Nodes (23): handle_callback(), Handle one Telegram update containing a callback_query. Returns the resulting…, encode_callback(), StrEnum, Encode inline-keyboard callback_data: v1|<action>|<job_id> (<=64 bytes)., ReviewAction, get_job_by_id(), _callback_update() (+15 more)

### Community 19 - "Settings"
Cohesion: 0.16
Nodes (9): BaseSettings, Path, Central configuration for the job agent. Secrets and overrides come from…, Return an absolute path rooted at the project directory when relative., Fixed path for the candidate's personal resume PDF (default for applications)., Model id used for scoring. Always the OpenAI scorer., Model id used for outreach / open-ended answers. Always OpenAI., Ordered alternates for a primary model (Gemini only), excluding duplicates. (+1 more)

### Community 20 - "session_scope"
Cohesion: 0.10
Nodes (44): Data model (core/db.py), Status lifecycle, StrEnum, Set the portfolio weight from the classified family. Fit and status stay put., Insert a job or update mutable fields when the posting is already stored. The…, session_scope(), Source, _stamp_role_family_weight() (+36 more)

### Community 21 - "TelegramClient"
Cohesion: 0.13
Nodes (12): HttpxTransport, Any, Path, Protocol, retry, High-level Telegram helpers used by review / handlers / poller., Configured default chat id (may be None until set in .env)., Edit a text message. Outcome cards are text, not photos. (+4 more)

### Community 22 - "pipeline.py"
Cohesion: 0.17
Nodes (14): Orchestration package (Step 7)., _benchmark_tier_one_stage(), PipelineSummary, _prepare_shortlisted_resumes(), Any, Full pipeline: ingest, score, shortlist, resume, suggest, prep, apply, reviews., Auto-discover + benchmark Tier-1 staged jobs (LinkedIn scrape, gated)., Run all pipeline stages sequentially with per-stage isolation. A failure in one… (+6 more)

### Community 23 - "get_settings"
Cohesion: 0.06
Nodes (63): What still needs the user (before live runs), apscheduler_schedulers_asyncio, apscheduler_triggers_cron, asyncio, launch_context(), _new_context(), new_page(), Page (+55 more)

### Community 24 - "workday_rest.py"
Cohesion: 0.11
Nodes (35): Response, _as_text(), _company_name(), _one(), _fetch_detail(), _fetch_listing_page(), fetch_workday(), _is_recent_posted_on() (+27 more)

### Community 25 - "role_classify.py"
Cohesion: 0.29
Nodes (12): _deterministic(), _ModelLabel, _parse_model(), BaseModel, Classify what a job is. This does not score whether the candidate should apply., Keep technology strategy, technology consulting, and product marketing apart., Return (classification, needs_llm). needs_llm is unused when classification is…, _result() (+4 more)

### Community 26 - "linkedin_jobspy.py"
Cohesion: 0.18
Nodes (21): math, PlannedSearch, _dataframe_to_postings(), _effective_windows(), _explicit_company_url(), _external_id(), fetch_linkedin_indeed(), _google_search_term() (+13 more)

### Community 27 - "bot/__init__.py"
Cohesion: 0.13
Nodes (24): Telegram review bot (Step 6)., build_keyboard(), build_review_caption(), format_answers_message(), format_cover_letter_message(), Any, Build and send Telegram review cards for pending_review jobs., Follow-up text with the stored cover letter, if one was drafted. (+16 more)

### Community 28 - "Any"
Cohesion: 0.10
Nodes (18): AnthropicClient, _attempt(), _as_int(), _finish_reason(), GeminiClient, _attempt(), _lower_thinking(), _attempt() (+10 more)

### Community 29 - "test_pipeline_order_and_aggregation"
Cohesion: 0.13
Nodes (18): _FakeSummary, MonkeyPatch, test_pipeline_order_and_aggregation(), fake_alerts(), fake_apply(), fake_ingestion(), fake_outcomes(), fake_prep() (+10 more)

### Community 30 - "Tier"
Cohesion: 0.15
Nodes (25): Tier, _cmd_doctor(), compute_tier(), is_dream_company(), Dream-company match tolerant of legal suffixes ('Google' == 'Google LLC')., Deterministic tier from score + dream-company override (thresholds in settings)., _status_for_tier(), _job() (+17 more)

### Community 31 - "diff.py"
Cohesion: 0.08
Nodes (68): apply_decided_suggestions(), decide_suggestion(), _format_card(), Any, Telegram delivery and apply path for skill suggestions., If all suggestions for a job are decided, recompile resume with approvals.…, Mark a suggestion approved/rejected/edited and maybe recompile., Send Telegram cards for jobs with unsent pending suggestions. (+60 more)

### Community 32 - "build_scheduler"
Cohesion: 0.23
Nodes (14): AsyncIOScheduler, build_scheduler(), parse_hhmm(), Any, Parse 'HH:MM' into (hour, minute). Raises ValueError on bad input., Build (but do not start) an AsyncIOScheduler with one job per HH:MM. Jobs use…, _noop(), MonkeyPatch (+6 more)

### Community 33 - "profile.py"
Cohesion: 0.22
Nodes (8): _load_yaml(), Any, Path, Load and validate the grounded candidate profile from YAML., Clear cache and reload (useful after editing profile.yaml)., reload_profile(), datetime, pydantic

### Community 34 - "workday.py"
Cohesion: 0.10
Nodes (36): action_delay_bounds(), human_delay(), Locator, Human-like delay and typing helpers for browser automation., Return (min_ms, max_ms) for between-action pauses., Return (min_ms, max_ms) for per-keystroke typing delay., Sleep a jittered duration; return the seconds slept., Clear and type text with per-keystroke jitter (accessibility-friendly). (+28 more)

### Community 35 - "alerts.py"
Cohesion: 0.20
Nodes (16): AlertSummary, build_alert_caption(), Telegram alerts for blocked / errored jobs (not pending_review cards)., Caption for a blocker / error alert., Notify on unsent manual_review / error jobs (screenshot + reason)., _send_one(), send_pending_alerts(), get_unsent_alerts() (+8 more)

### Community 36 - "Remaining Manual Setup"
Cohesion: 0.08
Nodes (24): 2a. Find a Workday URL, 2b. Edit `config/targets.yaml`, 3a. Run the save-session helper, 3b. What you do in the browser, 4a. Discover jobs (LinkedIn / Indeed + any real Workday tenants), 4b. Score with Gemini, 4c. Attach your base resume to staged jobs, 4d. Send LinkedIn/Indeed application prep pack (Telegram) (+16 more)

### Community 37 - "telegram.py"
Cohesion: 0.08
Nodes (49): _decision_caption(), _handle_outcome_callback(), _handle_suggest_callback(), Any, Dispatch Telegram callback_query decisions for pending_review jobs and skill…, Record a post-submit label. Does not change status or decided_at., Ack a callback_query; never raise (expired/fake IDs return Telegram 400)., Handle s1|approve|id / edit / reject suggestion callbacks. (+41 more)

### Community 38 - "test_prep_delivery.py"
Cohesion: 0.26
Nodes (21): Address, Education, Exclusions, Experience, Identity, Preferences, BaseModel, field_validator (+13 more)

### Community 39 - "ingest.py"
Cohesion: 0.10
Nodes (29): os, Classify an already-supplied company URL. Does not invent a domain., trustworthy_company_source(), CoverageReport, fail_unrecorded(), log_coverage(), Path, Internal discovery coverage. Not a share of the internship market. (+21 more)

### Community 40 - "test_recruiting_universe.py"
Cohesion: 0.39
Nodes (8): _family(), _jd(), Path, Marketing, technology strategy, MBA summer associate, and first discovery…, test_first_discovery_provenance_is_immutable(), test_marketing_is_separate_from_product_marketing_and_other(), test_mba_summer_associate_is_an_internship_signal(), test_technology_strategy_is_not_technology_consulting()

### Community 41 - "db.py"
Cohesion: 0.06
Nodes (56): async_sessionmaker, contextlib, _absolute_sqlite_url(), _company_name(), _dialect_name(), _ensure_job_columns(), finish_outcome_prompt(), get_engine() (+48 more)

### Community 42 - "test_pacing.py"
Cohesion: 0.06
Nodes (72): acquire(), AcquireResult, _clamp_multiplier(), _clock(), end_of_local_day(), gap_seconds(), is_pace_blocker(), note_pace_block() (+64 more)

### Community 43 - "_posting"
Cohesion: 0.29
Nodes (6): _posting(), Any, JDs often list a reachable minimum plus an aspirational 'preferred'., test_company_blocklist_does_not_match_lookalikes(), test_yoe_ceiling_follows_profile(), test_yoe_keeps_job_when_a_lower_band_is_reachable()

### Community 44 - "run_service"
Cohesion: 0.20
Nodes (9): _cmd_serve(), Event, Start the scheduler and (optionally) the Telegram poller until stopped.…, run_service(), MonkeyPatch, Path, Scheduler starts; preset stop_event exits cleanly with run_poller=False., test_run_service_stops_without_poller() (+1 more)

### Community 45 - "shortlist.py"
Cohesion: 0.15
Nodes (22): apply_shortlist(), _close_enough(), _company_key(), _company_ok(), config_hash(), _diversify(), _family(), _identity() (+14 more)

### Community 46 - "test_answers.py"
Cohesion: 0.19
Nodes (14): AnswerResolver, AnswerSource, StrEnum, Resolve form labels to answers; LLM only for open-ended unknowns., FakeAnswerClient, Any, Offline tests for AnswerResolver (deterministic + mock LLM)., test_cover_letter_field_uses_stored_text() (+6 more)

### Community 47 - "linkedin_people.py"
Cohesion: 0.22
Nodes (14): _heuristic_parse(), LLMClient, parse_profile(), parse_profile_json(), PeerProfileData, BaseModel, Protocol, LinkedIn people profile scrape + parse (authenticated session). Default posture… (+6 more)

### Community 48 - "test_prep_builder.py"
Cohesion: 0.11
Nodes (28): _answer_item(), build_job_section(), compile_prep_pdf(), generate_prep_pack(), PrepPackResult, Any, LLMClient, Path (+20 more)

### Community 49 - "test_base_resume.py"
Cohesion: 0.35
Nodes (12): pikepdf, _make_base_pdf(), _profile(), Path, Tests for static base resume preparation and on-demand Typst tailoring., Create a valid PDF via Typst to stand in for the user's base resume., _sample_job(), test_base_resume_file_property() (+4 more)

### Community 50 - "pytest"
Cohesion: 0.10
Nodes (20): pytest, build_baseline_resume_data(), _normalize(), Any, Assemble Typst resume JSON from an aggregated role skill profile., AggregatedSkill, BaseModel, A skill summarized across many JDs for one target role. (+12 more)

### Community 51 - "test_phase0_baseline.py"
Cohesion: 0.18
Nodes (16): _enable_internship_only(), _posting(), Any, MonkeyPatch, parametrize, Phase 0 locks: profile facts, experience span, internship gate, sponsorship., test_experience_span_is_about_five_years_and_not_summed(), test_friendly_sponsorship_stays_eligible() (+8 more)

### Community 52 - "Phase 5 role classification"
Cohesion: 0.29
Nodes (6): Inputs, Limits, Output, Phase 5 role classification, Taxonomy, When it runs again

### Community 53 - "AGENTS.md"
Cohesion: 0.22
Nodes (7): Build order and status, Coding conventions, Commands, Confirmed product decisions, Project, Repository layout, Workflow for implementing a step

### Community 54 - "Job Agent"
Cohesion: 0.13
Nodes (14): Application prep packs (LinkedIn / Indeed), Job Agent, Layout, LinkedIn peer benchmarking (optional, off by default), Resumes (Step 4), Run automation (Step 5), Run ingestion (Step 2), Run review bot (Step 6) (+6 more)

### Community 55 - "_build_doctor_report"
Cohesion: 0.36
Nodes (8): _build_doctor_report(), _count_jobs(), _print_doctor_report(), Any, First element of a row tuple; scalars pass through., Read-only pipeline health snapshot. No LLM calls., Human-readable health report. JSON mode prints the dict instead., _unwrap()

### Community 56 - "answers.py"
Cohesion: 0.14
Nodes (19): _discovery_channel(), is_open_ended(), _latest_education(), _matches(), needs_human_review(), _norm(), Any, Map Workday form questions to profile facts or LLM-drafted answers. (+11 more)

### Community 57 - "Phase 2 search taxonomy"
Cohesion: 0.50
Nodes (3): Ambiguous phrases, Phase 2 search taxonomy, What was added

### Community 58 - "Benchmark — Product Manager @ T-Mobile"
Cohesion: 0.33
Nodes (5): Benchmark — Product Manager @ T-Mobile, Dimensions, Gaps, Recommendations, Strengths

### Community 59 - "automation/__init__.py"
Cohesion: 0.15
Nodes (10): one(), answers_to_payload(), Resolve questions concurrently, preserving input order., Persistable JSON blob for Job.application_answers., ResolvedAnswer, Workday application automation (Step 5)., ApplySummary, Pre-fill a Workday application and pause at the review screen. (+2 more)

### Community 60 - "json"
Cohesion: 0.15
Nodes (22): effective_baseline(), effective_config_hash(), profile_hash(), public_config(), Any, Path, Secret-free snapshot of the candidate profile version and effective config. The…, SHA-256 of the parsed profile facts. Comments and key order do not matter. (+14 more)

### Community 61 - "LLMClient"
Cohesion: 0.14
Nodes (15): LLMClient, Protocol, Minimal async LLM interface (mockable for offline tests)., profile_vec(), _attach_priority(), _JobOutcome, Record attention order. A failure here does not change fit, tier, or status., Score discovered jobs and persist tiered results. (+7 more)

### Community 62 - ".total_years_experience"
Cohesion: 0.50
Nodes (4): _parse_month(), date, Approximate career length in years, spanning earliest start to latest end., Parse 'YYYY-MM' / 'YYYY'; 'Present' and unparseable values return None.

### Community 63 - "test_cover_letter.py"
Cohesion: 0.16
Nodes (16): cap_cover_letter(), _fallback_cover_letter(), generate_cover_letter(), Trim to the last sentence that fits, so a runaway letter stays usable., Deterministic letter used when the model keeps failing the style gate., Draft a short cover letter; retry once if banned words appear., build_cover_letter_user(), User prompt for a Tier-1 cover letter. Phrase is matched by test fakes. (+8 more)

### Community 64 - "OpenAIEmbedder"
Cohesion: 0.38
Nodes (4): OpenAIEmbedder, Any, OpenAI embeddings. Width is ``vector_dimensions``., _vectors_from_response()

### Community 65 - "test_company_intelligence.py"
Cohesion: 0.06
Nodes (72): CompanyIntelligence, get_recently_applied_companies(), Companies we submitted to within the cooldown window. Statuses included:…, Factual employer record shared by jobs. Not a score and not a preference., httpx, _accumulate_sources(), _apply_facts(), attach_company_intelligence() (+64 more)

### Community 66 - "priority.py"
Cohesion: 0.23
Nodes (21): _as_utc(), _components(), dream_company_component(), eligibility_component(), fit_component(), freshness_component(), _freshness_day(), _input_hash() (+13 more)

### Community 67 - "Phase 1 discovery architecture"
Cohesion: 0.10
Nodes (23): 40/40/15/5 priority model, Current problem, New architecture, Phase 1 discovery architecture, Provenance, Purpose, Role families, Search allocation (+15 more)

### Community 68 - "prep.py"
Cohesion: 0.11
Nodes (30): _load_scored(), _mark_sent(), PrepSummary, datetime, LLMClient, Generate and deliver LinkedIn/Indeed application prep packs via Telegram., One text file for the run. Empty input sends nothing., Build and send a prep pack for unsent staged LinkedIn/Indeed jobs. Brief mode… (+22 more)

### Community 71 - "Phase 6 candidate fit"
Cohesion: 0.33
Nodes (5): Dimensions, Not in this phase, Output, Phase 6 candidate fit, When the model is not called

### Community 72 - "token_optimizer.py"
Cohesion: 0.20
Nodes (13): approx_tokens(), cache_block(), compact_json_dumps(), minify_job(), Any, Payload compression, schema minification, and prompt-caching utilities., Build an Anthropic system content block with ephemeral prompt caching., Compact job description for scoring: title/company/location + cleaned JD. (+5 more)

### Community 73 - "test_role_weights.py"
Cohesion: 0.14
Nodes (26): functools, get_role_family_weight(), load_role_family_weights(), Strategic weight of a classified role family. Not fit and not search capacity., Load the portfolio weights. Raises if the file does not match Phase 5 families., Portfolio weight for a Phase 5 primary family. Missing or unknown names use…, Subfamilies use their primary family's weight. They do not have their own., _validate() (+18 more)

### Community 75 - "test_priority.py"
Cohesion: 0.16
Nodes (27): apply_priority(), calculate_priority(), _combine(), load_priority_config(), priority_is_current(), PriorityDecision, Portfolio weight scaled so the top family is 100. Not a fit score., Rank one stored job. Does not write the row and does not change fit. (+19 more)

### Community 76 - "Phase 0 baseline"
Cohesion: 0.22
Nodes (8): Candidate baseline, Discovery baseline, Local versus production, Phase 0 baseline, Production baseline, Scoring baseline, Sponsorship behavior locked by tests, Tests

### Community 77 - "test_scorer.py"
Cohesion: 0.14
Nodes (22): contains_banned(), _fallback_outreach(), generate_outreach(), Tier-1 alumni/referral outreach drafting with anti-AI style gate., Return banned phrases present as whole words (case-insensitive)., Drop sentences that contain banned words; keep the rest., Draft a 3-sentence outreach note; retry once if banned words appear., Deterministic, profile-grounded note used when the model keeps failing the gate. (+14 more)

### Community 78 - "test_phase13_shortlist.py"
Cohesion: 0.36
Nodes (13): Pick staged jobs in Phase 12 order. Does not write status or priority., select_shortlist(), _config(), _job(), Any, Review-queue selection. It orders staged jobs and does not discard the rest., test_apply_shortlist_is_idempotent_and_preserves_scores(), test_family_diversity_is_a_soft_swap() (+5 more)

### Community 79 - "Phase 9 visa and eligibility"
Cohesion: 0.25
Nodes (7): Cache and storage, Education, graduation, experience, location, dates, Phase 9 visa and eligibility, Sponsorship, citizenship, and clearance, States, What the profile contributes, What this phase does not do

### Community 80 - "compiler.py"
Cohesion: 0.09
Nodes (43): load_profile(), Load and validate profile.yaml. Cached after first successful load., copy, get_jobs_by_status(), Return jobs with the given status, oldest first., apply_fit_caps(), _baseline_pdf_for_job(), clean_name() (+35 more)

### Community 81 - "filters.py"
Cohesion: 0.11
Nodes (29): citizenship_restriction(), _clearance_clauses(), clearance_requirement(), evaluate_job(), FilterResult, _haystack(), location_acceptable(), _location_ok() (+21 more)

### Community 82 - "test_resume.py"
Cohesion: 0.12
Nodes (32): compile_resume(), Compile a tailored resume PDF for one job; return absolute path., build_resume_data(), extract_job_terms(), _grounded_summary(), Any, RankedBullet, Deterministic JD-aware bullet and skill selection for resume tailoring. (+24 more)

### Community 83 - "Job"
Cohesion: 0.13
Nodes (21): RuntimeError, Raised when no reusable storage_state exists for a tenant., SessionMissingError, Path, Reopen saved session, reach review, click Submit once., SubmitResult, WorkdaySubmitter, _incoming_description_unusable() (+13 more)

### Community 84 - "benchmark/engine.py"
Cohesion: 0.17
Nodes (21): BenchmarkReport, BenchmarkSummary, build_benchmark(), _derive_seniority(), DimensionScore, _education_rank(), _median(), _norm() (+13 more)

### Community 85 - "test_main_cli.py"
Cohesion: 0.14
Nodes (11): Offline tests for main.py CLI routing., test_default_command_is_serve(), test_doctor_cli(), test_poll_invokes_run_polling(), test_prep_pack_cli(), test_run_once_invokes_pipeline(), test_send_reviews_invokes_once(), test_serve_invokes_run_service() (+3 more)

### Community 86 - "scrape_profile"
Cohesion: 0.24
Nodes (11): auto_discover_peers(), _crawl(), _detect_blocker(), Any, Path, Navigate to a LinkedIn profile URL and extract visible text sections., Crawl LinkedIn People Search for peers matching this job's title. Requires…, _require_enabled() (+3 more)

### Community 87 - "test_linkedin_people.py"
Cohesion: 0.24
Nodes (9): discover_peers(), parse_profile_html(), Offline-friendly extraction from saved HTML (tests / fixtures)., Return peer profile URLs. Semi-automated by default: caller supplies explicit…, asyncio, Offline tests for LinkedIn profile HTML parse and peer discovery., test_discover_peers_semi_auto(), test_parse_profile_heuristic_without_client() (+1 more)

### Community 88 - "Phase 7 role-family weighting"
Cohesion: 0.22
Nodes (8): Canonical portfolio, Configuration, Four different questions, Phase 7 role-family weighting, Unknown classification, What is stored, What this phase does not do, Where the family comes from

### Community 89 - "parse_score"
Cohesion: 0.22
Nodes (9): parse_score(), Extract compact {"s","t","r"} JSON from model output (tolerant)., A garbage score must error, not silently become 0 / Tier 3., test_parse_score_handles_braces_inside_strings(), test_parse_score_rejects_non_numeric_score(), test_parse_score_clamps(), test_parse_score_code_fenced(), test_parse_score_plain_json() (+1 more)

### Community 90 - "Phase 8 company intelligence"
Cohesion: 0.29
Nodes (6): Names and reuse, Phase 8 company intelligence, Schema, Sources, What it is, What this phase does not change

### Community 91 - "dataclasses"
Cohesion: 0.10
Nodes (30): Scoring specifics (Step 3), dataclasses, build_llm_client(), OpenAIClient, OpenAI Chat Completions client. JSON scoring uses json_object mode., Scoring and writing always go through OpenAI., _FakeAio, _FakeAsyncModels (+22 more)

### Community 93 - "db_ready"
Cohesion: 0.20
Nodes (14): Testing conventions, db_ready(), _disable_apply_pacing(), _disable_vector_gate(), _internship_only_off(), fixture, MonkeyPatch, Path (+6 more)

### Community 94 - "3. Hard filters (before any model)"
Cohesion: 0.18
Nodes (11): 3.10 What a survivor looks like, 3.1 Company blocklist, 3.2 Exclusion keywords, 3.3 Clearance language, 3.4 Staffing agencies, 3.5 Internship gate, 3.6 Seniority filter (separate from the internship gate), 3.7 Years of experience (+3 more)

### Community 95 - "test_linkedin_discover.py"
Cohesion: 0.31
Nodes (8): build_people_search_url(), extract_profile_urls(), Build a LinkedIn People Search URL from role keywords., Pull unique /in/ profile URLs from a search-results HTML dump., Tests for LinkedIn people-search URL building and profile URL extraction., test_build_people_search_url_encodes_keywords(), test_extract_profile_urls_dedupes_and_caps(), test_extract_profile_urls_empty()

### Community 97 - "scorer/__init__.py"
Cohesion: 0.20
Nodes (9): ScoreSummary, LLM match evaluator with tier triage and Tier-1 outreach., Evaluation, BaseModel, field_validator, Pydantic schemas for LLM scoring output., Tolerant raw score payload from the model: {"s","t","r"}., Normalized evaluation ready to persist on a Job row. (+1 more)

### Community 98 - "scorer/engine.py"
Cohesion: 0.09
Nodes (38): re, _cache_path(), clears_threshold(), cosine(), jd_vector(), job_embed_text(), load_profile_embedding(), profile_hash() (+30 more)

### Community 99 - "sort_by_priority"
Cohesion: 0.29
Nodes (7): Configuration, Phase 13 shortlist, Pipeline, Selection, Highest priority first. Fit, then recency, then id break ties., sort_by_priority(), posted()

### Community 100 - "Embedder"
Cohesion: 0.29
Nodes (6): Tech stack, build_embedder(), Embedder, Protocol, OpenAI embedder when the gate is on and a key is set. Otherwise ``None``., Batch embedder. Result length matches ``texts``.

### Community 101 - "5. How fit is scored"
Cohesion: 0.22
Nodes (8): Compact, cacheable candidate summary for LLM system prompts (Step 3)., 10. File map, 5.1 What the model is, 5.2 The two inputs, 5.3 The rubric, verbatim in meaning, 5.4 What the code does with the score, 5.5 What a number means, 5. How fit is scored

### Community 102 - "main.py"
Cohesion: 0.17
Nodes (19): argparse, ArgumentParser, _eligible(), Workday source OR any source whose URL is a Workday company apply link., build_parser(), _cmd_benchmark(), _cmd_build_baseline(), _cmd_list_apply() (+11 more)

### Community 103 - "SQLModel"
Cohesion: 0.33
Nodes (6): persist_peer_profile(), Benchmark, PeerProfile, SQLModel, Parsed LinkedIn profile used for peer benchmarking., Benchmark of the candidate vs peers for one job.

### Community 104 - "How jobs are found, filtered, scored, and sent"
Cohesion: 0.25
Nodes (7): 1. What a run is, 4.1 Pre-score rank (`prerank_score`), 4.2 Embedding gate (this does drop jobs), 4.3 Fit-model cap, 4. How results are prioritised today, 7. Statuses, in one pass, How jobs are found, filtered, scored, and sent

### Community 105 - "has_internship_signal"
Cohesion: 0.40
Nodes (6): has_internship_signal(), datetime, True for intern titles and controlled MBA summer-associate titles. The word…, Title phrases that count as internships when the word 'intern' is absent., _soft_internship_signals(), test_internship_signal_matches_the_existing_gate()

### Community 106 - "2. Where jobs come from"
Cohesion: 0.29
Nodes (7): 2.1 Search terms, 2.2 Sites and the exact JobSpy arguments, 2.3 How each site treats "posted in the last 36 hours", 2.4 What is kept from a JobSpy row, 2.5 Workday, separately from LinkedIn, 2.6 Save and dedupe, 2. Where jobs come from

### Community 107 - "8. The weight discussion (not built)"
Cohesion: 0.33
Nodes (6): 8.1 What you asked for, 8.2 Decisions you agreed with, 8.3 A weight table we used as a sketch, 8.4 What we said the rubric should do for career-switch roles, 8.5 How that would sit on the current pipeline, 8. The weight discussion (not built)

### Community 108 - "9. Pain points we have actually hit or spelled out"
Cohesion: 0.33
Nodes (6): 9.1 Discovery, 9.2 Filters, 9.3 Scoring, 9.4 What you receive, 9.5 Operations, 9. Pain points we have actually hit or spelled out

### Community 109 - "logging.py"
Cohesion: 0.40
Nodes (4): configure_logging(), Central structlog configuration., Configure structlog + stdlib logging once at process start. Console renderer…, sys

### Community 110 - "6. What is sent to you"
Cohesion: 0.40
Nodes (5): 6.1 Who is eligible, 6.2 The shortlist rule, 6.3 Each line, 6.4 If brief mode is turned off, 6. What is sent to you

### Community 111 - "Phase 12 priority ranking"
Cohesion: 0.50
Nodes (3): Components, Phase 12 priority ranking, Version

### Community 112 - "FakeClient"
Cohesion: 0.40
Nodes (3): FakeClient, Any, Return different skills for baseline JDs vs the target posting.

### Community 113 - "BlockerError"
Cohesion: 0.50
Nodes (3): BlockerError, RuntimeError, LinkedIn checkpoint / login wall / Cloudflare detected.

## Knowledge Gaps
- **133 isolated node(s):** `job-agent`, `ScrapeSummary`, `_Sites`, `_FakeAio`, `Project` (+128 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 882 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **7 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Job` connect `Job` to `RawPosting`, `test_vector_gate.py`, `Profile`, `poller.py`, `test_fit.py`, `baseline.py`, `get_job_by_source_id`, `test_apply_url.py`, `job_identity.py`, `eligibility.py`, `get_job_by_id`, `session_scope`, `get_settings`, `bot/__init__.py`, `Tier`, `diff.py`, `workday.py`, `alerts.py`, `telegram.py`, `test_prep_delivery.py`, `ingest.py`, `db.py`, `test_pacing.py`, `shortlist.py`, `test_answers.py`, `test_prep_builder.py`, `test_base_resume.py`, `pytest`, `_build_doctor_report`, `answers.py`, `automation/__init__.py`, `LLMClient`, `test_cover_letter.py`, `test_company_intelligence.py`, `priority.py`, `prep.py`, `token_optimizer.py`, `test_role_weights.py`, `test_priority.py`, `test_scorer.py`, `test_phase13_shortlist.py`, `compiler.py`, `filters.py`, `test_resume.py`, `benchmark/engine.py`, `scorer/engine.py`, `sort_by_priority`, `main.py`, `SQLModel`?**
  _High betweenness centrality (0.161) - this node is a cross-community bridge._
- **Why does `get_settings()` connect `get_settings` to `test_webhook.py`, `test_vector_gate.py`, `Profile`, `targets.py`, `clients.py`, `poller.py`, `baseline.py`, `evaluate`, `textclean.py`, `job_identity.py`, `Settings`, `session_scope`, `TelegramClient`, `pipeline.py`, `Any`, `Tier`, `diff.py`, `build_scheduler`, `workday.py`, `telegram.py`, `test_prep_delivery.py`, `test_recruiting_universe.py`, `db.py`, `test_pacing.py`, `run_service`, `test_answers.py`, `linkedin_people.py`, `test_prep_builder.py`, `test_base_resume.py`, `pytest`, `test_phase0_baseline.py`, `_build_doctor_report`, `answers.py`, `automation/__init__.py`, `json`, `LLMClient`, `test_cover_letter.py`, `OpenAIEmbedder`, `prep.py`, `token_optimizer.py`, `test_scorer.py`, `compiler.py`, `filters.py`, `test_resume.py`, `benchmark/engine.py`, `scrape_profile`, `test_linkedin_people.py`, `dataclasses`, `scorer/engine.py`, `Embedder`, `main.py`?**
  _High betweenness centrality (0.133) - this node is a cross-community bridge._
- **Why does `Profile` connect `Profile` to `test_vector_gate.py`, `targets.py`, `test_fit.py`, `baseline.py`, `evaluate`, `job_identity.py`, `eligibility.py`, `session_scope`, `get_settings`, `linkedin_jobspy.py`, `Tier`, `diff.py`, `profile.py`, `workday.py`, `test_prep_delivery.py`, `ingest.py`, `test_pacing.py`, `_posting`, `test_answers.py`, `test_prep_builder.py`, `test_base_resume.py`, `pytest`, `test_phase0_baseline.py`, `answers.py`, `automation/__init__.py`, `LLMClient`, `.total_years_experience`, `test_cover_letter.py`, `priority.py`, `prep.py`, `test_priority.py`, `test_scorer.py`, `Phase 9 visa and eligibility`, `compiler.py`, `filters.py`, `test_resume.py`, `benchmark/engine.py`, `scorer/engine.py`, `5. How fit is scored`, `has_internship_signal`?**
  _High betweenness centrality (0.117) - this node is a cross-community bridge._
- **Are the 124 inferred relationships involving `Job` (e.g. with `Data model (core/db.py)` and `AnswerResolver`) actually correct?**
  _`Job` has 124 INFERRED edges - model-reasoned connections that need verification._
- **Are the 197 inferred relationships involving `Profile` (e.g. with `AnswerResolver` and `_latest_education()`) actually correct?**
  _`Profile` has 197 INFERRED edges - model-reasoned connections that need verification._
- **Are the 122 inferred relationships involving `Status` (e.g. with `Data model (core/db.py)` and `ApplyRunner`) actually correct?**
  _`Status` has 122 INFERRED edges - model-reasoned connections that need verification._
- **Are the 110 inferred relationships involving `Source` (e.g. with `Data model (core/db.py)` and `_eligible()`) actually correct?**
  _`Source` has 110 INFERRED edges - model-reasoned connections that need verification._