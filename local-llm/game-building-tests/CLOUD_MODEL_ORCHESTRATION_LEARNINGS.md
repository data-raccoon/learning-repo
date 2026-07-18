# Lessons from Orchestrating Mistral Cloud

## Scope

These conclusions come from experiment 04, Glimweave, built with Mistral Cloud
`mistral-medium-3.5` through Vibe. They should not be generalized to the constrained
local model used in experiments 01–03. The cloud model could design and implement a much
more ambitious multi-file application, but its agentic execution had a different cost
profile and a distinct set of failure modes.

## 1. Greater capability changes the feasible product, not the need for orchestration

Mistral Cloud successfully produced a substantial game design, architecture, data model,
five main JavaScript modules, CSS, documentation, repair artifacts, and test-support
modules. This is materially beyond what the local model reliably integrated.

It still disagreed with itself across files. Examples included `weftlingType` versus the
action discriminator, doctrine enum keys versus display values, state fields invented by
generated tests, a persistence helper expecting a return value from a void function, and
handler arguments emitted in reverse order. A stronger model supports a larger ambition;
it does not eliminate contracts, runtime tests, or acceptance decisions.

## 2. Cloud agent tokens can dwarf outer-orchestrator tokens

The experiment retained 28 accepted cloud run records. Their configured token ceilings
totalled roughly 2.5 million tokens. Four observed token-limit failures alone reached
about 902,000 tokens before producing no accepted artifact. Because Vibe exposed empty
usage objects in the run output, exact consumption is unavailable; the defensible rough
estimate is approximately 2–3 million Mistral tokens for the experiment, versus roughly
25,000–50,000 newly generated orchestration tokens from the outer model.

This accounting is cloud-specific. Local inference tokens were intentionally treated as
cheap in earlier experiments. With a paid cloud worker, every reread, agent turn, failed
full-file reproduction, and retry is part of the economic design.

Future runners should collect provider-side usage rather than relying on an agent CLI to
forward it. A token cap is an upper bound, not usage evidence. Price caps and token caps
should both be recorded.

## 3. Direct-to-disk transport was the right boundary

Cloud artifacts were captured by a local runner and written directly to their target
files. The outer orchestrator saw compact lines such as job ID, model, byte count, hash,
and duration—not tens of thousands of lines of generated source.

This prevented the expensive outer model from becoming a copy-and-paste relay. It also
made artifact hashes and run records natural outputs of the pipeline. Direct transport
should remain the default for both cloud and local workers, but the savings are especially
important when the worker itself is also paid by token.

## 4. Full-file replacement is a poor repair protocol

The most expensive failures came from asking the agent to reread and return complete
40–50 KB modules for a localized defect. Two UI repair attempts exceeded about 194,000
and 288,000 tokens without an accepted file. A focused simulation repair also crossed a
token ceiling before succeeding with a higher budget.

This was not evidence that the cloud model could not understand the defect. It was a
transport and editing problem: an agentic wrapper spent tokens reading, reasoning about,
and reproducing mostly unchanged code.

The preferred cloud repair protocols are, in order:

1. emit a structured patch against stable anchors;
2. replace a small independently owned module;
3. generate a narrow compatibility or adapter layer;
4. replace a large file only when its internal architecture truly must change.

A future runner should support validated patch artifacts rather than forcing full-file
responses.

## 5. Re-architecting the seam beat increasing the budget

When the UI overwrote the simulation test API, regenerating the UI was wasteful. The
successful design used three small pieces:

- `test-bridge.js` preserved the authoritative simulation test API;
- `smoke-scenarios.js` isolated contract-valid browser scenarios;
- `integration.js` normalized doctrine IDs and routed permanent upgrades.

These modules were cheap to inspect, replace, hash, and test independently. Small modules
helped the local model because of limited capability; here they helped a capable cloud
model by reducing paid context, regression surface, latency, and full-file output.

## 6. Reduce context before increasing token limits

One scenario repair failed at about 185,000 tokens when supplied the state and simulation
modules. The context-reduced retry received the scenario file, smoke expectations, and
data only; it returned a small accepted artifact. A larger ceiling had not improved the
task definition. Removing irrelevant source did.

Cloud prompts should be assembled from dependency slices, exported signatures, schema
fragments, and the exact failing scenario. A whole-repository packet is convenient for
the orchestrator but expensive and distracting for the worker.

## 7. Agentic latency is noisy and not proportional to artifact size

Tiny jobs were not consistently fast. A 384-byte bridge took almost five minutes, while
some larger repairs completed in under a minute. Documentation and harness repairs also
showed wide latency variance.

Do not infer progress or quality from elapsed time. Use explicit timeouts, idempotent job
specifications, resumable hashes, and compact completion records. Avoid fragmenting work
into trivial cloud calls solely for conceptual purity; each process has fixed latency and
agent overhead.

## 8. Independent runtime verification found the decisive defect

The browser suite initially exposed contract drift, but the most important production bug
required minimal diagnostic instrumentation. At a 100 ms tick, a Glimspinner produced
`0.1`; the simulation floored each tick to zero instead of accumulating the fraction.
The starter producer was therefore inert and organic progression could not begin.

Static inspection and model self-review had missed it. A small diagnostic page established
that no mote was ever created, which enabled a precise cloud repair. For simulations,
tests must exercise time across multiple ticks and verify accumulated behavior—not merely
inspect instantaneous rates.

## 9. Tests generated by the same model have correlated blind spots

Mistral-generated tests directly mutated state without maintaining derived fields, used
display values where action keys were required, expected serialization from a void save
method, and later invented integration fields such as `state.doctrine` and unrelated
Iridescence totals.

The solution is not to forbid generated tests; they were useful scaffolding. The outer
acceptance contract must remain authoritative, and generated scenarios must themselves be
run and rejected when inconsistent. For important invariants, derive test fixtures from
the schema or validate them before the behavior under test executes.

## 10. Accepted and failed runs need equal provenance

The runner recorded accepted outputs well, but early infrastructure failures and
token-limit failures did not receive the same durable JSON records. That weakens exact
cost analysis and makes the final attempt graph harder to reconstruct.

Every attempted cloud job should record start/end time, model, hashes, configured limits,
exit class, compact failure detail, and provider usage when available—even when no artifact
is accepted. Accepted artifacts should be immutable or versioned rather than silently
overwriting earlier evidence.

## 11. Recommended cloud workflow

For the next ambitious cloud-model build:

1. Define one machine-readable source of truth for enums, state fields, actions, and
   exported APIs.
2. Mechanically derive contract packets, validators, fixtures, and prompt fragments from
   it.
3. Generate data and low-coupling modules first; validate every artifact before it becomes
   downstream context.
4. Run one auditable job per meaningful artifact, but avoid trivial micro-jobs whose agent
   startup cost exceeds their value.
5. Write artifacts directly to staging, then accept them by hash only after deterministic
   and browser tests pass.
6. Use patch output or small replacement modules for repairs. Cap repeated failures by
   interface class and re-architect the seam early.
7. Keep independent smoke expectations outside generated production modules.
8. Record failed runs and provider-side token/cost usage as first-class evidence.
9. Separate automated correctness, organic playthrough, performance, accessibility, and
   human balance as different release gates.

## Bottom line

The local-model experiments taught how to architect ambitious products around a model's
limited integration capacity. Glimweave taught a different lesson: a capable cloud model
can own far more of the product, but agentic token economics and large-file repair become
first-class architectural constraints. Better orchestration is not simply granting a
larger budget. It is designing software, packets, edit protocols, tests, and evidence so
that the cloud model spends tokens only where its judgment adds value.
