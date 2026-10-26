# AGENTS.md

> Parts of this file are stale (Gemini, 3x/day APScheduler, Workday auto-fill as the main path). The current flow is in CLAUDE.md under Known state: discovery, scoring, shortlist, Telegram apply queue with Applied/Skip/Later, run by one external dispatch. The code wins over this file.

Guidance for AI agents and developers working on this repository. Read this before making changes.

## Project

Agentic, human-in-the-loop job discovery, scoring, and application engine. It runs (eventually 3x/day) to:

1. Discover jobs posted in the last 24h from LinkedIn/Indeed (JobSpy) and target Workday portals (CXS REST).
2. Pre-filter with hard negative rules, then score 0-100 with OpenAI (`gpt-5-mini` by default) against a grounded candidate profile.
3. Attach your base resume (`config/base_resume.pdf`) by default — or generate a Typst-tailored PDF on demand — and sanitize PDF metadata.
4. Pre-fill Workday applications with stealth Playwright and pause at the final review screen.
5. Send an interactive Telegram review (screenshot + link + drafted answers); never blind-submit.
6. Draft a referral/alumni outreach message for Tier-1 roles.

Everything is async Python. Applications are NEVER auto-submitted without human approval.

## Build order and status

| Step | Scope | Status |
|------|-------|--------|
| 1 | Foundations: config, profile, SQLite | Done |
| 2 | Ingestion: JobSpy + Workday REST | Done |
| 3 | Scorer: OpenAI `gpt-5-mini`, tiers, outreach | Done |
| 4 | Resume: base PDF default + Typst on demand + pikepdf | Done |
| 5 | Automation: Playwright Workday, vault, human telemetry | Done |
| 6 | Telegram review bot + FastAPI webhook | Done |
| 7 | Orchestration (APScheduler 3x/day) + Docker/VPS deploy | Done |
| 8 | Two-tier resume: role baseline from ~15-20 JDs, per-JD skill suggestions via Telegram Approve/Edit/Reject, one-page autofit | Done |
| 9 | LinkedIn peer benchmarking (ENABLE_LINKEDIN_SCRAPE; semi-auto peer URLs) | Done |

Update this table and the one in `README.md` as steps complete.

## Confirmed product decisions

- LLM provider: OpenAI only (`OPENAI_API_KEY`, `gpt-5-mini` for scoring and writing). Embeddings use the same key (`text-embedding-3-small`).
- Resume: default is the candidate's `config/base_resume.pdf` (copied per job + sanitized). Typst tailoring is on-demand via `main.py tailor-resume <job_id>` / `compile_for_job`.
- Automation posture: Workday = auto-fill + 1-tap submit (via Telegram). LinkedIn/Indeed Easy Apply = discovery + scoring + resume + prep pack (manual). LinkedIn/Indeed jobs whose `job_url_direct` is a company Workday page are auto-fill eligible like native Workday.
- Hosting: "run from anywhere" -> a cloud/VPS host is the target (Step 7); the automated browser will run there behind noVNC so takeover works from any device. Not local-machine-bound.
- Never blind-submit: the agent stops at the final review page and waits for a Telegram decision (Approve / Manual Takeover / Discard). Blockers (Cloudflare/MFA/unknown form) screenshot + alert + yield to manual.
- No hallucination: all candidate facts live in `config/profile.yaml`; the LLM may score/justify/phrase but must never invent background facts.

## Tech stack

- Python >= 3.12, fully async (`asyncio`).
- Package manager: `uv` (Astral). Deps in `pyproject.toml`; do not hand-edit versions—prefer `uv add`.
- Data models: Pydantic v2 (`pydantic`, `pydantic-settings`).
- DB: SQLModel + SQLAlchemy async — SQLite (`aiosqlite`) for local/tests; Neon Postgres (`asyncpg`) for cron/production via `DATABASE_URL`.
- HTTP: `httpx` (async) + `tenacity` retries. Scraping: `python-jobspy`, HTML clean via `selectolax`.
- LLM: OpenAI (`openai`) for scoring, writing, and embeddings via `build_llm_client()` / `build_embedder()`.
- Resume: `typst` (PyPI binding, no system binary) + `pikepdf` for metadata.
- Logging: `structlog`.
- Lint/format: `ruff`. Types: `pyright`. Tests: `pytest` + `pytest-asyncio` (asyncio_mode=auto).

