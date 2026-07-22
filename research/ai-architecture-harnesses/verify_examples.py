"""Validate structure and run every dependency-free example offline."""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parent
EXPECTED_APPROACHES = (
    "01-workflow-first",
    "02-multi-agent-und-multi-modell",
    "03-durable-execution",
    "04-vertraege-policy-gates",
    "05-sicherheit-und-isolation",
    "06-evaluation-observability",
    "07-formale-methoden",
    "08-referenzarchitektur",
    "09-harness-vergleich",
    "10-einfuehrungsplan",
)


def run(command: list[str], cwd: Path) -> dict[str, object]:
    environment = os.environ.copy()
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    completed = subprocess.run(
        command,
        cwd=cwd,
        env=environment,
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
    )
    return {
        "command": command,
        "returncode": completed.returncode,
        "stdout": completed.stdout[-2000:],
        "stderr": completed.stderr[-2000:],
    }


def main() -> int:
    results: dict[str, object] = {}
    failed = False
    approach_dirs = sorted(path for path in ROOT.iterdir() if path.is_dir() and re.match(r"^\d\d-", path.name))
    actual_names = tuple(path.name for path in approach_dirs)
    if actual_names != EXPECTED_APPROACHES:
        results["_structure"] = {
            "expected": EXPECTED_APPROACHES,
            "actual": actual_names,
            "error": "approach folder set differs",
        }
        failed = True

    for approach in approach_dirs:
        example = approach / "beispiel"
        required = (approach / "README.md", approach / "KURZFASSUNG.md", example / "README.md")
        test_files = tuple(example.rglob("test*.py")) if example.is_dir() else ()
        implementation_files = tuple(
            path for path in example.glob("*.py")
            if path.name != "demo.py" and not path.name.startswith("test")
        ) if example.is_dir() else ()
        structure_errors = [f"missing {path.relative_to(ROOT)}" for path in required if not path.is_file()]
        if not test_files:
            structure_errors.append("no test*.py files")
        if not implementation_files:
            structure_errors.append("no implementation module")
        if structure_errors:
            results[approach.name] = {"structure_errors": structure_errors}
            failed = True
            continue

        start_dir = "tests" if (example / "tests").is_dir() else "."
        checks = [run([sys.executable, "-m", "unittest", "discover", "-s", start_dir, "-p", "test*.py", "-v"], example)]
        match = re.search(r"Ran (\d+) tests?", checks[0]["stdout"] + checks[0]["stderr"])
        checks[0]["test_count"] = int(match.group(1)) if match else 0
        if checks[0]["test_count"] == 0:
            failed = True
        if (example / "demo.py").is_file():
            with tempfile.TemporaryDirectory(prefix=f"{approach.name}-") as temporary_directory:
                checks.append(run([sys.executable, str(example / "demo.py")], Path(temporary_directory)))
        if any(check["returncode"] != 0 for check in checks):
            failed = True
        results[approach.name] = checks

    print(json.dumps(results, ensure_ascii=False, indent=2))
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
