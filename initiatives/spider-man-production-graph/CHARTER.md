# Initiative charter

## Purpose

Build a reusable and explorable representation of the people, organizations,
roles, deliverables, and processes involved in making a company-scale creative
product. Film production is the first domain and *Spider-Man: Brand New Day* is
the first case study.

## Research boundary

The initiative uses public professional information: official studio pages,
guild and professional records, production and vendor pages, portfolios,
interviews, trade publications, and public credit databases. It excludes
private contact information, personal-life data, speculation about protected
characteristics, unlawfully acquired material, and any claim whose only basis
is an unattributed rumor.

The pilot covers production design and adjacent art-department functions.
“Exactly how it was made” means the best supportable reconstruction, not an
assertion of omniscience. Unknowns and disagreements remain first-class data.

## Source hierarchy

1. `official`: studios, distributors, filmmakers, and official production media.
2. `professional`: guilds, credited vendors, portfolios, and professional records.
3. `trade`: attributable interviews and established trade publications.
4. `credit_database`: public film-credit databases.
5. `secondary`: other attributable reporting used for discovery or corroboration.

Lower-tier sources can establish a seed claim but should be corroborated before
the claim is treated as publication-ready. A source's authority depends on the
claim: a vendor is authoritative about its own participation but not necessarily
about the whole production.

## Confidence policy

- `0.90–1.00`: direct, unambiguous primary or mutually corroborated evidence.
- `0.70–0.89`: strong secondary evidence or a constrained inference.
- `0.40–0.69`: plausible hypothesis with meaningful unresolved alternatives.
- `<0.40`: discovery lead only; normally rejected from the graph.

Every factual edge needs a claim and evidence. Every inference needs a method,
rationale, and confidence. Industry patterns may cite general methodology rather
than production-specific evidence, but must never be presented as verified.

## Contradictions and identity

Conflicting claims are retained independently and marked `disputed`. A review
decision can identify the preferred interpretation and rationale without
deleting alternatives.

Names are labels, not identifiers. Stable IDs are assigned once and aliases are
stored separately. People may be merged only with corroborating professional
identifiers or two independent professional attributes. Ambiguous identities
remain separate and appear in the unresolved-identity report.

## Deliverables

- versioned JSON Schemas and canonical JSONL;
- deterministic validation and SQLite materialization;
- coverage and duplicate/identity reports;
- complete JSON, Cytoscape JSON, CSV, and GraphML exports;
- a reproducible research ledger and expansion playbook.

The future explorer must consume generated exports or SQLite. It must show
evidence status, confidence, sources, contradictions, and known coverage gaps.
It must not become the source of truth.

