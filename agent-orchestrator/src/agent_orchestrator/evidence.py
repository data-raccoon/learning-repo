"""Compact run summaries and durable JSONL evidence."""

from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
from typing import Any


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def artifact_records(target: Path, names: tuple[str, ...]) -> list[dict[str, Any]]:
    records = []
    for name in names:
        path = target / name
        if path.is_file():
            records.append({"path": name, "bytes": path.stat().st_size, "sha256": sha256_file(path)})
        else:
            records.append({"path": name, "missing": True})
    return records


class RunEvidence:
    def __init__(self, runtime_root: Path, run_id: str):
        self.run_dir = runtime_root / "runs" / run_id
        self.run_dir.mkdir(parents=True, exist_ok=False)
        self.events_path = self.run_dir / "events.jsonl"

    def event(self, event_type: str, **values: Any) -> None:
        row = {"at": utc_now(), "type": event_type, **values}
        with self.events_path.open("a", encoding="utf-8") as stream:
            stream.write(json.dumps(row, ensure_ascii=False) + "\n")

    def write_text(self, name: str, value: str) -> Path:
        path = self.run_dir / name
        path.write_text(value, encoding="utf-8")
        return path

    def finish(self, summary: dict[str, Any]) -> dict[str, Any]:
        path = self.run_dir / "summary.json"
        path.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        return summary

