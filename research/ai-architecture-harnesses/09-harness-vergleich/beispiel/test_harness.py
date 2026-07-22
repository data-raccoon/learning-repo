import unittest

from conformance import ConformanceError, assert_core_conformance
from fake_adapters import EventReplayHarness, SnapshotHarness
from harness_contract import (
    Capability,
    CapabilityUnavailable,
    InvalidResume,
    Requirements,
    ResumeToken,
    RunRequest,
    RunStatus,
    capability_matrix,
    eligible_adapters,
)


class ContractTests(unittest.TestCase):
    def test_both_adapters_pass_shared_conformance_suite(self) -> None:
        for adapter in (SnapshotHarness(), EventReplayHarness()):
            with self.subTest(adapter=adapter.descriptor.name):
                assert_core_conformance(adapter)

    def test_conformance_rejects_adapter_with_empty_trace(self) -> None:
        class BrokenTraceAdapter(SnapshotHarness):
            def trace(self, run_id):
                return ()

        with self.assertRaisesRegex(ConformanceError, "no events"):
            assert_core_conformance(BrokenTraceAdapter())

    def test_missing_capability_excludes_adapter_and_fails_explicitly(self) -> None:
        snapshot, replay = SnapshotHarness(), EventReplayHarness()
        required = Requirements.requiring(Capability.RUN, Capability.CANCEL)
        self.assertEqual(
            ["snapshot-harness"],
            [a.descriptor.name for a in eligible_adapters((snapshot, replay), required)],
        )
        self.assertFalse(capability_matrix((replay,))[replay.descriptor.name][Capability.CANCEL])
        with self.assertRaises(CapabilityUnavailable):
            replay.cancel("any-run")

    def test_wrong_resume_token_is_rejected(self) -> None:
        snapshot = SnapshotHarness()
        paused = snapshot.run(RunRequest("task", ("a", "b")))
        wrong = ResumeToken("event-replay-harness", paused.run_id, paused.resume_token.value)
        with self.assertRaises(InvalidResume):
            snapshot.resume(wrong)

        replay = EventReplayHarness()
        paused = replay.run(RunRequest("task", ("a", "b")))
        wrong_cursor = ResumeToken(replay.descriptor.name, paused.run_id, "0")
        with self.assertRaises(InvalidResume):
            replay.resume(wrong_cursor)

    def test_cancel_is_terminal_and_invalidates_resume(self) -> None:
        adapter = SnapshotHarness()
        paused = adapter.run(RunRequest("task", ("a", "b")))
        cancelled = adapter.cancel(paused.run_id)
        self.assertIs(cancelled.status, RunStatus.CANCELLED)
        with self.assertRaises(InvalidResume):
            adapter.resume(paused.resume_token)
        self.assertEqual("run.cancelled", adapter.trace(paused.run_id)[-1].kind)

    def test_trace_has_end_to_end_correlation_and_monotonic_sequence(self) -> None:
        adapter = EventReplayHarness()
        result = adapter.run(RunRequest("task", ("a", "b"), "external-123"))
        result = adapter.resume(result.resume_token)
        events = adapter.trace(result.run_id)
        self.assertTrue(all(e.run_id == result.run_id for e in events))
        self.assertTrue(all(e.correlation_id == "external-123" for e in events))
        self.assertEqual(list(range(1, len(events) + 1)), [e.sequence for e in events])

    def test_selection_has_no_universal_ranking(self) -> None:
        # Reihenfolge bleibt die Eingabereihenfolge: Eligibility ist kein Score.
        snapshot, replay = SnapshotHarness(), EventReplayHarness()
        basic = Requirements.requiring(Capability.RUN, Capability.TRACE)
        self.assertEqual(
            ["event-replay-harness", "snapshot-harness"],
            [a.descriptor.name for a in eligible_adapters((replay, snapshot), basic)],
        )
        self.assertEqual(
            ["snapshot-harness", "event-replay-harness"],
            [a.descriptor.name for a in eligible_adapters((snapshot, replay), basic)],
        )


if __name__ == "__main__":
    unittest.main()
