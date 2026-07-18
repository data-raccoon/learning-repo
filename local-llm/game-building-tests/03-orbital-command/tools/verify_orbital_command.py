"""Run Orbital Command's integration suite in headless Edge; print compact status."""

from __future__ import annotations

import html
import re
import subprocess
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "orbital-command" / "index.html"
EDGE = Path(r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe")


def main() -> None:
    with tempfile.TemporaryDirectory(prefix="orbital-command-edge-") as profile:
        result = subprocess.run([
            str(EDGE), "--headless=new", "--disable-gpu", "--no-first-run", "--allow-file-access-from-files",
            f"--user-data-dir={profile}", "--virtual-time-budget=2500", "--dump-dom",
            INDEX.resolve().as_uri() + "?smoke=1",
        ], capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=60)
    match = re.search(r'<output id="smoke-result"[^>]*>(.*?)</output>', result.stdout, re.S)
    value = html.unescape(re.sub(r"<[^>]+>", "", match.group(1))).strip() if match else "FAIL:BROWSER_NO_RESULT"
    if value != "PASS":
        raise SystemExit(value)
    print("PASS browser_checks=14")


if __name__ == "__main__":
    main()
