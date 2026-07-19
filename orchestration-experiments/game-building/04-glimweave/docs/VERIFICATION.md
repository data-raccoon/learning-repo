# Verification Evidence

> **Superseded experiment evidence (2026-07-18).** This page describes the legacy
> pre–Living Loom runtime. Do **not** run `tools/assemble_runtime.py`; it targets the
> old layout and can overwrite the checked-in upgraded runtime. Current verification
> is defined by `docs/acceptance-contract.md` and runs
> `python tools/verify_glimweave.py --json` directly against checked-in files.

Final deterministic assembly and headless Edge run:

```text
PASS phases=4 weftlings=5 doctrines=3 upgrades=18
PASS browser_suite=core+integration
```

The browser suite covers module boot, initial-state validation, data cardinalities,
fractional production and real mote fade, capture/production separation, overflow,
unit and upgrade purchase, doctrine locking and ID normalization, all four phases,
Retuning, Reservoir Blueprint purchase/capacity persistence, victory, offline progress,
save/load reconstruction, DOM rendering, canvas initialization, ARIA live status, and
stylesheet loading.

Command:

```powershell
python 04-glimweave\tools\assemble_runtime.py
python 04-glimweave\tools\verify_glimweave.py
```

This is automated evidence, not a claim of a completed long-form human balance
playthrough.
