#!/usr/bin/env python3
"""Validate, materialize, report, and export the production graph."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import sqlite3
import sys
from collections import Counter, defaultdict
from datetime import date, datetime
from pathlib import Path
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
SCHEMAS = ROOT / "schemas" / "v1"
BUILD = ROOT / "build"
EXPORTS = ROOT / "exports"

FILES = {
    "entities": DATA / "entities.jsonl",
    "edges": DATA / "edges.jsonl",
    "claims": DATA / "claims.jsonl",
    "sources": DATA / "sources.jsonl",
    "manifests": DATA / "extraction-manifests.jsonl",
    "identities": DATA / "identity-resolutions.jsonl",
}
SCHEMA_FILES = {
    "entities": SCHEMAS / "entity.schema.json",
    "edges": SCHEMAS / "edge.schema.json",
    "claims": SCHEMAS / "claim.schema.json",
    "sources": SCHEMAS / "source.schema.json",
    "manifests": SCHEMAS / "extraction-manifest.schema.json",
    "identities": SCHEMAS / "identity-resolution.schema.json",
}


class ValidationFailure(Exception):
    pass


def read_jsonl(path: Path) -> list[dict]:
    records = []
    with path.open(encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, 1):
            if not line.strip():
                continue
            try:
                value = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValidationFailure(f"{path.name}:{line_number}: {exc}") from exc
            if not isinstance(value, dict):
                raise ValidationFailure(f"{path.name}:{line_number}: record must be an object")
            records.append(value)
    return records


def load_all() -> dict[str, list[dict]]:
    return {name: read_jsonl(path) for name, path in FILES.items()}


def _matches_type(value, expected: str) -> bool:
    types = {
        "object": dict,
        "array": list,
        "string": str,
        "number": (int, float),
        "integer": int,
        "boolean": bool,
        "null": type(None),
    }
    return isinstance(value, types[expected]) and not (
        expected in {"number", "integer"} and isinstance(value, bool)
    )


def _validate_subset(value, schema: dict, path: str, errors: list[str]) -> None:
    expected = schema.get("type")
    if expected:
        options = expected if isinstance(expected, list) else [expected]
        if not any(_matches_type(value, item) for item in options):
            errors.append(f"{path}: expected {' or '.join(options)}")
            return
    if "const" in schema and value != schema["const"]:
        errors.append(f"{path}: must equal {schema['const']!r}")
    if "enum" in schema and value not in schema["enum"]:
        errors.append(f"{path}: unsupported value {value!r}")
    if isinstance(value, str):
        if len(value) < schema.get("minLength", 0):
            errors.append(f"{path}: string is too short")
        if len(value) > schema.get("maxLength", 10**12):
            errors.append(f"{path}: string is too long")
        if schema.get("pattern") and not re.search(schema["pattern"], value):
            errors.append(f"{path}: does not match {schema['pattern']}")
        try:
            if schema.get("format") == "date":
                date.fromisoformat(value)
            elif schema.get("format") == "date-time":
                datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError:
            errors.append(f"{path}: invalid {schema['format']}")
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        if value < schema.get("minimum", value):
            errors.append(f"{path}: below minimum")
        if value > schema.get("maximum", value):
            errors.append(f"{path}: above maximum")
    if isinstance(value, dict):
        required = schema.get("required", [])
        for key in required:
            if key not in value:
                errors.append(f"{path}: missing required property {key}")
        properties = schema.get("properties", {})
        if schema.get("additionalProperties") is False:
            for key in value.keys() - properties.keys():
                errors.append(f"{path}: unexpected property {key}")
        for key, child in value.items():
            child_schema = properties.get(key)
            if child_schema:
                _validate_subset(child, child_schema, f"{path}.{key}", errors)
    if isinstance(value, list):
        if len(value) < schema.get("minItems", 0):
            errors.append(f"{path}: too few items")
        if schema.get("uniqueItems"):
            serialized = [json.dumps(item, sort_keys=True) for item in value]
            if len(serialized) != len(set(serialized)):
                errors.append(f"{path}: items must be unique")
        item_schema = schema.get("items")
        if item_schema:
            for index, child in enumerate(value):
                _validate_subset(child, item_schema, f"{path}[{index}]", errors)


def _unique_ids(records: dict[str, list[dict]], errors: list[str]) -> None:
    seen: dict[str, str] = {}
    for group, items in records.items():
        for record in items:
            identifier = record.get("id")
            if not identifier:
                continue
            if identifier in seen:
                errors.append(f"{group}:{identifier}: ID already used in {seen[identifier]}")
            seen[identifier] = group


def _process_cycle(edges: list[dict]) -> list[str] | None:
    graph: dict[str, list[str]] = defaultdict(list)
    nodes: set[str] = set()
    for edge in edges:
        if edge["type"] != "PROCESS_PRECEDES_PROCESS":
            continue
        if edge.get("attributes", {}).get("iterative"):
            continue
        graph[edge["from_id"]].append(edge["to_id"])
        nodes.update((edge["from_id"], edge["to_id"]))
    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(node: str, trail: list[str]) -> list[str] | None:
        if node in visiting:
            return trail[trail.index(node):] + [node]
        if node in visited:
            return None
        visiting.add(node)
        for target in graph[node]:
            cycle = visit(target, trail + [target])
            if cycle:
                return cycle
        visiting.remove(node)
        visited.add(node)
        return None

    for node in sorted(nodes):
        cycle = visit(node, [node])
        if cycle:
            return cycle
    return None


def validate(records: dict[str, list[dict]] | None = None) -> list[str]:
    records = records or load_all()
    errors: list[str] = []
    for group, items in records.items():
        schema = json.loads(SCHEMA_FILES[group].read_text(encoding="utf-8"))
        for index, record in enumerate(items, 1):
            _validate_subset(record, schema, f"{FILES[group].name}:{index}", errors)
    _unique_ids(records, errors)

    entities = {item["id"]: item for item in records["entities"]}
    edges = {item["id"]: item for item in records["edges"]}
    sources = {item["id"]: item for item in records["sources"]}
    claims = {item["id"]: item for item in records["claims"]}
    all_subjects = set(entities) | set(edges)

    for edge in edges.values():
        for field in ("from_id", "to_id"):
            if edge[field] not in entities:
                errors.append(f"{edge['id']}: {field} references missing entity {edge[field]}")
    subjects_with_claims = Counter(claim["subject_id"] for claim in claims.values()
                                   if claim["review_state"] != "rejected")
    for edge_id in edges:
        if not subjects_with_claims[edge_id]:
            errors.append(f"{edge_id}: relationship has no active supporting claim")
    for claim in claims.values():
        if claim["subject_id"] not in all_subjects:
            errors.append(f"{claim['id']}: missing subject {claim['subject_id']}")
        if claim["status"] in {"verified", "inferred", "disputed"} and not claim["evidence"]:
            errors.append(f"{claim['id']}: asserted claim has no evidence")
        if claim["status"] in {"inferred", "industry-pattern"}:
            if not claim["method"].strip() or not claim["rationale"].strip():
                errors.append(f"{claim['id']}: inference requires method and rationale")
        for evidence in claim["evidence"]:
            if evidence["source_id"] not in sources:
                errors.append(f"{claim['id']}: missing source {evidence['source_id']}")
        for other in claim.get("contradicts_claim_ids", []):
            if other not in claims:
                errors.append(f"{claim['id']}: missing contradicted claim {other}")
    for manifest in records["manifests"]:
        for source_id in manifest["source_ids"]:
            if source_id not in sources:
                errors.append(f"{manifest['id']}: missing source {source_id}")
    for resolution in records["identities"]:
        for entity_id in resolution["entity_ids"]:
            if entity_id not in entities:
                errors.append(f"{resolution['id']}: missing entity {entity_id}")
        if resolution["decision"] == "merge" and len(resolution["corroborating_identifiers"]) < 2:
            errors.append(f"{resolution['id']}: merge requires two corroborating identifiers")

    cycle = _process_cycle(list(edges.values()))
    if cycle:
        errors.append("non-iterative process cycle: " + " -> ".join(cycle))
    return errors


def require_valid(records: dict[str, list[dict]]) -> None:
    errors = validate(records)
    if errors:
        raise ValidationFailure("\n".join(errors))


def canonical_json(value) -> str:
    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":"))


def dataset_hash(records: dict[str, list[dict]]) -> str:
    digest = hashlib.sha256()
    for group in sorted(records):
        for item in sorted(records[group], key=lambda row: row["id"]):
            digest.update(group.encode())
            digest.update(canonical_json(item).encode())
            digest.update(b"\n")
    return digest.hexdigest()


def build_database(records: dict[str, list[dict]], target: Path | None = None) -> Path:
    require_valid(records)
    target = target or BUILD / "production-graph.sqlite"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.unlink(missing_ok=True)
    db = sqlite3.connect(target)
    db.executescript("""
        PRAGMA foreign_keys = ON;
        CREATE TABLE metadata(key TEXT PRIMARY KEY, value TEXT NOT NULL);
        CREATE TABLE entities(id TEXT PRIMARY KEY, type TEXT NOT NULL, name TEXT NOT NULL,
          scope_production_id TEXT, attributes_json TEXT NOT NULL);
        CREATE TABLE aliases(entity_id TEXT NOT NULL REFERENCES entities(id), alias TEXT NOT NULL,
          PRIMARY KEY(entity_id, alias));
        CREATE TABLE edges(id TEXT PRIMARY KEY, type TEXT NOT NULL,
          from_id TEXT NOT NULL REFERENCES entities(id), to_id TEXT NOT NULL REFERENCES entities(id),
          attributes_json TEXT NOT NULL);
        CREATE TABLE sources(id TEXT PRIMARY KEY, title TEXT NOT NULL, url TEXT NOT NULL,
          publisher TEXT NOT NULL, authority_tier TEXT NOT NULL, source_type TEXT NOT NULL,
          accessed_at TEXT NOT NULL, record_json TEXT NOT NULL);
        CREATE TABLE claims(id TEXT PRIMARY KEY, subject_id TEXT NOT NULL, predicate TEXT NOT NULL,
          object_json TEXT NOT NULL, status TEXT NOT NULL, confidence REAL NOT NULL,
          method TEXT NOT NULL, rationale TEXT NOT NULL, review_state TEXT NOT NULL,
          preferred_interpretation INTEGER, record_json TEXT NOT NULL);
        CREATE TABLE evidence(claim_id TEXT NOT NULL REFERENCES claims(id),
          source_id TEXT NOT NULL REFERENCES sources(id), locator TEXT NOT NULL,
          supporting_excerpt TEXT NOT NULL, PRIMARY KEY(claim_id, source_id, locator));
        CREATE TABLE identity_resolutions(id TEXT PRIMARY KEY, decision TEXT NOT NULL,
          record_json TEXT NOT NULL);
        CREATE INDEX idx_entities_type ON entities(type);
        CREATE INDEX idx_entities_name ON entities(name);
        CREATE INDEX idx_edges_type ON edges(type);
        CREATE INDEX idx_edges_from ON edges(from_id);
        CREATE INDEX idx_edges_to ON edges(to_id);
        CREATE INDEX idx_claims_subject ON claims(subject_id);
        CREATE INDEX idx_claims_status ON claims(status);
        CREATE INDEX idx_sources_tier ON sources(authority_tier);
    """)
    db.execute("INSERT INTO metadata VALUES (?, ?)", ("schema_version", "1.0.0"))
    db.execute("INSERT INTO metadata VALUES (?, ?)", ("dataset_sha256", dataset_hash(records)))
    for item in sorted(records["entities"], key=lambda row: row["id"]):
        db.execute("INSERT INTO entities VALUES (?, ?, ?, ?, ?)", (
            item["id"], item["type"], item["name"], item.get("scope_production_id"),
            canonical_json(item["attributes"])))
        for alias in sorted(item["aliases"]):
            db.execute("INSERT INTO aliases VALUES (?, ?)", (item["id"], alias))
    for item in sorted(records["edges"], key=lambda row: row["id"]):
        db.execute("INSERT INTO edges VALUES (?, ?, ?, ?, ?)", (
            item["id"], item["type"], item["from_id"], item["to_id"],
            canonical_json(item["attributes"])))
    for item in sorted(records["sources"], key=lambda row: row["id"]):
        db.execute("INSERT INTO sources VALUES (?, ?, ?, ?, ?, ?, ?, ?)", (
            item["id"], item["title"], item["url"], item["publisher"],
            item["authority_tier"], item["source_type"], item["accessed_at"],
            canonical_json(item)))
    for item in sorted(records["claims"], key=lambda row: row["id"]):
        preferred = item.get("preferred_interpretation")
        db.execute("INSERT INTO claims VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (
            item["id"], item["subject_id"], item["predicate"], canonical_json(item["object"]),
            item["status"], item["confidence"], item["method"], item["rationale"],
            item["review_state"], None if preferred is None else int(preferred),
            canonical_json(item)))
        for evidence in sorted(item["evidence"], key=lambda row: (row["source_id"], row["locator"])):
            db.execute("INSERT INTO evidence VALUES (?, ?, ?, ?)", (
                item["id"], evidence["source_id"], evidence["locator"],
                evidence["supporting_excerpt"]))
    for item in sorted(records["identities"], key=lambda row: row["id"]):
        db.execute("INSERT INTO identity_resolutions VALUES (?, ?, ?)", (
            item["id"], item["decision"], canonical_json(item)))
    db.commit()
    db.execute("VACUUM")
    db.close()
    return target


def coverage_report(records: dict[str, list[dict]]) -> dict:
    require_valid(records)
    entities = {row["id"]: row for row in records["entities"]}
    claims = [row for row in records["claims"] if row["review_state"] != "rejected"]
    by_source = Counter()
    for claim in claims:
        by_source.update(e["source_id"] for e in claim["evidence"])
    credited_people = {
        edge["from_id"] for edge in records["edges"]
        if edge["type"] == "PERSON_CREDITED_AS_ROLE"
    }
    provisional_people = {
        row["id"] for row in entities.values()
        if row["type"] == "person" and row["attributes"].get("identity_state") != "resolved"
    }
    return {
        "schema_version": "1.0.0",
        "dataset_sha256": dataset_hash(records),
        "counts": {
            "entities": len(records["entities"]),
            "edges": len(records["edges"]),
            "claims": len(claims),
            "sources": len(records["sources"]),
            "credited_people": len(credited_people),
        },
        "entities_by_type": dict(sorted(Counter(row["type"] for row in entities.values()).items())),
        "edges_by_type": dict(sorted(Counter(row["type"] for row in records["edges"]).items())),
        "claims_by_status": dict(sorted(Counter(row["status"] for row in claims).items())),
        "claims_by_review_state": dict(sorted(Counter(row["review_state"] for row in claims).items())),
        "evidence_uses_by_source": dict(sorted(by_source.items())),
        "department_coverage": {
            "production_design": {
                "state": "pilot",
                "credited_people_in_seed": len(credited_people),
                "teams_modeled": sum(1 for row in entities.values() if row["type"] == "team"),
                "processes_modeled": sum(1 for row in entities.values() if row["type"] == "process"),
                "known_true_credit_total": None,
                "complete_final_roll": False,
            }
        },
        "identity": {
            "provisional_or_unresolved_people": sorted(provisional_people),
            "unresolved_decisions": [
                row["id"] for row in records["identities"] if row["decision"] == "unresolved"
            ],
        },
        "limitations": [
            "Coverage denominator is the discovered public seed, not the final on-screen roll.",
            "Industry-pattern processes are hypotheses, not verified production events.",
        ],
    }


def duplicate_report(records: dict[str, list[dict]]) -> dict:
    entities = records["entities"]
    buckets: dict[str, list[str]] = defaultdict(list)
    for item in entities:
        terms = [item["name"], *item["aliases"]]
        for term in terms:
            normalized = re.sub(r"[^a-z0-9]+", "", term.casefold())
            if normalized:
                buckets[normalized].append(item["id"])
    candidates = {
        key: sorted(set(ids)) for key, ids in buckets.items() if len(set(ids)) > 1
    }
    return {
        "dataset_sha256": dataset_hash(records),
        "candidate_groups": dict(sorted(candidates.items())),
        "unresolved_identity_records": [
            row for row in records["identities"] if row["decision"] == "unresolved"
        ],
    }


def export_graph(records: dict[str, list[dict]]) -> list[Path]:
    require_valid(records)
    EXPORTS.mkdir(parents=True, exist_ok=True)
    entities = sorted(records["entities"], key=lambda row: row["id"])
    edges = sorted(records["edges"], key=lambda row: row["id"])
    claims_by_subject: dict[str, list[dict]] = defaultdict(list)
    for claim in records["claims"]:
        if claim["review_state"] != "rejected":
            claims_by_subject[claim["subject_id"]].append(claim)

    complete = {
        "schema_version": "1.0.0",
        "dataset_sha256": dataset_hash(records),
        **{key: sorted(value, key=lambda row: row["id"]) for key, value in records.items()},
    }
    complete_path = EXPORTS / "graph-complete.json"
    complete_path.write_text(json.dumps(complete, indent=2, ensure_ascii=False) + "\n",
                             encoding="utf-8")

    cyto = {
        "data": {"schema_version": "1.0.0", "dataset_sha256": dataset_hash(records)},
        "elements": {
            "nodes": [{"data": {**item, "claims": claims_by_subject[item["id"]]}}
                      for item in entities],
            "edges": [{"data": {**item, "source": item["from_id"], "target": item["to_id"],
                                "claims": claims_by_subject[item["id"]]}}
                      for item in edges],
        },
    }
    cyto_path = EXPORTS / "graph-cytoscape.json"
    cyto_path.write_text(json.dumps(cyto, indent=2, ensure_ascii=False) + "\n",
                         encoding="utf-8")

    nodes_path = EXPORTS / "nodes.csv"
    with nodes_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=[
            "id", "type", "name", "aliases", "scope_production_id", "attributes_json"])
        writer.writeheader()
        for item in entities:
            writer.writerow({
                "id": item["id"], "type": item["type"], "name": item["name"],
                "aliases": "|".join(item["aliases"]),
                "scope_production_id": item.get("scope_production_id") or "",
                "attributes_json": canonical_json(item["attributes"]),
            })
    edges_path = EXPORTS / "edges.csv"
    with edges_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=[
            "id", "type", "from_id", "to_id", "attributes_json",
            "claim_statuses", "max_confidence"])
        writer.writeheader()
        for item in edges:
            edge_claims = claims_by_subject[item["id"]]
            writer.writerow({
                "id": item["id"], "type": item["type"], "from_id": item["from_id"],
                "to_id": item["to_id"], "attributes_json": canonical_json(item["attributes"]),
                "claim_statuses": "|".join(sorted({row["status"] for row in edge_claims})),
                "max_confidence": max((row["confidence"] for row in edge_claims), default=""),
            })

    graphml_path = EXPORTS / "graph.graphml"
    node_xml = "\n".join(
        f'    <node id="{escape(item["id"])}"><data key="type">{escape(item["type"])}</data>'
        f'<data key="name">{escape(item["name"])}</data></node>' for item in entities)
    edge_xml = "\n".join(
        f'    <edge id="{escape(item["id"])}" source="{escape(item["from_id"])}" '
        f'target="{escape(item["to_id"])}"><data key="edge_type">{escape(item["type"])}</data>'
        f'</edge>' for item in edges)
    graphml_path.write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<graphml xmlns="http://graphml.graphdrawing.org/xmlns">\n'
        '  <key id="type" for="node" attr.name="type" attr.type="string"/>\n'
        '  <key id="name" for="node" attr.name="name" attr.type="string"/>\n'
        '  <key id="edge_type" for="edge" attr.name="type" attr.type="string"/>\n'
        '  <graph id="spider-man-production-graph" edgedefault="directed">\n'
        f"{node_xml}\n{edge_xml}\n  </graph>\n</graphml>\n", encoding="utf-8")
    return [complete_path, cyto_path, nodes_path, edges_path, graphml_path]


def write_report(value: dict, target: Path) -> Path:
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return target


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["validate", "build", "report", "duplicates", "export", "all"])
    args = parser.parse_args(argv)
    try:
        records = load_all()
        if args.command in {"validate", "all"}:
            errors = validate(records)
            if errors:
                raise ValidationFailure("\n".join(errors))
            print(f"valid: {sum(map(len, records.values()))} records; sha256={dataset_hash(records)}")
        if args.command in {"build", "all"}:
            print(f"built: {build_database(records)}")
        if args.command in {"report", "all"}:
            print(f"reported: {write_report(coverage_report(records), BUILD / 'coverage.json')}")
        if args.command in {"duplicates", "all"}:
            print(f"duplicates: {write_report(duplicate_report(records), BUILD / 'duplicates.json')}")
        if args.command in {"export", "all"}:
            for path in export_graph(records):
                print(f"exported: {path}")
        return 0
    except (OSError, ValidationFailure, sqlite3.Error) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

