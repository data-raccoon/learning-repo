"""Kleines, dependency-freies Durable-Workflow-Harness.

Das Beispiel demonstriert Mechanismen, keine allgemeine Exactly-once-Garantie.
History/Outbox sowie Inbox/fachliche Wirkung sind jeweils lokal atomar. Zwischen
diesen beiden SQLite-Datenbanken gibt es absichtlich keine verteilte Transaktion.
"""

from __future__ import annotations

import hashlib
import json
import sqlite3
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def stable_idempotency_key(run_id: str, logical_operation: str, version: int = 1) -> str:
    """Deterministischer Key; Retries derselben logischen Operation bleiben stabil."""
    material = canonical_json({"run_id": run_id, "operation": logical_operation, "version": version})
    return hashlib.sha256(material.encode("utf-8")).hexdigest()


def payload_hash(payload: dict[str, Any]) -> str:
    return hashlib.sha256(canonical_json(payload).encode("utf-8")).hexdigest()


class CrashInjected(RuntimeError):
    """Simulierter Prozessabsturz an einer expliziten Commit-Grenze."""


class IdempotencyConflict(RuntimeError):
    """Derselbe Key wurde mit einem anderen Payload wiederverwendet."""


class ClosingConnection(sqlite3.Connection):
    """Commit/Rollback wie sqlite3, danach das Dateihandle zuverlässig schließen."""

    def __exit__(self, exc_type: Any, exc_value: Any, traceback: Any) -> bool:
        try:
            return bool(super().__exit__(exc_type, exc_value, traceback))
        finally:
            self.close()


@dataclass(frozen=True)
class HistoryEvent:
    seq: int
    run_id: str
    kind: str
    data: dict[str, Any]


@dataclass
class WorkflowState:
    run_id: str
    order_id: str | None = None
    amount: int | None = None
    fail_shipping: bool = False
    scheduled: set[str] = field(default_factory=set)
    completed: set[str] = field(default_factory=set)
    failed: set[str] = field(default_factory=set)
    terminal: str | None = None


class WorkflowStore:
    """Persistiert unveränderliche History und Transactional Outbox gemeinsam."""

    def __init__(self, path: str | Path):
        self.path = str(path)
        self._initialize()

    def connect(self) -> sqlite3.Connection:
        db = sqlite3.connect(self.path, factory=ClosingConnection)
        db.row_factory = sqlite3.Row
        db.execute("PRAGMA foreign_keys = ON")
        return db

    def _initialize(self) -> None:
        with self.connect() as db:
            db.executescript(
                """
                CREATE TABLE IF NOT EXISTS events (
                    seq INTEGER PRIMARY KEY AUTOINCREMENT,
                    run_id TEXT NOT NULL,
                    kind TEXT NOT NULL,
                    data TEXT NOT NULL
                );
                CREATE INDEX IF NOT EXISTS events_run_seq ON events(run_id, seq);
                CREATE TRIGGER IF NOT EXISTS events_no_update
                    BEFORE UPDATE ON events BEGIN SELECT RAISE(ABORT, 'history is append-only'); END;
                CREATE TRIGGER IF NOT EXISTS events_no_delete
                    BEFORE DELETE ON events BEGIN SELECT RAISE(ABORT, 'history is append-only'); END;
                CREATE TABLE IF NOT EXISTS outbox (
                    event_seq INTEGER PRIMARY KEY REFERENCES events(seq),
                    run_id TEXT NOT NULL,
                    operation TEXT NOT NULL,
                    idempotency_key TEXT NOT NULL UNIQUE,
                    payload TEXT NOT NULL,
                    delivered INTEGER NOT NULL DEFAULT 0 CHECK(delivered IN (0, 1))
                );
                """
            )

    @staticmethod
    def _append(db: sqlite3.Connection, run_id: str, kind: str, data: dict[str, Any]) -> int:
        cursor = db.execute(
            "INSERT INTO events(run_id, kind, data) VALUES (?, ?, ?)",
            (run_id, kind, canonical_json(data)),
        )
        return int(cursor.lastrowid)

    def start(self, run_id: str, order_id: str, amount: int, fail_shipping: bool = False) -> None:
        with self.connect() as db:
            db.execute("BEGIN IMMEDIATE")
            exists = db.execute("SELECT 1 FROM events WHERE run_id = ?", (run_id,)).fetchone()
            if exists:
                raise ValueError(f"run already exists: {run_id}")
            self._append(
                db,
                run_id,
                "WorkflowStarted",
                {"order_id": order_id, "amount": amount, "fail_shipping": fail_shipping},
            )

    def append(self, run_id: str, kind: str, data: dict[str, Any]) -> int:
        with self.connect() as db:
            db.execute("BEGIN IMMEDIATE")
            return self._append(db, run_id, kind, data)

    def schedule(self, run_id: str, operation: str, payload: dict[str, Any]) -> str:
        key = stable_idempotency_key(run_id, operation)
        with self.connect() as db:
            db.execute("BEGIN IMMEDIATE")
            existing = db.execute(
                "SELECT payload FROM outbox WHERE idempotency_key = ?", (key,)
            ).fetchone()
            encoded = canonical_json(payload)
            if existing:
                if existing["payload"] != encoded:
                    raise IdempotencyConflict(f"payload mismatch for {key}")
                return key
            seq = self._append(
                db,
                run_id,
                "ActivityScheduled",
                {"operation": operation, "idempotency_key": key, "payload_hash": payload_hash(payload)},
            )
            db.execute(
                "INSERT INTO outbox(event_seq, run_id, operation, idempotency_key, payload) "
                "VALUES (?, ?, ?, ?, ?)",
                (seq, run_id, operation, key, encoded),
            )
        return key

    def pending(self, run_id: str) -> list[sqlite3.Row]:
        with self.connect() as db:
            return list(
                db.execute(
                    "SELECT * FROM outbox WHERE run_id = ? AND delivered = 0 ORDER BY event_seq", (run_id,)
                )
            )

    def acknowledge(
        self, row: sqlite3.Row, *, ok: bool, result: dict[str, Any], deduplicated: bool
    ) -> None:
        """History-Ergebnis und Outbox-Ack bilden eine lokale Transaktion."""
        with self.connect() as db:
            db.execute("BEGIN IMMEDIATE")
            current = db.execute(
                "SELECT delivered FROM outbox WHERE event_seq = ?", (row["event_seq"],)
            ).fetchone()
            if current is None or current["delivered"]:
                return
            self._append(
                db,
                row["run_id"],
                "ActivityCompleted" if ok else "ActivityFailed",
                {
                    "operation": row["operation"],
                    "idempotency_key": row["idempotency_key"],
                    "result": result,
                    "deduplicated_delivery": deduplicated,
                },
            )
            db.execute("UPDATE outbox SET delivered = 1 WHERE event_seq = ?", (row["event_seq"],))

    def history(self, run_id: str) -> list[HistoryEvent]:
        with self.connect() as db:
            rows = db.execute(
                "SELECT seq, run_id, kind, data FROM events WHERE run_id = ? ORDER BY seq", (run_id,)
            )
            return [HistoryEvent(r["seq"], r["run_id"], r["kind"], json.loads(r["data"])) for r in rows]


