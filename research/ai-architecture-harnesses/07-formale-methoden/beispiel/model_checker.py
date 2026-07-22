"""Expliziter bounded Model Checker mit kürzestem Gegenbeispiel (BFS)."""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass

from workflow_model import (
    TERMINAL,
    Event,
    ModelOptions,
    State,
    invariant_violations,
    successors,
)


@dataclass(frozen=True)
class TraceStep:
    event: Event
    state: State


@dataclass(frozen=True)
class Counterexample:
    violations: tuple[str, ...]
    trace: tuple[TraceStep, ...]


@dataclass(frozen=True)
class CheckResult:
    states_seen: int
    max_depth: int
    complete: bool
    counterexample: Counterexample | None
    deadlocks: tuple[tuple[TraceStep, ...], ...]

    @property
    def safety_holds_within_bound(self) -> bool:
        return self.counterexample is None


def check(
    initial: State = State(),
    options: ModelOptions = ModelOptions(),
    max_depth: int = 8,
) -> CheckResult:
    """Durchsucht per BFS; das erste Gegenbeispiel ist daher das kürzeste."""

    if max_depth < 0:
        raise ValueError("max_depth muss nichtnegativ sein")
    queue = deque([(initial, tuple(), 0)])
    seen = {initial}
    deadlocks: list[tuple[TraceStep, ...]] = []
    frontier_cut = False

    while queue:
        state, trace, depth = queue.popleft()
        violations = invariant_violations(state)
        if violations:
            return CheckResult(len(seen), max_depth, not frontier_cut, Counterexample(violations, trace), tuple(deadlocks))

        next_states = tuple(successors(state, options))
        if state.status not in TERMINAL and not next_states:
            deadlocks.append(trace)

        if depth == max_depth:
            if any(next_state not in seen for _, next_state in next_states):
                frontier_cut = True
            continue

        for event, next_state in next_states:
            if next_state not in seen:
                seen.add(next_state)
                queue.append((next_state, trace + (TraceStep(event, next_state),), depth + 1))

    return CheckResult(len(seen), max_depth, not frontier_cut, None, tuple(deadlocks))


def format_trace(trace: tuple[TraceStep, ...]) -> str:
    if not trace:
        return "(initial state)"
    return " -> ".join(f"{step.event.value}[{step.state.status.value}]" for step in trace)
