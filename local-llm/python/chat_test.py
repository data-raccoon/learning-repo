"""Send a chat request to the local Ministral OpenAI-compatible endpoint."""

from __future__ import annotations

import argparse
import json
import urllib.error
import urllib.request
from pathlib import Path


API_KEY_FILE = Path(r"C:\LLMs\config\api_key.txt")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "prompt",
        nargs="?",
        default="Antworte in einem Satz: Was ist ein lokal betriebenes LLM?",
    )
    parser.add_argument("--url", default="http://127.0.0.1:8081/v1/chat/completions")
    args = parser.parse_args()

    payload = {
        "model": "ministral-3b-q4",
        "messages": [
            {
                "role": "system",
                "content": "Du bist ein präziser deutschsprachiger Assistent.",
            },
            {"role": "user", "content": args.prompt},
        ],
        "temperature": 0.1,
        "max_tokens": 256,
    }
    headers = {"Content-Type": "application/json"}
    if API_KEY_FILE.exists():
        headers["Authorization"] = f"Bearer {API_KEY_FILE.read_text(encoding='ascii').strip()}"
    request = urllib.request.Request(
        args.url,
        data=json.dumps(payload).encode("utf-8"),
        headers=headers,
        method="POST",
    )

    try:
        with urllib.request.urlopen(request, timeout=120) as response:
            result = json.load(response)
    except urllib.error.URLError as error:
        raise SystemExit(f"Local model server is unavailable: {error}") from error

    print(result["choices"][0]["message"]["content"].strip())


if __name__ == "__main__":
    main()
