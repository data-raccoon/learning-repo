"""Run Glimweave's integrated browser checks and retain compact diagnostic evidence."""

from __future__ import annotations

import argparse
import html
import json
import re
import subprocess
import tempfile
from pathlib import Path


EXPERIMENT = Path(__file__).resolve().parents[1]
EDGE = Path(r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe")
EVIDENCE = EXPERIMENT / ".orchestration" / "runtime" / "verification-latest"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="Print one machine-readable result")
    parser.add_argument("--no-screenshot", action="store_true", help="Skip screenshot capture")
    args = parser.parse_args()
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    dom_path = EVIDENCE / "dom.html"
    stderr_path = EVIDENCE / "edge-stderr.txt"
    screenshot_path = EVIDENCE / "page.png"
    if not args.no_screenshot:
        screenshot_path.unlink(missing_ok=True)
    with tempfile.TemporaryDirectory(prefix="glimweave-edge-") as profile:
        command = [
            str(EDGE), "--headless=new", "--disable-gpu", "--no-first-run",
            "--allow-file-access-from-files", f"--user-data-dir={profile}",
            "--virtual-time-budget=5000", "--dump-dom", "--window-size=1440,900",
        ]
        if not args.no_screenshot:
            command.append(f"--screenshot={screenshot_path}")
        command.append((EXPERIMENT / "index.html").resolve().as_uri() + "?smoke=1")
        result = subprocess.run(command, capture_output=True, text=True, encoding="utf-8",
                                errors="replace", timeout=75)
    dom_path.write_text(result.stdout, encoding="utf-8")
    stderr_path.write_text(result.stderr, encoding="utf-8")
    match = re.search(r'<output id="smoke-result"[^>]*>(.*?)</output>', result.stdout, re.S)
    value = html.unescape(re.sub(r"<[^>]+>", "", match.group(1))).strip() if match else "FAIL:BROWSER_NO_RESULT"
    title = re.search(r"<title>(.*?)</title>", result.stdout, re.I | re.S)
    payload = {
        "status": "pass" if value == "PASS" else "fail", "result": value,
        "edge_exit_code": result.returncode, "dom_bytes": len(result.stdout.encode("utf-8")),
        "title": html.unescape(title.group(1)).strip() if title else None,
        "smoke_result_present": bool(match), "stderr_tail": result.stderr.strip()[-1200:],
        "evidence": {
            "dom": str(dom_path.relative_to(EXPERIMENT)),
            "stderr": str(stderr_path.relative_to(EXPERIMENT)),
            "screenshot": str(screenshot_path.relative_to(EXPERIMENT)) if screenshot_path.is_file() else None,
        },
    }
    if args.json:
        print(json.dumps(payload, separators=(",", ":"), ensure_ascii=False))
    elif value == "PASS":
        print("PASS browser_suite=core+integration")
    if value != "PASS":
        if not args.json:
            print(value)
        raise SystemExit(1)


if __name__ == "__main__":
    main()
