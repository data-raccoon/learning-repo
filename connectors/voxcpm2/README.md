# VoxCPM2 MCP connector proposal

## Recommendation

Run one optional VoxCPM2 MCP server on localhost and connect Codex, Mistral
Vibe, and Continue to that same process over Streamable HTTP. The MCP process
invokes a quantized Vulkan CLI for synthesis.

Keep the components separated by repository concern:

```text
local-models/voxcpm2-mcp/       Server source, dependency lock, tests, and launch scripts
connectors/voxcpm2/             Shared setup guide and client configuration examples
local-models/voxcpm2-mcp/data/  Gitignored reference audio, optional transcript, and output WAVs
```

This keeps the measured incremental GPU allocation near 5.6 GiB and avoids
loading a model once per editor extension. It also matches the repository rule
that serving code belongs under
`local-models/`, while client integration guidance belongs under `connectors/`.
Model weights, virtual environments, runtime logs, and PID files must remain
outside the repository.

## Local runtime

Use a dedicated Python 3.12 virtual environment:

```powershell
py -3.12 -m venv "$env:USERPROFILE\.venvs\voxcpm2"
& "$env:USERPROFILE\.venvs\voxcpm2\Scripts\python.exe" -m pip install --upgrade pip
```

Do not use the shared `$env:USERPROFILE\.venvs\all` environment: it currently
uses Python 3.14, while VoxCPM2 requires Python 3.10 through 3.12. Pin the final
dependency set in the server project rather than installing unversioned packages
from the client configurations. The implementation pins matching CUDA-enabled
Torch and Torchaudio wheels; a default PyPI install can silently select
CPU-only wheels on Windows.

The target machine has an NVIDIA GeForce RTX 2080 SUPER with 8 GB VRAM. The
original PyTorch backend was rejected after two 20-minute timeouts. The
quantized backend uses a Q8 BaseLM plus F16 acoustic module and should:

- accept only one synthesis job at a time;
- fail clearly when the external executable or either GGUF module is absent;
- bind to `127.0.0.1`, not all network interfaces;
- expose a health check separately from the MCP endpoint;
- save 48 kHz WAV files beneath the configured gitignored output directory.

The GGUF downloads belong in the external model directory, never in this
repository.

## Voice sample

Place the consented sample at:

```text
local-models/voxcpm2-mcp/data/reference-sample.wav
```

The entire `data/` directory is gitignored. Initially use isolated-reference
cloning, which does not require a transcript. If a verbatim transcript becomes
available later, save it as `data/reference.txt`; the server may then use both
files for VoxCPM2's higher-fidelity continuation-cloning mode.

The MCP API should not allow callers to select arbitrary reference files. One
configured, private reference sample keeps filesystem access narrow and makes
the voice identity explicit. Use only a voice whose speaker has authorized
cloning, and identify generated recordings as synthetic.

## MCP interface

Expose one mutating tool:

`synthesize_speech(text, filename?, style?, seed?)`

- `text` is required and length-limited.
- `filename` is optional and sanitized to a basename; the server adds `.wav`.
- `style` is optional and controls delivery without changing the configured
  speaker.
- `seed` is optional for repeatability.
- The result contains the absolute WAV path, sample rate, duration, seed, and
  whether isolated-reference or transcript-assisted cloning was used.

Reject empty or over-limit text, path traversal, unsupported output formats,
concurrent work beyond the single-job queue, and missing/unreadable reference
audio with structured MCP errors. Do not play audio automatically.

Use a loopback URL such as:

```text
http://127.0.0.1:8765/mcp
```

## Client configuration

All clients should point to the same URL; none should start its own model
process.

### Codex

Add this to the repository-root `.codex/config.toml`, merging it with any
existing project MCP configuration:

```toml
[mcp_servers.voxcpm2]
url = "http://127.0.0.1:8765/mcp"
enabled_tools = ["synthesize_speech"]
startup_timeout_sec = 10
tool_timeout_sec = 300
```

### Mistral Vibe

Add this machine-local entry to Vibe's `config.toml`:

```toml
[[mcp_servers]]
name = "voxcpm2"
transport = "streamable-http"
url = "http://127.0.0.1:8765/mcp"
startup_timeout_sec = 10
tool_timeout_sec = 300
```

The same entry is available as
[`vibe.config.toml`](vibe.config.toml) for copying or merging. It is a template
because Vibe reads machine-local configuration; the repository does not
overwrite a user's other Vibe servers or permissions.

Grant the generated `voxcpm2_synthesize_speech` tool an ask-before-use
permission because it writes an audio file.

### Continue

Create `.continue/mcpServers/voxcpm2.yaml`:

```yaml
name: VoxCPM2
version: 0.1.0
schema: v1
mcpServers:
  - name: voxcpm2
    type: streamable-http
    url: http://127.0.0.1:8765/mcp
    connectionTimeout: 300000
```

Continue exposes MCP tools only in Agent mode.

## Acceptance checks

Before enabling the client configurations:

1. Unit-test filename sanitization, text limits, missing sample handling, and
   serialized job execution without loading the model.
2. Start the service with the dedicated environment and confirm the health
   endpoint reports the model, CUDA device, and readiness without exposing local
   private paths.
3. Generate a short consented test phrase and verify a readable 48 kHz WAV is
   written only beneath `data/outputs/`.
4. Connect each client separately and confirm it discovers exactly
   `synthesize_speech`.
5. Connect all three clients concurrently and confirm they share one model
   process and queued calls complete without out-of-memory failure.

## Upstream basis

- VoxCPM2: <https://github.com/OpenBMB/VoxCPM>
- VoxCPM2 model card: <https://huggingface.co/openbmb/VoxCPM2>
- Codex MCP configuration: <https://developers.openai.com/codex/mcp>
- Mistral Vibe MCP configuration:
  <https://docs.mistral.ai/vibe/code/cli/mcp-servers>
- Continue MCP configuration:
  <https://docs.continue.dev/customize/deep-dives/mcp>
