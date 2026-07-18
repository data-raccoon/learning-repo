# Game-Building Orchestration Agent Instructions

These instructions apply to every game-building task in this directory. They synthesize
the shared lessons from experiments 01–04 and the Glimweave generation, QA, and repair
sessions. Treat them as operating rules, not suggestions.

## Mission

Build games through an auditable controller that gives each worker a bounded outcome,
accepts artifacts only through independent evidence, and preserves an honest record of
what generated, normalized, repaired, rejected, and verified each result.

A worker response is never completion. Completion means that the intended artifact exists,
structural guards pass, executable acceptance passes in the target runtime, and the
required evidence has been retained.

## Non-Negotiable Boundaries

- Keep generated artifacts on disk. Do not relay large source files through the outer
  orchestrator. Return compact status, hashes, byte counts, timings, usage, and failure
  codes.
- Keep the evaluator independent from the implementation worker. Workers may add tests,
  but they may not weaken, replace, or define the external release gate.
- Keep credentials out of repositories, prompts, logs, run records, and generated files.
- Preserve user work and unrelated changes. Scope every worker to declared files and
  inspect the diff after every run, including timed-out and failed runs.
- Maintain one authoritative source for every runtime datum, schema, enum, action, and
  test definition. Generate mirrors deterministically and verify that they agree.
- Disclose provenance. Distinguish worker-authored runtime files, rejected attempts,
  normalized or assembled output, orchestration infrastructure, adapters, and
  deterministic fallbacks.
- Never describe a build as playable, working, or complete from static inspection, a
  successful model response, generated unit tests, or a page-load smoke test alone.

## Controller Responsibilities

The outer orchestrator owns:

- the task graph, dependency order, ownership map, budgets, retry policy, and termination;
- machine-readable contracts, validators, fixtures, acceptance expectations, and release
  decisions;
- isolated staging, artifact transport, hashes, run records, checkpoints, and rollback
  guards;
- harness qualification, target-runtime execution, evidence collection, and failure
  routing;
- model routing and honest takeover decisions.

The worker owns:

- code-level diagnosis and hypotheses within its assigned subsystem;
- implementation inside its declared file scope;
- rerunning the supplied verifier and reporting the resulting delta;
- recording experiments and disproven hypotheses during a persistent repair episode.

Do not give a worker a vague request to “fix everything.” Do not prescribe selectors,
line edits, or an unproven causal theory when the worker is meant to diagnose. Give it an
outcome, coherent ownership, external evidence, constraints, a verifier command, and a
stopping rule. If the orchestrator supplies the causal hypothesis or exact patch, record
that diagnosis has already been taken over and classify the worker as an implementer.

## Architecture Before Generation

1. Write the acceptance contract and public player journeys first.
2. Define one machine-readable source of truth for state shapes, identifiers, actions,
   enum keys and display values, exported APIs, persistence, and initialization ownership.
3. Derive contract packets, validators, adapters, fixtures, and prompt fragments from that
   source when practical. Shared prose alone is not interface enforcement.
4. Validate declarative data before code consumes it. Check types, required fields,
   cardinalities, cross-references, uniqueness, ordering, numeric ranges, and safe defaults.
5. Decompose by independently testable contracts and causal ownership, not merely by file
   type. Prefer low-coupling data, state, simulation, renderer, UI, and integration seams.
6. Make invalid states hard to represent. Normalize harmless omissions deterministically;
   reject unsafe or ambiguous drift before it reaches downstream jobs.
7. Assign initialization once. Idempotence must not conceal duplicate boot calls,
   observers, loops, or lifecycle resets.
8. Choose persistence policy in the brief. Either migration is an explicit tested product
   requirement or development builds invalidate old saves by version. Do not improvise
   migration while diagnosing an unrelated failure.

For constrained local models, prefer a stable deterministic runtime interpreting rich,
validated declarative artifacts. Give local workers narrow outputs and small contracts;
do not require them to retain a multi-module architecture in one context.

For capable paid cloud models, larger product ownership is feasible, but contracts remain
mandatory. Use meaningful artifact-sized jobs—not trivial micro-jobs—and design for paid
context, agent startup latency, repeated reads, full-file reproduction, and regression risk.

## Job Design and Artifact Acceptance

