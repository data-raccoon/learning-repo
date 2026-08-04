# Portable agent packs

This directory is the canonical, model-agnostic and IDE-agnostic store for
reusable agent definitions, skills, workflows, contracts, and resources.

An agent pack contains inert definitions. It does not contain a running model.
An execution harness creates a worker by combining a selected model with one
pack entry point, a bounded task, tools, and limits.

Every direct child pack must contain `agent-pack.json` conforming to
`agent-pack.schema.json`. Packs may be one of three kinds:

- `role-pack` — reusable specialist definitions and skills;
- `workflow-pack` — definitions coordinated by a reusable workflow;
- `operating-system` — roles, skills, governance, and durable domain state.

Canonical components use repository-relative paths and declare capabilities,
not model names. Optional IDE or model integrations belong under an adapter
path and are never the source of truth for the portable pack.

Validate all packs from the workspace root:

```powershell
& "$env:USERPROFILE\.venvs\all\Scripts\python.exe" agent-packs\validate.py
```
