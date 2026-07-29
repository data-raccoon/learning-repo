# Spider-Man Production Graph

An evidence-aware data foundation for reconstructing how film productions are
organized and executed. The first case study is *Spider-Man: Brand New Day*
(2026), with production design as the pilot department.

The project deliberately separates three things:

1. public facts (for example, a credited role);
2. sourced inferences about this production; and
3. generic industry-pattern processes that are plausible but not yet evidenced
   for this production.

JSONL in `data/` is canonical. SQLite and graph exports are derived artifacts.
No private contact or personal-life information belongs in this initiative.

## Quick start

Use the workspace Python interpreter:

```powershell
& "$env:USERPROFILE\.venvs\all\Scripts\python.exe" tools\graph_tool.py validate
& "$env:USERPROFILE\.venvs\all\Scripts\python.exe" tools\graph_tool.py build
& "$env:USERPROFILE\.venvs\all\Scripts\python.exe" tools\graph_tool.py report
& "$env:USERPROFILE\.venvs\all\Scripts\python.exe" tools\graph_tool.py duplicates
& "$env:USERPROFILE\.venvs\all\Scripts\python.exe" tools\graph_tool.py export
& "$env:USERPROFILE\.venvs\all\Scripts\python.exe" -m unittest discover -s tests -v
```

All commands resolve paths relative to this directory, regardless of the
current working directory. `build` writes `build/production-graph.sqlite`;
`report` writes `build/coverage.json`; and `export` writes JSON, Cytoscape JSON,
CSV, and GraphML to `exports/`.

## Canonical records

- `entities.jsonl`: graph nodes with stable opaque IDs and aliases.
- `edges.jsonl`: typed directed relationships.
- `claims.jsonl`: assertions about entities or edges, including status,
  confidence, rationale, and evidence references.
- `sources.jsonl`: public-source registry and source authority tier.
- `extraction-manifests.jsonl`: reproducible acquisition/extraction ledger.
- `identity-resolutions.jsonl`: explicit merge/no-merge decisions.

The schemas in `schemas/v1/` are the public data contract. The validator
implements the cross-file rules that JSON Schema alone cannot express.

## Pilot status

The current seed demonstrates the complete model using publicly discoverable
information: the production, production designer Charles Wood, a small
representative art-department slice, and a reconstructed production-design
workflow. It is not represented as the complete on-screen credit roll. See
`research/coverage-gaps.md` and `research/expansion-playbook.md`.

## Evidence labels

| Status | Meaning |
| --- | --- |
| `verified` | Directly supported by one or more cited public sources. |
| `inferred` | A production-specific conclusion derived from cited evidence. |
| `industry-pattern` | A normal film-production pattern used as a research hypothesis. |
| `disputed` | Public sources conflict; alternatives remain preserved. |

Confidence is a numeric assessment from `0.0` to `1.0`; it never replaces the
status label or the cited evidence.

## Viewing the graph

Use **Cytoscape Desktop** as the default interactive viewer. It is the better
fit for this evidence-aware semantic graph because it supports attribute-based
filtering and close inspection of nodes and relationships. This makes it easier
to explore questions such as which people belong to a team, which processes a
team performs, and which processes produce a particular asset.

Open `exports/graph.graphml` in Cytoscape after running the export command.

Use **Gephi** when the objective is large-scale network analysis, clustering,
centrality analysis, or presentation-oriented graph layouts. Gephi is useful
for discovering collaboration patterns, but it is less convenient for
inspecting evidence-rich records one relationship at a time.

The current GraphML export includes entity names and types plus relationship
types. Complete claim provenance, confidence, evidence status, and source
records remain available in `graph-complete.json`, `graph-cytoscape.json`, and
the generated SQLite database. GraphML is therefore suitable for immediate
structural exploration, but it is not the complete evidence package.

### Inspecting types in Cytoscape

The **Table Panel** at the bottom-right of Cytoscape shows the attributes of a
selected graph element. Press `F5` if the panel is hidden. After selecting a
node, use the Node Table and enable the `name` and `type` columns. After
selecting an edge, use the Edge Table and enable `edge_type`.

For type information directly in the graph canvas, configure hover tooltips:

1. Open **Control Panel → Style** and select the **Node** tab.
2. Add or locate **Tooltip**.
3. Set its mapping column to `type` and choose **Passthrough Mapping**.
4. Repeat under the **Edge** tab using `edge_type`.

Hovering over an element will then display its type. Clicking selects the
corresponding row in the Table Panel; Cytoscape does not normally open a
click-based popover. Node and edge labels can also be mapped to these type
columns, but persistent type labels tend to clutter the graph.

The GraphML export does not currently include nested metadata such as
`identity_state`. Import `exports/nodes.csv` as Node Table columns, joining its
`id` column to the network column containing the stable entity IDs (normally
`shared name`), to inspect the raw `attributes_json` values. Identity state
belongs to person nodes—for example, Nigel Archer—not to their credited-role
nodes.
