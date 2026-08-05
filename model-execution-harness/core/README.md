# Model Execution Harness v3

V3 is an initiative controller, not a lifecycle CLI. Its public commands are:

```powershell
& "$env:USERPROFILE\.venvs\all\Scripts\python.exe" harness.py status initiatives/mc-mod-core --repo ..
& "$env:USERPROFILE\.venvs\all\Scripts\python.exe" harness.py run initiatives/mc-mod-core --repo ..
& "$env:USERPROFILE\.venvs\all\Scripts\python.exe" harness.py approve initiatives/mc-mod-core --task task-id --repo ..
```

Each initiative owns one `orchestration.json` with `v: 3`, an ID, and bounded
task entries. A task entry has an ID, state, optional blocker, and the bounded
task definition. Task targets must equal the initiative directory.

`run` selects exactly one dependency-eligible `ready` task and performs the
complete validation, model execution, external evidence persistence, and
independent gate. It derives worker identity and evidence location itself. A
passing run becomes `completed`; a failed run becomes `blocked`. A human uses
`approve` only after correcting a blocked task to allow another attempt.

Evidence is stored under `.orchestration/evidence/<initiative>/<task>/<run-id>`.
It is not an input to routine operation. No `NEXT-STEP.json`, packet command,
manual evidence path, worker flag, profile flag, or shell probing is public.

The runtime continues to enforce selected registered profiles, one target,
exact write roots, admitted command vectors, durable trajectories, complete-diff
audits, and independent verifiers.

## Verification

```powershell
& "$env:USERPROFILE\.venvs\all\Scripts\python.exe" -m unittest discover -s tests -v
```
