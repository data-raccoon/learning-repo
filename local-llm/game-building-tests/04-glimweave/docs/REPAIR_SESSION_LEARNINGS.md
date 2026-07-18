# Glimweave Repair-Session Learnings

## Status and Scope

This document records the full-image QA and attempted repair session that followed the
initial Mistral Cloud generation. It is cloud/Vibe-specific and does not supersede the
separate lessons for the local model.

The initial project was structurally ambitious, but it was not a complete working game.
At the end of this session, substantial fixes had landed, but the strengthened clean-profile
suite still reported a failed second public purchase and unchanged canvas pixels. The game
must not yet be described as working.

## The Original Green Build Was Not a Playability Test

The first clean 1440x900 browser capture showed a dashboard of controls with greyed-out
buttons and no recognizable game field. Source tracing confirmed four independent P0s:

- `UI.onAction` existed but production boot never installed a handler;
- fresh state began at zero Glim with no producer while the first producer cost 60;
- the full-width UI occupied the canvas area and reserved no central field;
- renderer initialization used the canvas's default backing attributes instead of its CSS
  display geometry.

The old smoke suite passed because it checked that DOM nodes existed and canvas width was
nonzero. Its progression scenarios directly funded isolated state. Neither proved that a
clean-profile player could see a playfield, click a public control, or reach the first
production/capture loop. Generated tests are especially dangerous when the same model owns
both implementation and the definition of success.

## Full Images Must Use the Native Multimodal Channel

Vibe's `read_file` tool is text-oriented. It rejected a 226 KB PNG on size and could not
render even a reduced JPEG as pixels. Base64 returned as text also exceeded tool-output
limits and still did not become vision input.

The installed Vibe runtime already supported `ImageAttachment` and
`AgentLoop.act(images=...)`. A project-local adapter successfully sent the original
1440x900 PNG directly from disk to Mistral without routing image bytes or model output
through the outer orchestrator. A small probe independently identified the dominant side
panels and missing reserved playfield.

The adapter exposed an important limitation: its multimodal loop completed image-only
analysis but stopped after a callable tool returned instead of scheduling the next model
turn. For this Vibe version, the reliable division is:

1. native multimodal, read-only visual audit;
2. persisted Markdown findings;
3. standard Vibe CLI tool loop for edits, without resending the image.

Trying to combine image attachment and multi-turn file editing before fixing that loop led
to empty assistant responses and no edits.

## Harness Defects Can Masquerade as Model Failure

Several expensive failures were caused by the orchestration harness rather than Mistral's
capability:

- The standard repair command omitted `--auto-approve`. Mistral proposed the correct edit,
  received `Tool execution not permitted`, and spent later turns attempting Bash
  workarounds.
- The initial request used POSIX `/c/...` paths on Windows. Vibe's `read_file` interpreted
  these as `C:\c\...`. Native Windows paths or exact workspace-relative paths are required.
- Vibe's terminal JSON formatter emitted no trajectory when a token or turn limit stopped
  a run. Streaming JSON preserved each assistant and tool message and made the actual loop
  diagnosable.
- The custom Vibe runtime required `init_harness_files_manager("user", "project")` before
  `VibeConfig.load()`. Omitting it made the multimodal adapter fail before inference.

Run a small capability probe for every required combination—read, edit, Bash, image, and
multi-turn continuation—before assigning a large repair. A model should not be judged on a
tool path that has not itself passed acceptance.

## Cumulative Token Limits Are Not Context-Window Limits

Vibe's `--max-tokens` limits cumulative prompt plus completion usage across the session.
Every tool turn resends prior file contents. Reading several 20–50 KB files can therefore
consume hundreds of thousands of tokens even when the model's instantaneous context is
valid. Raising a job from 180k to 600k did not make a broad repair efficient; it merely
allowed more repeated context before stopping.

Do not embed source files in the task packet and then ask the model to read them again.
Record their hashes for provenance, pass a compact task packet, and let the worker read
only the files or line ranges it needs. Large budgets are appropriate only after the tool
trajectory shows useful implementation progress.

## Failed Runs May Still Change the Repository

Vibe can reach a token or turn limit after successful edit or Bash calls but before its
final report. Conversely, a runner can print `PASS job=...` merely because it captured an
assistant artifact; that does not mean the game passes acceptance.

After every worker run, regardless of exit status:

- inspect the working-tree diff;
- validate changed-file size and syntax;
- run external acceptance independently;
- preserve the streaming trajectory when the run stops;
- never equate the worker's prose report with verification.

