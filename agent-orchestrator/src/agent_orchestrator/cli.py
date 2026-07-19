"""Machine-readable CLI for the repository-local model orchestrator."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import platform
import shutil
import sys
import re
from typing import Any

from . import __version__
from .contracts import ContractError, load_job
from .evaluation import audit_profiles, run_candidate
from .paths import validate_job_paths
from .registry import Registry, RegistryError
from .routing import RoutingError, route_job
from .runner import JobRunner
from .runtime import RuntimeManager
from .scheduler import load_graph, run_graph


ORCHESTRATOR_ROOT = Path(__file__).resolve().parents[2]
WORKSPACE = ORCHESTRATOR_ROOT.parent


def _emit(value: Any) -> None:
    print(json.dumps(value, indent=2, ensure_ascii=False))


def _registry() -> Registry:
    return Registry(ORCHESTRATOR_ROOT / "config")


def _runner(registry: Registry) -> JobRunner:
    return JobRunner(WORKSPACE, ORCHESTRATOR_ROOT, registry)


def _scoped_spec(path: Path) -> Path:
    resolved = path.resolve()
    if WORKSPACE not in resolved.parents:
        raise ContractError("job and graph specifications must be inside the repository")
    return resolved


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="model-orchestrator", description=__doc__)
    parser.add_argument("--version", action="version", version=__version__)
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("doctor", help="Inspect runtimes, credentials, and registry links")
    commands.add_parser("inventory", help="Print providers, models, harnesses, and profiles")
    route = commands.add_parser("route", help="Explain routing without starting a worker")
    route.add_argument("job", type=Path)
    run = commands.add_parser("run", help="Execute one transactional job")
    run.add_argument("job", type=Path)
    graph = commands.add_parser("run-graph", help="Execute a dependency graph")
    graph.add_argument("graph", type=Path)
    status = commands.add_parser("status", help="Read a compact run summary")
    status.add_argument("run_id", nargs="?", default="latest")
    runtime = commands.add_parser("runtime", help="Manage a registered local runtime")
    runtime.add_argument("action", choices=("start", "status", "stop"))
    runtime.add_argument("runtime_id", nargs="?", default="local-ministral")
    evaluate = commands.add_parser("eval", help="Audit profiles or run one live candidate job")
    evaluate.add_argument("action", choices=("run",))
    evaluate.add_argument("--job", type=Path)
    return parser


def doctor(registry: Registry) -> dict[str, Any]:
    inventory = registry.inventory()
    manager = RuntimeManager(WORKSPACE, ORCHESTRATOR_ROOT / ".runtime")
    commands = {name: shutil.which(name) for name in ("vibe", "agy", "codex", "llama-server", "ollama")}
    if not commands["agy"] and os.environ.get("LOCALAPPDATA"):
        installed = Path(os.environ["LOCALAPPDATA"]) / "agy" / "bin" / "agy.exe"
        commands["agy"] = str(installed) if installed.is_file() else None
    return {
        "status": "ok",
        "orchestrator_version": __version__,
        "python": platform.python_version(),
        "workspace": str(WORKSPACE),
        "commands": commands,
        "providers": [{"id": item["id"], "availability": item["availability"], "reason": item["availability_reason"]} for item in inventory["providers"]],
        "local_runtime": manager.status(),
    }


def read_status(run_id: str) -> dict[str, Any]:
    run_root = ORCHESTRATOR_ROOT / ".runtime" / "runs"
    if run_id == "latest":
        candidates = sorted((path for path in run_root.glob("*/summary.json")), key=lambda path: path.stat().st_mtime, reverse=True)
        if not candidates:
            raise FileNotFoundError("no run summaries exist")
        path = candidates[0]
    else:
        if not re.fullmatch(r"[A-Za-z0-9_.-]+", run_id):
            raise ContractError("invalid run id")
        path = run_root / run_id / "summary.json"
    return json.loads(path.read_text(encoding="utf-8"))


def main(argv: list[str] | None = None) -> None:
    args = build_parser().parse_args(argv)
    try:
        registry = _registry()
        if args.command == "doctor":
            result = doctor(registry)
        elif args.command == "inventory":
            result = registry.inventory()
        elif args.command == "route":
            job = load_job(_scoped_spec(args.job))
            validate_job_paths(WORKSPACE, job)
            result = route_job(registry, job)
        elif args.command == "run":
            result = _runner(registry).run(load_job(_scoped_spec(args.job)))
        elif args.command == "run-graph":
            jobs, maximum = load_graph(_scoped_spec(args.graph))
            result = run_graph(_runner(registry), jobs, maximum)
        elif args.command == "status":
            result = read_status(args.run_id)
        elif args.command == "runtime":
            manager = RuntimeManager(WORKSPACE, ORCHESTRATOR_ROOT / ".runtime")
            result = getattr(manager, args.action)(args.runtime_id)
        elif args.command == "eval":
            if args.job:
                job = load_job(_scoped_spec(args.job))
                destination = ORCHESTRATOR_ROOT / ".runtime" / "evals" / f"{job.id}.json"
                result = run_candidate(_runner(registry), job, destination)
            else:
                result = audit_profiles(registry)
        else:
            raise AssertionError(args.command)
        _emit(result)
        if isinstance(result, dict) and result.get("status") in {"failed", "skipped"}:
            raise SystemExit(1)
    except (ContractError, RegistryError, RoutingError, FileNotFoundError, RuntimeError, ValueError) as error:
        details = error.args[1] if isinstance(error, RoutingError) and len(error.args) > 1 else None
        _emit({"status": "error", "error": str(error.args[0] if error.args else error), "details": details})
        raise SystemExit(2) from None
