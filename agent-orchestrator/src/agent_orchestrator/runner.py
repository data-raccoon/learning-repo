"""Transactional execution and independent acceptance gates."""

from __future__ import annotations

from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import threading
import time
import uuid
from typing import Any

from .adapters import GoogleAccountCliAdapter, LocalChatAdapter, VibeAdapter
from .contracts import ContractError, Job
from .evidence import RunEvidence, artifact_records, utc_now
from .locking import TargetLock
from .paths import validate_job_paths
from .registry import Registry
from .routing import RoutingError, route_job
from .runtime import RuntimeManager
from .snapshot import TargetSnapshot


SAFE_VERIFIER_EXECUTABLES = {"python", "python.exe", "py", "py.exe", "node", "node.exe", "npm", "npm.cmd", "git", "git.exe"}


def _run_id(job_id: str) -> str:
    safe = re.sub(r"[^a-zA-Z0-9_.-]+", "-", job_id).strip("-")[:50] or "job"
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S")
    return f"{stamp}-{safe}-{uuid.uuid4().hex[:8]}"


class JobRunner:
    def __init__(self, workspace: Path, orchestrator_root: Path, registry: Registry, adapters: dict[str, Any] | None = None):
        self.workspace = workspace.resolve()
        self.orchestrator_root = orchestrator_root.resolve()
        self.runtime_root = self.orchestrator_root / ".runtime"
        self.runtime_root.mkdir(parents=True, exist_ok=True)
        self.registry = registry
        self.runtime = RuntimeManager(self.workspace, self.runtime_root)
        self.adapters = adapters or {
            "openai-chat": LocalChatAdapter(),
            "vibe": VibeAdapter(self.workspace),
            "antigravity-cli": GoogleAccountCliAdapter(),
        }
        local_slot = threading.BoundedSemaphore(1)
        google_slot = threading.BoundedSemaphore(1)
        self._semaphores: dict[str, threading.BoundedSemaphore] = {
            item.id: (
                local_slot if registry.models[item.model].provider == "local-ministral"
                else google_slot if registry.models[item.model].provider == "gemini-google-account"
                else threading.BoundedSemaphore(item.max_parallel)
            )
            for item in registry.profiles.values()
        }

    @staticmethod
    def _cost(model: Any, provider: Any, usage: dict[str, int | float]) -> dict[str, Any]:
        if provider.billing in ("free-account-quota", "free-vscode-extension"):
            return {
                "kind": "free-quota",
                "amount_usd": 0.0,
                "marginal_amount_usd": 0.0,
                "plan": provider.plan,
                "quota_based": True,
            }
        if provider.billing == "included-subscription":
            return {
                "kind": "included-subscription",
                "amount_usd": None,
                "marginal_amount_usd": 0.0,
                "plan": provider.plan,
                "fixed_subscription_cost_allocated": False,
            }
        if provider.billing == "local-compute":
            return {
                "kind": "local-compute",
                "amount_usd": None,
                "marginal_amount_usd": None,
                "note": "energy and hardware costs are not allocated per run",
            }
        if provider.billing != "metered-api":
            return {"kind": "unknown-billing", "amount_usd": None, "billing": provider.billing}
        if not any(key in usage for key in ("prompt_tokens", "input_tokens", "completion_tokens", "output_tokens")):
            return {"kind": "unavailable", "amount_usd": None}
        prompt = usage.get("prompt_tokens", usage.get("input_tokens", 0)) or 0
        completion = usage.get("completion_tokens", usage.get("output_tokens", 0)) or 0
        if model.input_cost_per_million is None or model.input_cost_per_million < 0:
            return {"kind": "unknown", "amount_usd": None}
        amount = (float(prompt) * model.input_cost_per_million + float(completion) * model.output_cost_per_million) / 1_000_000
        return {"kind": "estimated-token-cost", "amount_usd": round(amount, 8)}

    @staticmethod
    def _validate_output_schema(text: str, schema_path: Path) -> dict[str, Any]:
        try:
            value = json.loads(text)
            schema = json.loads(schema_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError) as error:
            return {"ok": False, "error": f"invalid JSON output or schema: {error}"}
        if schema.get("type") == "object":
            if not isinstance(value, dict):
                return {"ok": False, "error": "output is not an object"}
            missing = [name for name in schema.get("required", []) if name not in value]
            if missing:
                return {"ok": False, "error": "missing required properties: " + ", ".join(missing)}
            properties = schema.get("properties", {})
            if schema.get("additionalProperties") is False:
                extra = sorted(set(value) - set(properties))
                if extra:
                    return {"ok": False, "error": "unexpected properties: " + ", ".join(extra)}
            python_types = {"string": str, "integer": int, "number": (int, float), "boolean": bool, "array": list, "object": dict}
            for name, definition in properties.items():
                expected = python_types.get(definition.get("type"))
                if name in value and expected and (not isinstance(value[name], expected) or definition.get("type") == "integer" and isinstance(value[name], bool)):
                    return {"ok": False, "error": f"property {name} has the wrong type"}
        return {"ok": True}

    @staticmethod
    def _ownership_gate(changes: dict[str, list[str]], allowed_paths: tuple[str, ...]) -> dict[str, Any]:
        if not allowed_paths:
            return {"ok": True, "skipped": True}
        normalized = tuple(value.rstrip("/") for value in allowed_paths)
        touched = changes["added"] + changes["removed"] + changes["changed"]
        violations = sorted(
            name for name in touched
            if not any(name == allowed or name.startswith(allowed + "/") for allowed in normalized)
        )
        return {"ok": not violations, "allowed_paths": list(allowed_paths), "violations": violations}

    def _verify(self, job: Job, target: Path, evidence: RunEvidence) -> list[dict[str, Any]]:
        results = []
        secret_names = {"OPENAI_API_KEY", "CODEX_API_KEY", "MISTRAL_API_KEY", "LOCAL_LLM_API_KEY"}
        environment = {key: value for key, value in os.environ.items() if key not in secret_names}
        environment["PYTHONDONTWRITEBYTECODE"] = "1"
        for verifier in job.verifiers:
            argv = [sys.executable if item == "{python}" else item for item in verifier.argv]
            executable = Path(argv[0]).name.casefold()
            if executable not in SAFE_VERIFIER_EXECUTABLES:
                results.append({"id": verifier.id, "ok": False, "error": f"verifier executable is not allowlisted: {executable}"})
                continue
            process = subprocess.run(argv, cwd=target, env=environment, capture_output=True, text=True,
                                     encoding="utf-8", errors="replace", timeout=verifier.timeout_seconds, shell=False)
            evidence.write_text(f"verifier-{re.sub(r'[^a-zA-Z0-9_.-]', '-', verifier.id)}.log", process.stdout + process.stderr)
            results.append({"id": verifier.id, "ok": process.returncode == 0, "exit_code": process.returncode})
        return results

    def run(self, job: Job, *, allow_candidate: bool = False) -> dict[str, Any]:
        run_id = _run_id(job.id)
        evidence = RunEvidence(self.runtime_root, run_id)
        started = time.monotonic()
        summary: dict[str, Any] = {"run_id": run_id, "job": job.id, "status": "failed", "started_at": utc_now()}
        snapshot: TargetSnapshot | None = None
        target: Path | None = None
        try:
            target = validate_job_paths(self.workspace, job)
            route = route_job(self.registry, job, allow_candidate=allow_candidate)
            summary["route"] = {key: value for key, value in route.items() if key != "considered"}
            evidence.event("job.routed", route=route)
            profile = self.registry.profiles[route["selected_profile"]]
            model = self.registry.models[profile.model]
            provider = self.registry.providers[model.provider]
            harness = self.registry.harnesses[profile.harness]
            adapter = self.adapters.get(harness.kind)
            if adapter is None:
                raise RuntimeError(f"no adapter for harness kind {harness.kind}")
            lock_timeout = min(30, job.limits.timeout_seconds)
            with TargetLock(self.runtime_root / "locks", target, lock_timeout, mode=job.mode):
                if job.mode == "write":
                    snapshot = TargetSnapshot(target, evidence.run_dir)
                    snapshot.capture()
                    evidence.event("snapshot.captured")
                with self._semaphores[profile.id]:
                    if model.provider == "local-ministral":
                        runtime_state = self.runtime.start()
                        evidence.event("runtime.ready", state=runtime_state)
                    evidence.event("worker.started", profile=profile.id)
                    result = adapter.run(job, target, model, profile)
                evidence.write_text("trajectory.txt", result.trajectory)
                evidence.write_text("final-message.txt", result.final_text)
                if not result.ok:
                    raise RuntimeError(result.error or "worker failed")
                artifacts = artifact_records(target, job.expected_artifacts)
                artifact_gate = all(not item.get("missing") for item in artifacts)
                verifiers = self._verify(job, target, evidence)
                schema_gate = self._validate_output_schema(result.final_text, target / job.output_schema) if job.output_schema else {"ok": True, "skipped": True}
                changes = snapshot.changes() if snapshot else {"added": [], "removed": [], "changed": []}
                ownership_gate = self._ownership_gate(changes, job.allowed_write_paths)
                gates_ok = artifact_gate and schema_gate["ok"] and ownership_gate["ok"] and all(item["ok"] for item in verifiers)
                summary.update({
                    "artifacts": artifacts,
                    "gates": {
                        "artifacts": artifact_gate,
                        "output_schema": schema_gate,
                        "ownership": ownership_gate,
                        "verifiers": verifiers,
                    },
                    "usage": result.usage,
                    "cost": self._cost(model, provider, result.usage),
                })
                if snapshot:
                    summary["changes"] = changes
                if not gates_ok:
                    raise RuntimeError("independent acceptance gates failed")
                if snapshot:
                    snapshot.discard()
                summary["status"] = "passed"
                evidence.event("job.passed")
        except RoutingError as error:
            summary["error"] = str(error.args[0])
            if len(error.args) > 1:
                summary["routing_considered"] = error.args[1]
            evidence.event("job.failed", error=summary["error"])
        except (ContractError, Exception) as error:
            summary["error"] = f"{type(error).__name__}: {error}"
            evidence.event("job.failed", error=summary["error"])
        finally:
            if summary["status"] != "passed" and snapshot is not None:
                try:
                    quarantine = snapshot.quarantine()
                    snapshot.restore()
                    snapshot.discard()
                    summary["quarantine"] = str(quarantine.relative_to(self.orchestrator_root))
                    summary["rolled_back"] = True
                    evidence.event("job.rolled_back", quarantine=summary["quarantine"])
                except Exception as rollback_error:
                    summary["rollback_error"] = f"{type(rollback_error).__name__}: {rollback_error}"
            summary["duration_seconds"] = round(time.monotonic() - started, 3)
            summary["finished_at"] = utc_now()
            evidence.finish(summary)
        return summary
