# Graph Report - Automatic job search  (2026-09-25)

## Corpus Check
- 124 files · ~69,825 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 13 file(s) not represented in the graph (top: (none) 8, .typ 2, .mdc 1)

## Summary
- 1798 nodes · 6021 edges · 76 communities (74 shown, 2 thin omitted)
- Extraction: 89% EXTRACTED · 11% INFERRED · 0% AMBIGUOUS · INFERRED: 655 edges (avg confidence: 0.94)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `f4043dfb`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- main.py
- test_pipeline_order_and_aggregation
- compiler.py
- linkedin_people.py
- workday_rest.py
- clients.py
- Tier
- generate_suggestions_for_job
- typing
- targets.py
- evaluate
- test_prep_builder.py
- scorer/engine.py
- models.py
- get_settings
- textmatch.py
- test_robustness.py
- suggest.py
- profile.py
- test_resume.py
- Job
- Any
- test_pacing.py
- vault.py
- handle_callback
- review.py
- linkedin_jobspy.py
- telegram.py
- GeminiClient
- Settings
- diff.py
- db.py
- answers.py
- test_llm_provider.py
- human_delay
- benchmark/engine.py
- Remaining Manual Setup
- test_scorer.py
- skills.py
- test_apply_url.py
- scheduler.py
- test_vector_gate.py
- TelegramClient
- WorkdaySubmitter
- Profile
- ingest.py
- migrate_to_neon.py
- AGENTS.md
- prep.py
- profile
- init_db
- webhook.py
- test_cover_letter.py
- compile_resume_data
- Job Agent
- normalize_database_url
- baseline.py
- service.py
- Benchmark — Product Manager @ T-Mobile
- test_build_role_baseline_persists
- call_with_resilience
- test_workday_pairing.py
- load_profile
- LLMClient
- test_doctor.py
- filters.py
- _ensure_job_columns
- test_workday_locators.py
- sponsorship_signal
- job-agent
- _build_doctor_report
- GeminiEmbedder
- FakeClient
- test_send_prep_pack_empty
- get_recently_applied_companies

## God Nodes (most connected - your core abstractions)
1. `Job` - 204 edges
2. `Profile` - 170 edges
3. `session_scope()` - 141 edges
4. `get_settings()` - 137 edges
5. `Status` - 123 edges
6. `Source` - 114 edges
7. `get_job_by_id()` - 88 edges
8. `TelegramClient` - 74 edges
9. `upsert_job()` - 62 edges
10. `init_db()` - 58 edges

## Surprising Connections (you probably didn't know these)
- `What still needs the user (before live runs)` --references--> `save_session()`  [INFERRED]
  AGENTS.md → automation/login.py
- `Deploy with Docker` --references--> `save_session()`  [INFERRED]
  README.md → automation/login.py
- `Checklist (your remaining work)` --references--> `save_session()`  [INFERRED]
  SETUP.md → automation/login.py
- `Run review bot (Step 6)` --references--> `send_pending_alerts()`  [INFERRED]
  README.md → bot/alerts.py
- `Repository layout` --references--> `run_polling()`  [INFERRED]
  AGENTS.md → bot/poller.py

## Import Cycles
- None detected.

## Communities (76 total, 2 thin omitted)

### Community 0 - "main.py"
Cohesion: 0.10
Nodes (30): argparse, ArgumentParser, _eligible(), Workday source OR any source whose URL is a Workday company apply link., build_parser(), _cmd_benchmark(), _cmd_list_apply(), _cmd_poll() (+22 more)

### Community 1 - "test_pipeline_order_and_aggregation"
Cohesion: 0.15
Nodes (17): _FakeSummary, MonkeyPatch, Offline tests for orchestrator.pipeline (monkeypatched stages)., test_pipeline_order_and_aggregation(), fake_alerts(), fake_apply(), fake_ingestion(), fake_outcomes() (+9 more)

### Community 2 - "compiler.py"
Cohesion: 0.12
Nodes (30): get_jobs_by_status(), Return jobs with the given status, oldest first., pikepdf, _baseline_pdf_for_job(), clean_name(), compile_for_job(), compile_pending(), compile_resume() (+22 more)

### Community 3 - "linkedin_people.py"
Cohesion: 0.07
Nodes (42): auto_discover_peers(), _crawl(), BlockerError, build_people_search_url(), _detect_blocker(), discover_peers(), extract_profile_urls(), _heuristic_parse() (+34 more)

