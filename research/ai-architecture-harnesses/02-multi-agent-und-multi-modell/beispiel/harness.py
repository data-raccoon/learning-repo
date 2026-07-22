"""Dependency-free reference harness for bounded multi-agent/model execution.

The models in this module are deliberately injected.  Production adapters can
implement ``Model``, while the example and tests use deterministic fake models.
"""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from enum import Enum
from threading import Lock
from typing import Callable, Iterable, Mapping, Protocol, Sequence


class HarnessError(Exception):
    """Base class for failures rejected by the control plane."""


class InvalidHandoff(HarnessError):
    pass


class BudgetExceeded(HarnessError):
    pass


class InvalidPlan(HarnessError):
    pass


class TaskKind(str, Enum):
    EXTRACT = "extract"
    ANALYZE = "analyze"
    VERIFY = "verify"


@dataclass(frozen=True)
class Handoff:
    schema_version: str
    run_id: str
    task_id: str
    parent_id: str
    sender: str
    recipient: str
    reason_code: str
    kind: TaskKind
    scope: frozenset[str]
    prompt: str

    def validate(self, allowed_edges: frozenset[tuple[str, str]]) -> None:
        text_fields = (
            self.run_id,
            self.task_id,
            self.parent_id,
            self.sender,
            self.recipient,
            self.reason_code,
            self.prompt,
        )
        if self.schema_version != "1.0" or any(not value.strip() for value in text_fields):
            raise InvalidHandoff("missing field or unsupported schema version")
        if not isinstance(self.kind, TaskKind):
            raise InvalidHandoff("kind must be a TaskKind")
        if not self.scope or any(not isinstance(item, str) or not item for item in self.scope):
            raise InvalidHandoff("scope must contain non-empty strings")
        if (self.sender, self.recipient) not in allowed_edges:
            raise InvalidHandoff("handoff edge is not allowed")


@dataclass(frozen=True)
class WorkItem:
    task_id: str
    recipient: str
    kind: TaskKind
    scope: frozenset[str]
    prompt: str
    token_limit: int = 100


@dataclass(frozen=True)
class ModelResult:
    answer: str
    confidence: float
    tokens_used: int
    evidence: tuple[str, ...] = ()

    def validate(self, reserved_tokens: int) -> None:
        if not self.answer or not 0.0 <= self.confidence <= 1.0:
            raise HarnessError("invalid model result")
        if not 0 <= self.tokens_used <= reserved_tokens:
            raise HarnessError("model reported tokens outside its reservation")


class Model(Protocol):
    model_id: str
    failure_domain: str

    def invoke(self, handoff: Handoff, max_tokens: int) -> ModelResult: ...


@dataclass
class FakeModel:
    """Deterministic offline model, configured by task id or a default answer."""

    model_id: str
    failure_domain: str
    answers: Mapping[str, str]
    default_answer: str = "unknown"
    tokens_per_call: int = 10

    def invoke(self, handoff: Handoff, max_tokens: int) -> ModelResult:
        used = min(self.tokens_per_call, max_tokens)
        return ModelResult(
            answer=self.answers.get(handoff.task_id, self.default_answer),
            confidence=0.8,
            tokens_used=used,
            evidence=(f"fake:{self.model_id}:{handoff.task_id}",),
        )


@dataclass(frozen=True)
class Reservation:
    reservation_id: int
    calls: int
    tokens: int


@dataclass(frozen=True)
class BudgetSnapshot:
    max_calls: int
    max_tokens: int
    reserved_calls: int
    reserved_tokens: int
    spent_calls: int
    spent_tokens: int


