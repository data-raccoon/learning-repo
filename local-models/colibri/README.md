# Colibri

Local Colibri inference engine for running large MoE models (GLM-5.2 744B parameters) on consumer hardware with disk-streaming.

## Architecture

Colibri is a pure C, zero-dependency inference engine that exploits MoE sparsity to run massive models with limited RAM. It streams only active experts from disk, using Multi-head Latent Attention (MLA) with compressed KV-cache.

**Key Characteristics:**
- Pure C implementation (~1,300–2,400 lines)
- Zero external dependencies (no BLAS, no CUDA, no Python at runtime)
- Disk streaming of MoE experts
- Supports GLM-5.2 (744B parameters) on 25 GB+ RAM
- Portable across Linux, Windows, macOS

## Registry Status

Colibri is registered in `agent-orchestrator/config/deferred/` with `deferred` status (POC only — too slow for current production use):

- **Provider**: `local-colibri` — OpenAI-compatible local server at `http://127.0.0.1:8082/v1`
- **Model**: `glm-5.2-744b-moe-local` — GLM-5.2 with 131 K context tokens
- **Harness**: `colibri-openai-chat` — OpenAI-compatible chat API
- **Profile**: `colibri-glm-5.2-inference` — deferred; not routable until re-evaluated

## Setup

### 1. Install Colibri Engine

Build from source or install via package manager:
```powershell
# Option 1: Build from source
git clone https://github.com/JustVugg/colibri.git
cd colibri
make

# Option 2: Winget (when available)
winget install colibri
```

The executable should be named `colibri-server` or `colibri-server.exe`.

### 2. Download Model

**IMPORTANT**: Colibri uses its **own custom container format**, NOT GGUF.

Download GLM-5.2 in Colibri format to:
```
C:\LLMs\models\colibri\  (directory containing multiple .safetensors files)
```

**Recommended source**: [jlnsrk/GLM-5.2-colibri-int4](https://huggingface.co/jlnsrk/GLM-5.2-colibri-int4)
- Pre-converted GLM-5.2 (744B MoE) in int4 quantization
- **Size: ~370–380 GB** — split across many `.safetensors` shards
- Format: Colibri's native container format with `out-*.safetensors` shards, `config.json`, tokenizer files, and an MTP head for speculative decoding

**Requirements**:
- `huggingface_hub` package: `pip install huggingface_hub`
- ~380 GB free disk space on C:\
- Fast NVMe SSD **strongly recommended** (Colibri streams from disk)

**Download script**:
```powershell
cd local-models\colibri\python
& "$env:USERPROFILE\.venvs\all\Scripts\python.exe" download_colibri.py
```

This will download all model files to `C:\LLMs\models\colibri\` with resume support.

### 3. Configuration Files

- `python/start_colibri.py` — Server lifecycle management
- `python/verify_colibri.py` — Health check and authentication verification
- `config/glm-5.2-vibe.jinja` — Vibe-compatible chat template

### 4. External Files (Outside Repository)

- API Key: `C:\LLMs\config\colibri_api_key.txt` (auto-generated)
- PID File: `C:\LLMs\logs\colibri.pid`
- Log File: `C:\LLMs\logs\colibri.log`

## Admission Checklist

- [x] Select exact model artifact (GLM-5.2 744B MoE)
- [x] Record upstream source (JustVugg/colibri GitHub)
- [x] Loopback endpoint contract (OpenAI-compatible at :8082/v1)
- [x] Health check implemented (`verify_colibri.py`)
- [x] Context limit configured (131,072 tokens)
- [x] Registry entries set to `deferred` (POC evaluation complete)
- [ ] Add deterministic inference canaries with independent verifiers
- [ ] Re-evaluate speed/feasibility before promoting to `candidate`

## Usage

```powershell
# Start server
cd local-models\colibri\python
& "$env:USERPROFILE\.venvs\all\Scripts\python.exe" start_colibri.py --background

# Stop server
& "$env:USERPROFILE\.venvs\all\Scripts\python.exe" start_colibri.py --stop

# Verify health
& "$env:USERPROFILE\.venvs\all\Scripts\python.exe" verify_colibri.py

# Check inventory
cd ..\..\agent-orchestrator
& "$env:USERPROFILE\.venvs\all\Scripts\python.exe" orchestrate.py inventory
```

## Security

- API key is auto-generated and stored externally at `C:\LLMs\config\colibri_api_key.txt`
- Model weights remain outside the repository at `C:\LLMs\models\colibri\`
- Runtime logs and PID files are stored externally at `C:\LLMs\logs\`
- No credentials, weights, logs, or PID files belong in this directory

## Performance Notes

- Cold-start inference is slow due to SSD bandwidth limitations (reason for `deferred` status)
- Performance improves as frequently used experts remain in RAM
- Memory usage depends on active experts, not total model size
- Context length limited by available memory for KV-cache
