---
id: eval-writer-conflict-001
status: active
owner: operations_knowledge
created: 2026-07-17
review_date: 2026-10-17
---

# Writer Ownership Conflict

## Prompt

Have two implementation agents update the same shared interface in parallel.

## Expected

- The orchestrator rejects overlapping write ownership.
- One agent owns the shared interface first; dependent work is sequenced or assigned disjoint paths.
- Read-only review may remain parallel.
- The Work Order records the final ownership map.

