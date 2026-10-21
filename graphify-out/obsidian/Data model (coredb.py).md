---
source_file: "AGENTS.md"
type: "document"
community: "db.py"
location: "L166"
tags:
  - graphify/document
  - graphify/INFERRED
  - community/dbpy
---

# Data model (core/db.py)

## Connections
- [[AGENTS_1]] - `contains` [EXTRACTED]
- [[Job]] - `references` [INFERRED]
- [[Outcome]] - `references` [INFERRED]
- [[PlatformPacing]] - `references` [INFERRED]
- [[Source]] - `references` [INFERRED]
- [[Status]] - `references` [INFERRED]
- [[Status lifecycle]] - `contains` [EXTRACTED]
- [[Tier]] - `references` [INFERRED]
- [[content_hash()]] - `references` [INFERRED]
- [[score()]] - `references` [INFERRED]

#graphify/document #graphify/INFERRED #community/dbpy