class IdempotentReceiver:
    """Simuliertes Wirkungssystem mit atomarer Inbox + fachlichem Zustand."""

    def __init__(self, path: str | Path):
        self.path = str(path)
        with self.connect() as db:
            db.executescript(
                """
                CREATE TABLE IF NOT EXISTS inbox (
                    idempotency_key TEXT PRIMARY KEY,
                    payload_hash TEXT NOT NULL,
                    ok INTEGER NOT NULL,
                    result TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS orders (
                    order_id TEXT PRIMARY KEY,
                    reservation TEXT,
                    payment TEXT,
                    shipment TEXT
                );
                """
            )

    def connect(self) -> sqlite3.Connection:
        db = sqlite3.connect(self.path, factory=ClosingConnection)
        db.row_factory = sqlite3.Row
        return db

    def execute(
        self, operation: str, key: str, payload: dict[str, Any]
    ) -> tuple[bool, dict[str, Any], bool]:
        digest = payload_hash(payload)
        with self.connect() as db:
            db.execute("BEGIN IMMEDIATE")
            prior = db.execute("SELECT * FROM inbox WHERE idempotency_key = ?", (key,)).fetchone()
            if prior:
                if prior["payload_hash"] != digest:
                    raise IdempotencyConflict(f"payload mismatch for {key}")
                return bool(prior["ok"]), json.loads(prior["result"]), True

            order_id = str(payload["order_id"])
            db.execute("INSERT OR IGNORE INTO orders(order_id) VALUES (?)", (order_id,))
            ok, result = self._apply(db, operation, payload)
            db.execute(
                "INSERT INTO inbox(idempotency_key, payload_hash, ok, result) VALUES (?, ?, ?, ?)",
                (key, digest, int(ok), canonical_json(result)),
            )
            return ok, result, False

    @staticmethod
    def _apply(
        db: sqlite3.Connection, operation: str, payload: dict[str, Any]
    ) -> tuple[bool, dict[str, Any]]:
        order_id = str(payload["order_id"])
        if operation == "forward.reserve":
            db.execute("UPDATE orders SET reservation = 'ACTIVE' WHERE order_id = ?", (order_id,))
        elif operation == "forward.charge":
            db.execute("UPDATE orders SET payment = 'CHARGED' WHERE order_id = ?", (order_id,))
        elif operation == "forward.ship":
            if payload.get("fail_shipping"):
                return False, {"error": "shipping rejected"}
            db.execute("UPDATE orders SET shipment = 'SHIPPED' WHERE order_id = ?", (order_id,))
        elif operation == "compensate.refund":
            db.execute("UPDATE orders SET payment = 'REFUNDED' WHERE order_id = ?", (order_id,))
        elif operation == "compensate.release":
            db.execute("UPDATE orders SET reservation = 'RELEASED' WHERE order_id = ?", (order_id,))
        else:
            return False, {"error": f"unknown operation: {operation}"}
        return True, {"operation": operation, "order_id": order_id, "status": "applied"}

    def order(self, order_id: str) -> dict[str, Any]:
        with self.connect() as db:
            row = db.execute("SELECT * FROM orders WHERE order_id = ?", (order_id,)).fetchone()
            return dict(row) if row else {}

    def inbox_count(self) -> int:
        with self.connect() as db:
            return int(db.execute("SELECT COUNT(*) FROM inbox").fetchone()[0])


