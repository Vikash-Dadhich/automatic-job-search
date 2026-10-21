---
type: community
cohesion: 0.14
members: 25
---

# browser.py

**Cohesion:** 0.14 - loosely connected
**Members:** 25 nodes

## Members
- [[Browser]] - code
- [[BrowserContext]] - code
- [[Checklist (your remaining work)]] - document - SETUP.md
- [[Deploy with Docker]] - document - README.md
- [[Launch Chromium with stealth patches and optional saved storage_state. Yields…]] - rationale - automation/browser.py
- [[One-time interactive LinkedIn login helper (manual MFA). Opens a headful…]] - rationale - scraper/linkedin_session.py
- [[One-time interactive Workday login helper (manual placeholder). Opens a headful…]] - rationale - automation/login.py
- [[Open headful browser; after manual LinkedIn login, persist storage_state.]] - rationale - scraper/linkedin_session.py
- [[Open headful browser; after manual login, persist storage_state. Parameters…]] - rationale - automation/login.py
- [[Page]] - code
- [[Path_9]] - code
- [[Path_10]] - code
- [[Path_11]] - code
- [[Playwright]] - code
- [[Stealth Playwright browser context using saved Workday sessions.]] - rationale - automation/browser.py
- [[What still needs the user (before live runs)]] - document - AGENTS.md
- [[_new_context()]] - code - automation/browser.py
- [[browser.py]] - code - automation/browser.py
- [[launch_context()]] - code - automation/browser.py
- [[linkedin_session.py]] - code - scraper/linkedin_session.py
- [[login.py]] - code - automation/login.py
- [[new_page()]] - code - automation/browser.py
- [[save_linkedin_session()]] - code - scraper/linkedin_session.py
- [[save_session()]] - code - automation/login.py
- [[save_storage_state()]] - code - automation/browser.py

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/browserpy
SORT file.name ASC
```

## Connections to other communities
- 11 edges to [[_COMMUNITY_vault.py]]
- 11 edges to [[_COMMUNITY_workday.py]]
- 8 edges to [[_COMMUNITY_linkedin_people.py]]
- 7 edges to [[_COMMUNITY_get_settings]]
- 4 edges to [[_COMMUNITY_WorkdaySubmitter]]
- 4 edges to [[_COMMUNITY_typing]]
- 3 edges to [[_COMMUNITY_targets.py]]
- 3 edges to [[_COMMUNITY_ingest.py]]
- 3 edges to [[_COMMUNITY_pathlib]]
- 2 edges to [[_COMMUNITY_re]]
- 2 edges to [[_COMMUNITY_main.py]]
- 2 edges to [[_COMMUNITY_asyncio]]
- 1 edge to [[_COMMUNITY_Job Agent]]
- 1 edge to [[_COMMUNITY_conftest.py]]
- 1 edge to [[_COMMUNITY_scheduler.py]]
- 1 edge to [[_COMMUNITY_Remaining Manual Setup]]

## Top bridge nodes
- [[browser.py]] - degree 23, connects to 9 communities
- [[login.py]] - degree 16, connects to 8 communities
- [[linkedin_session.py]] - degree 14, connects to 7 communities
- [[launch_context()]] - degree 22, connects to 5 communities
- [[save_session()]] - degree 13, connects to 4 communities