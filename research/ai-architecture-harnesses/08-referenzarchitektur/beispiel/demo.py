"""Run from this directory with: python demo.py"""

from reference_architecture import (
    Approval,
    Command,
    FakeModel,
    IdempotentToolAdapter,
    Kernel,
    PolicyGate,
    Proposal,
)


def main() -> None:
    model = FakeModel(
        lambda command: Proposal(command.action, command.target, {"message": "Hello safely"})
    )
    adapter = IdempotentToolAdapter()
    kernel = Kernel(model, PolicyGate({"publish"}, {"sandbox"}), adapter)

    command = Command(
        run_id="demo-001",
        actor="alice",
        action="publish",
        target="sandbox",
        instruction="Draft and publish a greeting",
        risk="high",
    )
    run = kernel.start(command)
    print("After model and policy:", run.state.value)
    assert run.proposal is not None

    approval = Approval.for_proposal(command.run_id, run.proposal, approver="reviewer-bob")
    run = kernel.commit(command.run_id, approval)
    print("After bound approval:", run.state.value)
    print("Receipt:", run.receipt)
    print("Visible effects:", len(adapter.effects))
    print("Audit chain valid:", kernel.audit.verify())


if __name__ == "__main__":
    main()