### Community 4 - "workday_rest.py"
Cohesion: 0.11
Nodes (35): AsyncClient, WorkdayTenant, Exception, httpx, Response, _as_text(), _company_name(), _fetch_detail() (+27 more)

### Community 5 - "clients.py"
Cohesion: 0.15
Nodes (21): random, _backoff_delay(), is_permanent_account_error(), is_transient(), _lower_thinking(), BaseException, LLM client layer: provider clients, transient-error retries, model fallback.…, Depleted credits / bad key: surfaces as 429 or 403 but will never recover. (+13 more)

### Community 6 - "Tier"
Cohesion: 0.13
Nodes (18): Tier, compute_tier(), is_dream_company(), Dream-company match tolerant of legal suffixes ('Google' == 'Google LLC')., Deterministic tier from score + dream-company override (thresholds in settings)., ScoreSummary, LLM match evaluator with tier triage and Tier-1 outreach., Evaluation (+10 more)

### Community 7 - "generate_suggestions_for_job"
Cohesion: 0.20
Nodes (15): apply_decided_suggestions(), If all suggestions for a job are decided, recompile resume with approvals.…, get_role_baseline_by_id(), get_role_baseline_by_role(), get_suggestions_for_job(), Per-role baseline resume built from aggregating ~15-20 JDs., RoleBaseline, _cmd_tailor_resume() (+7 more)

### Community 8 - "typing"
Cohesion: 0.12
Nodes (27): Locator, Human-like delay and typing helpers for browser automation., Clear and type text with per-keystroke jitter (accessibility-friendly)., type_like_human(), click_by_role(), click_next(), _collect_labeled_fields(), detect_blocker() (+19 more)

### Community 9 - "targets.py"
Cohesion: 0.09
Nodes (26): Public config exports., load_targets(), _load_yaml(), parse_workday_url(), Any, BaseModel, Path, Load and validate discovery targets (search terms + Workday tenants). (+18 more)

### Community 10 - "evaluate"
Cohesion: 0.25
Nodes (19): evaluate(), Return whether a posting should proceed to scoring., _posting(), MonkeyPatch, Tests for the negative pre-filter., international' must not satisfy the intern word-boundary gate., test_clearance_regex_pattern(), test_exclude_clearance_keyword() (+11 more)

### Community 11 - "test_prep_builder.py"
Cohesion: 0.12
Nodes (26): _answer_item(), build_job_section(), compile_prep_pdf(), generate_prep_pack(), PrepPackResult, Any, LLMClient, Path (+18 more)

### Community 12 - "scorer/engine.py"
Cohesion: 0.09
Nodes (37): build_embedder(), _cache_path(), clears_threshold(), cosine(), Embedder, jd_vector(), load_profile_embedding(), Path (+29 more)

### Community 13 - "models.py"
Cohesion: 0.17
Nodes (17): hashlib, Normalized intermediate posting model and Job mapping., Populate description_clean from HTML or existing text; return the value., content_hash(), extract_sections(), html_to_text(), _normalize_whitespace(), HTML → clean text and section extraction for token-efficient scoring. (+9 more)

### Community 14 - "get_settings"
Cohesion: 0.13
Nodes (26): launch_context(), _new_context(), new_page(), Page, Path, Stealth Playwright browser context using saved Workday sessions., Launch Chromium with stealth patches and optional saved storage_state. Yields…, save_storage_state() (+18 more)

### Community 15 - "textmatch.py"
Cohesion: 0.14
Nodes (23): _city_state(), company_tokens(), contains_phrase(), is_remote_location(), location_matches(), normalize_text(), Shared matching + truncation helpers used by filters, scoring, and answers.…, True when a posting location satisfies one preference entry. Compares city and… (+15 more)

### Community 16 - "test_robustness.py"
Cohesion: 0.15
Nodes (15): max_acceptable_years(), Highest demanded YOE still worth scoring, derived from the candidate., Reject only when every stated YOE requirement is out of reach. A JD often lists…, _yoe_reason(), _posting(), Any, Regression tests for scoring isolation, profile-aware filters, and re-scoring., JDs often list a reachable minimum plus an aspirational 'preferred'. (+7 more)

### Community 17 - "suggest.py"
Cohesion: 0.10
Nodes (36): handle_message(), _handle_suggest_callback(), Any, Handle incoming text messages — specifically force_reply captures for pending…, Handle s1|approve|id / edit / reject suggestion callbacks., decide_suggestion(), _format_card(), Any (+28 more)

