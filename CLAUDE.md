# CLAUDE.md

Shared context for every Claude session on this repo (terminal, desktop app, or cloud).
Product description and commands are imported from AGENTS.md below. Parts of AGENTS.md, README.md and SETUP.md are stale (they mention Gemini and a 3x/day APScheduler). When docs and code disagree, the code wins.

@AGENTS.md

## What this is

An agent that finds Summer 2027 MBA internships in the US (product management and consulting first), scores fit, and sends a shortlist on Telegram. It is decision support. It never applies to jobs or contacts employers on its own.

## Working rules (follow these every session)

1. Run `git pull` before starting any work, then confirm `git status` is clean or understood.
2. Never commit or push straight to `main`. Work on a branch (`claude/<short-topic>`) and open a pull request.
3. Claude may merge its own pull request once CI is green (standing permission from the owner, 25 Oct 2026). The owner then runs `git pull` locally. GitHub `main` is the single source of truth. Never merge with red CI, and never merge a PR that touches `pipeline.yml` schedules or spend caps without telling the owner first.
4. One topic per branch and PR. Do not mix in unrelated files.
5. Tell the owner which branch and commit you are on at the start and end of a session.
6. Cloud sessions usually cannot install packages, so they cannot run tests. Let CI (`ci.yml`: pytest, Ruff, Pyright) run on the PR and report its result. Local sessions should run `uv run pytest -q`, `uv run ruff check .` and `uv run pyright` before pushing.

## Hard rules for the code

- Never add or enable automatic application submission or outreach. Application steps stay behind an explicit human action.
- Do not weaken fit validation. The accepted judgments, confidence values, dimension keys and grounding checks stay at least as strict as they are. Do not coerce invalid model output into accepted values.
- Any change to the fit prompt, schema or validation needs a `FIT_VERSION` bump and matching tests.
- Unknown visa or sponsorship status is not a rejection. Salary never affects the fit score.
- Do not raise token budgets or workload limits without evidence and a cost estimate. Production has no spend caps set; do not dispatch `pipeline.yml` or run the live pipeline, OpenAI calls, Telegram sends or job-site scraping without the owner asking for it.
- Keep exactly one scheduler. Do not add a GitHub `schedule` while an external cron also dispatches the workflow.
- Do not commit secrets, `.env`, personal data, resumes, generated output, or files under `graphify-out/`.
- `test_production_workflow_file_is_unchanged` compares `pipeline.yml` with `HEAD`, so tests fail until a workflow edit is committed.

## Known state (as of 26 Oct 2026, Phase 7)

- `FIT_VERSION` is `phase2-v1`. Stored jobs keep their old version string and are not re-scored; only newly scored jobs get the new one.
- Production sets spend caps in `pipeline.yml` (search capacity 40, score budget 60, 150 OpenAI requests, 60 role calls, posting and embedding caps). Raise them only with cost evidence.
- Hard-filtered rows are saved but not enriched (no company lookup, eligibility, JD reading or role call).
- Review cards with "Approve = submit" are only sent when `ENABLE_APPLY` is true.
- Plan for the next phases lives in the owner's private project (apply-agent-plan).
- Fit answers use a strict JSON schema (enums for judgment and confidence, all 8 dimensions required) and the same validation as before. The rubric defines the five labels for `REQUIREMENTS_RISK`. Grounding accepts inflections (shared first six letters); invented facts are still dropped.
- An unusable fit answer is retried at most `FIT_MAX_ATTEMPTS` (3) times, tracked in `jobs.fit_attempts`, then the job becomes `error` with `last_error` set. `score_max_tokens` is unchanged at 1024; raise it only with evidence of truncation.
- Company job boards (Greenhouse, Lever, Ashby) are read by `scraper/ats_boards.py` from the `ats_boards` list in `config/targets.yaml`. They are off unless `ENABLE_ATS_BOARDS=true`; `pipeline.yml` sets it. The board checker workflow (Check company boards) reports which names work; dead names were removed on 26 Oct 2026 and the rest are `verified: true`. A wrong token is reported as not found and skipped. Only internship titles that look like business roles (product, strategy, consulting, operations, marketing, analyst) are kept. `ATS_MAX_AGE_HOURS` limits age (unset keeps every open posting). `Source` gained `greenhouse`, `lever`, `ashby`; `init_db` adds them to the Postgres enum.
- Apply queue (Phase 4): with `ENABLE_APPLY=false` and Telegram set, each run first reads button taps (`telegram_sync`, one-shot `getUpdates`), expires old cards, then the shortlist fills open seats, capped at `QUEUE_DAILY_LIMIT` (15) new jobs per rolling 24h. Cards carry Applied / Skip / Later (`q1|` callbacks, `bot/queue.py`). Applied only records that the owner applied by hand. Later hides a job for `QUEUE_SNOOZE_DAYS` (3); unanswered cards expire after `QUEUE_EXPIRY_DAYS` (7). New `jobs.queued_at` and `jobs.snoozed_until` columns.
- Relevant queue (27 Oct 2026): `TARGET_TITLES_ONLY` drops titles that are not product, consulting, strategy, marketing or business roles (`scraper/title_family.py`), plus unpaid and non-summer roles, before scoring. `QUEUE_MIX` fills the queue by `config/queue_mix.yaml` (40% product, 40% consulting, 20% other, by title); empty seats spill to product first, never to off-target roles. Any job scoring `QUEUE_HIGH_FIT_SCORE` (80) or more is always queued, past the daily limit and the shortlist size; company cap and duplicate titles still apply. Cards show only title, company, place, freshness, deadline, an Open job button and Applied / Skip / Later; one header message per day is the only one that notifies. Drafted answers only with `KIT_ANSWERS=true`. `reset-queue` and `resend-queue` are manual workflows. `pipeline.yml` takes an `ingest_mode` input (daily or catchup). Workday sites search only "intern" and "MBA".
- Application kit (Phase 5): each queue card shows the resume version (`config/resume_versions.yaml`, by role family), a deadline when the posting states one, and two drafted answers from the grounded resolver (queued jobs only).
- Operations (Phase 6): a run after more than 26 hours without a good run sends a Telegram notice; the first run on Monday sends a weekly summary. `pipeline.yml` sets `ENABLE_ATS_BOARDS`, `SIMPLIFY_DISCOVERY` and `QUEUE_DAILY_LIMIT`. The only scheduler is the external cron-job.org dispatch.
- Repo hygiene (Phase 7): resume PDFs, `graphify-out/`, baselines and benchmarks are untracked and ignored. `config/profile.yaml` still holds personal contact details and is required by the code, so the repo should be private. Git history before 26 Oct 2026 still contains the removed files.
- The scheduled run is not active right now. Do not turn it back on without a readiness review.

Detailed onboarding notes live in the owner's private project, not in this public repo. Ask the owner if you need them.