Confirmed product decisions (resume / LinkedIn):
- Role baseline aggregates ~15-20 DB JDs matched to `preferences.titles`; incremental per-JD diffs propose only missing skills.
- Skill additions require Telegram Approve / Edit / Reject (`s1|<action>|<suggestion_id>`). Provenance is `grounded` (in profile) or `inferred` (would be invented).
- One-page guarantee: Typst compile loop with pikepdf page count + progressive fit levers.
- LinkedIn scrape is OFF by default (`ENABLE_LINKEDIN_SCRAPE`); use saved session + `--urls` or `--auto` for peer discovery. Pipeline benchmarking is gated by `ENABLE_BENCHMARK` (also off by default) and only runs for Tier-1 jobs.

## Commands

```bash
# Install (incl. dev tools)
uv sync --extra dev

# Lint (must pass, zero warnings)
uv run ruff check .
uv run ruff check --fix .   # auto-fix imports/format

# Tests (must be green; fully offline, no network/API key needed)
uv run pytest -q

# Run a single step manually (see README for each)
uv run python -c "import asyncio; from scraper import run_ingestion; print(asyncio.run(run_ingestion()))"
uv run python -c "import asyncio; from scorer import score_pending; print(asyncio.run(score_pending()))"
uv run python -c "import asyncio; from resume import prepare_pending; print(asyncio.run(prepare_pending()))"
uv run python main.py tailor-resume 42
uv run python main.py build-baseline "Software Engineer"
uv run python main.py suggest 42
uv run python main.py send-suggestions
uv run python main.py benchmark 42 --urls https://www.linkedin.com/in/peer1
uv run python main.py benchmark 42 --auto   # auto-discover peers (needs ENABLE_LINKEDIN_SCRAPE)
uv run python main.py prep-pack
uv run python -c "import asyncio; from automation import apply_pending; print(asyncio.run(apply_pending()))"
uv run python -c "import asyncio; from bot import send_pending_reviews; print(asyncio.run(send_pending_reviews()))"
uv run python main.py serve
uv run python main.py run-once
```

Always prefix Python with `uv run`. When running shell here, `export PATH="$HOME/.local/bin:$PATH"` if `uv` is not found.

One-time browser install (manual): `uv run playwright install chromium`.
One-time per-tenant session (manual): `from automation import save_session` — see README.
Telegram poller (manual): `from bot import run_polling` — or `uv run python main.py poll`.
Full service: `uv run python main.py serve` (scheduler + poller).
Docker: `docker compose up -d --build`.

## Repository layout

```text
config/
  settings.py     # pydantic-settings; get_settings(); PROJECT_ROOT; paths
  profile.py      # Pydantic Profile + load_profile()/reload_profile(); static_context_block()
  profile.yaml    # SINGLE SOURCE OF TRUTH for candidate facts (placeholders until filled)
  targets.py      # SearchConfig/WorkdayTenant/Targets; parse_workday_url(); load_targets()
  targets.yaml    # search terms/sites + Workday tenant careers URLs (placeholders)
core/
  db.py           # SQLModel engine + Job model + enums + upsert/query helpers
  textmatch.py    # SHARED matching: company_matches/location_matches/contains_phrase/truncate_middle
  token_optimizer.py  # cache_block(), minify_job(), approx_tokens(), compact_json_dumps()
scraper/
  models.py       # RawPosting + to_job() + content_hash mapping
  textclean.py    # html_to_text(), extract_sections(), content_hash()
  filters.py      # negative pre-filter: evaluate() -> FilterResult
  linkedin_jobspy.py  # async JobSpy wrapper (hours_old=24), client-side location filter
  workday_rest.py # async CXS client (paginate 20, recency shortlist, detail fetch, bot-block soft-fail)
  ingest.py       # run_ingestion(): fetch -> clean -> filter -> upsert; IngestSummary
scorer/
  schemas.py      # ScoreRaw ({"s","t","r"}) + Evaluation + SCORE_JSON_SCHEMA
  prompts.py      # cached rubric/system blocks, outreach prompt, BANNED_WORDS
  clients.py      # LLMClient protocol, Gemini/Anthropic clients, retry + model fallback
  engine.py       # parse_score, compute_tier, Scorer, score_pending (re-exports clients)
  outreach.py     # generate_outreach() + banned-word gate/retry + grounded fallback
resume/
  skills.py       # JdSkill/SkillCategory, extract_top_skills (+deterministic), aggregate_role_skills
  selector.py     # deterministic JD-term -> top 4-6 verified bullets; reorder_skills; build_resume_data
  compiler.py     # prepare_pending (base PDF), compile_resume/compile_for_job (Typst), sanitize_pdf
  templates/resume.typ  # one-page template; reads json(bytes(sys.inputs.data))
prep/
  questions.py    # IDENTITY / ESSAY / MANUAL_FILL question bank for LinkedIn/Indeed
  builder.py      # generate_prep_pack (Markdown + Typst PDF)
  templates/prep_pack.typ
automation/       # Step 5: Playwright Workday pre-fill (never submit)
  telemetry.py    # human_delay / type_like_human
  vault.py        # credentials + session_state paths
  answers.py      # AnswerResolver (profile facts + writer_model open-ended)
  browser.py      # stealth Chromium + storage_state
  login.py        # one-time interactive save_session (manual)
  workday.py      # WorkdayApplicator + BlockerError
  runner.py       # apply_pending() -> pending_review | manual_review
bot/              # Step 6: Telegram review + 1-tap submit
  telegram.py     # TelegramClient + encode/decode_callback (+ tenacity retry) + send_document
  review.py       # send_pending_reviews (screenshot + keyboard)
  alerts.py       # send_pending_alerts (manual_review -> Telegram; scoring errors stay in the DB)
  prep.py         # send_prep_pack (LinkedIn/Indeed Markdown+PDF via Telegram)
  submit.py       # WorkdaySubmitter (ONLY place that clicks Submit)
  handlers.py     # Approve / Manual / Discard callback dispatch
  poller.py       # long-poll getUpdates (primary local path)
  webhook.py      # FastAPI /telegram/webhook (optional production alt)
orchestrator/     # Step 7: single-process runtime
  pipeline.py     # run_pipeline() ingest->score->resume->prep->apply->reviews->alerts
  scheduler.py    # build_scheduler() CronTrigger per schedule_times
  service.py      # run_service() scheduler + poller, graceful shutdown
main.py           # CLI: serve | run-once | poll | send-reviews | prep-pack | webhook
Dockerfile        # mcr.microsoft.com/playwright/python + uv
docker-compose.yml
storage/
  sessions/  resumes/  screenshots/  prep_packs/   # runtime artifacts (gitignored)
tests/            # pytest suite (offline; mock LLM client; temp DB)
```

