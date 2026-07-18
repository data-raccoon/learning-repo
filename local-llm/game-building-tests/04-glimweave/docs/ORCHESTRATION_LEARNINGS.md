# Orchestration Learnings: Experiment 04 — Glimweave

## Overview

Experiment 04 demonstrated that Mistral Cloud `mistral-medium-3.5` can build a complete, original strategic browser game with real-time simulation, multiple factions, upgrade trees, and a finite campaign—provided the orchestration strategy constrains scope, enforces contracts, and keeps the model focused on small, replaceable artifacts.

## Actionable Lessons

### Contract Packets Enable Modular Production

Each major subsystem (`state.js`, `simulation.js`, `render.js`, `ui.js`, `styles.css`, and `data/game-data.json`) was produced by a separate, targeted Mistral Cloud run against a precise contract packet. These packets specified the exact interface, data shapes, and integration points required. This separation allowed independent model invocations to generate a coherent multi-file project without cross-contamination or prompt drift. The artifact ownership table in the brief was not decorative—it was the orchestration backbone.

### Full-File Regeneration Is Prohibitively Expensive

Modules of 40–50 KB repeatedly exceeded token limits and introduced cascading errors. Attempting to regenerate `simulation.js` or `ui.js` monolithically after a defect often produced new regressions elsewhere in the same file, forcing additional expensive repairs. The repair loop for monolithic artifacts was: error → full regeneration → new error → another regeneration. This cycle consumed budget and time while making it difficult to isolate the original defect.

### Small Integration Boundaries Are Superior

Targeted bridge modules (`test-bridge.js`, `smoke-scenarios.js`, `integration.js`) proved far more effective than regenerating large files. A single 60-line integration layer handled all cross-cutting concerns: doctrine ID normalization, permanent upgrade side-effect routing, and Retuning invariants. When a defect appeared—such as the action discriminator mismatch between caller and simulation, or the doctrine key/display normalization drift—the fix was localized to this small module rather than embedded in a massive file. This reduced blast radius, accelerated verification, and made normalization deterministic.

### Generated Tests Need Stable, External Expectations

Automated verifiers caught real defects, but the tests themselves could drift. The UI test API contract mismatch was a case in point: the test harness expected specific state shapes and function signatures that diverged from the actual implementation. The lesson is to keep verifier expectations external and stable, separate from the generated code. When contradictions arise, diagnose with minimal instrumentation and reject invented fields or signatures. The test API must be treated as a first-class contract, not an afterthought.

### Browser Execution Reveals What Static Review Misses

Headless Edge testing found the fractional production flooring bug that static review had missed. The starter producer emitted fractional Glim that `Math.floor` reduced to zero, making the first unit inert. This defect was invisible in code review but immediately apparent in runtime behavior. Browser-based verification is essential for real-time simulations where numeric edge cases and timing-dependent behavior matter.

### Narrow Prompts With Reduced Context Outperform Token Bloat

Simply increasing token limits did not solve the monolithic repair problem. Narrow, focused prompts with reduced context—targeting a specific function or data structure—produced better results than broad prompts with larger budgets. Precision beats profligacy.

### Provenance Hashes and Local Artifact Writes Are Force Multipliers

Recording run provenance (model, prompt, parameters, timestamps) and writing cloud artifacts directly to disk prevented the need to route massive model outputs through the outer orchestrator. Compact evidence—hashes, job records, and acceptance decisions—could be returned externally while the full artifacts remained local. This pattern kept orchestration traffic light and made reproduction trivial.

### Expose Stable Enums and Test APIs Early

The doctrine key/display normalization issue (`"LUMINANCE"` vs `"Luminance"`) and the action discriminator mismatch stemmed from a lack of stable, shared enumerations. Expose action/schema enums and test APIs at the data layer from the start. This prevents display-value/key drift and makes integration predictable. The compatibility layer that papered over these mismatches was effective but represented technical debt; a unified contract layer would have been cleaner.

### Distinguish Automated Acceptance from Human Balance

