"""Kleine Kommandozeilen-Demonstration."""

from model_checker import check, format_trace
from workflow_model import ModelOptions


def show(name: str, options: ModelOptions, depth: int = 8) -> None:
    result = check(options=options, max_depth=depth)
    print(f"{name}: states={result.states_seen}, complete={result.complete}")
    if result.counterexample:
        print("  safety:", ", ".join(result.counterexample.violations))
        print("  shortest trace:", format_trace(result.counterexample.trace))
    else:
        print("  safety: no violation within explored states")
    for trace in result.deadlocks:
        print("  deadlock/liveness warning:", format_trace(trace))


if __name__ == "__main__":
    show("safe", ModelOptions())
    show("unsafe", ModelOptions(unsafe_direct_commit=True))
    show("approval unavailable", ModelOptions(approval_service_available=False))
