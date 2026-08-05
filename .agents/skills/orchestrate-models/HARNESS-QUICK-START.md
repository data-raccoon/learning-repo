# Harness v3 Quick Start

Use the initiative controller. The only public commands are `status`, `run`,
and `approve`; do not invoke lifecycle, worker, packet, or evidence commands
directly.

```powershell
& "$env:USERPROFILE\.venvs\all\Scripts\python.exe" model-execution-harness/core/harness.py status initiatives/mc-mod-core --repo .
& "$env:USERPROFILE\.venvs\all\Scripts\python.exe" model-execution-harness/core/harness.py run initiatives/mc-mod-core --repo .
& "$env:USERPROFILE\.venvs\all\Scripts\python.exe" model-execution-harness/core/harness.py approve initiatives/mc-mod-core --task reconcile-packages --repo .
```

Each initiative has one `orchestration.json` containing `v: 3`, an initiative
ID, and bounded task entries. `run` selects exactly one eligible task, derives
the worker and external evidence path, preflights, executes, gates, and writes
the task state. A passing task becomes `completed`; any failure becomes
`blocked`. A human corrects the task and uses `approve` to allow a retry.

No `NEXT-STEP.json`, manual evidence directory, worker ID, profile flag, or
shell probing is required.
