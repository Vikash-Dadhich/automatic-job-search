# Graph Report - Automatic job search  (2026-09-25)

## Corpus Check
- 125 files · ~71,423 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 13 file(s) not represented in the graph (top: (none) 8, .typ 2, .mdc 1)

## Summary
- 1833 nodes · 6164 edges · 80 communities (77 shown, 3 thin omitted)
- Extraction: 89% EXTRACTED · 11% INFERRED · 0% AMBIGUOUS · INFERRED: 669 edges (avg confidence: 0.94)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `f4043dfb`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- main
- test_pipeline_order_and_aggregation
- compiler.py
- linkedin_people.py
- workday_rest.py
- clients.py
- Scorer
- telegram.py
- workday.py
- settings.py
- evaluate
- test_prep_builder.py
- scorer/engine.py
- models.py
- pathlib
- outreach.py
- max_acceptable_years
- suggest.py
- profile.py
- test_resume.py
- Job
- TelegramClient
- test_pacing.py
- vault.py
- handle_callback
- review.py
- linkedin_jobspy.py
- test_outcomes.py
- call_with_resilience
- Settings
- diff.py
- db.py
- answers.py
- test_llm_provider.py
- telemetry.py
- benchmark/engine.py
- Remaining Manual Setup
- test_scorer.py
- skills.py
- test_apply_url.py
- build_scheduler
- test_vector_gate.py
- FakeTransport
- WorkdaySubmitter
- Profile
- ingest.py
- runner.py
- AGENTS.md
- prep.py
- conftest.py
- get_settings
- test_webhook.py
- pacing.py
- parse_workday_url
- Job Agent
- typing
- baseline.py
- run_service
- Benchmark — Product Manager @ T-Mobile
- _request
- test_depleted_credits_fail_fast_without_fallback
- test_workday_pairing.py
- _load_yaml
- company_matches
- Tier
- filters.py
- apply_pending
- test_workday_locators.py
- webhook.py
- job-agent
- test_base_resume.py
- LLMBillingError
- FakeClient
- test_send_prep_pack_empty
- GeminiClient
- service.py
- scheduler.py
- is_pace_blocker
- .validate_grad_date

## God Nodes (most connected - your core abstractions)
1. `Job` - 214 edges
2. `Profile` - 171 edges
3. `session_scope()` - 148 edges
4. `get_settings()` - 146 edges
5. `Status` - 130 edges
6. `Source` - 119 edges
7. `get_job_by_id()` - 91 edges
8. `TelegramClient` - 76 edges
9. `upsert_job()` - 66 edges
10. `init_db()` - 58 edges

## Surprising Connections (you probably didn't know these)
- `Checklist (your remaining work)` --references--> `save_session()`  [INFERRED]
  SETUP.md → automation/login.py
- `Run review bot (Step 6)` --references--> `send_pending_alerts()`  [INFERRED]
  README.md → bot/alerts.py
- `Confirmed product decisions` --references--> `compile_for_job()`  [INFERRED]
  AGENTS.md → resume/compiler.py
- `What still needs the user (before live runs)` --references--> `save_session()`  [INFERRED]
  AGENTS.md → automation/login.py
- `Deploy with Docker` --references--> `save_session()`  [INFERRED]
  README.md → automation/login.py

## Import Cycles
- None detected.

## Communities (80 total, 3 thin omitted)

### Community 0 - "main"
Cohesion: 0.14
Nodes (18): ArgumentParser, build_parser(), _cmd_poll(), _cmd_prep_pack(), _cmd_send_reviews(), _cmd_webhook(), main(), Offline tests for main.py CLI routing. (+10 more)

### Community 1 - "test_pipeline_order_and_aggregation"
Cohesion: 0.15
Nodes (17): _FakeSummary, MonkeyPatch, Offline tests for orchestrator.pipeline (monkeypatched stages)., test_pipeline_order_and_aggregation(), fake_alerts(), fake_apply(), fake_ingestion(), fake_outcomes() (+9 more)

