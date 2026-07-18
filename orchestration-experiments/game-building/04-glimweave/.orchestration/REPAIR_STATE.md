# Glimweave Repair State

## Objective

Make first-run public gameplay independently verifiable without weakening the external
browser gate. Preserve the offline, dependency-free, multi-file game architecture.

## Current external evidence

- Command: `& "$env:USERPROFILE\.venvs\all\Scripts\python.exe" tools\verify_glimweave.py --json`
- Latest unrestricted pre-episode result:
  `FAIL:RESERVOIR_AFTER_DRIFTCATCHER_55_ACTION_MESSAGE_TUTORIAL_STEP_0,ANNOUNCER_REJECTED_ACTION,CANVAS_PIXEL_CHANGED`.
- A sandboxed run produced `BROWSER_NO_RESULT` because Edge's GPU/cache process crashed.
  The unrestricted run proved that was a harness failure and restored the actual game gates.
- Evidence is written under `.orchestration/runtime/verification-latest/`.
- Strong-model final result: `PASS` on the same unrestricted verifier command.

## Known history

- The stale-closure explanation for the second purchase was attempted and disproven.
- Previous permission, Windows path, empty terminal JSON, and multimodal continuation
  failures were harness defects, not evidence of model incapability.
- The working tree contains existing game repairs. Inspect current files; do not restore or
  overwrite them wholesale.

## Episode policy

- Mistral owns code-level hypotheses and repairs; the verifier may not be edited.
- Maximum three diagnosis-edit-verify cycles.
- Stop after two distinct hypotheses fail to improve the verifier trajectory.
- Record each hypothesis, evidence, result, and changed files below.

## Repair log

- Harness attempt 1 stopped at 312,540 cumulative tokens without editing or recording a
  game hypothesis. Its trajectory contained repeated broad reads, including a 59 KB tool
  result. This is a context-policy failure, not a failed repair hypothesis. The agent now
  compacts at 60k tokens, limits reads to 16 KB, and requires grep plus bounded line ranges.
- No game hypothesis has been attempted in the re-architected episode yet.
- Harness attempt 2 used the corrected Git-Bash command, grep-first retrieval, 16 KB read
  ceiling, and 60k compaction threshold. It stopped at 608,981 cumulative tokens after 18
  greps, 15 bounded reads, and 3 Bash calls. It made no edit, recorded no causal hypothesis,
  and never completed a verifier comparison.
- Escalation threshold reached: two bounded episodes produced no repair trajectory after the
  harness was qualified. Do not add another more prescriptive Mistral micro-prompt. Hand the
  evidence packet to a stronger diagnosis owner.
- Strong-model hypothesis 1 confirmed: the saved DOM exposed duplicate Weftling IDs
  (`fdfdfdfd-fdfd-4dfd-bdfd-fdfdfdfdfdfd`). The RNG used an unsafe 64-bit multiplier with
  JavaScript `Number`, collapsing successive UUID bytes. Replacing it with the specified
  32-bit Mulberry32 algorithm resolved the purchase and rejection-feedback gates.
- The rejection path also announced errors only through a transient notification. It now
  writes `Action rejected: ...` to the dedicated live announcer as well.
- Strong-model hypothesis 2 confirmed: animation frames can be deferred in background or
  automated contexts, leaving the canvas transparent. UI initialization and public state
  changes now paint synchronously, and duplicate renderer initialization was removed.
- Final unrestricted result: `PASS`. The full screenshot shows the Sky Loom field, two
  distinct Weftlings, motes, and Reservoir rather than a blank canvas.
