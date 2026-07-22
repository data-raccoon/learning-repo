import sqlite3
import tempfile
import unittest
from pathlib import Path

from durable_harness import (
    CrashInjected,
    DurableWorkflow,
    IdempotencyConflict,
    IdempotentReceiver,
    WorkflowStore,
    replay,
    stable_idempotency_key,
)


class DurableHarnessTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        root = Path(self.temp.name)
        self.workflow_path = root / "workflow.db"
        self.receiver_path = root / "receiver.db"
        self.store = WorkflowStore(self.workflow_path)
        self.receiver = IdempotentReceiver(self.receiver_path)
        self.engine = DurableWorkflow(self.store, self.receiver)

    def tearDown(self):
        self.temp.cleanup()

    def reopen(self):
        self.store = WorkflowStore(self.workflow_path)
        self.receiver = IdempotentReceiver(self.receiver_path)
        self.engine = DurableWorkflow(self.store, self.receiver)

    def test_crash_before_effect_resumes(self):
        self.store.start("r1", "o1", 100)
        self.engine.advance("r1")
        with self.assertRaises(CrashInjected):
            self.engine.dispatch_one("r1", "before_effect")
        self.assertEqual({}, self.receiver.order("o1"))
        self.reopen()
        self.assertEqual("COMPLETED", self.engine.run_until_terminal("r1").terminal)

    def test_crash_after_effect_is_deduplicated_on_resume(self):
        self.store.start("r2", "o2", 100)
        self.engine.advance("r2")
        with self.assertRaises(CrashInjected):
            self.engine.dispatch_one("r2", "after_effect_before_ack")
        self.assertEqual("ACTIVE", self.receiver.order("o2")["reservation"])
        self.reopen()
        self.assertEqual("COMPLETED", self.engine.run_until_terminal("r2").terminal)
        completed = [e for e in self.store.history("r2") if e.kind == "ActivityCompleted"]
        self.assertTrue(completed[0].data["deduplicated_delivery"])
        self.assertEqual(3, self.receiver.inbox_count())

    def test_crash_after_local_commit_does_not_repeat_completed_step(self):
        self.store.start("r3", "o3", 100)
        self.engine.advance("r3")
        with self.assertRaises(CrashInjected):
            self.engine.dispatch_one("r3", "after_local_commit")
        self.reopen()
        self.assertEqual("COMPLETED", self.engine.run_until_terminal("r3").terminal)
        reserve_events = [
            e for e in self.store.history("r3")
            if e.kind == "ActivityCompleted" and e.data["operation"] == "forward.reserve"
        ]
        self.assertEqual(1, len(reserve_events))

    def test_replay_is_repeatable_and_side_effect_free(self):
        self.store.start("r4", "o4", 100)
        self.engine.advance("r4")
        history = self.store.history("r4")
        first = replay(history)
        second = replay(history)
        self.assertEqual(first, second)
        self.assertEqual(0, self.receiver.inbox_count())

    def test_stable_key_and_duplicate_delivery(self):
        payload = {"order_id": "o5", "amount": 100}
        key = stable_idempotency_key("r5", "forward.reserve")
        first = self.receiver.execute("forward.reserve", key, payload)
        second = self.receiver.execute("forward.reserve", key, payload)
        self.assertFalse(first[2])
        self.assertTrue(second[2])
        self.assertEqual(first[:2], second[:2])
        self.assertEqual(1, self.receiver.inbox_count())
        with self.assertRaises(IdempotencyConflict):
            self.receiver.execute("forward.reserve", key, {"order_id": "other", "amount": 100})

    def test_failed_shipping_runs_saga_compensation(self):
        self.store.start("r6", "o6", 100, fail_shipping=True)
        state = self.engine.run_until_terminal("r6")
        self.assertEqual("COMPENSATED", state.terminal)
        order = self.receiver.order("o6")
        self.assertEqual("REFUNDED", order["payment"])
        self.assertEqual("RELEASED", order["reservation"])
        operations = [
            e.data["operation"] for e in self.store.history("r6") if e.kind == "ActivityCompleted"
        ]
        self.assertEqual(
            ["forward.reserve", "forward.charge", "compensate.refund", "compensate.release"],
            operations,
        )

    def test_history_rejects_mutation(self):
        self.store.start("r7", "o7", 100)
        with self.store.connect() as db:
            with self.assertRaises(sqlite3.IntegrityError):
                db.execute("UPDATE events SET kind = 'tampered' WHERE run_id = 'r7'")
            with self.assertRaises(sqlite3.IntegrityError):
                db.execute("DELETE FROM events WHERE run_id = 'r7'")


if __name__ == "__main__":
    unittest.main()