### Community 2 - "compiler.py"
Cohesion: 0.10
Nodes (44): load_profile(), Load and validate profile.yaml. Cached after first successful load., copy, apply_fit_caps(), _baseline_pdf_for_job(), clean_name(), compile_for_job(), compile_pending() (+36 more)

### Community 3 - "linkedin_people.py"
Cohesion: 0.07
Nodes (45): auto_discover_peers(), _crawl(), BlockerError, build_people_search_url(), _detect_blocker(), discover_peers(), extract_profile_urls(), _heuristic_parse() (+37 more)

### Community 4 - "workday_rest.py"
Cohesion: 0.14
Nodes (23): Skip placeholder tenants until the user fills real URLs., WorkdayTenant, httpx, _as_text(), _company_name(), _one(), fetch_workday(), _is_recent_posted_on() (+15 more)

### Community 5 - "clients.py"
Cohesion: 0.12
Nodes (26): dataclasses, _backoff_delay(), is_permanent_account_error(), is_transient(), LLMError, _lower_thinking(), _attempt(), BaseException (+18 more)

### Community 6 - "Scorer"
Cohesion: 0.10
Nodes (20): accept_or_reject(), _JobOutcome, Score discovered jobs and persist tiered results., Score a single job and optionally draft Tier-1 outreach and a cover letter., Score one job and persist; never raises (returns error outcome)., Score discovered jobs with bounded concurrency; optional early-stop., Scorer, run_one() (+12 more)

### Community 7 - "telegram.py"
Cohesion: 0.13
Nodes (24): AlertSummary, _decision_caption(), _handle_outcome_callback(), _handle_suggest_callback(), Any, Dispatch Telegram callback_query decisions for pending_review jobs and skill…, Record a post-submit label. Does not change status or decided_at., Ack a callback_query; never raise (expired/fake IDs return Telegram 400). (+16 more)

### Community 8 - "workday.py"
Cohesion: 0.15
Nodes (22): human_delay(), Sleep a jittered duration; return the seconds slept., click_by_role(), click_next(), _collect_labeled_fields(), detect_blocker(), _fill_field(), is_review_page() (+14 more)

### Community 9 - "settings.py"
Cohesion: 0.16
Nodes (15): Public config exports., Typed application settings loaded from environment / .env., load_targets(), _load_yaml(), Any, Path, Load and validate discovery targets (search terms + Workday tenants)., Load and validate targets.yaml. Cached after first successful load. (+7 more)

### Community 10 - "evaluate"
Cohesion: 0.16
Nodes (28): evaluate(), Return whether a posting should proceed to scoring., Classify a JD's stance on visa sponsorship without a profile dependency.…, sponsorship_signal(), _posting(), MonkeyPatch, Tests for the negative pre-filter., international' must not satisfy the intern word-boundary gate. (+20 more)

### Community 11 - "test_prep_builder.py"
Cohesion: 0.12
Nodes (28): _answer_item(), build_job_section(), compile_prep_pdf(), generate_prep_pack(), PrepPackResult, Any, LLMClient, Path (+20 more)

### Community 12 - "scorer/engine.py"
Cohesion: 0.10
Nodes (38): json, build_embedder(), _cache_path(), clears_threshold(), cosine(), Embedder, jd_vector(), job_embed_text() (+30 more)

### Community 13 - "models.py"
Cohesion: 0.17
Nodes (17): hashlib, Normalized intermediate posting model and Job mapping., Populate description_clean from HTML or existing text; return the value., content_hash(), extract_sections(), html_to_text(), _normalize_whitespace(), HTML → clean text and section extraction for token-efficient scoring. (+9 more)

### Community 14 - "pathlib"
Cohesion: 0.13
Nodes (25): What still needs the user (before live runs), asyncio, launch_context(), _new_context(), new_page(), Page, Path, Stealth Playwright browser context using saved Workday sessions. (+17 more)

