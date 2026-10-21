# Graph Report - Automatic job search  (2026-09-26)

## Corpus Check
- 125 files · ~72,189 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 13 file(s) not represented in the graph (top: (none) 8, .typ 2, .mdc 1)

## Summary
- 1867 nodes · 6155 edges · 82 communities (69 shown, 13 thin omitted)
- Extraction: 91% EXTRACTED · 9% INFERRED · 0% AMBIGUOUS · INFERRED: 556 edges (avg confidence: 0.94)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `37ab24a5`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- main.py
- test_pipeline_order_and_aggregation
- compiler.py
- linkedin_people.py
- workday_rest.py
- clients.py
- parse_score
- answers.py
- workday.py
- typing
- evaluate
- builder.py
- scorer/engine.py
- models.py
- LLMClient
- textmatch.py
- test_robustness.py
- suggest.py
- Profile
- test_resume.py
- Job
- Any
- test_pacing.py
- settings.py
- test_handlers.py
- bot/__init__.py
- linkedin_jobspy.py
- telegram.py
- Any
- Settings
- diff.py
- db.py
- test_answers.py
- test_llm_provider.py
- telemetry.py
- benchmark/engine.py
- Remaining Manual Setup
- prompts.py
- skills.py
- test_apply_url.py
- build_scheduler
- test_vector_gate.py
- TelegramClient
- WorkdaySubmitter
- prerank.py
- ingest.py
- runner.py
- AGENTS.md
- prep.py
- fixture
- get_settings
- scrape_profile
- TokenUsage
- targets.py
- Job Agent
- test_poller.py
- load_profile
- outreach.py
- Benchmark — Product Manager @ T-Mobile
- test_linkedin_people.py
- test_linkedin_discover.py
- test_build_role_baseline_persists
- .total_years_experience
- .generate_content
- BlockerError
- filters.py
- get_job_by_id
- test_workday_locators.py
- .complete
- job-agent
- LLMClient
- OpenAIEmbedder
- retry
- AsyncSession
- test_gemini_client_falls_back_when_model_unavailable
- SQLModel
- LLMClient
- LLMClient
- RuntimeError
- BaseModel
- field_validator

## God Nodes (most connected - your core abstractions)
1. `Job` - 214 edges
2. `session_scope()` - 148 edges
3. `get_settings()` - 146 edges
4. `Status` - 130 edges
5. `Source` - 119 edges
6. `get_job_by_id()` - 91 edges
7. `TelegramClient` - 76 edges
8. `Profile` - 72 edges
9. `upsert_job()` - 66 edges
10. `init_db()` - 58 edges

## Surprising Connections (you probably didn't know these)
- `Confirmed product decisions` --references--> `compile_for_job()`  [INFERRED]
  AGENTS.md → resume/compiler.py
- `Checklist (your remaining work)` --references--> `save_session()`  [INFERRED]
  SETUP.md → automation/login.py
- `Run review bot (Step 6)` --references--> `send_pending_alerts()`  [INFERRED]
  README.md → bot/alerts.py
- `Tech stack` --references--> `build_embedder()`  [INFERRED]
  AGENTS.md → scorer/embeddings.py
- `Repository layout` --references--> `run_polling()`  [INFERRED]
  AGENTS.md → bot/poller.py

## Import Cycles
- None detected.

## Communities (82 total, 13 thin omitted)

### Community 0 - "main.py"
Cohesion: 0.05
Nodes (59): argparse, ArgumentParser, get_recently_applied_companies(), Companies we submitted to within the cooldown window. Statuses included:…, configure_logging(), Central structlog configuration., Configure structlog + stdlib logging once at process start. Console renderer…, _build_doctor_report() (+51 more)

### Community 1 - "test_pipeline_order_and_aggregation"
Cohesion: 0.15
Nodes (17): _FakeSummary, MonkeyPatch, Offline tests for orchestrator.pipeline (monkeypatched stages)., test_pipeline_order_and_aggregation(), fake_alerts(), fake_apply(), fake_ingestion(), fake_outcomes() (+9 more)

