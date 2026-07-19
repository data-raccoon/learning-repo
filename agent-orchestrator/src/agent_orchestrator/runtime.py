"""Lifecycle management for registered local model servers."""

from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys
import time
import urllib.error
import urllib.request


class RuntimeManager:
    def __init__(self, workspace: Path, runtime_root: Path):
        self.workspace = workspace
        self.runtime_root = runtime_root
        self.state_dir = runtime_root / "runtimes"
        self.state_dir.mkdir(parents=True, exist_ok=True)
        self.external_pid = Path(r"C:\LLMs\logs\ministral.pid")
        self.script = workspace / "local-models" / "ministral" / "python" / "start_mistral.py"

    @staticmethod
    def _health() -> bool:
        request = urllib.request.Request("http://127.0.0.1:8081/health", method="GET")
        try:
            with urllib.request.urlopen(request, timeout=2) as response:
                return response.status == 200
        except (OSError, urllib.error.URLError):
            return False

    def status(self, runtime_id: str = "local-ministral") -> dict:
        if runtime_id != "local-ministral":
            raise ValueError(f"unknown runtime: {runtime_id}")
        state_path = self.state_dir / f"{runtime_id}.json"
        state = json.loads(state_path.read_text(encoding="utf-8")) if state_path.is_file() else {}
        pid = int(self.external_pid.read_text(encoding="ascii").strip()) if self.external_pid.is_file() else None
        return {"runtime": runtime_id, "healthy": self._health(), "pid": pid, "owned": bool(state.get("owned") and state.get("pid") == pid)}

    def start(self, runtime_id: str = "local-ministral", timeout: int = 60) -> dict:
        current = self.status(runtime_id)
        if current["healthy"]:
            return {**current, "action": "already-running"}
        if not self.script.is_file():
            raise RuntimeError(f"runtime script missing: {self.script}")
        process = subprocess.run([sys.executable, str(self.script), "--background"], cwd=self.script.parent,
                                 capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=30)
        if process.returncode:
            raise RuntimeError(process.stderr.strip() or process.stdout.strip())
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline and not self._health():
            time.sleep(0.5)
        if not self._health():
            raise RuntimeError("local runtime did not become healthy")
        pid = int(self.external_pid.read_text(encoding="ascii").strip())
        state = {"owned": True, "pid": pid, "started_by": os.getpid()}
        (self.state_dir / f"{runtime_id}.json").write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")
        return {**self.status(runtime_id), "action": "started"}

    def stop(self, runtime_id: str = "local-ministral") -> dict:
        current = self.status(runtime_id)
        if not current["healthy"]:
            return {**current, "action": "already-stopped"}
        if not current["owned"]:
            raise RuntimeError("refusing to stop a runtime not started by this orchestrator")
        process = subprocess.run([sys.executable, str(self.script), "--stop"], cwd=self.script.parent,
                                 capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=30)
        if process.returncode:
            raise RuntimeError(process.stderr.strip() or process.stdout.strip())
        (self.state_dir / f"{runtime_id}.json").unlink(missing_ok=True)
        return {**self.status(runtime_id), "action": "stopped"}
