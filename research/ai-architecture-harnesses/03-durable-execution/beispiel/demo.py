"""Ausführen mit: python demo.py (aus diesem Verzeichnis)."""

from pathlib import Path
from tempfile import TemporaryDirectory

from durable_harness import CrashInjected, DurableWorkflow, IdempotentReceiver, WorkflowStore


def main() -> None:
    with TemporaryDirectory() as directory:
        root = Path(directory)
        store = WorkflowStore(root / "workflow.db")
        receiver = IdempotentReceiver(root / "receiver.db")
        engine = DurableWorkflow(store, receiver)
        store.start("run-42", "order-7", 1250)
        engine.advance("run-42")

        try:
            engine.dispatch_one("run-42", crash_at="after_effect_before_ack")
        except CrashInjected as error:
            print(f"Simulierter Crash: {error}")

        # Neuer Prozess / neue Objekte, dieselben persistenten Datenbanken.
        resumed = DurableWorkflow(WorkflowStore(root / "workflow.db"), IdempotentReceiver(root / "receiver.db"))
        state = resumed.run_until_terminal("run-42")
        print(f"Endzustand: {state.terminal}")
        print(f"Fachzustand: {resumed.receiver.order('order-7')}")
        print("History:")
        for event in resumed.store.history("run-42"):
            print(f"  {event.seq:02d} {event.kind}: {event.data}")


if __name__ == "__main__":
    main()
