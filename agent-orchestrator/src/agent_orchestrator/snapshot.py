"""Transactional target snapshots and quarantined failure deltas."""

from __future__ import annotations

import difflib
import json
import os
from pathlib import Path
import shutil
import stat
from typing import Any

from .evidence import sha256_file


def _remove_tree(path: Path) -> None:
    """Remove snapshots even when OneDrive copied a Windows read-only attribute."""
    def clear_readonly(function: Any, name: str, error: Any) -> None:
        os.chmod(name, stat.S_IWRITE)
        function(name)

    shutil.rmtree(path, onerror=clear_readonly)


def _files(root: Path) -> dict[str, Path]:
    return {
        path.relative_to(root).as_posix(): path
        for path in root.rglob("*")
        if path.is_file() and ".runtime" not in path.relative_to(root).parts
    }


def _record(path: Path) -> dict[str, Any]:
    return {"bytes": path.stat().st_size, "sha256": sha256_file(path)}


class TargetSnapshot:
    def __init__(self, target: Path, run_dir: Path):
        self.target = target
        self.snapshot_dir = run_dir / "snapshot"
        self.quarantine_dir = run_dir / "quarantine"

    def capture(self) -> None:
        shutil.copytree(self.target, self.snapshot_dir, symlinks=True)

    def manifest(self, root: Path) -> dict[str, dict[str, Any]]:
        return {name: _record(path) for name, path in _files(root).items()}

    def changes(self) -> dict[str, list[str]]:
        before, after = self.manifest(self.snapshot_dir), self.manifest(self.target)
        return {
            "added": sorted(set(after) - set(before)),
            "removed": sorted(set(before) - set(after)),
            "changed": sorted(name for name in set(before) & set(after) if before[name] != after[name]),
        }

    @staticmethod
    def _text(path: Path) -> list[str] | None:
        try:
            return path.read_text(encoding="utf-8").splitlines(keepends=True)
        except (UnicodeDecodeError, OSError):
            return None

    def quarantine(self) -> Path:
        self.quarantine_dir.mkdir(parents=True, exist_ok=True)
        delta = self.changes()
        current = _files(self.target)
        patch_parts: list[str] = []
        for name in delta["added"] + delta["changed"]:
            source = current[name]
            destination = self.quarantine_dir / "files" / name
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, destination)
        before_files = _files(self.snapshot_dir)
        for name in delta["added"] + delta["removed"] + delta["changed"]:
            old = self._text(before_files[name]) if name in before_files else []
            new = self._text(current[name]) if name in current else []
            if old is not None and new is not None:
                patch_parts.extend(difflib.unified_diff(old, new, fromfile=f"a/{name}", tofile=f"b/{name}"))
        (self.quarantine_dir / "changes.json").write_text(json.dumps(delta, indent=2) + "\n", encoding="utf-8")
        (self.quarantine_dir / "changes.patch").write_text("".join(patch_parts), encoding="utf-8")
        return self.quarantine_dir

    def restore(self) -> None:
        for child in self.target.iterdir():
            if child.is_dir() and not child.is_symlink():
                _remove_tree(child)
            else:
                child.unlink()
        for child in self.snapshot_dir.iterdir():
            destination = self.target / child.name
            if child.is_dir() and not child.is_symlink():
                shutil.copytree(child, destination, symlinks=True)
            elif child.is_symlink():
                destination.symlink_to(child.readlink(), target_is_directory=child.is_dir())
            else:
                shutil.copy2(child, destination)

    def discard(self) -> None:
        if self.snapshot_dir.exists():
            _remove_tree(self.snapshot_dir)
