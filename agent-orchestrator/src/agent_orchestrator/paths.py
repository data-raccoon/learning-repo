"""Canonical workspace path validation."""

from __future__ import annotations

from pathlib import Path

from .contracts import ContractError, Job


def reject_symlink_components(root: Path, value: str) -> None:
    current = root.resolve()
    for part in Path(value).parts:
        current = current / part
        if current.is_symlink():
            raise ContractError(f"symbolic links are forbidden in scoped paths: {value}")


def contained_path(root: Path, value: str, *, must_exist: bool = False) -> Path:
    candidate = Path(value)
    if candidate.is_absolute():
        raise ContractError(f"absolute paths are forbidden: {value}")
    if any(part == ".." for part in candidate.parts):
        raise ContractError(f"parent traversal is forbidden: {value}")
    root = root.resolve()
    resolved = (root / candidate).resolve(strict=False)
    if resolved == root or root not in resolved.parents:
        raise ContractError(f"path escapes its allowed root: {value}")
    if must_exist and not resolved.exists():
        raise ContractError(f"required path does not exist: {value}")
    return resolved


def validate_job_paths(workspace: Path, job: Job) -> Path:
    workspace = workspace.resolve()
    reject_symlink_components(workspace, job.target_dir)
    target = contained_path(workspace, job.target_dir, must_exist=True)
    if not target.is_dir():
        raise ContractError("target_dir must be an existing directory")
    if target.is_symlink():
        raise ContractError("target_dir may not be a symbolic link")
    for value in (*job.context, *job.expected_artifacts):
        reject_symlink_components(target, value)
        path = contained_path(target, value, must_exist=value in job.context)
        if value in job.context and path.is_symlink():
            raise ContractError(f"context symlinks are forbidden: {value}")
    for value in job.allowed_write_paths:
        reject_symlink_components(target, value)
        contained_path(target, value)
    if job.output_schema:
        reject_symlink_components(target, job.output_schema)
        contained_path(target, job.output_schema, must_exist=True)
    return target
