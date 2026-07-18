# Game-Building Orchestration Learnings

This is the index for lessons from the game-building experiments. The conclusions are
split by model environment so observations about a constrained local model are not
mistaken for observations about Mistral Cloud.

## Universal lessons

These held for both local and cloud models:

1. Write generated artifacts directly to disk and return only compact status, hashes,
   and failure codes to the outer orchestrator.
2. Treat executable acceptance tests—not a successful model response—as completion.
3. Define state shapes, action schemas, enum representations, and module ownership before
   generating dependent code.
4. Run browser software in a real browser. Static review missed namespace, persistence,
   timing, numeric, DOM, and file-protocol defects.
5. Route a failure to the smallest responsible artifact with the narrowest useful context.
6. Generated tests are not automatically trustworthy. Keep acceptance expectations
   independent and reject tests that invent fields or signatures.
7. Record provenance for accepted and rejected attempts, including input and output
   hashes, model, duration, limits, and failure reason.
8. When the same integration failure repeats, change the architecture instead of merely
   increasing the token budget.

## Environment-specific documents

- [`LOCAL_MODEL_ORCHESTRATION_LEARNINGS.md`](LOCAL_MODEL_ORCHESTRATION_LEARNINGS.md)
  covers experiments 01–03: limited model capability, declarative generation, stable
  deterministic runtimes, and inexpensive local inference.
- [`CLOUD_MODEL_ORCHESTRATION_LEARNINGS.md`](CLOUD_MODEL_ORCHESTRATION_LEARNINGS.md)
  covers experiment 04: Mistral Cloud capability, agentic token consumption, latency,
  full-file repair costs, direct artifact transport, and cloud-specific accounting.
- [`04-glimweave/docs/ORCHESTRATION_LEARNINGS.md`](04-glimweave/docs/ORCHESTRATION_LEARNINGS.md)
  is the detailed Mistral-authored postmortem for Glimweave itself.

The local and cloud documents may recommend similar techniques for different reasons.
For example, small modules help a local model stay within its capability envelope; for a
cloud model they reduce paid context, full-file reproduction, latency, and regression
risk. Those are related conclusions, but not interchangeable evidence.
