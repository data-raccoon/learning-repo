# AI-Learn Root Agent Instructions

## Repository boundaries

- `small-context-harness/` — default model registry, bounded task packets,
  Mistral Vibe execution, durable evidence, and independent gates.
- `.agents/skills/orchestrate-models/` — global instructions for using the
  default harness.

## Model delegation

- Handle tasks directly by default. Do not create sub-workers, jobs, or graphs
  unless the user explicitly asks for delegation, sub-agents, worker models, or
  parallel agent work.
- When the user explicitly requests delegation, use
  `small-context-harness/harness.py` through the repo-local
  `orchestrate-models` skill.
- Delegation is one level deep. Only the root agent creates task packets.
- Give every worker exactly one target directory, explicit `write_roots`, all
  required context, independent verifiers, and hard limits.
- Never widen a worker's read scope to compensate for an incomplete task packet.
- Select the model profile explicitly; automatic routing and model substitution
  are disabled. Use `mistral-medium-3.5` for task definition, planning,
  architecture, and review, and `devstral-small` for coding.
- Route both profiles through the same bounded read/write/`limited_bash` Vibe
  worker. There is no public `invoke` command.
- Treat planning as a write task: require Medium to save the proposal or task
  definition to an exact artifact path instead of returning it only in chat.
- Use the workflow `pack`, `route`, `accept`, `snapshot`, `execute`, then
  `gate --baseline`.
- Store acknowledgements, baselines, results, and full trajectories outside the
  target. Return only compact status, hashes, model attestation, changed-file
  counts, gate results, usage, cost, and artifact paths by default.
- Accept worker output only after the complete-diff baseline audit and
  independent verifiers pass. The default baseline detects changes but does not
  contain backup data or provide rollback.
- Allow worker commands only as exact task-declared argv vectors admitted by
  the global `limited_bash` policy; never provide a generic shell.

## Secrets and local runtimes

- Keep credentials, model weights, runtime logs, and PID files outside the repository.
- Do not stop a local runtime unless the orchestrator proves it started that exact process.
- OpenAI/ChatGPT is inventory-only until explicitly admitted.
- Ollama workers use the loopback API and exact registered model digests.
- Mistral workers use the globally registered Vibe profiles. The harness sets
  `VIBE_ACTIVE_MODEL` per execution and uses an isolated temporary `VIBE_HOME`.
- Gemini proposal workers use the official `agy` executable and its OS-keyring
  session. Do not place OAuth data in the repository or substitute API/Vertex
  credentials for the consumer-account profile.
- Antigravity may use its external project/worktree storage. Gemini file tools write only inside the job target. The admitted Gemini QA profile runs only the fixed commands listed in the job's `allowed_commands`; each run gets a temporary absolute-target policy and an independent verifier. Network, MCP, package installation, downloads, and non-workspace access are forbidden.

## Shell

Windows 11, PowerShell. Avoid `&&`, `||`, and `;` in commands.

## Verification

Python interpreter for all scripts: `& "$env:USERPROFILE\.venvs\all\Scripts\python.exe"`. Never use bare `python`.

```powershell
# small-context-harness/ — after changing the default harness or its skill
& "$env:USERPROFILE\.venvs\all\Scripts\python.exe" -m unittest discover -s small-context-harness\tests -v
& "$env:USERPROFILE\.venvs\all\Scripts\python.exe" small-context-harness\harness.py inventory

```
