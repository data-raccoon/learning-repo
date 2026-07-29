from __future__ import annotations

import copy
import importlib.util
import json
import sqlite3
import tempfile
import unittest
from contextlib import closing
from pathlib import Path

MODULE_PATH = Path(__file__).resolve().parents[1] / "tools" / "graph_tool.py"
SPEC = importlib.util.spec_from_file_location("graph_tool", MODULE_PATH)
graph_tool = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
SPEC.loader.exec_module(graph_tool)


class GraphToolTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.records = graph_tool.load_all()

    def test_seed_dataset_is_valid(self):
        self.assertEqual([], graph_tool.validate(self.records))

    def test_fixture_covers_source_families(self):
        path = Path(__file__).parent / "fixtures" / "source-records.json"
        records = json.loads(path.read_text(encoding="utf-8"))
        self.assertEqual(
            {"official", "vendor", "interview", "credit_database"},
            {record["kind"] for record in records},
        )

    def test_orphaned_edge_is_rejected(self):
        records = copy.deepcopy(self.records)
        records["edges"][0]["from_id"] = "person-missing"
        errors = graph_tool.validate(records)
        self.assertTrue(any("missing entity" in error for error in errors))

    def test_unsupported_edge_is_rejected(self):
        records = copy.deepcopy(self.records)
        edge_id = records["edges"][0]["id"]
        records["claims"] = [
            claim for claim in records["claims"] if claim["subject_id"] != edge_id
        ]
        errors = graph_tool.validate(records)
        self.assertTrue(any("no active supporting claim" in error for error in errors))

    def test_inference_requires_method_and_rationale(self):
        records = copy.deepcopy(self.records)
        claim = next(row for row in records["claims"] if row["status"] == "inferred")
        claim["method"] = ""
        claim["rationale"] = ""
        errors = graph_tool.validate(records)
        self.assertTrue(any("requires method and rationale" in error for error in errors))

    def test_non_iterative_process_cycle_is_rejected(self):
        records = copy.deepcopy(self.records)
        template = copy.deepcopy(
            next(row for row in records["edges"] if row["type"] == "PROCESS_PRECEDES_PROCESS")
        )
        template.update({
            "id": "edge-test-cycle",
            "from_id": "process-asset-handover",
            "to_id": "process-script-breakdown",
        })
        records["edges"].append(template)
        claim = copy.deepcopy(records["claims"][0])
        claim.update({
            "id": "claim-test-cycle",
            "subject_id": "edge-test-cycle",
            "status": "industry-pattern",
            "method": "test",
            "rationale": "test cycle",
        })
        records["claims"].append(claim)
        errors = graph_tool.validate(records)
        self.assertTrue(any("process cycle" in error for error in errors))

    def test_explicit_iterative_process_edge_may_cycle(self):
        records = copy.deepcopy(self.records)
        template = copy.deepcopy(
            next(row for row in records["edges"] if row["type"] == "PROCESS_PRECEDES_PROCESS")
        )
        template.update({
            "id": "edge-test-iterative-cycle",
            "from_id": "process-asset-handover",
            "to_id": "process-script-breakdown",
            "attributes": {"iterative": True},
        })
        records["edges"].append(template)
        claim = copy.deepcopy(records["claims"][0])
        claim.update({
            "id": "claim-test-iterative-cycle",
            "subject_id": "edge-test-iterative-cycle",
            "status": "industry-pattern",
            "method": "test",
            "rationale": "explicit iterative feedback",
        })
        records["claims"].append(claim)
        self.assertEqual([], graph_tool.validate(records))

    def test_person_merge_requires_two_identifiers(self):
        records = copy.deepcopy(self.records)
        resolution = records["identities"][0]
        resolution["decision"] = "merge"
        resolution["corroborating_identifiers"] = ["one identifier"]
        errors = graph_tool.validate(records)
        self.assertTrue(any("two corroborating identifiers" in error for error in errors))

    def test_ambiguous_name_appears_in_identity_report(self):
        report = graph_tool.coverage_report(self.records)
        self.assertIn(
            "person-peter-buckley",
            report["identity"]["provisional_or_unresolved_people"],
        )
        self.assertIn(
            "identity-peter-buckley-unresolved",
            report["identity"]["unresolved_decisions"],
        )

    def test_multiple_roles_are_supported(self):
        person_edges = [
            row for row in self.records["edges"]
            if row["type"] == "PERSON_CREDITED_AS_ROLE"
        ]
        by_person = {}
        for edge in person_edges:
            by_person.setdefault(edge["from_id"], []).append(edge["to_id"])
        self.assertTrue(all(by_person.values()))
        self.assertEqual(len(person_edges), sum(len(value) for value in by_person.values()))

    def test_disputed_claim_shape_is_accepted(self):
        records = copy.deepcopy(self.records)
        claim = copy.deepcopy(records["claims"][0])
        claim.update({
            "id": "claim-test-disputed",
            "status": "disputed",
            "preferred_interpretation": False,
            "contradicts_claim_ids": [records["claims"][0]["id"]],
        })
        records["claims"].append(claim)
        self.assertEqual([], graph_tool.validate(records))

    def test_inaccessible_source_can_be_registered(self):
        records = copy.deepcopy(self.records)
        source = copy.deepcopy(records["sources"][0])
        source.update({
            "id": "source-test-inaccessible",
            "url": "https://example.invalid/record",
            "access_status": "inaccessible",
        })
        records["sources"].append(source)
        self.assertEqual([], graph_tool.validate(records))

    def test_vendor_subteam_can_be_modeled(self):
        records = copy.deepcopy(self.records)
        company = {
            "schema_version": "1.0.0", "id": "company-test-vendor", "type": "company",
            "name": "Test Vendor", "aliases": [], "attributes": {}, "scope_production_id": None,
        }
        team = {
            "schema_version": "1.0.0", "id": "team-test-vendor-subteam", "type": "team",
            "name": "Test Vendor Scenic Unit", "aliases": [], "attributes": {"vendor_team": True},
            "scope_production_id": "production-sm-bnd-2026",
        }
        records["entities"].extend([company, team])
        self.assertEqual([], graph_tool.validate(records))

    def test_sqlite_build_contains_queryable_evidence(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "graph.sqlite"
            graph_tool.build_database(self.records, target)
            with closing(sqlite3.connect(target)) as db:
                self.assertEqual(len(self.records["entities"]),
                                 db.execute("SELECT COUNT(*) FROM entities").fetchone()[0])
                self.assertGreater(
                    db.execute("SELECT COUNT(*) FROM evidence").fetchone()[0], 0)
                self.assertEqual(
                    graph_tool.dataset_hash(self.records),
                    db.execute("SELECT value FROM metadata WHERE key='dataset_sha256'").fetchone()[0],
                )

    def test_hash_is_independent_of_record_order(self):
        shuffled = copy.deepcopy(self.records)
        for values in shuffled.values():
            values.reverse()
        self.assertEqual(
            graph_tool.dataset_hash(self.records),
            graph_tool.dataset_hash(shuffled),
        )


if __name__ == "__main__":
    unittest.main()