### Community 15 - "outreach.py"
Cohesion: 0.12
Nodes (25): _city_state(), company_tokens(), contains_phrase(), is_remote_location(), location_matches(), normalize_text(), Shared matching + truncation helpers used by filters, scoring, and answers.…, True when a posting location satisfies one preference entry. Compares city and… (+17 more)

### Community 16 - "max_acceptable_years"
Cohesion: 0.15
Nodes (12): max_acceptable_years(), Highest demanded YOE still worth scoring, derived from the candidate., Reject only when every stated YOE requirement is out of reach. A JD often lists…, _yoe_reason(), _posting(), Any, JDs often list a reachable minimum plus an aspirational 'preferred'., Scores fine but always fails the outreach call. (+4 more)

### Community 17 - "suggest.py"
Cohesion: 0.11
Nodes (35): apply_decided_suggestions(), decide_suggestion(), _format_card(), Any, Telegram delivery and apply path for skill suggestions., If all suggestions for a job are decided, recompile resume with approvals.…, Mark a suggestion approved/rejected/edited and maybe recompile., Send Telegram cards for jobs with unsent pending suggestions. (+27 more)

### Community 18 - "profile.py"
Cohesion: 0.29
Nodes (19): Address, Education, Experience, Identity, Preferences, BaseModel, Load and validate the grounded candidate profile from YAML., WorkAuthorization (+11 more)

### Community 19 - "test_resume.py"
Cohesion: 0.14
Nodes (25): extract_job_terms(), _grounded_summary(), RankedBullet, Deterministic JD-aware bullet and skill selection for resume tailoring., Lowercase tokens + bigrams from title and cleaned description., Overlap score; matches that are also candidate skills weigh more., Pick top 4–6 verified bullets matching the job; regroup under experiences., JD-present skills first, then remaining profile skills. (+17 more)

### Community 20 - "Job"
Cohesion: 0.08
Nodes (71): Data model (core/db.py), Status lifecycle, _ensure_tenant(), Stamp job.tenant from the Workday URL when missing (LinkedIn→Workday case)., build_alert_caption(), Telegram alerts for blocked / errored jobs (not pending_review cards)., Caption for a blocker / error alert., Notify on unsent manual_review / error jobs (screenshot + reason). (+63 more)

### Community 21 - "TelegramClient"
Cohesion: 0.13
Nodes (12): HttpxTransport, Any, Path, Protocol, retry, High-level Telegram helpers used by review / handlers / poller., Configured default chat id (may be None until set in .env)., Edit a text message. Outcome cards are text, not photos. (+4 more)

### Community 22 - "test_pacing.py"
Cohesion: 0.23
Nodes (19): _as_utc(), SQLite returns naive datetimes; attach UTC before any comparison., _Applicator, _enable(), MonkeyPatch, Workday apply throttle: classifier, AIMD, blackout, and runner wiring., _row(), _seed() (+11 more)

### Community 23 - "vault.py"
Cohesion: 0.15
Nodes (24): CredentialsFile, get_tenant_credentials(), has_saved_session(), load_credentials(), _load_yaml(), Any, BaseModel, Path (+16 more)

### Community 24 - "handle_callback"
Cohesion: 0.29
Nodes (17): handle_callback(), Handle one Telegram update containing a callback_query. Returns the resulting…, SubmitResult, ReviewAction, _callback_update(), FakeSubmitter, Any, Path (+9 more)

### Community 25 - "review.py"
Cohesion: 0.13
Nodes (23): build_keyboard(), build_review_caption(), format_answers_message(), format_cover_letter_message(), Any, Build and send Telegram review cards for pending_review jobs., Follow-up text with the stored cover letter, if one was drafted., Send Telegram review cards for unsent pending_review jobs. (+15 more)

### Community 26 - "linkedin_jobspy.py"
Cohesion: 0.20
Nodes (17): math, _dataframe_to_postings(), _effective_windows(), _external_id(), fetch_linkedin_indeed(), _google_search_term(), _location_matches(), _parse_posted_at() (+9 more)