### Community 18 - "profile.py"
Cohesion: 0.21
Nodes (28): Address, Education, Exclusions, Experience, Identity, Preferences, BaseModel, field_validator (+20 more)

### Community 19 - "test_resume.py"
Cohesion: 0.14
Nodes (27): build_resume_data(), extract_job_terms(), _grounded_summary(), Any, RankedBullet, Deterministic JD-aware bullet and skill selection for resume tailoring., Lowercase tokens + bigrams from title and cleaned description., Overlap score; matches that are also candidate skills weigh more. (+19 more)

### Community 20 - "Job"
Cohesion: 0.12
Nodes (47): Data model (core/db.py), Status lifecycle, _send_one(), get_job_by_id(), get_job_by_source_id(), Job, Core job record threaded through discovery → scoring → application., Insert a job or update mutable fields when (source, external_id) already… (+39 more)

### Community 21 - "Any"
Cohesion: 0.13
Nodes (9): HttpxTransport, Any, Path, Protocol, retry, Edit a text message. Outcome cards are text, not photos., Minimal async transport (mockable for offline tests)., Real Telegram Bot API transport via httpx with retries. (+1 more)

### Community 22 - "test_pacing.py"
Cohesion: 0.06
Nodes (74): acquire(), AcquireResult, _clamp_multiplier(), _clock(), end_of_local_day(), gap_seconds(), is_pace_blocker(), note_pace_block() (+66 more)

### Community 23 - "vault.py"
Cohesion: 0.15
Nodes (23): CredentialsFile, get_tenant_credentials(), has_saved_session(), load_credentials(), _load_yaml(), Any, BaseModel, Path (+15 more)

### Community 24 - "handle_callback"
Cohesion: 0.12
Nodes (36): handle_callback(), Handle one Telegram update containing a callback_query. Returns the resulting…, Telegram review bot (Step 6)., process_updates(), Any, Event, Long-polling loop for Telegram callback_query updates., Route a batch of updates; return the next offset (last update_id + 1). (+28 more)

### Community 25 - "review.py"
Cohesion: 0.14
Nodes (23): build_keyboard(), build_review_caption(), format_answers_message(), format_cover_letter_message(), Any, Build and send Telegram review cards for pending_review jobs., Follow-up text with the stored cover letter, if one was drafted., Send Telegram review cards for unsent pending_review jobs. (+15 more)

### Community 26 - "linkedin_jobspy.py"
Cohesion: 0.15
Nodes (19): field_validator, SearchConfig, math, _dataframe_to_postings(), _effective_windows(), _external_id(), _google_search_term(), _location_matches() (+11 more)

### Community 27 - "telegram.py"
Cohesion: 0.09
Nodes (45): _decision_caption(), _handle_outcome_callback(), Dispatch Telegram callback_query decisions for pending_review jobs and skill…, Record a post-submit label. Does not change status or decided_at., Ack a callback_query; never raise (expired/fake IDs return Telegram 400)., _safe_answer(), build_outcome_keyboard(), button() (+37 more)

### Community 28 - "GeminiClient"
Cohesion: 0.14
Nodes (13): AnthropicClient, _attempt(), _as_int(), _finish_reason(), GeminiClient, _attempt(), Any, Anthropic Messages API client with prompt-caching system blocks. (+5 more)

### Community 29 - "Settings"
Cohesion: 0.22
Nodes (7): BaseSettings, Path, Central configuration for the job agent. Secrets and overrides come from…, Return an absolute path rooted at the project directory when relative., Fixed path for the candidate's personal resume PDF (default for applications)., Ordered alternates for a primary model (Gemini only), excluding duplicates., Settings

### Community 30 - "diff.py"
Cohesion: 0.17
Nodes (28): StrEnum, SkillPlacement, SkillProvenance, SuggestionStatus, apply_approved_suggestions_to_resume_data(), _baseline_skill_keys(), classify_provenance(), diff_against_baseline() (+20 more)

### Community 31 - "db.py"
Cohesion: 0.18
Nodes (15): async_sessionmaker, get_engine(), get_session_factory(), _is_postgres_url(), _is_sqlite_url(), datetime, Async SQLModel persistence for jobs, scoring, and workflow state. Supports…, Dispose the global engine (used by tests to switch DATABASE_URL). (+7 more)

