# CLAUDE.md

Shared context for every Claude session on this repo (terminal, desktop app, or cloud).
Product description and commands are imported from AGENTS.md below. Parts of AGENTS.md, README.md and SETUP.md are stale (they mention Gemini and a 3x/day APScheduler). When docs and code disagree, the code wins.

@AGENTS.md

## What this is

An agent that finds Summer 2027 MBA internships in the US (product management and consulting first), scores fit, and sends a shortlist on Telegram. It is decision support. It never applies to jobs or contacts employers on its own.

## Working rules (follow these every session)

1. Run `git pull` before starting any work, then confirm `git status` is clean or understood.
2. Never commit or push straight to `main`. Work on a branch (`claude/<short-topic>`) and open a pull request.
3. The owner merges on GitHub, then pulls locally. GitHub `main` is the single source of truth.
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

## Known state (as of 25 Oct 2026, commit dc49f28)

- CI is red only because `tests/test_fit.py::test_phase6_v1_fit_is_stale` still expects `FIT_VERSION == "phase6-v2"` while the code says `phase6-v3`.
- Production has no OpenAI, scoring, search or ingestion caps. The trial workflow sets them all.
- Two known fit-validation problems: an invalid judgment on `REQUIREMENTS_RISK`, and a grounding check that drops ordinary English words.
- The scheduled run is not active right now. Do not turn it back on without a readiness review.

Detailed onboarding notes live in the owner's private project, not in this public repo. Ask the owner if you need them.
