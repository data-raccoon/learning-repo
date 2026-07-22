"""Strict, dependency-free contracts for registries and jobs."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
import json
from pathlib import Path
from typing import Any


IMPORTANCE_THRESHOLDS = {
    "critical": 0.98,
    "high": 0.95,
    "normal": 0.85,
    "low": 0.75,
}
RISKS = {"low", "medium", "high", "critical"}
MODES = {"read", "write"}
TOOL_CLASSES = {"inference", "files_read", "files_write", "commands"}
WORKER_COMMAND_ALLOWLIST = {
    "python -m unittest -v",
    "python -m pytest -q",
    "pytest -q",
    "npm test",
    "npm run lint",
    "npm run typecheck",
    "npm run build",
    "git diff --",
    "git status --short",
    "git add",
    "git add .",
    "git commit -m",
    "git status",
}


class ContractError(ValueError):
    """Raised when a versioned public contract is invalid."""


@dataclass(frozen=True)
class Provider:
    id: str
    display_name: str
    kind: str
    status: str
    auth_kind: str
    auth_env: str = ""
    base_url: str = ""
    billing: str = "unknown"
    plan: str = ""
    executable: str = ""
    notes: str = ""
    usage_reporting: str = "unavailable"


@dataclass(frozen=True)
class Model:
    id: str
    provider: str
    remote_id: str
    quality: float
    context_tokens: int
    input_cost_per_million: float | None
    output_cost_per_million: float | None
    price_effective_at: str
    modalities: tuple[str, ...]
    capabilities: tuple[str, ...]
    notes: str = ""


@dataclass(frozen=True)
class Harness:
    id: str
    kind: str
    provider: str
    tool_class: str
    executable: str = ""
    agent: str = ""
    max_parallel: int = 1
    status: str = "candidate"


@dataclass(frozen=True)
class ModelProfile:
    id: str
    model: str
    harness: str
    status: str
    success_probability: float
    capabilities: tuple[str, ...]
    tool_class: str
    max_parallel: int = 1
    benchmark_version: str = "unbenchmarked"
    evaluated_at: str = ""


@dataclass(frozen=True)
class Verifier:
    id: str
    argv: tuple[str, ...]
    timeout_seconds: int = 120


@dataclass(frozen=True)
class Limits:
    timeout_seconds: int = 900
    max_turns: int = 12
    max_tokens: int = 30_000


@dataclass(frozen=True)
class Job:
    schema_version: int
    id: str
    objective: str
    target_dir: str
    mode: str
    importance: str
    risk: str
    tool_class: str
    required_capabilities: tuple[str, ...] = ()
    context: tuple[str, ...] = ()
    expected_artifacts: tuple[str, ...] = ()
    verifiers: tuple[Verifier, ...] = ()
    dependencies: tuple[str, ...] = ()
    model_profile: str = ""
    output_schema: str = ""
    limits: Limits = field(default_factory=Limits)
    allowed_commands: tuple[str, ...] = ()
    allowed_write_paths: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


JOB_KEYS = {
    "schema_version", "id", "objective", "target_dir", "mode", "importance",
    "risk", "tool_class", "required_capabilities", "context",
    "expected_artifacts", "verifiers", "dependencies", "model_profile",
    "output_schema", "limits", "allowed_commands", "allowed_write_paths",
}


def _strings(value: Any, name: str) -> tuple[str, ...]:
    if value is None:
        return ()
    if not isinstance(value, list) or any(not isinstance(item, str) or not item for item in value):
        raise ContractError(f"{name} must be an array of non-empty strings")
    return tuple(value)


def load_job(path: Path) -> Job:
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise ContractError(f"cannot load job {path}: {error}") from error
    if not isinstance(raw, dict):
        raise ContractError("job must be a JSON object")
    unknown = set(raw) - JOB_KEYS
    if unknown:
        raise ContractError(f"unknown job fields: {', '.join(sorted(unknown))}")
    required = {"schema_version", "id", "objective", "target_dir", "mode", "importance", "risk", "tool_class"}
    missing = required - set(raw)
    if missing:
        raise ContractError(f"missing job fields: {', '.join(sorted(missing))}")
    if raw["schema_version"] != 1:
        raise ContractError("unsupported job schema_version")
    for key in ("id", "objective", "target_dir", "mode", "importance", "risk", "tool_class"):
        if not isinstance(raw[key], str) or not raw[key].strip():
            raise ContractError(f"{key} must be a non-empty string")
    if raw["mode"] not in MODES:
        raise ContractError(f"mode must be one of {sorted(MODES)}")
    if raw["importance"] not in IMPORTANCE_THRESHOLDS:
        raise ContractError(f"importance must be one of {sorted(IMPORTANCE_THRESHOLDS)}")
    if raw["risk"] not in RISKS:
        raise ContractError(f"risk must be one of {sorted(RISKS)}")
    if raw["tool_class"] not in TOOL_CLASSES:
        raise ContractError(f"tool_class must be one of {sorted(TOOL_CLASSES)}")
    allowed_commands = _strings(raw.get("allowed_commands"), "allowed_commands")
    unknown_commands = sorted(set(allowed_commands) - WORKER_COMMAND_ALLOWLIST)
    if unknown_commands:
        raise ContractError("worker commands are not allowlisted: " + ", ".join(unknown_commands))
    if raw["tool_class"] == "commands" and not allowed_commands:
        raise ContractError("command jobs require allowed_commands")
    if raw["tool_class"] != "commands" and allowed_commands:
        raise ContractError("allowed_commands are only valid for command jobs")
    allowed_write_paths = _strings(raw.get("allowed_write_paths"), "allowed_write_paths")
    if raw["mode"] == "read" and allowed_write_paths:
        raise ContractError("allowed_write_paths are only valid for write jobs")
    verifier_values = raw.get("verifiers", [])
    if not isinstance(verifier_values, list):
        raise ContractError("verifiers must be an array")
    verifiers: list[Verifier] = []
    for item in verifier_values:
        if not isinstance(item, dict) or set(item) - {"id", "argv", "timeout_seconds"}:
            raise ContractError("each verifier must contain only id, argv, and timeout_seconds")
        argv = _strings(item.get("argv"), "verifier.argv")
        if not item.get("id") or not argv:
            raise ContractError("verifier id and argv are required")
        timeout = item.get("timeout_seconds", 120)
        if not isinstance(timeout, int) or not 1 <= timeout <= 3600:
            raise ContractError("verifier timeout_seconds must be 1..3600")
        verifiers.append(Verifier(str(item["id"]), argv, timeout))
    limit_values = raw.get("limits", {})
    if not isinstance(limit_values, dict) or set(limit_values) - {"timeout_seconds", "max_turns", "max_tokens"}:
        raise ContractError("limits contains unknown fields")
    limits = Limits(**limit_values)
    if limits.timeout_seconds < 1 or limits.max_turns < 1 or limits.max_tokens < 1:
        raise ContractError("all limits must be positive")
    return Job(
        schema_version=1,
        id=raw["id"], objective=raw["objective"], target_dir=raw["target_dir"],
        mode=raw["mode"], importance=raw["importance"], risk=raw["risk"],
        tool_class=raw["tool_class"],
        required_capabilities=_strings(raw.get("required_capabilities"), "required_capabilities"),
        context=_strings(raw.get("context"), "context"),
        expected_artifacts=_strings(raw.get("expected_artifacts"), "expected_artifacts"),
        verifiers=tuple(verifiers),
        dependencies=_strings(raw.get("dependencies"), "dependencies"),
        model_profile=str(raw.get("model_profile", "")),
        output_schema=str(raw.get("output_schema", "")),
        limits=limits,
        allowed_commands=allowed_commands,
        allowed_write_paths=allowed_write_paths,
    )
