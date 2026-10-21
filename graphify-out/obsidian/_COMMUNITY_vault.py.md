---
type: community
cohesion: 0.15
members: 26
---

# vault.py

**Cohesion:** 0.15 - loosely connected
**Members:** 26 nodes

## Members
- [[dot-is_placeholder()_1]] - code - automation/vault.py
- [[Any_46]] - code
- [[BaseModel_9]] - code
- [[CredentialsFile]] - code - automation/vault.py
- [[Load credentials.yaml (optional; missing file = empty tenants).]] - rationale - automation/vault.py
- [[Look up credentials by tenant key (case-insensitive).]] - rationale - automation/vault.py
- [[MonkeyPatch_28]] - code
- [[Path_49]] - code
- [[Path_50]] - code
- [[Path to Playwright storage_state JSON for a Workday tenant slug.]] - rationale - automation/vault.py
- [[Per-tenant credentials and Playwright storage_state paths.]] - rationale - automation/vault.py
- [[TenantCredentials]] - code - automation/vault.py
- [[Tests for credential vault and session path helpers.]] - rationale - tests/test_vault.py
- [[_load_yaml()_2]] - code - automation/vault.py
- [[get_tenant_credentials()]] - code - automation/vault.py
- [[has_saved_session()]] - code - automation/vault.py
- [[load_credentials()]] - code - automation/vault.py
- [[reload_credentials()]] - code - automation/vault.py
- [[session_state_path()]] - code - automation/vault.py
- [[test_get_tenant_credentials_placeholder_skip()]] - code - tests/test_vault.py
- [[test_has_saved_session()]] - code - tests/test_vault.py
- [[test_load_credentials_missing_file()]] - code - tests/test_vault.py
- [[test_session_state_path()]] - code - tests/test_vault.py
- [[test_session_state_path_rejects_empty()]] - code - tests/test_vault.py
- [[test_vault.py]] - code - tests/test_vault.py
- [[vault.py]] - code - automation/vault.py

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/vaultpy
SORT file.name ASC
```

## Connections to other communities
- 11 edges to [[_COMMUNITY_browser.py]]
- 4 edges to [[_COMMUNITY_get_settings]]
- 4 edges to [[_COMMUNITY_pytest]]
- 2 edges to [[_COMMUNITY_typing]]
- 2 edges to [[_COMMUNITY_pathlib]]
- 1 edge to [[_COMMUNITY_session_scope]]
- 1 edge to [[_COMMUNITY_main.py]]
- 1 edge to [[_COMMUNITY_conftest.py]]
- 1 edge to [[_COMMUNITY_ingest.py]]
- 1 edge to [[_COMMUNITY_linkedin_people.py]]
- 1 edge to [[_COMMUNITY_targets.py]]

## Top bridge nodes
- [[vault.py]] - degree 21, connects to 8 communities
- [[test_vault.py]] - degree 15, connects to 3 communities
- [[has_saved_session()]] - degree 9, connects to 3 communities
- [[session_state_path()]] - degree 15, connects to 2 communities
- [[load_credentials()]] - degree 9, connects to 2 communities