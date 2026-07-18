"""Download the approved Ministral GGUF into C:\\LLMs with resume support."""

from __future__ import annotations

import argparse
import os
import sys
import urllib.request
from pathlib import Path


MODEL_URL = (
    "https://huggingface.co/mistralai/Ministral-3-3B-Instruct-2512-GGUF/"
    "resolve/main/Ministral-3-3B-Instruct-2512-Q4_K_M.gguf?download=true"
)
DEFAULT_TARGET = Path(
    r"C:\LLMs\models\mistral\Ministral-3-3B-Instruct-2512-Q4_K_M.gguf"
)
MINIMUM_EXPECTED_SIZE = 2_000_000_000
CHUNK_SIZE = 8 * 1024 * 1024


def download(url: str, target: Path) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    partial = target.with_suffix(target.suffix + ".part")

    if target.exists() and target.stat().st_size >= MINIMUM_EXPECTED_SIZE:
        print(f"Model already present: {target}")
        return

    existing = partial.stat().st_size if partial.exists() else 0
    request = urllib.request.Request(url)
    if existing:
        request.add_header("Range", f"bytes={existing}-")

    with urllib.request.urlopen(request, timeout=120) as response:
        resumed = existing > 0 and response.status == 206
        if existing and not resumed:
            existing = 0
        mode = "ab" if resumed else "wb"
        remaining = int(response.headers.get("Content-Length", "0"))
        expected = existing + remaining if remaining else 0

        print(f"Downloading to {partial}")
        with partial.open(mode) as output:
            downloaded = existing
            while chunk := response.read(CHUNK_SIZE):
                output.write(chunk)
                downloaded += len(chunk)
                if expected:
                    percent = downloaded * 100 / expected
                    print(
                        f"\r{downloaded / 1024**3:.2f} / {expected / 1024**3:.2f} GiB "
                        f"({percent:.1f}%)",
                        end="",
                        flush=True,
                    )
                else:
                    print(f"\r{downloaded / 1024**3:.2f} GiB", end="", flush=True)
    print()

    if partial.stat().st_size < MINIMUM_EXPECTED_SIZE:
        raise RuntimeError(f"Downloaded file is unexpectedly small: {partial.stat().st_size} bytes")
    os.replace(partial, target)
    print(f"Download complete: {target}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--target", type=Path, default=DEFAULT_TARGET)
    args = parser.parse_args()
    try:
        download(MODEL_URL, args.target.resolve())
    except Exception as error:
        raise SystemExit(f"Download failed: {error}") from error


if __name__ == "__main__":
    main()
