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
        self.kolibri_pid = Path(r"C:\LLMs\logs\kolibri.pid")
        self.script = workspace / "local-models" / "ministral" / "python" / "start_mistral.py"
        self.kolibri_script = workspace / "local-models" / "kolibri" / "python" / "start_kolibri.py"

    @staticmethod
    def _health() -> bool:
        request = urllib.request.Request("http://127.0.0.1:8081/health", method="GET")
        try:
            with urllib.request.urlopen(request, timeout=2) as response:
                return response.status == 200
        except (OSError, urllib.error.URLError):
            return False

    @staticmethod
    def _kolibri_health() -> bool:
        request = urllib.request.Request("http://127.0.0.1:8082/health", method="GET")
        try:
            with urllib.request.urlopen(request, timeout=2) as response:
                return response.status == 200
        except (OSError, urllib.error.URLError):
            return False

    def status(self, runtime_id: str = "local-ministral") -> dict:
        if runtime_id == "local-ministral":
            state_path = self.state_dir / f"{runtime_id}.json"
            state = json.loads(state_path.read_text(encoding="utf-8")) if state_path.is_file() else {}
            pid = int(self.external_pid.read_text(encoding="ascii").strip()) if self.external_pid.is_file() else None
            return {"runtime": runtime_id, "healthy": self._health(), "pid": pid, "owned": bool(state.get("owned") and state.get("pid") == pid)}
        elif runtime_id == "local-kolibri":
            state_path = self.state_dir / f"{runtime_id}.json"
            state = json.loads(state_path.read_text(encoding="utf-8")) if state_path.is_file() else {}
            pid = int(self.kolibri_pid.read_text(encoding="ascii").strip()) if self.kolibri_pid.is_file() else None
            return {"runtime": runtime_id, "healthy": self._kolibri_health(), "pid": pid, "owned": bool(state.get("owned") and state.get("pid") == pid)}
        else:
            raise ValueError(f"unknown runtime: {runtime_id}")

    def start(self, runtime_id: str = "local-ministral", timeout: int = 60) -> dict:
        current = self.status(runtime_id)
        if current["healthy"]:
            return {**current, "action": "already-running"}
        
        if runtime_id == "local-ministral":
            if not self.script.is_file():
                raise RuntimeError(f"runtime script missing: {self.script}")
            script = self.script
            health_check = self._health
            pid_file = self.external_pid
        elif runtime_id == "local-kolibri":
            if not self.kolibri_script.is_file():
                raise RuntimeError(f"runtime script missing: {self.kolibri_script}")
            script = self.kolibri_script
            health_check = self._kolibri_health
            pid_file = self.kolibri_pid
        else:
            raise ValueError(f"unknown runtime: {runtime_id}")
        
        process = subprocess.run([sys.executable, str(script), "--background"], cwd=script.parent,
                                 capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=30)
        if process.returncode:
            raise RuntimeError(process.stderr.strip() or process.stdout.strip())
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline and not health_check():
            time.sleep(0.5)
        if not health_check():
            raise RuntimeError(f"{runtime_id} runtime did not become healthy")
        pid = int(pid_file.read_text(encoding="ascii").strip())
        state = {"owned": True, "pid": pid, "started_by": os.getpid()}
        (self.state_dir / f"{runtime_id}.json").write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")
        return {**self.status(runtime_id), "action": "started"}

    def stop(self, runtime_id: str = "local-ministral") -> dict:
        current = self.status(runtime_id)
        if not current["healthy"]:
            return {**current, "action": "already-stopped"}
        if not current["owned"]:
            raise RuntimeError("refusing to stop a runtime not started by this orchestrator")
        
        if runtime_id == "local-ministral":
            script = self.script
        elif runtime_id == "local-kolibri":
            script = self.kolibri_script
        else:
            raise ValueError(f"unknown runtime: {runtime_id}")
        
        process = subprocess.run([sys.executable, str(script), "--stop"], cwd=script.parent,
                                 capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=30)
        if process.returncode:
            raise RuntimeError(process.stderr.strip() or process.stdout.strip())
        (self.state_dir / f"{runtime_id}.json").unlink(missing_ok=True)
        return {**self.status(runtime_id), "action": "stopped"}
