"""Detect changed actionable Company-OS work without duplicate heartbeat noise."""

from __future__ import annotations

import argparse
import json
import os
import re
import tempfile
from dataclasses import asdict, dataclass
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Iterable


ACTIVE_WORK_ORDER_STATUSES = {"ready", "in-progress", "in_progress", "blocked"}
TERMINAL_WORK_ORDER_STATUSES = {
    "cancelled",
    "canceled",
    "closed",
    "complete",
    "completed",
    "stopped",
    "superseded",
}
FRONTMATTER_BOUNDARY = "---"


@dataclass(frozen=True)
class Finding:
    key: str
    kind: str
    path: str
    title: str
    owner: str
    status: str
    review_date: str
    approval_gate: str
    urgency: str


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _frontmatter(text: str) -> dict[str, str]:
    lines = text.splitlines()
    if not lines or lines[0].strip() != FRONTMATTER_BOUNDARY:
        return {}
    try:
        end = next(index for index in range(1, len(lines)) if lines[index].strip() == FRONTMATTER_BOUNDARY)
    except StopIteration:
        return {}
    values: dict[str, str] = {}
    for line in lines[1:end]:
        if ":" not in line or line.lstrip().startswith("#"):
            continue
        key, value = line.split(":", 1)
        values[key.strip()] = value.strip().strip("\"'")
    return values


def _heading(text: str) -> str:
    match = re.search(r"^#\s+(.+)$", text, flags=re.MULTILINE)
    return match.group(1).strip() if match else "Untitled artifact"


def _relative(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix()


def _review_date(value: str) -> date | None:
    try:
        return date.fromisoformat(value)
    except ValueError:
        return None


def _approval_gate(text: str) -> str:
    match = re.search(
        r"^##\s+Approval Level\s*$([\s\S]*?)(?=^##\s|\Z)",
        text,
        flags=re.IGNORECASE | re.MULTILINE,
    )
    if not match:
        return "not recorded"
    body = match.group(1)
    explicit = re.search(r"`(routine|founder-approval-required)`", body, flags=re.IGNORECASE)
    if explicit:
        return explicit.group(1).lower()
    if re.search(r"founder approval (?:is |remains )?required", body, flags=re.IGNORECASE):
        return "founder-approval-required"
    if re.search(r"\broutine\b", body, flags=re.IGNORECASE):
        return "routine"
    return "not recorded"


def _work_order_paths(root: Path) -> Iterable[Path]:
    paths = set(root.rglob("work-order.md"))
    work_order_directory = root / "company" / "work-orders"
    if work_order_directory.exists():
        paths.update(work_order_directory.glob("*.md"))
    return sorted(path for path in paths if "templates" not in path.parts)


def collect_work_orders(root: Path, today: date) -> list[Finding]:
    findings: list[Finding] = []
    for path in _work_order_paths(root):
        text = _read_text(path)
        metadata = _frontmatter(text)
        status = metadata.get("status", "unknown").lower()
        review_date = metadata.get("review_date", "unknown")
        parsed_review_date = _review_date(review_date)
        invalid_review_date = parsed_review_date is None
        overdue = parsed_review_date is not None and parsed_review_date < today
        if status not in ACTIVE_WORK_ORDER_STATUSES and not (
            overdue and status not in TERMINAL_WORK_ORDER_STATUSES
        ):
            continue
        relative = _relative(path, root)
        findings.append(
            Finding(
                key=f"work-order:{relative}",
                kind="work_order",
                path=relative,
                title=_heading(text),
                owner=metadata.get("owner", "unassigned"),
                status=status,
                review_date=review_date,
                approval_gate=_approval_gate(text),
                urgency=(
                    "high"
                    if invalid_review_date or status == "blocked"
                    else ("overdue" if overdue else "normal")
                ),
            )
        )
    return findings


def _table_rows(text: str) -> Iterable[dict[str, str]]:
    lines = [line.strip() for line in text.splitlines() if line.strip().startswith("|")]
    if len(lines) < 3:
        return []
    headers = [cell.strip().lower() for cell in lines[0].strip("|").split("|")]
    rows: list[dict[str, str]] = []
    for line in lines[2:]:
        cells = [cell.strip() for cell in line.strip("|").split("|")]
        if len(cells) != len(headers):
            continue
        rows.append(dict(zip(headers, cells)))
    return rows


def collect_open_risks(root: Path) -> list[Finding]:
    findings: list[Finding] = []
    for path in sorted(root.rglob("risk-register.md")):
        if "templates" in path.parts:
            continue
        text = _read_text(path)
        metadata = _frontmatter(text)
        relative = _relative(path, root)
        for row in _table_rows(text):
            if row.get("status", "").lower() != "open":
                continue
            risk_id = row.get("id", "unidentified")
            impact = row.get("impact", "unknown").lower()
            findings.append(
                Finding(
                    key=f"risk:{relative}:{risk_id}",
                    kind="risk",
                    path=relative,
                    title=f"{risk_id}: {row.get('risk', 'Open risk')}",
                    owner=row.get("owner", metadata.get("owner", "unassigned")),
                    status="open",
                    review_date=metadata.get("review_date", "unknown"),
                    approval_gate="Founder approval required to accept material residual risk",
                    urgency="high" if impact == "high" else "normal",
                )
            )
    return findings


def collect_findings(root: Path, today: date) -> dict[str, dict[str, str]]:
    findings = collect_work_orders(root, today) + collect_open_risks(root)
    result: dict[str, dict[str, str]] = {}
    for finding in sorted(findings, key=lambda item: item.key):
        if not finding.key.rsplit(":", 1)[-1].strip():
            raise ValueError(f"Finding has an empty identifier: {finding.path}")
        if finding.key in result:
            raise ValueError(f"Duplicate finding identifier: {finding.key}")
        result[finding.key] = asdict(finding)
    return result


def _load_state(path: Path) -> dict[str, object]:
    if not path.exists():
        return {"version": 1, "findings": {}}
    try:
        data = json.loads(_read_text(path))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"Cannot read heartbeat state {path}: {exc}") from exc
    if not isinstance(data, dict) or not isinstance(data.get("findings"), dict):
        raise ValueError(f"Invalid heartbeat state schema: {path}")
    return data