### Community 2 - "compiler.py"
Cohesion: 0.10
Nodes (41): get_role_baseline_by_role(), apply_fit_caps(), _baseline_pdf_for_job(), clean_name(), compile_for_job(), compile_pending(), compile_resume(), compile_resume_data() (+33 more)

### Community 3 - "linkedin_people.py"
Cohesion: 0.22
Nodes (14): _heuristic_parse(), LLMClient, parse_profile(), parse_profile_json(), PeerProfileData, BaseModel, Protocol, LinkedIn people profile scrape + parse (authenticated session). Default posture… (+6 more)

### Community 4 - "workday_rest.py"
Cohesion: 0.11
Nodes (35): AsyncClient, Exception, httpx, Response, _as_text(), _company_name(), _one(), _fetch_detail() (+27 more)

### Community 5 - "clients.py"
Cohesion: 0.10
Nodes (33): LLM client layer (`scorer/clients.py`), RuntimeError, _backoff_delay(), call_with_resilience(), is_permanent_account_error(), is_transient(), LLMBillingError, LLMError (+25 more)

### Community 6 - "parse_score"
Cohesion: 0.10
Nodes (20): BaseModel, field_validator, _extract_json_object(), parse_score(), Extract compact {"s","t","r"} JSON from model output (tolerant)., First brace-balanced JSON object, ignoring braces inside string literals., ScoreSummary, LLM match evaluator with tier triage and Tier-1 outreach. (+12 more)

### Community 7 - "answers.py"
Cohesion: 0.12
Nodes (21): _discovery_channel(), is_open_ended(), _latest_education(), _matches(), needs_human_review(), _norm(), Any, Profile (+13 more)

### Community 8 - "workday.py"
Cohesion: 0.11
Nodes (30): RuntimeError, Raised when no reusable storage_state exists for a tenant., SessionMissingError, human_delay(), Sleep a jittered duration; return the seconds slept., BlockerError, click_by_role(), click_next() (+22 more)

### Community 9 - "typing"
Cohesion: 0.16
Nodes (17): cap_cover_letter(), _fallback_cover_letter(), generate_cover_letter(), Profile, Tier-1 cover letter drafting with the same anti-AI gate as outreach., Trim to the last sentence that fits, so a runaway letter stays usable., Deterministic letter used when the model keeps failing the style gate., Draft a short cover letter; retry once if banned words appear. (+9 more)

### Community 10 - "evaluate"
Cohesion: 0.15
Nodes (32): evaluate(), _haystack(), RawPosting, Return whether a posting should proceed to scoring., Classify a JD's stance on visa sponsorship without a profile dependency.…, sponsorship_signal(), _posting(), MonkeyPatch (+24 more)

### Community 11 - "builder.py"
Cohesion: 0.14
Nodes (20): datetime, _answer_item(), build_job_section(), compile_prep_pdf(), generate_prep_pack(), PrepPackResult, Any, Path (+12 more)

### Community 12 - "scorer/engine.py"
Cohesion: 0.08
Nodes (44): build_embedder(), _cache_path(), clears_threshold(), cosine(), Embedder, jd_vector(), job_embed_text(), load_profile_embedding() (+36 more)

### Community 13 - "models.py"
Cohesion: 0.15
Nodes (19): hashlib, pydantic, hash_fallback(), Normalized intermediate posting model and Job mapping., Populate description_clean from HTML or existing text; return the value., content_hash(), extract_sections(), html_to_text() (+11 more)

### Community 14 - "LLMClient"
Cohesion: 0.21
Nodes (12): LLMClient, Protocol, Minimal async LLM interface (mockable for offline tests)., Profile, Score discovered jobs and persist tiered results., Score a single job and optionally draft Tier-1 outreach and a cover letter., Score one job and persist; never raises (returns error outcome)., Score discovered jobs with bounded concurrency; optional early-stop. (+4 more)

### Community 15 - "textmatch.py"
Cohesion: 0.13
Nodes (25): _city_state(), company_matches(), company_tokens(), contains_phrase(), is_remote_location(), location_matches(), normalize_text(), Shared matching + truncation helpers used by filters, scoring, and answers.… (+17 more)

