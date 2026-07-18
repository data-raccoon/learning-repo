"""Execute exactly one auditable local-Mistral job and persist its artifact directly."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import urllib.request
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
KEY_FILE = Path(r"C:\LLMs\config\api_key.txt")
ENDPOINT = "http://127.0.0.1:8081/v1/chat/completions"
MODEL = "ministral-3b-q4"


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def strip_fence(text: str, language: str = "") -> str:
    match = re.fullmatch(rf"\s*```(?:{re.escape(language)})?\s*(.*?)\s*```\s*", text, re.I | re.S)
    return (match.group(1) if match else text).strip()


def parse_json_artifact(text: str) -> object:
    candidate = strip_fence(text, "json")
    try:
        return json.loads(candidate)
    except json.JSONDecodeError:
        decoder = json.JSONDecoder()
        for index, character in enumerate(candidate):
            if character not in "[{":
                continue
            try:
                value, _ = decoder.raw_decode(candidate[index:])
                return value
            except json.JSONDecodeError:
                continue
    raise ValueError("model response contained no valid JSON artifact")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("spec", type=Path)
    args = parser.parse_args()
    spec_path = args.spec.resolve()
    spec = json.loads(spec_path.read_text(encoding="utf-8"))
    project = spec_path.parents[2]
    prompt_path = project / spec["prompt_file"]
    output_path = project / spec["output"]
    dependencies = [project / item for item in spec.get("inputs", [])]

    prompt_parts = [prompt_path.read_text(encoding="utf-8").strip()]
    input_records = [{"path": str(prompt_path.relative_to(project)), "sha256": digest(prompt_path.read_bytes())}]
    for path in dependencies:
        content = path.read_text(encoding="utf-8")
        prompt_parts.append(f"\n\n--- INPUT: {path.relative_to(project)} ---\n{content}")
        input_records.append({"path": str(path.relative_to(project)), "sha256": digest(path.read_bytes())})
    prompt = "".join(prompt_parts)

    started = datetime.now(timezone.utc)
    key = KEY_FILE.read_text(encoding="ascii").strip()
    payload = json.dumps({
        "model": MODEL,
        "messages": [
            {"role": "system", "content": spec["system"]},
            {"role": "user", "content": prompt},
        ],
        "temperature": spec.get("temperature", 0.1),
        "max_tokens": spec.get("max_tokens", 6000),
    }).encode("utf-8")
    request = urllib.request.Request(ENDPOINT, data=payload, method="POST", headers={
        "Content-Type": "application/json", "Authorization": f"Bearer {key}"})
    with urllib.request.urlopen(request, timeout=600) as response:
        result = json.load(response)
    raw = result["choices"][0]["message"]["content"].strip()
    kind = spec.get("kind", "text")
    artifact = strip_fence(raw, spec.get("language", ""))
    if kind == "json":
        parsed = parse_json_artifact(raw)
        artifact = json.dumps(parsed, indent=2, ensure_ascii=False)
    artifact = artifact.rstrip() + "\n"

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(artifact, encoding="utf-8")
    finished = datetime.now(timezone.utc)
    usage = result.get("usage", {})
    record = {
        "job": spec["id"], "model": MODEL,
        "started_utc": started.isoformat(), "finished_utc": finished.isoformat(),
        "duration_seconds": round((finished - started).total_seconds(), 3),
        "inputs": input_records,
        "output": {"path": str(output_path.relative_to(project)), "sha256": digest(artifact.encode("utf-8")), "bytes": len(artifact.encode("utf-8"))},
        "usage": usage,
    }
    run_dir = project / ".orchestration" / "runs"
    run_dir.mkdir(parents=True, exist_ok=True)
    record_path = run_dir / f"{spec['id']}.json"
    record_path.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    print(f"PASS job={spec['id']} output={record['output']['path']} bytes={record['output']['bytes']} prompt_tokens={usage.get('prompt_tokens','?')} completion_tokens={usage.get('completion_tokens','?')}")


if __name__ == "__main__":
    main()
