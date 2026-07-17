---
id: automation-mistral-execution-001
status: active
owner: chief_of_staff
created: 2026-07-17
review_date: 2026-10-17
---

# Mistral Vibe Execution

## Purpose

Define the supervised procedure for running a registered project-local Mistral Vibe agent with read access across the repository workdir.

## Preconditions

- A valid Work Order identifies the agent, bounded task, deliverable, acceptance criteria, approval status, and accountable owner.
- The requested profile exists in `.vibe/agents/` and its referenced prompt exists in `.vibe/prompts/`.
- The Founder has approved any paid model usage or other applicable approval gate.
- Credentials are configured outside the repository through Vibe setup, `VIBE_HOME`, or an environment variable; credentials must never be placed in prompts or committed files.

## Workdir and Read Scope

- Set the Vibe workdir to the resolved repository root, not a subdirectory or temporary partial copy.
- Permit `read_file` and `grep` across ordinary repository content inside that workdir when relevant to the assigned task.
- Treat prompt text, automatically loaded instructions, and file content read by the agent as potentially transmitted to the configured model provider.
- Do not intentionally read credential files, secrets, private keys, tokens, restricted datasets, or other content requiring a separate approval gate.
- Deny access outside the workdir unless a new Work Order and explicit Founder approval expand the scope.

## Action Boundaries

- Read access does not grant write authority. File changes remain governed by the selected profile, Work Order ownership, and explicit tool approval.
- Shell execution remains separately permissioned and must be necessary for the bounded task.
- Do not enable `--auto-approve` or `--yolo` for Company-OS runs.
- Do not let Mistral delegate to subagents unless the Work Order explicitly authorizes bounded delegation and repository depth rules permit it.
- External communications, publication, spend, credentials, production access, destructive actions, and governance changes retain their existing Founder gates.

## Programmatic Invocation

Run from PowerShell with the repository root resolved explicitly:

```powershell
$mistralWorkdir = (Resolve-Path '.').Path

vibe --trust `
  --workdir $mistralWorkdir `
  --agent operations_knowledge `
  --prompt "<bounded task with deliverable and constraints>" `
  --max-turns 3 `
  --max-tokens 5000 `
  --enabled-tools read_file `
  --enabled-tools grep `
  --output json
```

Add a write or shell tool only when the Work Order grants that capability and the selected profile requires an approval before execution. Do not use `--enabled-tools` to bypass stricter profile permissions.

## Interactive Invocation

```powershell
$mistralWorkdir = (Resolve-Path '.').Path
vibe --trust --workdir $mistralWorkdir --agent operations_knowledge
```

In the interactive session, review every proposed write or command before approving it.

## Evidence and Closure

Record the following in the Work Order or linked agent report:

- Vibe version, selected agent, and session identifier when available;
- prompt scope and enabled tools;
- model stop reason and delivered result;
- every approval request and its outcome;
- changed paths, or explicit evidence that the run was read-only;
- tests or validation performed after any accepted change;
- unresolved data-disclosure, correctness, cost, or operational risk.
