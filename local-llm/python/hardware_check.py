"""Collect local-LLM hardware information without third-party packages."""

from __future__ import annotations

import argparse
import ctypes
import json
import os
import platform
import shutil
import subprocess
import sys
from ctypes import wintypes
from pathlib import Path
from typing import Any


GIB = 1024**3


class MemoryStatusEx(ctypes.Structure):
    _fields_ = [
        ("dwLength", wintypes.DWORD),
        ("dwMemoryLoad", wintypes.DWORD),
        ("ullTotalPhys", ctypes.c_ulonglong),
        ("ullAvailPhys", ctypes.c_ulonglong),
        ("ullTotalPageFile", ctypes.c_ulonglong),
        ("ullAvailPageFile", ctypes.c_ulonglong),
        ("ullTotalVirtual", ctypes.c_ulonglong),
        ("ullAvailVirtual", ctypes.c_ulonglong),
        ("ullAvailExtendedVirtual", ctypes.c_ulonglong),
    ]


def memory_info() -> dict[str, float | int]:
    status = MemoryStatusEx()
    status.dwLength = ctypes.sizeof(status)
    if not ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(status)):
        raise ctypes.WinError()
    return {
        "total_gb": round(status.ullTotalPhys / GIB, 1),
        "available_gb": round(status.ullAvailPhys / GIB, 1),
        "load_percent": status.dwMemoryLoad,
    }


def cpu_name() -> str:
    try:
        import winreg

        key_path = r"HARDWARE\DESCRIPTION\System\CentralProcessor\0"
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path) as key:
            return str(winreg.QueryValueEx(key, "ProcessorNameString")[0]).strip()
    except (ImportError, OSError):
        return platform.processor() or "unknown"


def nvidia_info() -> list[dict[str, Any]]:
    command = [
        "nvidia-smi",
        "--query-gpu=name,memory.total,memory.used,memory.free,driver_version,compute_cap",
        "--format=csv,noheader,nounits",
    ]
    try:
        result = subprocess.run(
            command,
            check=True,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
    except (FileNotFoundError, subprocess.CalledProcessError):
        return []

    keys = [
        "name",
        "vram_total_mb",
        "vram_used_mb",
        "vram_free_mb",
        "driver_version",
        "compute_capability",
    ]
    gpus = []
    for line in result.stdout.splitlines():
        values = [value.strip() for value in line.split(",")]
        if len(values) == len(keys):
            gpu = dict(zip(keys, values, strict=True))
            for key in ("vram_total_mb", "vram_used_mb", "vram_free_mb"):
                gpu[key] = int(gpu[key])
            gpus.append(gpu)
    return gpus


def disk_info(path: Path) -> dict[str, Any]:
    usage = shutil.disk_usage(path)
    return {
        "path": str(path),
        "total_gb": round(usage.total / GIB, 1),
        "free_gb": round(usage.free / GIB, 1),
    }


def collect(model_root: Path) -> dict[str, Any]:
    return {
        "python": {
            "version": platform.python_version(),
            "executable": sys.executable,
        },
        "system": {
            "os": platform.platform(),
            "machine": platform.machine(),
            "cpu": cpu_name(),
            "logical_cpus": os.cpu_count(),
            "memory": memory_info(),
        },
        "gpu": nvidia_info(),
        "storage": disk_info(model_root if model_root.exists() else model_root.anchor),
        "model_root": {
            "path": str(model_root),
            "exists": model_root.is_dir(),
        },
        "tools": {
            name: shutil.which(name)
            for name in ("llama-server", "llama-cli", "ollama", "docker", "wsl")
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model-root", type=Path, default=Path(r"C:\LLMs"))
    parser.add_argument("--output", type=Path, help="Optional JSON output file")
    args = parser.parse_args()

    report = collect(args.model_root.resolve())
    rendered = json.dumps(report, indent=2, ensure_ascii=False)
    print(rendered)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
