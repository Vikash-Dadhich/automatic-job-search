# How jobs are found, filtered, scored, and sent

This document describes the pipeline as the code works today, then the weight-and-priority design we discussed and have not built yet, then the pain points behind that design.

It is a working note for you. It is not a proposal that has been implemented. Where the discussion and the code disagree, both are written down.

Last reviewed against the repo on 29 September 2026.

Phase 0 checked this note against the code and left discovery, scoring, embeddings, ranking, and the shortlist alone. The candidate facts, the production flags in the table below, and the filter behavior in section 3 match the code. Two additions from that pass: a secret-free run identity (`config/diagnostics.py`, also printed by `main.py doctor`), and `INTERNSHIP_ONLY=true` in the local `.env` so a local run does not use the code default of `false`. The code default itself is still false. Details, including phrases the sponsorship classifier does not yet catch, are in `docs/phase0-baseline.md`.

---

## 1. What a run is

A run is one pass of `uv run python main.py run-once`. GitHub Actions runs that command when something outside GitHub (the external cron, 9:00 and 19:00 America/Los_Angeles) dispatches the workflow. The workflow itself has no GitHub `schedule`. Overlapping runs cancel each other (`concurrency.group: pipeline`, `cancel-in-progress: true`). The job timeout is 45 minutes.

The live environment is:

| Setting | Value in GitHub Actions |
|---|---|
| `INTERNSHIP_ONLY` | `true` |
| `ENABLE_APPLY` | `false` (no Workday auto-fill) |
| `ENABLE_BENCHMARK` | `false` |
| `ENABLE_LINKEDIN_SCRAPE` | `false` (this flag is the peer-profile scraper, not job discovery) |
| `ENABLE_REVIEWS` | `true` |
| `ENABLE_PREP_PACK` | `true` |
| `PREP_PACK_BRIEF` | `true` (one shortlist text file, not essays or a PDF) |
| `PREP_PACK_LIMIT` | `20` (used only if brief mode is turned off) |
| `ENABLE_SUGGESTIONS` | `false` |
| `LLM_PROVIDER` | `openai` |
| `OPENAI_SCORER_MODEL` | `gpt-5-mini` |
| `OPENAI_WRITER_MODEL` | `gpt-5-mini` |
| `TIER_ONE_DRAFTS_ENABLED` | `false` (no outreach note, no cover letter) |
| `SCORE_BUDGET` | not set, so the default is unlimited |
| `VECTOR_GATE` | on by default (`vector_gate_enabled = true`) |

Stages, in order. One stage failing does not stop the later stages.

1. Ingestion: fetch, clean, hard-filter, save.
2. Scoring: embedding gate, then the fit model.
3. Resume: copy and sanitize the base PDF for staged jobs.
4. Suggestions: skipped.
5. LinkedIn peer benchmark: skipped.
6. Prep: the Telegram shortlist file.
7. Apply: skipped.
8. Reviews, outcome prompts, and alerts: still run, but they only matter for Workday applications sitting in `pending_review` or `manual_review`. With apply off, the thing you receive from a normal run is the shortlist file.

---

## 2. Where jobs come from

Discovery is not a logged-in LinkedIn session. `ENABLE_LINKEDIN_SCRAPE` is a different feature (peer profile benchmarking) and it is off.

Job posts come from the `python-jobspy` library, one search term at a time, across every site listed in `config/targets.yaml`. Workday company boards are a second fetcher, described in section 2.4.

### 2.1 Search terms

Phase 1 moved the phrase list into `config/discovery.yaml`. Families, buckets, and a 40/40/15/5 search-capacity split live there. Those weights are discovery priority, not fit scores. The ten phrases below are still searched. One starter phrase was added for each bucket that did not already have one. See `docs/phase1-discovery-architecture.md`.

Every selected query is still searched once, the same way, on the sites in `config/targets.yaml`.

Product management:

- Product Manager Intern
- MBA Product Manager Intern

Program and project management:

- Program Manager Intern
- Project Manager Intern

Product marketing:

- Product Marketing Intern

Strategy and GTM:

- Strategy Intern
- Go-to-Market Intern

Product operations:

- Product Operations Intern

Customer success:

- Customer Success Intern

Consulting:

- Management Consultant Intern

That was the original 10 terms. They are still in the discovery config, under role-family buckets.

