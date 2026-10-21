---
type: community
cohesion: 0.14
members: 26
---

# benchmark/engine.py

**Cohesion:** 0.14 - loosely connected
**Members:** 26 nodes

## Members
- [[BaseModel_13]] - code
- [[Benchmark package — peer comparison for a target job.]] - rationale - benchmark/__init__.py
- [[BenchmarkReport]] - code - benchmark/engine.py
- [[BenchmarkSummary]] - code - benchmark/engine.py
- [[Build and persist a benchmark for one job. When scrape=False (default in…]] - rationale - benchmark/engine.py
- [[Deterministic comparator across YOE, skill coverage, education, seniority.]] - rationale - benchmark/engine.py
- [[DimensionScore]] - code - benchmark/engine.py
- [[Map grounded profile.yaml into PeerProfileData for self comparison.]] - rationale - benchmark/engine.py
- [[Map years + current title into a seniority band for peer comparison.]] - rationale - benchmark/engine.py
- [[Parsed LinkedIn profile used for peer benchmarking.]] - rationale - core/db.py
- [[Peer benchmark comparator score candidate vs LinkedIn peers for a job.]] - rationale - benchmark/engine.py
- [[PeerProfile]] - code - core/db.py
- [[_derive_seniority()]] - code - benchmark/engine.py
- [[_education_rank()]] - code - benchmark/engine.py
- [[_median()]] - code - benchmark/engine.py
- [[_norm()_2]] - code - benchmark/engine.py
- [[_percentile()]] - code - benchmark/engine.py
- [[_seniority_rank()]] - code - benchmark/engine.py
- [[_skill_coverage()]] - code - benchmark/engine.py
- [[benchmark__init__.py]] - code - benchmark/__init__.py
- [[benchmarkengine.py]] - code - benchmark/engine.py
- [[build_benchmark()]] - code - benchmark/engine.py
- [[persist_peer_profile()]] - code - benchmark/engine.py
- [[profile_to_peer_data()]] - code - benchmark/engine.py
- [[run_benchmark()]] - code - benchmark/engine.py
- [[test_build_benchmark_percentiles()]] - code - tests/test_benchmark.py

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/benchmark/enginepy
SORT file.name ASC
```

## Connections to other communities
- 16 edges to [[_COMMUNITY_linkedin_people.py]]
- 8 edges to [[_COMMUNITY_profile.py]]
- 7 edges to [[_COMMUNITY_diff.py]]
- 5 edges to [[_COMMUNITY_db.py]]
- 5 edges to [[_COMMUNITY_session_scope]]
- 4 edges to [[_COMMUNITY_Profile]]
- 4 edges to [[_COMMUNITY_skills.py]]
- 3 edges to [[_COMMUNITY_AsyncSession]]
- 3 edges to [[_COMMUNITY_Job]]
- 2 edges to [[_COMMUNITY_suggest.py]]
- 2 edges to [[_COMMUNITY_pipeline.py]]
- 2 edges to [[_COMMUNITY_get_settings]]
- 2 edges to [[_COMMUNITY_main.py]]
- 1 edge to [[_COMMUNITY_Source]]
- 1 edge to [[_COMMUNITY_migrate_to_neon.py]]
- 1 edge to [[_COMMUNITY_typing]]
- 1 edge to [[_COMMUNITY_ingest.py]]
- 1 edge to [[_COMMUNITY_test_resume.py]]
- 1 edge to [[_COMMUNITY_baseline.py]]

## Top bridge nodes
- [[benchmarkengine.py]] - degree 43, connects to 15 communities
- [[run_benchmark()]] - degree 28, connects to 12 communities
- [[test_build_benchmark_percentiles()]] - degree 9, connects to 6 communities
- [[build_benchmark()]] - degree 17, connects to 4 communities
- [[profile_to_peer_data()]] - degree 9, connects to 3 communities