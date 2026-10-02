# Company intelligence 2.0

This layer records factual employer context on the existing `company_intelligence` row. It does not score the employer, the candidate, or the job.

## What it stores

`context` is a document with `version` `phase8-v2` and a `signals` list. Each signal has a name, a value, a short snippet, `basis: explicit`, a source type, a source URL, and `observed_at`.

Signals cover domains the page actually names, internship and MBA program language, U.S. presence language, and scale phrases such as revenue, a stock exchange, employee count, country count, and office count. The older columns (industry, headquarters, public or private, and the rest) stay as they were.

A missing phrase is absent. It is not stored as false, except an explicit statement that U.S. operations do not exist.

## What it does not store

There is no prestige, culture, reputation, brand, or employer-quality score, and no hidden equivalent. Dream-company preference stays a separate setting. Glassdoor, follower counts, and ranking lists are not sources.

Company-level facts do not decide job eligibility. A page that mentions visa sponsorship does not change the Phase 9 result for a job. Fit, priority, portfolio weight, and shortlist selection do not read these signals.

## Sources and refresh

Source types stay `official_website`, `careers`, `sec`, `regulatory`, and `other`. The caller still supplies the URL. The service does not guess a domain and does not call a model.

When the same URL is read again, that URL's previous signals are replaced by what the new text states. Signals from other URLs remain. If two sources disagree, the higher-priority source wins: official website, then careers, then regulatory, then SEC, then other. A page that does not mention a fact is not a contradiction.

The same text does not add a second copy of a signal. A changed page replaces that source's signals. `intelligence_version` on a newly written row is `phase8-v2`. A lookup that fails before any trustworthy text is stored does not erase facts already kept.

## Company versus job

"The company has U.S. operations" is a company fact. "This job refuses sponsorship" is a job fact. The company record must not override the job. Later priority work may read `context`. This phase does not change the priority formula.