### Community 27 - "test_outcomes.py"
Cohesion: 0.11
Nodes (35): build_outcome_keyboard(), button(), OutcomePromptSummary, Any, Telegram outcome keyboards for jobs that were actually submitted., Backfill outcome keyboards for submitted jobs that never got one., Two-row keyboard. Callbacks stay well under Telegram's 64-byte cap., Send one outcome keyboard. Never raises. False when the claim loses or send… (+27 more)

### Community 28 - "call_with_resilience"
Cohesion: 0.14
Nodes (13): AnthropicClient, _attempt(), _as_int(), call_with_resilience(), _finish_reason(), _attempt(), Any, Run attempt_fn(model) across candidate models, retrying transient errors. Each… (+5 more)

### Community 29 - "Settings"
Cohesion: 0.22
Nodes (7): BaseSettings, Path, Central configuration for the job agent. Secrets and overrides come from…, Return an absolute path rooted at the project directory when relative., Fixed path for the candidate's personal resume PDF (default for applications)., Ordered alternates for a primary model (Gemini only), excluding duplicates., Settings

### Community 30 - "diff.py"
Cohesion: 0.13
Nodes (33): StrEnum, SkillPlacement, SkillProvenance, apply_approved_suggestions_to_resume_data(), _baseline_skill_keys(), classify_provenance(), diff_against_baseline(), diff_against_baseline_async() (+25 more)

### Community 31 - "db.py"
Cohesion: 0.06
Nodes (51): async_sessionmaker, _absolute_sqlite_url(), Benchmark, _company_name(), _dialect_name(), _ensure_job_columns(), get_engine(), get_session_factory() (+43 more)

### Community 32 - "answers.py"
Cohesion: 0.05
Nodes (58): AnswerResolver, one(), answers_to_payload(), AnswerSource, _discovery_channel(), is_open_ended(), _latest_education(), _matches() (+50 more)

### Community 33 - "test_llm_provider.py"
Cohesion: 0.11
Nodes (22): Tech stack, build_llm_client(), OpenAIClient, OpenAI Chat Completions client. JSON scoring uses json_object mode., Scoring and writing always go through OpenAI., _FakeAio, _FakeAsyncModels, _FakeCandidate (+14 more)

### Community 34 - "telemetry.py"
Cohesion: 0.16
Nodes (16): action_delay_bounds(), Locator, Human-like delay and typing helpers for browser automation., Return (min_ms, max_ms) for between-action pauses., Return (min_ms, max_ms) for per-keystroke typing delay., Clear and type text with per-keystroke jitter (accessibility-friendly)., type_like_human(), typing_delay_bounds() (+8 more)

### Community 35 - "benchmark/engine.py"
Cohesion: 0.17
Nodes (19): BenchmarkReport, BenchmarkSummary, build_benchmark(), _derive_seniority(), DimensionScore, _education_rank(), _median(), _norm() (+11 more)

### Community 36 - "Remaining Manual Setup"
Cohesion: 0.08
Nodes (25): 2a. Find a Workday URL, 2b. Edit `config/targets.yaml`, 3a. Run the save-session helper, 3b. What you do in the browser, 4a. Discover jobs (LinkedIn / Indeed + any real Workday tenants), 4b. Score with Gemini, 4c. Attach your base resume to staged jobs, 4d. Send LinkedIn/Indeed application prep pack (Telegram) (+17 more)

### Community 37 - "test_scorer.py"
Cohesion: 0.09
Nodes (35): approx_tokens(), cache_block(), compact_json_dumps(), minify_job(), Any, Payload compression, schema minification, and prompt-caching utilities., Build an Anthropic system content block with ephemeral prompt caching., Compact job description for scoring: title/company/location + cleaned JD. (+27 more)

### Community 38 - "skills.py"
Cohesion: 0.10
Nodes (33): collections, aggregate_role_skills(), AggregatedSkill, _categorize(), extract_top_skills(), extract_top_skills_deterministic(), parse_skills_json(), BaseModel (+25 more)