### Community 16 - "test_robustness.py"
Cohesion: 0.15
Nodes (19): compute_tier(), is_dream_company(), Dream-company match tolerant of legal suffixes ('Google' == 'Google LLC')., Deterministic tier from score + dream-company override (thresholds in settings)., max_acceptable_years(), Highest demanded YOE still worth scoring, derived from the candidate., _posting(), Any (+11 more)

### Community 17 - "suggest.py"
Cohesion: 0.11
Nodes (37): AsyncSession, apply_decided_suggestions(), decide_suggestion(), _format_card(), Any, Telegram delivery and apply path for skill suggestions., If all suggestions for a job are decided, recompile resume with approvals.…, Mark a suggestion approved/rejected/edited and maybe recompile. (+29 more)

### Community 18 - "Profile"
Cohesion: 0.12
Nodes (45): Address, Education, Exclusions, Experience, Identity, Preferences, Profile, BaseModel (+37 more)

### Community 19 - "test_resume.py"
Cohesion: 0.13
Nodes (29): pikepdf, build_resume_data(), extract_job_terms(), _grounded_summary(), Any, RankedBullet, Deterministic JD-aware bullet and skill selection for resume tailoring., Lowercase tokens + bigrams from title and cleaned description. (+21 more)

### Community 20 - "Job"
Cohesion: 0.11
Nodes (52): Data model (core/db.py), Status lifecycle, _unsent_scored_jobs(), get_job_by_source_id(), Job, StrEnum, Core job record threaded through discovery → scoring → application., Insert a job or update mutable fields when (source, external_id) already… (+44 more)

### Community 21 - "Any"
Cohesion: 0.13
Nodes (9): HttpxTransport, Any, Path, Protocol, Edit a text message. Outcome cards are text, not photos., Minimal async transport (mockable for offline tests)., Real Telegram Bot API transport via httpx with retries., TelegramTransport (+1 more)

### Community 22 - "test_pacing.py"
Cohesion: 0.11
Nodes (44): acquire(), AcquireResult, _clamp_multiplier(), _clock(), end_of_local_day(), gap_seconds(), note_pace_block(), note_success() (+36 more)

### Community 23 - "settings.py"
Cohesion: 0.08
Nodes (50): What still needs the user (before live runs), launch_context(), _new_context(), new_page(), Page, Path, Stealth Playwright browser context using saved Workday sessions., Launch Chromium with stealth patches and optional saved storage_state. Yields… (+42 more)

### Community 24 - "test_handlers.py"
Cohesion: 0.33
Nodes (15): SubmitResult, ReviewAction, _callback_update(), FakeSubmitter, Any, Path, Offline tests for Telegram callback handlers with FakeSubmitter., _seed_pending() (+7 more)

### Community 25 - "bot/__init__.py"
Cohesion: 0.11
Nodes (29): Telegram review bot (Step 6)., build_keyboard(), build_review_caption(), format_answers_message(), format_cover_letter_message(), Any, Build and send Telegram review cards for pending_review jobs., Follow-up text with the stored cover letter, if one was drafted. (+21 more)

### Community 26 - "linkedin_jobspy.py"
Cohesion: 0.17
Nodes (21): math, _dataframe_to_postings(), _effective_windows(), _external_id(), fetch_linkedin_indeed(), _google_search_term(), _location_matches(), _parse_posted_at() (+13 more)

### Community 27 - "telegram.py"
Cohesion: 0.07
Nodes (56): _decision_caption(), handle_callback(), _handle_outcome_callback(), _handle_suggest_callback(), Any, Dispatch Telegram callback_query decisions for pending_review jobs and skill…, Record a post-submit label. Does not change status or decided_at., Handle one Telegram update containing a callback_query. Returns the resulting… (+48 more)

### Community 28 - "Any"
Cohesion: 0.16
Nodes (12): _attempt(), _as_int(), _finish_reason(), GeminiClient, _attempt(), _lower_thinking(), _attempt(), Any (+4 more)

