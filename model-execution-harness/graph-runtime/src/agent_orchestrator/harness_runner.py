"""Deterministic execution for bounded harness specifications."""

from __future__ import annotations

from concurrent.futures import FIRST_COMPLETED, Future, ThreadPoolExecutor, wait
from dataclasses import replace
from datetime import datetime, timezone
import hashlib
import json
import math
import os
from pathlib import Path
import re
import subprocess
import sys
import time
import uuid
from typing import Any

from .contracts import ContractError, Job, Verifier
from .evidence import sha256_file, utc_now
from .harness_contracts import ArtifactContract, Handoff, HarnessNode, HarnessSpec
from .paths import contained_path, validate_job_paths
from .routing import route_job
from .runner import JobRunner
from .snapshot import TargetSnapshot


def _safe_id(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.-]+", "-", value).strip("-")[:50] or "harness"


def _run_id(identifier: str) -> str:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S")
    return f"{stamp}-{_safe_id(identifier)}-{uuid.uuid4().hex[:8]}"


def _job_hash(job: Job) -> str:
    payload = json.dumps(job.to_dict(), sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _usage_tokens(summary: dict[str, Any]) -> int | None:
    usage = summary.get("usage")
    if not isinstance(usage, dict) or not usage:
        return None
    total = usage.get("total_tokens")
    if isinstance(total, (int, float)) and not isinstance(total, bool) and math.isfinite(total) and total >= 0:
        return int(total)
    prompt = usage.get("prompt_tokens", usage.get("input_tokens"))
    completion = usage.get("completion_tokens", usage.get("output_tokens"))
    if (
        not isinstance(prompt, (int, float)) or isinstance(prompt, bool)
        or not isinstance(completion, (int, float)) or isinstance(completion, bool)
        or not math.isfinite(prompt) or not math.isfinite(completion) or prompt < 0 or completion < 0
    ):
        return None
    return int(prompt + completion)


def _cost_amount(summary: dict[str, Any]) -> float | None:
    cost = summary.get("cost")
    if not isinstance(cost, dict):
        return None
    value = cost.get("marginal_amount_usd", cost.get("amount_usd"))
    if not isinstance(value, (int, float)) or isinstance(value, bool) or not math.isfinite(value) or value < 0:
        return None
    return float(value)


class HarnessEvidence:
    def __init__(self, runtime_root: Path, run_id: str):
        self.run_dir = runtime_root / "harness-runs" / run_id
        self.run_dir.mkdir(parents=True, exist_ok=False)
        self.events_path = self.run_dir / "events.jsonl"

    def event(self, event_type: str, **values: Any) -> None:
        with self.events_path.open("a", encoding="utf-8") as stream:
            stream.write(json.dumps({"at": utc_now(), "type": event_type, **values}, ensure_ascii=False) + "\n")

    def write_json(self, name: str, value: Any) -> None:
        (self.run_dir / name).write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def _route_details(spec: HarnessSpec, workspace: Path, runner: JobRunner) -> dict[str, dict[str, Any]]:
    routes: dict[str, dict[str, Any]] = {}
    for node in spec.nodes:
        generated_context = {
            artifact.path for handoff in spec.handoffs if handoff.to_node == node.id
            for artifact in handoff.artifacts
        }
        validation_job = replace(node.job, context=tuple(item for item in node.job.context if item not in generated_context))
        validate_job_paths(workspace, validation_job)
        route = route_job(runner.registry, node.job)
        routes[node.id] = {key: value for key, value in route.items() if key != "considered"}
    return routes


def _measurable_cost(runner: JobRunner, route: dict[str, Any]) -> bool:
    provider = runner.registry.providers[route["provider"]]
    if provider.usage_reporting != "measured":
        return False
    if provider.billing in {"free-account-quota", "included-subscription"}:
        return True
    if provider.billing != "metered-api":
        return False
    model = runner.registry.models[route["model"]]
    prices = (model.input_cost_per_million, model.output_cost_per_million)
    if any(value is None or value < 0 for value in prices):
        return False
    return True


def _canonical_write_scopes(spec: HarnessSpec, workspace: Path) -> None:
    dependencies = {node.id: set(node.job.dependencies) for node in spec.nodes}

    def ancestors(node_id: str) -> set[str]:
        found: set[str] = set()
        pending = list(dependencies[node_id])
        while pending:
            item = pending.pop()
            if item not in found:
                found.add(item)
                pending.extend(dependencies[item])
        return found

    scopes: dict[str, list[Path]] = {}
    for node in spec.nodes:
        if node.job.mode != "write":
            continue
        target = contained_path(workspace, node.job.target_dir, must_exist=True)
        scopes[node.id] = [contained_path(target, item) for item in node.job.allowed_write_paths]
    for index, first in enumerate(spec.nodes):
        for second in spec.nodes[index + 1:]:
            if first.id not in scopes or second.id not in scopes:
                continue
            if first.id in ancestors(second.id) or second.id in ancestors(first.id):
                continue
            for left in scopes[first.id]:
                for right in scopes[second.id]:
                    if left == right or left in right.parents or right in left.parents:
                        raise ContractError(
                            f"parallel write nodes {first.id} and {second.id} have overlapping canonical ownership"
                        )


def _policy_hashes(spec: HarnessSpec, workspace: Path) -> dict[str, str]:
    records: dict[str, str] = {}
    for node in spec.nodes:
        target = contained_path(workspace, node.job.target_dir, must_exist=True)
        if node.job.output_schema:
            path = contained_path(target, node.job.output_schema, must_exist=True)
            records[f"{node.id}:output-schema:{node.job.output_schema}"] = sha256_file(path)
        for verifier in node.job.verifiers:
            if len(verifier.argv) == 2 and verifier.argv[0] == "{python}":
                path = contained_path(target, verifier.argv[1], must_exist=True)
                records[f"{node.id}:job-verifier:{verifier.argv[1]}"] = sha256_file(path)
        selector = node.fan_in.verifier
        if selector and len(selector.argv) == 2 and selector.argv[0] == "{python}":
            path = contained_path(target, selector.argv[1], must_exist=True)
            records[f"{node.id}:selector:{selector.argv[1]}"] = sha256_file(path)
    for handoff in spec.handoffs:
        target = contained_path(workspace, spec.by_id[handoff.from_node].job.target_dir, must_exist=True)
        for artifact in handoff.artifacts:
            if artifact.schema:
                path = contained_path(target, artifact.schema, must_exist=True)
                records[f"{handoff.from_node}:artifact-schema:{artifact.schema}"] = sha256_file(path)
    return records


def resolve_harness(spec: HarnessSpec, workspace: Path, runner: JobRunner) -> dict[str, Any]:
    """Resolve paths and routes without creating evidence or invoking an adapter."""
    routes = _route_details(spec, workspace, runner)
    _canonical_write_scopes(spec, workspace)
    for handoff in spec.handoffs:
        producer = spec.by_id[handoff.from_node].job
        target = contained_path(workspace, producer.target_dir, must_exist=True)
        for artifact in handoff.artifacts:
            if artifact.schema:
                contained_path(target, artifact.schema, must_exist=True)
    if spec.limits.cost_enforcement == "strict":
        if spec.limits.max_tokens is not None:
            missing = [
                node.id for node in spec.nodes
                if runner.registry.providers[routes[node.id]["provider"]].usage_reporting != "measured"
            ]
            if missing:
                raise ContractError("strict token budget requires measured usage for nodes: " + ", ".join(missing))
        if spec.limits.max_cost_usd is not None:
            missing = [node.id for node in spec.nodes if not _measurable_cost(runner, routes[node.id])]
            if missing:
                raise ContractError("strict cost budget cannot be computed for nodes: " + ", ".join(missing))
    return {
        "status": "valid",
        "harness": spec.id,
        "topology": spec.topology,
        "manifest_hash": spec.digest(),
        "node_order": [node.id for node in spec.nodes],
        "routes": routes,
        "policy_hashes": _policy_hashes(spec, workspace),
        "limits": spec.normalized()["limits"],
    }


def _validate_json_schema(value: Any, schema: dict[str, Any], location: str = "artifact") -> str:
    declared = schema.get("type")
    python_types: dict[str, Any] = {
        "string": str, "integer": int, "number": (int, float), "boolean": bool,
        "array": list, "object": dict, "null": type(None),
    }
    expected = python_types.get(declared)
    if declared is not None and expected is None:
        return f"{location} schema has unsupported type {declared}"
    if expected and (
        not isinstance(value, expected)
        or declared in {"integer", "number"} and isinstance(value, bool)
    ):
        return f"{location} has the wrong type"
    if "enum" in schema and value not in schema["enum"]:
        return f"{location} is not one of the allowed values"
    if declared == "object":
        properties = schema.get("properties", {})
        required = schema.get("required", [])
        if not isinstance(properties, dict) or not isinstance(required, list):
            return f"{location} schema has invalid object constraints"
        missing = [name for name in required if name not in value]
        if missing:
            return "missing required properties: " + ", ".join(missing)
        if schema.get("additionalProperties") is False:
            extra = sorted(set(value) - set(properties))
            if extra:
                return "unexpected properties: " + ", ".join(extra)
        for name, definition in properties.items():
            if name in value:
                if not isinstance(definition, dict):
                    return f"property {name} schema must be an object"
                error = _validate_json_schema(value[name], definition, f"property {name}")
                if error:
                    return error
    if declared == "array" and "items" in schema:
        item_schema = schema["items"]
        if not isinstance(item_schema, dict):
            return f"{location} items schema must be an object"
        for index, item in enumerate(value):
            error = _validate_json_schema(item, item_schema, f"{location}[{index}]")
            if error:
                return error
    return ""


def _artifact_record(target: Path, contract: ArtifactContract) -> dict[str, Any]:
    path = contained_path(target, contract.path, must_exist=True)
    if not path.is_file():
        return {"path": contract.path, "ok": False, "error": "artifact is not a file"}
    digest = sha256_file(path)
    record: dict[str, Any] = {
        "path": contract.path, "media_type": contract.media_type,
        "bytes": path.stat().st_size, "sha256": digest, "ok": True,
    }
    if contract.sha256 and digest != contract.sha256:
        record.update(ok=False, error="artifact hash does not match pinned sha256")
        return record
    try:
        if contract.media_type == "application/json":
            value = json.loads(path.read_text(encoding="utf-8"))
            if contract.schema:
                schema_path = contained_path(target, contract.schema, must_exist=True)
                schema = json.loads(schema_path.read_text(encoding="utf-8"))
                error = _validate_json_schema(value, schema)
                if error:
                    record.update(ok=False, error=error)
        elif contract.media_type == "text/plain":
            path.read_text(encoding="utf-8")
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        record.update(ok=False, error=f"artifact validation failed: {error}")
    return record


def _outgoing_gate(spec: HarnessSpec, node: HarnessNode, workspace: Path):
    contracts = [
        artifact for handoff in spec.handoffs if handoff.from_node == node.id
        for artifact in handoff.artifacts
    ]

    def gate(target: Path) -> dict[str, Any]:
        records = [_artifact_record(target, item) for item in contracts]
        return {"ok": all(item["ok"] for item in records), "artifacts": records}

    return gate if contracts else None


def _node_gate(spec: HarnessSpec, node: HarnessNode, selected: set[str],
               recorded: dict[tuple[str, str], dict[str, Any]], workspace: Path):
    outgoing = _outgoing_gate(spec, node, workspace)

    def gate(target: Path) -> dict[str, Any]:
        outgoing_result = outgoing(target) if outgoing else {"ok": True, "artifacts": []}
        immutable, error = _verify_immutable_handoffs(spec, node, selected, recorded, workspace)
        return {
            "ok": outgoing_result["ok"] and immutable,
            "artifacts": outgoing_result["artifacts"],
            "consumed_artifacts_unchanged": immutable,
            **({"error": error} if error else {}),
        }

    return gate


def _required_handoffs(spec: HarnessSpec, node_id: str, selected: set[str]) -> list[Handoff]:
    return [item for item in spec.handoffs if item.to_node == node_id and item.from_node in selected]


def _effective_job(spec: HarnessSpec, node: HarnessNode, selected: set[str]) -> Job:
    incoming = [item for item in spec.handoffs if item.to_node == node.id]
    generated = {artifact.path for handoff in incoming for artifact in handoff.artifacts}
    selected_paths = {
        artifact.path for handoff in incoming if handoff.from_node in selected
        for artifact in handoff.artifacts
    }
    context = tuple(item for item in node.job.context if item not in generated or item in selected_paths)
    return replace(node.job, context=context)


def _verify_immutable_handoffs(spec: HarnessSpec, node: HarnessNode, selected: set[str],
                               records: dict[tuple[str, str], dict[str, Any]], workspace: Path) -> tuple[bool, str]:
    target = contained_path(workspace, node.job.target_dir, must_exist=True)
    for handoff in _required_handoffs(spec, node.id, selected):
        for contract in handoff.artifacts:
            previous = records.get((handoff.from_node, contract.path))
            if not previous:
                return False, f"missing recorded handoff {handoff.from_node}:{contract.path}"
            current = _artifact_record(target, contract)
            if not current["ok"] or current.get("sha256") != previous.get("sha256"):
                return False, f"immutable handoff changed: {contract.path}"
    return True, ""


def _selector(spec: HarnessSpec, node: HarnessNode, passed: list[str], workspace: Path,
              evidence: HarnessEvidence) -> str:
    verifier = node.fan_in.verifier
    if verifier is None:
        raise ContractError("selector verifier is missing")
    target = validate_job_paths(workspace, node.job)
    if len(verifier.argv) != 2 or verifier.argv[0] != "{python}" or not verifier.argv[1].endswith(".py"):
        raise ContractError("selector verifier must be {python} plus one contained target-relative .py file")
    script = contained_path(target, verifier.argv[1], must_exist=True)
    if not script.is_file():
        raise ContractError("selector verifier script must be a file")
    argv = [sys.executable, str(script)]
    candidates_path = evidence.run_dir / f"selector-{_safe_id(node.id)}-candidates.json"
    candidates_path.write_text(json.dumps({"candidates": passed}, indent=2) + "\n", encoding="utf-8")
    environment = {
        key: os.environ[key] for key in ("SYSTEMROOT", "PATH", "PATHEXT", "TEMP", "TMP")
        if key in os.environ
    }
    environment["HARNESS_CANDIDATES_FILE"] = str(candidates_path)
    environment.update({"PYTHONIOENCODING": "utf-8", "PYTHONUTF8": "1", "PYTHONDONTWRITEBYTECODE": "1"})
    snapshot = TargetSnapshot(target, evidence.run_dir)
    snapshot.capture()
    try:
        try:
            process = subprocess.run(
                argv, cwd=target, env=environment, capture_output=True, text=True,
                encoding="utf-8", errors="replace", timeout=verifier.timeout_seconds, shell=False,
            )
        except (OSError, subprocess.TimeoutExpired) as error:
            snapshot.restore()
            raise ContractError(f"selector verifier failed safely: {error}") from error
        changes = snapshot.changes()
        if any(changes.values()):
            snapshot.restore()
            raise ContractError("selector verifier modified its target")
    finally:
        snapshot.discard()
    evidence.event("fan_in.selector", node=node.id, argv_sha256=hashlib.sha256("\0".join(argv).encode()).hexdigest(),
                   exit_code=process.returncode)
    if process.returncode:
        raise ContractError(f"selector verifier exited {process.returncode}")
    try:
        selected = json.loads(process.stdout).get("selected_node")
    except (json.JSONDecodeError, AttributeError) as error:
        raise ContractError(f"selector verifier returned invalid JSON: {error}") from error
    if selected not in passed:
        raise ContractError("selector verifier did not choose a passed dependency")
    evidence.write_json(f"selector-{_safe_id(node.id)}-result.json", {
        "selected_node": selected,
        "stdout": process.stdout[:10_000],
        "stderr": process.stderr[:10_000],
    })
    return selected


def _resume_nodes(spec: HarnessSpec, previous: dict[str, Any] | None, routes: dict[str, dict[str, Any]],
                  workspace: Path) -> tuple[set[str], dict[tuple[str, str], dict[str, Any]]]:
    if not previous or previous.get("manifest_hash") != spec.digest():
        return set(), {}
    old_nodes = previous.get("nodes", {})
    reusable: set[str] = set()
    records: dict[tuple[str, str], dict[str, Any]] = {}
    for node in spec.nodes:
        old = old_nodes.get(node.id, {})
        if old.get("status") != "passed" or old.get("job_hash") != _job_hash(node.job) or old.get("route") != routes[node.id]:
            continue
        if any(dependency not in reusable for dependency in node.job.dependencies):
            continue
        target = validate_job_paths(workspace, node.job)
        artifacts_by_path = {
            item["path"]: item
            for item in [*old.get("output_artifacts", []), *old.get("artifact_contracts", [])]
            if isinstance(item, dict) and item.get("path")
        }
        artifacts = list(artifacts_by_path.values())
        if not all(
            not item.get("missing") and item.get("sha256") and item.get("ok", True)
            and (target / item["path"]).is_file()
            and sha256_file(target / item["path"]) == item.get("sha256")
            for item in artifacts
        ):
            continue
        reusable.add(node.id)
        for item in artifacts:
            records[(node.id, item["path"])] = item
    return reusable, records


class HarnessRunner:
    def __init__(self, workspace: Path, runner: JobRunner):
        self.workspace = workspace.resolve()
        self.runner = runner

    def run(self, spec: HarnessSpec, *, dry_run: bool = False, resume: str = "") -> dict[str, Any]:
        resolved = resolve_harness(spec, self.workspace, self.runner)
        if dry_run:
            return {**resolved, "dry_run": True}
        previous = None
        if resume:
            if not re.fullmatch(r"[A-Za-z0-9_.-]+", resume):
                raise ContractError("invalid resume run id")
            path = self.runner.runtime_root / "harness-runs" / resume / "summary.json"
            try:
                previous = json.loads(path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError) as error:
                raise ContractError(f"cannot read resume evidence: {error}") from error
        run_id = _run_id(spec.id)
        evidence = HarnessEvidence(self.runner.runtime_root, run_id)
        normalized = spec.normalized()
        evidence.write_json("normalized-manifest.json", normalized)
        evidence.event("harness.started", harness=spec.id, manifest_hash=spec.digest(), resumed_from=resume or None)
        if previous and previous.get("policy_hashes") != resolved["policy_hashes"]:
            evidence.event("resume.invalidated", reason="policy hashes changed")
            previous = None
        try:
            if spec.topology == "repair":
                summary = self._run_repair(spec, resolved, evidence, previous)
            else:
                summary = self._run_dag(spec, resolved, evidence, previous)
        except Exception as error:
            summary = {
                "status": "failed", "nodes": {},
                "error": f"harness exception: {type(error).__name__}: {error}",
                "finished_at": utc_now(),
            }
        summary.update({
            "run_id": run_id, "harness": spec.id, "topology": spec.topology,
            "manifest_hash": spec.digest(), "policy_hashes": resolved["policy_hashes"],
            "resumed_from": resume or None,
        })
        evidence.event("harness.finished", status=summary["status"])
        evidence.write_json("summary.json", summary)
        return summary

    def _run_dag(self, spec: HarnessSpec, resolved: dict[str, Any], evidence: HarnessEvidence,
                 previous: dict[str, Any] | None) -> dict[str, Any]:
        routes = resolved["routes"]
        reusable, artifact_records = _resume_nodes(spec, previous, routes, self.workspace)
        states = {node.id: ("passed" if node.id in reusable else "pending") for node in spec.nodes}
        nodes: dict[str, dict[str, Any]] = {}
        for node in spec.nodes:
            if node.id in reusable:
                nodes[node.id] = previous["nodes"][node.id]
                evidence.event("node.resumed", node=node.id)
            else:
                evidence.event("node.pending", node=node.id)
        attempts = {node.id: 0 for node in spec.nodes}
        selections: dict[str, set[str]] = {}
        running: dict[Future[dict[str, Any]], HarnessNode] = {}
        started = time.monotonic()
        used_tokens = 0
        used_cost = 0.0
        accounting_complete = True
        total_attempts = 0
        stop_reason = ""

        def dependency_state(node: HarnessNode) -> tuple[str, set[str]]:
            dependencies = list(node.job.dependencies)
            if not dependencies:
                return "ready", set()
            if any(states[item] in {"pending", "running"} for item in dependencies):
                return "waiting", set()
            passed = [item for item in dependencies if states[item] == "passed"]
            if node.fan_in.strategy == "all":
                return ("ready", set(passed)) if passed else ("skip", set())
            if not passed:
                return "skip", set()
            if node.fan_in.strategy == "first-passing":
                first = next(item for item in dependencies if item in passed)
                return "ready", {first}
            try:
                selected = _selector(spec, node, passed, self.workspace, evidence)
            except ContractError as error:
                nodes[node.id] = {"status": "failed", "error": str(error), "job_hash": _job_hash(node.job), "route": routes[node.id]}
                states[node.id] = "failed"
                evidence.event("node.failed", node=node.id, error=str(error))
                return "failed", set()
            return "ready", {selected}

        with ThreadPoolExecutor(max_workers=spec.limits.max_parallel, thread_name_prefix="harness-node") as pool:
            while any(value in {"pending", "running"} for value in states.values()):
                progressed = False
                for node in spec.nodes:
                    if states[node.id] != "pending":
                        continue
                    dependency_status, selected = dependency_state(node)
                    if dependency_status in {"waiting", "failed"}:
                        continue
                    if dependency_status == "skip":
                        states[node.id] = "skipped"
                        nodes[node.id] = {"status": "skipped", "job_hash": _job_hash(node.job), "route": routes[node.id]}
                        evidence.event("node.skipped", node=node.id)
                        progressed = True
                        continue
                    if len(running) >= spec.limits.max_parallel:
                        break
                    if time.monotonic() - started >= spec.limits.deadline_seconds:
                        stop_reason = "deadline"
                        break
                    if total_attempts >= spec.limits.max_attempts:
                        stop_reason = "max-attempts"
                        break
                    if spec.limits.max_tokens is not None and used_tokens >= spec.limits.max_tokens:
                        stop_reason = "max-tokens"
                        break
                    if spec.limits.max_cost_usd is not None and used_cost >= spec.limits.max_cost_usd:
                        stop_reason = "max-cost"
                        break
                    immutable, error = _verify_immutable_handoffs(spec, node, selected, artifact_records, self.workspace)
                    if not immutable:
                        states[node.id] = "failed"
                        nodes[node.id] = {"status": "failed", "error": error, "job_hash": _job_hash(node.job), "route": routes[node.id]}
                        evidence.event("node.failed", node=node.id, error=error)
                        progressed = True
                        continue
                    attempts[node.id] += 1
                    total_attempts += 1
                    selections[node.id] = selected
                    states[node.id] = "running"
                    evidence.event("node.started", node=node.id, attempt=attempts[node.id], selected_dependencies=sorted(selected))
                    execution_job = _effective_job(spec, node, selected)
                    future = pool.submit(
                        self.runner.run, execution_job,
                        acceptance_gate=_node_gate(spec, node, selected, artifact_records, self.workspace),
                    )
                    running[future] = node
                    progressed = True
                if stop_reason:
                    for node in spec.nodes:
                        if states[node.id] == "pending":
                            states[node.id] = "budget-stopped"
                            nodes[node.id] = {"status": "budget-stopped", "reason": stop_reason,
                                              "job_hash": _job_hash(node.job), "route": routes[node.id]}
                            evidence.event("node.budget_stopped", node=node.id, reason=stop_reason)
                if running:
                    completed, _ = wait(running, return_when=FIRST_COMPLETED)
                    for future in completed:
                        node = running.pop(future)
                        try:
                            result = future.result()
                        except Exception as error:
                            result = {"status": "failed", "error": f"runner exception: {type(error).__name__}: {error}"}
                        tokens = _usage_tokens(result)
                        cost = _cost_amount(result)
                        if tokens is None:
                            accounting_complete = False
                        else:
                            used_tokens += tokens
                        if cost is None:
                            accounting_complete = False
                        else:
                            used_cost += cost
                        accounting_errors = []
                        if spec.limits.cost_enforcement == "strict" and spec.limits.max_tokens is not None and tokens is None:
                            accounting_errors.append("strict token usage was not reported")
                        if spec.limits.cost_enforcement == "strict" and spec.limits.max_cost_usd is not None and cost is None:
                            accounting_errors.append("strict cost was not reported")
                        if accounting_errors and result.get("status") == "passed":
                            result = {**result, "status": "failed", "error": "; ".join(accounting_errors)}
                        node_summary = {
                            "status": result["status"], "job_hash": _job_hash(node.job), "route": routes[node.id],
                            "attempts": attempts[node.id], "child_run_ids": [result.get("run_id")],
                            "usage": result.get("usage", {}), "cost": result.get("cost", {}),
                            "selected_dependencies": sorted(selections.get(node.id, set())),
                            "output_artifacts": result.get("artifacts", []),
                            "artifact_contracts": result.get("gates", {}).get("harness", {}).get("artifacts", []),
                            "gates": result.get("gates", {}),
                        }
                        attempt_record = {
                            "attempt": attempts[node.id], "status": result["status"],
                            "child_run_id": result.get("run_id"), "usage": result.get("usage", {}),
                            "cost": result.get("cost", {}), "gates": result.get("gates", {}),
                        }
                        if result["status"] == "passed":
                            states[node.id] = "passed"
                            for item in node_summary["artifact_contracts"]:
                                artifact_records[(node.id, item["path"])] = item
                            evidence.event("node.passed", node=node.id, child_run_id=result.get("run_id"))
                        elif attempts[node.id] < node.max_attempts and total_attempts < spec.limits.max_attempts and not stop_reason:
                            states[node.id] = "pending"
                            node_summary["status"] = "pending"
                            evidence.event("node.retry", node=node.id, attempt=attempts[node.id])
                        else:
                            states[node.id] = "failed"
                            node_summary["error"] = result.get("error", "job failed")
                            evidence.event("node.failed", node=node.id, child_run_id=result.get("run_id"), error=node_summary["error"])
                        old = nodes.get(node.id)
                        if old and old.get("child_run_ids"):
                            node_summary["child_run_ids"] = old["child_run_ids"] + node_summary["child_run_ids"]
                        node_summary["attempt_results"] = (old.get("attempt_results", []) if old else []) + [attempt_record]
                        nodes[node.id] = node_summary
                    progressed = True
                elif not progressed and any(value == "pending" for value in states.values()):
                    raise RuntimeError("harness scheduler made no progress")
        status = "passed" if all(value == "passed" for value in states.values()) else "failed"
        return {
            "status": status, "nodes": nodes,
            "budget": {"attempts": total_attempts, "tokens": used_tokens, "cost_usd": round(used_cost, 8),
                       "accounting_complete": accounting_complete, "stop_reason": stop_reason or None},
            "duration_seconds": round(time.monotonic() - started, 3), "finished_at": utc_now(),
        }

    def _run_repair(self, spec: HarnessSpec, resolved: dict[str, Any], evidence: HarnessEvidence,
                    previous: dict[str, Any] | None) -> dict[str, Any]:
        loop = spec.repair_loop
        assert loop is not None
        by_id = spec.by_id
        routes = resolved["routes"]
        reusable, artifact_records = _resume_nodes(spec, previous, routes, self.workspace)
        nodes: dict[str, dict[str, Any]] = {
            node_id: previous["nodes"][node_id] for node_id in reusable
        } if previous else {}
        for node in spec.nodes:
            evidence.event("node.resumed" if node.id in reusable else "node.pending", node=node.id)
        total_attempts = 0
        started = time.monotonic()
        used_tokens = 0
        used_cost = 0.0
        accounting_complete = True
        stop_reason = ""

        if loop.work_node in reusable and loop.verify_node in reusable and (
            previous and previous.get("nodes", {}).get(loop.repair_node, {}).get("status") == "skipped"
            or loop.repair_node in reusable
        ):
            if previous and loop.repair_node not in nodes:
                nodes[loop.repair_node] = previous["nodes"][loop.repair_node]
            return {
                "status": "passed", "nodes": nodes,
                "budget": {"attempts": 0, "tokens": 0, "cost_usd": 0.0,
                           "accounting_complete": True, "stop_reason": None},
                "duration_seconds": 0.0, "finished_at": utc_now(),
            }

        def execute(node: HarnessNode, selected: set[str]) -> dict[str, Any]:
            nonlocal total_attempts, used_tokens, used_cost, accounting_complete, stop_reason
            if total_attempts >= spec.limits.max_attempts:
                stop_reason = "max-attempts"
            elif time.monotonic() - started >= spec.limits.deadline_seconds:
                stop_reason = "deadline"
            elif spec.limits.max_tokens is not None and used_tokens >= spec.limits.max_tokens:
                stop_reason = "max-tokens"
            else:
                if spec.limits.max_cost_usd is not None and used_cost >= spec.limits.max_cost_usd:
                    stop_reason = "max-cost"
            if stop_reason:
                result = {"status": "budget-stopped", "error": f"repair harness stopped at {stop_reason}"}
                nodes[node.id] = {
                    "status": "budget-stopped", "error": result["error"],
                    "job_hash": _job_hash(node.job), "route": routes[node.id],
                }
                evidence.event("node.budget_stopped", node=node.id, reason=stop_reason)
                return result
            immutable, error = _verify_immutable_handoffs(spec, node, selected, artifact_records, self.workspace)
            if not immutable:
                nodes[node.id] = {
                    "status": "failed", "error": error,
                    "job_hash": _job_hash(node.job), "route": routes[node.id],
                }
                evidence.event("node.failed", node=node.id, error=error)
                return {"status": "failed", "error": error}
            total_attempts += 1
            evidence.event("node.started", node=node.id, attempt=total_attempts)
            execution_job = _effective_job(spec, node, selected)
            try:
                result = self.runner.run(
                    execution_job,
                    acceptance_gate=_node_gate(spec, node, selected, artifact_records, self.workspace),
                )
            except Exception as error:
                result = {"status": "failed", "error": f"runner exception: {type(error).__name__}: {error}"}
            tokens = _usage_tokens(result)
            cost = _cost_amount(result)
            accounting_errors = []
            if spec.limits.cost_enforcement == "strict" and spec.limits.max_tokens is not None and tokens is None:
                accounting_errors.append("strict token usage was not reported")
            if spec.limits.cost_enforcement == "strict" and spec.limits.max_cost_usd is not None and cost is None:
                accounting_errors.append("strict cost was not reported")
            if accounting_errors and result.get("status") == "passed":
                result = {**result, "status": "failed", "error": "; ".join(accounting_errors)}
            evidence.event(f"node.{result['status']}", node=node.id, child_run_id=result.get("run_id"))
            summary = nodes.setdefault(node.id, {
                "job_hash": _job_hash(node.job), "route": routes[node.id], "attempts": 0,
                "child_run_ids": [], "artifact_contracts": [],
            })
            summary["attempts"] += 1
            summary["child_run_ids"].append(result.get("run_id"))
            summary["status"] = result["status"]
            summary["usage"] = result.get("usage", {})
            summary["cost"] = result.get("cost", {})
            summary["output_artifacts"] = result.get("artifacts", [])
            summary["artifact_contracts"] = result.get("gates", {}).get("harness", {}).get("artifacts", [])
            summary["gates"] = result.get("gates", {})
            summary.setdefault("attempt_results", []).append({
                "attempt": summary["attempts"], "status": result["status"],
                "child_run_id": result.get("run_id"), "usage": result.get("usage", {}),
                "cost": result.get("cost", {}), "gates": result.get("gates", {}),
            })
            if result.get("error"):
                summary["error"] = result["error"]
            if tokens is None:
                accounting_complete = False
            else:
                used_tokens += tokens
            if cost is None:
                accounting_complete = False
            else:
                used_cost += cost
            if result["status"] == "passed":
                for item in summary["artifact_contracts"]:
                    artifact_records[(node.id, item["path"])] = item
            return result

        work = {"status": "passed"} if loop.work_node in reusable else execute(by_id[loop.work_node], set())
        if work["status"] != "passed":
            nodes[loop.verify_node] = {"status": "skipped", "job_hash": _job_hash(by_id[loop.verify_node].job), "route": routes[loop.verify_node]}
            nodes[loop.repair_node] = {"status": "skipped", "job_hash": _job_hash(by_id[loop.repair_node].job), "route": routes[loop.repair_node]}
        else:
            verified = execute(by_id[loop.verify_node], {loop.work_node})
            cycles = 0
            while verified["status"] != "passed" and cycles < loop.max_cycles:
                repaired = execute(by_id[loop.repair_node], {loop.work_node, loop.verify_node})
                if repaired["status"] != "passed":
                    break
                cycles += 1
                verified = execute(by_id[loop.verify_node], {loop.repair_node})
            if nodes.get(loop.repair_node) is None:
                nodes[loop.repair_node] = {"status": "skipped", "job_hash": _job_hash(by_id[loop.repair_node].job), "route": routes[loop.repair_node]}
        passed = nodes.get(loop.work_node, {}).get("status") == "passed" and nodes.get(loop.verify_node, {}).get("status") == "passed"
        return {
            "status": "passed" if passed else "failed", "nodes": nodes,
            "budget": {"attempts": total_attempts, "tokens": used_tokens, "cost_usd": round(used_cost, 8),
                       "accounting_complete": accounting_complete, "stop_reason": stop_reason or None},
            "duration_seconds": round(time.monotonic() - started, 3), "finished_at": utc_now(),
        }


def read_harness_status(runtime_root: Path, run_id: str) -> dict[str, Any]:
    if not re.fullmatch(r"[A-Za-z0-9_.-]+", run_id):
        raise ContractError("invalid harness run id")
    root = runtime_root / "harness-runs"
    if run_id == "latest":
        candidates = sorted(root.glob("*/summary.json"), key=lambda path: path.stat().st_mtime, reverse=True)
        if not candidates:
            raise FileNotFoundError("no harness run summaries exist")
        path = candidates[0]
    else:
        path = root / run_id / "summary.json"
    return json.loads(path.read_text(encoding="utf-8"))
