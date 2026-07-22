from harness import (
    AtomicBudget,
    DeterministicRouter,
    EvalCase,
    FakeModel,
    Orchestrator,
    RouteRule,
    TaskKind,
    WorkItem,
    compare_baseline_and_ensemble,
)


def main() -> None:
    analyst = FakeModel("small-analyst", "family-a", {"market": "stable"})
    verifier = FakeModel("special-verifier", "family-b", {"risk": "low"})
    router = DeterministicRouter([
        RouteRule(TaskKind.ANALYZE, "analyst", analyst.model_id),
        RouteRule(TaskKind.VERIFY, "verifier", verifier.model_id),
    ])
    orchestrator = Orchestrator(
        router,
        {model.model_id: model for model in (analyst, verifier)},
        AtomicBudget(max_calls=2, max_tokens=80),
        frozenset({("orchestrator", "analyst"), ("orchestrator", "verifier")}),
    )
    outputs = orchestrator.run("run-001", [
        WorkItem("market", "analyst", TaskKind.ANALYZE, frozenset({"market"}), "Assess market", 40),
        WorkItem("risk", "verifier", TaskKind.VERIFY, frozenset({"risk"}), "Assess risk", 40),
    ])
    for output in outputs:
        print(f"{output.handoff.task_id}: {output.result.answer} via {output.model_id}")

    cases = [EvalCase("q1", "2 + 2?", "4"), EvalCase("q2", "3 + 3?", "6")]
    baseline = FakeModel("baseline", "base", {"q1": "4", "q2": "5"})
    ensemble = [
        FakeModel("a", "family-a", {"q1": "4", "q2": "6"}),
        FakeModel("b", "family-b", {"q1": "4", "q2": "6"}),
        FakeModel("c", "family-c", {"q1": "5", "q2": "6"}),
    ]
    base_metrics, ensemble_metrics = compare_baseline_and_ensemble(cases, baseline, ensemble)
    print(f"baseline accuracy={base_metrics.accuracy:.0%}, calls={base_metrics.calls}")
    print(f"ensemble accuracy={ensemble_metrics.accuracy:.0%}, calls={ensemble_metrics.calls}")


if __name__ == "__main__":
    main()