### Community 29 - "Settings"
Cohesion: 0.16
Nodes (9): BaseSettings, Path, Central configuration for the job agent. Secrets and overrides come from…, Return an absolute path rooted at the project directory when relative., Fixed path for the candidate's personal resume PDF (default for applications)., Model id used for scoring. Always the OpenAI scorer., Model id used for outreach / open-ended answers. Always OpenAI., Ordered alternates for a primary model (Gemini only), excluding duplicates. (+1 more)

### Community 30 - "diff.py"
Cohesion: 0.12
Nodes (40): SkillPlacement, SkillProvenance, SuggestionStatus, JdSkill, apply_approved_suggestions_to_resume_data(), _baseline_skill_keys(), classify_provenance(), diff_against_baseline() (+32 more)

### Community 31 - "db.py"
Cohesion: 0.05
Nodes (59): Testing conventions, async_sessionmaker, contextlib, _absolute_sqlite_url(), _company_name(), _dialect_name(), _ensure_job_columns(), get_engine() (+51 more)

### Community 32 - "test_answers.py"
Cohesion: 0.14
Nodes (19): AnswerResolver, one(), answers_to_payload(), AnswerSource, StrEnum, Resolve form labels to answers; LLM only for open-ended unknowns., Resolve questions concurrently, preserving input order., Persistable JSON blob for Job.application_answers. (+11 more)

### Community 33 - "test_llm_provider.py"
Cohesion: 0.13
Nodes (21): Scoring specifics (Step 3), Tech stack, Compact, cacheable candidate summary for LLM system prompts (Step 3)., build_llm_client(), OpenAIClient, OpenAI Chat Completions client. JSON scoring uses json_object mode., Scoring and writing always go through OpenAI., _FakeAio (+13 more)

### Community 34 - "telemetry.py"
Cohesion: 0.16
Nodes (16): action_delay_bounds(), Locator, Human-like delay and typing helpers for browser automation., Return (min_ms, max_ms) for between-action pauses., Return (min_ms, max_ms) for per-keystroke typing delay., Clear and type text with per-keystroke jitter (accessibility-friendly)., type_like_human(), typing_delay_bounds() (+8 more)

### Community 35 - "benchmark/engine.py"
Cohesion: 0.13
Nodes (26): BenchmarkReport, BenchmarkSummary, build_benchmark(), _derive_seniority(), DimensionScore, _education_rank(), _median(), _norm() (+18 more)

### Community 36 - "Remaining Manual Setup"
Cohesion: 0.08
Nodes (25): 2a. Find a Workday URL, 2b. Edit `config/targets.yaml`, 3a. Run the save-session helper, 3b. What you do in the browser, 4a. Discover jobs (LinkedIn / Indeed + any real Workday tenants), 4b. Score with Gemini, 4c. Attach your base resume to staged jobs, 4d. Send LinkedIn/Indeed application prep pack (Telegram) (+17 more)

### Community 37 - "prompts.py"
Cohesion: 0.13
Nodes (20): approx_tokens(), cache_block(), compact_json_dumps(), minify_job(), Any, Payload compression, schema minification, and prompt-caching utilities., Build an Anthropic system content block with ephemeral prompt caching., Compact job description for scoring: title/company/location + cleaned JD. (+12 more)

### Community 38 - "skills.py"
Cohesion: 0.08
Nodes (38): collections, enum, aggregate_role_skills(), AggregatedSkill, _categorize(), extract_top_skills(), extract_top_skills_deterministic(), JdSkill (+30 more)

### Community 39 - "test_apply_url.py"
Cohesion: 0.18
Nodes (21): _eligible(), Workday source OR any source whose URL is a Workday company apply link., ApplyKind, classify_apply_url(), _host(), is_automateable_apply_url(), is_workday_url(), StrEnum (+13 more)

### Community 40 - "build_scheduler"
Cohesion: 0.23
Nodes (14): AsyncIOScheduler, build_scheduler(), parse_hhmm(), Any, Parse 'HH:MM' into (hour, minute). Raises ValueError on bad input., Build (but do not start) an AsyncIOScheduler with one job per HH:MM. Jobs use…, _noop(), MonkeyPatch (+6 more)

