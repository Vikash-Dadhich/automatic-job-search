---
source_file: "automation/runner.py"
type: "code"
community: "runner.py"
location: "L75"
tags:
  - graphify/code
  - graphify/EXTRACTED
  - community/runnerpy
---

# _eligible()

## Connections
- [[dot-apply_pending()]] - `calls` [EXTRACTED]
- [[Job]] - `uses` [INFERRED]
- [[Source]] - `uses` [INFERRED]
- [[Workday source OR any source whose URL is a Workday company apply link.]] - `rationale_for` [EXTRACTED]
- [[_cmd_list_apply()]] - `calls` [EXTRACTED]
- [[_ready_for_explicit_apply()]] - `calls` [EXTRACTED]
- [[application_portfolio.py]] - `imports` [EXTRACTED]
- [[apply_portfolio()]] - `calls` [EXTRACTED]
- [[is_automateable_apply_url()]] - `calls` [EXTRACTED]
- [[main.py]] - `imports` [EXTRACTED]
- [[runner.py]] - `contains` [EXTRACTED]

#graphify/code #graphify/EXTRACTED #community/runnerpy