"""Scaffold and validate engine-neutral gaming-agent job packets."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import shutil
import sys
from typing import Any


PACKAGE_ROOT = Path(__file__).resolve().parent
WORKSPACE = PACKAGE_ROOT.parent
STATE_NAME = ".game-agents"
SLUG = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*\Z")
PROTECTED_TARGET_ROOTS = {".agents", ".git", "agent-orchestrator", "gaming-agents", "local-models"}
SAFE_VERIFIER_EXECUTABLES = {"{python}", "python", "python.exe", "py", "py.exe", "node", "node.exe", "npm", "npm.cmd", "git", "git.exe"}


class GamingAgentsError(ValueError):
    pass


def _json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise GamingAgentsError(f"cannot read JSON {path}: {error}") from error


def _write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _relative_path(value: str, name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise GamingAgentsError(f"{name} must be a non-empty relative path")
    path = Path(value)
    if path.is_absolute() or ".." in path.parts or value.startswith(("/", "\\")):
        raise GamingAgentsError(f"{name} must not be absolute or traverse parents: {value}")
    normalized = path.as_posix().lstrip("./")
    if not normalized or normalized == "." or normalized.startswith(STATE_NAME + "/"):
        raise GamingAgentsError(f"{name} is reserved or invalid: {value}")
    return normalized


def _unique_paths(value: Any, name: str) -> list[str]:
    if not isinstance(value, list) or not value:
        raise GamingAgentsError(f"{name} must be a non-empty array")
    result = [_relative_path(item, f"{name} item") for item in value]
    if len(result) != len(set(result)):
        raise GamingAgentsError(f"{name} must contain unique paths")
    return result


class GamingAgentsManager:
    def __init__(self, workspace: Path = WORKSPACE, package_root: Path = PACKAGE_ROOT):
        self.workspace = workspace.resolve()
        self.package_root = package_root.resolve()

    def target(self, value: str, *, create: bool = False) -> Path:
        raw = Path(value)
        if raw.is_absolute() or ".." in raw.parts or not raw.parts:
            raise GamingAgentsError("target must be a repository-relative subdirectory without traversal")
        if raw.parts[0] in PROTECTED_TARGET_ROOTS:
            raise GamingAgentsError(f"target root is reserved: {raw.parts[0]}")
        current = self.workspace
        for part in raw.parts:
            current = current / part
            if current.is_symlink():
                raise GamingAgentsError(f"target contains a symbolic link: {value}")
        resolved = (self.workspace / raw).resolve(strict=False)
        if resolved == self.workspace or self.workspace not in resolved.parents:
            raise GamingAgentsError("target escapes the repository workspace")
        if create:
            resolved.mkdir(parents=True, exist_ok=True)
        if not resolved.is_dir():
            raise GamingAgentsError(f"target directory does not exist: {value}")
        return resolved

    def _target_value(self, target: Path) -> str:
        return target.relative_to(self.workspace).as_posix()

    def init(self, target_value: str, game_id: str) -> dict[str, Any]:
        if not SLUG.fullmatch(game_id):
            raise GamingAgentsError("id must be a lowercase kebab-case slug")
        target = self.target(target_value, create=True)
        state = target / STATE_NAME
        if state.exists():
            raise GamingAgentsError(f"gaming-agent state already exists: {state}")
        context = state / "context"
        jobs = state / "jobs"
        for directory in (context / "roles", context / "templates", jobs, state / "evidence"):
            directory.mkdir(parents=True, exist_ok=True)
        for source in sorted((self.package_root / "roles").glob("*.md")):
            shutil.copyfile(source, context / "roles" / source.name)
        for source in sorted((self.package_root / "templates").iterdir()):
            if source.is_file():
                shutil.copyfile(source, context / "templates" / source.name)
        intent = (self.package_root / "templates" / "intent.md").read_text(encoding="utf-8").replace("{{GAME_ID}}", game_id)
        (state / "intent.md").write_text(intent, encoding="utf-8")
        target_dir = self._target_value(target)
        director = {
            "schema_version": 1,
            "id": f"{game_id}-game-director",
            "objective": "Create the complete approved-design candidate described by the intent. Write exactly docs/game-brief.md, docs/acceptance-contract.md, and docs/game-spec.json from the supplied templates and role contract.",
            "target_dir": target_dir,
            "mode": "write",
            "importance": "critical",
            "risk": "medium",
            "tool_class": "files_write",
            "required_capabilities": ["reasoning", "review", "file-editing"],
            "context": [
                f"{STATE_NAME}/intent.md",
                f"{STATE_NAME}/context/roles/game-director.md",
                f"{STATE_NAME}/context/templates/game-brief.md",
                f"{STATE_NAME}/context/templates/acceptance-contract.md",
                f"{STATE_NAME}/context/templates/game-spec.example.json",
            ],
            "expected_artifacts": ["docs/game-brief.md", "docs/acceptance-contract.md", "docs/game-spec.json"],
            "allowed_write_paths": ["docs/game-brief.md", "docs/acceptance-contract.md", "docs/game-spec.json"],
            "verifiers": [],
            "dependencies": [],
            "limits": {"timeout_seconds": 900, "max_turns": 12, "max_tokens": 30000},
        }
        _write_json(jobs / "01-game-director.json", director)
        _write_json(jobs / "01-game-director.graph.json", {
            "schema_version": 1, "max_parallel": 1, "jobs": ["01-game-director.json"],
        })
        _write_json(state / "ownership.json", {
            "schema_version": 1,
            "game_id": game_id,
            "owners": {
                "game-director": ["docs/game-brief.md", "docs/acceptance-contract.md", "docs/game-spec.json"],
                "creative-producer": ["assets", "docs/style-guide.md"],
                "gameplay-engineer": ["src", "tests", "config", "docs/architecture.md", "docs/implementation-handoff.md"],
                "qa-playtest": [],
            },
        })
        return {"status": "initialized", "game_id": game_id, "target": target_dir, "director_graph": str((jobs / "01-game-director.graph.json").relative_to(self.workspace))}

    def _game_id(self, target: Path) -> str:
        value = _json(target / STATE_NAME / "ownership.json")
        game_id = value.get("game_id") if isinstance(value, dict) else None
        if not isinstance(game_id, str) or not SLUG.fullmatch(game_id):
            raise GamingAgentsError("ownership.json has an invalid game_id")
        return game_id

    def _validate_spec(self, target: Path) -> dict[str, Any]:
        spec = _json(target / "docs" / "game-spec.json")
        required = {"schema_version", "game_id", "engine", "entrypoint", "run_argv", "creative_artifacts", "engineer_artifacts", "verifiers"}
        if not isinstance(spec, dict) or set(spec) != required or spec.get("schema_version") != 1:
            raise GamingAgentsError("game-spec.json must contain exactly the version-1 fields")
        if spec.get("game_id") != self._game_id(target):
            raise GamingAgentsError("game-spec game_id does not match initialized state")
        if not isinstance(spec.get("engine"), str) or not spec["engine"].strip():
            raise GamingAgentsError("game-spec engine is required")
        entrypoint = _relative_path(spec.get("entrypoint"), "entrypoint")
        run_argv = spec.get("run_argv")
        if not isinstance(run_argv, list) or not run_argv or any(not isinstance(item, str) or not item for item in run_argv):
            raise GamingAgentsError("run_argv must be a non-empty string array")
        creative = _unique_paths(spec.get("creative_artifacts"), "creative_artifacts")
        if any(not value.startswith("assets/") for value in creative):
            raise GamingAgentsError("creative_artifacts must be files under assets/")
        engineer = _unique_paths(spec.get("engineer_artifacts"), "engineer_artifacts")
        if entrypoint not in engineer:
            raise GamingAgentsError("entrypoint must be listed in engineer_artifacts")
        if set(creative) & set(engineer) or any(value.startswith("assets/") for value in engineer):
            raise GamingAgentsError("Creative and Engineering artifact ownership must be disjoint")
        if any("/" in value and value.split("/", 1)[0] not in {"src", "tests", "config"} for value in engineer):
            raise GamingAgentsError("nested engineer_artifacts must be under src/, tests/, or config/")
        verifiers = spec.get("verifiers")
        if not isinstance(verifiers, list) or not verifiers:
            raise GamingAgentsError("at least one independent verifier is required")
        normalized_verifiers = []
        for item in verifiers:
            if not isinstance(item, dict) or set(item) - {"id", "argv", "timeout_seconds"}:
                raise GamingAgentsError("verifiers may contain only id, argv, and timeout_seconds")
            argv = item.get("argv")
            if not item.get("id") or not isinstance(argv, list) or not argv or any(not isinstance(arg, str) or not arg for arg in argv):
                raise GamingAgentsError("each verifier requires a non-empty id and argv")
            if Path(argv[0]).name.casefold() not in {name.casefold() for name in SAFE_VERIFIER_EXECUTABLES}:
                raise GamingAgentsError(f"verifier executable is not allowlisted: {argv[0]}")
            timeout = item.get("timeout_seconds", 120)
            if not isinstance(timeout, int) or not 1 <= timeout <= 3600:
                raise GamingAgentsError("verifier timeout_seconds must be 1..3600")
            normalized_verifiers.append({"id": str(item["id"]), "argv": argv, "timeout_seconds": timeout})
        return {**spec, "entrypoint": entrypoint, "creative_artifacts": creative, "engineer_artifacts": engineer, "verifiers": normalized_verifiers}

    @staticmethod
    def _require_complete_document(path: Path) -> None:
        try:
            text = path.read_text(encoding="utf-8")
        except OSError as error:
            raise GamingAgentsError(f"required Director artifact is missing: {path}") from error
        if len(text.strip()) < 80 or "[TBD" in text:
            raise GamingAgentsError(f"Director artifact is incomplete: {path}")

    def approve(self, target_value: str) -> dict[str, Any]:
        target = self.target(target_value)
        state = target / STATE_NAME
        if not state.is_dir():
            raise GamingAgentsError("target has not been initialized")
        intent = state / "intent.md"
        self._require_complete_document(intent)
        paths = [target / "docs" / name for name in ("game-brief.md", "acceptance-contract.md", "game-spec.json")]
        for path in paths[:2]:
            self._require_complete_document(path)
        self._validate_spec(target)
        hashes = {path.relative_to(target).as_posix(): _sha256(path) for path in paths}
        approval = {
            "schema_version": 1,
            "game_id": self._game_id(target),
            "approved_by": "human-cli",
            "approved_at": datetime.now(timezone.utc).isoformat(),
            "sha256": hashes,
        }
        _write_json(state / "approval.json", approval)
        return {"status": "approved", "game_id": approval["game_id"], "sha256": hashes}

    def _verified_approval(self, target: Path) -> dict[str, Any]:
        approval = _json(target / STATE_NAME / "approval.json")
        if not isinstance(approval, dict) or approval.get("schema_version") != 1 or approval.get("game_id") != self._game_id(target):
            raise GamingAgentsError("approval manifest is invalid")
        hashes = approval.get("sha256")
        required = {"docs/game-brief.md", "docs/acceptance-contract.md", "docs/game-spec.json"}
        if not isinstance(hashes, dict) or set(hashes) != required:
            raise GamingAgentsError("approval manifest does not cover all Director artifacts")
        stale = sorted(name for name, expected in hashes.items() if not (target / name).is_file() or _sha256(target / name) != expected)
        if stale:
            raise GamingAgentsError("approval is stale for: " + ", ".join(stale))
        return approval

    def materialize_build(self, target_value: str) -> dict[str, Any]:
        target = self.target(target_value)
        approval = self._verified_approval(target)
        spec = self._validate_spec(target)
        state = target / STATE_NAME
        jobs = state / "jobs"
        game_id = approval["game_id"]
        target_dir = self._target_value(target)
        common_context = ["docs/game-brief.md", "docs/acceptance-contract.md", "docs/game-spec.json"]
        creative_expected = ["docs/style-guide.md", "assets/asset-manifest.json", *spec["creative_artifacts"]]
        creative_expected = list(dict.fromkeys(creative_expected))
        creative = {
            "schema_version": 1,
            "id": f"{game_id}-creative-producer",
            "objective": "Create the approved procedural or placeholder art, UI, and audio package. Produce every declared Creative artifact and record complete provenance in the asset manifest.",
            "target_dir": target_dir,
            "mode": "write",
            "importance": "normal",
            "risk": "medium",
            "tool_class": "files_write",
            "required_capabilities": ["coding", "file-editing"],
            "context": [f"{STATE_NAME}/context/roles/creative-producer.md", f"{STATE_NAME}/context/templates/handoff.md", *common_context],
            "expected_artifacts": creative_expected,
            "allowed_write_paths": ["assets", "docs/style-guide.md"],
            "verifiers": [],
            "dependencies": [],
            "limits": {"timeout_seconds": 900, "max_turns": 12, "max_tokens": 30000},
        }
        engineer_expected = [*spec["engineer_artifacts"], "docs/architecture.md", "docs/implementation-handoff.md"]
        engineer_expected = list(dict.fromkeys(engineer_expected))
        root_engineer_paths = [value for value in spec["engineer_artifacts"] if "/" not in value]
        engineer = {
            "schema_version": 1,
            "id": f"{game_id}-gameplay-engineer",
            "objective": "Implement and integrate the approved playable MVP. Preserve the approved contracts and Creative package, add developer tests, and produce the architecture and implementation handoff.",
            "target_dir": target_dir,
            "mode": "write",
            "importance": "normal",
            "risk": "medium",
            "tool_class": "files_write",
            "required_capabilities": ["coding", "reasoning", "file-editing"],
            "context": [f"{STATE_NAME}/context/roles/gameplay-engineer.md", f"{STATE_NAME}/context/templates/handoff.md", *common_context, *creative_expected],
            "expected_artifacts": engineer_expected,
            "allowed_write_paths": ["src", "tests", "config", "docs/architecture.md", "docs/implementation-handoff.md", *root_engineer_paths],
            "verifiers": [],
            "dependencies": [creative["id"]],
            "limits": {"timeout_seconds": 1200, "max_turns": 16, "max_tokens": 40000},
        }
        qa = {
            "schema_version": 1,
            "id": f"{game_id}-qa-playtest",
            "objective": "Independently audit the implemented MVP against the approved acceptance contract and return only one QA report JSON object. Do not edit any file.",
            "target_dir": target_dir,
            "mode": "read",
            "importance": "high",
            "risk": "medium",
            "tool_class": "files_read",
            "required_capabilities": ["review", "reasoning"],
            "context": [f"{STATE_NAME}/context/roles/qa-playtest.md", f"{STATE_NAME}/context/templates/qa-report.schema.json", *common_context, *creative_expected, *engineer_expected],
            "expected_artifacts": [],
            "verifiers": spec["verifiers"],
            "dependencies": [engineer["id"]],
            "output_schema": f"{STATE_NAME}/context/templates/qa-report.schema.json",
            "limits": {"timeout_seconds": 900, "max_turns": 10, "max_tokens": 20000},
        }
        _write_json(jobs / "02-creative-producer.json", creative)
        _write_json(jobs / "03-gameplay-engineer.json", engineer)
        _write_json(jobs / "04-qa-playtest.json", qa)
        graph = jobs / "02-build-and-qa.graph.json"
        _write_json(graph, {
            "schema_version": 1,
            "max_parallel": 1,
            "jobs": ["02-creative-producer.json", "03-gameplay-engineer.json", "04-qa-playtest.json"],
        })
        ownership = _json(state / "ownership.json")
        ownership["owners"]["gameplay-engineer"].extend(value for value in root_engineer_paths if value not in ownership["owners"]["gameplay-engineer"])
        _write_json(state / "ownership.json", ownership)
        return {"status": "materialized", "game_id": game_id, "build_graph": str(graph.relative_to(self.workspace)), "approval_sha256": approval["sha256"]}

    def validate(self, target_value: str) -> dict[str, Any]:
        target = self.target(target_value)
        state = target / STATE_NAME
        if not state.is_dir():
            raise GamingAgentsError("target has not been initialized")
        game_id = self._game_id(target)
        source_root = self.workspace / "agent-orchestrator" / "src"
        if not source_root.is_dir():
            raise GamingAgentsError("agent-orchestrator source is unavailable")
        source_value = str(source_root)
        if source_value not in sys.path:
            sys.path.insert(0, source_value)
        from agent_orchestrator.contracts import load_job
        from agent_orchestrator.paths import validate_job_paths
        from agent_orchestrator.scheduler import load_graph

        jobs_dir = state / "jobs"
        try:
            director_job = load_job(jobs_dir / "01-game-director.json")
            validate_job_paths(self.workspace, director_job)
            load_graph(jobs_dir / "01-game-director.graph.json")
            checked = [director_job.id]
            build_graph = jobs_dir / "02-build-and-qa.graph.json"
            if build_graph.exists():
                self._verified_approval(target)
                self._validate_spec(target)
                jobs, _ = load_graph(build_graph)
                for job in jobs:
                    validate_job_paths(self.workspace, job)
                    if job.mode == "write" and not job.allowed_write_paths:
                        raise GamingAgentsError(f"write job lacks ownership paths: {job.id}")
                    if job.id.endswith("qa-playtest") and (job.mode != "read" or job.allowed_write_paths or not job.verifiers):
                        raise GamingAgentsError("QA must be read-only and retain independent verifiers")
                    checked.append(job.id)
        except GamingAgentsError:
            raise
        except Exception as error:
            raise GamingAgentsError(f"orchestrator validation failed: {error}") from error
        return {"status": "valid", "game_id": game_id, "jobs": checked, "phase": "build" if build_graph.exists() else "director"}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    initialize = commands.add_parser("init")
    initialize.add_argument("--target", required=True)
    initialize.add_argument("--id", required=True)
    for name in ("approve", "materialize-build", "validate"):
        command = commands.add_parser(name)
        command.add_argument("--target", required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    manager = GamingAgentsManager()
    try:
        if args.command == "init":
            result = manager.init(args.target, args.id)
        elif args.command == "approve":
            result = manager.approve(args.target)
        elif args.command == "materialize-build":
            result = manager.materialize_build(args.target)
        else:
            result = manager.validate(args.target)
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return 0
    except GamingAgentsError as error:
        print(json.dumps({"status": "error", "error": str(error)}, indent=2, ensure_ascii=False))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
