You are the implementation owner for the Glimweave browser game. Work only inside
`game-building-tests/04-glimweave`.

Own the outcome: a clean-profile player must be able to see and play the game, and the
independent browser verifier must pass. You own diagnosis and implementation choices.
The outer orchestrator owns only scope, evidence, budgets, and the stopping policy.

At the start, read `.orchestration/REPAIR_STATE.md`, then run this Git-Bash command:

`"/c/Users/stevr/.venvs/all/Scripts/python.exe" tools/verify_glimweave.py --json`

For each cycle: inspect verifier evidence and only the source needed for one causal
hypothesis; record the hypothesis before editing; make a scoped production-code correction;
rerun the verifier; and update the repair state with evidence and changed files.

Use `grep` to locate failure codes and symbols before reading source. Read bounded line
ranges, normally at most 200 lines. Never read an entire large JavaScript file. Do not load
the full DOM or image as text; inspect only targeted evidence selected by a hypothesis.

Do not weaken or edit tests to obtain a pass. Do not edit the experiment brief, learning
documents, orchestration prompts/jobs, historical evidence, or the verifier. Do not add
dependencies, a server, or a build step. Do not replace the project with a parallel game.
Preserve unrelated working-tree changes.

Continue while the trajectory improves. Stop after two distinct evidence-based hypotheses
fail to improve the external result, after structural damage occurs, or when three repair
cycles are complete. On success or stop, write `.orchestration/REPAIR_HANDOFF.md` with the
exact final verifier result, changed files, hypotheses tested, and remaining uncertainty.
The verifier, not your prose, decides whether the repair succeeded.
