# AI-Learn Root Agent Instructions

## Repository boundaries

- `agent-packs/` — canonical model- and IDE-neutral agent definitions, skills,
  workflows, resources, and manifests.
- `model-execution-harness/core/` — default model registry, bounded task
  packets, Mistral Vibe execution, durable evidence, and independent gates.
- `model-execution-harness/graph-runtime/` — advanced graphs, managed runtimes,
  transactional materialization, rollback, and quarantine.
- `.agents/skills/orchestrate-models/` — global instructions for using the
  default harness.

## Vocabulary

- A model is an inference engine such as Medium or Devstral.
- An agent definition is inert role and authority text stored in an agent pack.
- A skill is a reusable procedure stored in an agent pack or exposed through an
  IDE adapter.
- A worker is one bounded model execution created from a model, pack entry
  point, task, tools, and limits.
- An agent pack never selects a model or IDE. Keep those bindings in the
  execution harness or an explicitly declared adapter.

## Dot directories

- Keep root `.agents/`, `.codex/`, `.continue/`, and `.vscode/` as thin
  discovery adapters only. Each adapter must point to its canonical repository
  source in a comment or its loaded instructions.
- Do not create a repository-local `.vibe/`; Vibe model admission is user-global
  and execution isolation belongs to the model execution harness.
- Put package-specific IDE integrations in an explicit `adapters/` directory,
  never in package-local dot folders.
- Keep generated runtime state outside the repository. Dot-prefixed lifecycle
  and historical evidence directories are data and must not be deleted merely
  because of their names.

## Model delegation

- Handle tasks directly by default. Do not create sub-workers, jobs, or graphs
  unless the user explicitly asks for delegation, sub-agents, worker models, or
  parallel agent work.
- When the user explicitly requests delegation, use
  `model-execution-harness/core/harness.py` through the repo-local
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
- Use v2 tasks only. Run `preflight`, then the fail-fast `run` command, which
  performs `pack`, `route`, `accept`, `snapshot`, `execute`, and baseline gate
  internally. Regenerate old tasks instead of adapting v1 evidence.
- Coding and repair tasks require exact-file `write_roots`, admitted worker-loop
  tests, independent verifiers, and generous session/turn budgets.
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
# model-execution-harness/core/ — after changing the default harness or its skill
& "$env:USERPROFILE\.venvs\all\Scripts\python.exe" -m unittest discover -s model-execution-harness\core\tests -v
& "$env:USERPROFILE\.venvs\all\Scripts\python.exe" model-execution-harness\core\harness.py inventory

```