### Community 39 - "test_apply_url.py"
Cohesion: 0.20
Nodes (19): ApplyKind, classify_apply_url(), _host(), is_automateable_apply_url(), is_workday_url(), StrEnum, Classify job apply URLs (Workday vs LinkedIn listing vs other company ATS)., Where the candidate actually applies. (+11 more)

### Community 40 - "build_scheduler"
Cohesion: 0.23
Nodes (14): AsyncIOScheduler, build_scheduler(), parse_hhmm(), Any, Parse 'HH:MM' into (hour, minute). Raises ValueError on bad input., Build (but do not start) an AsyncIOScheduler with one job per HH:MM. Jobs use…, _noop(), MonkeyPatch (+6 more)

### Community 41 - "test_vector_gate.py"
Cohesion: 0.22
Nodes (27): profile_embed_text(), Head of the cacheable candidate block. Same cap as a job description., Module-level entry point used by README / Step 7., score_pending(), FakeClient, Any, Deterministic LLM stand-in for offline tests., __init__() (+19 more)

### Community 42 - "FakeTransport"
Cohesion: 0.14
Nodes (19): decode_callback(), encode_callback(), BaseException, Encode inline-keyboard callback_data: v1|<action>|<job_id> (<=64 bytes)., Decode callback_data into (action, job_id)., Retry transport errors and HTTP 5xx; never retry 4xx client errors., _should_retry_telegram(), FakeTransport (+11 more)

### Community 43 - "WorkdaySubmitter"
Cohesion: 0.18
Nodes (14): RuntimeError, Raised when no reusable storage_state exists for a tenant., SessionMissingError, Path, Reopen saved session, reach review, click Submit once., WorkdaySubmitter, contextlib, MonkeyPatch (+6 more)

### Community 44 - "Profile"
Cohesion: 0.20
Nodes (21): Profile, Single Source of Truth for candidate facts. No LLM invention beyond this., Clear cache and reload (useful after editing profile.yaml)., reload_profile(), prerank_jobs(), prerank_score(), Deterministic, LLM-free pre-rank to order jobs before scoring. Recall/cost…, Return jobs ordered best-first by ``prerank_score`` (stable on ties). (+13 more)

### Community 45 - "ingest.py"
Cohesion: 0.17
Nodes (21): _dedupe(), IngestSummary, Ingestion orchestrator: fetch → clean → filter → upsert., Run one full discovery cycle and persist results., run_ingestion(), Job discovery scrapers (LinkedIn/Indeed via JobSpy, Workday CXS REST)., hash_fallback(), BaseModel (+13 more)

