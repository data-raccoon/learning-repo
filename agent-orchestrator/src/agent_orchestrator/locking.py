"""Cross-process advisory reader/writer locks for overlapping target trees."""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import threading
import time
import uuid


class LockTimeout(TimeoutError):
    pass


def _overlaps(first: Path, second: Path) -> bool:
    return first == second or first in second.parents or second in first.parents


class TargetLock:
    def __init__(self, lock_root: Path, target: Path, timeout: float = 30.0, mode: str = "write"):
        if mode not in {"read", "write"}:
            raise ValueError("lock mode must be read or write")
        self.lock_root = lock_root
        self.target = target.resolve()
        self.timeout = timeout
        self.mode = mode
        key = hashlib.sha256(str(self.target).casefold().encode("utf-8")).hexdigest()[:16]
        unique = f"{os.getpid()}-{threading.get_ident()}-{uuid.uuid4().hex[:8]}"
        self.path = lock_root / f"{key}-{unique}.lock"
        self.guard = lock_root / ".registry.guard"
        self.owned = False

    def _acquire_guard(self, deadline: float) -> None:
        while True:
            try:
                descriptor = os.open(self.guard, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
                os.close(descriptor)
                return
            except FileExistsError:
                try:
                    if time.time() - self.guard.stat().st_mtime > max(30.0, self.timeout):
                        self.guard.unlink(missing_ok=True)
                        continue
                except OSError:
                    pass
                if time.monotonic() >= deadline:
                    raise LockTimeout(f"lock registry is busy: {self.guard}")
                time.sleep(0.025)

    def _conflicts(self) -> bool:
        for path in self.lock_root.glob("*.lock"):
            try:
                row = json.loads(path.read_text(encoding="utf-8"))
                try:
                    os.kill(int(row["pid"]), 0)
                except PermissionError:
                    pass
                except (ProcessLookupError, ValueError):
                    path.unlink(missing_ok=True)
                    continue
                other = Path(row["target"])
                if _overlaps(self.target, other) and (self.mode == "write" or row.get("mode") == "write"):
                    return True
            except (OSError, KeyError, json.JSONDecodeError):
                try:
                    if time.time() - path.stat().st_mtime > max(30.0, self.timeout):
                        path.unlink(missing_ok=True)
                        continue
                except OSError:
                    continue
                return True
        return False

    def __enter__(self) -> "TargetLock":
        self.lock_root.mkdir(parents=True, exist_ok=True)
        deadline = time.monotonic() + self.timeout
        while True:
            self._acquire_guard(deadline)
            try:
                if not self._conflicts():
                    descriptor = os.open(self.path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
                    with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
                        json.dump({"pid": os.getpid(), "target": str(self.target), "mode": self.mode, "created": time.time()}, stream)
                    self.owned = True
                    return self
            finally:
                self.guard.unlink(missing_ok=True)
            if time.monotonic() >= deadline:
                raise LockTimeout(f"overlapping target is locked: {self.target}")
            time.sleep(0.1)

    def __exit__(self, *_: object) -> None:
        if self.owned:
            self.path.unlink(missing_ok=True)
            self.owned = False