One stopped CSS run deleted roughly 435 lines before its replacement was complete. The
next recovery run restored the committed 705-line stylesheet before attempting a safer
append-only override. Repair jobs need a transaction boundary: checkpoint, edit, verify,
and automatically restore only the worker's scoped files when structural guards fail.

## Duplicated Runtime Data Defeats Correct-Looking Repairs

The opening-economy repair changed `data/game-data.json`, but the browser actually loaded
the generated `data/game-data.js`. Fresh state then started with 135 Glim against the old
runtime capacity of 100 and failed validation at boot.

There should be one authoritative data source and one deterministic generation step. The
verifier must assert that source JSON and runtime JavaScript values agree. Asking a model
to remember to edit both copies is not a reliable architecture.

## External Verification Must Exercise Public Interfaces

The strengthened browser suite eventually checked real geometry and public interactions:

- explicit 1440x900 viewport;
- a central gap between bounded control rails overlapping the canvas;
- initial visible Reservoir value;
- exact purchase buttons selected through accessible labels;
- visible Reservoir changes after clicks;
- re-querying controls after UI rebuilds;
- a position-sensitive canvas pixel hash before and after actions.

These checks exposed stale assumptions in generated helpers: Retuning still expected zero
starting Glim, offline progress compared an object to a number, and a duplicate
`smoke-scenarios.js` definition overrode a corrected UI helper. Test definitions need one
owner just as production data needs one owner.

## Narrow Scope Helped, Then Became Micromanagement

Once broad repair passes repeatedly exhausted cumulative budgets before editing, tasks were
split by file and exact responsibility. This successfully landed action wiring, opening
economy changes, DPR-aware renderer sizing, responsive layout overrides, runtime-data
synchronization, and stronger smoke gates.

However, the outer orchestrator then began prescribing individual selectors, expected
values, closure changes, and checksum algorithms. At that point it was micromanaging
Mistral rather than orchestrating it. This consumed outer-model reasoning tokens, biased
diagnosis toward the orchestrator's hypotheses, and produced a long chain of small cloud
runs. One prescribed stale-closure diagnosis was disproved when the failure persisted.

The correct middle ground is not a vague “fix everything” prompt and not a sequence of
line-level patches. It is a persistent worker loop with:

- a compact release objective;
- ownership of a coherent subsystem;
- a trusted edit path proven before the job;
- one external verifier command returning compact, high-signal failure codes;
- access to saved screenshots and runtime evidence through appropriate channels;
- authority to diagnose, edit, and rerun until the gate passes or a bounded failure policy
  triggers;
- periodic checkpoints and diff guards controlled by the outer orchestrator.

The orchestrator should define evidence, permissions, ownership, budgets, and terminal
conditions. The worker should own code-level hypotheses and implementation.

## Recommended Architecture for the Next Repair

1. **Prove the worker environment first.** Test Windows path reads, normal edits, Bash,
   streaming output, image-only vision, and multi-turn continuation.
2. **Separate visual perception from code repair when necessary.** Persist visual findings
   once; do not resend the image on every edit turn.
3. **Use a persistent repair agent profile.** Remove the default requirement to reread
   entire large files for localized tasks, keep auto-approval scoped to the experiment,
   and retain conversation state across verifier iterations.
4. **Provide one browser-verifier tool.** It should launch a clean profile at declared
   desktop/mobile sizes and return compact DOM geometry, console errors, public journey
   state, pixel hashes, and screenshot paths.
5. **Give subsystem ownership, not line edits.** For example: “own first-15-minute public
   playability across UI/integration/simulation until `verify_glimweave.py` passes.”
6. **Enforce transactional guards.** Reject truncation, duplicate data drift, syntax
   failure, out-of-scope edits, and missing final evidence before accepting a worker turn.
7. **Keep acceptance external.** The worker may add tests, but only the outer clean-profile
   verifier decides completion.
8. **Stop when the process degrades.** Repeated line-level prompts are a signal to repair
   the harness or redefine module boundaries, not to continue micromanaging.

## Research-Informed Repair and Escalation Policy

Current agent-harness guidance reinforces the session evidence. Long-running work benefits
from a persistent worker, a small high-signal context, structured cross-session notes, and
an evaluator independent of the implementation worker. Browser application work needs an
active evaluator that navigates the product and records screenshots and runtime state;
source inspection and generated unit tests are insufficient.

The Glimweave implementation now follows that shape:

