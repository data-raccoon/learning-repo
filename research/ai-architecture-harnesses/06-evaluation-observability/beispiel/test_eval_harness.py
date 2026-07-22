import json
import tempfile
import unittest
from pathlib import Path

from eval_harness import (FakeAgent, Summary, TraceRecorder, canary_slo_decision,
                          load_suite, redact, regression_gate, run_evaluation,
                          summarize)


HERE = Path(__file__).parent


class HarnessTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.suite = load_suite(HERE / "cases.v1.json")

    def test_deterministic_scores_for_same_version_seed_and_cases(self):
        agent = FakeAgent("stable", error_rate=0.37)
        first = run_evaluation(self.suite, agent, 20, seed=7)
        second = run_evaluation(self.suite, agent, 20, seed=7)
        projection = lambda rows: [(r.case_id, r.trial, r.status, r.passed, r.output) for r in rows]
        self.assertEqual(projection(first), projection(second))
        self.assertEqual(summarize(self.suite, agent, first, 20).pass_rate,
                         summarize(self.suite, agent, second, 20).pass_rate)

    def test_regression_is_blocked(self):
        baseline = Summary("1", "base", 100, 100, 98, 0, .98, .93, .995)
        candidate = Summary("1", "new", 100, 100, 80, 0, .80, .71, .87)
        result = regression_gate(baseline, candidate, max_regression=.02)
        self.assertEqual("block", result["decision"])
        self.assertIn("point_estimate_regression", result["reasons"])

    def test_incomplete_sample_is_not_dropped_and_blocks(self):
        agent = FakeAgent("timeouts", incomplete_rate=1.0)
        summary = summarize(self.suite, agent, run_evaluation(self.suite, agent, 3), 3)
        baseline = Summary("1", "base", 12, 12, 12, 0, 1.0, .75, 1.0)
        self.assertEqual(12, summary.planned)
        self.assertEqual(0, summary.completed)
        self.assertEqual(0.0, summary.pass_rate)
        self.assertIn("incomplete_sample", regression_gate(baseline, summary)["reasons"])

    def test_redaction_happens_before_trace_export(self):
        recorder = TraceRecorder("redaction-test")
        recorder.emit("tool.call", {
            "authorization": "Bearer raw-token",
            "nested": {"email": "alice@example.org", "message": "API_KEY=top-secret"},
        })
        serialized_memory = json.dumps(recorder.events)
        self.assertNotIn("raw-token", serialized_memory)
        self.assertNotIn("alice@example.org", serialized_memory)
        self.assertNotIn("top-secret", serialized_memory)
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "trace.jsonl"
            recorder.write_jsonl(target)
            exported = target.read_text(encoding="utf-8")
            self.assertNotIn("raw-token", exported)
            self.assertIn("[REDACTED]", exported)

    def test_redact_preserves_non_sensitive_structure(self):
        self.assertEqual({"route": "billing", "count": 2}, redact({"route": "billing", "count": 2}))

    def test_canary_critical_violation_rolls_back_immediately(self):
        result = canary_slo_decision(requests=1, successful=1, critical_violations=1,
                                     incomplete_traces=0, min_requests=20)
        self.assertEqual({"decision": "rollback", "reason": "critical_violation"}, result)


if __name__ == "__main__":
    unittest.main()
