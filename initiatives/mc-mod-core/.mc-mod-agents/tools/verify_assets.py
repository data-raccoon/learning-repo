"""Verify declared Fabric resource assets and their provenance manifest."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import struct
import sys


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def png_dimensions(path: Path) -> tuple[int, int]:
    header = path.read_bytes()[:24]
    if len(header) != 24 or header[:8] != b"\x89PNG\r\n\x1a\n" or header[12:16] != b"IHDR":
        raise ValueError(f"invalid PNG header: {path}")
    return struct.unpack(">II", header[16:24])


def main() -> int:
    root = Path(__file__).resolve().parents[2]
    try:
        spec = json.loads((root / "mod-spec.json").read_text(encoding="utf-8"))
        manifest = json.loads((root / "assets" / "asset-manifest.json").read_text(encoding="utf-8"))
        entries = manifest["assets"]
        if not isinstance(entries, list) or not all(isinstance(item, dict) for item in entries):
            raise ValueError("asset manifest entries must be objects")
        by_path = {item["path"]: item for item in entries}
        declared = spec["creative_artifacts"]
        if len(entries) != len(by_path) or len(entries) != len(declared):
            raise ValueError("asset manifest contains duplicate or extra entries")
        if manifest["mod_id"] != spec["mod_id"] or set(by_path) != set(declared):
            raise ValueError("asset manifest does not exactly cover creative_artifacts")
        for relative in declared:
            path = root / relative
            if not path.is_file():
                raise ValueError(f"missing creative artifact: {relative}")
            entry = by_path[relative]
            if entry.get("checksum") != sha256(path):
                raise ValueError(f"checksum mismatch: {relative}")
            if entry.get("size_bytes") != path.stat().st_size:
                raise ValueError(f"byte-size mismatch: {relative}")
            if entry.get("provenance") not in {"procedural", "placeholder", "original", "modified"}:
                raise ValueError(f"invalid provenance: {relative}")
            if not isinstance(entry.get("placeholder"), bool) or not entry.get("format"):
                raise ValueError(f"incomplete provenance fields: {relative}")
            if path.suffix.lower() == ".json":
                json.loads(path.read_text(encoding="utf-8"))
            if path.suffix.lower() == ".png":
                width, height = png_dimensions(path)
                if width & (width - 1) or height & (height - 1):
                    raise ValueError(f"PNG dimensions are not powers of two: {relative}")
            if path.suffix.lower() == ".ogg" and path.read_bytes()[:4] != b"OggS":
                raise ValueError(f"invalid OGG header: {relative}")
        print(json.dumps({"status": "passed", "assets": len(declared)}))
        return 0
    except (OSError, KeyError, TypeError, ValueError, json.JSONDecodeError) as error:
        print(str(error), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