class AtomicBudget:
    """Reserve before fan-out, so concurrent workers cannot double-spend."""

    def __init__(self, max_calls: int, max_tokens: int) -> None:
        if max_calls < 0 or max_tokens < 0:
            raise ValueError("budget limits must be non-negative")
        self._max_calls = max_calls
        self._max_tokens = max_tokens
        self._reserved_calls = 0
        self._reserved_tokens = 0
        self._spent_calls = 0
        self._spent_tokens = 0
        self._next_id = 1
        self._active: dict[int, Reservation] = {}
        self._lock = Lock()

    def reserve(self, calls: int, tokens: int) -> Reservation:
        if calls <= 0 or tokens < 0:
            raise ValueError("reservation must contain calls and non-negative tokens")
        with self._lock:
            if self._reserved_calls + self._spent_calls + calls > self._max_calls:
                raise BudgetExceeded("call budget exceeded")
            if self._reserved_tokens + self._spent_tokens + tokens > self._max_tokens:
                raise BudgetExceeded("token budget exceeded")
            reservation = Reservation(self._next_id, calls, tokens)
            self._next_id += 1
            self._active[reservation.reservation_id] = reservation
            self._reserved_calls += calls
            self._reserved_tokens += tokens
            return reservation

    def reserve_many(self, token_limits: Sequence[int]) -> tuple[Reservation, ...]:
        """Atomically admit a complete fan-out plan or reserve nothing."""
        if not token_limits or any(limit < 0 for limit in token_limits):
            raise ValueError("batch requires non-negative token limits")
        calls = len(token_limits)
        tokens = sum(token_limits)
        with self._lock:
            if self._reserved_calls + self._spent_calls + calls > self._max_calls:
                raise BudgetExceeded("call budget exceeded")
            if self._reserved_tokens + self._spent_tokens + tokens > self._max_tokens:
                raise BudgetExceeded("token budget exceeded")
            reservations = tuple(
                Reservation(self._next_id + offset, 1, limit)
                for offset, limit in enumerate(token_limits)
            )
            self._next_id += calls
            for reservation in reservations:
                self._active[reservation.reservation_id] = reservation
            self._reserved_calls += calls
            self._reserved_tokens += tokens
            return reservations

    def settle(self, reservation: Reservation, actual_tokens: int) -> None:
        if not 0 <= actual_tokens <= reservation.tokens:
            raise ValueError("actual usage must fit the reservation")
        with self._lock:
            active = self._active.pop(reservation.reservation_id, None)
            if active != reservation:
                raise ValueError("unknown or already settled reservation")
            self._reserved_calls -= reservation.calls
            self._reserved_tokens -= reservation.tokens
            self._spent_calls += reservation.calls
            self._spent_tokens += actual_tokens

    def cancel(self, reservation: Reservation) -> None:
        with self._lock:
            active = self._active.pop(reservation.reservation_id, None)
            if active != reservation:
                raise ValueError("unknown or already closed reservation")
            self._reserved_calls -= reservation.calls
            self._reserved_tokens -= reservation.tokens

    def snapshot(self) -> BudgetSnapshot:
        with self._lock:
            return BudgetSnapshot(
                self._max_calls,
                self._max_tokens,
                self._reserved_calls,
                self._reserved_tokens,
                self._spent_calls,
                self._spent_tokens,
            )


@dataclass(frozen=True)
class RouteRule:
    kind: TaskKind
    recipient: str
    model_id: str


class DeterministicRouter:
    def __init__(self, rules: Sequence[RouteRule]) -> None:
        self._routes: dict[tuple[TaskKind, str], str] = {}
        for rule in rules:
            key = (rule.kind, rule.recipient)
            if key in self._routes:
                raise ValueError(f"duplicate route: {key}")
            self._routes[key] = rule.model_id

    def route(self, kind: TaskKind, recipient: str) -> str:
        try:
            return self._routes[(kind, recipient)]
        except KeyError as exc:
            raise HarnessError(f"no route for {kind.value}/{recipient}") from exc


@dataclass(frozen=True)
class WorkerOutput:
    handoff: Handoff
    model_id: str
    failure_domain: str
    result: ModelResult


class Orchestrator:
    def __init__(
        self,
        router: DeterministicRouter,
        models: Mapping[str, Model],
        budget: AtomicBudget,
        allowed_edges: frozenset[tuple[str, str]],
    ) -> None:
        self.router = router
        self.models = dict(models)
        self.budget = budget
        self.allowed_edges = allowed_edges

    @staticmethod
    def validate_disjoint(items: Sequence[WorkItem]) -> None:
        if not items:
            raise InvalidPlan("plan must contain at least one work item")
        seen: set[str] = set()
        task_ids: set[str] = set()
        for item in items:
            if not item.scope or item.scope & seen:
                raise InvalidPlan("worker scopes must be non-empty and disjoint")
            if item.task_id in task_ids or item.token_limit < 0:
                raise InvalidPlan("task ids must be unique and token limits non-negative")
            seen.update(item.scope)
            task_ids.add(item.task_id)

    def _execute(
        self, handoff: Handoff, token_limit: int, reservation: Reservation
    ) -> WorkerOutput:
        handoff.validate(self.allowed_edges)
        model_id = self.router.route(handoff.kind, handoff.recipient)
        try:
            model = self.models[model_id]
        except KeyError as exc:
            raise HarnessError(f"routed model is not registered: {model_id}") from exc
        try:
            result = model.invoke(handoff, max_tokens=token_limit)
            result.validate(token_limit)
        except Exception:
            self.budget.cancel(reservation)
            raise
        self.budget.settle(reservation, result.tokens_used)
        return WorkerOutput(handoff, model.model_id, model.failure_domain, result)

    def run(self, run_id: str, items: Sequence[WorkItem]) -> tuple[WorkerOutput, ...]:
        self.validate_disjoint(items)
        handoffs = [
            Handoff(
                schema_version="1.0",
                run_id=run_id,
                task_id=item.task_id,
                parent_id=run_id,
                sender="orchestrator",
                recipient=item.recipient,
                reason_code="SECTION_WORK",
                kind=item.kind,
                scope=item.scope,
                prompt=item.prompt,
            )
            for item in items
        ]
        # Validate the entire plan before any budget or model side effect.
        for handoff in handoffs:
            handoff.validate(self.allowed_edges)
            model_id = self.router.route(handoff.kind, handoff.recipient)
            if model_id not in self.models:
                raise HarnessError(f"routed model is not registered: {model_id}")
        reservations = self.budget.reserve_many([item.token_limit for item in items])
        with ThreadPoolExecutor(max_workers=max(1, len(handoffs))) as pool:
            futures = [
                pool.submit(self._execute, handoff, item.token_limit, reservation)
                for handoff, item, reservation in zip(handoffs, items, reservations)
            ]
            return tuple(future.result() for future in futures)


