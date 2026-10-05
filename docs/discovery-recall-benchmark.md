# Discovery recall benchmark

This measures whether stored jobs include a frozen list of Summer 2027 MBA internships. It is recall on that list only. It is not the share of internships that exist in the market, and it is not the search-execution coverage in [Phase 3](phase3-discovery-coverage.md).

The list does not change discovery, fit, eligibility, priority, shortlist, portfolio, or applications.

## What is checked in

`tests/fixtures/discovery_recall_benchmark.yaml`, version `discovery-recall-v1`.

The checked-in list is a bounded set opened on 2026-10-04. It is not the market. An empty eligible list is not 100% and not 0%.

Add a case only after the posting has been opened on a V1 board: LinkedIn, Indeed, Google, ZipRecruiter, or a configured Workday tenant. Record the date, a short provenance note, the title and employer, and either the posting URL or the source plus external id. Mark `relevant`, `internship`, and `summer_2027` from the posting itself, not from whether this pipeline stored it. Set `role_family` only when that label was verified, using a discovery family id when one fits. Do not paste the full description, and do not invent a URL or id.

The 2026-10-04 pass opened LinkedIn job pages and the public Workday posting API for the configured tenants (NVIDIA, Salesforce, Workday, Zillow, Boeing, Adobe). Indeed returned HTTP 403, so no Indeed case was added. Google Jobs and ZipRecruiter were not opened as original postings. Company career sites that are not a configured Workday tenant were not used as the observation, even when they described the same internship. Postings that did not state both an MBA internship and Summer 2027 stayed out of the denominator. Examples left out: Adobe “2027 MBA Intern” pages that never say summer, Adobe full-time MBA graduate roles, Salesforce bachelor’s internships, Boeing summer internships that accept a bachelor’s or master’s degree, NVIDIA PhD and engineering internships, and an Alvarez & Marsal page whose body did not state Summer 2027. A second city listing of the same title was not given its own case when it looked like the same program.

## Label corrections on 2026-10-04

The first measurement against the stored snapshot (`discovered_at` through 2026-09-29) was 4 matched out of 22 verified positives, 18.2%. Two fixture labels were wrong.

Marvell `li-4469345846` used the employer “Marvell Semiconductor.” The opened LinkedIn page and stored row `li-4469345846` both say “Marvell Technology,” with the same title, city, and URL. The employer conflict blocked that source id. The fixture employer is now “Marvell Technology.” Identity matching in production was not changed.

Intuit `li-4473553475` stays in the file. The opened page says “MBA Intern for Summer 2027” and also “beginning in May or June 2026.” `summer_2027` is false, so the case is not a verified positive and is not a verified negative. It returns to the denominator only after the start year is resolved.

Those corrections are label fixes. Re-measured with this fixture and the existing evaluator against the same snapshot, the result is 5 matched out of 21 verified positives, 23.8%. That figure is still only this list. Indeed was blocked, and Google Jobs and ZipRecruiter were not opened. A miss still means the stored snapshot did not contain that identity. It does not mean the posting was absent from the board.

One posting observed on two boards is one case with two observations. It counts once in the denominator.

## Matching

`scraper/discovery_recall.py` uses the same identity rules as job upsert:

- the same source and external id, unless the employer or a specific location clearly conflicts
- or the same canonical posting URL, with those same conflict checks
- or the same description hash with the same company, title, and agreeing location, and without two different posting URLs

A shared title is not a match.

Only cases with `relevant`, `internship`, and `summer_2027` all true enter the denominator. Recall is matched cases divided by that count, as a percentage rounded to one decimal. Unmatched case ids are listed.

## Reproduce

```bash
uv run pytest -q tests/test_discovery_recall.py
```

The CI check runs this file with the rest of `tests/`. The test loads the fixture and measures it against an empty job list. It does not call a job board and it does not read the stored job database. A separate read-only comparison is required for recall against stored rows.

## Limits

The list will be biased toward postings someone could open and verify. A miss means the stored rows did not contain that identity. It does not mean the posting was absent from the board, and it does not mean a search failed. Search coverage remains a separate report.
