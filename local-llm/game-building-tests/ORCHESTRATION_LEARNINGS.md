# Lessons from Orchestrating a Small Local Model

## 1. Keep local output local

Large generated files should move directly from the local endpoint to the filesystem.
Routing them through a frontier model wastes paid tokens and turns the orchestrator into
an expensive copy-and-paste layer. The outer agent should receive only compact status,
failure codes, and artifact metadata.

## 2. Treat the orchestrator as a state machine

The controller owns task order, schemas, budgets, retries, persistence, validation, and
termination. A model response is not completion. Completion means that an artifact was
written and objective acceptance checks passed.

## 3. Reduce coupling at the model boundary

A small model struggled when asked to design, implement, integrate, review, and repair a
whole HTML application in one context. It performed much better on narrow outputs such
as a JSON manifest, presentation copy, or CSS against a fixed DOM contract.

## 4. Prefer declarative artifacts

Validated JSON and other constrained data are safer model outputs than tightly coupled
application code. A deterministic runtime can interpret that data while the model still
owns game design, level design, wording, and visual direction.

## 5. Make invalid states difficult to represent

The controller should validate schemas, normalize harmless omissions, supply safe
defaults, escape embedded data, and reject unsafe constructs. Trivial schema drift does
not deserve another inference pass when it can be repaired deterministically.

## 6. Test behavior, not source spelling

Checking for an exact variable name or expression creates false failures. The useful
contract is observable behavior. Run the artifact in a real browser and test controls,
state transitions, scoring, restarts, accessibility, and failure states.

## 7. Separate generation from integration

Give each model task a small contract and token budget. Assemble the outputs through
stable interfaces owned by the controller. This reduces the amount of architecture the
model must remember and makes individual artifacts independently replaceable.

## 8. Preserve durable evidence

Specifications, manifests, test summaries, and final artifacts let later stages resume
without repeating earlier reasoning. Timeouts and token overruns are recoverable when a
valid artifact already exists.

## 9. Use compact repair loops

When something fails, feed the responsible local task only the relevant artifact and
short failure codes. Avoid asking the model to reread the entire project. Cap retries and
fail explicitly rather than looping indefinitely.

## 10. Architect for the model that exists

Orchestration is not merely dividing a large prompt into smaller prompts. The software
itself should expose low-context modules, explicit schemas, deterministic interfaces,
and executable checks suited to the model's actual capabilities.

## Lessons from the multi-file Orbital Command experiment

### 11. A controller run is not the same as visible model orchestration

Putting several inference calls inside one controller process makes the task graph hard
to inspect. For credible orchestration, each model task should be a distinct process or
session with a durable job specification and run record. Orbital Command recorded the
model, timestamps, input hashes, output hash, byte count, and token usage for every run.

This made dependencies and repairs independently observable. It also prevented the
orchestrator from quietly rewriting history after a failed generation.

### 12. Preserve failed work as evidence

Failed modules and repair attempts reveal the model's capability boundary. Their run
records should remain available even if deterministic code replaces their outputs.
Deleting or overwriting all evidence would make the final result look more autonomous
than it was and would prevent later analysis of recurring failure patterns.

### 13. Shared interfaces require stronger enforcement than prose

Separate model-generated modules repeatedly violated a simple shared namespace:

- one module replaced `window.OC`, erasing earlier functions;
- state and engine disagreed about whether modules were IDs or objects;
- code used `state.technologies` where the contract defined `completedTech`;
- generated UI mixed incompatible `this` bindings and data paths.

Supplying the same prose contract to every task was insufficient. Future systems should
generate interface definitions once and mechanically derive validators, adapters,
fixtures, and task prompts from that source of truth.

### 14. Validate schemas before code generation

Declarative content should pass a deterministic relationship gate before any code task
consumes it. This caught an extra generated event and normalized it without another
inference. Downstream modules then consumed one integrated `content.js` interface rather
than independently interpreting several JSON files.

Schema validation should cover not just types and required fields, but also identifiers,
cross-references, cardinality, numeric ranges, ordering, and safe defaults.

### 15. Behavioral repair needs precise localization

An initial browser failure such as `TEST_API` was too broad. A pre-module error recorder
and phase-labelled smoke tests reduced failures to actionable codes such as:

- the responsible filename and line;
- exception type and sanitized message;
- the scenario phase: boot, build, research, crew, turn, persistence, render, or reset.

Good diagnostics dramatically reduce repair context. A repair task should receive the
responsible artifact, its exact interface contract, and the smallest useful failure—not
the whole project and a request to "fix everything."

### 16. Put a hard ceiling on model repair loops

Repeated repair prompts can produce regressions or cosmetically different versions of
the same architectural error. In Orbital Command, repairs fixed one issue while creating
temporal-dead-zone errors, state-shape mismatches, or inverted resource logic.

A practical policy is:

1. Try the original bounded generation.
2. Permit one repair for a local implementation mistake.
3. Permit a second only when diagnostics identify a different, narrower defect.
4. If the same interface class fails again, change the architecture or use a deterministic
   adapter instead of spending more tokens.

### 17. Deterministic fallbacks must be disclosed

When the model-generated state, engine, and UI could not pass integration, deterministic
adapters replaced them. That was the correct engineering decision, but it changed the
provenance of the result. The project therefore records this explicitly in
`03-orbital-command/orbital-command/.orchestration/INTEGRATION_DECISIONS.md` and its
README.

The final artifact should distinguish:

- model-authored files still used at runtime;
- model-authored files that were rejected;
- normalized or assembled artifacts;
- orchestrator-owned infrastructure and fallback implementations.

### 18. Declarative generation scales better than integrated code generation

The local model reliably created the world, economy, technology tree, events, interface
copy, visual system, and documentation as bounded independent tasks. It was much less
reliable when implementing stateful modules whose correctness depended on several other
generated interfaces.

For a small model, an ambitious product should therefore use a stable interpreter or
runtime plus rich declarative content. Complexity can live in the product without forcing
the model to reproduce all integration logic on every run.

### 19. Browser tests are the integration authority

The final result passed only after running the actual ordered script files in Edge.
Source inspection would not have caught namespace replacement, binding errors, render
side effects, persistence rejection, or file-protocol behavior with equal confidence.

The smoke suite should exercise meaningful state transitions, not merely page loading:
initialization, affordable actions, construction, research, crew invariants, advancing a
turn, persistence, rendering, reset, and accessibility regions.

### 20. Optimize frontier-token usage, not only local inference

Local inference was inexpensive, but the outer orchestration consumed substantial
frontier-model context through large patches, repeated diagnostics, and overly long
repair chains. Keeping generated source out of the conversation helped, but it was not
enough.

Future cost controls should include:

- create the interface schema and test harness before launching generation;
- keep orchestration code reusable rather than rebuilding controllers per project;
- return only hashes, counts, timings, and failure codes from tools;
- avoid printing full generated modules during diagnosis;
- use automated failure-to-owner routing;
- cap repairs by failure class;
- switch to deterministic adapters earlier;
- report local and frontier token usage separately.

### 21. The best next architecture is a reusable local build system

The experiments produced several one-off controllers. The next iteration should be a
general task runner with:

- declarative job graphs and dependency hashes;
- typed artifact schemas;
- one inference per auditable run;
- isolated staging directories;
- automatic validators and browser scenarios;
- provenance manifests;
- failure ownership and bounded repair policies;
- resumability based on unchanged input hashes;
- a final bill of materials showing exactly who or what authored each file.

That would move the expensive frontier model out of routine execution. Its role would be
limited to designing contracts, improving the orchestration system, and intervening when
new failure classes appear.