Runtime model (Step 7): one async process — `AsyncIOScheduler` fires `run_pipeline()` at each `SCHEDULE_TIMES` entry (timezone-aware); a concurrent `run_polling()` task handles Telegram taps. Per-stage try/except isolation: one failure never aborts later stages. Pipeline stages: ingest → score → resume → **prep** → apply → reviews → alerts. `ENABLE_APPLY` / `ENABLE_REVIEWS` / `ENABLE_PREP_PACK` toggles skip Workday/Telegram/prep stages when sessions or tokens are not ready. Prep packs require `ENABLE_REVIEWS` (Telegram delivery). Brief mode sends one text file of the persisted shortlist, in shortlist order. It does not fill that file from other scores. An empty shortlist stays empty. `SCORE_BUDGET` unset means every job that passes filters and the embedding gate is scored. noVNC browser takeover is an optional follow-up (not in-tree).

Types: `uv run pyright` must report 0 errors (same bar as ruff/pytest).
## Data model (core/db.py)

`Job` table, unique on `(source, external_id)`; JSON column for `justification`.

- Identity/dedup: `source`, `external_id`, `tenant`, `content_hash`.
- Posting: `title`, `company`, `location`, `url`, `description_clean`, `posted_at`, `discovered_at`.
- Scoring: `score` (0-100), `tier`, `justification` (list[str]), `outreach_draft`, `cover_letter`, `scored_at`, `embedding` (JD vector), `vector_score`, `vector_profile_hash`, `vector_decision` (`pass`, `reject`, or `recovered`), `vector_recovery`, `vector_recovery_reason`, `vector_recovery_hash`. A changed `content_hash` clears the vector and recovery fields. `career_intelligence` is a separate per-job reading and does not change fit, priority, or shortlist membership.
- Workflow: `status`, `resume_path`, `screenshot_path`, `application_answers` (dict JSON), `review_message_id`, `review_chat_id`, `decided_at`, `outcome`, `outcome_at`, `outcome_message_id`, `last_error`, `alerted_at`, `prep_pack_sent_at`, `created_at`, `updated_at`.

`PlatformPacing` table, primary key `platform` (the apply runner uses `workday`): `multiplier`, `clean_streak`, `blocked_until`, `next_eligible_at`, `updated_at`. Compare those timestamps with `_as_utc`; SQLite returns them naive.

Enums:
- `Source`: linkedin | indeed | workday
- `Tier`: one | two | three
- `Outcome`: ghosted | screening | interview | rejected | offer (nullable; not a status)
- `Status`: discovered | filtered_out | scored | staged | pending_review | submitted | manual_review | ignored | error

### Status lifecycle

