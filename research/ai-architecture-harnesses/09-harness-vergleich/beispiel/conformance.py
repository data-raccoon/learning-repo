"""Wiederverwendbare, herstellerneutrale Conformance-Pruefungen."""

from harness_contract import Capability, HarnessAdapter, RunRequest, RunStatus


class ConformanceError(RuntimeError):
    """An advertised adapter behavior violates the shared contract."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ConformanceError(message)


def assert_core_conformance(adapter: HarnessAdapter) -> None:
    """Raise ConformanceError if advertised core behavior is inconsistent."""

    require(Capability.RUN in adapter.descriptor.capabilities, "RUN must be advertised")
    result = adapter.run(RunRequest("conformance", ("one", "two"), "contract-check"))
    require(bool(result.run_id), "run_id must not be empty")
    require(result.correlation_id == "contract-check", "correlation_id was not preserved")

    if Capability.RESUME in adapter.descriptor.capabilities:
        require(result.status is RunStatus.PAUSED, "resumable run must pause")
        require(result.resume_token is not None, "paused run requires a resume token")
        result = adapter.resume(result.resume_token)
        require(result.status is RunStatus.COMPLETED, "resume must complete the conformance run")
        require(result.resume_token is None, "completed run must not expose a resume token")

    if Capability.TRACE in adapter.descriptor.capabilities:
        events = adapter.trace(result.run_id)
        require(bool(events), "TRACE capability returned no events")
        require(
            [event.sequence for event in events] == list(range(1, len(events) + 1)),
            "trace sequence is not contiguous",
        )
        require(all(event.run_id == result.run_id for event in events), "trace run_id mismatch")
        require(
            all(event.correlation_id == result.correlation_id for event in events),
            "trace correlation_id mismatch",
        )
