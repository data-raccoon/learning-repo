"""Manage the staged, small-context workflow for a Fabric 26.2 mod."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
from pathlib import Path, PurePosixPath
import re
import shutil
import sys
from typing import Any


PACKAGE_ROOT = Path(__file__).resolve().parent
WORKSPACE = PACKAGE_ROOT.parent.parent
HARNESS_PATH = WORKSPACE / "model-execution-harness" / "core" / "harness.py"
STATE_NAME = ".mc-mod-agents"
SLUG = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*\Z")
PLACEHOLDER = re.compile(r"\[(?:TBD|What|List|Description|From |Current |Target |Used |One sentence|single-player|5 minutes)", re.IGNORECASE)
PROTECTED_TARGET_ROOTS = {
    ".agents", ".codex", ".git", "agent-packs", "local-models", "model-execution-harness",
}

PINS = {
    "minecraft_version": "26.2",
    "fabric_loader_version": "0.19.3",
    "fabric_api_version": "0.154.2+26.2",
    "fabric_loom_version": "1.17-SNAPSHOT",
    "gradle_version": "9.5.1",
    "java_version": "25",
}
STANDARD_VERIFIERS = {
    "compile-common": "compileJava",
    "compile-client": "compileClientJava",
    "unit-tests": "test",
    "build": "build",
}
CORE_ENGINEER_FILES = {
    "build.gradle",
    "settings.gradle",
    "gradle.properties",
    "gradlew",
    "gradlew.bat",
    "gradle/wrapper/gradle-wrapper.jar",
    "gradle/wrapper/gradle-wrapper.properties",
    "src/main/resources/fabric.mod.json",
}
APPROVED_DESIGN_PATHS = (
    f"{STATE_NAME}/intent.md",
    f"{STATE_NAME}/context/roles/mod-architect.md",
    f"{STATE_NAME}/context/templates/mod-brief.md",
    f"{STATE_NAME}/context/templates/acceptance-contract.md",
    f"{STATE_NAME}/context/templates/mod-spec.schema.json",
    "docs/PRODUCT.md",
    "docs/ARCHITECTURE.md",
    "docs/ACCEPTANCE.md",
    "mod-spec.json",
)


class MCModAgentsError(ValueError):
    """A fail-closed lifecycle or contract error."""


def _json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise MCModAgentsError(f"cannot read JSON {path}: {error}") from error


def _write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _relative_file(value: Any, name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise MCModAgentsError(f"{name} must be a non-empty relative file path")
    normalized = value.replace("\\", "/")
    path = PurePosixPath(normalized)
    if path.is_absolute() or ".." in path.parts or "." in path.parts:
        raise MCModAgentsError(f"{name} must not be absolute or traverse parents: {value}")
    if normalized.endswith("/") or not path.name or normalized.startswith(STATE_NAME + "/"):
        raise MCModAgentsError(f"{name} must name a file outside {STATE_NAME}: {value}")
    return path.as_posix()


def _unique_files(value: Any, name: str, *, allow_empty: bool = False) -> list[str]:
    if not isinstance(value, list) or (not value and not allow_empty):
        raise MCModAgentsError(f"{name} must be {'an' if allow_empty else 'a non-empty'} array")
    result = [_relative_file(item, f"{name} item") for item in value]
    if len(result) != len(set(result)):
        raise MCModAgentsError(f"{name} must contain unique files")
    return result


def _reference(path: str) -> dict[str, str]:
    return {"path": path}


def _limits(*, kind: str, critical: bool = False, verifiers: int = 0) -> dict[str, int]:
    session_tokens, tool_calls = {
        "planning": (500_000 if critical else 300_000, 40 if critical else 24),
        "review": (300_000, 20),
        "coding": (800_000, 60),
        "repair": (180_000, 16),
    }[kind]
    return {
        "packet_chars": 70_000 if critical else 50_000,
        "output_chars": 24_000 if critical else 16_000,
        "model_context_tokens": 160_000 if kind == "coding" else 100_000,
        "model_session_tokens": session_tokens,
        "model_output_tokens": 100_000 if kind == "coding" else 8_192,
        "model_timeout_seconds": 1_800,
        "max_tool_calls": tool_calls,
        "max_verifiers": verifiers,
        "verifier_timeout_seconds": 900,
    }


class MCModAgentsManager:
    def __init__(self, workspace: Path = WORKSPACE, package_root: Path = PACKAGE_ROOT):
        self.workspace = workspace.resolve()
        self.package_root = package_root.resolve()

    def target(self, value: str, *, create: bool = False) -> Path:
        normalized = value.replace("\\", "/")
        raw = PurePosixPath(normalized)
        if raw.is_absolute() or ".." in raw.parts or "." in raw.parts or not raw.parts:
            raise MCModAgentsError("target must be a repository-relative subdirectory without traversal")
        if raw.parts[0].casefold() in {item.casefold() for item in PROTECTED_TARGET_ROOTS}:
            raise MCModAgentsError(f"target root is reserved: {raw.parts[0]}")
        current = self.workspace
        for part in raw.parts:
            current = current / part
            if current.is_symlink():
                raise MCModAgentsError(f"target contains a symbolic link: {value}")
        resolved = self.workspace.joinpath(*raw.parts).resolve(strict=False)
        try:
            resolved.relative_to(self.workspace)
        except ValueError as error:
            raise MCModAgentsError("target escapes the repository workspace") from error
        if resolved == self.workspace:
            raise MCModAgentsError("target must not be the repository root")
        if create:
            resolved.mkdir(parents=True, exist_ok=True)
        if not resolved.is_dir():
            raise MCModAgentsError(f"target directory does not exist: {value}")
        return resolved

    def _target_value(self, target: Path) -> str:
        return target.relative_to(self.workspace).as_posix()

    def _task(self, target: Path, *, task_id: str, goal: str, profile: str, capability: str,
              importance: str, context: list[str], write_roots: list[str],
              done: list[str], forbidden: list[str], verifiers: list[dict[str, Any]] | None = None,
              depends_on: list[str] | None = None,
              allowed_commands: list[list[str]] | None = None) -> dict[str, Any]:
        if not isinstance(profile, str) or not profile.strip() or profile == "auto":
            raise MCModAgentsError("profile must name an explicitly selected model")
        checks = verifiers or []
        kind = (
            "planning"
            if capability in {"architecture", "planning"}
            else "review"
            if capability == "review"
            else "coding"
        )
        return {
            "v": 2,
            "id": task_id,
            "kind": kind,
            "depends_on": depends_on or [],
            "goal": goal,
            "target": self._target_value(target),
            "model": {"profile": profile, "capability": capability, "importance": importance},
            "context": [_reference(path) for path in context],
            "write_roots": write_roots,
            "allowed_commands": allowed_commands or [],
            "done": done,
            "forbidden": forbidden,
            "limits": _limits(kind=kind, critical=importance == "critical", verifiers=len(checks)),
            "verifiers": checks,
        }

    def init(self, target_value: str, mod_id: str, profile: str) -> dict[str, Any]:
        if not SLUG.fullmatch(mod_id):
            raise MCModAgentsError("id must be a lowercase kebab-case slug")
        target = self.target(target_value, create=True)
        state = target / STATE_NAME
        if state.exists():
            raise MCModAgentsError(f"mc-mod-agent state already exists: {state}")
        for directory in (state / "context" / "roles", state / "context" / "templates",
                          state / "tasks", state / "tools", state / "evidence"):
            directory.mkdir(parents=True, exist_ok=True)
        for source in sorted((self.package_root / "context" / "roles").glob("*.md")):
            shutil.copyfile(source, state / "context" / "roles" / source.name)
        for source in sorted((self.package_root / "context" / "templates").iterdir()):
            if source.is_file():
                shutil.copyfile(source, state / "context" / "templates" / source.name)
        for source in sorted((self.package_root / "context" / "tools").glob("*.py")):
            shutil.copyfile(source, state / "tools" / source.name)
        intent = (self.package_root / "context" / "templates" / "intent.md").read_text(encoding="utf-8")
        (state / "intent.md").write_text(intent.replace("{{MOD_ID}}", mod_id), encoding="utf-8")
        ownership = {
            "schema_version": 2,
            "mod_id": mod_id,
            "owners": {
                "mod-architect": ["docs/PRODUCT.md", "docs/ARCHITECTURE.md", "docs/ACCEPTANCE.md", "mod-spec.json"],
                "asset-producer": ["docs/style-guide.md", "assets/asset-manifest.json"],
                "mod-engineer": ["docs/IMPLEMENTATION.md"],
                "mod-qa": [f"{STATE_NAME}/evidence/qa-report.json"],
            },
        }
        _write_json(state / "ownership.json", ownership)
        task = self._architect_task(target, mod_id, profile)
        _write_json(state / "tasks" / "01-mod-architect.task.json", task)
        return {
            "status": "initialized",
            "mod_id": mod_id,
            "target": self._target_value(target),
            "next": f"complete {STATE_NAME}/intent.md, then pack 01-mod-architect.task.json",
        }

    def _architect_task(self, target: Path, mod_id: str, profile: str) -> dict[str, Any]:
        return self._task(
            target,
            task_id=f"{mod_id}-mod-architect",
            goal="Produce a small, testable Fabric 26.2 MVP design from the completed intent and supplied contracts.",
            profile=profile,
            capability="architecture",
            importance="critical",
            context=[
                f"{STATE_NAME}/intent.md",
                f"{STATE_NAME}/context/roles/mod-architect.md",
                f"{STATE_NAME}/context/templates/mod-brief.md",
                f"{STATE_NAME}/context/templates/acceptance-contract.md",
                f"{STATE_NAME}/context/templates/mod-spec.schema.json",
                f"{STATE_NAME}/context/templates/mod-spec.example.json",
            ],
            write_roots=["docs/PRODUCT.md", "docs/ARCHITECTURE.md", "docs/ACCEPTANCE.md", "mod-spec.json"],
            done=[
                "All four design artifacts exist and contain no unresolved placeholders.",
                "mod-spec.json uses the pinned Fabric 26.2 toolchain and lists individual files only.",
                "Client/server authority, persistence, networking, and test seams are explicit.",
            ],
            forbidden=[
                "Do not implement Java, Gradle, assets, or tests.",
                "Do not change the pinned toolchain versions.",
                "Do not use network access or introduce unapproved dependencies.",
            ],
            verifiers=[
                {
                    "id": "design-contract",
                    "argv": ["{python}", f"{STATE_NAME}/tools/verify_design.py"],
                }
            ],
        )

    def _mod_id(self, target: Path) -> str:
        value = _json(target / STATE_NAME / "ownership.json")
        mod_id = value.get("mod_id") if isinstance(value, dict) else None
        if not isinstance(mod_id, str) or not SLUG.fullmatch(mod_id):
            raise MCModAgentsError("ownership.json has an invalid mod_id")
        return mod_id

    def _validate_spec(self, target: Path) -> dict[str, Any]:
        spec = _json(target / "mod-spec.json")
        required = {
            "schema_version", "mod_id", "engine", *PINS,
            "entrypoints", "run_argv", "creative_artifacts", "engineer_artifacts", "verifiers",
        }
        if not isinstance(spec, dict) or set(spec) != required or spec.get("schema_version") != 2:
            raise MCModAgentsError("mod-spec.json must contain exactly the version-2 fields")
        if spec.get("mod_id") != self._mod_id(target):
            raise MCModAgentsError("mod-spec mod_id does not match initialized state")
        if spec.get("engine") != "Fabric":
            raise MCModAgentsError("mod-spec engine must be exactly 'Fabric'")
        for field, expected in PINS.items():
            if str(spec.get(field)) != expected:
                raise MCModAgentsError(f"{field} must remain pinned to {expected}")
        entrypoints = spec.get("entrypoints")
        if not isinstance(entrypoints, dict) or "main" not in entrypoints or set(entrypoints) - {"main", "client"}:
            raise MCModAgentsError("entrypoints must contain main and may contain client")
        normalized_entrypoints = {key: _relative_file(value, f"entrypoints.{key}") for key, value in entrypoints.items()}
        if not normalized_entrypoints["main"].startswith("src/main/java/"):
            raise MCModAgentsError("the main entrypoint must be under src/main/java/")
        if "client" in normalized_entrypoints and not normalized_entrypoints["client"].startswith("src/client/java/"):
            raise MCModAgentsError("the client entrypoint must be under src/client/java/")
        if spec.get("run_argv") != ["{gradle}", "runClient"]:
            raise MCModAgentsError("run_argv must be ['{gradle}', 'runClient']")
        creative = _unique_files(spec.get("creative_artifacts"), "creative_artifacts")
        creative_roots = ("src/main/resources/assets/", "src/client/resources/assets/")
        if any(not path.startswith(creative_roots) for path in creative):
            raise MCModAgentsError("creative_artifacts must be individual files under a Fabric resources/assets directory")
        engineer = _unique_files(spec.get("engineer_artifacts"), "engineer_artifacts")
        if not CORE_ENGINEER_FILES.issubset(engineer):
            missing = sorted(CORE_ENGINEER_FILES - set(engineer))
            raise MCModAgentsError("engineer_artifacts is missing required project files: " + ", ".join(missing))
        if any(path not in engineer for path in normalized_entrypoints.values()):
            raise MCModAgentsError("every entrypoint must be listed in engineer_artifacts")
        allowed_roots = ("src/", "tests/", "config/", "gradle/")
        allowed_root_files = {"build.gradle", "settings.gradle", "gradle.properties", "gradlew", "gradlew.bat"}
        if any(path not in allowed_root_files and not path.startswith(allowed_roots) for path in engineer):
            raise MCModAgentsError("engineer_artifacts contains a file outside the approved engineering roots")
        if set(creative) & set(engineer) or any(path.startswith(creative_roots) for path in engineer):
            raise MCModAgentsError("Creative and Engineering ownership must be disjoint")
        verifiers = spec.get("verifiers")
        if verifiers != list(STANDARD_VERIFIERS):
            raise MCModAgentsError("verifiers must be the fixed standard verifier ID list")
        return {
            **spec,
            "entrypoints": normalized_entrypoints,
            "creative_artifacts": creative,
            "engineer_artifacts": engineer,
        }

    @staticmethod
    def _require_complete_document(path: Path) -> None:
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeError) as error:
            raise MCModAgentsError(f"required document is missing or unreadable: {path}") from error
        if len(text.strip()) < 80 or "[TBD" in text or "{{" in text or PLACEHOLDER.search(text):
            raise MCModAgentsError(f"document contains unresolved placeholders or is incomplete: {path}")

    def check_design(self, target_value: str) -> dict[str, Any]:
        target = self.target(target_value)
        self._require_complete_document(target / STATE_NAME / "intent.md")
        for name in ("PRODUCT.md", "ARCHITECTURE.md", "ACCEPTANCE.md"):
            self._require_complete_document(target / "docs" / name)
        spec = self._validate_spec(target)
        return {"status": "valid", "mod_id": spec["mod_id"], "schema_version": spec["schema_version"]}

    def approve(self, target_value: str) -> dict[str, Any]:
        target = self.target(target_value)
        design = self.check_design(target_value)
        paths = [target / name for name in APPROVED_DESIGN_PATHS]
        hashes = {path.relative_to(target).as_posix(): _sha256(path) for path in paths}
        approval = {
            "schema_version": 2,
            "mod_id": design["mod_id"],
            "approved_by": "human-cli",
            "approved_at": datetime.now(timezone.utc).isoformat(),
            "sha256": hashes,
        }
        _write_json(target / STATE_NAME / "approval.json", approval)
        return {"status": "approved", "mod_id": design["mod_id"], "sha256": hashes}

    def _verified_approval(self, target: Path) -> dict[str, Any]:
        approval = _json(target / STATE_NAME / "approval.json")
        if not isinstance(approval, dict) or approval.get("schema_version") != 2 or approval.get("mod_id") != self._mod_id(target):
            raise MCModAgentsError("approval manifest is invalid")
        hashes = approval.get("sha256")
        if not isinstance(hashes, dict) or set(hashes) != set(APPROVED_DESIGN_PATHS):
            raise MCModAgentsError("approval manifest does not cover every design input and output")
        stale = sorted(name for name, expected in hashes.items() if not (target / name).is_file() or _sha256(target / name) != expected)
        if stale:
            raise MCModAgentsError("approval is stale for: " + ", ".join(stale))
        return approval

    def materialize_build(self, target_value: str, profile: str) -> dict[str, Any]:
        target = self.target(target_value)
        approval = self._verified_approval(target)
        spec = self._validate_spec(target)
        state = target / STATE_NAME
        task = self._task(
            target,
            task_id=f"{approval['mod_id']}-asset-producer",
            goal="Create the approved original or procedural Fabric resource files and a complete provenance manifest.",
            profile=profile,
            capability="coding",
            importance="normal",
            context=[
                f"{STATE_NAME}/context/roles/asset-producer.md",
                f"{STATE_NAME}/context/templates/asset-manifest.schema.json",
                "docs/PRODUCT.md", "docs/ARCHITECTURE.md", "docs/ACCEPTANCE.md", "mod-spec.json",
            ],
            write_roots=["docs/style-guide.md", "assets/asset-manifest.json", *spec["creative_artifacts"]],
            done=[
                "Every declared creative artifact exists at its exact Fabric resource path.",
                "assets/asset-manifest.json records every creative artifact with provenance and SHA-256.",
                "docs/style-guide.md explains the visual and accessibility rules used.",
            ],
            forbidden=[
                "Do not edit Java, Gradle, approved design documents, mod-spec.json, or agent state.",
                "Do not download assets or use material with unclear licensing.",
            ],
            verifiers=[{"id": "asset-contract", "argv": ["{python}", f"{STATE_NAME}/tools/verify_assets.py"]}],
            depends_on=[f"{approval['mod_id']}-mod-architect"],
            allowed_commands=[
                [
                    "{python}", "-m", "unittest", "discover", "-s",
                    f"{STATE_NAME}/tools", "-p", "test_assets.py", "-v",
                ]
            ],
        )
        _write_json(state / "tasks" / "02-asset-producer.task.json", task)
        ownership = _json(state / "ownership.json")
        ownership["owners"]["asset-producer"] = ["docs/style-guide.md", "assets/asset-manifest.json", *spec["creative_artifacts"]]
        _write_json(state / "ownership.json", ownership)
        return {"status": "materialized", "phase": "assets", "task": f"{STATE_NAME}/tasks/02-asset-producer.task.json"}

    def _validate_assets(self, target: Path, spec: dict[str, Any]) -> None:
        for name in ("docs/style-guide.md", "assets/asset-manifest.json", *spec["creative_artifacts"]):
            if not (target / name).is_file():
                raise MCModAgentsError(f"asset phase output is missing: {name}")
        manifest = _json(target / "assets" / "asset-manifest.json")
        if not isinstance(manifest, dict) or manifest.get("mod_id") != spec["mod_id"]:
            raise MCModAgentsError("asset manifest is invalid or has the wrong mod_id")
        entries = manifest.get("assets")
        paths = [item.get("path") for item in entries] if isinstance(entries, list) and all(isinstance(item, dict) for item in entries) else []
        if set(paths) != set(spec["creative_artifacts"]):
            raise MCModAgentsError("asset manifest paths do not exactly match creative_artifacts")

    def materialize_engineer(self, target_value: str, profile: str) -> dict[str, Any]:
        target = self.target(target_value)
        approval = self._verified_approval(target)
        spec = self._validate_spec(target)
        self._validate_assets(target, spec)
        state = target / STATE_NAME
        asset_evidence = state / "evidence" / "asset-gate.json"
        if not asset_evidence.is_file() or _json(asset_evidence).get("gate", {}).get("status") != "passed":
            raise MCModAgentsError("record a passing asset gate before materializing Engineering")
        verifiers = [
            {"id": verifier_id, "argv": ["{python}", f"{STATE_NAME}/tools/run_gradle.py", task]}
            for verifier_id, task in STANDARD_VERIFIERS.items()
        ]
        task = self._task(
            target,
            task_id=f"{approval['mod_id']}-mod-engineer",
            goal="Implement the approved Fabric 26.2 mod and its tests using the completed creative package.",
            profile=profile,
            capability="coding",
            importance="high",
            context=[
                f"{STATE_NAME}/context/roles/mod-engineer.md",
                f"{STATE_NAME}/context/templates/handoff.md",
                "docs/PRODUCT.md", "docs/ARCHITECTURE.md", "docs/ACCEPTANCE.md", "mod-spec.json",
                "docs/style-guide.md", "assets/asset-manifest.json",
            ],
            write_roots=["docs/IMPLEMENTATION.md", *spec["engineer_artifacts"]],
            done=[
                "Every declared engineering artifact exists as an individual file.",
                "The implementation preserves common/client source-set isolation and server authority.",
                "docs/IMPLEMENTATION.md maps behavior and tests to the approved acceptance contract.",
                "All four trusted Gradle verifiers pass.",
            ],
            forbidden=[
                "Do not edit approved design files, creative files, mod-spec.json, or agent state.",
                "Do not download dependencies manually, change pinned versions, use Forge APIs, or add unjustified mixins.",
            ],
            verifiers=verifiers,
            depends_on=[f"{approval['mod_id']}-asset-producer"],
            allowed_commands=[
                ["gradlew.bat", "compileJava", "--no-daemon"],
                ["gradlew.bat", "compileClientJava", "--no-daemon"],
                ["gradlew.bat", "test", "--no-daemon"],
                ["gradlew.bat", "build", "--no-daemon"],
            ],
        )
        _write_json(state / "tasks" / "03-mod-engineer.task.json", task)
        ownership = _json(state / "ownership.json")
        ownership["owners"]["mod-engineer"] = ["docs/IMPLEMENTATION.md", *spec["engineer_artifacts"]]
        _write_json(state / "ownership.json", ownership)
        return {"status": "materialized", "phase": "engineering", "task": f"{STATE_NAME}/tasks/03-mod-engineer.task.json"}

    def record_asset_gate(self, target_value: str, gate_path: str) -> dict[str, Any]:
        target = self.target(target_value)
        self._verified_approval(target)
        source = Path(gate_path).resolve()
        gate = _json(source)
        expected_id = f"{self._mod_id(target)}-asset-producer"
        checks = gate.get("checks") if isinstance(gate, dict) else None
        valid_check = (
            isinstance(checks, list)
            and len(checks) == 1
            and checks[0].get("id") == "asset-contract"
            and checks[0].get("exit_code") == 0
        )
        if not isinstance(gate, dict) or gate.get("status") != "passed" or gate.get("task_id") != expected_id or not valid_check:
            raise MCModAgentsError("gate result is not a passing asset-contract result for the current Asset task")
        evidence = {
            "schema_version": 1,
            "recorded_at": datetime.now(timezone.utc).isoformat(),
            "source_sha256": _sha256(source),
            "gate": gate,
        }
        destination = target / STATE_NAME / "evidence" / "asset-gate.json"
        _write_json(destination, evidence)
        return {"status": "recorded", "evidence": destination.relative_to(target).as_posix(), "sha256": _sha256(destination)}

    def record_build_gate(self, target_value: str, gate_path: str) -> dict[str, Any]:
        target = self.target(target_value)
        self._verified_approval(target)
        gate = _json(Path(gate_path).resolve())
        expected_id = f"{self._mod_id(target)}-mod-engineer"
        if not isinstance(gate, dict) or gate.get("status") != "passed" or gate.get("task_id") != expected_id:
            raise MCModAgentsError("gate result is not a passing result for the current engineer task")
        checks = gate.get("checks")
        ids = {item.get("id") for item in checks} if isinstance(checks, list) and all(isinstance(item, dict) for item in checks) else set()
        if ids != set(STANDARD_VERIFIERS) or any(item.get("exit_code") != 0 for item in checks):
            raise MCModAgentsError("gate result does not contain every passing standard verifier")
        evidence = {
            "schema_version": 1,
            "recorded_at": datetime.now(timezone.utc).isoformat(),
            "source_sha256": _sha256(Path(gate_path).resolve()),
            "gate": gate,
        }
        destination = target / STATE_NAME / "evidence" / "build-gate.json"
        _write_json(destination, evidence)
        return {"status": "recorded", "evidence": destination.relative_to(target).as_posix(), "sha256": _sha256(destination)}

    def materialize_qa(self, target_value: str, profile: str) -> dict[str, Any]:
        target = self.target(target_value)
        approval = self._verified_approval(target)
        spec = self._validate_spec(target)
        evidence_path = target / STATE_NAME / "evidence" / "build-gate.json"
        if not evidence_path.is_file():
            raise MCModAgentsError("record a passing engineer gate before materializing QA")
        evidence = _json(evidence_path)
        if evidence.get("gate", {}).get("status") != "passed":
            raise MCModAgentsError("recorded build evidence is not passing")
        required = ["docs/IMPLEMENTATION.md", *spec["creative_artifacts"], *spec["engineer_artifacts"]]
        missing = [name for name in required if not (target / name).is_file()]
        if missing:
            raise MCModAgentsError("QA inputs are missing: " + ", ".join(missing))
        task = self._task(
            target,
            task_id=f"{approval['mod_id']}-mod-qa",
            goal="Audit the implementation and the already-completed trusted gate evidence; return one QA report matching the supplied schema.",
            profile=profile,
            capability="review",
            importance="high",
            context=[
                f"{STATE_NAME}/context/roles/mod-qa.md",
                f"{STATE_NAME}/context/templates/qa-report.schema.json",
                f"{STATE_NAME}/evidence/build-gate.json",
                "docs/PRODUCT.md", "docs/ARCHITECTURE.md", "docs/ACCEPTANCE.md", "mod-spec.json",
                "docs/style-guide.md", "assets/asset-manifest.json", "docs/IMPLEMENTATION.md",
            ],
            write_roots=[f"{STATE_NAME}/evidence/qa-report.json"],
            done=[
                "The response is one JSON object conforming to qa-report.schema.json.",
                "Verifier results reproduce the supplied build-gate evidence without invention.",
                "Every finding has concrete evidence and exactly one owner.",
            ],
            forbidden=[
                "Do not edit repository files; the root may materialize the validated report afterward.",
                "Do not rerun verifiers, repair findings, or claim coverage absent from the evidence.",
            ],
            verifiers=[
                {
                    "id": "qa-report-contract",
                    "argv": ["{python}", f"{STATE_NAME}/tools/verify_qa_report.py"],
                }
            ],
            depends_on=[f"{approval['mod_id']}-mod-engineer"],
        )
        path = target / STATE_NAME / "tasks" / "04-mod-qa.task.json"
        _write_json(path, task)
        return {"status": "materialized", "phase": "qa", "task": path.relative_to(target).as_posix()}

    @staticmethod
    def _harness_validate_task(task: Any) -> None:
        if not HARNESS_PATH.is_file():
            raise MCModAgentsError("model-execution-harness/core/harness.py is unavailable")
        harness_dir = str(HARNESS_PATH.parent)
        if harness_dir not in sys.path:
            sys.path.insert(0, harness_dir)
        spec = importlib.util.spec_from_file_location("mc_mod_small_context_harness", HARNESS_PATH)
        if spec is None or spec.loader is None:
            raise MCModAgentsError("cannot load small-context harness validator")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        try:
            module.validate_task(task)
        except Exception as error:
            raise MCModAgentsError(f"small-context task validation failed: {error}") from error

    def validate(self, target_value: str) -> dict[str, Any]:
        target = self.target(target_value)
        state = target / STATE_NAME
        if not state.is_dir():
            raise MCModAgentsError("target has not been initialized")
        self._require_complete_document(state / "intent.md")
        task_paths = sorted((state / "tasks").glob("*.task.json"))
        if not task_paths:
            raise MCModAgentsError("no small-context tasks are materialized")
        checked = []
        legacy_auto_profiles = []
        for task_path in task_paths:
            task = _json(task_path)
            if task.get("model", {}).get("profile") == "auto":
                legacy = json.loads(json.dumps(task))
                legacy["model"]["profile"] = "legacy-unroutable"
                self._harness_validate_task(legacy)
                legacy_auto_profiles.append(task["id"])
            else:
                self._harness_validate_task(task)
            if task.get("target") != self._target_value(target):
                raise MCModAgentsError(f"task target mismatch: {task_path.name}")
            for source in task["context"]:
                context_path = target / source["path"]
                if not context_path.is_file():
                    raise MCModAgentsError(f"task context is missing: {source['path']}")
            checked.append(task["id"])
        phase = "qa" if any(name.endswith("mod-qa") for name in checked) else "engineering" if any(name.endswith("mod-engineer") for name in checked) else "assets" if any(name.endswith("asset-producer") for name in checked) else "architect"
        result = {"status": "valid", "mod_id": self._mod_id(target), "tasks": checked, "phase": phase}
        if legacy_auto_profiles:
            result["legacy_auto_profile_tasks"] = legacy_auto_profiles
        return result


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    initialize = commands.add_parser("init")
    initialize.add_argument("--target", required=True)
    initialize.add_argument("--id", required=True)
    initialize.add_argument("--profile", required=True)
    for name in ("check-design", "approve", "validate"):
        command = commands.add_parser(name)
        command.add_argument("--target", required=True)
    for name in ("materialize-build", "materialize-engineer", "materialize-qa"):
        command = commands.add_parser(name)
        command.add_argument("--target", required=True)
        command.add_argument("--profile", required=True)
    for name in ("record-asset-gate", "record-build-gate"):
        record = commands.add_parser(name)
        record.add_argument("--target", required=True)
        record.add_argument("--gate", required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    manager = MCModAgentsManager()
    try:
        if args.command == "init":
            result = manager.init(args.target, args.id, args.profile)
        elif args.command == "check-design":
            result = manager.check_design(args.target)
        elif args.command == "approve":
            result = manager.approve(args.target)
        elif args.command == "materialize-build":
            result = manager.materialize_build(args.target, args.profile)
        elif args.command == "materialize-engineer":
            result = manager.materialize_engineer(args.target, args.profile)
        elif args.command == "record-asset-gate":
            result = manager.record_asset_gate(args.target, args.gate)
        elif args.command == "record-build-gate":
            result = manager.record_build_gate(args.target, args.gate)
        elif args.command == "materialize-qa":
            result = manager.materialize_qa(args.target, args.profile)
        else:
            result = manager.validate(args.target)
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return 0
    except MCModAgentsError as error:
        print(json.dumps({"status": "error", "error": str(error)}, indent=2, ensure_ascii=False))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
