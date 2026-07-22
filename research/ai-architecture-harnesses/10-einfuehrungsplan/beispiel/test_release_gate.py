import copy
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

from demo import build_manifest
from release_gate import Decision, ReleaseGate, sha256_file


class ReleaseGateTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.now = datetime(2026, 7, 22, 12, tzinfo=timezone.utc)
        self.manifest = build_manifest(self.root)
        stamp = self.now.isoformat()
        self.manifest["created_at"] = stamp
        for item in self.manifest["evidence"]:
            item["collected_at"] = stamp
        for item in self.manifest["metrics"]:
            item["measured_at"] = stamp
        self.gate = ReleaseGate(self.now)

    def tearDown(self):
        self.temp.cleanup()

    def evaluate(self, manifest=None):
        return self.gate.evaluate(manifest or self.manifest, self.root)

    def codes(self, result):
        return {finding.code for finding in result.findings}

    def test_pre_canary_pass_produces_plan_only(self):
        result = self.evaluate()
        self.assertEqual(Decision.CANARY, result.decision)
        self.assertIn("5% traffic", result.next_actions[0])

    def test_completed_canary_promotes(self):
        self.manifest["rollout"].update(phase="canary", observed_hours=12, samples=500)
        self.assertEqual(Decision.PROMOTE, self.evaluate().decision)

    def test_missing_required_evidence_fails_closed(self):
        self.manifest["evidence"] = [item for item in self.manifest["evidence"] if item["id"] != "contract_tests"]
        result = self.evaluate()
        self.assertEqual(Decision.HOLD, result.decision)
        self.assertIn("evidence_required", self.codes(result))

    def test_tampered_evidence_fails_hash_check(self):
        item = self.manifest["evidence"][0]
        (self.root / item["path"]).write_text("tampered", encoding="utf-8")
        result = self.evaluate()
        self.assertEqual(Decision.HOLD, result.decision)
        self.assertIn("evidence_hash_mismatch", self.codes(result))

    def test_expired_evidence_fails_closed(self):
        self.manifest["evidence"][0]["collected_at"] = (self.now - timedelta(hours=25)).isoformat()
        result = self.evaluate()
        self.assertEqual(Decision.HOLD, result.decision)
        self.assertIn("evidence_expired", self.codes(result))

    def test_metric_regression_holds(self):
        metric = next(item for item in self.manifest["metrics"] if item["id"] == "error_rate")
        metric["value"] = 0.03
        result = self.evaluate()
        self.assertEqual(Decision.HOLD, result.decision)
        self.assertIn("metric_above_threshold", self.codes(result))

    def test_active_stop_overrides_other_failures_and_rolls_back(self):
        self.manifest["stop_signals"]["unauthorized_side_effect"] = True
        self.manifest["evidence"] = []
        result = self.evaluate()
        self.assertEqual(Decision.ROLLBACK, result.decision)
        self.assertEqual(0, result.rollback_stage)

    def test_unknown_stop_state_fails_closed(self):
        del self.manifest["stop_signals"]["audit_correlation_missing"]
        result = self.evaluate()
        self.assertEqual(Decision.HOLD, result.decision)
        self.assertIn("stop_signal_unknown", self.codes(result))

    def test_short_canary_cannot_promote(self):
        self.manifest["rollout"].update(phase="canary", observed_hours=2, samples=500)
        result = self.evaluate()
        self.assertEqual(Decision.HOLD, result.decision)
        self.assertIn("canary_too_short", self.codes(result))

    def test_stage_jump_is_forbidden(self):
        self.manifest["target_stage"] = 2
        result = self.evaluate()
        self.assertEqual(Decision.HOLD, result.decision)
        self.assertIn("stage_jump_forbidden", self.codes(result))

    def test_evidence_path_cannot_escape_manifest_directory(self):
        item = self.manifest["evidence"][0]
        outside = self.root.parent / "outside-evidence.txt"
        outside.write_text("outside", encoding="utf-8")
        self.addCleanup(lambda: outside.unlink(missing_ok=True))
        item.update(path="../outside-evidence.txt", sha256=sha256_file(outside))
        result = self.evaluate()
        self.assertEqual(Decision.HOLD, result.decision)
        self.assertIn("evidence_path_escape", self.codes(result))


if __name__ == "__main__":
    unittest.main()