### Community 32 - "answers.py"
Cohesion: 0.08
Nodes (40): AnswerResolver, one(), answers_to_payload(), AnswerSource, _discovery_channel(), is_open_ended(), _latest_education(), _matches() (+32 more)

### Community 33 - "test_llm_provider.py"
Cohesion: 0.10
Nodes (26): Tech stack, build_llm_client(), Factory: return GeminiClient or AnthropicClient from settings.llm_provider., _FakeAio, _FakeAsyncModels, _FakeCandidate, _FakeGenaiClient, _FakeGenerateResponse (+18 more)

### Community 34 - "human_delay"
Cohesion: 0.26
Nodes (12): action_delay_bounds(), human_delay(), Return (min_ms, max_ms) for between-action pauses., Return (min_ms, max_ms) for per-keystroke typing delay., Sleep a jittered duration; return the seconds slept., typing_delay_bounds(), MonkeyPatch, Tests for human delay / typing bound helpers. (+4 more)

### Community 35 - "benchmark/engine.py"
Cohesion: 0.11
Nodes (34): BenchmarkReport, BenchmarkSummary, build_benchmark(), _derive_seniority(), DimensionScore, _education_rank(), _median(), _norm() (+26 more)

### Community 36 - "Remaining Manual Setup"
Cohesion: 0.08
Nodes (25): 2a. Find a Workday URL, 2b. Edit `config/targets.yaml`, 3a. Run the save-session helper, 3b. What you do in the browser, 4a. Discover jobs (LinkedIn / Indeed + any real Workday tenants), 4b. Score with Gemini, 4c. Attach your base resume to staged jobs, 4d. Send LinkedIn/Indeed application prep pack (Telegram) (+17 more)

### Community 37 - "test_scorer.py"
Cohesion: 0.09
Nodes (34): approx_tokens(), cache_block(), compact_json_dumps(), minify_job(), Any, Payload compression, schema minification, and prompt-caching utilities., Build an Anthropic system content block with ephemeral prompt caching., Compact job description for scoring: title/company/location + cleaned JD. (+26 more)

### Community 38 - "skills.py"
Cohesion: 0.11
Nodes (28): collections, json, _categorize(), extract_top_skills(), extract_top_skills_deterministic(), parse_skills_json(), StrEnum, JD skill extraction and cross-JD aggregation for the two-tier resume flow. Per-… (+20 more)

### Community 39 - "test_apply_url.py"
Cohesion: 0.23
Nodes (17): ApplyKind, classify_apply_url(), _host(), is_automateable_apply_url(), is_workday_url(), StrEnum, Classify job apply URLs (Workday vs LinkedIn listing vs other company ATS)., Where the candidate actually applies. (+9 more)

### Community 40 - "scheduler.py"
Cohesion: 0.16
Nodes (18): apscheduler_schedulers_asyncio, apscheduler_triggers_cron, AsyncIOScheduler, build_scheduler(), parse_hhmm(), Any, APScheduler construction for the 3x/day pipeline., Parse 'HH:MM' into (hour, minute). Raises ValueError on bad input. (+10 more)

### Community 41 - "test_vector_gate.py"
Cohesion: 0.19
Nodes (30): job_embed_text(), profile_embed_text(), profile_hash(), Title and company first, then a tail-truncated description., Head of the cacheable candidate block. Same cap as a job description., Module-level entry point used by README / Step 7., score_pending(), FakeClient (+22 more)

### Community 42 - "TelegramClient"
Cohesion: 0.08
Nodes (38): AlertSummary, build_alert_caption(), Telegram alerts for blocked / errored jobs (not pending_review cards)., Caption for a blocker / error alert., Notify on unsent manual_review / error jobs (screenshot + reason)., send_pending_alerts(), BaseException, High-level Telegram helpers used by review / handlers / poller. (+30 more)

### Community 43 - "WorkdaySubmitter"
Cohesion: 0.18
Nodes (14): RuntimeError, Raised when no reusable storage_state exists for a tenant., SessionMissingError, Path, Reopen saved session, reach review, click Submit once., WorkdaySubmitter, contextlib, MonkeyPatch (+6 more)

### Community 44 - "Profile"
Cohesion: 0.29
Nodes (16): Profile, Single Source of Truth for candidate facts. No LLM invention beyond this., prerank_jobs(), prerank_score(), Return jobs ordered best-first by ``prerank_score`` (stable on ties)., Cheap 0..~100 heuristic; higher = score sooner. No network, no LLM., _job(), datetime (+8 more)

