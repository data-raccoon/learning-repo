"""Download GLM-5.2 in Kolibri format into C:\\LLMs.

IMPORTANT: Kolibri uses its OWN custom container format, NOT GGUF.
The model consists of multiple .safetensors shards (out-00000.safetensors, etc.)
plus config files, totaling ~370-380 GB.

Source: https://huggingface.co/jlnsrk/GLM-5.2-colibri-int4
This is a pre-converted GLM-5.2 (744B MoE) in int4 quantization for Kolibri.

Requirements:
- huggingface_hub package: pip install huggingface_hub
- ~380 GB free disk space
- Fast NVMe SSD recommended
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path


REPO_ID = "jlnsrk/GLM-5.2-colibri-int4"
DEFAULT_TARGET_DIR = Path(r"C:\LLMs\models\kolibri")
EXPECTED_FILES = [
    "config.json",
    "generation_config.json", 
    "tokenizer.json",
    "tokenizer_config.json",
]
MINIMUM_TOTAL_SIZE = 350_000_000_000  # 350 GB


def check_prerequisites() -> None:
    """Check if huggingface_hub is installed."""
    try:
        import huggingface_hub
    except ImportError:
        raise SystemExit(
            "huggingface_hub package is required.\n"
            "Install it with: pip install huggingface_hub"
        )


def download_with_huggingface_hub(repo_id: str, target_dir: Path) -> None:
    """Download the entire repository using huggingface_hub library."""
    from huggingface_hub import snapshot_download
    
    print(f"Downloading {repo_id} to {target_dir}")
    print(f"This will download ~370-380 GB of model files...")
    print()
    
    try:
        snapshot_download(
            repo_id=repo_id,
            local_dir=str(target_dir),
            local_dir_use_symlinks=False,
            resume_download=True,
            ignore_patterns=["*.msgpack", "*.h5", "*.tflite", "*.safetensors.index.json"],
        )
    except Exception as error:
        raise RuntimeError(f"Download failed: {error}") from error
    
    # Verify download
    verify_download(target_dir)


def download_with_hf_cli(repo_id: str, target_dir: Path) -> None:
    """Download using hf CLI tool (alternative method)."""
    cmd = [
        "huggingface-cli",
        "download",
        repo_id,
        "--local-dir", str(target_dir),
        "--local-dir-use-symlinks", "False",
        "--resume-download",
    ]
    
    print(f"Running: {' '.join(cmd)}")
    print()
    
    result = subprocess.run(cmd, check=False, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"hf CLI failed:\n{result.stderr}")
    
    verify_download(target_dir)


def verify_download(target_dir: Path) -> None:
    """Verify the downloaded files."""
    # Check for expected files
    missing = []
    for expected in EXPECTED_FILES:
        if not (target_dir / expected).is_file():
            missing.append(expected)
    
    if missing:
        raise RuntimeError(f"Missing expected files: {missing}")
    
    # Check total size
    total_size = sum(
        f.stat().st_size for f in target_dir.rglob("*") if f.is_file()
    )
    
    print(f"\nDownload complete!")
    print(f"Total size: {total_size / 1024**3:.2f} GB")
    print(f"Files: {len(list(target_dir.rglob('*'))) - 1} (including subdirectories)")
    
    if total_size < MINIMUM_TOTAL_SIZE:
        print(f"\nWARNING: Downloaded size ({total_size / 1024**3:.0f} GB) is below expected ({MINIMUM_TOTAL_SIZE / 1024**3:.0f} GB)")
        print("Some files may be missing. Check your network connection and try again.")


def main() -> None:
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        "--target-dir",
        type=Path,
        default=DEFAULT_TARGET_DIR,
        help="Target directory (default: C:\\LLMs\\models\\kolibri)"
    )
    parser.add_argument(
        "--method",
        choices=["huggingface_hub", "hf_cli"],
        default="huggingface_hub",
        help="Download method (default: huggingface_hub Python library)"
    )
    args = parser.parse_args()
    
    try:
        check_prerequisites()
        
        target_dir = args.target_dir.resolve()
        target_dir.parent.mkdir(parents=True, exist_ok=True)
        
        # Check if already exists
        if target_dir.exists():
            total = sum(f.stat().st_size for f in target_dir.rglob("*") if f.is_file())
            if total >= MINIMUM_TOTAL_SIZE:
                print(f"Model already present: {target_dir}")
                print(f"Size: {total / 1024**3:.2f} GB")
                return
        
        if args.method == "huggingface_hub":
            download_with_huggingface_hub(REPO_ID, target_dir)
        else:
            download_with_hf_cli(REPO_ID, target_dir)
        
        print(f"\nModel downloaded to: {target_dir}")
        print(f"\nNext steps:")
        print(f"1. Install Kolibri engine: git clone https://github.com/JustVugg/colibri.git && cd colibri/c && ./setup.sh")
        print(f"2. Set COLIBRI_MODEL={target_dir}")
        print(f"3. Run: ./coli chat")
        
    except Exception as error:
        raise SystemExit(f"Download failed: {error}") from error


if __name__ == "__main__":
    main()
