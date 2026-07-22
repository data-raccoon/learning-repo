"""Runnable offline demonstration: ``python demo.py``."""

from workflow import Budget, Proposal, Request, WorkflowKernel


def main() -> None:
    committed = []

    def model_stub(request: Request) -> Proposal:
        # A real adapter could call a model here. Its output remains untrusted.
        return Proposal(content=request.text.strip().upper(), labels=("demo",))

    def commit(request: Request, proposal: Proposal) -> str:
        committed.append(proposal.content)
        return f"memory:{request.request_id}:{len(committed)}"

    kernel = WorkflowKernel(
        request=Request("demo-1", "  kontrollierter Entwurf  "),
        budget=Budget(max_steps=4, max_cost_units=10),
        probabilistic_step=model_stub,
        request_validator=lambda request: bool(request.request_id and request.text.strip()),
        commit_gate=lambda _request, proposal: len(proposal.content) <= 100,
        commit_adapter=commit,
        probabilistic_step_cost=7,
    )
    final_state = kernel.run()
    print(f"state={final_state.value} receipt={kernel.commit_receipt}")
    for event in kernel.audit_events:
        print(event)


if __name__ == "__main__":
    main()
