# Remaining Manual Setup

Everything agent-side is done (code, deps, Chromium, your resume at `config/base_resume.pdf`, `profile.yaml`, search terms, Gemini + Telegram already in `.env`).

This file lists **only what you still need to do by hand**, in order.

---

## Quick status

| Item | Status |
|------|--------|
| Install tools / Playwright | Done |
| Resume PDF → `config/base_resume.pdf` | Done |
| `config/profile.yaml` (from resume) | Done (2 small TODOs left) |
| Search terms in `config/targets.yaml` | Done |
| `GEMINI_API_KEY` in `.env` | Done |
| `TELEGRAM_BOT_TOKEN` + `TELEGRAM_CHAT_ID` in `.env` | Done |
| Real Workday careers URLs | **Pending (you)** |
| Save Workday login sessions | **Pending (you)** |
| Optional profile address / GitHub | **Pending (you)** |
| First live test run | **Pending (you)** |

---

## Step 1 — Finish two optional fields in `profile.yaml` (5 minutes)

Open `config/profile.yaml` and replace:

1. **`github_url`** — if you have a GitHub profile, put the full URL (e.g. `https://github.com/yourhandle`). Leave `""` if you don't use GitHub.
2. **`address.street`** and **`address.zip`** — your US mailing address (Seattle). Used only when Workday forms ask for street / ZIP. City/state/country are already set.

Example:

```yaml
  github_url: "https://github.com/yourhandle"   # or leave ""
  address:
    street: "123 Example Ave Apt 4"
    city: "Seattle"
    state: "WA"
    zip: "98105"
    country: "United States"
```

You can skip this until you start Workday auto-apply; LinkedIn/Indeed discovery and scoring do not need street/ZIP.

---

## Step 2 — Add real Workday company careers URLs (required for auto-apply)

LinkedIn/Indeed discovery already works from the search terms. **Workday auto-fill only works** for companies you list with a real careers URL.

### 2a. Find a Workday URL

1. Open a company's careers / jobs site in your browser.
2. Look at the address bar. A Workday site looks like:

```text
https://nvidia.wd5.myworkdayjobs.com/NVIDIAExternalCareerSite
```

or

```text
https://company.wd1.myworkdayjobs.com/External
```

If the host contains `myworkdayjobs.com`, it is a Workday tenant. Copy that full careers (or site) URL.

### 2b. Edit `config/targets.yaml`

Replace the placeholder block under `workday_tenants:` with real companies. Example with two tenants:

```yaml
workday_tenants:
  - name: "NVIDIA"
    url: "https://nvidia.wd5.myworkdayjobs.com/NVIDIAExternalCareerSite"
    search_terms: []          # empty = use the Product Manager / Consultant terms above

  - name: "SomeCompany"
    url: "https://somecompany.wd5.myworkdayjobs.com/External"
    search_terms: []
```

Rules:
- `name` is a short label (used for session files).
- `url` must be a **real** Workday careers URL — do not invent tenant/shard names.
- Any entry still containing `placeholder` is **skipped** automatically.
- You can start with **one** company and add more later.

Until this step is done, the agent can still **discover + score** LinkedIn/Indeed jobs, but it will **not** pre-fill Workday applications.

---

## Step 3 — Save a Workday login session (once per company)

**Why:** Logging in every run triggers MFA / bot walls. You log in once; the agent reuses a saved session file.

**Requirements:**
- You already created an account on that company's Workday careers site (email verification done).
- You are on a machine **with a screen** (a browser window will open).

### 3a. Run the save-session helper

From the project folder, replace the URL with **one** careers URL from Step 2:

```bash
cd "/Users/vikashdadhich/Documents/Automatic job search"
export PATH="$HOME/.local/bin:$PATH"

uv run python -c "
import asyncio
from automation import save_session
print(asyncio.run(save_session('https://nvidia.wd5.myworkdayjobs.com/NVIDIAExternalCareerSite')))
"
```

### 3b. What you do in the browser

1. A Chromium window opens on the careers site.
2. Sign in (and complete MFA if asked).
3. Wait until you can see the logged-in careers site (jobs list / account menu).
4. Return to the **terminal** and press **Enter**.
5. Session is written under `storage/sessions/` (gitignored).

