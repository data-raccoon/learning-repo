import pathlib
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from model_checker import check
from runtime_monitor import PolicyViolation, RuntimeMonitor
from workflow_model import Event, ModelOptions, Status


class ModelCheckerTests(unittest.TestCase):
    def test_valid_model_is_complete_safe_and_deadlock_free(self):
        result = check(max_depth=8)
        self.assertTrue(result.complete)
        self.assertTrue(result.safety_holds_within_bound)
        self.assertIsNone(result.counterexample)
        self.assertEqual((), result.deadlocks)

    def test_safety_violation_returns_shortest_counterexample(self):
        result = check(options=ModelOptions(unsafe_direct_commit=True), max_depth=8)
        self.assertIsNotNone(result.counterexample)
        assert result.counterexample is not None
        self.assertIn("commit_without_authorization", result.counterexample.violations)
        self.assertEqual([Event.COMMIT], [step.event for step in result.counterexample.trace])

    def test_deadlock_is_reported_as_liveness_warning(self):
        result = check(options=ModelOptions(approval_service_available=False), max_depth=8)
        self.assertTrue(result.complete)
        self.assertTrue(result.safety_holds_within_bound)
        self.assertEqual(1, len(result.deadlocks))
        self.assertEqual(Status.AWAITING_APPROVAL, result.deadlocks[0][-1].state.status)

    def test_insufficient_depth_is_explicitly_incomplete(self):
        result = check(max_depth=1)
        self.assertFalse(result.complete)
        self.assertTrue(result.safety_holds_within_bound)


class RuntimeMonitorTests(unittest.TestCase):
    def test_monitor_accepts_valid_high_risk_trace(self):
        monitor = RuntimeMonitor()
        for event in (
            Event.VALIDATE,
            Event.AUTHORIZE,
            Event.REQUEST_APPROVAL,
            Event.APPROVE,
            Event.COMMIT,
        ):
            monitor.observe(event)
        self.assertEqual(Status.COMMITTED, monitor.state.status)

    def test_monitor_rejects_direct_commit_even_if_model_option_exposes_it(self):
        monitor = RuntimeMonitor(options=ModelOptions(unsafe_direct_commit=True))
        with self.assertRaises(PolicyViolation):
            monitor.observe(Event.COMMIT)
        self.assertEqual(Status.DRAFT, monitor.state.status)
        self.assertEqual([], monitor.audit_log)


if __name__ == "__main__":
    unittest.main()
