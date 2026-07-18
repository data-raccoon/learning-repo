"""Dependency-free validation for Opportunity Scan 001."""

from __future__ import annotations

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parent
ID_PATTERN = re.compile(r"^POC-001-OPP-\d{3}$")
LEVELS = {"low", "medium", "high"}
STATUSES = {
    "untriaged",
    "shortlist_candidate",
    "evidence_continue",
    "evidence_hold",
    "evidence_stop",
}
REQUIRED = {
    "id",
    "title",
    "domain",
    "status",
    "signal",
    "source_ids",
    "join_logic",
    "hypothesis",
    "levers",
    "efficiency_effect",
    "effectiveness_effect",
    "evidence_maturity",
    "decision_proximity",
    "controllability",
    "test_cost",
    "risk_level",
    "caveat",
    "next_test",
    "approval_flags",
    "related_case",
}


def fail(message: str) -> None:
    raise SystemExit(f"Opportunity Scan validation failed: {message}")


def main() -> None:
    records = json.loads((ROOT / "opportunities.json").read_text(encoding="utf-8"))
    source_text = (ROOT / "sources.md").read_text(encoding="utf-8")
    source_ids = set(re.findall(r"`(OS1-S\d{2})`", source_text))

    if not isinstance(records, list) or not 10 <= len(records) <= 30:
        fail(f"expected 10 to 30 records, found {len(records) if isinstance(records, list) else 'non-list'}")

    ids: set[str] = set()
    advanced_count = 0
    for index, record in enumerate(records, start=1):
        missing = REQUIRED - set(record)
        if missing:
            fail(f"record {index} is missing {sorted(missing)}")
        if not ID_PATTERN.fullmatch(record["id"]):
            fail(f"invalid opportunity ID {record['id']!r}")
        if record["id"] in ids:
            fail(f"duplicate opportunity ID {record['id']}")
        ids.add(record["id"])
        if record["status"] not in STATUSES:
            fail(f"{record['id']} has invalid status")
        advanced_count += record["status"] in {
            "shortlist_candidate",
            "evidence_continue",
            "evidence_hold",
            "evidence_stop",
        }
        for field in ("evidence_maturity", "decision_proximity", "controllability", "test_cost", "risk_level"):
            if record[field] not in LEVELS:
                fail(f"{record['id']} has invalid {field}")
        refs = record["source_ids"]
        if not isinstance(refs, list) or len(set(refs)) < 2:
            fail(f"{record['id']} must join at least two sources")
        unknown = set(refs) - source_ids
        if unknown:
            fail(f"{record['id']} references unknown sources {sorted(unknown)}")
        if not isinstance(record["levers"], list) or not record["levers"]:
            fail(f"{record['id']} has no levers")
        if not isinstance(record["approval_flags"], list):
            fail(f"{record['id']} approval_flags must be a list")
        for field in ("title", "signal", "join_logic", "hypothesis", "caveat", "next_test"):
            if not isinstance(record[field], str) or not record[field].strip():
                fail(f"{record['id']} has an empty {field}")

    if advanced_count != 8:
        fail(f"expected exactly 8 shortlisted or evidence-tested candidates, found {advanced_count}")

    print(
        f"Opportunity Scan validation passed: {len(records)} unique opportunities, "
        f"{len(source_ids)} sources, exactly {advanced_count} advanced candidates, "
        "and at least two sources per opportunity."
    )


if __name__ == "__main__":
    main()