### Community 46 - "runner.py"
Cohesion: 0.14
Nodes (17): Workday application automation (Step 5)., ApplyRunner, ApplySummary, _eligible(), datetime, Random, Batch runner: staged Workday-eligible jobs -> pending_review (or…, Workday source OR any source whose URL is a Workday company apply link. (+9 more)

### Community 47 - "AGENTS.md"
Cohesion: 0.10
Nodes (15): Build order and status, Coding conventions, Commands, Confirmed product decisions, Project, Repository layout, Scoring specifics (Step 3), Workflow for implementing a step (+7 more)

### Community 48 - "prep.py"
Cohesion: 0.15
Nodes (23): _load_scored(), _mark_sent(), PrepSummary, datetime, LLMClient, Generate and deliver LinkedIn/Indeed application prep packs via Telegram., One text file for the run. Empty input sends nothing., Build and send a prep pack for unsent staged LinkedIn/Indeed jobs. Brief mode… (+15 more)

### Community 49 - "conftest.py"
Cohesion: 0.18
Nodes (16): Testing conventions, collections_abc, Dispose the global engine (used by tests to switch DATABASE_URL)., reset_engine(), db_ready(), _disable_apply_pacing(), _disable_vector_gate(), fixture (+8 more)

### Community 50 - "get_settings"
Cohesion: 0.09
Nodes (37): argparse, persist_peer_profile(), Build and persist a benchmark for one job. When scrape=False (default in…, run_benchmark(), get_settings(), Cached settings singleton., get_jobs_by_status(), get_recently_applied_companies() (+29 more)

### Community 51 - "test_webhook.py"
Cohesion: 0.26
Nodes (11): fastapi_testclient, TestClient, client(), fixture, MonkeyPatch, Offline tests for FastAPI Telegram webhook., test_health(), test_webhook_ignored_without_callback() (+3 more)

### Community 52 - "pacing.py"
Cohesion: 0.15
Nodes (22): acquire(), AcquireResult, _clamp_multiplier(), _clock(), end_of_local_day(), gap_seconds(), note_pace_block(), note_success() (+14 more)

### Community 53 - "parse_workday_url"
Cohesion: 0.14
Nodes (14): parse_workday_url(), BaseModel, field_validator, Extract tenant, shard, and site from a Workday careers / job deep link. Walks…, SearchConfig, WorkdayParts, Tests for Workday URL parsing and targets loading., test_load_targets_defaults() (+6 more)

### Community 54 - "Job Agent"
Cohesion: 0.13
Nodes (14): Application prep packs (LinkedIn / Indeed), Job Agent, Layout, LinkedIn peer benchmarking (optional, off by default), Resumes (Step 4), Run automation (Step 5), Run ingestion (Step 2), Run review bot (Step 6) (+6 more)

### Community 55 - "typing"
Cohesion: 0.15
Nodes (16): process_updates(), Any, Event, Long-polling loop for Telegram callback_query updates., Route a batch of updates; return the next offset (last update_id + 1)., Long-poll Telegram getUpdates until stop_event is set (or max_iterations).…, run_polling(), Protocol (+8 more)

### Community 56 - "baseline.py"
Cohesion: 0.13
Nodes (25): get_jobs_for_role(), get_role_baseline_by_role(), Per-role baseline resume built from aggregating ~15-20 JDs., Return recent jobs whose title matches any of the role title terms. Matching is…, RoleBaseline, build_baseline_resume_data(), build_role_baseline(), _normalize() (+17 more)

### Community 57 - "run_service"
Cohesion: 0.19
Nodes (10): _cmd_serve(), Event, Start the scheduler and (optionally) the Telegram poller until stopped.…, run_service(), MonkeyPatch, Path, Offline tests for run_service lifecycle (no real polling)., Scheduler starts; preset stop_event exits cleanly with run_poller=False. (+2 more)

### Community 58 - "Benchmark — Product Manager @ T-Mobile"
Cohesion: 0.33
Nodes (5): Benchmark — Product Manager @ T-Mobile, Dimensions, Gaps, Recommendations, Strengths

### Community 59 - "_request"
Cohesion: 0.22
Nodes (15): AsyncClient, Exception, Response, _fetch_detail(), _fetch_listing_page(), _parse_json(), Any, retry (+7 more)

### Community 60 - "test_depleted_credits_fail_fast_without_fallback"
Cohesion: 0.20
Nodes (6): asyncio, Burning the whole fallback chain on a dead account wastes ~2 minutes., test_call_with_resilience_falls_through_to_next_model(), test_call_with_resilience_reraises_permanent_error(), test_call_with_resilience_retries_then_succeeds(), test_depleted_credits_fail_fast_without_fallback()

### Community 61 - "test_workday_pairing.py"
Cohesion: 0.29
Nodes (5): asyncio, MonkeyPatch, Regression test: Workday detail responses must attach to the right listing., A listing without externalPath used to shift details onto the wrong jobs., test_details_pair_with_correct_listing()

### Community 62 - "_load_yaml"
Cohesion: 0.67
Nodes (3): _load_yaml(), Any, Path

### Community 63 - "company_matches"
Cohesion: 0.29
Nodes (7): company_matches(), True when two company names refer to the same employer. 'Google' == 'Google…, _hard_blocked(), Hard negative or company cooldown. Those jobs are not embedded., The substring blocklist used to drop MetLife whenever Meta was excluded., test_company_matches_ignores_legal_suffixes(), test_company_matches_rejects_lookalikes()

### Community 64 - "Tier"
Cohesion: 0.18
Nodes (22): Tier, _cmd_doctor(), compute_tier(), _decide_vector(), is_dream_company(), Dream-company match tolerant of legal suffixes ('Google' == 'Google LLC')., Deterministic tier from score + dream-company override (thresholds in settings)., Persist pass or reject. Dream companies always pass. (+14 more)

### Community 65 - "filters.py"
Cohesion: 0.23
Nodes (11): evaluate_job(), FilterResult, _haystack(), location_acceptable(), _location_ok(), datetime, Deterministic negative pre-filter before LLM scoring., Title phrases that count as internships when the word 'intern' is absent. (+3 more)

### Community 66 - "apply_pending"
Cohesion: 0.33
Nodes (13): apply_pending(), Module-level entry point used by README / Step 7., FakeApplicator, Path, Offline tests for apply_pending with FakeApplicator (no browser)., LinkedIn-discovered roles that apply on Workday must be eligible., _seed_job(), test_apply_linkedin_with_workday_url() (+5 more)

### Community 67 - "test_workday_locators.py"
Cohesion: 0.40
Nodes (3): asyncio, Optional Playwright locator smoke test against a local HTML fixture. Skipped…, test_accessibility_locators_on_fixture()

### Community 68 - "webhook.py"
Cohesion: 0.18
Nodes (11): handle_message(), Handle incoming text messages — specifically force_reply captures for pending…, health(), Any, FastAPI webhook for Telegram (ready for Step 7 production)., Receive Telegram updates. Validates optional secret token header., telegram_webhook(), fastapi (+3 more)

### Community 71 - "test_base_resume.py"
Cohesion: 0.32
Nodes (11): Exclusions, pikepdf, _make_base_pdf(), _profile(), Path, Tests for static base resume preparation and on-demand Typst tailoring., Create a valid PDF via Typst to stand in for the user's base resume., _sample_job() (+3 more)

### Community 72 - "LLMBillingError"
Cohesion: 0.27
Nodes (7): LLM client layer (`scorer/clients.py`), LLMBillingError, Account has no credit / invalid key — retrying and failing over is pointless., OpenAIEmbedder, Any, OpenAI embeddings. Width is ``vector_dimensions``., _vectors_from_response()

### Community 73 - "FakeClient"
Cohesion: 0.40
Nodes (3): FakeClient, Any, Return different skills for baseline JDs vs the target posting.

### Community 74 - "test_send_prep_pack_empty"
Cohesion: 0.40
Nodes (4): FakeClient, Any, Path, test_send_prep_pack_empty()

### Community 75 - "GeminiClient"
Cohesion: 0.29
Nodes (10): GeminiClient, Google Gemini client via google-genai (maps system_blocks → system_instruction)., _FakeGenaiClient, asyncio, A 503 on the primary model must roll over to the configured fallback., Thinking can eat the whole budget; retry must raise max_output_tokens., test_gemini_client_complete_maps_system_blocks(), test_gemini_client_escalates_on_truncated_output() (+2 more)

### Community 76 - "service.py"
Cohesion: 0.29
Nodes (6): configure_logging(), Central structlog configuration., Configure structlog + stdlib logging once at process start. Console renderer…, Long-running service: APScheduler + Telegram long-poll., signal, sys

### Community 77 - "scheduler.py"
Cohesion: 0.29
Nodes (5): apscheduler_schedulers_asyncio, apscheduler_triggers_cron, Orchestration package (Step 7)., APScheduler construction for the 3x/day pipeline., zoneinfo

### Community 78 - "is_pace_blocker"
Cohesion: 0.50
Nodes (5): is_pace_blocker(), True when a blocker looks like a bot wall, not MFA or a missing session., parametrize, test_pace_hints_ignore_mfa_and_empty(), test_pace_hints_match()

## Knowledge Gaps
- **42 isolated node(s):** `job-agent`, `ScrapeSummary`, `_FakeAio`, `Project`, `Build order and status` (+37 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 621 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **3 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `get_settings()` connect `get_settings` to `main`, `compiler.py`, `linkedin_people.py`, `clients.py`, `Scorer`, `telegram.py`, `workday.py`, `settings.py`, `evaluate`, `test_prep_builder.py`, `scorer/engine.py`, `models.py`, `pathlib`, `outreach.py`, `max_acceptable_years`, `suggest.py`, `profile.py`, `test_resume.py`, `Job`, `TelegramClient`, `test_pacing.py`, `vault.py`, `call_with_resilience`, `Settings`, `diff.py`, `db.py`, `answers.py`, `test_llm_provider.py`, `telemetry.py`, `benchmark/engine.py`, `test_scorer.py`, `skills.py`, `build_scheduler`, `test_vector_gate.py`, `runner.py`, `prep.py`, `conftest.py`, `test_webhook.py`, `pacing.py`, `baseline.py`, `run_service`, `Tier`, `filters.py`, `webhook.py`, `test_base_resume.py`, `LLMBillingError`, `service.py`, `scheduler.py`?**
  _High betweenness centrality (0.236) - this node is a cross-community bridge._
- **Why does `Job` connect `Job` to `compiler.py`, `Scorer`, `telegram.py`, `workday.py`, `test_prep_builder.py`, `scorer/engine.py`, `models.py`, `outreach.py`, `suggest.py`, `profile.py`, `test_resume.py`, `test_pacing.py`, `handle_callback`, `review.py`, `test_outcomes.py`, `diff.py`, `db.py`, `answers.py`, `benchmark/engine.py`, `test_scorer.py`, `skills.py`, `test_vector_gate.py`, `WorkdaySubmitter`, `Profile`, `ingest.py`, `runner.py`, `prep.py`, `get_settings`, `typing`, `baseline.py`, `company_matches`, `Tier`, `filters.py`, `apply_pending`, `test_base_resume.py`?**
  _High betweenness centrality (0.146) - this node is a cross-community bridge._
- **Why does `Profile` connect `Profile` to `compiler.py`, `Scorer`, `workday.py`, `settings.py`, `evaluate`, `test_prep_builder.py`, `scorer/engine.py`, `outreach.py`, `max_acceptable_years`, `suggest.py`, `profile.py`, `test_resume.py`, `Job`, `linkedin_jobspy.py`, `diff.py`, `answers.py`, `benchmark/engine.py`, `test_scorer.py`, `test_vector_gate.py`, `ingest.py`, `runner.py`, `AGENTS.md`, `prep.py`, `get_settings`, `baseline.py`, `company_matches`, `Tier`, `filters.py`, `apply_pending`, `test_base_resume.py`?**
  _High betweenness centrality (0.074) - this node is a cross-community bridge._
- **Are the 76 inferred relationships involving `Job` (e.g. with `Data model (core/db.py)` and `AnswerResolver`) actually correct?**
  _`Job` has 76 INFERRED edges - model-reasoned connections that need verification._
- **Are the 114 inferred relationships involving `Profile` (e.g. with `AnswerResolver` and `_latest_education()`) actually correct?**
  _`Profile` has 114 INFERRED edges - model-reasoned connections that need verification._
- **Are the 91 inferred relationships involving `Status` (e.g. with `Data model (core/db.py)` and `ApplyRunner`) actually correct?**
  _`Status` has 91 INFERRED edges - model-reasoned connections that need verification._
- **What connects `job-agent`, `ScrapeSummary`, `_FakeAio` to the rest of the system?**
  _42 weakly-connected nodes found - possible documentation gaps or missing edges._