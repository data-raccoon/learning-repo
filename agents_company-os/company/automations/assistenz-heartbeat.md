---
id: automation-assistenz-heartbeat-001
status: ready
owner: assistenz
created: 2026-07-17
review_date: 2026-07-31
---

# Assistenz Heartbeat

## Purpose

Run a quiet, read-only triage loop every fifteen minutes. Report only newly actionable, changed, or resolved Company-OS work. Never start implementation or cross an approval gate.

## Local Check

Run from the repository root:

```powershell
& "${env:USERPROFILE}\.venvs\all\Scripts\python.exe" scripts\check_assistenz_heartbeat.py
```

The scanner checks active or overdue Work Orders and open risk-register entries. It stores committed and pending deduplication checkpoints below `.runtime/assistenz-heartbeat/`, which is excluded from Git. An unchanged run produces no output.

Reports use an acknowledgement protocol so a delivery failure cannot silently discard a finding. A run with changes writes `pending.json` but does not advance `state.json`. At the start of the next run, acknowledge the pending report only if the prior heartbeat message is visibly present in this chat:

```powershell
& "${env:USERPROFILE}\.venvs\all\Scripts\python.exe" scripts\check_assistenz_heartbeat.py --ack
```

Use `--dry-run --json` for inspection without changing the checkpoint.

## Scheduled Task Configuration

- Destination: this continuing Founder chat.
- Project: the local `multi-agent` repository.
- Cadence: every 15 minutes.
- Mode: local project, not a new worktree on each run.
- Permissions: existing sandbox defaults; no added network or external-app access.
- Stop condition: pause after three consecutive execution errors, an unavailable project, or a request for new authority.

## Durable Prompt

```text
Every 15 minutes, check whether the Founder Office has genuinely new or changed work requiring attention.

Delegate repository triage to the `assistenz` agent. Do not use repository write tools. The only permitted write is the scanner's checkpoint below `.runtime/assistenz-heartbeat/`.

At the start of a run, inspect this chat. If the immediately preceding heartbeat report is visibly present and complete, acknowledge it by running:

& "${env:USERPROFILE}\.venvs\all\Scripts\python.exe" scripts\check_assistenz_heartbeat.py --ack

Do not acknowledge a missing, failed, or incomplete report. Then run this command from the current project root:

& "${env:USERPROFILE}\.venvs\all\Scripts\python.exe" scripts\check_assistenz_heartbeat.py

Also inspect new Founder instructions in this chat and determine whether a previously blocked dependency is now satisfied.

If the command is silent and there is no new chat instruction or unblocked dependency, produce no report and make no repository change.

If something material changed, report only:
- what is new, changed, or resolved;
- urgency;
- accountable owner;
- required decision or next step;
- applicable approval gate.

If specialist work is needed, add a `DELEGATION_REQUEST` containing:
- requested existing agent role;
- bounded task and reason;
- read-only or writable scope;
- expected deliverable and acceptance criteria;
- urgency and dependencies;
- applicable approval gate;
- why separate execution is useful.

Do not start the requested agent. The Chief of Staff may review and route the request; only the root orchestration turn may actually start an agent after verifying the Work Order, ownership boundaries, capacity, and approval authority. If no registered agent fits, report a capability gap; creating a new agent definition requires separate Founder direction.

Do not implement discovered work, edit canonical artifacts, send communications, access restricted data, incur spend, deploy, change credentials, modify production data, or treat a recommendation as approved. A new task must be routed through a scoped Work Order with one accountable owner. Request Founder direction whenever new authority is required.

If the scanner fails three consecutive times, pause this heartbeat and report the exact error and last successful run.
```

## Manual Acceptance Test

1. Remove only the ignored local checkpoint if a clean first-run simulation is required.
2. Run the scanner once and review all baseline findings.
3. Run with `--ack`, then run the scanner again without repository changes; expect no output.
4. Change a fixture or use the unit tests to verify new, changed, and resolved output.
5. Test the durable prompt manually in this chat.
6. Activate the fifteen-minute schedule in ChatGPT Scheduled Tasks and review its first three runs.

## Approval Boundary

The heartbeat is an attention mechanism, not an execution authority. Existing Work Orders, decision rights, and Founder approval gates remain controlling.

## Product Reference

- [OpenAI Scheduled Tasks documentation](https://developers.openai.com/codex/app/automations)