Each job specification must declare:

- one concrete outcome and one owner;
- allowed read and write paths;
- exact contract fragments and dependency hashes;
- required output format and target path;
- structural guards and the independent verifier command;
- token, price, time, turn, and retry ceilings;
- success, retry, handoff, and rollback conditions.

Use one auditable process or session per meaningful artifact. Write output to staging and
accept it by hash only after validation. Prefer the following repair protocols, in order:

1. a validated structured patch against stable anchors;
2. replacement of a small independently owned module;
3. a narrow compatibility or adapter layer at the seam;
4. full replacement of a large file only when its internal architecture must change.

Do not ask a worker to reproduce a 40–50 KB file for a localized defect. Reduce context
before increasing limits: supply exported signatures, schema slices, the failing scenario,
and bounded relevant reads. Do not embed large source in the prompt and then ask the worker
to read it again.

After every run, even one that times out or reports failure:

- inspect the scoped diff because failed runs may still edit files;
- check size, syntax, truncation, duplicate definitions, and out-of-scope changes;
- run external acceptance independently;
- preserve the streamed trajectory and artifacts;
- roll back only the worker's scoped files when transactional guards fail.

Never interpret a runner's `PASS job=...` or a worker's final prose as product acceptance.

## Harness Qualification

Before an expensive generation or repair episode, prove every required tool path with a
small capability probe. Test the actual operating system paths and shell syntax, reads,
bounded reads, edits, approvals, commands, verifier execution, streaming output, session
continuation, compaction, and image transport where applicable.

Classify permission denials, invalid paths, empty responses, lost trajectories, browser
crashes, missing evidence, and broken continuation as harness failures. Repair and re-prove
the harness before using those episodes to judge the worker model.

Know the runner's accounting semantics. A cumulative token ceiling is not a context-window
limit: tool turns may resend earlier file contents. Capture provider-side token and price
usage where possible; configured ceilings are not usage evidence. Use grep-first retrieval,
bounded slices, early compaction, and a durable state ledger for long repair sessions.

When the text tool cannot transmit image pixels, use the runtime's native multimodal image
channel. If image-plus-tools continuation is unreliable, split the flow into a read-only
visual audit, persisted findings, and a normal editing loop. Do not encode images as text.

## Independent Verification

Test behavior, not source spelling. Avoid assertions tied to variable names or exact
expressions unless they are part of a public contract. Generated tests are scaffolding,
not authority; validate their fixtures and reject invented fields, signatures, or enum
representations.

For browser games, execute the real ordered production files in a real browser, including
the intended file or server protocol. Verification must cover meaningful transitions:

- boot, initial state, and the absence of production exceptions;
- first-use economy and organic progress without direct state funding;
- public actions, resource changes, scoring or progression, failure feedback, and reset;
- time-based accumulation across multiple ticks, including fractional production;
- persistence, reload, version behavior, and invalid-save handling;
- rendering after boot and after public state changes;
- accessibility regions, accessible names, focus, keyboard paths, and responsive layouts;
- domain invariants such as identifier uniqueness, RNG repeatability and sequence
  variation, enum normalization, and cross-reference validity.

Keep automated correctness, organic playthrough, performance, accessibility, visual
quality, and human balance as separate gates. A mechanical pass does not prove fun,
balance, long-term winnability, or a complete human playthrough.

### Clean-Profile Visual and First-Use Gate

Run public journeys with empty storage at declared desktop and mobile viewports. Require:

- a visible, materially sized playfield not occluded by control panels;
- canvas backing geometry consistent with CSS size and device-pixel-ratio policy;
- within the declared onboarding window, either an enabled meaningful action or a visible
  passive path to one;
- first producer, first generated resource, first purchase or capture, first upgrade,
  phase transition, major choice, reset loop, save/reload, and keyboard path through public
  interfaces rather than direct state mutation;
- visible output and state-level confirmation after actions;
- a full-resolution screenshot that independently shows a meaningful rendered product.

Render the initial state synchronously enough to work in automated or background tabs.
Do not rely exclusively on `requestAnimationFrame` for first paint or state-changing paint.

### Physical Interaction Gate

Treat action semantics, DOM wiring, and physical interaction as three separate layers.
`HTMLElement.click()` may probe a handler but cannot prove that a person can use a control.

