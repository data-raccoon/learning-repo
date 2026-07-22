"""Strict contracts for bounded multi-agent and multi-model harnesses."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
import hashlib
import json
from pathlib import Path, PurePosixPath
from typing import Any

from .contracts import ContractError, Job, Verifier, load_job


TOPOLOGIES = {"pipeline", "fanout-fanin", "repair"}
FAN_IN_STRATEGIES = {"all", "first-passing", "verifier"}
COST_ENFORCEMENT = {"strict", "best-effort"}
MEDIA_TYPES = {"application/json", "text/plain", "application/octet-stream"}


@dataclass(frozen=True)
class HarnessLimits:
    max_parallel: int = 4
    deadline_seconds: int = 3600
    max_jobs: int = 32
    max_attempts: int = 32
    max_tokens: int | None = None
    max_cost_usd: float | None = None
    cost_enforcement: str = "strict"


@dataclass(frozen=True)
class ArtifactContract:
    path: str
    media_type: str
    schema: str = ""
    sha256: str = ""


@dataclass(frozen=True)
class Handoff:
    from_node: str
    to_node: str
    artifacts: tuple[ArtifactContract, ...]


@dataclass(frozen=True)
class FanIn:
    strategy: str = "all"
    verifier: Verifier | None = None


@dataclass(frozen=True)
class HarnessNode:
    id: str
    role: str
    job_path: Path
    job: Job
    max_attempts: int = 1
    fan_in: FanIn = field(default_factory=FanIn)


@dataclass(frozen=True)
class RepairLoop:
    work_node: str
    verify_node: str
    repair_node: str
    max_cycles: int


@dataclass(frozen=True)
class HarnessSpec:
    schema_version: int
    id: str
    topology: str
    source_path: Path
    nodes: tuple[HarnessNode, ...]
    handoffs: tuple[Handoff, ...]
    limits: HarnessLimits
    repair_loop: RepairLoop | None = None

    @property
    def by_id(self) -> dict[str, HarnessNode]:
        return {node.id: node for node in self.nodes}

    def normalized(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "id": self.id,
            "topology": self.topology,
            "limits": asdict(self.limits),
            "nodes": [
                {
                    "id": node.id,
                    "role": node.role,
                    "job": node.job_path.relative_to(self.source_path.parent).as_posix(),
                    "max_attempts": node.max_attempts,
                    "fan_in": {
                        "strategy": node.fan_in.strategy,
                        **({"verifier": asdict(node.fan_in.verifier)} if node.fan_in.verifier else {}),
                    },
                    "job_contract": node.job.to_dict(),
                }
                for node in self.nodes
            ],
            "handoffs": [asdict(item) for item in self.handoffs],
            **({"repair_loop": asdict(self.repair_loop)} if self.repair_loop else {}),
        }

    def digest(self) -> str:
        encoded = json.dumps(self.normalized(), sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
        return hashlib.sha256(encoded).hexdigest()


TOP_LEVEL_KEYS = {"schema_version", "id", "topology", "limits", "nodes", "handoffs", "repair_loop"}
NODE_KEYS = {"job", "role", "max_attempts", "fan_in"}
FAN_IN_KEYS = {"strategy", "verifier"}
LIMIT_KEYS = {
    "max_parallel", "deadline_seconds", "max_jobs", "max_attempts",
    "max_tokens", "max_cost_usd", "cost_enforcement",
}
HANDOFF_KEYS = {"from", "to", "artifacts"}
ARTIFACT_KEYS = {"path", "media_type", "schema", "sha256"}
REPAIR_KEYS = {"work_node", "verify_node", "repair_node", "max_cycles"}


def _object(value: Any, name: str, allowed: set[str]) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ContractError(f"{name} must be an object")
    unknown = set(value) - allowed
    if unknown:
        raise ContractError(f"unknown {name} fields: {', '.join(sorted(unknown))}")
    return value


def _non_empty(value: Any, name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ContractError(f"{name} must be a non-empty string")
    return value


def _relative(value: Any, name: str) -> str:
    text = _non_empty(value, name).replace("\\", "/")
    path = PurePosixPath(text)
    if path.is_absolute() or ".." in path.parts:
        raise ContractError(f"{name} must be a contained relative path")
    return text


def _positive_int(value: Any, name: str, maximum: int | None = None) -> int:
    if not isinstance(value, int) or isinstance(value, bool) or value < 1 or maximum is not None and value > maximum:
        suffix = f" and at most {maximum}" if maximum is not None else ""
        raise ContractError(f"{name} must be a positive integer{suffix}")
    return value


def _verifier(value: Any, name: str) -> Verifier:
    raw = _object(value, name, {"id", "argv", "timeout_seconds"})
    identifier = _non_empty(raw.get("id"), f"{name}.id")
    argv = raw.get("argv")
    if not isinstance(argv, list) or not argv or any(not isinstance(item, str) or not item for item in argv):
        raise ContractError(f"{name}.argv must be an array of non-empty strings")
    timeout = _positive_int(raw.get("timeout_seconds", 120), f"{name}.timeout_seconds", 3600)
    return Verifier(identifier, tuple(argv), timeout)


def _path_overlaps(first: str, second: str) -> bool:
    a = PurePosixPath(first.replace("\\", "/")).as_posix().rstrip("/").casefold()
    b = PurePosixPath(second.replace("\\", "/")).as_posix().rstrip("/").casefold()
    return a == b or a.startswith(b + "/") or b.startswith(a + "/")


def _dependencies(nodes: tuple[HarnessNode, ...]) -> dict[str, set[str]]:
    return {node.id: set(node.job.dependencies) for node in nodes}


def _ancestors(node_id: str, dependencies: dict[str, set[str]]) -> set[str]:
    found: set[str] = set()
    pending = list(dependencies[node_id])
    while pending:
        item = pending.pop()
        if item not in found:
            found.add(item)
            pending.extend(dependencies[item])
    return found


def _validate_dag(nodes: tuple[HarnessNode, ...]) -> None:
    dependencies = _dependencies(nodes)
    known = set(dependencies)
    for node_id, required in dependencies.items():
        unknown = required - known
        if unknown:
            raise ContractError(f"node {node_id} has unknown dependencies: {sorted(unknown)}")
    remaining = set(known)
    while remaining:
        ready = {item for item in remaining if not (dependencies[item] & remaining)}
        if not ready:
            raise ContractError("harness contains a dependency cycle")
        remaining -= ready


def _validate_write_ownership(nodes: tuple[HarnessNode, ...]) -> None:
    dependencies = _dependencies(nodes)
    for node in nodes:
        if node.job.mode == "write" and not node.job.allowed_write_paths:
            raise ContractError(f"write node {node.id} requires allowed_write_paths")
        if node.job.mode == "read" and node.job.tool_class in {"files_write", "commands"}:
            raise ContractError(f"read node {node.id} may not use a write-capable tool class")
    for index, first in enumerate(nodes):
        for second in nodes[index + 1:]:
            first_target = PurePosixPath(first.job.target_dir.replace("\\", "/")).as_posix().casefold()
            second_target = PurePosixPath(second.job.target_dir.replace("\\", "/")).as_posix().casefold()
            if first.job.mode != "write" or second.job.mode != "write" or first_target != second_target:
                continue
            ordered = first.id in _ancestors(second.id, dependencies) or second.id in _ancestors(first.id, dependencies)
            if ordered:
                continue
            overlaps = [
                (a, b) for a in first.job.allowed_write_paths for b in second.job.allowed_write_paths
                if _path_overlaps(a, b)
            ]
            if overlaps:
                raise ContractError(f"parallel write nodes {first.id} and {second.id} have overlapping ownership")


def _validate_topology(spec: HarnessSpec) -> None:
    nodes = spec.nodes
    dependencies = _dependencies(nodes)
    if spec.topology == "pipeline":
        roots = [item for item in nodes if not item.job.dependencies]
        if len(roots) != 1 or any(len(item.job.dependencies) > 1 for item in nodes):
            raise ContractError("pipeline requires one root and at most one dependency per node")
        if len(nodes) > 1 and sum(len(item.job.dependencies) for item in nodes) != len(nodes) - 1:
            raise ContractError("pipeline must form one connected chain")
        children = {item.id: 0 for item in nodes}
        for item in nodes:
            for dependency in item.job.dependencies:
                children[dependency] += 1
        if sum(value == 0 for value in children.values()) != 1 or any(value > 1 for value in children.values()):
            raise ContractError("pipeline must form one connected chain")
    elif spec.topology == "fanout-fanin":
        if not any(len(item.job.dependencies) > 1 for item in nodes):
            raise ContractError("fanout-fanin requires at least one fan-in node")
    elif spec.topology == "repair":
        loop = spec.repair_loop
        if loop is None:
            raise ContractError("repair topology requires repair_loop")
        if set(spec.by_id) != {loop.work_node, loop.verify_node, loop.repair_node}:
            raise ContractError("minimal repair topology must contain exactly work, verify, and repair nodes")
        if dependencies[loop.work_node] or dependencies[loop.verify_node] != {loop.work_node} or dependencies[loop.repair_node] != {loop.verify_node}:
            raise ContractError("repair topology dependencies must be work -> verify -> repair")
    if spec.topology != "repair" and spec.repair_loop is not None:
        raise ContractError("repair_loop is only valid for repair topology")


def _validate_handoffs(spec: HarnessSpec) -> None:
    by_id = spec.by_id
    seen: set[tuple[str, str, str]] = set()
    for handoff in spec.handoffs:
        if handoff.from_node not in by_id or handoff.to_node not in by_id:
            raise ContractError("handoff references an unknown node")
        source = by_id[handoff.from_node].job
        target = by_id[handoff.to_node].job
        repair_feedback = (
            spec.topology == "repair" and spec.repair_loop is not None
            and (
                handoff.from_node == spec.repair_loop.repair_node
                and handoff.to_node == spec.repair_loop.verify_node
                or handoff.from_node == spec.repair_loop.work_node
                and handoff.to_node == spec.repair_loop.repair_node
            )
        )
        if handoff.from_node not in target.dependencies and not repair_feedback:
            raise ContractError("handoff source must be a direct dependency of its consumer")
        if source.target_dir != target.target_dir:
            raise ContractError("handoff nodes must share a target_dir")
        for artifact in handoff.artifacts:
            key = (handoff.from_node, handoff.to_node, artifact.path)
            if key in seen:
                raise ContractError("duplicate handoff artifact")
            seen.add(key)
            if artifact.path not in source.expected_artifacts:
                raise ContractError(f"handoff artifact {artifact.path} is not declared by producer {handoff.from_node}")
            if artifact.path not in target.context:
                raise ContractError(f"handoff artifact {artifact.path} is not declared as context by consumer {handoff.to_node}")
            if target.mode == "write" and any(_path_overlaps(artifact.path, item) for item in target.allowed_write_paths):
                raise ContractError(f"consumer {handoff.to_node} may write immutable handoff artifact {artifact.path}")


def load_harness(path: Path) -> HarnessSpec:
    path = path.resolve()
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise ContractError(f"cannot load harness {path}: {error}") from error
    raw = _object(raw, "harness", TOP_LEVEL_KEYS)
    if raw.get("schema_version") != 1:
        raise ContractError("unsupported harness schema_version")
    identifier = _non_empty(raw.get("id"), "harness.id")
    topology = raw.get("topology")
    if topology not in TOPOLOGIES:
        raise ContractError(f"topology must be one of {sorted(TOPOLOGIES)}")

    limit_values = _object(raw.get("limits", {}), "limits", LIMIT_KEYS)
    enforcement = limit_values.get("cost_enforcement", "strict")
    if enforcement not in COST_ENFORCEMENT:
        raise ContractError(f"cost_enforcement must be one of {sorted(COST_ENFORCEMENT)}")
    max_tokens = limit_values.get("max_tokens")
    if max_tokens is not None:
        max_tokens = _positive_int(max_tokens, "limits.max_tokens")
    max_cost = limit_values.get("max_cost_usd")
    if max_cost is not None and (not isinstance(max_cost, (int, float)) or isinstance(max_cost, bool) or max_cost < 0):
        raise ContractError("limits.max_cost_usd must be a non-negative number")
    limits = HarnessLimits(
        max_parallel=_positive_int(limit_values.get("max_parallel", 4), "limits.max_parallel", 32),
        deadline_seconds=_positive_int(limit_values.get("deadline_seconds", 3600), "limits.deadline_seconds"),
        max_jobs=_positive_int(limit_values.get("max_jobs", 32), "limits.max_jobs", 1000),
        max_attempts=_positive_int(limit_values.get("max_attempts", 32), "limits.max_attempts", 1000),
        max_tokens=max_tokens,
        max_cost_usd=float(max_cost) if max_cost is not None else None,
        cost_enforcement=enforcement,
    )

    node_values = raw.get("nodes")
    if not isinstance(node_values, list) or not node_values:
        raise ContractError("nodes must be a non-empty array")
    nodes: list[HarnessNode] = []
    for index, value in enumerate(node_values):
        node_raw = _object(value, f"nodes[{index}]", NODE_KEYS)
        job_value = _relative(node_raw.get("job"), f"nodes[{index}].job")
        job_path = (path.parent / Path(job_value)).resolve()
        if path.parent not in job_path.parents:
            raise ContractError("job path escapes harness directory")
        job = load_job(job_path)
        role = _non_empty(node_raw.get("role"), f"nodes[{index}].role")
        attempts = _positive_int(node_raw.get("max_attempts", 1), f"nodes[{index}].max_attempts", 100)
        fan_raw = _object(node_raw.get("fan_in", {}), f"nodes[{index}].fan_in", FAN_IN_KEYS)
        strategy = fan_raw.get("strategy", "all")
        if strategy not in FAN_IN_STRATEGIES:
            raise ContractError(f"fan-in strategy must be one of {sorted(FAN_IN_STRATEGIES)}")
        selector = _verifier(fan_raw["verifier"], f"nodes[{index}].fan_in.verifier") if "verifier" in fan_raw else None
        if strategy == "verifier" and selector is None:
            raise ContractError("verifier fan-in requires a verifier")
        if strategy != "verifier" and selector is not None:
            raise ContractError("fan-in verifier is only valid with verifier strategy")
        if strategy != "all" and len(job.dependencies) < 2:
            raise ContractError("non-default fan-in requires at least two dependencies")
        nodes.append(HarnessNode(job.id, role, job_path, job, attempts, FanIn(strategy, selector)))
    node_tuple = tuple(nodes)
    if len({item.id for item in node_tuple}) != len(node_tuple):
        raise ContractError("harness node ids must be unique")
    if len(node_tuple) > limits.max_jobs:
        raise ContractError("node count exceeds limits.max_jobs")
    if sum(item.max_attempts for item in node_tuple) > limits.max_attempts:
        raise ContractError("node attempt limits exceed limits.max_attempts")

    handoff_values = raw.get("handoffs", [])
    if not isinstance(handoff_values, list):
        raise ContractError("handoffs must be an array")
    handoffs: list[Handoff] = []
    for index, value in enumerate(handoff_values):
        item = _object(value, f"handoffs[{index}]", HANDOFF_KEYS)
        artifact_values = item.get("artifacts")
        if not isinstance(artifact_values, list) or not artifact_values:
            raise ContractError("handoff artifacts must be a non-empty array")
        artifacts: list[ArtifactContract] = []
        for artifact_index, artifact_value in enumerate(artifact_values):
            artifact = _object(artifact_value, f"handoffs[{index}].artifacts[{artifact_index}]", ARTIFACT_KEYS)
            digest = artifact.get("sha256", "")
            if digest and (not isinstance(digest, str) or len(digest) != 64 or any(char not in "0123456789abcdef" for char in digest.lower())):
                raise ContractError("artifact sha256 must be a 64-character hexadecimal digest")
            media_type = _non_empty(artifact.get("media_type"), "artifact.media_type")
            if media_type not in MEDIA_TYPES:
                raise ContractError(f"artifact.media_type must be one of {sorted(MEDIA_TYPES)}")
            if artifact.get("schema") and media_type != "application/json":
                raise ContractError("artifact.schema is only valid for application/json")
            artifacts.append(ArtifactContract(
                _relative(artifact.get("path"), "artifact.path"),
                media_type,
                _relative(artifact["schema"], "artifact.schema") if artifact.get("schema") else "",
                digest.lower(),
            ))
        handoffs.append(Handoff(
            _non_empty(item.get("from"), "handoff.from"),
            _non_empty(item.get("to"), "handoff.to"),
            tuple(artifacts),
        ))

    repair_loop = None
    if "repair_loop" in raw:
        item = _object(raw["repair_loop"], "repair_loop", REPAIR_KEYS)
        repair_loop = RepairLoop(
            _non_empty(item.get("work_node"), "repair_loop.work_node"),
            _non_empty(item.get("verify_node"), "repair_loop.verify_node"),
            _non_empty(item.get("repair_node"), "repair_loop.repair_node"),
            _positive_int(item.get("max_cycles"), "repair_loop.max_cycles", 100),
        )
        by_id = {item.id: item for item in node_tuple}
        unknown_repair_nodes = {
            repair_loop.work_node, repair_loop.verify_node, repair_loop.repair_node,
        } - set(by_id)
        if unknown_repair_nodes:
            raise ContractError(f"repair loop references unknown nodes: {sorted(unknown_repair_nodes)}")
        required_attempts = 2 + repair_loop.max_cycles * 2
        if required_attempts > limits.max_attempts:
            raise ContractError("repair loop can exceed limits.max_attempts")
        if by_id[repair_loop.verify_node].max_attempts < repair_loop.max_cycles + 1:
            raise ContractError("verify node max_attempts must cover every repair cycle")
        if by_id[repair_loop.repair_node].max_attempts < repair_loop.max_cycles:
            raise ContractError("repair node max_attempts must cover every repair cycle")

    spec = HarnessSpec(1, identifier, topology, path, node_tuple, tuple(handoffs), limits, repair_loop)
    _validate_dag(spec.nodes)
    _validate_write_ownership(spec.nodes)
    _validate_topology(spec)
    _validate_handoffs(spec)
    return spec
