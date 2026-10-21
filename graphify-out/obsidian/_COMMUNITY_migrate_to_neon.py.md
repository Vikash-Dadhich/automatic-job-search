---
type: community
cohesion: 0.13
members: 23
---

# migrate_to_neon.py

**Cohesion:** 0.13 - loosely connected
**Members:** 23 nodes

## Members
- [[AsyncSession_3]] - code
- [[Copy local SQLite rows into the Neon Postgres database. Reads…]] - rationale - scripts/migrate_to_neon.py
- [[DATABASE_URL normalization for SQLite + Neon Postgres.]] - rationale - tests/test_database_url.py
- [[Make relative sqlite paths absolute so cwd does not matter.]] - rationale - core/db.py
- [[Normalize DATABASE_URL for SQLAlchemy async engines. - Relative sqlite paths…]] - rationale - core/db.py
- [[SQLModel_1]] - code
- [[_absolute_sqlite_url()]] - code - core/db.py
- [[_cell()]] - code - scripts/migrate_to_neon.py
- [[_copy_table()]] - code - scripts/migrate_to_neon.py
- [[_counts()]] - code - scripts/migrate_to_neon.py
- [[_reset_sequences()]] - code - scripts/migrate_to_neon.py
- [[_row()_3]] - code - scripts/migrate_to_neon.py
- [[main()_1]] - code - scripts/migrate_to_neon.py
- [[migrate_to_neon.py]] - code - scripts/migrate_to_neon.py
- [[normalize_database_url()]] - code - core/db.py
- [[sqlalchemy_dialects_postgresql]] - concept
- [[sqlalchemy_ext_asyncio]] - concept
- [[sqlmodel_ext_asyncio_session]] - concept
- [[test_database_url.py]] - code - tests/test_database_url.py
- [[test_normalize_drops_prisma_connection_limit()]] - code - tests/test_database_url.py
- [[test_normalize_keeps_sqlite()]] - code - tests/test_database_url.py
- [[test_normalize_upgrades_postgres_scheme()]] - code - tests/test_database_url.py
- [[test_normalize_upgrades_postgresql()]] - code - tests/test_database_url.py

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/migrate_to_neonpy
SORT file.name ASC
```

## Connections to other communities
- 9 edges to [[_COMMUNITY_db.py]]
- 2 edges to [[_COMMUNITY_get_settings]]
- 1 edge to [[_COMMUNITY_suggest.py]]
- 1 edge to [[_COMMUNITY_diff.py]]
- 1 edge to [[_COMMUNITY_AsyncSession]]
- 1 edge to [[_COMMUNITY_Job]]
- 1 edge to [[_COMMUNITY_benchmarkengine.py]]
- 1 edge to [[_COMMUNITY_company_intelligence.py]]
- 1 edge to [[_COMMUNITY_tracker.py]]
- 1 edge to [[_COMMUNITY_typing]]
- 1 edge to [[_COMMUNITY_asyncio]]
- 1 edge to [[_COMMUNITY_baseline.py]]
- 1 edge to [[_COMMUNITY_skills.py]]
- 1 edge to [[_COMMUNITY_pathlib]]

## Top bridge nodes
- [[migrate_to_neon.py]] - degree 25, connects to 12 communities
- [[sqlmodel_ext_asyncio_session]] - degree 4, connects to 3 communities
- [[normalize_database_url()]] - degree 12, connects to 1 community
- [[test_database_url.py]] - degree 7, connects to 1 community
- [[main()_1]] - degree 6, connects to 1 community