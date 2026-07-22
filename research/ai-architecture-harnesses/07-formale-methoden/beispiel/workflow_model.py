"""Endliches Referenzmodell eines sicherheitskritischen Agent-Workflows.

Das Modell behandelt die Modellausgabe als beliebige vorgeschlagene Aktion. Nur
die hier definierte deterministische Transitionsfunktion entscheidet, was gilt.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from enum import Enum
from typing import Iterable


class Status(str, Enum):
    DRAFT = "draft"
    VALIDATED = "validated"
    AUTHORIZED = "authorized"
    AWAITING_APPROVAL = "awaiting_approval"
    APPROVED = "approved"
    COMMITTED = "committed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class Event(str, Enum):
    VALIDATE = "validate"
    AUTHORIZE = "authorize"
    REQUEST_APPROVAL = "request_approval"
    APPROVE = "approve"
    REJECT = "reject"
    COMMIT = "commit"
    FAIL = "fail"
    CANCEL = "cancel"


TERMINAL = frozenset({Status.COMMITTED, Status.FAILED, Status.CANCELLED})


@dataclass(frozen=True)
class State:
    status: Status = Status.DRAFT
    high_risk: bool = True
    authorized: bool = False
    approved: bool = False
    commits: int = 0
    budget: int = 3


@dataclass(frozen=True)
class ModelOptions:
    """Fehlerinjektion für demonstrierbare Gegenbeispiele."""

    unsafe_direct_commit: bool = False
    approval_service_available: bool = True


class InvalidTransition(ValueError):
    pass


def enabled_events(state: State, options: ModelOptions = ModelOptions()) -> tuple[Event, ...]:
    if state.status in TERMINAL:
        return ()

    # Störungsmodell: Der Run hängt im blockierenden Fremddienst; auch lokale
    # Timeout-/Cancel-Behandlung fehlt. Das macht den Designfehler als echten
    # nichtterminalen Zustand ohne Kante sichtbar.
    if state.status == Status.AWAITING_APPROVAL and not options.approval_service_available:
        return ()

    events: list[Event] = [Event.FAIL, Event.CANCEL]
    if state.status == Status.DRAFT:
        events.append(Event.VALIDATE)
        if options.unsafe_direct_commit:
            events.append(Event.COMMIT)
    elif state.status == Status.VALIDATED:
        events.append(Event.AUTHORIZE)
    elif state.status == Status.AUTHORIZED:
        events.append(Event.REQUEST_APPROVAL if state.high_risk else Event.COMMIT)
    elif state.status == Status.AWAITING_APPROVAL:
        events.extend((Event.APPROVE, Event.REJECT))
    elif state.status == Status.APPROVED:
        events.append(Event.COMMIT)
    return tuple(events)


def transition(
    state: State, event: Event, options: ModelOptions = ModelOptions()
) -> State:
    """Wendet genau eine atomare Modellaktion an oder lehnt sie ab."""

    if event not in enabled_events(state, options):
        raise InvalidTransition(f"{event.value!r} ist in {state.status.value!r} nicht erlaubt")

    if event == Event.VALIDATE:
        return replace(state, status=Status.VALIDATED, budget=state.budget - 1)
    if event == Event.AUTHORIZE:
        return replace(state, status=Status.AUTHORIZED, authorized=True, budget=state.budget - 1)
    if event == Event.REQUEST_APPROVAL:
        return replace(state, status=Status.AWAITING_APPROVAL)
    if event == Event.APPROVE:
        return replace(state, status=Status.APPROVED, approved=True)
    if event == Event.REJECT:
        return replace(state, status=Status.CANCELLED)
    if event == Event.COMMIT:
        return replace(state, status=Status.COMMITTED, commits=state.commits + 1)
    if event == Event.FAIL:
        return replace(state, status=Status.FAILED)
    if event == Event.CANCEL:
        return replace(state, status=Status.CANCELLED)
    raise AssertionError(f"nicht behandeltes Ereignis: {event}")


def invariant_violations(state: State) -> tuple[str, ...]:
    violations: list[str] = []
    if state.commits > 0 and not state.authorized:
        violations.append("commit_without_authorization")
    if state.commits > 0 and state.high_risk and not state.approved:
        violations.append("high_risk_commit_without_approval")
    if state.commits > 1:
        violations.append("more_than_one_logical_commit")
    if state.budget < 0:
        violations.append("negative_budget")
    return tuple(violations)


def successors(
    state: State, options: ModelOptions = ModelOptions()
) -> Iterable[tuple[Event, State]]:
    for event in enabled_events(state, options):
        yield event, transition(state, event, options)
