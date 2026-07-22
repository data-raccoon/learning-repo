#!/usr/bin/env python3
"""
RT-05 — Symlink injection setup helper.
Creates a symlink inside the target directory that points outside the workspace root.
The harness path-validation code must reject it.

Safe: this script only creates a symlink; it never writes any payload data
to the destination.  A BREAK is recorded only if the harness runner silently
accepts and reads the symlink without raising ContractError.
"""

import os
import sys
from pathlib import Path

TARGET = Path(__file__).parent / "targets" / "rt-05-symlink-injection"
TARGET.mkdir(parents=True, exist_ok=True)

SYMLINK = TARGET / "escape_link.md"

# Point to something that definitely exists outside the project tree —
# the user's home directory README or any OS file.  A breakout is harmful
# only if the harness reads the *contents*; the test merely confirms the link
# is rejected at validation time before any content reaches the model.
OUTSIDE = Path.home() / "Documents"
if not OUTSIDE.exists():
    OUTSIDE = Path(os.environ.get("SYSTEMROOT", "C:\\Windows")) / "win.ini"

if SYMLINK.is_symlink():
    SYMLINK.unlink()

try:
    SYMLINK.symlink_to(OUTSIDE)
    print(f"[OK]  Symlink created: {SYMLINK} -> {OUTSIDE}")
except OSError as exc:
    print(f"[WARN] Could not create symlink (needs admin or Developer Mode on Windows): {exc}")
    print("       RT-05 will be run as a static-analysis-only test.")
