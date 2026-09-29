# Phase 0 baseline

Recorded 29 September 2026. This is the measurement baseline for later phases. It describes the system as it behaves now. It does not retune discovery, scoring, embeddings, ranking, or the shortlist.

Profile facts are hashed from the parsed `config/profile.yaml` model, not from the raw file, so comments do not change the hash. The hash is not the embedding-text hash in `scorer/embeddings.py`.

Current profile hash: `84b2d1be120b0719cd906b21f77ffa239b59bd4e5803be8245e7449828f8958a`

A run logs `pipeline_baseline` and, outside pytest, writes `storage/diagnostics/effective_config.json`. `uv run python main.py doctor` prints the same public block. Neither output contains keys, tokens, or the profile text.

## Candidate baseline

- Vikash Dadhich, based in Seattle.
- MBA, Foster School of Business, University of Washington, graduation June 2028.
- B.Tech, Metallurgical and Materials Engineering, NITK Surathkal, May 2021, CGPA 7.68.
- Professional span on 29 September 2026: **5.2 years**. The calculator uses the earliest start through the latest end. Overlapping Standard Chartered and Saarthi dates are not added together (that sum is 6.6 years). The MBA is education, not an experience row.
- Standard Chartered GBS, continuous: Software Developer Jul 2021–Apr 2024, Senior Software Developer Apr 2024–Sep 2025, Manager – Development Sep 2025–Aug 2026.
- Saarthi Manosetu Wellness, Co-founder and Technical Product Lead, Apr 2025–present. Counted as real experience.
- Work authorization text: F-1, CPT can cover internships, full-time roles need sponsorship.
- `sponsorship_required: true` and `needs_visa_sponsorship: true`, so explicit hostile sponsorship language is filtered.
- `authorized_to_work_us: false` means unrestricted work authorization. Form-fill answers "No" to that question. It does not by itself reject an internship that never mentions sponsorship.
- Geography: `relocation_ok: true` and `remote_ok: true`. Preferred locations are Seattle and Remote. That list is a pre-rank bonus (+8 Seattle, +5 remote), not a hard geographic filter.
- Dream companies: empty.
- Target titles stay the existing internship list. Role-family weights are not implemented.

Left unchanged on purpose, because the Phase 0 brief did not establish them as facts already in the file or they would change scoring:

- Dean's Merit Fellow, GMAT Focus 685, and the "testing into software development" sentence stay in the summary.
- Skill tags were not extended. Java 17 / Java 21, Jakarta REST, stakeholder management, and business transformation are not separate skill tags. Jakarta REST appears in a Standard Chartered bullet.
- Street address remains unconfirmed.

## Discovery baseline

Unchanged.

- JobSpy sites: LinkedIn, Indeed, Google, ZipRecruiter.
- Search terms: Product Manager Intern, MBA Product Manager Intern, Program Manager Intern, Project Manager Intern, Product Marketing Intern, Strategy Intern, Go-to-Market Intern, Product Operations Intern, Customer Success Intern, Management Consultant Intern.
- Workday boards: NVIDIA, Salesforce Futureforce Internships, Workday Early Career, Zillow, Boeing, Adobe.
- Production `INTERNSHIP_ONLY=true`.

## Scoring baseline

Unchanged.

| Knob | Value |
|---|---|
| Embedding model | `text-embedding-3-small` |
| Dimensions | 768 |
| Threshold | 0.50 |
| Profile and JD embed cap | 6,000 characters |
| Embedding failure | fail open |
| Scorer and writer | `gpt-5-mini` |
| JD cap | 9,000 characters, head and tail |
| Tier 1 | score >= 85, or a dream company |
| Tier 2 | 65–84 |
| Tier 3 | below 65 |
| Score budget | unset (unlimited) |
| Vector gate | on |
| Years-of-experience slack | +3 |
| Ceiling on 29 September 2026 | 8 (round(5.2) + 3) |

## Production baseline

GitHub Actions (`.github/workflows/pipeline.yml`) is the production process. It runs `main.py run-once`. It does not load `.env`. An external cron dispatches it at 09:00 and 19:00 America/Los_Angeles. The workflow file has no GitHub `schedule`.

| Setting | Production |
|---|---|
| `INTERNSHIP_ONLY` | true |
| `ENABLE_APPLY` | false |
| `ENABLE_BENCHMARK` | false |
| `ENABLE_LINKEDIN_SCRAPE` | false |
| `ENABLE_REVIEWS` | true |
| `ENABLE_PREP_PACK` | true |
| `PREP_PACK_BRIEF` | true |
| `PREP_PACK_LIMIT` | 20 |
| `ENABLE_SUGGESTIONS` | false |
| `LLM_PROVIDER` | openai |
| `OPENAI_SCORER_MODEL` | gpt-5-mini |
| `OPENAI_WRITER_MODEL` | gpt-5-mini |
| `TIER_ONE_DRAFTS_ENABLED` | false |
| `SCORE_BUDGET` | unset |
| `VECTOR_GATE` | on (code default; the workflow does not set it) |
| `TIMEZONE` | America/Los_Angeles |
| In-process `SCHEDULE_TIMES` | 08:00, 13:00, 18:00 (not what fires Actions) |

## Local versus production

Code defaults still differ from production. That is intentional. Tests lock the code default.

| Setting | Code default | Local `.env` after Phase 0 | Production |
|---|---|---|---|
| `INTERNSHIP_ONLY` | false | true | true |
| `ENABLE_APPLY` | true | false | false |
| `ENABLE_SUGGESTIONS` | true | false | false |
| `PREP_PACK_BRIEF` | false | true | true |

`.env.example` still shows `ENABLE_APPLY=true` and `ENABLE_SUGGESTIONS=true`. It is a template, not the live environment.

The local internship flag was unset, so a local `run-once` used the code default and would have saved full-time titles. The local database URL is the Neon database, so that run would have written those titles into the same store production uses. Phase 0 set `INTERNSHIP_ONLY=true` in `.env` only. The code default stays false. A pipeline log warning fires when the flag is off.

Scoring knobs (models, tiers, embedding threshold, JD cap, slack, score budget, vector gate) match between local and production.

## Sponsorship behavior locked by tests

Hostile and dropped: "No visa sponsorship available", "Applicants must be U.S. citizens", and the phrases already listed in the working note.

Kept, because the current classifier returns `unknown`:

- "Must be authorized to work in the U.S. without sponsorship"
- "Must have permanent work authorization"
- "Sponsorship may be available"
- "Open to candidates requiring sponsorship"
- a posting with no sponsorship language

Friendly and kept: "Visa sponsorship available".

The visa classifier was not expanded. Those `unknown` phrases are a later visa-engine item.

## Tests

Phase 0 added `tests/test_phase0_baseline.py` and `tests/test_diagnostics.py`.

`tests/conftest.py` forces `INTERNSHIP_ONLY=false` for the suite so a developer `.env` cannot change filter tests.

Full suite on 29 September 2026: 345 passed, 1 skipped. The skip is pre-existing: `test_dream_company_match_tolerates_suffix` skips because `dream_companies` is empty. No Phase 0 failure.
