Return ONLY the complete corrected `README.md` as Markdown. Preserve its useful player pitch and verification information, but repair every factual/documentation issue below:

1. `index.html` is the browser entry point for a multi-file runtime, not a single-file entry point.
2. Expand the runtime map to include `bootstrap.js`, generated `data/game-data.js`, `src/integration.js`, `src/test-bridge.js`, `src/smoke-scenarios.js`, and `smoke.js`, accurately distinguishing production, generated wrapper, and smoke-only modules.
3. Link `docs/ORCHESTRATION_LEARNINGS.md` alongside QA and verification.
4. Orchestration evidence is:
   - `.orchestration/prompts/`: task/repair prompts;
   - `.orchestration/jobs/`: executable job specifications;
   - `.orchestration/runs/`: accepted run evidence with model, input/output hashes, timestamps, duration, and usage when exposed;
   - `.orchestration/NORMALIZATIONS.md`: mechanical transport normalizations.
   Do not describe `.orchestration/runtime/` as evidence; it is temporary packet space and is empty after runs.
5. There is no `tools/normalize.py`. List the real tools: `run_cloud_vibe_job.py`, `extract_contract_packets.py`, `assemble_runtime.py`, and `verify_glimweave.py`.
6. Mistral Cloud authored/repaired `src/integration.js`, both test seam modules, and `smoke.js` as well as the main product artifacts. The OUTER orchestrator authored the brief, runner/job orchestration, deterministic assembler/wrappers, verification command, prompt routing, acceptance/rejection decisions, and compact evidence handling. Do not credit it with writing the integration layer.
7. `README.md`, `docs/QA_REVIEW.md`, and `docs/ORCHESTRATION_LEARNINGS.md` were also Mistral Cloud documentation jobs.
8. Verification proves the covered mechanics/integration paths pass. Retain the honest limitation: no completed long-form human balance/playthrough claim. Avoid saying the game may be “unwinnable”; the automated victory path passes, but organic balance/pacing remains unproven.
9. Remove redundant horizontal rules and keep Markdown clean.
10. Keep the original IP clear: Glim is luminous possibility coaxed from the living Sky Loom and caught before fading. Never characterize it with rock/mining terminology.

Keep correct relative links and exact verification commands. No surrounding fences/commentary.