def replay(events: Iterable[HistoryEvent]) -> WorkflowState:
    """Reine Zustandsreduktion: kein I/O, keine Uhrzeit, kein Zufall."""
    state: WorkflowState | None = None
    for event in events:
        if event.kind == "WorkflowStarted":
            if state is not None:
                raise ValueError("duplicate WorkflowStarted")
            state = WorkflowState(
                run_id=event.run_id,
                order_id=event.data["order_id"],
                amount=int(event.data["amount"]),
                fail_shipping=bool(event.data["fail_shipping"]),
            )
        elif state is None:
            raise ValueError("history does not start with WorkflowStarted")
        elif event.kind == "ActivityScheduled":
            state.scheduled.add(event.data["operation"])
        elif event.kind == "ActivityCompleted":
            state.completed.add(event.data["operation"])
        elif event.kind == "ActivityFailed":
            state.failed.add(event.data["operation"])
        elif event.kind == "WorkflowCompleted":
            state.terminal = "COMPLETED"
        elif event.kind == "WorkflowCompensated":
            state.terminal = "COMPENSATED"
        else:
            raise ValueError(f"unknown event kind: {event.kind}")
    if state is None:
        raise ValueError("empty history")
    return state


class DurableWorkflow:
    FORWARD = ("forward.reserve", "forward.charge", "forward.ship")
    COMPENSATIONS = (("forward.charge", "compensate.refund"), ("forward.reserve", "compensate.release"))

    def __init__(self, store: WorkflowStore, receiver: IdempotentReceiver):
        self.store = store
        self.receiver = receiver

    def state(self, run_id: str) -> WorkflowState:
        return replay(self.store.history(run_id))

    def advance(self, run_id: str) -> WorkflowState:
        """Leitet exakt den nächsten Command deterministisch aus der History ab."""
        state = self.state(run_id)
        if state.terminal or self.store.pending(run_id):
            return state
        payload = {"order_id": state.order_id, "amount": state.amount}

        if state.failed:
            for prerequisite, compensation in self.COMPENSATIONS:
                if prerequisite in state.completed and compensation not in state.completed:
                    if compensation not in state.scheduled:
                        self.store.schedule(run_id, compensation, payload)
                    return self.state(run_id)
            self.store.append(run_id, "WorkflowCompensated", {})
            return self.state(run_id)

        for operation in self.FORWARD:
            if operation not in state.completed:
                if operation not in state.scheduled:
                    operation_payload = dict(payload)
                    if operation == "forward.ship":
                        operation_payload["fail_shipping"] = state.fail_shipping
                    self.store.schedule(run_id, operation, operation_payload)
                return self.state(run_id)
        self.store.append(run_id, "WorkflowCompleted", {})
        return self.state(run_id)

    def dispatch_one(self, run_id: str, crash_at: str | None = None) -> bool:
        rows = self.store.pending(run_id)
        if not rows:
            return False
        row = rows[0]
        if crash_at == "before_effect":
            raise CrashInjected("before receiver effect")
        ok, result, deduplicated = self.receiver.execute(
            row["operation"], row["idempotency_key"], json.loads(row["payload"])
        )
        if crash_at == "after_effect_before_ack":
            raise CrashInjected("receiver committed; workflow has not acknowledged")
        self.store.acknowledge(row, ok=ok, result=result, deduplicated=deduplicated)
        if crash_at == "after_local_commit":
            raise CrashInjected("workflow result committed; caller did not observe acknowledgement")
        return True

    def run_until_terminal(self, run_id: str, max_iterations: int = 100) -> WorkflowState:
        for _ in range(max_iterations):
            state = self.advance(run_id)
            if state.terminal:
                return state
            self.dispatch_one(run_id)
        raise RuntimeError("iteration limit reached")
