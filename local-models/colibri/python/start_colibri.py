"""Start the local OpenAI-compatible Colibri server for GLM-5.2 MoE model."""

from __future__ import annotations

import argparse
import os
import secrets
import shutil
import subprocess
import sys
from pathlib import Path


# Colibri uses a different port than Ministral to avoid conflicts
DEFAULT_PORT = 8082
PID_FILE = Path(r"C:\LLMs\logs\kolibri.pid")
LOG_FILE = Path(r"C:\LLMs\logs\kolibri.log")
API_KEY_FILE = Path(r"C:\LLMs\config\kolibri_api_key.txt")
# Default model directory for GLM-5.2 in Colibri's custom format (NOT GGUF)
# Colibri uses its own container format with multiple .safetensors shards
# Model is a directory, not a single file
DEFAULT_MODEL_DIR = Path(r"C:\LLMs\models\kolibri")


def find_server() -> Path:
    """Find the kolibri server (openai_server.py from colibri project)."""
    # Check local repository first (local-models/kolibri/c/)
    workspace = Path(__file__).parent.parent  # local-models/kolibri/
    colibri_c = workspace / "c"
    if colibri_c.is_dir():
        openai_server = colibri_c / "openai_server.py"
        if openai_server.is_file():
            return openai_server
    
    # Fallback to shutil.which for backward compatibility
    command = shutil.which("kolibri-server") or shutil.which("kolibri-server.exe")
    if command:
        return Path(command)

    raise FileNotFoundError(
        "Colibri server not found. Install it by:\n"
        "1. Downloading from https://github.com/JustVugg/colibri/releases\n"
        "2. Or building from source: git clone https://github.com/JustVugg/colibri.git && cd colibri/c && make\n"
        "3. The server is 'openai_server.py' and requires 'glm.exe' (the C engine)"
    )


def api_key() -> str:
    """Get or create the API key for Colibri server."""
    API_KEY_FILE.parent.mkdir(parents=True, exist_ok=True)
    if not API_KEY_FILE.exists():
        API_KEY_FILE.write_text(secrets.token_urlsafe(32), encoding="ascii")
    return API_KEY_FILE.read_text(encoding="ascii").strip()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model-dir", type=Path, default=DEFAULT_MODEL_DIR)
    parser.add_argument("--port", type=int, default=DEFAULT_PORT)
    parser.add_argument("--ctx-size", type=int, default=131072)
    parser.add_argument("--background", action="store_true")
    parser.add_argument("--stop", action="store_true")
    args = parser.parse_args()

    if args.stop:
        if not PID_FILE.exists():
            print("No Colibri PID file found.")
            return
        pid = int(PID_FILE.read_text(encoding="ascii").strip())
        result = subprocess.run(["taskkill", "/PID", str(pid), "/T", "/F"], check=False)
        if result.returncode == 0:
            PID_FILE.unlink(missing_ok=True)
            print(f"Stopped Colibri server (PID {pid}).")
        else:
            raise SystemExit(f"Could not stop PID {pid}; inspect {PID_FILE}.")
        return

    model_dir = args.model_dir.resolve()
    # Check if model directory exists and has expected files
    if not model_dir.is_dir():
        raise SystemExit(
            f"Model directory not found: {model_dir}\n"
            "Download GLM-5.2 in Colibri format first using download_kolibri.py"
        )
    
    # Verify key files exist
    config_file = model_dir / "config.json"
    if not config_file.is_file():
        raise SystemExit(
            f"Model directory {model_dir} is missing config.json\n"
            "The download may have failed. Try running download_kolibri.py again."
        )

    server = find_server()
    
    # Find the glm engine binary - prefer local repository
    workspace = Path(__file__).parent.parent  # local-models/kolibri/
    colibri_c = workspace / "c"
    engine_path = None
    
    # Check for glm.exe in local colibri/c directory first
    if colibri_c.is_dir():
        for name in ["glm.exe", "glm"]:
            candidate = colibri_c / name
            if candidate.is_file():
                engine_path = candidate
                break
        # Also check for colibri-*.exe
        if not engine_path:
            matches = list(colibri_c.glob("colibri-*.exe"))
            if matches:
                engine_path = matches[0]
    
    if not engine_path:
        raise FileNotFoundError(
            f"glm.exe (Colibri C engine) not found in {colibri_c}.\n"
            "Install it by:\n"
            "1. Downloading pre-built binary from https://github.com/JustVugg/colibri/releases\n"
            "2. Or building from source: git clone https://github.com/JustVugg/colibri.git && cd colibri/c && make\n"
            "3. Place glm.exe in local-models/kolibri/c/"
        )
    
    command = [
        sys.executable,
        str(server),
        "--model",
        str(model_dir),
        "--model-id",
        "GLM-5.2-744B-MoE",
        "--host",
        "127.0.0.1",
        "--port",
        str(args.port),
        "--api-key",
        api_key(),
        "--engine",
        str(engine_path),
    ]
    
    # Set environment variables for the colibri engine
    # Context size
    os.environ["CTX"] = str(args.ctx_size)
    # Allow RAM overcommit (use with caution - may cause OOM kills if RAM is insufficient)
    os.environ["COLI_RAM_OVERCOMMIT"] = "1"
    # Reduce RAM budget for experts to fit in available memory
    os.environ["RAM_GB"] = "20"
    
    print(f"Starting Colibri (GLM-5.2) at http://127.0.0.1:{args.port}")
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