@dataclass(frozen=True)
class Vote:
    answer: str
    voter_id: str
    failure_domain: str
    evidence: tuple[str, ...] = ()


class ResolutionStatus(str, Enum):
    CONSENSUS_UNVERIFIED = "consensus_unverified"
    VERIFIED = "verified"
    UNRESOLVED = "unresolved"
    REJECTED = "rejected"


@dataclass(frozen=True)
class Resolution:
    status: ResolutionStatus
    answer: str | None
    supporting_domains: tuple[str, ...]
    conflicts: Mapping[str, tuple[str, ...]] = field(default_factory=dict)


def resolve_votes(
    votes: Iterable[Vote],
    quorum: int = 2,
    verifier: Callable[[str], bool] | None = None,
) -> Resolution:
    """Resolve by independent failure domains; never label bare consensus true."""
    if quorum <= 0:
        raise ValueError("quorum must be positive")
    by_domain: dict[str, Vote] = {}
    conflicts: dict[str, list[str]] = {}
    for vote in votes:
        previous = by_domain.get(vote.failure_domain)
        if previous is None:
            by_domain[vote.failure_domain] = vote
        elif previous.answer != vote.answer:
            conflicts.setdefault(vote.failure_domain, [previous.answer]).append(vote.answer)

    support: dict[str, list[str]] = {}
    for domain, vote in by_domain.items():
        support.setdefault(vote.answer, []).append(domain)
    ordered = sorted(support.items(), key=lambda pair: (-len(pair[1]), pair[0]))
    frozen_conflicts = {key: tuple(value) for key, value in conflicts.items()}
    if not ordered or len(ordered[0][1]) < quorum:
        return Resolution(ResolutionStatus.UNRESOLVED, None, (), frozen_conflicts)
    if len(ordered) > 1 and len(ordered[0][1]) == len(ordered[1][1]):
        return Resolution(ResolutionStatus.UNRESOLVED, None, (), frozen_conflicts)
    answer, domains = ordered[0]
    if verifier is None:
        status = ResolutionStatus.CONSENSUS_UNVERIFIED
    else:
        status = ResolutionStatus.VERIFIED if verifier(answer) else ResolutionStatus.REJECTED
    return Resolution(status, answer, tuple(sorted(domains)), frozen_conflicts)


@dataclass(frozen=True)
class EvalCase:
    case_id: str
    prompt: str
    expected: str


@dataclass(frozen=True)
class EvalMetrics:
    cases: int
    correct: int
    abstained: int
    calls: int
    tokens: int

    @property
    def accuracy(self) -> float:
        return self.correct / self.cases if self.cases else 0.0


def compare_baseline_and_ensemble(
    cases: Sequence[EvalCase],
    baseline: Model,
    ensemble: Sequence[Model],
    quorum: int = 2,
) -> tuple[EvalMetrics, EvalMetrics]:
    """Simple labeled evaluation; expected values never enter model prompts."""
    baseline_correct = baseline_tokens = 0
    ensemble_correct = ensemble_tokens = abstained = 0
    for case in cases:
        handoff = Handoff(
            "1.0", "eval", case.case_id, "eval", "evaluator", "worker",
            "EVAL", TaskKind.ANALYZE, frozenset({case.case_id}), case.prompt,
        )
        base = baseline.invoke(handoff, 100)
        base.validate(100)
        baseline_tokens += base.tokens_used
        baseline_correct += base.answer == case.expected

        votes: list[Vote] = []
        for model in ensemble:
            result = model.invoke(handoff, 100)
            result.validate(100)
            ensemble_tokens += result.tokens_used
            votes.append(Vote(result.answer, model.model_id, model.failure_domain, result.evidence))
        resolution = resolve_votes(votes, quorum=quorum)
        if resolution.answer is None:
            abstained += 1
        else:
            ensemble_correct += resolution.answer == case.expected

    return (
        EvalMetrics(len(cases), baseline_correct, 0, len(cases), baseline_tokens),
        EvalMetrics(
            len(cases), ensemble_correct, abstained,
            len(cases) * len(ensemble), ensemble_tokens,
        ),
    )
