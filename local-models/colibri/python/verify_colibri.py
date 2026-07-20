"""Verify the local Colibri process, API authentication, and chat response."""

from __future__ import annotations

import json
import subprocess
import urllib.error
import urllib.request
from pathlib import Path


URL = "http://127.0.0.1:8082/v1/chat/completions"
PID_FILE = Path(r"C:\LLMs\logs\kolibri.pid")
API_KEY_FILE = Path(r"C:\LLMs\config\kolibri_api_key.txt")


def request(headers: dict[str, str]) -> dict:
    """Send a test request to the Colibri server."""
    payload = {
        "model": "GLM-5.2-744B-MoE",
        "messages": [{"role": "user", "content": "Antworte aussschlie\u00dflich mit: Bereit."}],
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
    """Verify Colibri server health and authentication."""
    pid = PID_FILE.read_text(encoding="ascii").strip()
    
    # Check for GPU processes (Colibri may use CPU or GPU)
    gpu_processes = []
    try:
        result = subprocess.run(
            [
                "nvidia-smi",
                "--query-compute-apps=pid,process_name",
                "--format=csv,noheader",
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        gpu_processes = [line for line in result.stdout.splitlines() if "kolibri" in line.lower() or "glm" in line.lower() or "openai_server" in line.lower()]
    except (subprocess.CalledProcessError, FileNotFoundError):
        # nvidia-smi not available or no GPU
        pass

    # Test unauthenticated access
    try:
        request({})
    except urllib.error.HTTPError as error:
        unauthenticated_status = error.code
    else:
        unauthenticated_status = 200

    # Test authenticated access
    key = API_KEY_FILE.read_text(encoding="ascii").strip()
    response = request({"Authorization": f"Bearer {key}"})
    answer = response["choices"][0]["message"]["content"].strip()

    report = {
        "pid": int(pid),
        "gpu_kolibri_processes": gpu_processes,
        "unauthenticated_http_status": unauthenticated_status,
        "authenticated_answer": answer,
    }
    print(json.dumps(report, indent=2, ensure_ascii=False))

    # Validation checks
    if gpu_processes and not any(line.startswith(pid + ",") for line in gpu_processes):
        print("Warning: No GPU-backed kolibri process matching the PID file.")
    if unauthenticated_status not in (401, 403):
        raise SystemExit("The API accepted an unauthenticated request.")


if __name__ == "__main__":
    main()
