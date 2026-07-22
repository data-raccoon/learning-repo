"""Ausfuehrbare Auswahl- und Resume-Demonstration."""

from conformance import assert_core_conformance
from fake_adapters import EventReplayHarness, SnapshotHarness
from harness_contract import Capability, Requirements, RunRequest, capability_matrix, eligible_adapters


def main() -> None:
    adapters = [SnapshotHarness(), EventReplayHarness()]
    print("Capability-Matrix:")
    for name, capabilities in capability_matrix(adapters).items():
        flags = ", ".join(f"{cap.value}={supported}" for cap, supported in capabilities.items())
        print(f"  {name}: {flags}")

    requirements = Requirements.requiring(Capability.RUN, Capability.RESUME, Capability.CANCEL)
    eligible = eligible_adapters(adapters, requirements)
    print("\nGeeignet fuer run+resume+cancel:", ", ".join(a.descriptor.name for a in eligible))

    adapter = eligible[0]
    result = adapter.run(RunRequest("Bericht erzeugen", ("planen", "schreiben"), "demo-42"))
    print("Erster Aufruf:", result.status.value, result.output)
    result = adapter.resume(result.resume_token)  # type: ignore[arg-type]
    print("Nach Resume:", result.status.value, result.output)
    print("Trace:", [(event.sequence, event.kind) for event in adapter.trace(result.run_id)])

    for candidate in adapters:
        assert_core_conformance(candidate)
    print("Conformance: OK")


if __name__ == "__main__":
    main()
