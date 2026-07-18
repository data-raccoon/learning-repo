"""Regression test for Vibe histories with consecutive OpenAI message roles."""

from __future__ import annotations

import argparse
import json
import urllib.error
import urllib.request
from pathlib import Path


API_KEY_FILE = Path(r"C:\LLMs\config\api_key.txt")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--large", action="store_true", help="Use a Vibe-sized history")
    parser.add_argument("--tool-call", action="store_true", help="Require a read_file call")
    args = parser.parse_args()

    messages = [
        {"role": "system", "content": "You are a concise test assistant."},
        {"role": "user", "content": "Remember the word alpha."},
        {"role": "user", "content": "Reply with OK."},
    ]
    if args.large:
        filler = ("project context implementation detail verification step " * 48).strip()
        messages = [{"role": "system", "content": "You are a concise test assistant."}]
        messages.extend(
            {"role": "user", "content": f"Context block {index}: {filler}"}
            for index in range(1, 35)
        )
        messages[-1]["content"] += "\nReply with OK."
    elif args.tool_call:
        messages = [
            {"role": "system", "content": "Use the available file tools."},
            {"role": "user", "content": "Call read_file for C:\\test.txt now."},
        ]

    payload = {
        "model": "ministral-3b-q4",
        "messages": messages,
        "tools": [
            {
                "type": "function",
                "function": {
                    "name": "read_file",
                    "description": "Read a file.",
                    "parameters": {
                        "type": "object",
                        "properties": {"file_path": {"type": "string"}},
                        "required": ["file_path"],
                    },
                },
            }
        ],
        "tool_choice": "required" if args.tool_call else "auto",
        "temperature": 0.0,
        "max_tokens": 16 if args.large else 32,
    }
    key = API_KEY_FILE.read_text(encoding="ascii").strip()
    request = urllib.request.Request(
        "http://127.0.0.1:8081/v1/chat/completions",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            result = json.load(response)
    except urllib.error.HTTPError as error:
        body = error.read().decode("utf-8", errors="replace")
        raise SystemExit(f"Regression test failed: HTTP {error.code}\n{body}") from error

    content = result["choices"][0]["message"].get("content")
    tool_calls = result["choices"][0]["message"].get("tool_calls")
    if args.tool_call and not tool_calls:
        raise SystemExit(f"Regression test failed: expected tool call, got {result['choices'][0]['message']}")
    print(
        json.dumps(
            {
                "status": "passed",
                "message_count": len(messages),
                "approx_chars": sum(len(message["content"]) for message in messages),
                "content": content,
                "tool_calls": tool_calls,
            },
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
