"""Open this workspace in VS Code with the local Vibe API key in process memory."""

from __future__ import annotations

import os
import subprocess
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
API_KEY_PATH = Path(r"C:\LLMs\config\api_key.txt")


def find_vscode() -> Path:
    candidates = [
        Path(os.environ["LOCALAPPDATA"]) / "Programs/Microsoft VS Code/Code.exe",
        Path(os.environ.get("ProgramFiles", r"C:\Program Files")) / "Microsoft VS Code/Code.exe",
    ]
    for candidate in candidates:
        if candidate.is_file():
            return candidate
    raise FileNotFoundError("Code.exe was not found in the standard installation directories.")


def main() -> None:
    if not API_KEY_PATH.is_file():
        raise SystemExit(f"Local API key not found: {API_KEY_PATH}")

    environment = os.environ.copy()
    environment["LOCAL_LLM_API_KEY"] = API_KEY_PATH.read_text(encoding="ascii").strip()
    vscode = find_vscode()

    subprocess.Popen(
        [str(vscode), "--new-window", str(PROJECT_ROOT)],
        env=environment,
    )
    print(f"Opened VS Code workspace: {PROJECT_ROOT}")
    print("The API key was passed in process memory and was not copied into the project.")


if __name__ == "__main__":
    main()
