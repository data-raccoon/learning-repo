import unittest

from workflow import (
    Budget,
    BudgetExceeded,
    GateRejected,
    Proposal,
    Request,
    State,
    ValidationFailed,
    WorkflowKernel,
)


class WorkflowKernelTests(unittest.TestCase):
    def make_kernel(self, **overrides):
        calls = overrides.pop("calls", {"model": 0, "commit": 0})

        def model(request):
            calls["model"] += 1
            return Proposal("candidate", ("safe",))

        def commit(request, proposal):
            calls["commit"] += 1
            return "receipt-1"

        arguments = dict(
            request=Request("r-1", "create draft"),
            budget=Budget(max_steps=4, max_cost_units=5),
            probabilistic_step=model,
            request_validator=lambda request: bool(request.text),
            commit_gate=lambda request, proposal: "safe" in proposal.labels,
            commit_adapter=commit,
            probabilistic_step_cost=5,
        )
        arguments.update(overrides)
        return WorkflowKernel(**arguments), calls

    def test_happy_path_commits_only_after_gate(self):
        observations = []

        def gate(_request, proposal):
            observations.append(("gate", proposal.digest))
            return True

        def commit(_request, proposal):
            observations.append(("commit", proposal.digest))
            return "receipt"

        kernel, _ = self.make_kernel(commit_gate=gate, commit_adapter=commit)
        self.assertEqual(kernel.run(), State.COMMITTED)
        self.assertEqual([item[0] for item in observations], ["gate", "commit"])
        self.assertEqual(kernel.step_count, 4)
        self.assertEqual(kernel.cost_units, 5)
        self.assertEqual(kernel.commit_receipt, "receipt")
        self.assertEqual(
            [event.sequence for event in kernel.audit_events],
            list(range(1, len(kernel.audit_events) + 1)),
        )

    def test_invalid_request_never_calls_model_or_commit(self):
        calls = {"model": 0, "commit": 0}
        kernel, calls = self.make_kernel(
            calls=calls, request_validator=lambda _request: False
        )
        with self.assertRaises(ValidationFailed):
            kernel.run()
        self.assertEqual(kernel.state, State.REJECTED)
        self.assertEqual(calls, {"model": 0, "commit": 0})

    def test_cost_is_reserved_before_probabilistic_dispatch(self):
        calls = {"model": 0, "commit": 0}
        kernel, calls = self.make_kernel(
            calls=calls, budget=Budget(max_steps=4, max_cost_units=4)
        )
        with self.assertRaises(BudgetExceeded):
            kernel.run()
        self.assertEqual(kernel.state, State.FAILED)
        self.assertEqual(calls["model"], 0)
        self.assertEqual(kernel.cost_units, 0)
        denial = [e for e in kernel.audit_events if e.event == "budget_denied"]
        self.assertEqual(denial[0].details_dict()["reason"], "cost_budget")

    def test_step_budget_stops_before_commit(self):
        calls = {"model": 0, "commit": 0}
        kernel, calls = self.make_kernel(
            calls=calls, budget=Budget(max_steps=3, max_cost_units=5)
        )
        with self.assertRaises(BudgetExceeded):
            kernel.run()
        self.assertEqual(kernel.state, State.FAILED)
        self.assertEqual(calls["model"], 1)
        self.assertEqual(calls["commit"], 0)

    def test_gate_rejection_is_fail_closed(self):
        calls = {"model": 0, "commit": 0}
        kernel, calls = self.make_kernel(
            calls=calls, commit_gate=lambda _request, _proposal: False
        )
        with self.assertRaises(GateRejected):
            kernel.run()
        self.assertEqual(kernel.state, State.REJECTED)
        self.assertEqual(calls["commit"], 0)
        self.assertIsNone(kernel.commit_receipt)

    def test_probabilistic_exception_fails_without_commit(self):
        calls = {"model": 0, "commit": 0}

        def broken_model(_request):
            calls["model"] += 1
            raise RuntimeError("simulated model failure")

        kernel, calls = self.make_kernel(calls=calls, probabilistic_step=broken_model)
        with self.assertRaisesRegex(RuntimeError, "simulated"):
            kernel.run()
        self.assertEqual(kernel.state, State.FAILED)
        self.assertEqual(calls["commit"], 0)

    def test_commit_failure_never_claims_committed(self):
        def broken_commit(_request, _proposal):
            raise OSError("simulated sink failure")

        kernel, _ = self.make_kernel(commit_adapter=broken_commit)
        with self.assertRaisesRegex(OSError, "sink failure"):
            kernel.run()
        self.assertEqual(kernel.state, State.FAILED)
        self.assertIsNone(kernel.commit_receipt)

    def test_kernel_cannot_be_run_twice(self):
        kernel, _ = self.make_kernel()
        kernel.run()
        with self.assertRaisesRegex(RuntimeError, "only once"):
            kernel.run()


if __name__ == "__main__":
    unittest.main()