Repeat Step 3 for **each** Workday company you added.

If a session expires later (login walls again), re-run the same command for that company.

---

## Step 4 — First live test (recommended order)

Run stages one at a time the first time so you can see each part working.

Open a terminal:

```bash
cd "/Users/vikashdadhich/Documents/Automatic job search"
export PATH="$HOME/.local/bin:$PATH"
```

### 4a. Discover jobs (LinkedIn / Indeed + any real Workday tenants)

```bash
uv run python -c "import asyncio; from scraper import run_ingestion; print(asyncio.run(run_ingestion()))"
```

### 4b. Score with Gemini

Enable **Gemini paid billing** for useful throughput (free tier is ~5 req/min and will stall). Optional knobs in `.env`:

```text
SCORER_CONCURRENCY=8                            # parallel scoring workers
GEMINI_SCORER_MODEL=gemini-3.6-flash            # fast, runs on every job
GEMINI_SCORER_THINKING_LEVEL=low                # keeps scoring ~3s/job
GEMINI_WRITER_MODEL=gemini-3.1-pro-preview      # deep reasoning, few calls
GEMINI_WRITER_THINKING_LEVEL=high               # outreach / essays only
GEMINI_FALLBACK_MODELS=["gemini-3.8-flash","gemini-3.6-flash"]
```

Why split the models: scoring runs on every discovered job, so it wants the cheap
fast model; outreach and essay answers run on a handful of Tier-1 jobs, where the
deeper model is worth it. The agent automatically fails over to
`GEMINI_FALLBACK_MODELS` when the primary returns 503 (common on newly released
models) or is rate-limited.

