# Spider-Man Production Graph Initiative

## Summary

Create `initiatives/spider-man-production-graph/` as a reusable, evidence-aware data foundation for reconstructing how film productions are organized and executed. The first case study will be Sony/Marvel’s *Spider-Man: Brand New Day* (2026), with production design as the end-to-end pilot.

The canonical dataset will use version-controlled JSONL, with SQLite generated as a query layer. Public databases and professional public sources will be used; no end-credit recording is assumed.

## Key Changes

- Establish an initiative charter defining research boundaries, terminology, source policy, confidence rules, deliverables, and the path toward a future visual explorer.
- Model these primary entity types:
  - Production, person, credited role, department, team, company/vendor, location, asset/deliverable, process, production phase, tool/technology, source, and claim.
- Represent relationships as typed, directed edges such as:
  - `PERSON_CREDITED_AS_ROLE`
  - `ROLE_MEMBER_OF_TEAM`
  - `TEAM_PART_OF_DEPARTMENT`
  - `PERSON_AFFILIATED_WITH_COMPANY`
  - `COMPANY_PROVIDED_SERVICE`
  - `PROCESS_PRECEDES_PROCESS`
  - `TEAM_PERFORMS_PROCESS`
  - `PROCESS_PRODUCES_ASSET`
  - `PROCESS_HANDS_OFF_TO_TEAM`
- Attach provenance to every factual or inferred claim:
  - Source URL, publisher, publication/access dates, source type, supporting excerpt or locator, extraction method, confidence, and `verified`, `inferred`, or `industry-pattern` status.
  - Preserve contradictory claims rather than silently choosing one; record the preferred interpretation and rationale separately.
- Keep raw normalized records in JSONL and build a deterministic SQLite database containing indexed entity, edge, claim, source, alias, and evidence tables.
- Provide stable IDs independent of names, plus aliases and identity-resolution records to prevent accidental merging of similarly named people or companies.
- Add exports suitable for the later explorer: complete JSON, Cytoscape-compatible JSON, CSV node/edge tables, and GraphML.

## Pilot and Research Workflow

- Build a public-source registry ranked by authority: official studio material, guild and professional records, production/vendor pages, interviews and trade publications, then public credit databases and secondary reporting.
- Inventory all publicly discoverable credits before normalization and record source coverage gaps explicitly.
- Populate the production-design pilot across art direction, concept art, set design, construction, props, graphics, locations, set decoration, and related vendors where supported.
- Reconstruct processes by production phase—development, pre-production, production, post-production, and delivery—linking teams, inputs, outputs, dependencies, and handoffs.
- Use professional public data for people: credited work, employers, vendors, portfolios, guild membership, interviews, and relevant prior productions. Exclude private contact details and personal-life information.
- Add a reproducible research ledger recording queries, extraction runs, unresolved identities, rejected claims, and review decisions.
- Document how the same schema and pipeline can subsequently expand to every credited department and other companies or productions.

## Interfaces and Validation

- Define versioned JSON Schemas for entities, edges, claims, sources, and extraction manifests.
- Provide deterministic commands for validation, SQLite rebuilding, coverage reporting, duplicate detection, and graph export.
- Validate that:
  - Every edge references existing entities.
  - Every asserted fact has at least one source.
  - Every inference has a method, rationale, and confidence.
  - Person merges require corroborating professional identifiers.
  - Process ordering is acyclic unless explicitly marked iterative.
  - Rebuilding SQLite and exports from unchanged JSONL produces equivalent results.
- Generate coverage reports by department, source, confidence, and evidence status.

## Test and Acceptance Plan

- Parse representative official, vendor, interview, and public-credit records into normalized fixtures.
- Test ambiguous names, aliases, multiple simultaneous roles, uncredited public claims, vendor subteams, conflicting sources, inaccessible sources, and iterative workflows.
- Confirm the production-design pilot can answer:
  - Who participated, in which role, team, department, and company?
  - Which processes did each team likely perform?
  - What inputs, outputs, dependencies, and handoffs connected those processes?
  - Which answers are directly evidenced versus reconstructed?
  - What remains unknown or disputed?
- Acceptance requires schema-valid canonical data, reproducible SQLite and graph exports, no orphaned relationships, complete claim provenance, and a documented expansion procedure.

## Assumptions

- “New Spider-Man movie” means *Spider-Man: Brand New Day*, officially listed by [Sony Pictures](https://www.sonypictures.com/movies/spidermanbrandnewday) and [Marvel](https://www.marvel.com/movies/spider-man-brand-new-day).
- The first milestone is the initiative architecture plus a populated production-design pilot, not the complete all-department graph or visual frontend.
- “Exactly how it was made” is treated as a best-supported reconstruction. The system will clearly distinguish direct evidence from inference and unknowns.
- Public sources may not reproduce every on-screen credit; missing-credit coverage will be measured and exposed rather than silently treated as complete.
- JSONL is canonical, SQLite is generated, and the future explorer consumes exported graph data rather than becoming the source of truth.