### Community 45 - "ingest.py"
Cohesion: 0.15
Nodes (24): _dedupe(), IngestSummary, Ingestion orchestrator: fetch → clean → filter → upsert., Run one full discovery cycle and persist results., run_ingestion(), Job discovery scrapers (LinkedIn/Indeed via JobSpy, Workday CXS REST)., fetch_linkedin_indeed(), Fetch LinkedIn/Indeed postings for all configured search terms. (+16 more)

### Community 46 - "migrate_to_neon.py"
Cohesion: 0.22
Nodes (13): enum, _cell(), _copy_table(), _counts(), main(), AsyncSession, SQLModel, Copy local SQLite rows into the Neon Postgres database. Reads… (+5 more)

### Community 47 - "AGENTS.md"
Cohesion: 0.10
Nodes (16): Build order and status, Coding conventions, Commands, Confirmed product decisions, Project, Repository layout, Scoring specifics (Step 3), What still needs the user (before live runs) (+8 more)

### Community 48 - "prep.py"
Cohesion: 0.15
Nodes (15): _brief_message(), PrepSummary, LLMClient, Generate and deliver LinkedIn/Indeed application prep packs via Telegram., Build and send a prep pack for unsent staged LinkedIn/Indeed jobs. Brief mode…, Compact job list — no LLM, no PDF, just the 6 fields the user wants., Send a compact text message — no LLM calls, no file uploads., _send_brief() (+7 more)

### Community 49 - "profile"
Cohesion: 0.20
Nodes (14): Testing conventions, db_ready(), _disable_apply_pacing(), _disable_vector_gate(), profile(), fixture, MonkeyPatch, Path (+6 more)

### Community 50 - "init_db"
Cohesion: 0.20
Nodes (12): init_db(), Create storage directories and ensure all tables exist., Orchestration package (Step 7)., _benchmark_tier_one_stage(), PipelineSummary, Any, Full pipeline: ingest, score, resume, suggest, prep, apply, reviews, outcomes,…, Run all pipeline stages sequentially with per-stage isolation. A failure in one… (+4 more)

### Community 51 - "webhook.py"
Cohesion: 0.17
Nodes (14): health(), FastAPI webhook for Telegram (ready for Step 7 production)., fastapi, fastapi_testclient, get, TestClient, client(), fixture (+6 more)

### Community 52 - "test_cover_letter.py"
Cohesion: 0.11
Nodes (28): cap_cover_letter(), _fallback_cover_letter(), generate_cover_letter(), Tier-1 cover letter drafting with the same anti-AI gate as outreach., Trim to the last sentence that fits, so a runaway letter stays usable., Deterministic letter used when the model keeps failing the style gate., Draft a short cover letter; retry once if banned words appear., run_one() (+20 more)

### Community 53 - "compile_resume_data"
Cohesion: 0.21
Nodes (17): apply_fit_caps(), compile_resume_data(), FitReport, _next_fit_state(), pdf_page_count(), Any, Return the number of pages in a PDF., Return a copy of resume data with content caps and typography knobs applied. (+9 more)

### Community 54 - "Job Agent"
Cohesion: 0.13
Nodes (14): Application prep packs (LinkedIn / Indeed), Deploy with Docker, Job Agent, Layout, LinkedIn peer benchmarking (optional, off by default), Resumes (Step 4), Run automation (Step 5), Run ingestion (Step 2) (+6 more)

### Community 55 - "normalize_database_url"
Cohesion: 0.29
Nodes (9): _absolute_sqlite_url(), normalize_database_url(), Normalize DATABASE_URL for SQLAlchemy async engines. - Relative sqlite paths…, Make relative sqlite paths absolute so cwd does not matter., DATABASE_URL normalization for SQLite + Neon Postgres., test_normalize_drops_prisma_connection_limit(), test_normalize_keeps_sqlite(), test_normalize_upgrades_postgres_scheme() (+1 more)

### Community 56 - "baseline.py"
Cohesion: 0.10
Nodes (27): get_jobs_for_role(), Return recent jobs whose title matches any of the role title terms. Matching is…, _cmd_build_baseline(), re, build_baseline_resume_data(), build_role_baseline(), _normalize(), Any (+19 more)

