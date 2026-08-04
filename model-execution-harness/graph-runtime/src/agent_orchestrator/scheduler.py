"""Dependency-aware parallel job scheduling."""

from __future__ import annotations

from concurrent.futures import FIRST_COMPLETED, Future, ThreadPoolExecutor, wait
import json
from pathlib import Path
from typing import Any

from .contracts import ContractError, Job, load_job
from .runner import JobRunner


def load_graph(path: Path) -> tuple[list[Job], int]:
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise ContractError(f"cannot load graph: {error}") from error
    if not isinstance(raw, dict) or set(raw) - {"schema_version", "jobs", "max_parallel"}:
        raise ContractError("graph must contain only schema_version, jobs, and max_parallel")
    if raw.get("schema_version") != 1 or not isinstance(raw.get("jobs"), list):
        raise ContractError("graph schema_version 1 and jobs array are required")
    maximum = raw.get("max_parallel", 4)
    if not isinstance(maximum, int) or not 1 <= maximum <= 32:
        raise ContractError("max_parallel must be 1..32")
    job_paths = []
    for item in raw["jobs"]:
        if not isinstance(item, str) or Path(item).is_absolute() or ".." in Path(item).parts:
            raise ContractError("graph job paths must be relative and may not traverse parents")
        job_paths.append((path.parent / item).resolve())
    jobs = [load_job(item) for item in job_paths]
    ids = [job.id for job in jobs]
    if len(ids) != len(set(ids)):
        raise ContractError("graph job ids must be unique")
    known = set(ids)
    for job in jobs:
        unknown = set(job.dependencies) - known
        if unknown:
            raise ContractError(f"job {job.id} has unknown dependencies: {sorted(unknown)}")
    _assert_acyclic(jobs)
    return jobs, maximum


def _assert_acyclic(jobs: list[Job]) -> None:
    dependencies = {job.id: set(job.dependencies) for job in jobs}
    remaining = set(dependencies)
    while remaining:
        ready = {item for item in remaining if not (dependencies[item] & remaining)}
        if not ready:
            raise ContractError("job graph contains a dependency cycle")
        remaining -= ready


def run_graph(runner: JobRunner, jobs: list[Job], max_parallel: int) -> dict[str, Any]:
    by_id = {job.id: job for job in jobs}
    pending = set(by_id)
    results: dict[str, dict[str, Any]] = {}
    running: dict[Future[dict[str, Any]], str] = {}
    with ThreadPoolExecutor(max_workers=max_parallel, thread_name_prefix="model-job") as pool:
        while pending or running:
            progressed = False
            for job_id in list(pending):
                job = by_id[job_id]
                if not set(job.dependencies).issubset(results):
                    continue
                failed_dependencies = [item for item in job.dependencies if results[item]["status"] != "passed"]
                if failed_dependencies:
                    results[job_id] = {"job": job_id, "status": "skipped", "failed_dependencies": failed_dependencies}
                    pending.remove(job_id)
                    progressed = True
                elif len(running) < max_parallel:
                    future = pool.submit(runner.run, job)
                    running[future] = job_id
                    pending.remove(job_id)
                    progressed = True
            if running:
                completed, _ = wait(running, return_when=FIRST_COMPLETED)
                for future in completed:
                    job_id = running.pop(future)
                    try:
                        results[job_id] = future.result()
                    except Exception as error:
                        results[job_id] = {"job": job_id, "status": "failed", "error": f"scheduler: {error}"}
            elif pending and not progressed:
                raise RuntimeError("scheduler made no progress")
    ordered = [results[job.id] for job in jobs]
    return {
        "status": "passed" if all(item["status"] == "passed" for item in ordered) else "failed",
        "jobs": ordered,
    }