### Community 41 - "test_vector_gate.py"
Cohesion: 0.28
Nodes (27): profile_embed_text(), profile_hash(), Head of the cacheable candidate block. Same cap as a job description., Module-level entry point used by README / Step 7., score_pending(), FakeClient, Deterministic LLM stand-in for offline tests., _enable() (+19 more)

### Community 42 - "TelegramClient"
Cohesion: 0.08
Nodes (42): AlertSummary, build_alert_caption(), Telegram alerts for blocked / errored jobs (not pending_review cards)., Caption for a blocker / error alert., Notify on unsent manual_review / error jobs (screenshot + reason)., _send_one(), send_pending_alerts(), BaseException (+34 more)

### Community 43 - "WorkdaySubmitter"
Cohesion: 0.09
Nodes (26): Path, Reopen saved session, reach review, click Submit once., WorkdaySubmitter, Any, Receive Telegram updates. Validates optional secret token header., telegram_webhook(), fastapi_testclient, post (+18 more)

### Community 44 - "prerank.py"
Cohesion: 0.21
Nodes (19): prerank_jobs(), prerank_score(), Profile, Deterministic, LLM-free pre-rank to order jobs before scoring. Recall/cost…, Return jobs ordered best-first by ``prerank_score`` (stable on ties)., Map a job source to a rank weight. Unknown values score as 1.0., Cheap 0..~100 heuristic; higher = score sooner. No network, no LLM., _source_weight() (+11 more)

### Community 45 - "ingest.py"
Cohesion: 0.19
Nodes (20): _dedupe(), IngestSummary, Ingestion orchestrator: fetch → clean → filter → upsert., Run one full discovery cycle and persist results., run_ingestion(), Job discovery scrapers (LinkedIn/Indeed via JobSpy, Workday CXS REST)., BaseModel, Source-agnostic posting produced by scrapers before DB persistence. (+12 more)

