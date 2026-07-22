import unittest

from reference_architecture import (
    Approval,
    ApprovalError,
    BudgetLease,
    Command,
    FakeModel,
    IdempotentToolAdapter,
    Kernel,
    PolicyGate,
    Proposal,
    State,
)


def command(run_id="run-1", risk="low", action="publish", target="sandbox"):
    return Command(run_id, "alice", action, target, "create a greeting", risk)


def kernel_for(proposer=None, actions=None, targets=None):
    proposer = proposer or (
        lambda cmd: Proposal(cmd.action, cmd.target, {"message": "hello"})
    )
    adapter = IdempotentToolAdapter()
    kernel = Kernel(
        FakeModel(proposer),
        PolicyGate(actions or {"publish"}, targets or {"sandbox"}),
        adapter,
    )
    return kernel, adapter


class ReferenceArchitectureTests(unittest.TestCase):
    def test_happy_path_commits_low_risk_action(self):
        kernel, adapter = kernel_for()

        run = kernel.start(command())

        self.assertEqual(State.COMMITTED, run.state)
        self.assertEqual(1, len(adapter.effects))
        self.assertIsNotNone(run.receipt)
        self.assertTrue(kernel.audit.verify())

    def test_policy_denies_unknown_target_without_effect(self):
        kernel, adapter = kernel_for(targets={"sandbox"})

        run = kernel.start(command(target="production"))

        self.assertEqual(State.POLICY_DENIED, run.state)
        self.assertEqual([], adapter.effects)

    def test_model_and_tool_budgets_fail_closed(self):
        model_kernel, _ = kernel_for()
        model_run = model_kernel.start(command("no-model"), BudgetLease(max_model_calls=0))
        self.assertEqual(State.BUDGET_EXHAUSTED, model_run.state)
        self.assertEqual(0, model_kernel.model.calls)

        tool_kernel, tool_adapter = kernel_for()
        tool_run = tool_kernel.start(
            command("no-tool"), BudgetLease(max_model_calls=1, max_tool_attempts=0)
        )
        self.assertEqual(State.BUDGET_EXHAUSTED, tool_run.state)
        self.assertEqual([], tool_adapter.effects)

    def test_approval_hash_rejects_tampered_payload(self):
        kernel, adapter = kernel_for()
        run = kernel.start(command(risk="high"))
        self.assertEqual(State.APPROVAL_PENDING, run.state)
        self.assertIsNotNone(run.proposal)
        approval = Approval.for_proposal(run.command.run_id, run.proposal, "bob")
        tampered = Proposal("publish", "sandbox", {"message": "changed after approval"})

        with self.assertRaises(ApprovalError):
            kernel.commit(run.command.run_id, approval, tampered)

        self.assertEqual(State.FAILED, run.state)
        self.assertEqual([], adapter.effects)

    def test_retry_is_deduplicated_by_adapter(self):
        adapter = IdempotentToolAdapter()
        proposal = Proposal("publish", "sandbox", {"message": "hello"})

        first = adapter.execute("same-run", proposal)
        retry = adapter.execute("same-run", proposal)

        self.assertEqual(first, retry)
        self.assertEqual(2, adapter.attempts)
        self.assertEqual(1, len(adapter.effects))


if __name__ == "__main__":
    unittest.main()