For critical controls, verify:

- hit-testing with `elementFromPoint()` or trusted browser input at the control's center;
- pointer down, a delay spanning at least one application tick, and pointer up;
- the same connected target survives the complete press lifecycle;
- no overlay or stacking layer intercepts the coordinates;
- native keyboard activation and focus continuity during live updates;
- visible and state changes after activation;
- another interaction after a legitimate structural rerender;
- loop-generated callbacks with at least two distinct indices.

Interactive DOM identity is an architectural invariant. High-frequency loops may update
text, progress, and disabled state in place, but must not replace focused or pressed
controls. Rebuild structure only for real structural changes such as unlocks, phases, or
completed purchases. Tutorial and modal layers require explicit stacking, focus, advance,
back, dismissal, and interception tests.

## Evidence and Diagnostics

Return compact structured gate results for routing while retaining rich artifacts for
diagnosis. A browser run should preserve, as applicable:

- exact verifier command, viewport, profile state, timestamps, and exit class;
- failed gate codes and before/after state deltas;
- the first relevant production exception and console errors;
- final DOM, notification text, accessible labels, geometry, and hit-test targets;
- canvas dimensions and position-sensitive pixel hashes;
- full-resolution screenshots and their paths.

Compact failures are symptoms. Before assigning separate workers, check whether several
gates share one causal dependency or failed state transition. Compare implementation with
architecture contracts at high-risk seams such as algorithms, action schemas, persistence,
initialization, and sources of truth. Turn foundational assumptions into direct gates.

Localize failure evidence to filename, line when known, exception class, scenario phase,
contract, and smallest responsible artifact. Send the repair owner only that evidence and
the context needed to act.

## Repair Loop and Model Routing

Use a persistent repair worker when the runner supports it. Maintain a compact repair
ledger containing current gates, latest observations, hypotheses tried and disproven,
files changed, verifier deltas, and the next proposed experiment.

For each cycle:

1. run the immutable external verifier;
2. identify one causal hypothesis or coherent causal group;
3. make a scoped production change;
4. inspect structural guards and diff;
5. rerun the same verifier;
6. record the before/after delta and narrow the next scope.

Continue while the trajectory becomes more specific, reduces external failures, completes
a tested experiment, or lands an independently surviving patch. A lower failure count is
meaningful evidence and should narrow the next job.

Use this bounded policy:

1. allow the original implementation attempt;
2. allow one repair for a localized implementation defect;
3. allow another only for a distinct, narrower defect or when external evidence improves;
4. if the same interface class recurs, re-architect the seam or add a deterministic adapter;
5. route diagnosis upward when a qualified episode repeatedly explores without forming an
   experiment, repeats disproven reasoning, weakens acceptance, causes structural damage,
   loses cross-file invariants, or exceeds the cost cap without external progress.

Do not count harness failures against the worker. Do not claim that escalation proves a
model can never solve the problem; it identifies the best next owner for the observed state,
harness, and budget.

A takeover packet must include the current diff, exact verifier command and output, paths
to retained DOM/screenshots/state evidence, contracts and ownership, constraints, cost and
trajectory summary, and tried or disproven hypotheses. Do not include the stronger model's
proposed fix; the new diagnosis owner must reason independently.

## Provenance and Resumability

Record every accepted and rejected attempt, including infrastructure failures. Each run
record should contain:

- job and dependency identifiers;
- model and runner versions;
- start and end times and duration;
- input, contract, dependency, and output hashes;
- output path and byte count;
- token, price, turn, and timeout limits;
- provider usage when available;
- changed files, exit class, compact failure detail, and acceptance decision.

Keep accepted artifacts immutable or versioned. Preserve failed artifacts and repair
attempts as capability evidence. Resume jobs only when input and dependency hashes still
match. End with a bill of materials that states who or what authored every shipped file.

## Release Decision

Release only when all mandatory structural, behavioral, clean-profile, interaction,
accessibility, persistence, and visual gates pass without weakening the evaluator. Inspect
the final rendered evidence after automated green. Report untested quality dimensions and
known limitations plainly.

When a gate fails, report the failure and its evidence. When only mechanical acceptance
passes, say exactly that. Honest provenance and bounded claims are part of correctness.
