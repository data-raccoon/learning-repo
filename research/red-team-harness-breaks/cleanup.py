#!/usr/bin/env python3
"""Clean up red-team harness break experiment targets and old reports."""

from __future__ import annotations

import subprocess
import shutil
from pathlib import Path

WORKSPACE = Path(__file__).parent.resolve()
TARGETS_DIR = WORKSPACE / "targets"
RESULTS_DIR = WORKSPACE / "results"
REPO_ROOT = WORKSPACE.parent.parent  # research directory is under repo root

# For RT-11, RT-12, RT-13: output.md is tracked in git as a seed file
# and is also an output artifact. We need to reset it to git state.
# For other tests, only context files are tracked.
TRACKED_FILES = {
    "rt-01-prompt-injection": ["context.md"],
    "rt-02-path-escape": ["context.md"],
    "rt-03-verifier-bypass": ["context.md"],
    "rt-04-ownership-bypass": ["context.md", "allowed.txt"],
    "rt-05-symlink-injection": [],
    "rt-06-command-injection": ["context.md"],
    "rt-07-schema-smuggling": ["context.md"],
    "rt-08-token-exhaustion": ["context.md"],
    "rt-09-role-override": ["context.md"],
    "rt-10-snapshot-race": ["context.md"],
    "rt-11-materialization-schema-smuggling": ["context.md", "output.md", "output.schema.json"],
    "rt-12-transcript-role-injection": ["context.md", "output.md", "output.schema.json", "prior.md"],
    "rt-13-output-amplification": ["context.md", "output.md", "output.schema.json"],
    "rt-14-verifier-cwd-escape": ["context.md"],
}


def reset_tracked_files() -> None:
    """Reset tracked files to their git state."""
    if not TARGETS_DIR.is_dir():
        return
    
    for target_dir in TARGETS_DIR.iterdir():
        if target_dir.is_dir():
            dir_name = target_dir.name
            tracked = TRACKED_FILES.get(dir_name, [])
            if not tracked:
                continue
            
            print(f"Resetting tracked files in {dir_name}...")
            for filename in tracked:
                file_path = target_dir / filename
                if file_path.is_file():
                    # Remove the file, git checkout will restore it
                    file_path.unlink()
    
    # Use git checkout to restore all tracked files in targets
    try:
        subprocess.run(
            ["git", "checkout", "--", "research/red-team-harness-breaks/targets/"],
            cwd=REPO_ROOT,
            check=True,
            capture_output=True,
            text=True
        )
        print("Tracked files reset to git state")
    except Exception as e:
        print(f"Warning: Could not reset tracked files via git: {e}")


def clean_generated_files() -> None:
    """Remove files that are NOT tracked by git."""
    if not TARGETS_DIR.is_dir():
        print(f"Targets directory not found: {TARGETS_DIR}")
        return

    for target_dir in TARGETS_DIR.iterdir():
        if target_dir.is_dir():
            dir_name = target_dir.name
            tracked = set(TRACKED_FILES.get(dir_name, []))
            print(f"Cleaning generated files in {dir_name}...")
            
            for item in target_dir.iterdir():
                item_name = item.name
                # Remove anything not tracked
                if item_name not in tracked:
                    if item.is_file():
                        item.unlink()
                    elif item.is_dir():
                        # Remove any generated subdirectories
                        shutil.rmtree(item, ignore_errors=True)


def clean_results() -> None:
    """Remove old report files but keep the directory."""
    if not RESULTS_DIR.is_dir():
        print(f"Results directory not found: {RESULTS_DIR}")
        return

    removed = 0
    for item in RESULTS_DIR.iterdir():
        if item.is_file():
            item.unlink()
            removed += 1
    print(f"Removed {removed} old report files from {RESULTS_DIR.name}")


def main() -> None:
    print(f"Cleaning red-team harness targets in: {WORKSPACE}")
    reset_tracked_files()
    clean_generated_files()
    clean_results()
    print("Cleanup complete.")


if __name__ == "__main__":
    main()
