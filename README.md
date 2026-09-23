# Job Agent

Agentic, human-in-the-loop job discovery, scoring, and application engine.

Discovers jobs from LinkedIn/Indeed and Workday portals, scores them with Gemini (default; Anthropic optional) against a grounded candidate profile, attaches your base resume PDF (or a Typst-tailored one on demand), sends LinkedIn/Indeed application prep packs via Telegram, pre-fills Workday applications, and pauses for Telegram approval before any submit.

## Status

| Step | Scope | Status |
|------|--------|--------|
| 1 | Foundations (config, profile, SQLite) | Done |
| 2 | Ingestion (JobSpy + Workday REST) | Done |
| 3 | Scorer (Gemini / Anthropic, tiers) | Done |
| 4 | Resume (base PDF default + Typst on demand) | Done |
| 5 | Automation (Playwright Workday) | Done |
| 6 | Telegram review bot | Done |
| 7 | Orchestration & deploy | Done |
| 8 | Two-tier resume (role baseline + Telegram skill suggestions + one-page autofit) | Done |
| 9 | LinkedIn peer benchmarking (optional, off by default) | Done |

## Setup

Requires Python 3.12+ and [uv](https://docs.astral.sh/uv/).

```bash
# Install dependencies
uv sync --extra dev

# Copy env and fill in secrets
cp .env.example .env

# Edit your grounded candidate profile
# config/profile.yaml
```

## Smoke-check (Step 1)

```bash
uv run python -c "
import asyncio
from config.settings import get_settings
from config.profile import load_profile
from core.db import init_db

settings = get_settings()
profile = load_profile()
asyncio.run(init_db())
print('settings OK:', settings.database_url)
print('profile OK:', profile.identity.full_name)
print('db OK: storage/job_agent.db')
"
```

## Run ingestion (Step 2)

Edit `config/targets.yaml` (search terms + real Workday careers URLs), then:

```bash
uv run python -c "
import asyncio
from scraper import run_ingestion

summary = asyncio.run(run_ingestion())
print(summary)
"
```

Placeholder Workday tenants are skipped automatically. LinkedIn/Indeed calls may be rate-limited.

## Run scoring (Step 3)

Put your Gemini key in `.env` (`LLM_PROVIDER=gemini`, `GEMINI_API_KEY=...`), then score discovered jobs:

```bash
uv run python -c "
import asyncio
from scorer import score_pending

summary = asyncio.run(score_pending())
print(summary)
"
```

Tiers: 1 (score ≥ 85 or dream company) and 2 (65–84) → `staged`; 3 (< 65) → `filtered_out`.
Tier-1 jobs also get an `outreach_draft`. Offline tests use a mock LLM client (no API key required).

If you already have a local `storage/job_agent.db` from before Step 3, delete it once so new columns (`outreach_draft`, `scored_at`) are created:

```bash
rm -f storage/job_agent.db
```

## Resumes (Step 4)

By default the pipeline attaches **your** PDF from `config/base_resume.pdf` (copied per job + metadata sanitized):

```bash
uv run python -c "
import asyncio
from resume import prepare_pending

summary = asyncio.run(prepare_pending())
print(summary)
"
```

Output path: `storage/resumes/{job_id}/First_Last_Resume.pdf`. Status stays `staged`; `resume_path` marks completion for automation.

**On demand** — generate a Typst-tailored resume for one job (uses `profile.yaml` bullets/skills):

```bash
uv run python main.py tailor-resume <job_id>
```

### Two-tier resume (role baseline + Telegram skill suggestions)

1. **Build a role baseline** once (aggregates the latest ~15–20 matching JDs from your DB):

```bash
uv run python main.py build-baseline "Software Engineer"
# rebuild later:
uv run python main.py build-baseline "Software Engineer" --refresh
```

2. **Diff a new JD** against that baseline and queue suggestions (missing skills only):

```bash
uv run python main.py suggest <job_id>
uv run python main.py send-suggestions   # Telegram Approve / Edit / Reject
```

3. After you decide each suggestion, the agent recompiles a **one-page** autofit resume. Inferred skills only land after your explicit Approve/Edit.

### LinkedIn peer benchmarking (optional, off by default)

```bash
# one-time: save LinkedIn session (headful MFA)
uv run python -c "import asyncio; from scraper.linkedin_session import save_linkedin_session; print(asyncio.run(save_linkedin_session()))"

# set ENABLE_LINKEDIN_SCRAPE=true in .env, then:
uv run python main.py benchmark <job_id> --urls https://www.linkedin.com/in/peer1 https://www.linkedin.com/in/peer2 --scrape
```

Reports land in `storage/benchmarks/{job_id}/`. Semi-automated peer URLs are the default; full people-search crawl stays behind `LINKEDIN_AUTO_SEARCH`.

## Application prep packs (LinkedIn / Indeed)

Staged LinkedIn/Indeed jobs cannot be auto-filled (ban risk). Instead the agent builds a **combined** Markdown + PDF prep pack of grounded answers (standard identity fields + common essays) and sends both files to Telegram.

```bash
uv run python main.py prep-pack
```

Also runs automatically in the pipeline after resume prep when `ENABLE_PREP_PACK=true` and `ENABLE_REVIEWS=true`. Jobs are marked with `prep_pack_sent_at` so each is included once. Files land in `storage/prep_packs/`.

If you already have a local DB from before this column existed:

```bash
rm -f storage/job_agent.db
```

## Run automation (Step 5)

Pre-fills **Workday** applications for `staged` jobs that already have a `resume_path`. Stops at the final review screen (never clicks Submit), saves a screenshot, and sets status to `pending_review`. Blockers (Cloudflare/MFA/missing session) → `manual_review`.

```bash
# One-time (manual): install Chromium
uv run playwright install chromium

# One-time per tenant (manual): save a reusable login session (headful)
uv run python -c "
import asyncio
from automation import save_session
print(asyncio.run(save_session('https://TENANT.wd5.myworkdayjobs.com/en-US/External')))
"

# Pre-fill staged Workday jobs
uv run python -c "
import asyncio
from automation import apply_pending
print(asyncio.run(apply_pending()))
"
```

LinkedIn/Indeed stay discovery + resume only (no auto-apply). Optional `config/credentials.yaml` (copy from `credentials.example.yaml`) is reserved for a future auto-login fallback; the default flow uses the saved session only.

If you already have a local DB from before Step 5, delete it once so the new `application_answers` column is created:

```bash
rm -f storage/job_agent.db
```

## Run review bot (Step 6)

Interactive Telegram review for `pending_review` jobs. Sends a screenshot + facts + drafted answers with Approve / Manual Takeover / Discard buttons. **Approve** reopens the saved Workday session and clicks Submit (the only place Submit is ever clicked). Manual → `manual_review`; Discard → `ignored`.

Blocked / errored jobs (`manual_review` from Cloudflare/MFA, or `error` from apply/scoring failures) get a separate Telegram **alert** (screenshot + reason) via `send_pending_alerts` — they are no longer silent. The full pipeline runs alerts after reviews.

```bash
# Put TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID in .env first (manual placeholders).

# Send review cards for unsent pending_review jobs
uv run python -c "
import asyncio
from bot import send_pending_reviews
print(asyncio.run(send_pending_reviews()))
"

# Send blocker/error alerts
uv run python -c "
import asyncio
from bot import send_pending_alerts
print(asyncio.run(send_pending_alerts()))
"

# Long-poll for button taps (Ctrl+C to stop)
uv run python -c "
import asyncio
from bot import run_polling
asyncio.run(run_polling())
"
```

Optional production webhook (Step 7): set `TELEGRAM_WEBHOOK_URL` + `TELEGRAM_WEBHOOK_SECRET`, then serve `bot.app` with uvicorn. Local runs use long-polling only.

If you already have a local DB from before the alert columns (`last_error`, `alerted_at`), delete it once:

```bash
rm -f storage/job_agent.db
```

## Run the full service (Step 7)

One long-running process: APScheduler fires the full pipeline (ingest → score → resume → prep → apply → send reviews → alerts) at each `SCHEDULE_TIMES` entry, while a concurrent Telegram long-poller handles Approve / Manual / Discard taps.

```bash
# Run scheduler + poller (Ctrl+C for graceful shutdown)
uv run python main.py serve

# Or run the pipeline once (debug / cron)
uv run python main.py run-once

# Other subcommands
uv run python main.py poll           # Telegram poller only
uv run python main.py send-reviews   # send pending cards once
uv run python main.py prep-pack      # LinkedIn/Indeed prep pack once
uv run python main.py webhook        # FastAPI webhook (optional alt to poll)
```

Toggles in `.env`: `ENABLE_APPLY=false` / `ENABLE_REVIEWS=false` / `ENABLE_PREP_PACK=false` skip Workday pre-fill / Telegram send / prep packs (useful before sessions exist). Stage failures are isolated — one bad stage never aborts the rest of the run.

## Deploy with Docker

Headless-first container (Playwright Chromium preinstalled). Persist `storage/` and mount your filled config:

```bash
# One-time on the host (manual): create credentials file if missing
cp -n config/credentials.example.yaml config/credentials.yaml

# One-time on the host (manual): save Workday sessions headfully BEFORE containerizing
# so storage/sessions/*.json are reused inside the container
uv run playwright install chromium
uv run python -c "import asyncio; from automation import save_session; \
  print(asyncio.run(save_session('https://TENANT.wd5.myworkdayjobs.com/en-US/External')))"

# Build and run
docker compose up -d --build
docker compose logs -f job-agent
```

Volumes: `./storage` (DB + sessions + resumes + screenshots), read-only mounts for `config/profile.yaml`, `config/targets.yaml`, `config/credentials.yaml`. Set secrets in `.env`.

**Optional follow-up (not included):** a noVNC sidecar for live browser takeover from any device. The current stack is headless; run `save_session` on the host when sessions expire.

## Layout

```text
config/         # Settings + grounded candidate profile
core/           # DB, logging, token optimizer
scraper/        # LinkedIn/Indeed + Workday discovery
scorer/         # LLM match evaluator
resume/         # Base PDF + Typst templates
prep/           # LinkedIn/Indeed application prep packs
automation/     # Playwright agents
bot/            # Telegram + FastAPI webhook
orchestrator/   # Pipeline + APScheduler + service
main.py         # CLI: serve | run-once | poll | send-reviews | prep-pack | webhook
Dockerfile      # Playwright python image + uv
docker-compose.yml
storage/        # Sessions, resumes, screenshots, prep_packs
```