The acceptance suite proved mechanics: phases, units, doctrines, upgrades, production/capture separation, victory conditions, Retuning, and persistence. But it did not claim the economy was fun, balanced, or winnable. Automated acceptance and human balance/playtesting serve different goals. The verification evidence (`PASS phases=4 weftlings=5 doctrines=3 upgrades=18`, `PASS browser_suite=core+integration`) confirms correctness, not quality of experience.

## Failed Approaches

Full-module regeneration was the most significant failure. The first instinct when a defect appeared in `simulation.js` or `ui.js` was to re-prompt the model to regenerate the entire file. This approach failed repeatedly: it was token-expensive, introduced regressions, and made it difficult to isolate the root cause. Each regeneration risked new errors in unrelated parts of the module, turning a single defect into a chain of problems.

Monolithic integration was another dead end. Initially, all cross-cutting logic was embedded directly in the large modules. This made normalization fragile and manual. Extracting a small integration layer solved this, but the initial attempt to keep everything internal wasted time and budget.

Relying solely on static review for runtime behavior was insufficient. The fractional production flooring bug evaded static analysis but was immediately caught by browser execution. The lesson is that runtime verification is non-negotiable for simulations with numeric edge cases.

## Recommended Orchestration Blueprint

For the next ambitious local or cloud model project, adopt the following pattern:

1. **Decompose by contract, not by convenience.** Break the system into the smallest independently testable modules with explicit interfaces. For a game, this typically means separate modules for state management, simulation logic, rendering, UI controls, and data definitions. Use contract packets to specify exact inputs, outputs, and integration points for each.

2. **Favor small, replaceable artifacts.** Target individual functions, data structures, or thin bridge modules rather than monolithic files. When a defect appears, regenerate or repair only the smallest possible unit. The integration layer for Glimweave was ~60 lines and handled all cross-cutting concerns; this is the model to emulate.

3. **Establish a stable test API early.** Define a minimal, stable test interface (`createState`, `validateState`, `handleAction`) and expose it as a first-class part of the contract. Keep verifier expectations external and independent of generated code. When generated tests diverge, align the implementation to the external contract, not vice versa.

4. **Verify in the target runtime.** Use headless browser automation for any project that runs in a browser. Static review will miss runtime-specific defects like fractional value flooring, timing issues, or DOM integration problems. The verification suite for Glimweave covered module boot, initial-state validation, data cardinalities, simulation mechanics, UI rendering, and accessibility—all in headless Edge.

5. **Record provenance and write artifacts locally.** Store run records (model, prompt, parameters, timestamps) and write generated artifacts directly to disk. Return only compact evidence (hashes, pass/fail status) to the orchestrator. This keeps traffic light and makes reproduction deterministic.

6. **Normalize at the boundaries.** Use a thin integration layer to handle ID normalization, key/display mapping, and other cross-cutting concerns. This layer should be small, focused, and easy to regenerate if needed. Avoid embedding cross-cutting logic in large modules.

7. **Separate acceptance from balance.** Define automated acceptance tests that verify correctness and completeness of mechanics. Do not conflate this with human balance or playtesting. The acceptance suite for Glimweave proved the mechanics worked; it did not claim the game was balanced or fun.

8. **Plan for failure modes.** Assume generated tests may be wrong. Assume large regenerations may introduce regressions. Assume static review will miss runtime defects. Design the orchestration to catch these failures quickly with minimal instrumentation and clear feedback loops.

## Conclusion

Glimweave succeeded in its core objective: Mistral Cloud built a complete, original browser game with a rich simulation, multiple factions, upgrade trees, and a finite campaign. The key to success was not the model’s raw capability but the orchestration strategy: contract-driven modularity, small replaceable artifacts, stable external contracts, runtime verification, and disciplined provenance tracking. The failures—full-module regeneration, monolithic integration, static-only review—were as instructive as the successes. The blueprint above distills these lessons into a repeatable pattern for the next ambitious project.