- a dedicated `glimweave-repair` Vibe agent owns diagnosis and implementation;
- `.orchestration/REPAIR_STATE.md` carries current evidence and disproven hypotheses;
- `verify_glimweave.py --json` returns compact status while retaining DOM, stderr, and a
  screenshot for just-in-time inspection;
- one repair episode permits autonomous diagnose-edit-verify cycles instead of a chain of
  outer-authored micro-prompts;
- the external verifier remains outside the worker's editable scope;
- a bounded handoff policy distinguishes lack of model progress from harness failure.

Escalation must be based on the observed repair trajectory, not the task description. Tool
denials, invalid paths, missing output, and broken continuation are harness failures and
must be fixed before judging the model. Mistral should continue when it reduces failures,
turns a generic failure into specific evidence, or lands a patch that survives independent
verification. A stronger model should take ownership when, in a proven harness, two distinct
evidence-based repairs leave the same failure unchanged; the worker repeats a disproven
hypothesis; it weakens acceptance; it damages structure twice; or it cannot preserve the
project's cross-file invariants through compaction.

The takeover packet must contain the current diff, exact verifier command and output,
screenshot and DOM paths, architecture constraints, and tried or disproven hypotheses. The
stronger model should own the next diagnosis rather than receive another proposed patch.

The first run of the new persistent agent exposed one further harness limit before making
any game edit: it consumed 312,540 cumulative tokens through repeated broad reads, including
a 59 KB file result. This is not a failed causal repair. The corrected profile compacts at
60k tokens, caps each read at 16 KB, requires grep-first bounded slices, and uses the native
Git-Bash verifier command. A persistent session without an early compaction and retrieval
policy can be just as wasteful as repeated one-shot jobs.

The retry proved the stopping policy is necessary. With those corrections active, Mistral
used 608,981 cumulative tokens across 18 greps, 15 bounded reads, and three verifier/shell
calls, but still made no edit, recorded no hypothesis, and completed no before/after
comparison. This is now sufficient trajectory evidence for a stronger diagnosis owner.
Further narrowing by the outer model would recreate the micromanagement failure the harness
was designed to avoid. The exact takeover packet is `.orchestration/REPAIR_HANDOFF.md`.

The stronger-model takeover validated the routing decision and added a useful evidence
lesson. The compact failure string reported the three observable symptoms, but the retained
DOM contained the decisive production exception: both purchases generated the same UUID.
The broken RNG used a 64-bit multiplier outside JavaScript's exact integer range despite the
architecture specifying Mulberry32. Correcting that one source-of-truth defect removed the
purchase and feedback symptoms. A second scoped correction made the first and post-action
canvas paints independent of deferred animation frames and removed duplicate renderer
initialization. The verifier progressed from three failures, to one, to exact `PASS`.

Compact evaluator output should therefore include the primary user-visible gates while also
retaining richer evidence artifacts for escalation. A stronger model should begin with those
artifacts rather than rereading the whole repository. This outcome does not prove Mistral
could never find the defect; it shows that, under the measured harness and budget, temporal
routing to a stronger diagnosis owner was more efficient than further narrowing its prompt.

## What Established the Takeover Point

The decision was not based on the game being difficult or on Mistral failing once. The first
persistent episode revealed that the agent could consume an entire budget through broad
reads, so the harness was corrected before judging the model. The retry then used a proven
browser command, qualified edit permissions, a 16 KB read ceiling, grep-first retrieval, a
60k compaction threshold, a durable repair ledger, and an external stopping policy.

Under those corrected conditions, the retry still used 608,981 cumulative tokens across 18
greps, 15 bounded reads, and three shell calls without recording a hypothesis, making an
edit, or completing a verifier comparison. The decisive signal was not token volume alone;
it was the absence of a transition from exploration to an experiment.

The takeover rule learned here is:

- harness failures do not count against the worker model;
- narrowing evidence and correcting retrieval deserve one measured retry;
- useful specificity, a tested hypothesis, a smaller failure set, or an independently valid
  patch are reasons to continue;
- repeated exploration with no experiment in a qualified harness is a plateau;
- if the outer model must provide the hypothesis or line-level patch, diagnosis has already
  been taken over and should be acknowledged as such;
- escalation describes the best next owner for this state and budget, not an absolute claim
  that the previous model can never solve the class of problem.

The takeover itself stayed clean because the prompt supplied the evidence, constraints,
disproven stale-closure hypothesis, and verifier command but no proposed repair. The stronger
model could therefore produce an independent diagnosis rather than confirm an anchored one.