If your Gemini credits run out, calls fail immediately with
`LLMBillingError: account cannot serve requests` instead of retrying for minutes.
Top up at [AI Studio](https://ai.studio/projects) when you see it.

Score the backlog (or stop once N jobs are staged):

```bash
uv run python -c "import asyncio; from scorer import score_pending; print(asyncio.run(score_pending()))"
# On-demand: stop after 2 staged
uv run python -c "import asyncio; from scorer import score_pending; print(asyncio.run(score_pending(stop_after_staged=2)))"
```

### 4c. Attach your base resume to staged jobs

```bash
uv run python -c "import asyncio; from resume import prepare_pending; print(asyncio.run(prepare_pending()))"
```

(Uses `config/base_resume.pdf`. Optional tailor for one job: `uv run python main.py tailor-resume <job_id>`.)

### 4d. Send LinkedIn/Indeed application prep pack (Telegram)

Staged LinkedIn/Indeed jobs get a **combined** Markdown + PDF document with drafted answers (identity fields + common essays), grounded in your profile and filtered for AI buzzwords. Copy-paste when you apply manually.

```bash
uv run python main.py prep-pack
```

Toggle in `.env`: `ENABLE_PREP_PACK=true` (also requires Telegram / `ENABLE_REVIEWS=true` in the full pipeline). Each job is included once (`prep_pack_sent_at`).

If you already have a local DB from before this feature, reset it once so the new column exists:

```bash
rm -f storage/job_agent.db
```

### 4e. Pre-fill Workday applications (only if Steps 2–3 are done)

If you are **not** ready for Workday yet, skip this and set in `.env`:

```text
ENABLE_APPLY=false
```

When ready:

```bash
uv run python -c "import asyncio; from automation import apply_pending; print(asyncio.run(apply_pending()))"
```

### 4f. Send Telegram review cards

```bash
uv run python -c "import asyncio; from bot import send_pending_reviews; print(asyncio.run(send_pending_reviews()))"
```

Check Telegram for a screenshot + Approve / Manual / Discard.

### 4g. Listen for your button taps

Keep this running (Ctrl+C to stop):

```bash
uv run python -c "import asyncio; from bot import run_polling; asyncio.run(run_polling())"
```

Tap **Approve** only when you want that application submitted.

---

## Step 5 — Run the full service (after the test works)

Scheduler (3x/day per `SCHEDULE_TIMES`) + Telegram listener together:

```bash
uv run python main.py serve
```

Useful one-shots:

```bash
uv run python main.py run-once       # full pipeline once now
uv run python main.py poll           # Telegram taps only
uv run python main.py send-reviews   # push pending review cards
```

---

## Neon Postgres + GitHub Actions cron (off-laptop)

The pipeline can run 3x/day on GitHub Actions against a Neon Postgres database so your laptop does not need to stay on.

### Already done by the agent

- Neon project `job-agent` (Postgres 16, `aws-us-west-2`)
- Dual-dialect `DATABASE_URL` support (SQLite local / `postgresql+asyncpg` Neon)
- Workflow file: `.github/workflows/pipeline.yml` (`ENABLE_APPLY=false`)

### Manual steps (you)

1. Push this repo to GitHub (private recommended).
2. In the repo → **Settings → Secrets and variables → Actions**, add:
   - `DATABASE_URL` — Neon connection string (`postgresql+asyncpg://...` or plain `postgresql://...` from the Neon console)
   - `GEMINI_API_KEY`
   - `TELEGRAM_BOT_TOKEN`
   - `TELEGRAM_CHAT_ID`
3. Ensure `config/base_resume.pdf`, `config/profile.yaml`, and `config/targets.yaml` are in the repo (or available to the checkout).
4. Trigger **Actions → Job Pipeline → Run workflow** once to verify.
5. Cron fires at ~08:00 / 13:00 / 18:00 America/Los_Angeles (UTC schedule in the workflow file).

Until the Telegram webhook is deployed, approve/reject skill suggestions by running locally:

```bash
uv run python main.py poll
```

### Optional later — Telegram webhook (always-on button taps)

`bot/webhook.py` already exposes `POST /telegram/webhook`. To stop needing a local poller:

1. Deploy FastAPI (Fly.io / Railway / Vercel) with `DATABASE_URL` + Telegram secrets.
2. Set `TELEGRAM_WEBHOOK_URL` and `TELEGRAM_WEBHOOK_SECRET` in that host's env.
3. Register the webhook: `uv run python -c "import asyncio; from bot.telegram import TelegramClient; print(asyncio.run(TelegramClient().set_webhook('https://YOUR_HOST/telegram/webhook', secret_token='...')))"`

---

## Optional later — Docker / VPS (24/7)

Only after local Steps 2–5 work:

1. Copy the project to a server (include `.env`, filled YAML, `config/base_resume.pdf`, and `storage/sessions/`).
2. On the server:

```bash
docker compose up -d --build
docker compose logs -f job-agent
```

If a Workday session expires on the server, re-run Step 3 on a machine with a screen and copy the new file from `storage/sessions/` up.

---

## Checklist (your remaining work)

- [ ] Push repo to GitHub + add Actions secrets (`DATABASE_URL`, Gemini, Telegram)
- [ ] Trigger **Job Pipeline** workflow once to verify Neon cron
- [ ] (Optional) Fill GitHub URL + street/ZIP in `config/profile.yaml`
- [ ] Add at least one real Workday URL in `config/targets.yaml`
- [ ] Run `save_session` once per Workday company
- [ ] Test: ingest → score → prepare resume
- [ ] (When ready) Test: apply → Telegram reviews → poll / Approve
- [ ] Run `uv run python main.py serve` (local) or rely on GitHub Actions cron
- [ ] (Optional) Deploy Telegram webhook for always-on button taps
- [ ] (Optional) Deploy with Docker / VPS for Workday apply

---

## If something fails

| Symptom | What to check |
|---------|----------------|
| Scoring fails / empty API key | `LLM_PROVIDER=gemini` and `GEMINI_API_KEY` in `.env` |
| No Telegram messages | You must have messaged the bot first; confirm token + chat id |
| Resume stage error | `config/base_resume.pdf` must exist |
| Apply skipped | Need `resume_path` (Step 4c) + Workday source + saved session |
| Cloudflare / MFA wall | Job goes to `manual_review`; Telegram alert with screenshot — handle manually, re-save session if needed |
| Want discovery only | Set `ENABLE_APPLY=false` in `.env` |
