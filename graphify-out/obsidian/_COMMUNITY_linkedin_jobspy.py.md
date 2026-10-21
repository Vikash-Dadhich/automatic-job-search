---
type: community
cohesion: 0.16
members: 25
---

# linkedin_jobspy.py

**Cohesion:** 0.16 - loosely connected
**Members:** 25 nodes

## Members
- [[dot-provenance_for()]] - code - scraper/discovery.py
- [[Any_45]] - code
- [[Client-side locationremote filter (JobSpy drops is_remote when hours_old set).…]] - rationale - scraper/linkedin_jobspy.py
- [[Employer site already on the source row. The job posting URL is not used.]] - rationale - scraper/linkedin_jobspy.py
- [[Fetch JobSpy postings for the discovery plan, once per selected query.]] - rationale - scraper/linkedin_jobspy.py
- [[Google Jobs needs a natural-language query; bare keywords return little.…]] - rationale - scraper/linkedin_jobspy.py
- [[How each site actually applies ``hours_old`` (JobSpy does not honor it…]] - rationale - scraper/linkedin_jobspy.py
- [[LinkedIn  Indeed discovery via python-jobspy (async wrapper).]] - rationale - scraper/linkedin_jobspy.py
- [[PlannedSearch]] - code - scraper/discovery.py
- [[Shared geo rule for JobSpy pre-filtering, ingest, and the scoring guard.]] - rationale - scraper/filters.py
- [[_dataframe_to_postings()]] - code - scraper/linkedin_jobspy.py
- [[_effective_windows()]] - code - scraper/linkedin_jobspy.py
- [[_explicit_company_url()]] - code - scraper/linkedin_jobspy.py
- [[_external_id()]] - code - scraper/linkedin_jobspy.py
- [[_google_search_term()]] - code - scraper/linkedin_jobspy.py
- [[_jobspy_observations()]] - code - scraper/linkedin_jobspy.py
- [[_location_matches()]] - code - scraper/linkedin_jobspy.py
- [[_parse_posted_at()]] - code - scraper/linkedin_jobspy.py
- [[_row_value()]] - code - scraper/linkedin_jobspy.py
- [[_scrape_term()]] - code - scraper/linkedin_jobspy.py
- [[datetime_15]] - code
- [[fetch_linkedin_indeed()]] - code - scraper/linkedin_jobspy.py
- [[linkedin_jobspy.py]] - code - scraper/linkedin_jobspy.py
- [[location_acceptable()]] - code - scraper/filters.py
- [[math]] - concept

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/linkedin_jobspypy
SORT file.name ASC
```

## Connections to other communities
- 16 edges to [[_COMMUNITY_ingest.py]]
- 8 edges to [[_COMMUNITY_Source]]
- 7 edges to [[_COMMUNITY_targets.py]]
- 5 edges to [[_COMMUNITY_Profile]]
- 3 edges to [[_COMMUNITY_test_discovery.py]]
- 2 edges to [[_COMMUNITY_eligibility.py]]
- 2 edges to [[_COMMUNITY_filters.py]]
- 2 edges to [[_COMMUNITY_test_company_intelligence.py]]
- 2 edges to [[_COMMUNITY_json]]
- 2 edges to [[_COMMUNITY_asyncio]]
- 2 edges to [[_COMMUNITY_workday_rest.py]]
- 1 edge to [[_COMMUNITY_textclean.py]]
- 1 edge to [[_COMMUNITY_discovery_recall.py]]
- 1 edge to [[_COMMUNITY_company_intelligence.py]]
- 1 edge to [[_COMMUNITY_db.py]]
- 1 edge to [[_COMMUNITY_profile.py]]
- 1 edge to [[_COMMUNITY_typing]]

## Top bridge nodes
- [[linkedin_jobspy.py]] - degree 39, connects to 13 communities
- [[fetch_linkedin_indeed()]] - degree 16, connects to 6 communities
- [[location_acceptable()]] - degree 8, connects to 4 communities
- [[_dataframe_to_postings()]] - degree 12, connects to 3 communities
- [[PlannedSearch]] - degree 9, connects to 2 communities