## What the Successful Repairs Teach About Orchestration

### Compact results need rich evidence behind them

The three failure codes were useful for routing but insufficient for diagnosis. The retained
DOM contained the decisive message: state validation rejected a duplicate UUID. Future
browser verifiers should return compact gates while persisting DOM, screenshot, console and
notification text, relevant state deltas, and the first production exception. The exception
should also be promoted into the compact JSON when possible.

### Group failures by causal dependency before assigning work

The second purchase, rejection feedback, and unchanged canvas looked like three repair tasks.
Two were downstream of one broken RNG: duplicate UUIDs rejected the purchase, so the second
unit could not appear on the canvas. Splitting work by failure code would have duplicated
investigation and risked inconsistent patches. The first diagnostic task should ask which
gates share a state transition.

### Contracts are diagnostic indexes, not ceremonial documentation

The architecture specified Mulberry32, while production used a 64-bit LCG-style multiplier
that JavaScript `Number` could not represent exactly. That disagreement localized the defect
quickly. Generated architecture should be checked against implementation at high-risk seams:
algorithms, action schemas, persistent fields, initialization order, and sources of truth.

### Foundational invariants deserve direct gates

The deterministic tests did not catch an RNG that repeatedly returned the same effective
bytes. Repeatability is only half of a seeded RNG contract; sequence variation and UUID
uniqueness must also be tested. Low-level invariants can prevent several misleading UI-level
failures and are cheaper to diagnose.

### Lifecycle assumptions must be tested outside the happy browser path

The canvas relied entirely on `requestAnimationFrame`, which may be deferred in background
or automated contexts. An application should paint its initial state synchronously and paint
public state changes without relying on a future scheduling opportunity. The UI also invoked
renderer initialization twice; idempotence had hidden unclear ownership rather than resolving
it. Initialization should have one owner and an observable call count in QA.

### Intermediate verifier deltas should control scope

After the RNG and feedback correction, the verifier fell from three failures to only
`CANVAS_PIXEL_CHANGED`. That smaller result was evidence that the causal model was mostly
correct and justified one renderer-focused iteration. The orchestrator should reevaluate
scope after every external delta instead of carrying the original broad task forward.

### Automated green and visual proof reinforce each other

The final `PASS` was followed by inspection of the full-resolution screenshot. It showed a
real field, Reservoir, motes, and both units. This matters because the session began with a
false-green suite and a visually empty game. For visual applications, completion needs both
executable behavioral evidence and a meaningful rendered artifact.

Sources consulted on 2026-07-18:

- Anthropic, *Effective context engineering for AI agents*:
  https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents
- Anthropic, *Effective harnesses for long-running agents*:
  https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents
- Anthropic, *Harness design for long-running application development*:
  https://www.anthropic.com/engineering/harness-design-long-running-apps
- Mistral, *Choose between the CLI, VS Code, web, and sessions*:
  https://docs.mistral.ai/vibe/code/choose-cli-vscode-web-sessions
- Mistral, *Agents* and *MCP servers*:
  https://docs.mistral.ai/vibe/code/vs-code-extension/agents
  https://docs.mistral.ai/vibe/code/cli/mcp-servers
- SWE-Router, temporal routing from partial agent trajectories:
  https://openreview.net/pdf/5dddb41624aa40faed655bcd2deaf8151437173a.pdf

## Conclusion

Mistral Cloud demonstrated strong visual analysis, source tracing, localized editing, and
the ability to implement substantial repairs once its tools were correctly configured.
The session also demonstrated that a capable model cannot compensate for an unproven tool
loop, duplicated sources of truth, false-green tests, or an orchestrator that responds to
harness failures by taking over code-level reasoning.

The earlier session status was: Glimweave was a valuable orchestration experiment, not yet a verified finished game. The
next step should be a re-architected persistent Mistral repair loop—not another sequence of
outer-authored micro-patches.

The current status supersedes that earlier snapshot. Glimweave is now externally verified
by the strengthened clean-profile browser suite, and the final full-resolution evidence
shows a meaningful rendered playfield. This does not prove long-term balance or a complete
human playthrough, but it closes the original non-working game blocker.

The re-architected Mistral loop still produced value even though it did not complete the
repair: it made the takeover decision measurable. A qualified harness, durable evidence,
explicit progress signals, and a bounded routing rule allowed the stronger model to take
over without micromanaging the cheaper worker or repeating its broad repository search.
