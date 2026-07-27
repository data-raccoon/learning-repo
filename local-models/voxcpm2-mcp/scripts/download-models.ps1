$ErrorActionPreference = "Stop"
$venvPython = "$env:USERPROFILE\.venvs\voxcpm2\Scripts\python.exe"
$modelDir = "$env:USERPROFILE\.cache\voxcpm2-gguf"

if (-not (Test-Path -LiteralPath $venvPython)) {
    throw "VoxCPM2 Python environment is missing."
}

& $venvPython -c "from huggingface_hub import hf_hub_download; from pathlib import Path; root=Path(r'$modelDir'); print(hf_hub_download('DennisHuang648/VoxCPM2-GGUF','VoxCPM2-BaseLM-Q8_0.gguf',local_dir=root)); print(hf_hub_download('DennisHuang648/VoxCPM2-GGUF','VoxCPM2-Acoustic-F16.gguf',local_dir=root))"
