# Project-local Vibe model option

This project contains a snapshot of the user-level Vibe configuration plus the
additional local model `local-ministral-3b-q4`. The project copy is scoped to this
workspace; the source file under `%USERPROFILE%\.vibe` was not modified. The old,
inactive `local` model on port 8080 was removed from this project copy. The active
project model is the authenticated Ministral server on port 8081. Copying the global
file over this project file again would remove these project-only changes.

## Credential boundary

The API key remains outside the repository at:

```text
C:\LLMs\config\api_key.txt
```

Vibe loads that value as `LOCAL_LLM_API_KEY` from `%USERPROFILE%\.vibe\.env`, which
is created by `python\configure_vibe_credentials.py`. Do not copy the key into
`config.toml`, VS Code settings, source files, or Git.

## Use in VS Code

1. Start the local server:

   ```powershell
   & "${env:USERPROFILE}\.venvs\all\Scripts\python.exe" C:\LLMs\python\start_mistral.py --background
   ```

2. Open this workspace normally in VS Code.
3. Open Mistral Vibe, start a new conversation, and select
   `local-ministral-3b-q4` in the model picker.
4. Begin with a small, read-only task. Local tool-calling quality is not yet
   qualified for autonomous edits or shell execution.

The server uses a project-maintained native Mistral chat template that permits
OpenAI/Vibe histories with consecutive user or assistant roles. Regenerate and test
it with `python\create_vibe_chat_template.py` and
`python\test_vibe_message_roles.py --large`.

## Cloud and local agent separation

The project default remains Vibe's `Default` agent with `mistral-medium-3.5`, the
standard `cli` prompt, and all configured tools, skills, and connectors. Use this
agent with either cloud model.

Select the project agent `Local Files` to use `local-ministral-3b-q4`. Only this
agent uses the token-minimal `local-files` prompt and exposes `read_file`, `grep`,
`edit`, and `write_file`; web access, shell execution, connectors, skills,
subagents, and task-management tools are disabled for it. Install its
project-maintained prompt into Vibe's prompt directory with:

```powershell
& "${env:USERPROFILE}\.venvs\all\Scripts\python.exe" .\python\install_vibe_prompt.py
```

After changing the prompt, agent, or tool list, run `/reload` in Vibe and start a
new conversation; existing sessions retain their original system prompt and
schemas. In VS Code choose `Default` for cloud/full capability or `Local Files`
for local/file-only capability in the agent selector.

Run the dependency-free project check with:

```powershell
& "${env:USERPROFILE}\.venvs\all\Scripts\python.exe" .\python\verify_vibe_config.py
```
