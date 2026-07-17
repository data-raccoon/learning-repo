"""Dependency-free validation for Evidence Sprint 001."""

from __future__ import annotations

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parent
SCAN_ROOT = ROOT.parent.parent / "opportunity-scans" / "scan-001"
SHORTLIST_STATES = {"evidence_continue", "evidence_hold"}
DISPOSITIONS = {"continue", "hold", "stop"}
CONFIDENCE = {"low", "medium", "high"}
REQUIRED = {
    "opportunity_id",
    "disposition",
    "confidence",
    "test_question",
    "source_ids",
    "supporting_evidence",
    "counterevidence",
    "result",
    "next_action",
    "stop_condition",
    "approval_gate",
}


def fail(message: str) -> None:
    raise SystemExit(f"Evidence Sprint validation failed: {message}")


def main() -> None:
    decisions = json.loads((ROOT / "decisions.json").read_text(encoding="utf-8"))
    opportunities = json.loads((SCAN_ROOT / "opportunities.json").read_text(encoding="utf-8"))
    source_text = (ROOT / "sources.md").read_text(encoding="utf-8")
    result_text = (ROOT / "sprint-results.md").read_text(encoding="utf-8")
    sources = set(re.findall(r"`(ES1-S\d{2})`", source_text))
    opportunity_by_id = {item["id"]: item for item in opportunities}

    if len(decisions) != 8:
        fail(f"expected exactly 8 decisions, found {len(decisions)}")

    seen: set[str] = set()
    counts = {item: 0 for item in DISPOSITIONS}
    for decision in decisions:
        missing = REQUIRED - set(decision)
        if missing:
            fail(f"decision is missing {sorted(missing)}")
        opportunity_id = decision["opportunity_id"]
        if opportunity_id in seen:
            fail(f"duplicate decision for {opportunity_id}")
        seen.add(opportunity_id)
        if opportunity_id not in opportunity_by_id:
            fail(f"unknown opportunity {opportunity_id}")
        if opportunity_by_id[opportunity_id]["status"] not in SHORTLIST_STATES:
            fail(f"{opportunity_id} was not advanced to an evidence state")
        disposition = decision["disposition"]
        if disposition not in DISPOSITIONS:
            fail(f"invalid disposition for {opportunity_id}")
        counts[disposition] += 1
        expected_state = f"evidence_{disposition}"
        if opportunity_by_id[opportunity_id]["status"] != expected_state:
            fail(f"lifecycle mismatch for {opportunity_id}")
        if decision["confidence"] not in CONFIDENCE:
            fail(f"invalid confidence for {opportunity_id}")
        refs = decision["source_ids"]
        if not isinstance(refs, list) or len(set(refs)) < 2:
            fail(f"{opportunity_id} must reference at least two sprint sources")
        unknown = set(refs) - sources
        if unknown:
            fail(f"{opportunity_id} references unknown sources {sorted(unknown)}")
        if opportunity_id.replace("POC-001-", "") not in result_text:
            fail(f"human-readable results omit {opportunity_id}")
        for field in REQUIRED - {"source_ids"}:
            if not isinstance(decision[field], str) or not decision[field].strip():
                fail(f"{opportunity_id} has empty {field}")

    if counts != {"continue": 7, "hold": 1, "stop": 0}:
        fail(f"unexpected disposition counts {counts}")

    print(
        f"Evidence Sprint validation passed: {len(decisions)} decisions, "
        f"{counts['continue']} continue, {counts['hold']} hold, {counts['stop']} stop, "
        f"and {len(sources)} source objects."
    )


if __name__ == "__main__":
    main()

