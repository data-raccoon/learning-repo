# Local Models

One directory per locally hosted model family. Runtime code, model-specific templates, and endpoint checks belong here; generated products and organization workflows do not.

- `ministral/`: current local Ministral runtime (llama.cpp) and project-local Vibe provider setup.
- `soofi/`: deferred local-model family scaffold; exact model and runtime are not selected.
- `colibri/`: Colibri inference engine with GLM-5.2 (744B MoE) support; POC complete, registered as `deferred` — too slow for current use.
