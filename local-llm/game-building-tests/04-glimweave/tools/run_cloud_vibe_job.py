"""Run exactly one Mistral Cloud Vibe job and persist its artifact without printing it."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path


EXPERIMENT = Path(__file__).resolve().parents[1]
WORKSPACE = Path(__file__).resolve().parents[3]
MODEL = "mistral-medium-3.5"


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def unfence(text: str, language: str = "") -> str:
    match = re.fullmatch(rf"\s*```(?:{re.escape(language)})?\s*(.*?)\s*```\s*", text, re.I | re.S)
    if match:
        return match.group(1).strip()
    generic = re.fullmatch(r"\s*```[a-zA-Z0-9_-]*\s*(.*?)\s*```\s*", text, re.S)
    if generic:
        return generic.group(1).strip()
    if language:
        embedded = re.search(r"```(?:[a-zA-Z0-9_-]+)?\s*\r?\n(.*?)\r?\n```", text, re.S)
        if embedded:
            return embedded.group(1).strip()
    return text.strip()


def assistant_text(value: object) -> list[str]:
    found: list[str] = []
    if isinstance(value, dict):
        role = value.get("role")
        content = value.get("content")
        if role == "assistant" and isinstance(content, str):
            found.append(content)
        for child in value.values():
            found.extend(assistant_text(child))
    elif isinstance(value, list):
        for child in value:
            found.extend(assistant_text(child))
    return found


def find_usage(value: object) -> dict[str, object]:
    if isinstance(value, dict):
        if "usage" in value and isinstance(value["usage"], dict):
            return value["usage"]
        for child in value.values():
            usage = find_usage(child)
            if usage:
                return usage
    elif isinstance(value, list):
        for child in value:
            usage = find_usage(child)
            if usage:
                return usage
    return {}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("spec", type=Path)
    args = parser.parse_args()
    spec_path = args.spec.resolve()
    spec = json.loads(spec_path.read_text(encoding="utf-8"))
    prompt_path = EXPERIMENT / spec["prompt_file"]
    output_path = EXPERIMENT / spec["output"]
    inputs = [EXPERIMENT / item for item in spec.get("inputs", [])]
    records = [{"path": str(prompt_path.relative_to(EXPERIMENT)), "sha256": sha(prompt_path.read_bytes())}]
    parts = [prompt_path.read_text(encoding="utf-8")]
    for path in inputs:
        parts.append(f"\n\n--- INPUT: {path.relative_to(EXPERIMENT)} ---\n{path.read_text(encoding='utf-8')}")
        records.append({"path": str(path.relative_to(EXPERIMENT)), "sha256": sha(path.read_bytes())})
    prompt = "".join(parts)

    packet_path = EXPERIMENT / ".orchestration" / "runtime" / f"{spec['id']}.md"
    packet_path.parent.mkdir(parents=True, exist_ok=True)
    packet_path.write_text(prompt, encoding="utf-8")
    packet_relative = packet_path.relative_to(WORKSPACE).as_posix()
    request_prompt = (
        f"Use read_file to read the complete task packet at {packet_relative}. "
        "Follow it exactly and return only the requested artifact. Do not modify files."
    )
    command = [
        "vibe", "--prompt", request_prompt, "--trust", "--workdir", str(WORKSPACE),
        "--agent", "default", "--enabled-tools", "read_file", "--max-turns", str(spec.get("max_turns", 30)),
        "--max-price", str(spec.get("max_price", 2.0)),
        "--max-tokens", str(spec.get("max_tokens", 50000)), "--output", "json",
    ]
    environment = os.environ.copy()
    environment["VIBE_ACTIVE_MODEL"] = MODEL
    environment["PYTHONIOENCODING"] = "utf-8"
    environment["PYTHONUTF8"] = "1"
    started = datetime.now(timezone.utc)
    try:
        process = subprocess.run(command, cwd=WORKSPACE, env=environment, capture_output=True,
                                 text=True, encoding="utf-8", errors="replace", timeout=900)
    finally:
        packet_path.unlink(missing_ok=True)
    if process.returncode != 0:
        compact = re.sub(r"\s+", " ", process.stderr or process.stdout).strip()[:400]
        raise SystemExit(f"VIBE_FAILED job={spec['id']} detail={compact}")
    result = json.loads(process.stdout)
    candidates = assistant_text(result)
    if not candidates:
        raise SystemExit(f"VIBE_FAILED job={spec['id']} detail=no assistant artifact")
    artifact = unfence(candidates[-1], spec.get("language", ""))
    if spec.get("kind") == "json":
        artifact = json.dumps(json.loads(artifact), indent=2, ensure_ascii=False)
    artifact = artifact.rstrip() + "\n"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(artifact, encoding="utf-8")
    finished = datetime.now(timezone.utc)
    usage = find_usage(result)
    record = {
        "job": spec["id"], "provider": "Mistral Cloud", "model": MODEL,
        "started_utc": started.isoformat(), "finished_utc": finished.isoformat(),
        "duration_seconds": round((finished - started).total_seconds(), 3),
        "inputs": records,
        "output": {"path": spec["output"], "bytes": len(artifact.encode()), "sha256": sha(artifact.encode())},
        "usage": usage, "command_policy": {"tools": "disabled", "max_price_usd": spec.get("max_price", 2.0)},
    }
    evidence = EXPERIMENT / ".orchestration" / "runs" / f"{spec['id']}.json"
    evidence.parent.mkdir(parents=True, exist_ok=True)
    evidence.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    print(f"PASS job={spec['id']} model={MODEL} output={spec['output']} bytes={record['output']['bytes']} duration={record['duration_seconds']}s")


if __name__ == "__main__":
    main()
