"""Start the local OpenAI-compatible Ministral llama.cpp server."""

from __future__ import annotations

import argparse
import os
import secrets
import shutil
import subprocess
import sys
from pathlib import Path


DEFAULT_MODEL = Path(
    r"C:\LLMs\models\mistral\Ministral-3-3B-Instruct-2512-Q4_K_M.gguf"
)
PID_FILE = Path(r"C:\LLMs\logs\ministral.pid")
LOG_FILE = Path(r"C:\LLMs\logs\ministral.log")
API_KEY_FILE = Path(r"C:\LLMs\config\api_key.txt")
CHAT_TEMPLATE_FILE = Path(r"C:\LLMs\config\ministral-vibe.jinja")


def find_server() -> Path:
    command = shutil.which("llama-server") or shutil.which("llama-server.exe")
    if command:
        return Path(command)

    package_root = (
        Path(os.environ["LOCALAPPDATA"])
        / "Microsoft"
        / "WinGet"
        / "Packages"
    )
    candidates = sorted(package_root.glob("ggml.llamacpp*/llama-server.exe"))
    if not candidates:
        raise FileNotFoundError("llama-server.exe not found; install it with 'winget install llama.cpp'")
    return candidates[-1]


def api_key() -> str:
    API_KEY_FILE.parent.mkdir(parents=True, exist_ok=True)
    if not API_KEY_FILE.exists():
        API_KEY_FILE.write_text(secrets.token_urlsafe(32), encoding="ascii")
    return API_KEY_FILE.read_text(encoding="ascii").strip()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", type=Path, default=DEFAULT_MODEL)
    parser.add_argument("--port", type=int, default=8081)
    parser.add_argument("--ctx-size", type=int, default=32768)
    parser.add_argument("--background", action="store_true")
    parser.add_argument("--stop", action="store_true")
    args = parser.parse_args()

    if args.stop:
        if not PID_FILE.exists():
            print("No Ministral PID file found.")
            return
        pid = int(PID_FILE.read_text(encoding="ascii").strip())
        result = subprocess.run(["taskkill", "/PID", str(pid), "/T", "/F"], check=False)
        if result.returncode == 0:
            PID_FILE.unlink(missing_ok=True)
            print(f"Stopped Ministral server (PID {pid}).")
        else:
            raise SystemExit(f"Could not stop PID {pid}; inspect {PID_FILE}.")
        return

    model = args.model.resolve()
    if not model.is_file():
        raise SystemExit(f"Model not found: {model}\nRun download_mistral.py first.")
    if not CHAT_TEMPLATE_FILE.is_file():
        raise SystemExit(
            f"Chat template not found: {CHAT_TEMPLATE_FILE}\n"
            "Run create_vibe_chat_template.py while the server is running."
        )

    server = find_server()
    command = [
        str(server),
        "--model",
        str(model),
        "--alias",
        "ministral-3b-q4",
        "--host",
        "127.0.0.1",
        "--port",
        str(args.port),
        "--ctx-size",
        str(args.ctx_size),
        "--parallel",
        "1",
        "--threads",
        str(min(os.cpu_count() or 1, 6)),
        "--n-gpu-layers",
        "99",
        "--jinja",
        "--chat-template-file",
        str(CHAT_TEMPLATE_FILE),
        "--api-key",
        api_key(),
    ]
    print(f"Starting Ministral at http://127.0.0.1:{args.port}")
    if args.background:
        PID_FILE.parent.mkdir(parents=True, exist_ok=True)
        creationflags = 0
        if sys.platform == "win32":
            creationflags = subprocess.CREATE_NEW_PROCESS_GROUP | subprocess.CREATE_NO_WINDOW
        with LOG_FILE.open("a", encoding="utf-8") as log:
            process = subprocess.Popen(
                command,
                stdin=subprocess.DEVNULL,
                stdout=log,
                stderr=subprocess.STDOUT,
                creationflags=creationflags,
            )
        PID_FILE.write_text(str(process.pid), encoding="ascii")
        print(f"Background PID: {process.pid}")
        print(f"Log: {LOG_FILE}")
        return

    print("Stop the server with Ctrl+C.")
    try:
        subprocess.run(command, check=True)
    except KeyboardInterrupt:
        print("\nServer stopped.")


if __name__ == "__main__":
    main()