```
discovered --(negative filter fail)--> filtered_out
discovered --(scorer)--> staged (Tier 1/2)  |  filtered_out (Tier 3)  |  error (LLM/parse failure)
staged + resume_path set (Step 4)
staged LinkedIn/Indeed --(send_prep_pack)--> Telegram Markdown+PDF (prep_pack_sent_at set)
staged --(Step 5 Workday pre-fill)--> pending_review (+ screenshot_path, application_answers)
  |-- BlockerError --> manual_review (+ screenshot_path)
pending_review --(send_pending_reviews)--> review card on Telegram (review_message_id set)
manual_review --(send_pending_alerts)--> Telegram alert (alerted_at set; screenshot if present)
error (scoring failure) stays in the database and is not alerted
pending_review --(Telegram Approve)--> submitted | manual_review (if submit blocked)
pending_review --(Telegram Manual)--> manual_review
pending_review --(Telegram Discard)--> ignored
```

Helpers: `init_db()`, `reset_engine()` (tests), `session_scope()`, `upsert_job()` (idempotent; refreshes posting fields; only overrides status/justification while `discovered`/`filtered_out`; a changed `content_hash` rewinds `scored`/`staged` jobs to `discovered` so a rewritten JD is re-scored, leaving human-touched states alone), `get_job_by_id()`, `get_job_by_source_id()`, `get_jobs_by_status()`, `get_unsent_pending_reviews()`, `get_unsent_alerts()`, `get_unsent_prep_pack_jobs()`.

Note: `create_all` does NOT ALTER an existing SQLite file. When adding columns, delete `storage/job_agent.db` in dev (`rm -f storage/job_agent.db`). Tests use fresh temp DBs.

## LLM client layer (`scorer/clients.py`)

Provider clients live in `scorer/clients.py`; `scorer/engine.py` re-exports
`LLMClient` / `GeminiClient` / `AnthropicClient` / `build_llm_client` for back-compat.
`build_llm_client()` returns `OpenAIClient`. The Gemini notes below describe that
retained client. They are not the live scoring path.

- Per-role models: `GEMINI_SCORER_MODEL` (fast, high volume) vs `GEMINI_WRITER_MODEL`
  (deep reasoning, few calls). Thinking level is per-role too
  (`GEMINI_SCORER_THINKING_LEVEL=low`, `GEMINI_WRITER_THINKING_LEVEL=high`) and is
  passed per call — never read from a global inside the client.
- `call_with_resilience()` retries transient failures (429 / 503 / 500 / timeouts)
  up to `LLM_MAX_ATTEMPTS` per model, honoring the server's `retryDelay` hint when
  present, then falls over to the next model in `GEMINI_FALLBACK_MODELS`.
- Billing exhaustion (`prepayment credits are depleted`, invalid key) also arrives as
  429 but raises `LLMBillingError` immediately — no retries, no fallback. Retrying it
  across the whole chain wastes ~2 minutes per call.
- Truncation: Gemini thinking tokens draw from `max_output_tokens`, so an empty reply
  with `finish_reason=MAX_TOKENS` triggers one retry at 3x budget with thinking lowered.
- Unsupported `thinking_level` values are detected at call time (not build time),
  remembered per model, and dropped on retry.
- Scoring passes `SCORE_JSON_SCHEMA` as Gemini `response_schema` alongside
  `response_mime_type=application/json` (verified live against `gemini-3.6-flash`).

## Scoring specifics (Step 3)

