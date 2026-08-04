"""Run one fixed Gradle verification task through the checked-in wrapper."""

from __future__ import annotations

import os
from pathlib import Path
import subprocess
import sys


ALLOWED_TASKS = {"compileJava", "compileClientJava", "test", "build"}


def main(argv: list[str]) -> int:
    if len(argv) != 1 or argv[0] not in ALLOWED_TASKS:
        print("expected exactly one allowlisted Gradle task", file=sys.stderr)
        return 2
    root = Path(__file__).resolve().parents[2]
    wrapper = root / ("gradlew.bat" if os.name == "nt" else "gradlew")
    wrapper_jar = root / "gradle" / "wrapper" / "gradle-wrapper.jar"
    if not wrapper.is_file() or not wrapper_jar.is_file():
        print("checked-in Gradle wrapper is incomplete", file=sys.stderr)
        return 2
    command = [str(wrapper), "--no-daemon", argv[0]]
    completed = subprocess.run(command, cwd=root, shell=False, check=False)
    return completed.returncode


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