### Community 57 - "service.py"
Cohesion: 0.13
Nodes (16): asyncio, configure_logging(), Central structlog configuration., Configure structlog + stdlib logging once at process start. Console renderer…, Event, Long-running service: APScheduler + Telegram long-poll., Start the scheduler and (optionally) the Telegram poller until stopped.…, run_service() (+8 more)

### Community 58 - "Benchmark — Product Manager @ T-Mobile"
Cohesion: 0.33
Nodes (5): Benchmark — Product Manager @ T-Mobile, Dimensions, Gaps, Recommendations, Strengths

### Community 59 - "test_build_role_baseline_persists"
Cohesion: 0.33
Nodes (5): FakeClient, Path_exists(), Any, asyncio, test_build_role_baseline_persists()

### Community 60 - "call_with_resilience"
Cohesion: 0.14
Nodes (15): LLM client layer (`scorer/clients.py`), call_with_resilience(), LLMBillingError, LLMError, RuntimeError, Run attempt_fn(model) across candidate models, retrying transient errors. Each…, Raised when a completion cannot be obtained from any candidate model., Account has no credit / invalid key — retrying and failing over is pointless. (+7 more)

### Community 61 - "test_workday_pairing.py"
Cohesion: 0.29
Nodes (5): asyncio, MonkeyPatch, Regression test: Workday detail responses must attach to the right listing., A listing without externalPath used to shift details onto the wrong jobs., test_details_pair_with_correct_listing()

### Community 62 - "load_profile"
Cohesion: 0.25
Nodes (8): load_profile(), _load_yaml(), Any, Path, Load and validate profile.yaml. Cached after first successful load., Clear cache and reload (useful after editing profile.yaml)., reload_profile(), test_load_profile_for_scorer()

### Community 63 - "LLMClient"
Cohesion: 0.16
Nodes (13): company_matches(), True when two company names refer to the same employer. 'Google' == 'Google…, LLMClient, Protocol, Minimal async LLM interface (mockable for offline tests)., _hard_blocked(), Hard negative or company cooldown. Those jobs are not embedded., Score discovered jobs and persist tiered results. (+5 more)

### Community 64 - "test_doctor.py"
Cohesion: 0.44
Nodes (10): _cmd_doctor(), _job(), datetime, Path, Offline tests for the doctor health report., test_doctor_cooldown(), test_doctor_empty_db(), test_doctor_outcomes() (+2 more)

### Community 65 - "filters.py"
Cohesion: 0.24
Nodes (10): FilterResult, _haystack(), location_acceptable(), _location_ok(), datetime, Deterministic negative pre-filter before LLM scoring., Title phrases that count as internships when the word 'intern' is absent., Shared geo rule for JobSpy pre-filtering, ingest, and the scoring guard. (+2 more)

### Community 66 - "_ensure_job_columns"
Cohesion: 0.31
Nodes (9): _dialect_name(), _ensure_job_columns(), _job_column_names(), job_to_dict(), Any, UTC-aware DateTime column (TIMESTAMPTZ on Postgres; works on SQLite too)., Column names on jobs, or empty when the table does not exist yet., Add Phase 2 columns to an existing jobs table. No-op when already present. (+1 more)

### Community 67 - "test_workday_locators.py"
Cohesion: 0.40
Nodes (3): asyncio, Optional Playwright locator smoke test against a local HTML fixture. Skipped…, test_accessibility_locators_on_fixture()

### Community 68 - "sponsorship_signal"
Cohesion: 0.22
Nodes (9): Classify a JD's stance on visa sponsorship without a profile dependency.…, sponsorship_signal(), test_sponsorship_signal_friendly_explicit(), test_sponsorship_signal_friendly_opt_cpt(), test_sponsorship_signal_hostile_beats_friendly(), test_sponsorship_signal_hostile_citizenship_required(), test_sponsorship_signal_hostile_no_sponsorship(), test_sponsorship_signal_sponsor_events_is_not_friendly() (+1 more)

### Community 71 - "_build_doctor_report"
Cohesion: 0.36
Nodes (8): _build_doctor_report(), _count_jobs(), _print_doctor_report(), Any, First element of a row tuple; scalars pass through., Read-only pipeline health snapshot. No LLM calls., Human-readable health report. JSON mode prints the dict instead., _unwrap()

### Community 72 - "GeminiEmbedder"
Cohesion: 0.38
Nodes (4): GeminiEmbedder, Any, Gemini ``embed_content`` with semantic-similarity task type., _vectors_from_response()

