"""Herstellerneutraler Vertrag fuer Workflow-/Agent-Harnesses.

Die Typen modellieren nur pruefbare Laufzeiteigenschaften. Sie behaupten weder
fachliche Korrektheit eines Modelloutputs noch Exactly-once-Nebenwirkungen.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from types import MappingProxyType
from typing import Any, Iterable, Mapping
from uuid import uuid4


class Capability(str, Enum):
    RUN = "run"
    RESUME = "resume"
    CANCEL = "cancel"
    TRACE = "trace"


class RunStatus(str, Enum):
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


@dataclass(frozen=True)
class AdapterDescriptor:
    name: str
    version: str
    resume_semantics: str
    capabilities: frozenset[Capability]


@dataclass(frozen=True)
class RunRequest:
    task: str
    steps: tuple[str, ...]
    correlation_id: str = field(default_factory=lambda: str(uuid4()))

    def __post_init__(self) -> None:
        if not self.task.strip():
            raise ValueError("task must not be empty")
        if not self.steps:
            raise ValueError("at least one step is required")


@dataclass(frozen=True)
class ResumeToken:
    """Opaque, adaptergebundener Fortsetzungsbeleg."""

    adapter: str
    run_id: str
    value: str


@dataclass(frozen=True)
class RunResult:
    run_id: str
    correlation_id: str
    status: RunStatus
    output: tuple[str, ...]
    resume_token: ResumeToken | None = None


@dataclass(frozen=True)
class TraceEvent:
    sequence: int
    run_id: str
    correlation_id: str
    kind: str
    attributes: Mapping[str, Any]

    def __post_init__(self) -> None:
        object.__setattr__(self, "attributes", MappingProxyType(dict(self.attributes)))


class HarnessError(RuntimeError):
    pass


class CapabilityUnavailable(HarnessError):
    pass


class InvalidResume(HarnessError):
    pass


class UnknownRun(HarnessError):
    pass


class HarnessAdapter(ABC):
    """Kleinstmoegliche Portabilitaetsgrenze fuer Harness-Runtimes."""

    @property
    @abstractmethod
    def descriptor(self) -> AdapterDescriptor:
        raise NotImplementedError

    @abstractmethod
    def run(self, request: RunRequest) -> RunResult:
        raise NotImplementedError

    @abstractmethod
    def resume(self, token: ResumeToken) -> RunResult:
        raise NotImplementedError

    @abstractmethod
    def cancel(self, run_id: str) -> RunResult:
        raise NotImplementedError

    @abstractmethod
    def trace(self, run_id: str) -> tuple[TraceEvent, ...]:
        raise NotImplementedError


@dataclass(frozen=True)
class Requirements:
    """Deklarative Muss-Kriterien; keine versteckten Produktgewichte."""

    required: frozenset[Capability]

    @classmethod
    def requiring(cls, *capabilities: Capability) -> "Requirements":
        return cls(frozenset(capabilities))


def capability_matrix(adapters: Iterable[HarnessAdapter]) -> dict[str, dict[Capability, bool]]:
    return {
        adapter.descriptor.name: {
            capability: capability in adapter.descriptor.capabilities
            for capability in Capability
        }
        for adapter in adapters
    }


def eligible_adapters(
    adapters: Iterable[HarnessAdapter], requirements: Requirements
) -> tuple[HarnessAdapter, ...]:
    """Filtert ungeeignete Adapter, rankt die verbleibenden aber bewusst nicht."""

    return tuple(
        adapter
        for adapter in adapters
        if requirements.required <= adapter.descriptor.capabilities
    )
