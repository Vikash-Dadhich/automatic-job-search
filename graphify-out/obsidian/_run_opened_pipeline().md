---
source_file: "orchestrator/pipeline.py"
type: "code"
community: "pipeline.py"
location: "L230"
tags:
  - graphify/code
  - graphify/EXTRACTED
  - community/pipelinepy
---

# _run_opened_pipeline()

## Connections
- [[Any_16]] - `references` [EXTRACTED]
- [[PipelineSummary]] - `references` [EXTRACTED]
- [[_apply_allocated()]] - `indirect_call` [INFERRED]
- [[_benchmark_stage()]] - `indirect_call` [INFERRED]
- [[_note_skipped()]] - `calls` [EXTRACTED]
- [[_portfolio_stage()]] - `indirect_call` [INFERRED]
- [[_prep_stage()]] - `indirect_call` [INFERRED]
- [[_prepare_shortlisted_resumes()]] - `indirect_call` [INFERRED]
- [[_run_stage()]] - `calls` [EXTRACTED]
- [[_safe_close_run()]] - `calls` [EXTRACTED]
- [[_shortlist_stage()]] - `indirect_call` [INFERRED]
- [[_suggest_stage()]] - `indirect_call` [INFERRED]
- [[effective_baseline()]] - `calls` [EXTRACTED]
- [[pipeline.py]] - `contains` [EXTRACTED]
- [[run_pipeline()]] - `calls` [EXTRACTED]
- [[time]] - `calls` [EXTRACTED]
- [[write_effective_baseline()]] - `calls` [EXTRACTED]

#graphify/code #graphify/EXTRACTED #community/pipelinepy