- Prompt caching: `build_scoring_system_blocks(profile)` returns a single cached block (candidate `static_context_block()` + rubric) so the static prefix is reused across jobs in a run. Dynamic user message is the minified JD only.
- Output contract: compact JSON `{"s":<0-100>,"t":<1|2|3>,"r":["..."]}` enforced via `response_schema`. `parse_score()` stays tolerant (strips fences/prose, brace-balanced extraction that survives `{}` inside strings). A non-numeric `s` now raises instead of silently becoming 0/Tier 3. Tier is recomputed in code via `compute_tier()` (model `t` is only a hint).
- Throughput: `score_pending` launches all jobs behind a `SCORER_CONCURRENCY` semaphore (default 8). `stop_after_staged=N` is checked **per job**, so queued jobs are skipped the moment the target is met (reported as `summary.skipped`) instead of paying for a whole wave.
- Outreach is isolated: a failed Tier-1 draft is logged and the score still persists. Previously any outreach exception pushed a valid Tier-1 job to `Status.error`.
- Pre-filter hard negatives (ingest + scoring backlog guard): company/keyword/clearance/staffing/location, plus seniority titles (`ENABLE_SENIORITY_FILTER` + `SENIORITY_TITLE_KEYWORDS`) and sponsorship-hostile language. The YOE gate is profile-aware: the ceiling is the candidate's own experience (`Profile.total_years_experience()`) plus `YEARS_EXPERIENCE_SLACK`, overridable via `MAX_REQUIRED_YEARS_EXPERIENCE`. A JD is dropped only when its *lowest* stated requirement is out of reach, so "3+ required / 10+ preferred" survives.
- Tier mapping: Tier 1 = score>=`TIER_ONE_MIN_SCORE` OR company in `preferences.dream_companies` -> `staged` + outreach draft. Tier 2 = >=`TIER_TWO_MIN_SCORE` -> `staged`. Tier 3 -> `filtered_out`. Dream-company matching normalizes legal suffixes, so "Google" matches "Google LLC".
- `build_llm_client()` always returns `OpenAIClient`. It raises if `OPENAI_API_KEY` is empty. Tests inject a `FakeClient` implementing the `LLMClient` protocol (no network).
- Model ids: `openai_scorer_model` / `openai_writer_model`. Callers use `settings.active_scorer_model` / `settings.active_writer_model`, which always resolve to those.
- Anti-AI style gate: `BANNED_WORDS` (delve, tapestry, beacon, testament, "thrilled to apply", etc.). Outreach retries once, then strips offending sentences.

## Coding conventions

- Async-first: `asyncio`, `httpx.AsyncClient`, `playwright.async_api` (Step 5). Wrap sync libs (JobSpy) with `asyncio.to_thread`.
- Pydantic v2 everywhere for I/O boundaries; type-annotate all public functions.
- `from __future__ import annotations` at top of modules.
- Line length 100; ruff rules `E,F,I,UP,B`. Keep imports sorted (ruff `I`).
- Comments explain intent/trade-offs only—no narration of what code does.
- Robust error handling: per-item failures in batch pipelines are logged (structlog) and isolated; one bad job/tenant never crashes a run.
- Safety-first automation (Step 5+): on Cloudflare/MFA/unknown form, screenshot + Telegram blocker alert + yield to manual; do not crash.
- Locators (Step 5): accessibility-first only (`get_by_role`, `get_by_label`, `get_by_placeholder`). Never brittle CSS/absolute XPath.
- Matching (companies, locations, banned words) goes through `core/textmatch.py`. Do not reintroduce `needle in haystack` substring checks: they made "Meta" block "MetLife" and "Portland, OR" satisfy a "Portland, ME" preference.
- Unanswerable form fields resolve to `AnswerSource.needs_review` (not a silent blank) when the label looks submission-blocking (salary, start date, notice period, clearance...).
- Screening answers/outreach: 1-3 clear sentences; no banned buzzwords.
- Prefer editing existing files; add durable pytest coverage for new logic.

## Testing conventions

- Fully offline and deterministic. No real network or API key in tests.
- `tests/conftest.py` provides: `tmp_db` (temp DATABASE_URL + cache clears), `db_ready` (async, fresh DB + `reset_engine`), `profile` (loads profile.yaml).
- Mock the LLM via a `FakeClient` matching `scorer.engine.LLMClient`.
- Resume tests actually compile with Typst (no network) and read metadata back with pikepdf.
- After edits, run `uv run ruff check .` and `uv run pytest -q`; both must pass.

## What still needs the user (before live runs)

- Fill `config/profile.yaml` with real candidate facts (replace all `PLACEHOLDER_*`).
- Save your resume PDF as `config/base_resume.pdf` (used by default for applications).
- Fill `config/targets.yaml`: real search terms + at least one real Workday careers URL (placeholder tenants are auto-skipped).
- Put `OPENAI_API_KEY` in `.env`. Scoring uses OpenAI (`gpt-5-mini`).
- Step 5 manual: `uv run playwright install chromium`; fill real Workday URLs in `targets.yaml`; run `save_session` once per tenant.
- Step 6 manual: create a bot with @BotFather; set `TELEGRAM_BOT_TOKEN` + `TELEGRAM_CHAT_ID` in `.env`.
- Step 7 manual: confirm `SCHEDULE_TIMES` / `TIMEZONE`; run `save_session` on the host before Docker; `docker compose up -d` on a VPS.
- Optional later: noVNC sidecar for live browser takeover; webhook URL + secret.

## Workflow for implementing a step

1. In Plan mode, read the relevant code and ask 1-2 critical questions, then produce a plan (CreatePlan) with todos.
2. In Agent mode, implement todo-by-todo (mark in_progress/completed), do not edit the plan file.
3. Add/extend tests; run ruff + pytest until green.
4. Update `README.md` status table and this file's status table.