### 2.2 Sites and the exact JobSpy arguments

Sites, in list order:

- linkedin
- indeed
- google
- zip_recruiter

For each term, the code calls `scrape_jobs` once with all four sites together:

| Argument | Value | What it does |
|---|---|---|
| `site_name` | the four sites above | One call covers every site |
| `search_term` | the term, unchanged | Keyword query |
| `location` | `United States` | Geo bias |
| `distance` | `50` miles | Radius around that location. A country-level location makes this radius weak |
| `results_wanted` | `50` | Up to 50 jobs **per site** for that term. Four sites means up to 200 raw rows per term before dedupe |
| `hours_old` | `36` | Recency window. Not honored the same way on every site (see below) |
| `country_indeed` | `USA` | Indeed country |
| `description_format` | `markdown` | Description text shape |
| `linkedin_fetch_description` | `true` | Extra request per LinkedIn job to get the full description and, when present, the direct company URL |
| `verbose` | `0` | Quiet |
| `google_search_term` | `"{term} internship"` | Sent only because Google is in the site list |

Theoretical ceiling before dedupe and filters: 10 terms × 4 sites × 50 = 2,000 rows. Real runs are smaller. LinkedIn stops returning results well before that, many rows are duplicates across terms and sites, and the location filter drops some before they are saved.

### 2.3 How each site treats "posted in the last 36 hours"

The code logs this at the start of every scrape, because the library does not apply `hours_old` uniformly.

| Site | Effective window |
|---|---|
| LinkedIn | 36 hours, as configured |
| Indeed | 36 hours, as configured |
| Google | `hours_old` is ignored. The Google query is `"{term} internship"` and does not say "since yesterday", so Google is not limited to 36 hours |
| ZipRecruiter | `hours_old` is rounded up to the next full day, so 36 hours behaves like about 48 hours |

LinkedIn is the strict board. JobSpy's own docs say LinkedIn typically returns HTTP 429 after about the 10th page from one IP, around 100 results, and `linkedin_fetch_description=true` spends an extra request per job. A failure on one term is logged and the next term still runs. A `TypeError` that says the installed JobSpy does not accept `google_search_term` is retried once without that argument, so LinkedIn, Indeed, and ZipRecruiter for that term are not thrown away with Google.

There is no delay between terms and no proxy list.

### 2.4 What is kept from a JobSpy row

A row is dropped immediately, before the hard filter, when:

- the site name is not one of linkedin, indeed, google, zip_recruiter
- title, company, or URL is empty
- the location fails the same location rule as the later hard filter (section 3.8)

