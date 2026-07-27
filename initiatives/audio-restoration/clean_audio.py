"""Reproducibly clean the initiative's source voice recording with FFmpeg."""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
from pathlib import Path

import imageio_ffmpeg


ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
SOURCE = HERE / "inputs/latin-american-sample_uncleaned.ogg"
OUTPUTS = HERE / "outputs"
MASTER_V1 = OUTPUTS / "latin-american-sample_cleaned_v1.wav"
MASTER_V2 = OUTPUTS / "latin-american-sample_cleaned_v2_aggressive.wav"
REPORT = OUTPUTS / "analysis.json"

FILTERS_V1 = ",".join(
    [
        "adeclip",
        "adeclick=w=55:o=85:a=2:t=1.3:b=5",
        "highpass=f=100:p=2",
        "lowpass=f=8500:p=2",
        "afftdn=nr=18:nf=-40:tn=1:gs=10",
        "anlmdn=s=0.005:p=0.002:r=0.006:m=15",
        "deesser=i=0.25:m=0.35:f=0.55",
        (
            "silenceremove="
            "stop_periods=-1:stop_duration=0.6:stop_threshold=-38dB:"
            "stop_silence=0.25:detection=rms:window=0.03"
        ),
        "loudnorm=I=-18:TP=-3:LRA=7",
    ]
)

# Version 2 intentionally trades more natural room tone and high-frequency
# detail for stronger suppression of microphone crackle, hiss, and broadband
# contamination. Version 1 remains available when this sounds over-processed.
FILTERS_V2 = ",".join(
    [
        "adeclip",
        "adeclick=w=60:o=85:a=3:t=1.1:b=7",
        "highpass=f=100:p=2",
        "arnndn=m=initiatives/audio-restoration/models/sh.rnnn:mix=0.95",
        "afftdn=nr=10:nf=-42:tn=1:gs=8",
        "lowpass=f=9000:p=2",
        "deesser=i=0.3:m=0.4:f=0.52",
        (
            "silenceremove="
            "stop_periods=-1:stop_duration=0.45:stop_threshold=-35dB:"
            "stop_silence=0.18:detection=rms:window=0.03"
        ),
        "loudnorm=I=-18:TP=-3:LRA=6",
    ]
)


def run(*args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    command = [imageio_ffmpeg.get_ffmpeg_exe(), "-hide_banner", *args]
    return subprocess.run(
        command, check=check, text=True, capture_output=True, cwd=ROOT
    )


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def probe(path: Path) -> dict[str, object]:
    result = run(
        "-i",
        str(path),
        "-af",
        "volumedetect,silencedetect=noise=-42dB:d=0.35",
        "-f",
        "null",
        "NUL",
    )
    log = result.stderr

    def value(pattern: str) -> float | None:
        match = re.search(pattern, log)
        return float(match.group(1)) if match else None

    duration = value(r"Duration: 00:00:([0-9.]+)")
    mean = value(r"mean_volume: ([-0-9.]+) dB")
    peak = value(r"max_volume: ([-0-9.]+) dB")
    clipped = value(r"histogram_0db: ([0-9]+)")
    silences = [
        {
            "start_seconds": float(start),
            "end_seconds": float(end),
            "duration_seconds": float(length),
        }
        for start, end, length in re.findall(
            r"silence_start: ([0-9.]+).*?"
            r"silence_end: ([0-9.]+) \| silence_duration: ([0-9.]+)",
            log,
            flags=re.DOTALL,
        )
    ]
    stream = re.search(
        r"Audio: ([^,\n]+), ([0-9]+) Hz, ([^,\n]+)", log
    )
    return {
        "duration_seconds": duration,
        "codec": stream.group(1).strip() if stream else None,
        "sample_rate_hz": int(stream.group(2)) if stream else None,
        "channels": stream.group(3).strip() if stream else None,
        "mean_volume_db": mean,
        "peak_volume_db": peak,
        "samples_at_0db": int(clipped) if clipped is not None else 0,
        "silences_over_350ms": silences,
        "sha256": sha256(path),
        "bytes": path.stat().st_size,
    }


def main() -> None:
    if not SOURCE.is_file():
        raise SystemExit(f"Source not found: {SOURCE}")

    OUTPUTS.mkdir(exist_ok=True)
    before = probe(SOURCE)
    versions = {}
    for version, output, filters in [
        ("v1", MASTER_V1, FILTERS_V1),
        ("v2_aggressive", MASTER_V2, FILTERS_V2),
    ]:
        run(
            "-y",
            "-i",
            str(SOURCE),
            "-af",
            filters,
            "-ar",
            "48000",
            "-ac",
            "1",
            "-c:a",
            "pcm_s24le",
            str(output),
        )
        versions[version] = {
            "file": output.name,
            "filters": filters,
            "analysis": probe(output),
        }

    report = {
        "source": str(SOURCE.relative_to(HERE)).replace("\\", "/"),
        "neural_model": {
            "file": "models/sh.rnnn",
            "sha256": sha256(HERE / "models/sh.rnnn"),
            "source": "https://github.com/richardpl/arnndn-models/blob/master/sh.rnnn",
        },
        "before": before,
        "versions": versions,
        "checks": {"source_unchanged": before["sha256"] == sha256(SOURCE)},
    }
    for version, details in versions.items():
        analysis = details["analysis"]
        report["checks"][f"{version}_decodes"] = (
            analysis["duration_seconds"] is not None
        )
        report["checks"][f"{version}_has_headroom"] = (
            analysis["peak_volume_db"] is not None
            and analysis["peak_volume_db"] <= -1.0
        )
        report["checks"][f"{version}_has_no_0db_samples"] = (
            analysis["samples_at_0db"] == 0
        )
        report["checks"][f"{version}_duration_reduced"] = (
            analysis["duration_seconds"] is not None
            and before["duration_seconds"] is not None
            and analysis["duration_seconds"] < before["duration_seconds"]
        )
    REPORT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    if not all(report["checks"].values()):
        raise SystemExit("One or more validation checks failed; see analysis.json")
    print(json.dumps(report["checks"], sort_keys=True))


if __name__ == "__main__":
    main()
