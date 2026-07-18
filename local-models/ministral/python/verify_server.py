"""Verify the local Ministral process, API authentication, and chat response."""

from __future__ import annotations

import json
import subprocess
import urllib.error
import urllib.request
from pathlib import Path


URL = "http://127.0.0.1:8081/v1/chat/completions"
PID_FILE = Path(r"C:\LLMs\logs\ministral.pid")
API_KEY_FILE = Path(r"C:\LLMs\config\api_key.txt")


def request(headers: dict[str, str]) -> dict:
    payload = {
        "model": "ministral-3b-q4",
        "messages": [{"role": "user", "content": "Antworte ausschließlich mit: Bereit."}],
        "temperature": 0.0,
        "max_tokens": 16,
    }
    http_request = urllib.request.Request(
        URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json", **headers},
        method="POST",
    )
    with urllib.request.urlopen(http_request, timeout=120) as response:
        return json.load(response)


def main() -> None:
    pid = PID_FILE.read_text(encoding="ascii").strip()
    gpu_processes = subprocess.run(
        [
            "nvidia-smi",
            "--query-compute-apps=pid,process_name",
            "--format=csv,noheader",
        ],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.splitlines()
    llama_processes = [line for line in gpu_processes if "llama-server" in line]

    try:
        request({})
    except urllib.error.HTTPError as error:
        unauthenticated_status = error.code
    else:
        unauthenticated_status = 200

    key = API_KEY_FILE.read_text(encoding="ascii").strip()
    response = request({"Authorization": f"Bearer {key}"})
    answer = response["choices"][0]["message"]["content"].strip()

    report = {
        "pid": int(pid),
        "gpu_llama_processes": llama_processes,
        "unauthenticated_http_status": unauthenticated_status,
        "authenticated_answer": answer,
    }
    print(json.dumps(report, indent=2, ensure_ascii=False))

    if len(llama_processes) != 1 or not llama_processes[0].startswith(pid + ","):
        raise SystemExit("Expected exactly one GPU-backed llama-server matching the PID file.")
    if unauthenticated_status not in (401, 403):
        raise SystemExit("The API accepted an unauthenticated request.")


if __name__ == "__main__":
    main()