def _save_state(path: Path, findings: dict[str, dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "version": 1,
        "checked_at": datetime.now(timezone.utc).isoformat(),
        "findings": findings,
    }
    handle, temporary_name = tempfile.mkstemp(prefix=f"{path.name}.", suffix=".tmp", dir=path.parent)
    temporary = Path(temporary_name)
    try:
        with os.fdopen(handle, "w", encoding="utf-8") as stream:
            json.dump(payload, stream, indent=2, sort_keys=True)
            stream.write("\n")
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def _contained_state_path(root: Path, state_path: Path) -> Path:
    runtime = (root / ".runtime" / "assistenz-heartbeat").resolve()
    resolved = state_path.resolve()
    if resolved != runtime / "state.json":
        raise ValueError(f"Heartbeat state must be {runtime / 'state.json'}")
    return resolved


def acknowledge(root: Path) -> bool:
    root = root.resolve()
    state_path = _contained_state_path(root, root / ".runtime" / "assistenz-heartbeat" / "state.json")
    pending_path = state_path.with_name("pending.json")
    if not pending_path.exists():
        return False
    pending = _load_state(pending_path)
    findings = pending.get("findings")
    assert isinstance(findings, dict)
    _save_state(state_path, findings)
    pending_path.unlink()
    return True


def check(root: Path, state_path: Path, today: date, persist: bool = True) -> dict[str, list[dict[str, str]]]:
    root = root.resolve()
    state_path = _contained_state_path(root, state_path)
    pending_path = state_path.with_name("pending.json")
    current = collect_findings(root, today)
    previous = _load_state(state_path).get("findings", {})
    assert isinstance(previous, dict)

    new = [current[key] for key in sorted(set(current) - set(previous))]
    resolved = []
    for key in sorted(set(previous) - set(current)):
        item = dict(previous[key])
        item["previous_status"] = item.get("status", "unknown")
        item["status"] = "resolved"
        resolved.append(item)
    changed = [
        current[key]
        for key in sorted(set(current) & set(previous))
        if current[key] != previous[key]
    ]
    if persist:
        if new or changed or resolved:
            _save_state(pending_path, current)
        else:
            _save_state(state_path, current)
            pending_path.unlink(missing_ok=True)
    return {"new": new, "changed": changed, "resolved": resolved}


def _format(changes: dict[str, list[dict[str, str]]]) -> str:
    labels = {"new": "NEW", "changed": "CHANGED", "resolved": "RESOLVED"}
    lines: list[str] = []
    for category in ("new", "changed", "resolved"):
        for item in changes[category]:
            lines.append(
                f"[{labels[category]}] {item['title']} | owner={item['owner']} | "
                f"urgency={item['urgency']} | status={item['status']} | path={item['path']} | "
                f"gate={item['approval_gate']}"
            )
    return "\n".join(lines)


def main() -> int:
    default_root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=default_root)
    parser.add_argument("--today", type=date.fromisoformat, default=date.today())
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--ack", action="store_true", help="Acknowledge the previously delivered pending report")
    args = parser.parse_args()
    if args.ack:
        if args.dry_run or args.json:
            parser.error("--ack cannot be combined with --dry-run or --json")
        acknowledge(args.root)
        return 0
    state_path = args.root / ".runtime" / "assistenz-heartbeat" / "state.json"
    changes = check(args.root, state_path, args.today, persist=not args.dry_run)
    if args.json:
        print(json.dumps(changes, indent=2, sort_keys=True))
    else:
        output = _format(changes)
        if output:
            print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
