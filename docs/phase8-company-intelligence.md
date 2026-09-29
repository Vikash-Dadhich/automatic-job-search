# Phase 8 company intelligence

Phase 8 records factual information about an employer. It does not decide whether the candidate should apply, whether one company is better than another, or whether the company will sponsor a visa.

## What it is

Role classification says what the job is. Candidate fit says how well the candidate matches the description. Role-family weight says how important that family is in the internship portfolio. Company intelligence says what we can support about the employer from a source. Eligibility and priority are later phases. This phase does not combine those signals.

The record is factual. It can say that a source calls the company public, names a headquarters city, or states an employee phrase that appears in the text. It does not say that a company is prestigious, excellent, or a weak employer. There is no company score.

## Schema

`company_intelligence` is its own table. Jobs keep the discovered `company` string. `Job.company_intelligence_id` points at the shared row. Two jobs can share one row. They stay separate jobs, with their own source and external id.

Stored fields are the lookup key, the raw and canonical names, website, industry, company type, public or private, headquarters, employee range, founded year, parent company, a short self-description, sources, confidence, status, `phase8-v1`, and timestamps. A field stays null when the source does not state it.

Status is `complete`, `partial`, `unresolved`, or `failed`. Confidence is `high`, `medium`, or `low`. Those words describe the evidence, not whether the company is attractive. `failed` and `unresolved` do not mean the company is a bad place to apply.

## Sources

A fact is stored only when a pattern in the retrieved text states it. A provider may also return extra claims. Those claims are ignored. The service does not use an LLM as the source of company facts, and it does not use the candidate profile.

Each stored source has a type, a URL, and a retrieved time. Types are `official_website`, `careers`, `sec`, `regulatory`, and `other`. The caller supplies the URL. The HTTP adapter performs one GET of that URL, with a short timeout and no crawl. It does not invent a domain from the company name, and it does not treat the job description or the job's location as company facts. A Workday posting URL is not fetched as a company profile.

If no reliable URL is available, the row is `unresolved` and every fact stays null. If the request times out, errors, or returns nothing usable, the row is `failed` when nothing trustworthy was stored yet. A failure on a later refresh keeps facts that were already stored. Either way the job remains usable, and scoring still runs.

## Names and reuse

The lookup key trims whitespace, lowercases the name, and drops trailing legal suffixes such as Inc, LLC, and Corp. `Acme, Inc.` and `Acme Inc` share one row. `Mercury`, `Mercury Systems`, and `Mercury Insurance` do not. Interior words are kept, because a shorter name is not safe proof that two employers are the same.

The first lookup for a key calls the provider once when a URL was supplied. Later jobs with that key reuse the row. An explicit refresh may call the provider again. Refreshing the company row does not clear fit, role-family weight, tier, status, discovery fields, or the vector score. Changing a job description does not delete the company row.

## What this phase does not change

Discovery queries, capacity, and coverage stay as they are. Fit still answers only how the candidate matches the description. Role-family weights stay 40, 40, 15, and 5. Dream-company preference and the company cooldown window are untouched. There is no visa decision, no job-identity merge, and no priority score.
