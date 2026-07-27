$ErrorActionPreference = "Stop"
$venvPython = "$env:USERPROFILE\.venvs\voxcpm2\Scripts\python.exe"

if (-not (Test-Path -LiteralPath $venvPython)) {
    throw "Create the Python 3.12 environment at $env:USERPROFILE\.venvs\voxcpm2 first."
}

& $venvPython -m pip install --upgrade pip
& $venvPython -m pip install --editable (Split-Path -Parent $PSScriptRoot)

$projectDir = Split-Path -Parent $PSScriptRoot
& $venvPython -c "from pathlib import Path; from voxcpm2_mcp.service import Settings, VoxCPM2Service; print(VoxCPM2Service(Settings.from_env(Path(r'$projectDir'))).health())"
