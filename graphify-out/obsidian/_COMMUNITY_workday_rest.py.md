---
type: community
cohesion: 0.10
members: 40
---

# workday_rest.py

**Cohesion:** 0.10 - loosely connected
**Members:** 40 nodes

## Members
- [[Any_5]] - code
- [[AsyncClient]] - code
- [[Coerce Workday locationcompany fields (str  dict  None) to plain text.]] - rationale - scraper/workday_rest.py
- [[Decode JSON or raise WorkdayBlockedError on HTMLchallenge bodies.]] - rationale - scraper/workday_rest.py
- [[Exception]] - code
- [[Fetch from many tenants concurrently; failures are isolated.]] - rationale - scraper/workday_rest.py
- [[Fetch recent postings from a single Workday tenant.]] - rationale - scraper/workday_rest.py
- [[Interpret Workday's relative postedOn strings for ~24h shortlisting.]] - rationale - scraper/workday_rest.py
- [[Job discovery scrapers (LinkedInIndeed via JobSpy, Workday CXS REST).]] - rationale - scraper/__init__.py
- [[Raised when a tenant returns 403  challenge  Akamai block.]] - rationale - scraper/workday_rest.py
- [[Rate limit or temporary unavailability — retried before giving up. Subclasses…]] - rationale - scraper/workday_rest.py
- [[Response]] - code
- [[Semaphore]] - code
- [[Tests for Workday recency helpers (no network).]] - rationale - tests/test_workday_recency.py
- [[Workday CXS REST client for public career portals (async httpx).]] - rationale - scraper/workday_rest.py
- [[WorkdayBlockedError]] - code - scraper/workday_rest.py
- [[WorkdayTransientError]] - code - scraper/workday_rest.py
- [[_as_text()]] - code - scraper/workday_rest.py
- [[_company_name()]] - code - scraper/workday_rest.py
- [[_fetch_detail()]] - code - scraper/workday_rest.py
- [[_fetch_listing_page()]] - code - scraper/workday_rest.py
- [[_is_recent_posted_on()]] - code - scraper/workday_rest.py
- [[_one()]] - code - scraper/workday_rest.py
- [[_parse_json()]] - code - scraper/workday_rest.py
- [[_parse_start_date()]] - code - scraper/workday_rest.py
- [[_request()]] - code - scraper/workday_rest.py
- [[_within_hours()]] - code - scraper/workday_rest.py
- [[_workday_observation()]] - code - scraper/workday_rest.py
- [[datetime_1]] - code
- [[fetch_all_workday()]] - code - scraper/workday_rest.py
- [[fetch_workday()]] - code - scraper/workday_rest.py
- [[retry]] - code
- [[scraper__init__.py]] - code - scraper/__init__.py
- [[test_as_text_coercion()]] - code - tests/test_workday_recency.py
- [[test_company_name_ignores_location_field()]] - code - tests/test_workday_recency.py
- [[test_is_recent_posted_on_variants()]] - code - tests/test_workday_recency.py
- [[test_parse_start_date()]] - code - tests/test_workday_recency.py
- [[test_within_hours()]] - code - tests/test_workday_recency.py
- [[test_workday_recency.py]] - code - tests/test_workday_recency.py
- [[workday_rest.py]] - code - scraper/workday_rest.py

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/workday_restpy
SORT file.name ASC
```

## Connections to other communities
- 15 edges to [[_COMMUNITY_targets.py]]
- 14 edges to [[_COMMUNITY_ingest.py]]
- 11 edges to [[_COMMUNITY_Source]]
- 4 edges to [[_COMMUNITY_asyncio]]
- 2 edges to [[_COMMUNITY_HttpCompanyIntelProvider]]
- 2 edges to [[_COMMUNITY_re]]
- 2 edges to [[_COMMUNITY_linkedin_jobspy.py]]
- 1 edge to [[_COMMUNITY_diff.py]]
- 1 edge to [[_COMMUNITY_pathlib]]
- 1 edge to [[_COMMUNITY_db.py]]
- 1 edge to [[_COMMUNITY_typing]]
- 1 edge to [[_COMMUNITY_baseline.py]]

## Top bridge nodes
- [[workday_rest.py]] - degree 37, connects to 9 communities
- [[fetch_workday()]] - degree 21, connects to 6 communities
- [[scraper__init__.py]] - degree 13, connects to 4 communities
- [[fetch_all_workday()]] - degree 10, connects to 4 communities
- [[test_workday_recency.py]] - degree 15, connects to 2 communities