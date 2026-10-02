# Structured JD intelligence

The normalized description remains the text the rest of the pipeline stores and hashes. This layer is a second reading of that same text. It does not replace `description_clean`, and it does not change role family, fit, eligibility, priority, shortlist, portfolio, applications, feedback, calibration, or monitoring.

## What is stored

`structured_job_descriptions` holds one row per job:

- `content_hash` — the normalized JD hash the reading was built from
- `version` — `phase19-v1`
- `availability` — `available`, `partial` (truncated text), or `unavailable` (missing or suspiciously short)
- `document` — responsibilities, required and preferred qualifications, experience, education and MBA, functional phrases, internship or program signals, work model, sponsorship and authorization evidence, and domain phrases

Each extracted item keeps a short snippet and an explicit basis. A usable JD with no mention is `not_mentioned`. A missing or unreadable JD stays `unknown`. Nothing is filled in from the job title or the company name.

`MBA internship` records the program. It does not, by itself, mark an MBA degree as required.

## Cache

A row is current only when its hash equals the job's normalized hash and its version is `phase19-v1`. Ingestion writes the row after the job is saved. The same text is not extracted again. A changed description drops the old row and the next pass writes a new one. Jobs that have never been through this pass simply have no row.

## Limits

The extractor is deterministic and phrase-based. Headings it does not recognize do not become qualifications. Years, degrees, sponsorship, and clearance are recorded only when the wording is explicit. This file is evidence for later fixes. It is not a decision.
