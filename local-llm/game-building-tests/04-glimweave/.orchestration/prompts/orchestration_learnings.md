Write `docs/ORCHESTRATION_LEARNINGS.md`, a concise technical postmortem of this Mistral Cloud game-building experiment. Return ONLY Markdown.

Explain the actionable lessons, grounded in the attached QA review and experiment brief:

- contract packets helped independent model runs produce a multi-file project;
- full-file regeneration of 40–50 KB modules is token-expensive and repeatedly exceeded limits;
- integration boundaries should be small, independently replaceable artifacts (`test-bridge.js`, `smoke-scenarios.js`, `integration.js`);
- generated tests can be wrong too, so keep verifier expectations external/stable, diagnose contradictions with minimal instrumentation, and reject invented fields/signatures;
- browser execution found faults static review missed, especially fractional production flooring;
- narrow prompts plus reduced context outperformed simply increasing token limits;
- provenance hashes/run records and silent local artifact writes prevent routing huge model output through the outer orchestrator;
- architecture should expose stable action/schema enums and test APIs early to avoid display-value/key drift;
- distinguish automated acceptance from human balance/playtesting.

Include a brief recommended orchestration blueprint for the next ambitious local/cloud model project. Be candid about failed approaches. Do not mention company policy, shards, or GNORP. Target 700–1100 words.
