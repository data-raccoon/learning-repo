# Vibe Harness Orchestrator Adapter

This is an explicit Vibe adapter for the repository-default execution harness.
It makes an interactive Vibe session a controller of bounded v2 tasks; it does
not let Vibe start Medium or Devstral directly. Only `harness.py run` dispatches
a registered worker profile.

The controller rules are canonical in
[`../../ORCHESTRATOR-CONTRACT.md`](../../ORCHESTRATOR-CONTRACT.md). This adapter
only maps them to Vibe's agent, prompt, and Windows command-tool conventions.

## Installation

Keep this adapter canonical in the repository. For the Mistral Vibe VS Code
extension, copy or symlink both files into the user-level Vibe directories:

| Canonical source | User-level Vibe destination |
| --- | --- |
| `agents/harness_orchestrator.toml` | `%USERPROFILE%\.vibe\agents\harness_orchestrator.toml` |
| `prompts/harness_orchestrator.md` | `%USERPROFILE%\.vibe\prompts\harness_orchestrator.md` |

The extension discovers custom agents from the user-level `agents` directory
and resolves their custom system prompts from the user-level `prompts`
directory. Restart the extension, select **Harness Orchestrator** from the
agent selector, and start a new session at the repository root.

The custom prompt is the persistent bootstrap. It directs the agent to read the
canonical orchestration contract, repository `AGENTS.md`, target `AGENTS.md`,
and the orchestration skill before it creates or runs work. Do not rely on a
first chat message to establish these rules.

An `agent_paths` entry in `%USERPROFILE%\.vibe\config.toml` may be used by
other Vibe surfaces, but is not the primary VS Code extension installation
method.

Do not create a repository-local `.vibe` directory and do not copy credentials
or model configuration into this adapter.

Start Vibe from the repository root with the `harness_orchestrator` agent. The
agent uses Vibe's command tool only after approval to run a single PowerShell
command. When Vibe exposes `bash` instead of `powershell` on Windows, the agent
uses `bash` solely to invoke `powershell.exe -NoProfile -Command ...`; it must
not issue Unix commands. It may invoke the registered Python interpreter and
`harness.py`; it must not invoke a model CLI, use shell chaining, or call
`harness.py execute`.

## Controller lifecycle

1. Read the root and target `AGENTS.md`, the orchestration skill, and the
   relevant target artifacts.
2. Write a v2 plan or task artifact with one target, selected profile, exact
   write roots, ordered context, allowed worker-loop argv vectors, and
   independent verifiers.
3. Run `preflight`, then `run` for one accepted task.
4. Read the compact result and gate evidence. Materialize a dependent task only
   after its prerequisite has passed.

The full worker trajectory remains outside the target and is consulted only for
narrow failure diagnosis.
