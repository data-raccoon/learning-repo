import sys
import unittest
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from harness import (  # noqa: E402
    AtomicBudget,
    BudgetExceeded,
    DeterministicRouter,
    EvalCase,
    FakeModel,
    Handoff,
    InvalidHandoff,
    InvalidPlan,
    Orchestrator,
    ResolutionStatus,
    RouteRule,
    TaskKind,
    Vote,
    WorkItem,
    compare_baseline_and_ensemble,
    resolve_votes,
)


class BudgetTests(unittest.TestCase):
    def test_reservation_rejects_overspend(self):
        budget = AtomicBudget(1, 10)
        held = budget.reserve(1, 10)
        with self.assertRaises(BudgetExceeded):
            budget.reserve(1, 1)
        budget.settle(held, 7)
        snap = budget.snapshot()
        self.assertEqual((snap.spent_calls, snap.spent_tokens), (1, 7))

    def test_parallel_reservations_are_atomic(self):
        budget = AtomicBudget(1, 10)

        def attempt():
            try:
                return budget.reserve(1, 10)
            except BudgetExceeded:
                return None

        with ThreadPoolExecutor(max_workers=8) as pool:
            reservations = list(pool.map(lambda _: attempt(), range(8)))
        self.assertEqual(sum(item is not None for item in reservations), 1)


class HandoffAndPlanTests(unittest.TestCase):
    def test_invalid_handoff_is_rejected(self):
        handoff = Handoff(
            "2.0", "run", "task", "run", "orchestrator", "worker",
            "WORK", TaskKind.ANALYZE, frozenset({"a"}), "prompt",
        )
        with self.assertRaises(InvalidHandoff):
            handoff.validate(frozenset({("orchestrator", "worker")}))

    def test_overlapping_worker_scopes_are_rejected(self):
        items = [
            WorkItem("a", "worker", TaskKind.ANALYZE, frozenset({"shared"}), "a"),
            WorkItem("b", "worker", TaskKind.ANALYZE, frozenset({"shared"}), "b"),
        ]
        with self.assertRaises(InvalidPlan):
            Orchestrator.validate_disjoint(items)

    def test_router_and_workers_are_deterministic(self):
        model = FakeModel("model-a", "domain-a", {"a": "A", "b": "B"})
        router = DeterministicRouter([RouteRule(TaskKind.ANALYZE, "worker", "model-a")])
        harness = Orchestrator(
            router, {"model-a": model}, AtomicBudget(2, 40),
            frozenset({("orchestrator", "worker")}),
        )
        outputs = harness.run("run", [
            WorkItem("a", "worker", TaskKind.ANALYZE, frozenset({"a"}), "a", 20),
            WorkItem("b", "worker", TaskKind.ANALYZE, frozenset({"b"}), "b", 20),
        ])
        self.assertEqual([output.result.answer for output in outputs], ["A", "B"])

    def test_complete_fanout_is_rejected_before_any_model_call(self):
        calls = []

        class CountingModel(FakeModel):
            def invoke(self, handoff, max_tokens):
                calls.append(handoff.task_id)
                return super().invoke(handoff, max_tokens)

        model = CountingModel("model-a", "domain-a", {"a": "A", "b": "B"})
        harness = Orchestrator(
            DeterministicRouter([RouteRule(TaskKind.ANALYZE, "worker", "model-a")]),
            {"model-a": model}, AtomicBudget(1, 20),
            frozenset({("orchestrator", "worker")}),
        )
        items = [
            WorkItem("a", "worker", TaskKind.ANALYZE, frozenset({"a"}), "a", 10),
            WorkItem("b", "worker", TaskKind.ANALYZE, frozenset({"b"}), "b", 10),
        ]
        with self.assertRaises(BudgetExceeded):
            harness.run("run", items)
        self.assertEqual(calls, [])
        snapshot = harness.budget.snapshot()
        self.assertEqual((snapshot.reserved_calls, snapshot.spent_calls), (0, 0))


class VotingTests(unittest.TestCase):
    def test_correlated_wrong_votes_do_not_create_quorum(self):
        votes = [
            Vote("wrong", "a1", "same-family"),
            Vote("wrong", "a2", "same-family"),
            Vote("wrong", "a3", "same-family"),
            Vote("right", "b", "independent-family"),
        ]
        resolution = resolve_votes(votes, quorum=2)
        self.assertEqual(resolution.status, ResolutionStatus.UNRESOLVED)
        self.assertIsNone(resolution.answer)

    def test_false_independent_consensus_is_not_truth(self):
        votes = [Vote("wrong", "a", "a"), Vote("wrong", "b", "b")]
        unverified = resolve_votes(votes, quorum=2)
        rejected = resolve_votes(votes, quorum=2, verifier=lambda answer: answer == "right")
        self.assertEqual(unverified.status, ResolutionStatus.CONSENSUS_UNVERIFIED)
        self.assertEqual(rejected.status, ResolutionStatus.REJECTED)

    def test_deterministically_verified_quorum(self):
        votes = [Vote("4", "a", "a"), Vote("4", "b", "b"), Vote("5", "c", "c")]
        resolution = resolve_votes(votes, quorum=2, verifier=lambda answer: answer == "4")
        self.assertEqual(resolution.status, ResolutionStatus.VERIFIED)
        self.assertEqual(resolution.answer, "4")


class EvaluationTests(unittest.TestCase):
    def test_baseline_vs_ensemble_reports_quality_and_cost(self):
        cases = [EvalCase("q1", "one", "yes"), EvalCase("q2", "two", "yes")]
        baseline = FakeModel("base", "base", {"q1": "yes", "q2": "no"}, tokens_per_call=2)
        ensemble = [
            FakeModel("a", "a", {"q1": "yes", "q2": "yes"}, tokens_per_call=3),
            FakeModel("b", "b", {"q1": "yes", "q2": "yes"}, tokens_per_call=3),
        ]
        base, multi = compare_baseline_and_ensemble(cases, baseline, ensemble)
        self.assertEqual((base.accuracy, base.calls, base.tokens), (0.5, 2, 4))
        self.assertEqual((multi.accuracy, multi.calls, multi.tokens), (1.0, 4, 12))


if __name__ == "__main__":
    unittest.main()
