# Discovery recall benchmark

This measures whether stored jobs include a frozen list of Summer 2027 MBA internships. It is recall on that list only. It is not the share of internships that exist in the market, and it is not the search-execution coverage in [Phase 3](phase3-discovery-coverage.md).

The list does not change discovery, fit, eligibility, priority, shortlist, portfolio, or applications.

## What is checked in

`tests/fixtures/discovery_recall_benchmark.yaml`, version `discovery-recall-v1`.

The checked-in list currently has no cases. Recall is unavailable. An empty list is not 100% and not 0%.

Add a case only after a person has opened the posting on a V1 board: LinkedIn, Indeed, Google, ZipRecruiter, or a configured Workday tenant. Record the date, a short provenance note, the title and employer, and either the posting URL or the source plus external id. Mark `relevant`, `internship`, and `summer_2027` from the posting itself, not from whether this pipeline stored it. Set `role_family` only when that label was verified. Do not paste the full description, and do not invent a URL or id.

One posting observed on two boards is one case with two observations. It counts once in the denominator.

## Matching

`scraper/discovery_recall.py` uses the same identity rules as job upsert:

- the same source and external id
- or the same canonical posting URL, without a location or employer conflict
- or the same description hash with the same company, title, and agreeing location, and without two different posting URLs

A shared title is not a match.

Only cases with `relevant`, `internship`, and `summer_2027` all true enter the denominator. Recall is matched cases divided by that count, as a percentage rounded to one decimal. Unmatched case ids are listed.

## Reproduce

```bash
uv run pytest -q tests/test_discovery_recall.py
```

The CI check runs this file with the rest of `tests/`. The test does not call a job board.

## Limits

The list will be biased toward postings someone could open and verify. A miss means the stored rows did not contain that identity. It does not mean the posting was absent from the board, and it does not mean a search failed. Search coverage remains a separate report.
