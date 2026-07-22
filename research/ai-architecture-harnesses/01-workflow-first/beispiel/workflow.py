"""Dependency-free workflow-first reference kernel.

The probabilistic function can propose data, but cannot transition state or commit it.
Costs are integer units on purpose: no floating-point accounting ambiguity exists.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from hashlib import sha256
import json
from typing import Callable, Mapping, Optional, Sequence, Tuple


class State(str, Enum):
    RECEIVED = "received"
    VALIDATED = "validated"
    PROPOSED = "proposed"
    POLICY_CHECKED = "policy_checked"
    COMMITTED = "committed"
    REJECTED = "rejected"
    FAILED = "failed"


TERMINAL_STATES = frozenset({State.COMMITTED, State.REJECTED, State.FAILED})


class WorkflowError(RuntimeError):
    """Base class for controlled workflow failures."""


class IllegalTransition(WorkflowError):
    pass


class BudgetExceeded(WorkflowError):
    pass


class ValidationFailed(WorkflowError):
    pass


class GateRejected(WorkflowError):
    pass


@dataclass(frozen=True)
class Request:
    request_id: str
    text: str


@dataclass(frozen=True)
class Proposal:
    """Untrusted output of the injected probabilistic leaf."""

    content: str
    labels: Tuple[str, ...] = ()

    def canonical_bytes(self) -> bytes:
        value = {"content": self.content, "labels": list(self.labels)}
        return json.dumps(
            value, sort_keys=True, separators=(",", ":"), ensure_ascii=False
        ).encode("utf-8")

    @property
    def digest(self) -> str:
        return sha256(self.canonical_bytes()).hexdigest()


@dataclass(frozen=True)
class Budget:
    max_steps: int
    max_cost_units: int

    def __post_init__(self) -> None:
        if self.max_steps < 0 or self.max_cost_units < 0:
            raise ValueError("budget limits must be non-negative")


@dataclass(frozen=True)
class AuditEvent:
    sequence: int
    event: str
    state_before: State
    state_after: State
    step_count: int
    cost_units: int
    details: Tuple[Tuple[str, str], ...]

    def details_dict(self) -> Mapping[str, str]:
        return dict(self.details)


ProbabilisticStep = Callable[[Request], Proposal]
RequestValidator = Callable[[Request], bool]
CommitGate = Callable[[Request, Proposal], bool]
CommitAdapter = Callable[[Request, Proposal], str]


class WorkflowKernel:
    """Single-run deterministic authority around an untrusted leaf function.

    The public API deliberately exposes only ``run``. State transitions are checked
    against a closed transition table. A production implementation would persist
    state and events atomically; this compact example keeps them in memory.
    """

    _TRANSITIONS = {
        State.RECEIVED: frozenset({State.VALIDATED, State.REJECTED, State.FAILED}),
        State.VALIDATED: frozenset({State.PROPOSED, State.FAILED}),
        State.PROPOSED: frozenset({State.POLICY_CHECKED, State.REJECTED, State.FAILED}),
        State.POLICY_CHECKED: frozenset({State.COMMITTED, State.FAILED}),
    }

    def __init__(
        self,
        *,
        request: Request,
        budget: Budget,
        probabilistic_step: ProbabilisticStep,
        request_validator: RequestValidator,
        commit_gate: CommitGate,
        commit_adapter: CommitAdapter,
        probabilistic_step_cost: int,
    ) -> None:
        if probabilistic_step_cost < 0:
            raise ValueError("probabilistic_step_cost must be non-negative")
        self.request = request
        self.budget = budget
        self.probabilistic_step = probabilistic_step
        self.request_validator = request_validator
        self.commit_gate = commit_gate
        self.commit_adapter = commit_adapter
        self.probabilistic_step_cost = probabilistic_step_cost

        self.state = State.RECEIVED
        self.step_count = 0
        self.cost_units = 0
        self.proposal: Optional[Proposal] = None
        self.commit_receipt: Optional[str] = None
        self._events: list[AuditEvent] = []
        self._record("run_received", State.RECEIVED, State.RECEIVED)

    @property
    def audit_events(self) -> Sequence[AuditEvent]:
        return tuple(self._events)

    def run(self) -> State:
        if self.state != State.RECEIVED:
            raise WorkflowError("a kernel instance can be run only once")

        try:
            self._consume_step("validate_request")
            if not self.request_validator(self.request):
                self._transition(State.REJECTED, "request_rejected")
                raise ValidationFailed("request validation failed")
            self._transition(State.VALIDATED, "request_validated")

            # Reserve the complete known charge before dispatch. If reservation
            # fails, the probabilistic callback is never invoked.
            self._consume_step(
                "probabilistic_dispatch", cost_units=self.probabilistic_step_cost
            )
            proposal = self.probabilistic_step(self.request)
            if not isinstance(proposal, Proposal):
                raise TypeError("probabilistic step must return Proposal")
            self.proposal = proposal
            self._transition(
                State.PROPOSED,
                "proposal_created",
                {"proposal_sha256": proposal.digest},
            )

            self._consume_step("commit_gate")
            if not self.commit_gate(self.request, proposal):
                self._transition(
                    State.REJECTED,
                    "commit_gate_rejected",
                    {"proposal_sha256": proposal.digest},
                )
                raise GateRejected("commit gate rejected proposal")
            self._transition(
                State.POLICY_CHECKED,
                "commit_gate_passed",
                {"proposal_sha256": proposal.digest},
            )

            self._consume_step("commit")
            receipt = self.commit_adapter(self.request, proposal)
            if not isinstance(receipt, str) or not receipt:
                raise ValueError("commit adapter must return a non-empty receipt")
            self.commit_receipt = receipt
            self._transition(
                State.COMMITTED,
                "committed",
                {"proposal_sha256": proposal.digest, "receipt": receipt},
            )
            return self.state
        except (ValidationFailed, GateRejected):
            raise
        except Exception as exc:
            # Fail closed. FAILED is reached only if the current state permits it;
            # a terminal REJECTED/COMMITTED run can never be rewritten.
            if self.state not in TERMINAL_STATES:
                self._transition(
                    State.FAILED,
                    "run_failed",
                    {"error_type": type(exc).__name__, "error": str(exc)},
                )
            raise

    def _consume_step(self, name: str, cost_units: int = 0) -> None:
        next_steps = self.step_count + 1
        next_cost = self.cost_units + cost_units
        if next_steps > self.budget.max_steps:
            self._record(
                "budget_denied",
                self.state,
                self.state,
                {"operation": name, "reason": "step_budget"},
            )
            raise BudgetExceeded(f"step budget denies {name}")
        if next_cost > self.budget.max_cost_units:
            self._record(
                "budget_denied",
                self.state,
                self.state,
                {"operation": name, "reason": "cost_budget"},
            )
            raise BudgetExceeded(f"cost budget denies {name}")
        self.step_count = next_steps
        self.cost_units = next_cost
        self._record(
            "budget_consumed",
            self.state,
            self.state,
            {"operation": name, "cost_units": str(cost_units)},
        )

    def _transition(
        self,
        new_state: State,
        event: str,
        details: Optional[Mapping[str, str]] = None,
    ) -> None:
        allowed = self._TRANSITIONS.get(self.state, frozenset())
        if new_state not in allowed:
            raise IllegalTransition(f"{self.state.value} -> {new_state.value} denied")
        old_state = self.state
        self.state = new_state
        self._record(event, old_state, new_state, details)

    def _record(
        self,
        event: str,
        before: State,
        after: State,
        details: Optional[Mapping[str, str]] = None,
    ) -> None:
        normalized = tuple(sorted((str(k), str(v)) for k, v in (details or {}).items()))
        self._events.append(
            AuditEvent(
                sequence=len(self._events) + 1,
                event=event,
                state_before=before,
                state_after=after,
                step_count=self.step_count,
                cost_units=self.cost_units,
                details=normalized,
            )
        )