### Community 46 - "runner.py"
Cohesion: 0.14
Nodes (15): Workday application automation (Step 5)., is_pace_blocker(), True when a blocker looks like a bot wall, not MFA or a missing session., ApplySummary, datetime, Random, Batch runner: staged Workday-eligible jobs -> pending_review (or…, Applicator (+7 more)

### Community 47 - "AGENTS.md"
Cohesion: 0.22
Nodes (7): Build order and status, Coding conventions, Commands, Confirmed product decisions, Project, Repository layout, Workflow for implementing a step

### Community 48 - "prep.py"
Cohesion: 0.15
Nodes (23): _load_scored(), _mark_sent(), PrepSummary, datetime, Profile, Generate and deliver LinkedIn/Indeed application prep packs via Telegram., One text file for the run. Empty input sends nothing., Build and send a prep pack for unsent staged LinkedIn/Indeed jobs. Brief mode… (+15 more)

### Community 50 - "get_settings"
Cohesion: 0.10
Nodes (28): apscheduler_schedulers_asyncio, apscheduler_triggers_cron, asyncio, collections_abc, get_settings(), Cached settings singleton., get_jobs_by_status(), init_db() (+20 more)

### Community 51 - "scrape_profile"
Cohesion: 0.24
Nodes (11): auto_discover_peers(), _crawl(), _detect_blocker(), Any, Path, Navigate to a LinkedIn profile URL and extract visible text sections., Crawl LinkedIn People Search for peers matching this job's title. Requires…, _require_enabled() (+3 more)

### Community 52 - "TokenUsage"
Cohesion: 0.20
Nodes (5): AnthropicClient, Anthropic Messages API client with prompt-caching system blocks., Accumulated provider usage for one client instance (one scoring run)., TokenUsage, __init__()

### Community 53 - "targets.py"
Cohesion: 0.07
Nodes (33): Public config exports., load_targets(), _load_yaml(), parse_workday_url(), Any, BaseModel, field_validator, Path (+25 more)

### Community 54 - "Job Agent"
Cohesion: 0.13
Nodes (14): Application prep packs (LinkedIn / Indeed), Job Agent, Layout, LinkedIn peer benchmarking (optional, off by default), Resumes (Step 4), Run automation (Step 5), Run ingestion (Step 2), Run review bot (Step 6) (+6 more)

### Community 55 - "test_poller.py"
Cohesion: 0.13
Nodes (17): handle_message(), Handle incoming text messages — specifically force_reply captures for pending…, process_updates(), Any, Event, Long-polling loop for Telegram callback_query updates., Route a batch of updates; return the next offset (last update_id + 1)., Long-poll Telegram getUpdates until stop_event is set (or max_iterations).… (+9 more)

### Community 56 - "load_profile"
Cohesion: 0.12
Nodes (21): load_profile(), _load_yaml(), Any, Path, Load and validate profile.yaml. Cached after first successful load., get_jobs_for_role(), Return recent jobs whose title matches any of the role title terms. Matching is…, json (+13 more)

### Community 57 - "outreach.py"
Cohesion: 0.25
Nodes (10): contains_banned(), _fallback_outreach(), generate_outreach(), Tier-1 alumni/referral outreach drafting with anti-AI style gate., Return banned phrases present as whole words (case-insensitive)., Drop sentences that contain banned words; keep the rest., Draft a 3-sentence outreach note; retry once if banned words appear., Deterministic, profile-grounded note used when the model keeps failing the gate. (+2 more)

### Community 58 - "Benchmark — Product Manager @ T-Mobile"
Cohesion: 0.33
Nodes (5): Benchmark — Product Manager @ T-Mobile, Dimensions, Gaps, Recommendations, Strengths

### Community 59 - "test_linkedin_people.py"
Cohesion: 0.24
Nodes (9): discover_peers(), parse_profile_html(), Offline-friendly extraction from saved HTML (tests / fixtures)., Return peer profile URLs. Semi-automated by default: caller supplies explicit…, asyncio, Offline tests for LinkedIn profile HTML parse and peer discovery., test_discover_peers_semi_auto(), test_parse_profile_heuristic_without_client() (+1 more)

### Community 60 - "test_linkedin_discover.py"
Cohesion: 0.31
Nodes (8): build_people_search_url(), extract_profile_urls(), Build a LinkedIn People Search URL from role keywords., Pull unique /in/ profile URLs from a search-results HTML dump., Tests for LinkedIn people-search URL building and profile URL extraction., test_build_people_search_url_encodes_keywords(), test_extract_profile_urls_dedupes_and_caps(), test_extract_profile_urls_empty()

### Community 61 - "test_build_role_baseline_persists"
Cohesion: 0.33
Nodes (5): FakeClient, Path_exists(), Any, asyncio, test_build_role_baseline_persists()

### Community 62 - ".total_years_experience"
Cohesion: 0.50
Nodes (4): _parse_month(), Approximate career length in years, spanning earliest start to latest end., Parse 'YYYY-MM' / 'YYYY'; 'Present' and unparseable values return None., date

### Community 63 - ".generate_content"
Cohesion: 0.40
Nodes (4): _FakeAsyncModels, _FakeCandidate, _FakeGenerateResponse, Any

### Community 64 - "BlockerError"
Cohesion: 0.50
Nodes (3): BlockerError, RuntimeError, LinkedIn checkpoint / login wall / Cloudflare detected.

### Community 65 - "filters.py"
Cohesion: 0.20
Nodes (14): evaluate_job(), FilterResult, location_acceptable(), _location_ok(), datetime, Profile, Deterministic negative pre-filter before LLM scoring., Title phrases that count as internships when the word 'intern' is absent. (+6 more)

### Community 66 - "get_job_by_id"
Cohesion: 0.17
Nodes (18): ApplyRunner, _ensure_tenant(), ApplyResult, Stamp job.tenant from the Workday URL when missing (LinkedIn→Workday case)., Drive Workday pre-fill for staged jobs with injectable Applicator., BlockerError, get_job_by_id(), FakeApplicator (+10 more)

### Community 67 - "test_workday_locators.py"
Cohesion: 0.40
Nodes (3): asyncio, Optional Playwright locator smoke test against a local HTML fixture. Skipped…, test_accessibility_locators_on_fixture()

### Community 72 - "OpenAIEmbedder"
Cohesion: 0.38
Nodes (4): OpenAIEmbedder, Any, OpenAI embeddings. Width is ``vector_dimensions``., _vectors_from_response()

### Community 75 - "test_gemini_client_falls_back_when_model_unavailable"
Cohesion: 0.38
Nodes (7): _FakeGenaiClient, asyncio, A 503 on the primary model must roll over to the configured fallback., Thinking can eat the whole budget; retry must raise max_output_tokens., test_gemini_client_complete_maps_system_blocks(), test_gemini_client_escalates_on_truncated_output(), test_gemini_client_falls_back_when_model_unavailable()

## Knowledge Gaps
- **42 isolated node(s):** `Project`, `Build order and status`, `Commands`, `Coding conventions`, `Workflow for implementing a step` (+37 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 638 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **13 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `get_settings()` connect `get_settings` to `main.py`, `compiler.py`, `linkedin_people.py`, `clients.py`, `answers.py`, `workday.py`, `typing`, `evaluate`, `builder.py`, `scorer/engine.py`, `models.py`, `LLMClient`, `test_robustness.py`, `suggest.py`, `Profile`, `test_resume.py`, `Job`, `Any`, `test_pacing.py`, `settings.py`, `telegram.py`, `Any`, `Settings`, `diff.py`, `db.py`, `test_answers.py`, `test_llm_provider.py`, `telemetry.py`, `benchmark/engine.py`, `prompts.py`, `skills.py`, `build_scheduler`, `test_vector_gate.py`, `TelegramClient`, `WorkdaySubmitter`, `runner.py`, `prep.py`, `scrape_profile`, `TokenUsage`, `targets.py`, `load_profile`, `outreach.py`, `test_linkedin_people.py`, `filters.py`, `OpenAIEmbedder`?**
  _High betweenness centrality (0.239) - this node is a cross-community bridge._
- **Why does `Job` connect `Job` to `main.py`, `compiler.py`, `answers.py`, `workday.py`, `typing`, `builder.py`, `scorer/engine.py`, `models.py`, `LLMClient`, `test_robustness.py`, `suggest.py`, `Profile`, `test_resume.py`, `test_pacing.py`, `test_handlers.py`, `bot/__init__.py`, `telegram.py`, `diff.py`, `db.py`, `test_answers.py`, `benchmark/engine.py`, `prompts.py`, `skills.py`, `test_apply_url.py`, `test_vector_gate.py`, `TelegramClient`, `WorkdaySubmitter`, `prerank.py`, `ingest.py`, `runner.py`, `prep.py`, `get_settings`, `test_poller.py`, `load_profile`, `outreach.py`, `test_build_role_baseline_persists`, `filters.py`, `get_job_by_id`?**
  _High betweenness centrality (0.135) - this node is a cross-community bridge._
- **Why does `session_scope()` connect `Job` to `main.py`, `compiler.py`, `typing`, `scorer/engine.py`, `LLMClient`, `test_robustness.py`, `suggest.py`, `Profile`, `test_resume.py`, `test_pacing.py`, `test_handlers.py`, `bot/__init__.py`, `telegram.py`, `diff.py`, `db.py`, `benchmark/engine.py`, `test_apply_url.py`, `test_vector_gate.py`, `TelegramClient`, `ingest.py`, `runner.py`, `prep.py`, `get_settings`, `test_poller.py`, `load_profile`, `test_build_role_baseline_persists`, `get_job_by_id`?**
  _High betweenness centrality (0.052) - this node is a cross-community bridge._
- **Are the 76 inferred relationships involving `Job` (e.g. with `Data model (core/db.py)` and `AnswerResolver`) actually correct?**
  _`Job` has 76 INFERRED edges - model-reasoned connections that need verification._
- **Are the 91 inferred relationships involving `Status` (e.g. with `Data model (core/db.py)` and `ApplyRunner`) actually correct?**
  _`Status` has 91 INFERRED edges - model-reasoned connections that need verification._
- **Are the 76 inferred relationships involving `Source` (e.g. with `Data model (core/db.py)` and `_eligible()`) actually correct?**
  _`Source` has 76 INFERRED edges - model-reasoned connections that need verification._
- **What connects `Project`, `Build order and status`, `Commands` to the rest of the system?**
  _42 weakly-connected nodes found - possible documentation gaps or missing edges._