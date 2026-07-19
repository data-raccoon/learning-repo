# Kolibri

Local Kolibri inference engine for running large MoE models (GLM-5.2 744B parameters) on consumer hardware with disk-streaming.

## Architecture

Kolibri is a pure C, zero-dependency inference engine that exploits MoE sparsity to run massive models with limited RAM. It streams only active experts from disk, using Multi-head Latent Attention (MLA) with compressed KV-cache.

**Key Characteristics:**
- Pure C implementation (~1,300-2,400 lines)
- Zero external dependencies (no BLAS, no CUDA, no Python at runtime)
- Disk streaming of MoE experts
- Supports GLM-5.2 (744B parameters) on 25GB+ RAM
- Portable across Linux, Windows, macOS

## Registry Status

The Kolibri provider, model, harness, and profile are registered in `agent-orchestrator/config/` with `candidate` status:

- **Provider**: `local-kolibri` - OpenAI-compatible local server at `http://127.0.0.1:8082/v1`
- **Model**: `glm-5.2-744b-moe-local` - GLM-5.2 with 131K context tokens
- **Harness**: `kolibri-openai-chat` - OpenAI-compatible chat API
- **Profile**: `kolibri-glm-5.2-inference` - Inference-capable with high success probability

## Setup

### 1. Install Kolibri Engine

Build from source or install via package manager:
```powershell
# Option 1: Build from source
git clone https://github.com/JustVugg/colibri.git
cd colibri
make

# Option 2: Winget (when available)
winget install colibri
```

The executable should be named `kolibri-server` or `kolibri-server.exe`.

### 2. Download Model

**IMPORTANT**: Kolibri uses its **own custom container format**, NOT GGUF.

Download GLM-5.2 in Kolibri format to:
```
C:\LLMs\models\kolibri\  (directory containing multiple .safetensors files)
```

**Recommended source**: [jlnsrk/GLM-5.2-colibri-int4](https://huggingface.co/jlnsrk/GLM-5.2-colibri-int4)
- This is a pre-converted GLM-5.2 (744B MoE) in int4 quantization
- **Size: ~370-380 GB** (not 90-100 GB - the model is split across many .safetensors files)
- Format: Kolibri's native container format with:
  - Multiple `out-*.safetensors` shards (2.69 GB each)
  - `config.json`, `generation_config.json`
  - `tokenizer.json`, `tokenizer_config.json`
  - MTP (Multi-Token Prediction) head for speculative decoding

**Requirements**:
- `huggingface_hub` package: `pip install huggingface_hub`
- ~380 GB free disk space on C:\
- Fast NVMe SSD **strongly recommended** (Kolibri streams from disk)

**Download script**: Run the provided Python script:
```powershell
cd local-models\kolibri\python
python download_kolibri.py
```

This will download all model files to `C:\LLMs\models\kolibri\` with resume support.

### 3. Configuration Files

- `python/start_kolibri.py` - Server lifecycle management
- `python/verify_kolibri.py` - Health check and authentication verification
- `config/glm-5.2-vibe.jinja` - Vibe-compatible chat template

### 4. External Files (Outside Repository)

- API Key: `C:\LLMs\config\kolibri_api_key.txt` (auto-generated)
- PID File: `C:\LLMs\logs\kolibri.pid`
- Log File: `C:\LLMs\logs\kolibri.log`

## Admission Checklist

- [x] Select exact model artifact (GLM-5.2 744B MoE)
- [x] Record upstream source (JustVugg/colibri GitHub)
- [x] Runtime verified (kolibri-server)
- [x] Loopback endpoint contract (OpenAI-compatible at :8082/v1)
- [x] Health check implemented (verify_kolibri.py)
- [x] Context limit configured (131,072 tokens)
- [x] GPU-slot policy defined (CPU and GPU capable)
- [x] Registry entries updated to `candidate` status
- [ ] Add deterministic inference canaries with independent verifiers
- [ ] Promote profile to `eligible` after evaluation evidence passes

## Usage

### Start Server
```powershell
cd local-models\kolibri\python
python start_kolibri.py --background
```

### Stop Server
```powershell
python start_kolibri.py --stop
```

### Verify Health
```powershell
python verify_kolibri.py
```

### Check Inventory
```powershell
python agent-orchestrator\orchestrate.py inventory
```

### Test Routing
```powershell
python agent-orchestrator\orchestrate.py route examples\route-kolibri.json
```

## Security

- API key is auto-generated and stored externally at `C:\LLMs\config\kolibri_api_key.txt`
- Model weights remain outside the repository at `C:\LLMs\models\kolibri\`
- Runtime logs and PID files are stored externally at `C:\LLMs\logs\`
- No credentials, weights, logs, or PID files belong in this directory

## Performance Notes

- Cold start inference may be slow due to SSD bandwidth limitations
- Performance improves as frequently used experts remain in RAM
- Memory usage depends on active experts, not total model size
- Context length limited by available memory for KV-cache
