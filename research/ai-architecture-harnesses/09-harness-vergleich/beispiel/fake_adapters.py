"""Deterministische Test-Doubles zweier verschiedener Resume-Modelle."""

from __future__ import annotations

from dataclasses import dataclass, field
from uuid import uuid4

from harness_contract import (
    AdapterDescriptor,
    Capability,
    CapabilityUnavailable,
    HarnessAdapter,
    InvalidResume,
    ResumeToken,
    RunRequest,
    RunResult,
    RunStatus,
    TraceEvent,
    UnknownRun,
)


@dataclass
class _RunState:
    request: RunRequest
    completed: int = 0
    status: RunStatus = RunStatus.PAUSED
    output: list[str] = field(default_factory=list)
    events: list[TraceEvent] = field(default_factory=list)
    token_nonce: str | None = None


class _MemoryAdapter(HarnessAdapter):
    """Gemeinsamer Speicher, nicht Teil des oeffentlichen Adaptervertrags."""

    def __init__(self) -> None:
        self._runs: dict[str, _RunState] = {}

    def _state(self, run_id: str) -> _RunState:
        try:
            return self._runs[run_id]
        except KeyError as exc:
            raise UnknownRun(run_id) from exc

    def _emit(self, run_id: str, kind: str, **attributes: object) -> None:
        state = self._state(run_id)
        state.events.append(
            TraceEvent(
                sequence=len(state.events) + 1,
                run_id=run_id,
                correlation_id=state.request.correlation_id,
                kind=kind,
                attributes=attributes,
            )
        )

    def _result(self, run_id: str, token: ResumeToken | None = None) -> RunResult:
        state = self._state(run_id)
        return RunResult(
            run_id=run_id,
            correlation_id=state.request.correlation_id,
            status=state.status,
            output=tuple(state.output),
            resume_token=token,
        )

    def trace(self, run_id: str) -> tuple[TraceEvent, ...]:
        if Capability.TRACE not in self.descriptor.capabilities:
            raise CapabilityUnavailable("trace")
        return tuple(self._state(run_id).events)


class SnapshotHarness(_MemoryAdapter):
    """Fuehrt je Aufruf einen Schritt aus und ersetzt danach den Snapshot-Token."""

    descriptor = AdapterDescriptor(
        name="snapshot-harness",
        version="1.0",
        resume_semantics="opaque mutable snapshot; every token is single-use",
        capabilities=frozenset(Capability),
    )

    def run(self, request: RunRequest) -> RunResult:
        run_id = str(uuid4())
        self._runs[run_id] = _RunState(request=request)
        self._emit(run_id, "run.started", task=request.task)
        return self._advance(run_id)

    def _advance(self, run_id: str) -> RunResult:
        state = self._state(run_id)
        step = state.request.steps[state.completed]
        state.output.append(f"snapshot:{step}")
        state.completed += 1
        self._emit(run_id, "step.completed", step=step)
        if state.completed == len(state.request.steps):
            state.status = RunStatus.COMPLETED
            state.token_nonce = None
            self._emit(run_id, "run.completed")
            return self._result(run_id)
        state.token_nonce = str(uuid4())
        token = ResumeToken(self.descriptor.name, run_id, state.token_nonce)
        self._emit(run_id, "run.paused", checkpoint=state.completed)
        return self._result(run_id, token)

    def resume(self, token: ResumeToken) -> RunResult:
        if token.adapter != self.descriptor.name:
            raise InvalidResume("token belongs to another adapter")
        state = self._state(token.run_id)
        if state.status is not RunStatus.PAUSED or token.value != state.token_nonce:
            raise InvalidResume("stale or invalid snapshot token")
        state.token_nonce = None
        self._emit(token.run_id, "run.resumed")
        return self._advance(token.run_id)

    def cancel(self, run_id: str) -> RunResult:
        state = self._state(run_id)
        if state.status is RunStatus.PAUSED:
            state.status = RunStatus.CANCELLED
            state.token_nonce = None
            self._emit(run_id, "run.cancelled")
        return self._result(run_id)


class EventReplayHarness(_MemoryAdapter):
    """Rekonstruiert Fortschritt aus einem Cursor; Cancel wird nicht angeboten."""

    descriptor = AdapterDescriptor(
        name="event-replay-harness",
        version="1.0",
        resume_semantics="immutable event cursor bound to run history",
        capabilities=frozenset({Capability.RUN, Capability.RESUME, Capability.TRACE}),
    )

    def run(self, request: RunRequest) -> RunResult:
        run_id = str(uuid4())
        self._runs[run_id] = _RunState(request=request)
        self._emit(run_id, "run.started", task=request.task)
        return self._replay_and_advance(run_id, expected_cursor=0)

    def _replay_and_advance(self, run_id: str, expected_cursor: int) -> RunResult:
        state = self._state(run_id)
        if state.completed != expected_cursor:
            raise InvalidResume("cursor does not match durable event history")
        step = state.request.steps[state.completed]
        state.output.append(f"event:{step}")
        state.completed += 1
        self._emit(run_id, "event.committed", cursor=state.completed, step=step)
        if state.completed == len(state.request.steps):
            state.status = RunStatus.COMPLETED
            self._emit(run_id, "run.completed")
            return self._result(run_id)
        token = ResumeToken(self.descriptor.name, run_id, str(state.completed))
        self._emit(run_id, "run.paused", cursor=state.completed)
        return self._result(run_id, token)

    def resume(self, token: ResumeToken) -> RunResult:
        if token.adapter != self.descriptor.name:
            raise InvalidResume("token belongs to another adapter")
        state = self._state(token.run_id)
        if state.status is not RunStatus.PAUSED:
            raise InvalidResume("run is not paused")
        try:
            cursor = int(token.value)
        except ValueError as exc:
            raise InvalidResume("cursor must be an integer") from exc
        self._emit(token.run_id, "history.replayed", cursor=cursor)
        return self._replay_and_advance(token.run_id, cursor)

    def cancel(self, run_id: str) -> RunResult:
        raise CapabilityUnavailable("event-replay-harness does not support cancel")