### Community 73 - "FakeClient"
Cohesion: 0.40
Nodes (3): FakeClient, Any, Return different skills for baseline JDs vs the target posting.

### Community 74 - "test_send_prep_pack_empty"
Cohesion: 0.40
Nodes (4): FakeClient, Any, Path, test_send_prep_pack_empty()

### Community 75 - "get_recently_applied_companies"
Cohesion: 0.50
Nodes (4): _company_name(), get_recently_applied_companies(), Unwrap a single-column select row into a company string., Companies we submitted to within the cooldown window. Statuses included:…

## Knowledge Gaps
- **42 isolated node(s):** `job-agent`, `ScrapeSummary`, `_FakeAio`, `Project`, `Build order and status` (+37 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 612 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **2 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `get_settings()` connect `get_settings` to `main.py`, `compiler.py`, `linkedin_people.py`, `clients.py`, `Tier`, `generate_suggestions_for_job`, `typing`, `targets.py`, `evaluate`, `test_prep_builder.py`, `scorer/engine.py`, `models.py`, `test_robustness.py`, `suggest.py`, `profile.py`, `test_resume.py`, `Any`, `test_pacing.py`, `vault.py`, `telegram.py`, `GeminiClient`, `Settings`, `diff.py`, `db.py`, `answers.py`, `test_llm_provider.py`, `human_delay`, `benchmark/engine.py`, `test_scorer.py`, `skills.py`, `scheduler.py`, `test_vector_gate.py`, `TelegramClient`, `migrate_to_neon.py`, `prep.py`, `init_db`, `webhook.py`, `test_cover_letter.py`, `baseline.py`, `service.py`, `LLMClient`, `filters.py`, `_build_doctor_report`, `GeminiEmbedder`?**
  _High betweenness centrality (0.189) - this node is a cross-community bridge._
- **Why does `Job` connect `Job` to `main.py`, `compiler.py`, `generate_suggestions_for_job`, `typing`, `test_prep_builder.py`, `scorer/engine.py`, `models.py`, `get_settings`, `test_robustness.py`, `suggest.py`, `profile.py`, `test_resume.py`, `test_pacing.py`, `handle_callback`, `review.py`, `telegram.py`, `diff.py`, `db.py`, `answers.py`, `benchmark/engine.py`, `test_scorer.py`, `skills.py`, `test_vector_gate.py`, `TelegramClient`, `WorkdaySubmitter`, `Profile`, `ingest.py`, `migrate_to_neon.py`, `prep.py`, `test_cover_letter.py`, `baseline.py`, `test_build_role_baseline_persists`, `LLMClient`, `test_doctor.py`, `filters.py`, `_ensure_job_columns`, `_build_doctor_report`?**
  _High betweenness centrality (0.136) - this node is a cross-community bridge._
- **Why does `Profile` connect `Profile` to `compiler.py`, `Tier`, `generate_suggestions_for_job`, `typing`, `targets.py`, `evaluate`, `test_prep_builder.py`, `scorer/engine.py`, `test_robustness.py`, `suggest.py`, `profile.py`, `test_resume.py`, `Job`, `test_pacing.py`, `linkedin_jobspy.py`, `diff.py`, `answers.py`, `benchmark/engine.py`, `test_scorer.py`, `test_vector_gate.py`, `ingest.py`, `AGENTS.md`, `prep.py`, `test_cover_letter.py`, `baseline.py`, `load_profile`, `LLMClient`, `filters.py`?**
  _High betweenness centrality (0.098) - this node is a cross-community bridge._
- **Are the 71 inferred relationships involving `Job` (e.g. with `Data model (core/db.py)` and `AnswerResolver`) actually correct?**
  _`Job` has 71 INFERRED edges - model-reasoned connections that need verification._
- **Are the 113 inferred relationships involving `Profile` (e.g. with `AnswerResolver` and `_latest_education()`) actually correct?**
  _`Profile` has 113 INFERRED edges - model-reasoned connections that need verification._
- **Are the 86 inferred relationships involving `Status` (e.g. with `Data model (core/db.py)` and `ApplyRunner`) actually correct?**
  _`Status` has 86 INFERRED edges - model-reasoned connections that need verification._
- **What connects `job-agent`, `ScrapeSummary`, `_FakeAio` to the rest of the system?**
  _42 weakly-connected nodes found - possible documentation gaps or missing edges._