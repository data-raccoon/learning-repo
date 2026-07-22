"""Dependency-free miniature reference architecture for controlled AI actions.

The model is deliberately a leaf: it can propose data but cannot authorize or
execute an action.  All authority remains in :class:`Kernel`.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from hashlib import sha256
import json
from typing import Any, Callable, Mapping, Optional


class State(str, Enum):
    RECEIVED = "received"
    MODEL_PENDING = "model_pending"
    CANDIDATE_READY = "candidate_ready"
    POLICY_ALLOWED = "policy_allowed"
    APPROVAL_PENDING = "approval_pending"
    COMMITTING = "committing"
    COMMITTED = "committed"
    POLICY_DENIED = "policy_denied"
    BUDGET_EXHAUSTED = "budget_exhausted"
    FAILED = "failed"


TERMINAL_STATES = {
    State.COMMITTED,
    State.POLICY_DENIED,
    State.BUDGET_EXHAUSTED,
    State.FAILED,
}


class ArchitectureError(RuntimeError):
    """Base class for failures that the control plane must handle explicitly."""


class InvalidTransition(ArchitectureError):
    pass


class BudgetExceeded(ArchitectureError):
    pass


class ApprovalError(ArchitectureError):
    pass


@dataclass(frozen=True)
class Command:
    run_id: str
    actor: str
    action: str
    target: str
    instruction: str
    risk: str = "low"

    def __post_init__(self) -> None:
        if not all((self.run_id, self.actor, self.action, self.target)):
            raise ValueError("command identity, action and target must be non-empty")
        if self.risk not in {"low", "high"}:
            raise ValueError("risk must be 'low' or 'high'")


@dataclass(frozen=True)
class Proposal:
    action: str
    target: str
    payload: Mapping[str, Any]

    def canonical_bytes(self) -> bytes:
        value = {"action": self.action, "target": self.target, "payload": self.payload}
        return json.dumps(
            value, sort_keys=True, separators=(",", ":"), ensure_ascii=False
        ).encode("utf-8")

    @property
    def payload_hash(self) -> str:
        return "sha256:" + sha256(self.canonical_bytes()).hexdigest()


@dataclass(frozen=True)
class Approval:
    run_id: str
    proposal_hash: str
    approver: str

    @classmethod
    def for_proposal(cls, run_id: str, proposal: Proposal, approver: str) -> "Approval":
        return cls(run_id=run_id, proposal_hash=proposal.payload_hash, approver=approver)


@dataclass(frozen=True)
class Receipt:
    idempotency_key: str
    effect_number: int
    status: str = "applied"


@dataclass(frozen=True)
class AuditEvent:
    sequence: int
    run_id: str
    event_type: str
    state_before: State
    state_after: State
    details: Mapping[str, Any]
    previous_hash: str
    event_hash: str


class AppendOnlyAudit:
    """An in-memory append-only, hash-chained audit log.

    Production code would put this API in front of immutable durable storage.
    Returning tuples prevents callers from mutating the internal event list.
    """

    def __init__(self) -> None:
        self._events: list[AuditEvent] = []

    @property
    def events(self) -> tuple[AuditEvent, ...]:
        return tuple(self._events)

    def append(
        self,
        run_id: str,
        event_type: str,
        before: State,
        after: State,
        details: Optional[Mapping[str, Any]] = None,
    ) -> AuditEvent:
        sequence = len(self._events) + 1
        previous_hash = self._events[-1].event_hash if self._events else "GENESIS"
        body = {
            "sequence": sequence,
            "run_id": run_id,
            "event_type": event_type,
            "state_before": before.value,
            "state_after": after.value,
            "details": dict(details or {}),
            "previous_hash": previous_hash,
        }
        digest = sha256(
            json.dumps(body, sort_keys=True, separators=(",", ":")).encode("utf-8")
        ).hexdigest()
        event = AuditEvent(
            sequence, run_id, event_type, before, after, body["details"], previous_hash, digest
        )
        self._events.append(event)
        return event

    def verify(self) -> bool:
        previous = "GENESIS"
        for event in self._events:
            body = {
                "sequence": event.sequence,
                "run_id": event.run_id,
                "event_type": event.event_type,
                "state_before": event.state_before.value,
                "state_after": event.state_after.value,
                "details": dict(event.details),
                "previous_hash": previous,
            }
            expected = sha256(
                json.dumps(body, sort_keys=True, separators=(",", ":")).encode("utf-8")
            ).hexdigest()
            if event.previous_hash != previous or event.event_hash != expected:
                return False
            previous = event.event_hash
        return True


@dataclass
class BudgetLease:
    max_model_calls: int = 1
    max_tool_attempts: int = 1
    model_calls: int = 0
    tool_attempts: int = 0

    def consume_model_call(self) -> None:
        if self.model_calls >= self.max_model_calls:
            raise BudgetExceeded("model-call budget exhausted")
        self.model_calls += 1

    def consume_tool_attempt(self) -> None:
        if self.tool_attempts >= self.max_tool_attempts:
            raise BudgetExceeded("tool-attempt budget exhausted")
        self.tool_attempts += 1


class FakeModel:
    """Injected deterministic test double for a probabilistic model API."""

    def __init__(self, proposer: Callable[[Command], Proposal]) -> None:
        self._proposer = proposer
        self.calls = 0

    def propose(self, command: Command) -> Proposal:
        self.calls += 1
        return self._proposer(command)


class PolicyGate:
    def __init__(self, allowed_actions: set[str], allowed_targets: set[str]) -> None:
        self.allowed_actions = frozenset(allowed_actions)
        self.allowed_targets = frozenset(allowed_targets)

    def allows(self, command: Command, proposal: Proposal) -> bool:
        # The model may not silently change the authorized action or target.
        return (
            proposal.action == command.action
            and proposal.target == command.target
            and proposal.action in self.allowed_actions
            and proposal.target in self.allowed_targets
        )


class IdempotentToolAdapter:
    """Records one visible effect per deterministic idempotency key."""

    def __init__(self) -> None:
        self._receipts: dict[str, Receipt] = {}
        self.effects: list[Proposal] = []
        self.attempts = 0

    @staticmethod
    def key(run_id: str, proposal: Proposal) -> str:
        material = (run_id + "\n" + proposal.payload_hash).encode("utf-8")
        return "sha256:" + sha256(material).hexdigest()

    def execute(self, run_id: str, proposal: Proposal) -> Receipt:
        self.attempts += 1
        key = self.key(run_id, proposal)
        if key in self._receipts:
            return self._receipts[key]
        self.effects.append(proposal)
        receipt = Receipt(key, effect_number=len(self.effects))
        self._receipts[key] = receipt
        return receipt


@dataclass
class Run:
    command: Command
    budget: BudgetLease
    state: State = State.RECEIVED
    proposal: Optional[Proposal] = None
    receipt: Optional[Receipt] = None


class Kernel:
    """Deterministic control plane around model and tool leaves."""

    _ALLOWED: dict[State, set[State]] = {
        State.RECEIVED: {State.MODEL_PENDING, State.BUDGET_EXHAUSTED},
        State.MODEL_PENDING: {State.CANDIDATE_READY, State.BUDGET_EXHAUSTED, State.FAILED},
        State.CANDIDATE_READY: {State.POLICY_ALLOWED, State.POLICY_DENIED},
        State.POLICY_ALLOWED: {
            State.APPROVAL_PENDING,
            State.COMMITTING,
            State.BUDGET_EXHAUSTED,
        },
        State.APPROVAL_PENDING: {State.COMMITTING, State.FAILED, State.BUDGET_EXHAUSTED},
        State.COMMITTING: {State.COMMITTED, State.FAILED},
    }

    def __init__(
        self,
        model: FakeModel,
        policy: PolicyGate,
        adapter: IdempotentToolAdapter,
        audit: Optional[AppendOnlyAudit] = None,
    ) -> None:
        self.model = model
        self.policy = policy
        self.adapter = adapter
        self.audit = audit or AppendOnlyAudit()
        self.runs: dict[str, Run] = {}

    def _transition(self, run: Run, after: State, event_type: str, **details: Any) -> None:
        before = run.state
        if after not in self._ALLOWED.get(before, set()):
            raise InvalidTransition(f"{before.value} -> {after.value} is not allowed")
        run.state = after
        self.audit.append(run.command.run_id, event_type, before, after, details)

    def start(self, command: Command, budget: Optional[BudgetLease] = None) -> Run:
        if command.run_id in self.runs:
            raise ValueError(f"duplicate run_id: {command.run_id}")
        run = Run(command=command, budget=budget or BudgetLease())
        self.runs[command.run_id] = run
        try:
            run.budget.consume_model_call()
        except BudgetExceeded:
            self._transition(run, State.BUDGET_EXHAUSTED, "budget.exhausted", resource="model")
            return run

        self._transition(run, State.MODEL_PENDING, "model.requested")
        try:
            proposal = self.model.propose(command)
            if not isinstance(proposal, Proposal):
                raise TypeError("model result is not a Proposal")
            run.proposal = proposal
            self._transition(
                run, State.CANDIDATE_READY, "model.candidate", proposal_hash=proposal.payload_hash
            )
        except Exception as exc:
            self._transition(run, State.FAILED, "model.failed", error=type(exc).__name__)
            return run

        if not self.policy.allows(command, proposal):
            self._transition(run, State.POLICY_DENIED, "policy.denied")
            return run
        self._transition(run, State.POLICY_ALLOWED, "policy.allowed")

        if command.risk == "high":
            self._transition(
                run,
                State.APPROVAL_PENDING,
                "approval.requested",
                proposal_hash=proposal.payload_hash,
            )
            return run
        return self._commit(run, approval=None, proposal=proposal)

    def commit(
        self,
        run_id: str,
        approval: Approval,
        proposal: Optional[Proposal] = None,
    ) -> Run:
        run = self.runs[run_id]
        candidate = proposal or run.proposal
        if candidate is None:
            raise ApprovalError("run has no proposal")
        if run.state != State.APPROVAL_PENDING:
            raise InvalidTransition("run is not awaiting approval")
        if (
            approval.run_id != run_id
            or not approval.approver
            or approval.proposal_hash != candidate.payload_hash
            or candidate != run.proposal
        ):
            self._transition(run, State.FAILED, "approval.invalid")
            raise ApprovalError("approval does not bind this run's exact proposal")
        self.audit.append(
            run_id,
            "approval.accepted",
            run.state,
            run.state,
            {"approver": approval.approver, "proposal_hash": approval.proposal_hash},
        )
        return self._commit(run, approval=approval, proposal=candidate)

    def _commit(
        self, run: Run, approval: Optional[Approval], proposal: Proposal
    ) -> Run:
        del approval  # validation happened at the boundary above
        try:
            run.budget.consume_tool_attempt()
        except BudgetExceeded:
            self._transition(run, State.BUDGET_EXHAUSTED, "budget.exhausted", resource="tool")
            return run
        self._transition(run, State.COMMITTING, "tool.requested")
        try:
            run.receipt = self.adapter.execute(run.command.run_id, proposal)
        except Exception as exc:
            self._transition(run, State.FAILED, "tool.failed", error=type(exc).__name__)
            return run
        self._transition(
            run,
            State.COMMITTED,
            "tool.committed",
            idempotency_key=run.receipt.idempotency_key,
        )
        return run
