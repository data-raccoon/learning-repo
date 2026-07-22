"""Synchroner Runtime-Monitor auf Basis derselben Ereignisregeln wie das Modell."""

from __future__ import annotations

from workflow_model import Event, InvalidTransition, ModelOptions, State, invariant_violations, transition


class PolicyViolation(RuntimeError):
    pass


class RuntimeMonitor:
    """Fail-closed Monitor; der Aufrufer muss ihn vor jedem Effekt verwenden."""

    def __init__(self, initial: State = State(), options: ModelOptions = ModelOptions()):
        self.state = initial
        self.options = options
        self.audit_log: list[tuple[Event, State]] = []

    def observe(self, event: Event) -> State:
        try:
            candidate = transition(self.state, event, self.options)
        except InvalidTransition as exc:
            raise PolicyViolation(str(exc)) from exc
        violations = invariant_violations(candidate)
        if violations:
            raise PolicyViolation(", ".join(violations))
        self.state = candidate
        self.audit_log.append((event, candidate))
        return candidate