Kept fields: source, an id (the board's id, or a hash of the URL), title, company, location, URL (direct company URL when JobSpy has one, otherwise the board URL), description, posted date.

Duplicates inside one term and across terms are removed on `(source, external id)`.

### 2.5 Workday, separately from LinkedIn

These company boards are also fetched, using the same 10 search terms because each tenant's `search_terms` list is empty:

- NVIDIA
- Salesforce Futureforce Internships
- Workday Early Career
- Zillow
- Boeing
- Adobe

Starbucks, Nike, Amazon, and Microsoft are not in this list. They do not publish a Workday board, so they only appear if LinkedIn, Indeed, Google, or ZipRecruiter returns them.

Workday auto-fill is off (`ENABLE_APPLY=false`). A Workday posting can still be discovered, scored, and put on the shortlist. You apply by hand.

### 2.6 Save and dedupe

Each posting is cleaned (HTML to text), hard-filtered (section 3), and upserted into Neon Postgres.

Identity is `(source, external id)`.

- A repeat of the same posting refreshes the text and does not create a second row.
- If the description hash changes, a job that was only `discovered`, `filtered_out`, `scored`, or `staged` is rewound to `discovered` so it is scored again.
- Jobs you have already touched (`pending_review`, `submitted`, `manual_review`, `ignored`) are not rewound.

---

## 3. Hard filters (before any model)

`scraper/filters.py` `evaluate()` runs at ingest and again as a backlog guard at scoring time. A failure is saved as `filtered_out` with a reason. It never reaches the fit model.

Order of checks:

### 3.1 Company blocklist

Whole-name match, so "Meta" does not block "MetLife". Current list:

- Revature
- Dice

### 3.2 Exclusion keywords

Phrase match against title, company, location, and description:

- security clearance required
- must have active TS/SCI
- staffing agency

### 3.3 Clearance language

On, because `clearance_required: true`. Patterns include "security clearance", active TS/SCI or secret, "must have/hold/possess … clearance", "requires … clearance", and citizenship-plus-clearance wording.

### 3.4 Staffing agencies

On, because `third_party_staffing: true`. Patterns include "staffing agency", "recruiting firm", "third-party staffing/recruiter", the word "revature", the word "dice", and "contract-to-hire agency".

### 3.5 Internship gate

On in production because `INTERNSHIP_ONLY=true`. The default in code is off, so a local run without that env var does not apply this gate.

The title must have one positive signal.

Positive signals:

- The word `intern` or `internship` as a whole word. "International" and "internal" do not count.
- `summer {year}` for the current calendar year through three years ahead. In 2026 that is summer 2026, 2027, 2028, and 2029.
- `new grad` or `new graduate`.

If the title has the whole word intern or internship, seniority words do not remove it. That keeps bank titles such as "Summer Assistant Vice President Internship".

If the title only has a soft signal (`summer 2027`, `new grad`) and also contains a seniority word, it is dropped. Seniority words in this gate: senior, sr., lead, staff, principal, director, head of, vp, vice president.

A title with none of the positive signals is dropped. Plain "Product Manager" is dropped. "Product Manager Intern" is kept. "Associate Product Manager, New Grad" is kept. "Senior Product Manager, New Grad" is dropped.

### 3.6 Seniority filter (separate from the internship gate)

On by default. This one looks only at the title, using phrase match, for: director, vp, avp, svp, evp, principal, chief, head of.

"Senior" is not in this list. A "Senior Product Manager Intern" can pass this check. The internship gate is what blocks "senior" when the title does not literally say intern.

### 3.7 Years of experience

The filter reads every "N years of experience" number in the posting. It rejects the job only when the **lowest** stated number is above your experience plus slack.

Slack is 3 years (`years_experience_slack`). There is no manual cap (`max_required_years_experience` is unset), so the ceiling is your career length from `profile.yaml` dates, rounded, plus 3. "3+ required, 10+ preferred" survives, because the lowest number is 3. A posting whose minimum is above the ceiling is dropped.

### 3.8 Visa and sponsorship

This runs because your profile has `sponsorship_required: true` and `needs_visa_sponsorship: true`.

A posting is dropped when the text is **hostile**. Hostile phrases include:

- no visa sponsorship
- do/does not offer or provide sponsorship
- cannot / can not offer, provide, or sponsor
- must be a US citizen
- US citizens only
- citizenship required
- requires US citizenship
- unable to sponsor
- will not sponsor

A posting that says it will sponsor, or that welcomes OPT, CPT, or F-1 students, is classified `friendly` and kept.

A posting that says nothing is classified `unknown` and kept.

Phase 0 locked the current classifier and did not extend it. These plain-English lines are still `unknown`, so they are kept: "must be authorized to work in the U.S. without sponsorship", "must have permanent work authorization", "sponsorship may be available", and "open to candidates requiring sponsorship". "No visa sponsorship available" and "applicants must be U.S. citizens" are hostile and dropped.

The classifier checks hostile phrases before friendly ones, so "we do not offer visa sponsorship, OPT students may apply" stays hostile.

"We sponsor employee events" is not treated as visa sponsorship. The friendly "we sponsor …" pattern requires visa, H-1, or work authorization as the object.

The shortlist file you receive does **not** print this friendly/unknown flag. Hostile jobs are simply absent.

### 3.9 Location

Preferences: Seattle, WA, and Remote. `remote_ok: true`. `relocation_ok: true`.

- Blank location: kept. The fit model is expected to judge it from the description.
- Remote, and remote is allowed: kept. "Remote" is a whole word, so "Remoteville" is not remote.
- A city that matches a preferred city, and the state matches when both sides have a state: kept. Portland, OR does not satisfy Portland, ME.
- Anything else: still kept, because `relocation_ok` is true.

With relocation on, location almost never removes a US internship. It matters more as a small boost in the pre-score ordering (section 4).

### 3.10 What a survivor looks like

Passed jobs are saved as `discovered`. Failed jobs are saved as `filtered_out`. Only `discovered` jobs are eligible for the embedding gate and the fit model.

---

## 4. How results are prioritised today

There is no role-family weight. Product management and customer success are searched with the same 50-result cap and the same term order. Term order is the list in section 2.1, product management first, customer success and consulting later. If LinkedIn starts returning 429s mid-run, later terms are the ones that lose results. That is an accident of list order, not a designed priority.

After the hard filter, two rankings exist. They do different jobs.

### 4.1 Pre-score rank (`prerank_score`)

This number is not the fit score and it is not shown to you. It only orders the queue before embeddings and the fit model, so that if a cap is on, the front of the queue is scored and the tail waits.

`SCORE_BUDGET` is unset in production, so this rank does not drop jobs today. It still controls the order in which the embedding gate walks the list.

Points, added together:

| Signal | Points |
|---|---|
| Whole word intern or internship in the title | +40 |
| Else summer 20xx, or new grad / new graduate | +22 |
| Title contains any target-family keyword (product manager, product management, associate product, program manager, project manager, project management, product marketing, strategy, consultant, consulting, product operations, customer success, go-to-market, gtm) | +14, once |
| Title overlaps any preferred title in `profile.yaml`, either direction | +16, once |
| Company matches a dream company | +30 |
| Location matches a non-remote preference (Seattle, WA) | +8 |
| Remote location and remote is allowed | +5 |
| Source: Workday 6, LinkedIn 4, Indeed 3, ZipRecruiter 2, Google 1, anything else 1 | that value |
| Posted or discovered within 12 hours | +10 |
| Within 24 hours | +6 |
| Within 48 hours | +3 |

Dream companies in the profile are an empty list, so the +30 never fires.

The family keywords are flat. "Product Manager Intern" and "Customer Success Intern" both receive the +14. The first matching preferred title also gives both the +16 if the title string overlaps. There is no "product management is worth more than customer success."

Unknown source strings do not crash the run. They score as 1.

### 4.2 Embedding gate (this does drop jobs)

On by default. Model: `text-embedding-3-small`. Vector width: 768. Threshold: cosine similarity **0.50**.

What is embedded:

- Your side: the start of the same candidate block the fit model sees, cut at 6,000 characters.
- The job side: title, company, then the description, also cut at 6,000 characters.

The gate walks jobs in pre-score rank order.

A job skips the gate and goes straight to the fit model when:

- it already failed a hard filter or is in a company cooldown
- the text is shorter than 40 characters
- the embedding call fails (billing error, network, missing key). Failure means "let the fit model see it," not "drop it"

A dream company always passes, even below 0.50. None are configured.

Otherwise cosine similarity versus your profile vector must be at least 0.50. Below that, the job is saved as a vector reject and is not sent to `gpt-5-mini`. Rejects do not consume `SCORE_BUDGET` when a budget is set.

The profile vector is cached on disk under `storage/embeddings/` keyed by a hash of the profile text. A profile edit changes the hash and forces a new embedding.

Company cooldown: 30 days after a submission, that company is treated as blocked for this gate. With apply turned off, submissions are rare, so this rarely fires.

### 4.3 Fit-model cap

`score_budget` default is `None`. Every job that passes the hard filter and the embedding gate is scored. The pre-score rank orders the work. It does not cut it.

If you later set `SCORE_BUDGET` to a number, only that many jobs from the front of the pre-score rank are sent to the fit model. The rest stay `discovered` for a later run. With the vector gate on, embedding rejects do not use up those slots.

Concurrency is 8 fit-model calls at a time. Transient errors (429, 503, 500, timeouts) retry up to 4 times. A billing or invalid-key error stops immediately.

---

## 5. How fit is scored

### 5.1 What the model is

`gpt-5-mini` through the OpenAI API. This is not the ChatGPT app. Custom GPTs, ChatGPT memory, and custom instructions in the chat product are not visible to this call.

The model is told to use only the candidate block in the request. It is told not to invent degrees, dates, titles, skills, or work authorization.

### 5.2 The two inputs

**Input A, system block.** Built once per run and reused for every job. It is your profile summary plus the rubric.

The profile summary (`static_context_block`) contains, in this order:

- Name: Vikash Dadhich
- Location: Seattle, WA
- Email, phone, LinkedIn URL, GitHub URL
- The `summary` paragraph from `profile.yaml` (Foster MBA, Dean's Merit Fellow, graduation June 2028, Standard Chartered path, GMAT Focus 685, product and technology-strategy goal, NITK B.Tech, CGPA 7.68/10)
- Work auth: F-1, CPT can cover internships, full-time roles need sponsorship; `sponsorship_required=true`; `authorized_to_work_us=false`; `needs_visa_sponsorship=true`
- Education: each degree, field, school, graduation date, and GPA when present
- Experience: every role as title, company, dates, and the achievement bullets joined with ` | `
- Skills: the list in `profile.yaml` (product strategy, user research, GTM, RICE, BRD/PRD, wireframing, and the engineering stack through Lit Web Components)
- Target titles: every title in `preferences.titles`, comma-separated, with no weights
- Target locations: Seattle, WA and Remote; `remote_ok=true`; `relocation_ok=true`

Street address, portfolio URL, and dream companies are not in this block. Dream companies are empty anyway.

The achievement bullets **are** in this block today. An earlier version of the scorer sent only title, company, and dates. That older shape is what we talked about when consulting roles looked under-scored. The bullets and the summary paragraph were added after that conversation. The rubric was not changed to match.

**Input B, user message.** One job, minified:

```text
Evaluate this job posting:

Title: …
Company: …
Location: …

{description, middle-truncated at 9000 characters}
```

`max_jd_chars` is 9000. Truncation keeps the head and the tail of the description, because sponsorship and years-of-experience lines often sit at the bottom.

No resume PDF is attached. No web search. No prior chat.

### 5.3 The rubric, verbatim in meaning

The model is a strict job-fit evaluator. Score 0–100 on exactly these:

1. Title match
2. Must-have skills overlap
3. Years-of-experience fit
4. Location or remote fit
5. Work-auth / sponsorship gate. Hard penalty if the role requires sponsorship the candidate needs, or a clearance the candidate lacks.

The wording of item 5 is easy to misread. Your profile says you need sponsorship. A hostile posting should already have been removed by the hard filter. The rubric still tells the model to penalise a sponsorship mismatch.

Tier hint the model may suggest, which the code then recomputes:

- 1 if score is at least 85, or the company is a dream company
- 2 if score is 65–84
- 3 if score is under 65

Required output, and nothing else:

```json
{"s":0,"t":1,"r":["short reason","short reason"]}
```

`s` is 0–100. `t` is 1, 2, or 3. `r` is 1–3 short reasons. Banned words in generated prose (used for outreach, not for this JSON) include delve, tapestry, beacon, testament, "thrilled to apply", "leverage synergies", "cutting-edge", "passionate about", "excited to bring", seamless, "robust solution", "game-changer".

`max_output_tokens` for the score call is 1024.

### 5.4 What the code does with the score

`s` must be numeric. A non-numeric score is an error, not a silent 0.

Tier is recomputed in code. The model's `t` is only a hint.

| Result | Rule | Status |
|---|---|---|
| Tier 1 | score >= 85, or company is a dream company | `staged` |
| Tier 2 | score >= 65 and < 85 | `staged` |
| Tier 3 | score < 65 | `filtered_out` |

Dream-company matching ignores legal suffixes, so "Google" would match "Google LLC". The list is empty, so only the score thresholds apply.

Tier 1 outreach and cover letters are off (`TIER_ONE_DRAFTS_ENABLED=false`). A failed draft, if drafts were on, would not demote a good score to an error.

The stored score is the model's `s`. Role family does not add to it.

### 5.5 What a number means

A 78 means the model, using only the block in section 5.2 and the five checks in section 5.3, judged this description a 78. It does not mean the model remembered you from the internet.

Title match is an explicit check. A consulting internship can still score low when your job titles are engineering and product-shaped, even with the bullets present, because the rubric rewards title match and lists every target title as equal.

---

## 6. What is sent to you

Brief mode is on. You get one Telegram document per run, a `.txt` file, caption like `12 leads, 9 above 75`.

### 6.1 Who is eligible

Jobs from this run's scoring pass that have a numeric score and have not already been sent (`prep_pack_sent_at` is empty). The query that backs a manual prep-pack send also allows status `staged` or `filtered_out`. The pipeline path passes the ids that scoring just touched.

Tier 3 jobs have scores under 65. They can sit in the pool. The shortlist rule below still excludes anything under 60, and a Tier 3 score is under 65, so a 64 can be included as fill and a 50 cannot.

### 6.2 The shortlist rule

`select_shortlist` in `bot/prep.py`:

1. Take every unsent job with score **above 75**. Sort by score, highest first.
2. If that set already has 20 or more, send all of them. There is no cap once you are above 75. A day with 30 jobs at 76 or higher sends all 30.
3. If fewer than 20 are above 75, fill from jobs with score **from 60 through 75**, highest first, until the file has 20.
4. Anything **under 60** is left out.
5. Fill rows are marked `[fill]` so a 70 is not read as a 90.

Order inside the file is fit score only. Family is not a section. A 92 customer-success intern is above an 88 product-management intern.

### 6.3 Each line

```text
1. 91  Product Manager Intern @ Stripe
    Seattle, WA
    https://...

2. 70  [fill]  Strategy Intern @ Some Co
    Remote
    https://...
```

Fields: rank, score, optional `[fill]`, title, company, location, URL.

Not included: visa friendly/unknown, tier name, source site, the model's reasons, family, or the pre-score rank.

After a successful send, `prep_pack_sent_at` is set. The next run does not send those rows again unless the job is rewound.

### 6.4 If brief mode is turned off

`PREP_PACK_BRIEF=false` switches to the full prep pack: model-written answers, a Typst PDF, and a Markdown file, capped at `PREP_PACK_LIMIT` (20) staged manual-apply jobs (LinkedIn, Indeed, Google, ZipRecruiter). That path is not what the cron uses.

Workday review cards (approve / manual / discard) are a different Telegram message. They only appear after the apply stage, which is off.

---

## 7. Statuses, in one pass

```text
fetched
  -> filtered_out          hard filter failed (section 3)
  -> discovered            hard filter passed
       -> filtered_out     embedding cosine < 0.50
       -> filtered_out     fit score < 65 (Tier 3)
       -> staged           fit score >= 65 (Tier 2) or >= 85 (Tier 1)
            -> Telegram    score > 75, or score >= 60 while the file has under 20
```

`scored` exists as a status in the database enum. The live tier mapping writes `staged` or `filtered_out` directly.

---

## 8. The weight discussion (not built)

This section is the design we talked through. None of the weights below are in `targets.yaml`, `profile.yaml`, `prerank.py`, or the shortlist. Today every family is equal, as in sections 2 and 4.

### 8.1 What you asked for

A family weight should do three things, in order:

1. **Search.** A heavier family gets more of the run: more queries and a deeper result pull. Product management at 40 is searched harder than customer success at 2.
2. **Scoring queue.** Those jobs are scored first when a cap exists, so a full day does not spend the model on the lightest family while product management waits.
3. **Fit stays a separate judgment.** The model still scores the job against your profile from 0 to 100. The weight does not invent fit. It decides who gets that judgment, and it can lift a job in the list you see.

You also asked that a quiet day for a heavy family must not shrink the run. Unused search slots move to the other families in proportion to the weights they already have.

### 8.2 Decisions you agreed with

**Fit floor.** Weight gets a job into the scoring queue. It appears in the Telegram file only when fit is at least 60, which is already the fill floor. A product-management intern at 55 stays out even if the family weight is 40.

**Search heavy families first.** If LinkedIn starts blocking mid-run, product management, strategy, and consulting have already been fetched. The lighter families are what get cut.

**Match families with phrases, not one keyword.** "Product" also hits Product Owner and Product Analyst. Each family uses the titles you already list (product manager, product management, associate product manager, and so on). The first matching family wins, so "Product Marketing Intern" counts as product marketing and not also as product management.

**Spillover is search volume only.** If product management is allotted 80 slots and the boards only return 12, the other 68 slots are added to the remaining families in proportion to their weights. Strategy at 25 absorbs more of that leftover than customer success at 2. The preference weights used for list rank do not change on a thin day. Customer success does not become your top family because product management had a quiet morning.

**Spillover watches raw postings, not fit scores.** If 80 product-management internships exist and only 10 fit you, the search already did its job. Moving slots because the scores are low would spend the rest of the run on families you care about less.

**One pass.** Search the heaviest family up to its share, count real postings, add the unused slots to the next families, then search those. Cap how far any one family can grow so one empty family does not turn into an unlimited pull that trips LinkedIn's rate limit.

**Keep fit and weight as two numbers.** Show the fit score on its own. Rank the list with fit plus family weight.

Example we used:

- Product-management intern, fit 78, weight 40, list rank 118
- Customer-success intern, fit 95, weight 8, list rank 103

Product management leads. A genuinely strong customer-success role can still appear. Adding the 40 inside the model would hide a poor fit: a 50 would look like a 90. That is why the weight stays outside `s`.

**Do not ask the model to use outside knowledge of you.** The API call does not see ChatGPT memory or a custom GPT. Public training data is empty, stale, or wrong for a specific person, and two runs would not agree. Training the ChatGPT app does not change this scorer. The practical way to change scores is the rubric plus a few examples you write, after the profile block contains the evidence you want judged.

### 8.3 A weight table we used as a sketch

Not chosen as final. It was an illustration so the three steps (search share, queue order, list rank) could share one list.

| Priority | Family | Sketch weight |
|---|---|---|
| 1 | Product management | 40 |
| 2 | Strategy and GTM | 25 |
| 3 | Consulting | 15 |
| 4 | Product marketing | 8 |
| 5 | Program and project management | 6 |
| 6 | Product operations | 4 |
| 7 | Customer success | 2 |
| last | No phrase match | Other, no extra weight |

You had not signed this table. The open choice underneath it was whether a very high fit in a light family may outrank a medium fit in product management. The fit-plus-weight formula allows that (95 + 8 can beat 70 + 40). A stricter rule would fill product management first and only then let other families in. You agreed with the formula and the floor of 60, which is the looser rule.

### 8.4 What we said the rubric should do for career-switch roles

Consulting and strategy internships for an MBA are often for people who have not held that title. The pain was that "title match" treats a missing consulting title as a weak fit.

The direction we landed on, still not implemented:

- Keep the score grounded in `profile.yaml` and the job text.
- Judge the description against evidence the posting asks for: structured problem solving, a measured result, stakeholder work, product or strategy judgment.
- Treat a missing prior consulting title as expected, not as a reject.
- Still penalise a true gap: clearance, a required language, a seniority the internship gate already removes.
- Optional later: two or three examples in the prompt (a strategy internship scored high from the bullets; a senior full-time role scored low). A fine-tune waits until you have personally marked a few hundred jobs.

### 8.5 How that would sit on the current pipeline

| Step today | With weights |
|---|---|
| Every term, 50 results, term list order | Heaviest family first. Result depth is that family's share of a fixed budget. Unused slots spill to the next families by their weights |
| Pre-score rank gives +14 to every family keyword | Family weight replaces that flat +14, so the queue and any future `SCORE_BUDGET` prefer heavy families |
| Fit `s` is the only list order | File still shows `s`. Order is `s + family weight`. Sections can follow family order |
| Shortlist: all above 75, else fill from 60 to 20 | Same floor. Weight does not pull a 55 into the file |

Search share has a ceiling. LinkedIn rate-limits a single IP, and a term often has fewer than 50 new internships in 36 hours. Extra depth helps a heavy family. Repeating the same query does not.

---

## 9. Pain points we have actually hit or spelled out

### 9.1 Discovery

- **Equal search, unequal intent.** You care more about product management, strategy, and consulting than about customer success. The scraper does not.
- **The 50-result cap is a cut, not a ranking.** For a busy term, LinkedIn's own order decides which 50 you see. Jobs ranked 51 and below are never downloaded, so they are never scored. Raising the cap and adding Google and ZipRecruiter was the mitigation. It does not prefer a family.
- **LinkedIn blocks deep pulls.** `linkedin_fetch_description=true` plus 10 terms times 50 results can 429 partway through. Later terms, which include consulting, are the ones most likely to be missing. There is no proxy and no pause between terms.
- **Google is not on the 36-hour window.** Its query has no recency clause. ZipRecruiter rounds 36 hours up to about 48. The three boards are not the same "new today" set.
- **`distance: 50` around "United States"** does not mean 50 miles from Seattle. Location filtering then keeps almost everything because relocation is allowed.
- **Full-time backlog.** Jobs discovered before `INTERNSHIP_ONLY` stayed staged until a one-time cleanup. The filter does not rewrite old rows by itself.
- **Substring false friend.** "International" used to pass the intern check. The word-boundary regex fixed that. The test `test_internship_only_rejects_international_substring` locks it.

### 9.2 Filters

- **"Senior" is inconsistent.** The internship gate blocks "senior" only on soft signals. The general seniority list does not include "senior" at all. "Senior Product Manager Intern" can pass both.
- **Sponsorship unknown is invisible.** Hostile text is dropped. Friendly and unstated are kept, and the file you get does not say which. You still have to open the posting to see if they sponsor.
- **YOE uses the lowest number.** That correctly keeps "3+ required / 10+ preferred". A posting that hides the minimum and only lists a high preferred number can still pass.
- **Relocation on means the location gate rarely drops anything.** Seattle preference only shows up as +8 in the pre-score rank.

### 9.3 Scoring

- **Title match punishes the career switch.** The rubric's first check is title match. Your history is engineering and product leadership. Consulting and some strategy internships look like a miss even when the bullets support them.
- **All target titles are equal in the prompt.** The model is shown one flat list. It is not told that product management outranks customer success.
- **The fit score and the pre-score rank are easy to confuse.** Only `s` is shown. The pre-score rank, the embedding cosine, and the reasons in `r` are stored or logged and are not in the Telegram file.
- **Embedding gate can drop a job the rubric would have liked.** Cosine under 0.50 never reaches `gpt-5-mini`. The threshold is 0.50 on a 6,000-character slice. A short or oddly worded internship can lose here.
- **Outside knowledge would make this worse, not better.** Asking the model to add "everything you know about me" pulls in guesses. ChatGPT training does not attach to this API call.
- **Bullets used to be missing.** They are in the candidate block now, with the summary paragraph. The rubric still leads with title match, so the consulting pain is not fully gone.
- **Cost.** Scoring every survivor with no `SCORE_BUDGET` is why a wide funnel (4 sites, 50 results, 10 terms) can get expensive. The pre-score rank is ready for a cap. The cap is not turned on in Actions.

### 9.4 What you receive

- **No family sections.** The file is one list by fit score. A strong low-priority role outranks a slightly weaker role you actually want.
- **Above 75 is uncapped, under 60 is gone, 60–75 only fills up to 20.** A day of thirty 76s sends all thirty. A day of fifteen 90s and fifteen 70s sends the fifteen 90s plus five 70s. The 70s are not grouped by family.
- **No visa line, no reasons, no source.** You get score, title, company, location, URL.
- **Already-sent jobs stay sent.** A posting only comes back if its description hash changes enough to rewind it.

### 9.5 Operations

- **GitHub's own scheduler was unreliable**, so the clock is an external cron that dispatches the workflow. The workflow file no longer has a `cron` block, on purpose, so the two clocks do not double-fire.
- **Cron-job.org needed a classic GitHub token** with `repo` and `workflow` scopes. A fine-grained token returned 403.
- **Neon idle connections** during long runs were fixed with pool pre-ping and a 240-second recycle. A very long run can still drop a connection. That is why the timeout and the model choice matter.
- **Apply, suggestions, and peer benchmark are off** so a run does not spend model calls or a browser on steps you are not using.

---

## 10. File map

| Piece | File |
|---|---|
| Search terms, sites, 50 results, 36 hours, Workday boards | `config/targets.yaml` |
| Role families, buckets, queries, search capacity | `config/discovery.yaml`, `scraper/discovery.py` |
| Phase 1 discovery architecture | `docs/phase1-discovery-architecture.md` |
| JobSpy call, Google query, per-site window log | `scraper/linkedin_jobspy.py` |
| Fetch, clean, filter, save | `scraper/ingest.py` |
| Hard filters and sponsorship classifier | `scraper/filters.py` |
| Pre-score rank | `scorer/prerank.py` |
| Embedding gate | `scorer/embeddings.py`, `scorer/engine.py` |
| Rubric and the two scoring inputs | `scorer/prompts.py` |
| Candidate block | `config/profile.py` `static_context_block` |
| Your facts | `config/profile.yaml` |
| Thresholds, budget, vector settings | `config/settings.py` |
| Secret-free profile and config identity | `config/diagnostics.py` |
| Phase 0 measurement baseline | `docs/phase0-baseline.md` |
| Stage order | `orchestrator/pipeline.py` |
| Shortlist rule and Telegram file | `bot/prep.py` |
| Production env | `.github/workflows/pipeline.yml` |
