"""Dependency-free boundary for small-context repository workers."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path, PurePosixPath
from typing import Any

from model_runtime import (
    ModelRejected,
    inventory as model_inventory,
    load_registry,
    run_canary as run_model_canary,
    run_mistral_vibe_worker,
    route as route_model,
)


class Rejected(ValueError):
    """A contract or release-gate rejection."""


CONTRACT_VERSION = 2
TASK_FIELDS = {
    "v", "id", "kind", "depends_on", "goal", "target", "model", "context",
    "write_roots", "allowed_commands", "done", "forbidden", "limits",
    "verifiers",
}
LIMIT_FIELDS = {
    "packet_chars", "output_chars", "model_context_tokens",
    "model_session_tokens", "model_output_tokens", "model_timeout_seconds",
    "max_tool_calls", "max_verifiers", "verifier_timeout_seconds",
}
RESULT_FIELDS = {
    "v", "task_id", "packet_sha256", "status", "summary", "changed", "risks",
}
BASELINE_FIELDS = {"v", "task_id", "packet_sha256", "worker", "target", "files"}
HEX64 = re.compile(r"^[a-f0-9]{64}$")
IDENTIFIER = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,63}$")
SECRET_PATTERNS = (
    re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    re.compile(r"\b(?:sk|ghp|github_pat|xox[baprs])[-_][A-Za-z0-9_-]{12,}\b"),
    re.compile(r"(?i)\b(?:api[_-]?key|password|secret|token)\s*[:=]\s*[^\s]{8,}"),
)
BLOCKED_NAMES = {".env", "id_rsa", "id_ed25519"}
TASK_KINDS = {"planning", "review", "coding", "repair"}


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")


def digest_value(value: Any) -> str:
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


def digest_file(path: Path) -> str:
    sha = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            sha.update(chunk)
    return sha.hexdigest()


def target_manifest(target: Path) -> list[dict[str, str]]:
    target = target.resolve()
    files: list[dict[str, str]] = []
    paths = sorted(
        target.rglob("*"),
        key=lambda item: item.relative_to(target).as_posix(),
    )
    for path in paths:
        relative = path.relative_to(target)
        label = relative.as_posix()
        if path.is_symlink():
            raise Rejected(f"target manifest contains a symbolic link: {label}")
        if path.is_file():
            files.append({"path": label, "sha256": digest_file(path)})
    return files


def read_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise Rejected(f"cannot read JSON {path}: {exc}") from exc


def write_json(path: Path, value: Any) -> None:
    path.write_text(
        json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n",
        encoding="utf-8",
    )


def exact_fields(value: Any, fields: set[str], label: str) -> dict[str, Any]:
    if type(value) is not dict:
        raise Rejected(f"{label} must be an object")
    keys = set(value)
    if keys != fields:
        raise Rejected(
            f"{label} field mismatch; missing={sorted(fields - keys)}, "
            f"unknown={sorted(keys - fields)}"
        )
    return value


def nonempty_text(value: Any, label: str, maximum: int) -> str:
    if type(value) is not str or not value.strip() or len(value) > maximum:
        raise Rejected(f"{label} must be non-empty text of at most {maximum} chars")
    return value


def string_list(value: Any, label: str, maximum: int, item_maximum: int) -> list[str]:
    if type(value) is not list or len(value) > maximum:
        raise Rejected(f"{label} must be a list with at most {maximum} items")
    for index, item in enumerate(value):
        nonempty_text(item, f"{label}[{index}]", item_maximum)
    return value


def relative_path(value: Any, label: str) -> PurePosixPath:
    text = nonempty_text(value, label, 500).replace("\\", "/")
    path = PurePosixPath(text)
    if path.is_absolute() or ".." in path.parts or "." in path.parts or not path.parts:
        raise Rejected(f"{label} must be a normalized relative path")
    return path


def resolve_inside(root: Path, relative: PurePosixPath, label: str) -> Path:
    root = root.resolve()
    lexical = root.joinpath(*relative.parts)
    current = root
    for part in relative.parts:
        current = current / part
        if current.is_symlink():
            raise Rejected(f"{label} contains a symbolic link")
    candidate = lexical.resolve()
    try:
        candidate.relative_to(root)
    except ValueError as exc:
        raise Rejected(f"{label} escapes its target") from exc
    return candidate


def bounded_int(
    value: Any, label: str, minimum: int, maximum: int
) -> int:
    if type(value) is not int or not minimum <= value <= maximum:
        raise Rejected(f"{label} must be an integer in [{minimum}, {maximum}]")
    return value


def validate_task(raw: Any) -> dict[str, Any]:
    task = exact_fields(raw, TASK_FIELDS, "task")
    if task["v"] != CONTRACT_VERSION:
        raise Rejected("unsupported task version")
    if type(task["id"]) is not str or not IDENTIFIER.fullmatch(task["id"]):
        raise Rejected("invalid task id")
    if task["kind"] not in TASK_KINDS:
        raise Rejected("invalid task kind")
    depends_on = string_list(task["depends_on"], "depends_on", 64, 64)
    if len(depends_on) != len(set(depends_on)):
        raise Rejected("depends_on contains duplicates")
    if task["id"] in depends_on:
        raise Rejected("task cannot depend on itself")
    if any(not IDENTIFIER.fullmatch(item) for item in depends_on):
        raise Rejected("depends_on contains an invalid task id")
    nonempty_text(task["goal"], "goal", 1000)
    relative_path(task["target"], "target")
    model = exact_fields(
        task["model"], {"profile", "capability", "importance"}, "model"
    )
    nonempty_text(model["profile"], "model.profile", 128)
    if model["profile"] == "auto":
        raise Rejected("model.profile must name a human-selected profile")
    nonempty_text(model["capability"], "model.capability", 128)
    if model["importance"] not in {"low", "normal", "high", "critical"}:
        raise Rejected("model.importance is invalid")
    if type(task["context"]) is not list or not 1 <= len(task["context"]) <= 24:
        raise Rejected("context must contain 1..24 slices")
    for index, item in enumerate(task["context"]):
        item = exact_fields(item, {"path", "start", "end"}, f"context[{index}]")
        relative_path(item["path"], f"context[{index}].path")
        start = bounded_int(item["start"], f"context[{index}].start", 1, 10_000_000)
        end = bounded_int(item["end"], f"context[{index}].end", 1, 10_000_000)
        if end < start:
            raise Rejected(f"context[{index}] end precedes start")
    if type(task["write_roots"]) is not list or not 1 <= len(task["write_roots"]) <= 256:
        raise Rejected("write_roots must contain 1..256 paths")
    normalized_roots: list[PurePosixPath] = []
    for index, item in enumerate(task["write_roots"]):
        root = relative_path(item, f"write_roots[{index}]")
        if any(character in str(root) for character in "*?[]"):
            raise Rejected(f"write_roots[{index}] must be an exact path")
        normalized_roots.append(root)
    if len(normalized_roots) != len(set(normalized_roots)):
        raise Rejected("write_roots contains duplicates")
    for index, root in enumerate(normalized_roots):
        if any(root in other.parents or other in root.parents for other in normalized_roots[index + 1 :]):
            raise Rejected("write_roots must not overlap")
    allowed_commands = task["allowed_commands"]
    if type(allowed_commands) is not list or len(allowed_commands) > 16:
        raise Rejected("allowed_commands must contain at most 16 argv vectors")
    for index, argv in enumerate(allowed_commands):
        if type(argv) is not list or not 1 <= len(argv) <= 32:
            raise Rejected(f"allowed_commands[{index}] must contain 1..32 strings")
        for arg_index, arg in enumerate(argv):
            if type(arg) is not str or not arg or len(arg) > 500:
                raise Rejected(f"invalid allowed command argument {index}:{arg_index}")
        if not command_is_admitted(argv):
            raise Rejected(f"allowed_commands[{index}] is not globally admitted")
    if not string_list(task["done"], "done", 16, 500):
        raise Rejected("done must contain at least one criterion")
    string_list(task["forbidden"], "forbidden", 16, 300)
    limits = exact_fields(task["limits"], LIMIT_FIELDS, "limits")
    bounded_int(limits["packet_chars"], "packet_chars", 256, 1_000_000)
    bounded_int(limits["output_chars"], "output_chars", 128, 1_000_000)
    bounded_int(
        limits["model_context_tokens"], "model_context_tokens", 1024, 256_000
    )
    bounded_int(
        limits["model_session_tokens"], "model_session_tokens", 1024, 1_000_000
    )
    if limits["model_session_tokens"] < limits["model_context_tokens"]:
        raise Rejected("model_session_tokens must cover model_context_tokens")
    bounded_int(
        limits["model_output_tokens"], "model_output_tokens", 32, 256_000
    )
    bounded_int(
        limits["model_timeout_seconds"], "model_timeout_seconds", 1, 3600
    )
    bounded_int(limits["max_tool_calls"], "max_tool_calls", 1, 1000)
    bounded_int(limits["max_verifiers"], "max_verifiers", 0, 32)
    bounded_int(
        limits["verifier_timeout_seconds"], "verifier_timeout_seconds", 1, 3600
    )
    if type(task["verifiers"]) is not list:
        raise Rejected("verifiers must be a list")
    if len(task["verifiers"]) > limits["max_verifiers"]:
        raise Rejected("verifier count exceeds task limit")
    if not task["verifiers"]:
        raise Rejected("every task requires an independent verifier")
    verifier_ids: set[str] = set()
    for index, verifier in enumerate(task["verifiers"]):
        verifier = exact_fields(verifier, {"id", "argv"}, f"verifiers[{index}]")
        if type(verifier["id"]) is not str or not IDENTIFIER.fullmatch(verifier["id"]):
            raise Rejected(f"invalid verifier id at index {index}")
        if verifier["id"] in verifier_ids:
            raise Rejected(f"duplicate verifier id: {verifier['id']}")
        verifier_ids.add(verifier["id"])
        argv = verifier["argv"]
        if type(argv) is not list or not 1 <= len(argv) <= 64:
            raise Rejected(f"verifiers[{index}].argv must contain 1..64 strings")
        for arg_index, arg in enumerate(argv):
            if type(arg) is not str or len(arg) > 1000:
                raise Rejected(f"invalid verifier argument {index}:{arg_index}")
    if task["kind"] in {"coding", "repair"} and not allowed_commands:
        raise Rejected("coding and repair tasks require worker-loop test commands")
    minimums = {
        "planning": (300_000, 24),
        "review": (300_000, 20),
        "coding": (300_000, 24),
        "repair": (120_000, 10),
    }
    minimum_session, minimum_turns = minimums[task["kind"]]
    if limits["model_session_tokens"] < minimum_session:
        raise Rejected(
            f"{task['kind']} tasks require at least {minimum_session} session tokens"
        )
    if limits["max_tool_calls"] < minimum_turns:
        raise Rejected(
            f"{task['kind']} tasks require at least {minimum_turns} tool turns"
        )
    return task


def command_is_admitted(argv: list[str]) -> bool:
    if argv[:2] in (["git", "status"], ["git", "diff"]):
        return True
    if argv[0] in {"./gradlew", "gradlew", "gradlew.bat"}:
        return len(argv) >= 2 and all(
            item in {
                "build", "test", "check", "compileJava", "compileTestJava",
                "spotlessCheck", "--no-daemon", "--stacktrace", "--info",
            }
            for item in argv[1:]
        )
    if argv[:2] in (["npm", "test"], ["npm", "run"]):
        return argv[:2] == ["npm", "test"] or (
            len(argv) == 3 and argv[2] in {"test", "lint", "typecheck", "build"}
        )
    if argv[:2] == ["cargo", "test"]:
        return all(item in {"--all", "--workspace", "--locked"} for item in argv[2:])
    if argv[:2] == ["go", "test"]:
        return len(argv) == 3 and argv[2] == "./..."
    if argv[:2] == ["dotnet", "test"]:
        return len(argv) == 2
    if argv[0] == "{python}" and len(argv) >= 3 and argv[1] == "-m":
        return argv[2] in {"unittest", "pytest"} and "-c" not in argv
    return False


def validate_packet(raw: Any) -> dict[str, Any]:
    packet = exact_fields(raw, {"v", "task", "task_sha256", "excerpts"}, "packet")
    if packet["v"] != CONTRACT_VERSION:
        raise Rejected("unsupported packet version")
    task = validate_task(packet["task"])
    if type(packet["task_sha256"]) is not str or not HEX64.fullmatch(packet["task_sha256"]):
        raise Rejected("invalid task digest")
    if packet["task_sha256"] != digest_value(task):
        raise Rejected("packet task digest mismatch")
    if type(packet["excerpts"]) is not list or len(packet["excerpts"]) != len(task["context"]):
        raise Rejected("packet excerpt count mismatch")
    expected_fields = {"path", "start", "end", "sha256", "text"}
    for index, excerpt in enumerate(packet["excerpts"]):
        excerpt = exact_fields(excerpt, expected_fields, f"excerpts[{index}]")
        source = task["context"][index]
        if any(excerpt[key] != source[key] for key in ("path", "start", "end")):
            raise Rejected(f"excerpt {index} does not match task slice")
        if type(excerpt["text"]) is not str:
            raise Rejected(f"excerpt {index} text must be a string")
        expected = hashlib.sha256(excerpt["text"].encode("utf-8")).hexdigest()
        if excerpt["sha256"] != expected:
            raise Rejected(f"excerpt {index} digest mismatch")
    packet_chars = len(canonical_bytes(packet).decode("utf-8"))
    if packet_chars > task["limits"]["packet_chars"]:
        raise Rejected("packet exceeds packet_chars")
    return packet


def validate_result(raw: Any) -> dict[str, Any]:
    result = exact_fields(raw, RESULT_FIELDS, "result")
    if result["v"] != CONTRACT_VERSION:
        raise Rejected("unsupported result version")
    nonempty_text(result["task_id"], "task_id", 64)
    if type(result["packet_sha256"]) is not str or not HEX64.fullmatch(result["packet_sha256"]):
        raise Rejected("invalid result packet digest")
    if result["status"] not in {"done", "blocked", "failed"}:
        raise Rejected("invalid result status")
    nonempty_text(result["summary"], "summary", 100_000)
    string_list(result["risks"], "risks", 64, 2000)
    if type(result["changed"]) is not list or len(result["changed"]) > 256:
        raise Rejected("changed must be a list with at most 256 items")
    seen: set[str] = set()
    for index, changed in enumerate(result["changed"]):
        changed = exact_fields(changed, {"path", "sha256"}, f"changed[{index}]")
        normalized = str(relative_path(changed["path"], f"changed[{index}].path"))
        if normalized in seen:
            raise Rejected(f"duplicate changed path: {normalized}")
        seen.add(normalized)
        if type(changed["sha256"]) is not str or not HEX64.fullmatch(changed["sha256"]):
            raise Rejected(f"invalid changed digest at index {index}")
    return result


def validate_baseline(raw: Any) -> dict[str, Any]:
    baseline = exact_fields(raw, BASELINE_FIELDS, "baseline")
    if baseline["v"] != CONTRACT_VERSION:
        raise Rejected("unsupported baseline version")
    nonempty_text(baseline["task_id"], "baseline.task_id", 64)
    nonempty_text(baseline["worker"], "baseline.worker", 128)
    if (
        type(baseline["packet_sha256"]) is not str
        or not HEX64.fullmatch(baseline["packet_sha256"])
    ):
        raise Rejected("invalid baseline packet digest")
    relative_path(baseline["target"], "baseline.target")
    if type(baseline["files"]) is not list or len(baseline["files"]) > 100_000:
        raise Rejected("baseline.files must contain at most 100000 items")
    seen: set[str] = set()
    previous = ""
    for index, item in enumerate(baseline["files"]):
        item = exact_fields(item, {"path", "sha256"}, f"baseline.files[{index}]")
        normalized = str(relative_path(item["path"], f"baseline.files[{index}].path"))
        if normalized in seen:
            raise Rejected(f"duplicate baseline path: {normalized}")
        if previous and normalized < previous:
            raise Rejected("baseline files must be sorted by path")
        seen.add(normalized)
        previous = normalized
        if type(item["sha256"]) is not str or not HEX64.fullmatch(item["sha256"]):
            raise Rejected(f"invalid baseline digest at index {index}")
    return baseline


def reject_likely_secret(path: PurePosixPath, text: str) -> None:
    if path.name.lower() in BLOCKED_NAMES or path.suffix.lower() in {".pem", ".key", ".p12"}:
        raise Rejected(f"context file is secret-prone: {path}")
    if any(pattern.search(text) for pattern in SECRET_PATTERNS):
        raise Rejected(f"likely secret found in context file: {path}")


def prepare_task_packet(raw_task: Any, repo: Path) -> tuple[dict[str, Any], int]:
    task = validate_task(raw_task)
    target = resolve_inside(repo, relative_path(task["target"], "target"), "target")
    if not target.is_dir():
        raise Rejected(f"target directory does not exist: {task['target']}")
    for index, value in enumerate(task["write_roots"]):
        relative = relative_path(value, f"write_roots[{index}]")
        candidate = resolve_inside(target, relative, f"write_roots[{index}]")
        if candidate.exists() and not candidate.is_file():
            raise Rejected(f"write_roots[{index}] must name a file: {relative}")
    excerpts = []
    total_chars = 0
    for index, source in enumerate(task["context"]):
        relative = relative_path(source["path"], f"context[{index}].path")
        path = resolve_inside(target, relative, f"context[{index}].path")
        if not path.is_file():
            raise Rejected(f"context file does not exist: {relative}")
        try:
            lines = path.read_text(encoding="utf-8").splitlines(keepends=True)
        except (OSError, UnicodeError) as exc:
            raise Rejected(f"cannot read context file {relative}: {exc}") from exc
        if source["start"] > len(lines):
            raise Rejected(f"context slice starts after EOF: {relative}")
        text = "".join(lines[source["start"] - 1 : source["end"]])
        reject_likely_secret(relative, text)
        total_chars += len(text)
        excerpts.append(
            {
                "path": str(relative),
                "start": source["start"],
                "end": source["end"],
                "sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
                "text": text,
            }
        )
    packet = {
        "v": CONTRACT_VERSION,
        "task": task,
        "task_sha256": digest_value(task),
        "excerpts": excerpts,
    }
    packet_chars = len(canonical_bytes(packet).decode("utf-8"))
    if packet_chars > task["limits"]["packet_chars"]:
        raise Rejected("complete worker packet exceeds packet_chars")
    return packet, total_chars


def prepare_packet(task_path: Path, repo: Path) -> tuple[dict[str, Any], int]:
    return prepare_task_packet(read_json(task_path), repo)


def preflight_task(
    raw_task: Any,
    repo: Path,
    registry_path: Path,
) -> dict[str, Any]:
    packet, excerpt_chars = prepare_task_packet(raw_task, repo)
    task = packet["task"]
    profiles = load_registry(registry_path)
    selected = profiles.get(task["model"]["profile"])
    if selected is None:
        raise Rejected(f"unknown model profile: {task['model']['profile']}")
    limits = task["limits"]
    requested = {
        "model_context_tokens": selected.context_tokens,
        "model_session_tokens": selected.session_tokens,
        "model_output_tokens": selected.output_tokens,
    }
    for field, available in requested.items():
        if limits[field] > available:
            raise Rejected(
                f"{field} exceeds registered profile limit {available}: {limits[field]}"
            )
    packet_chars = len(canonical_bytes(packet).decode("utf-8"))
    warnings = []
    if packet_chars >= limits["packet_chars"] * 0.85:
        warnings.append("packet budget is at least 85% utilized")
    if limits["model_session_tokens"] < limits["model_context_tokens"] * 3:
        warnings.append("session budget provides less than three context epochs")
    return {
        "status": "passed",
        "task_id": task["id"],
        "kind": task["kind"],
        "profile": selected.id,
        "target": task["target"],
        "excerpts": len(packet["excerpts"]),
        "excerpt_chars": excerpt_chars,
        "packet_chars": packet_chars,
        "packet_budget": limits["packet_chars"],
        "worker_test_commands": len(task["allowed_commands"]),
        "independent_verifiers": len(task["verifiers"]),
        "warnings": warnings,
    }


def command_preflight(
    task_path: Path,
    repo: Path,
    registry_path: Path,
) -> dict[str, Any]:
    return preflight_task(read_json(task_path), repo, registry_path)


def command_pack(task_path: Path, packet_path: Path, repo: Path) -> dict[str, Any]:
    packet, total_chars = prepare_packet(task_path, repo)
    task = packet["task"]
    packet_chars = len(canonical_bytes(packet).decode("utf-8"))
    write_json(packet_path, packet)
    return {
        "status": "packed",
        "task_id": task["id"],
        "packet_sha256": digest_value(packet),
        "excerpt_chars": total_chars,
        "packet_chars": packet_chars,
        "packet_budget": task["limits"]["packet_chars"],
        "excerpts": len(packet["excerpts"]),
    }


def command_accept(
    packet_path: Path, ack_path: Path, worker: str, reject_reason: str | None
) -> dict[str, Any]:
    packet = validate_packet(read_json(packet_path))
    nonempty_text(worker, "worker", 128)
    accepted = reject_reason is None
    ack = {
        "v": CONTRACT_VERSION,
        "task_id": packet["task"]["id"],
        "packet_sha256": digest_value(packet),
        "worker": worker,
        "accepted": accepted,
        "reason": "" if accepted else nonempty_text(reject_reason, "reason", 1000),
    }
    write_json(ack_path, ack)
    return {"status": "accepted" if accepted else "rejected", **ack}


def command_snapshot(
    task_path: Path,
    packet_path: Path,
    ack_path: Path,
    baseline_path: Path,
    repo: Path,
) -> dict[str, Any]:
    task = validate_task(read_json(task_path))
    packet = validate_packet(read_json(packet_path))
    ack = validate_ack(read_json(ack_path))
    if packet["task_sha256"] != digest_value(task) or packet["task"] != task:
        raise Rejected("task and packet do not match")
    packet_sha = digest_value(packet)
    if (
        not ack["accepted"]
        or ack["task_id"] != task["id"]
        or ack["packet_sha256"] != packet_sha
    ):
        raise Rejected("snapshot requires the accepted acknowledgement for this packet")
    target = resolve_inside(repo, relative_path(task["target"], "target"), "target")
    if not target.is_dir():
        raise Rejected(f"target directory does not exist: {task['target']}")
    baseline_resolved = baseline_path.resolve()
    try:
        baseline_resolved.relative_to(target.resolve())
    except ValueError:
        pass
    else:
        raise Rejected("baseline must be stored outside the task target")
    baseline = {
        "v": CONTRACT_VERSION,
        "task_id": task["id"],
        "packet_sha256": packet_sha,
        "worker": ack["worker"],
        "target": task["target"],
        "files": target_manifest(target),
    }
    validate_baseline(baseline)
    write_json(baseline_path, baseline)
    return {
        "status": "snapshotted",
        "task_id": task["id"],
        "packet_sha256": baseline["packet_sha256"],
        "baseline": str(baseline_path),
        "baseline_sha256": digest_value(baseline),
        "files": len(baseline["files"]),
    }


def command_inventory(registry_path: Path, endpoint: str) -> dict[str, Any]:
    profiles = load_registry(registry_path)
    return model_inventory(profiles, ollama_endpoint=endpoint)


def command_canary(
    profile_id: str,
    registry_path: Path,
    endpoint: str,
    timeout: int,
) -> dict[str, Any]:
    bounded_int(timeout, "canary timeout", 1, 3600)
    profiles = load_registry(registry_path)
    selected = profiles.get(profile_id)
    if selected is None:
        raise Rejected(f"unknown canary profile: {profile_id}")
    availability = model_inventory(profiles, ollama_endpoint=endpoint)
    available = {
        row["id"]
        for row in availability["profiles"]
        if row["available"]
    }
    if selected.id not in available or selected.status != "eligible":
        raise Rejected(f"canary profile is unavailable or ineligible: {profile_id}")
    packet = {
        "task": {
            "id": "provider-canary",
            "goal": "Reply with exactly SMALL_CONTEXT_CANARY_OK.",
            "done": ["The response is exactly SMALL_CONTEXT_CANARY_OK."],
            "forbidden": ["Do not add explanation or formatting."],
        },
        "excerpts": [],
    }
    result = run_model_canary(
        selected,
        packet,
        endpoint=endpoint,
        context_tokens=2048,
        output_tokens=64,
        timeout=timeout,
    )
    passed = result["text"].strip() == "SMALL_CONTEXT_CANARY_OK"
    if not passed:
        raise Rejected(
            f"canary response mismatch for {profile_id}: "
            f"{result['text'].strip()[:200]}"
        )
    return {
        "status": "passed",
        "profile": selected.id,
        "provider": selected.provider,
        "model": selected.model,
        "usage": result["usage"],
        "attestation": result["attestation"],
    }


def select_model(
    packet: dict[str, Any], registry_path: Path, endpoint: str
) -> tuple[Any, dict[str, Any]]:
    profiles = load_registry(registry_path)
    availability = model_inventory(profiles, ollama_endpoint=endpoint)
    selected = route_model(profiles, availability, packet["task"]["model"])
    return selected, availability


def command_route(
    packet_path: Path, registry_path: Path, endpoint: str
) -> dict[str, Any]:
    packet = validate_packet(read_json(packet_path))
    selected, _ = select_model(packet, registry_path, endpoint)
    return {
        "status": "routed",
        "task_id": packet["task"]["id"],
        "packet_sha256": digest_value(packet),
        "profile": selected.id,
        "provider": selected.provider,
        "model": selected.model,
        "billing": selected.billing,
        "context_tokens": min(
            packet["task"]["limits"]["model_context_tokens"],
            selected.context_tokens,
        ),
        "compaction_tokens": (
            min(
                packet["task"]["limits"]["model_context_tokens"],
                selected.compaction_tokens,
            )
            if selected.compaction_tokens
            else 0
        ),
        "session_tokens": min(
            packet["task"]["limits"]["model_session_tokens"],
            selected.session_tokens,
        ),
        "output_tokens": min(
            packet["task"]["limits"]["model_output_tokens"],
            selected.output_tokens,
        ),
    }


def command_execute(
    packet_path: Path,
    ack_path: Path,
    baseline_path: Path,
    result_path: Path,
    trajectory_path: Path,
    repo: Path,
    registry_path: Path,
    endpoint: str,
) -> dict[str, Any]:
    packet = validate_packet(read_json(packet_path))
    ack = validate_ack(read_json(ack_path))
    packet_sha = digest_value(packet)
    if (
        not ack["accepted"]
        or ack["task_id"] != packet["task"]["id"]
        or ack["packet_sha256"] != packet_sha
    ):
        raise Rejected("execute requires the accepted acknowledgement for this packet")
    selected, _ = select_model(packet, registry_path, endpoint)
    if selected.provider != "mistral-vibe":
        raise Rejected("execute requires a registered Mistral Vibe profile")
    task = packet["task"]
    target = resolve_inside(repo, relative_path(task["target"], "target"), "target")
    if not target.is_dir():
        raise Rejected(f"target directory does not exist: {task['target']}")
    for label, path in (("baseline", baseline_path), ("result", result_path), ("trajectory", trajectory_path)):
        try:
            path.resolve().relative_to(target.resolve())
        except ValueError:
            pass
        else:
            raise Rejected(f"{label} must be stored outside the task target")
    baseline = validate_baseline(read_json(baseline_path))
    if (
        baseline["task_id"] != task["id"]
        or baseline["packet_sha256"] != packet_sha
        or baseline["worker"] != ack["worker"]
        or baseline["target"] != task["target"]
    ):
        raise Rejected("baseline is bound to another task, packet, or target")
    before = {item["path"]: item["sha256"] for item in baseline["files"]}
    current = {item["path"]: item["sha256"] for item in target_manifest(target)}
    if current != before:
        raise Rejected("target changed after snapshot and before execute")
    limits = packet["task"]["limits"]
    allowed_commands = [
        expand_argv(argv) for argv in task.get("allowed_commands", [])
    ]
    worker = run_mistral_vibe_worker(
        selected,
        packet,
        target=target,
        write_roots=task["write_roots"],
        allowed_commands=allowed_commands,
        trajectory_path=trajectory_path,
        context_tokens=limits["model_context_tokens"],
        session_tokens=limits["model_session_tokens"],
        output_tokens=limits["model_output_tokens"],
        max_turns=limits["max_tool_calls"],
        command_timeout=limits["verifier_timeout_seconds"],
        timeout=limits["model_timeout_seconds"],
    )
    after = {item["path"]: item["sha256"] for item in target_manifest(target)}
    changed_paths = sorted(
        path for path in set(before) | set(after) if before.get(path) != after.get(path)
    )
    deleted = sorted(path for path in changed_paths if path not in after)
    current_changes = [
        {"path": path, "sha256": after[path]}
        for path in changed_paths
        if path in after
    ]
    write_roots = [relative_path(item, "write_root") for item in task["write_roots"]]
    outside = sorted(
        item["path"]
        for item in current_changes
        if not path_is_writable(PurePosixPath(item["path"]), write_roots)
    )
    success = worker["success"] and bool(current_changes) and not deleted and not outside
    risks = []
    if worker["error"]:
        risks.append(worker["error"])
    if not current_changes:
        risks.append("Worker completed without changing a durable artifact.")
    if deleted:
        risks.append("Worker deleted target files: " + ", ".join(deleted))
    if outside:
        risks.append("Worker changed files outside write_roots: " + ", ".join(outside))
    result = {
        "v": CONTRACT_VERSION,
        "task_id": task["id"],
        "packet_sha256": packet_sha,
        "status": "done" if success else "failed",
        "summary": (
            f"Bounded worker completed with {len(current_changes)} changed file(s); "
            "the full trajectory is stored separately."
        ),
        "changed": current_changes,
        "risks": risks,
    }
    write_json(result_path, result)
    return {
        "status": "completed" if success else "worker_failed",
        "task_id": task["id"],
        "packet_sha256": packet_sha,
        "profile": selected.id,
        "provider": selected.provider,
        "model": selected.model,
        "changed_files": len(current_changes),
        "result": str(result_path),
        "result_sha256": digest_value(result),
        "trajectory": worker["trajectory"],
        "trajectory_sha256": worker["trajectory_sha256"],
        "stderr": worker["stderr"],
        "context_window_tokens": worker["context_window_tokens"],
        "session_token_budget": worker["session_token_budget"],
        "compaction_threshold_tokens": worker["compaction_threshold_tokens"],
        "attestation": worker["attestation"],
    }


def classify_failure(text: str) -> tuple[str, str]:
    lowered = text.lower()
    if "failed to create session directory" in lowered or "permissionerror" in lowered:
        return "session-permission", "rerun with permission for the isolated Vibe home"
    if "token limit exceeded" in lowered:
        return "token-limit", "issue a fresh continuation or repair with a larger session budget"
    if "turn limit" in lowered:
        return "turn-limit", "issue a fresh continuation or repair with more tool turns"
    if "verifier failed" in lowered:
        return "verifier-failure", "diagnose the first verifier and reduce repair write scope"
    if "outside write_roots" in lowered or "outside write roots" in lowered:
        return "write-scope", "reject the output and correct the task boundary"
    if "without changing a durable artifact" in lowered:
        return "no-artifact", "require a durable artifact or use a non-mutating review workflow"
    if "context slice starts after eof" in lowered:
        return "context-eof", "correct the context slice and preflight again"
    if "packet" in lowered and "exceed" in lowered:
        return "packet-budget", "reduce context or raise the packet budget after review"
    return "worker-failure", "inspect the compact result and first stderr diagnostic"


def command_diagnose(
    result_path: Path | None,
    stderr_path: Path | None,
) -> dict[str, Any]:
    if result_path is None and stderr_path is None:
        raise Rejected("diagnose requires --result or --stderr")
    parts: list[str] = []
    task_id = ""
    if result_path is not None:
        result = validate_result(read_json(result_path))
        task_id = result["task_id"]
        parts.extend(result["risks"])
        parts.append(result["summary"])
    if stderr_path is not None:
        try:
            parts.append(stderr_path.read_text(encoding="utf-8", errors="replace"))
        except OSError as exc:
            raise Rejected(f"cannot read stderr {stderr_path}: {exc}") from exc
    text = "\n".join(parts).strip()
    failure_kind, action = classify_failure(text)
    first_line = next((line.strip() for line in text.splitlines() if line.strip()), "")
    return {
        "status": "diagnosed",
        "task_id": task_id,
        "failure_kind": failure_kind,
        "recommended_action": action,
        "detail": first_line[:500],
    }


def command_materialize_plan(
    plan_path: Path,
    output_dir: Path,
    repo: Path,
    registry_path: Path,
) -> dict[str, Any]:
    plan = exact_fields(read_json(plan_path), {"v", "id", "completed", "tasks"}, "plan")
    if plan["v"] != CONTRACT_VERSION:
        raise Rejected("unsupported plan version")
    if type(plan["id"]) is not str or not IDENTIFIER.fullmatch(plan["id"]):
        raise Rejected("invalid plan id")
    completed = string_list(plan["completed"], "plan.completed", 256, 64)
    if len(completed) != len(set(completed)) or any(
        not IDENTIFIER.fullmatch(item) for item in completed
    ):
        raise Rejected("plan.completed contains invalid or duplicate task ids")
    if type(plan["tasks"]) is not list or not plan["tasks"]:
        raise Rejected("plan.tasks must be a non-empty list")
    known = set(completed)
    tasks = []
    for index, raw_task in enumerate(plan["tasks"]):
        task = validate_task(raw_task)
        if task["id"] in known:
            raise Rejected(f"duplicate plan task id: {task['id']}")
        missing = sorted(set(task["depends_on"]) - known)
        if missing:
            raise Rejected(
                f"plan task {task['id']} has unresolved dependencies: {', '.join(missing)}"
            )
        known.add(task["id"])
        preflight_task(task, repo, registry_path)
        tasks.append(task)
    resolved_output = output_dir.resolve()
    for task in tasks:
        target = resolve_inside(repo, relative_path(task["target"], "target"), "target")
        try:
            resolved_output.relative_to(target.resolve())
        except ValueError:
            pass
        else:
            raise Rejected("materialized tasks must be stored outside every task target")
    if output_dir.exists() and any(output_dir.iterdir()):
        raise Rejected("materialize output directory must be absent or empty")
    output_dir.mkdir(parents=True, exist_ok=True)
    written = []
    for index, task in enumerate(tasks, start=1):
        path = output_dir / f"{index:02d}-{task['id']}.task.json"
        write_json(path, task)
        written.append({"path": str(path), "sha256": digest_file(path)})
    return {
        "status": "materialized",
        "plan_id": plan["id"],
        "tasks": written,
    }


def validate_ack(raw: Any) -> dict[str, Any]:
    ack = exact_fields(
        raw, {"v", "task_id", "packet_sha256", "worker", "accepted", "reason"}, "ack"
    )
    if ack["v"] != CONTRACT_VERSION or type(ack["accepted"]) is not bool:
        raise Rejected("invalid acknowledgement")
    nonempty_text(ack["task_id"], "ack.task_id", 64)
    nonempty_text(ack["worker"], "ack.worker", 128)
    if type(ack["packet_sha256"]) is not str or not HEX64.fullmatch(ack["packet_sha256"]):
        raise Rejected("invalid acknowledgement packet digest")
    if type(ack["reason"]) is not str or len(ack["reason"]) > 1000:
        raise Rejected("invalid acknowledgement reason")
    if not ack["accepted"] and not ack["reason"].strip():
        raise Rejected("rejected acknowledgement needs a reason")
    return ack


def path_is_writable(path: PurePosixPath, roots: list[PurePosixPath]) -> bool:
    return path in roots


def expand_argv(argv: list[str]) -> list[str]:
    return [sys.executable if item == "{python}" else item for item in argv]


def audit_baseline(
    baseline_path: Path,
    task: dict[str, Any],
    packet_sha: str,
    target: Path,
    result_path: Path,
    worker: str,
    reported_paths: set[str],
    write_roots: list[PurePosixPath],
) -> dict[str, Any]:
    baseline_resolved = baseline_path.resolve()
    try:
        baseline_resolved.relative_to(target.resolve())
    except ValueError:
        pass
    else:
        raise Rejected("baseline must be stored outside the task target")
    baseline = validate_baseline(read_json(baseline_path))
    if (
        baseline["task_id"] != task["id"]
        or baseline["packet_sha256"] != packet_sha
        or baseline["worker"] != worker
        or baseline["target"] != task["target"]
    ):
        raise Rejected("baseline is bound to another task, packet, or target")
    before = {item["path"]: item["sha256"] for item in baseline["files"]}
    current_files = target_manifest(target)
    after = {item["path"]: item["sha256"] for item in current_files}
    ignored: set[str] = set()
    try:
        ignored.add(result_path.resolve().relative_to(target.resolve()).as_posix())
    except ValueError:
        pass
    actual = {
        path
        for path in set(before) | set(after)
        if before.get(path) != after.get(path) and path not in ignored
    }
    deleted = sorted(path for path in actual if path in before and path not in after)
    if deleted:
        raise Rejected("target files were deleted since baseline: " + ", ".join(deleted))
    outside = sorted(
        path
        for path in actual
        if not path_is_writable(PurePosixPath(path), write_roots)
    )
    if outside:
        raise Rejected("baseline found changes outside write_roots: " + ", ".join(outside))
    unreported = sorted(actual - reported_paths)
    if unreported:
        raise Rejected("baseline found unreported changed paths: " + ", ".join(unreported))
    unchanged = sorted(reported_paths - actual)
    if unchanged:
        raise Rejected("result reports paths unchanged from baseline: " + ", ".join(unchanged))
    return {
        "sha256": digest_value(baseline),
        "files_before": len(before),
        "files_after": len(after),
        "changed_paths": len(actual),
    }


def command_gate(
    task_path: Path,
    packet_path: Path,
    ack_path: Path,
    result_path: Path,
    repo: Path,
    baseline_path: Path | None = None,
) -> dict[str, Any]:
    task = validate_task(read_json(task_path))
    packet = validate_packet(read_json(packet_path))
    ack = validate_ack(read_json(ack_path))
    try:
        raw_result_text = result_path.read_text(encoding="utf-8")
        if len(raw_result_text) > task["limits"]["output_chars"]:
            raise Rejected("result exceeds output_chars")
        result = validate_result(json.loads(raw_result_text))
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise Rejected(f"invalid result JSON: {exc}") from exc
    packet_sha = digest_value(packet)
    if packet["task_sha256"] != digest_value(task) or packet["task"] != task:
        raise Rejected("task and packet do not match")
    if not ack["accepted"]:
        raise Rejected("worker rejected the packet")
    for bound in (ack, result):
        if bound["task_id"] != task["id"] or bound["packet_sha256"] != packet_sha:
            raise Rejected("acknowledgement or result is bound to another task")
    if result["status"] != "done":
        raise Rejected(f"worker status is {result['status']}")
    target = resolve_inside(repo, relative_path(task["target"], "target"), "target")
    write_roots = [
        relative_path(item, f"write_roots[{index}]")
        for index, item in enumerate(task["write_roots"])
    ]
    reported_paths = {
        str(relative_path(changed["path"], f"changed[{index}].path"))
        for index, changed in enumerate(result["changed"])
    }
    baseline_audit = (
        audit_baseline(
            baseline_path,
            task,
            packet_sha,
            target,
            result_path,
            ack["worker"],
            reported_paths,
            write_roots,
        )
        if baseline_path is not None
        else None
    )
    verified_files = []
    for index, changed in enumerate(result["changed"]):
        relative = relative_path(changed["path"], f"changed[{index}].path")
        if not path_is_writable(relative, write_roots):
            raise Rejected(f"changed path is outside write_roots: {relative}")
        path = resolve_inside(target, relative, f"changed[{index}].path")
        if not path.is_file():
            raise Rejected(f"changed artifact is not a file: {relative}")
        actual = digest_file(path)
        if actual != changed["sha256"]:
            raise Rejected(f"changed artifact digest mismatch: {relative}")
        verified_files.append({"path": str(relative), "sha256": actual})
    checks = []
    timeout = task["limits"]["verifier_timeout_seconds"]
    for verifier in task["verifiers"]:
        try:
            completed = subprocess.run(
                expand_argv(verifier["argv"]),
                cwd=target,
                shell=False,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=timeout,
                check=False,
            )
        except (OSError, subprocess.TimeoutExpired) as exc:
            raise Rejected(f"verifier {verifier['id']} could not complete: {exc}") from exc
        checks.append(
            {
                "id": verifier["id"],
                "exit_code": completed.returncode,
                "stdout_tail": completed.stdout[-1000:],
                "stderr_tail": completed.stderr[-1000:],
            }
        )
        if completed.returncode != 0:
            raise Rejected(f"verifier failed: {verifier['id']}")
    output = {
        "status": "passed",
        "task_id": task["id"],
        "packet_sha256": packet_sha,
        "worker": ack["worker"],
        "verified_files": verified_files,
        "checks": checks,
        "risks": result["risks"],
    }
    if baseline_audit is not None:
        output["baseline_audit"] = baseline_audit
    return output


def command_run(
    task_path: Path,
    evidence_dir: Path,
    worker: str,
    repo: Path,
    registry_path: Path,
    endpoint: str,
) -> dict[str, Any]:
    preflight = command_preflight(task_path, repo, registry_path)
    task = validate_task(read_json(task_path))
    target = resolve_inside(repo, relative_path(task["target"], "target"), "target")
    resolved_evidence = evidence_dir.resolve()
    try:
        resolved_evidence.relative_to(target.resolve())
    except ValueError:
        pass
    else:
        raise Rejected("run evidence must be stored outside the task target")
    if evidence_dir.exists() and any(evidence_dir.iterdir()):
        raise Rejected("run evidence directory must be absent or empty")
    evidence_dir.mkdir(parents=True, exist_ok=True)
    paths = {
        name: evidence_dir / filename
        for name, filename in {
            "packet": "packet.json",
            "route": "route.json",
            "ack": "ack.json",
            "baseline": "baseline.json",
            "result": "result.json",
            "trajectory": "trajectory.json",
            "gate": "gate.json",
            "run": "run.json",
        }.items()
    }
    packed = command_pack(task_path, paths["packet"], repo)
    routed = command_route(paths["packet"], registry_path, endpoint)
    write_json(paths["route"], routed)
    accepted = command_accept(paths["packet"], paths["ack"], worker, None)
    snapshotted = command_snapshot(
        task_path,
        paths["packet"],
        paths["ack"],
        paths["baseline"],
        repo,
    )
    executed = command_execute(
        paths["packet"],
        paths["ack"],
        paths["baseline"],
        paths["result"],
        paths["trajectory"],
        repo,
        registry_path,
        endpoint,
    )
    base = {
        "task_id": task["id"],
        "evidence": str(evidence_dir),
        "preflight": preflight,
        "packet_sha256": packed["packet_sha256"],
        "route": routed,
        "worker": accepted["worker"],
        "baseline_sha256": snapshotted["baseline_sha256"],
        "execution": executed,
    }
    if executed["status"] != "completed":
        stderr = Path(executed["stderr"]) if executed.get("stderr") else None
        diagnosis = command_diagnose(
            paths["result"],
            stderr if stderr is not None and stderr.is_file() else None,
        )
        output = {"status": "worker_failed", "stage": "execute", **base, "diagnosis": diagnosis}
        write_json(paths["run"], output)
        return output
    gated = command_gate(
        task_path,
        paths["packet"],
        paths["ack"],
        paths["result"],
        repo,
        paths["baseline"],
    )
    write_json(paths["gate"], gated)
    output = {"status": "passed", "stage": "gate", **base, "gate": gated}
    write_json(paths["run"], output)
    return output


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(description=__doc__)
    commands = root.add_subparsers(dest="command", required=True)
    inventory = commands.add_parser("inventory")
    inventory.add_argument(
        "--registry", type=Path, default=Path(__file__).with_name("models.json")
    )
    inventory.add_argument(
        "--ollama-endpoint", default="http://127.0.0.1:11434"
    )
    canary = commands.add_parser("canary")
    canary.add_argument("--profile", required=True)
    canary.add_argument(
        "--registry", type=Path, default=Path(__file__).with_name("models.json")
    )
    canary.add_argument(
        "--ollama-endpoint", default="http://127.0.0.1:11434"
    )
    canary.add_argument("--timeout", type=int, default=120)
    preflight = commands.add_parser("preflight")
    preflight.add_argument("task", type=Path)
    preflight.add_argument("--repo", type=Path, default=Path.cwd())
    preflight.add_argument(
        "--registry", type=Path, default=Path(__file__).with_name("models.json")
    )
    pack = commands.add_parser("pack")
    pack.add_argument("task", type=Path)
    pack.add_argument("packet", type=Path)
    pack.add_argument("--repo", type=Path, default=Path.cwd())
    accept = commands.add_parser("accept")
    accept.add_argument("packet", type=Path)
    accept.add_argument("ack", type=Path)
    accept.add_argument("--worker", required=True)
    accept.add_argument("--reject", dest="reject_reason")
    snapshot = commands.add_parser("snapshot")
    snapshot.add_argument("task", type=Path)
    snapshot.add_argument("packet", type=Path)
    snapshot.add_argument("ack", type=Path)
    snapshot.add_argument("baseline", type=Path)
    snapshot.add_argument("--repo", type=Path, default=Path.cwd())
    route = commands.add_parser("route")
    route.add_argument("packet", type=Path)
    route.add_argument(
        "--registry", type=Path, default=Path(__file__).with_name("models.json")
    )
    route.add_argument(
        "--ollama-endpoint", default="http://127.0.0.1:11434"
    )
    execute = commands.add_parser("execute")
    execute.add_argument("packet", type=Path)
    execute.add_argument("ack", type=Path)
    execute.add_argument("baseline", type=Path)
    execute.add_argument("result", type=Path)
    execute.add_argument("trajectory", type=Path)
    execute.add_argument("--repo", type=Path, default=Path.cwd())
    execute.add_argument(
        "--registry", type=Path, default=Path(__file__).with_name("models.json")
    )
    execute.add_argument(
        "--ollama-endpoint", default="http://127.0.0.1:11434"
    )
    gate = commands.add_parser("gate")
    gate.add_argument("task", type=Path)
    gate.add_argument("packet", type=Path)
    gate.add_argument("ack", type=Path)
    gate.add_argument("result", type=Path)
    gate.add_argument("--baseline", type=Path)
    gate.add_argument("--repo", type=Path, default=Path.cwd())
    diagnose = commands.add_parser("diagnose")
    diagnose.add_argument("--result", type=Path)
    diagnose.add_argument("--stderr", type=Path)
    materialize = commands.add_parser("materialize-plan")
    materialize.add_argument("plan", type=Path)
    materialize.add_argument("output", type=Path)
    materialize.add_argument("--repo", type=Path, default=Path.cwd())
    materialize.add_argument(
        "--registry", type=Path, default=Path(__file__).with_name("models.json")
    )
    run = commands.add_parser("run")
    run.add_argument("task", type=Path)
    run.add_argument("evidence", type=Path)
    run.add_argument("--worker", required=True)
    run.add_argument("--repo", type=Path, default=Path.cwd())
    run.add_argument(
        "--registry", type=Path, default=Path(__file__).with_name("models.json")
    )
    run.add_argument(
        "--ollama-endpoint", default="http://127.0.0.1:11434"
    )
    return root


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    try:
        if args.command == "inventory":
            output = command_inventory(args.registry, args.ollama_endpoint)
        elif args.command == "canary":
            output = command_canary(
                args.profile,
                args.registry,
                args.ollama_endpoint,
                args.timeout,
            )
        elif args.command == "preflight":
            output = command_preflight(args.task, args.repo, args.registry)
        elif args.command == "pack":
            output = command_pack(args.task, args.packet, args.repo)
        elif args.command == "accept":
            output = command_accept(
                args.packet, args.ack, args.worker, args.reject_reason
            )
        elif args.command == "snapshot":
            output = command_snapshot(
                args.task, args.packet, args.ack, args.baseline, args.repo
            )
        elif args.command == "route":
            output = command_route(
                args.packet, args.registry, args.ollama_endpoint
            )
        elif args.command == "execute":
            output = command_execute(
                args.packet,
                args.ack,
                args.baseline,
                args.result,
                args.trajectory,
                args.repo,
                args.registry,
                args.ollama_endpoint,
            )
        elif args.command == "gate":
            output = command_gate(
                args.task,
                args.packet,
                args.ack,
                args.result,
                args.repo,
                args.baseline,
            )
        elif args.command == "diagnose":
            output = command_diagnose(args.result, args.stderr)
        elif args.command == "materialize-plan":
            output = command_materialize_plan(
                args.plan, args.output, args.repo, args.registry
            )
        else:
            output = command_run(
                args.task,
                args.evidence,
                args.worker,
                args.repo,
                args.registry,
                args.ollama_endpoint,
            )
    except (Rejected, ModelRejected, OSError) as exc:
        print(json.dumps({"status": "rejected", "reason": str(exc)}, sort_keys=True))
        return 2
    print(json.dumps(output, ensure_ascii=False, sort_keys=True))
    return 2 if output.get("status") in {"failed", "worker_failed"} else 0


if __name__ == "__main__":
    raise SystemExit(main())
