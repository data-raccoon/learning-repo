$ErrorActionPreference = "Stop"
$venvPython = "$env:USERPROFILE\.venvs\voxcpm2\Scripts\python.exe"

if (-not (Test-Path -LiteralPath $venvPython)) {
    throw "VoxCPM2 environment is missing. Run scripts\setup.ps1 first."
}

& $venvPython -m voxcpm2_mcp.server --transport streamable-http
