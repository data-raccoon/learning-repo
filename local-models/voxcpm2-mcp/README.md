# VoxCPM2 MCP server

Local Streamable HTTP MCP server for generating WAV files with one configured,
consented VoxCPM2 reference voice.

## Prerequisites

- 64-bit Python 3.12
- NVIDIA GPU with Vulkan support
- CMake, Visual Studio C++ Build Tools, and the Vulkan SDK
- `llama.cpp-omni` checkout at `$env:USERPROFILE\git\llama.cpp-omni`
- A voice sample whose speaker has authorized cloning

Build the quantized Vulkan runtime, download the two GGUF modules, and install
the MCP package:

```powershell
.\scripts\setup.ps1
.\scripts\build-quantized.ps1
.\scripts\download-models.ps1
```

The environment lives at `$env:USERPROFILE\.venvs\voxcpm2`. The Q8 BaseLM and
F16 acoustic weights live under `$env:USERPROFILE\.cache\voxcpm2-gguf`; the
compiled runtime stays in the external checkout. None are stored in this
repository.

## Configure

The configured sample is `data/latin-american-sample.wav`. Optionally add its
verbatim transcript at
`data/reference.txt` to enable transcript-assisted cloning. The `data/`
directory is gitignored.

Defaults can be overridden with:

| Variable | Default |
| --- | --- |
| `VOXCPM2_DATA_DIR` | `./data` |
| `VOXCPM2_REFERENCE_WAV` | `./data/latin-american-sample.wav` |
| `VOXCPM2_REFERENCE_TEXT` | `./data/reference.txt` |
| `VOXCPM2_OUTPUT_DIR` | `./data/outputs` |
| `VOXCPM2_MODEL` | `openbmb/VoxCPM2` |
| `VOXCPM2_BACKEND` | `cpp` |
| `VOXCPM2_CPP_BINARY` | `~/git/llama.cpp-omni/build-vulkan/bin/Release/voxcpm2-cli.exe` |
| `VOXCPM2_BASE_MODEL` | `~/.cache/voxcpm2-gguf/VoxCPM2-BaseLM-Q8_0.gguf` |
| `VOXCPM2_ACOUSTIC_MODEL` | `~/.cache/voxcpm2-gguf/VoxCPM2-Acoustic-F16.gguf` |
| `VOXCPM2_INFERENCE_TIMESTEPS` | `10` |
| `VOXCPM2_MAX_STEPS` | `200` |
| `VOXCPM2_PROCESS_TIMEOUT_SECONDS` | `600` |

The MCP tool never downloads or builds dependencies during a request. After all
three setup commands complete, start it:

```powershell
.\scripts\start.ps1
```

- MCP endpoint: `http://127.0.0.1:8765/mcp`
- Health endpoint: `http://127.0.0.1:8765/health`

Each request invokes the quantized Vulkan CLI; calls are serialized. On the RTX
2080 SUPER, the measured incremental GPU allocation was about 5.6 GiB.

## Test

Tests use a fake model and do not require CUDA or VoxCPM weights:

```powershell
& "$env:USERPROFILE\.venvs\voxcpm2\Scripts\python.exe" -m unittest discover -s tests -v
```

Client configuration examples are in
[`../../connectors/voxcpm2/README.md`](../../connectors/voxcpm2/README.md).
