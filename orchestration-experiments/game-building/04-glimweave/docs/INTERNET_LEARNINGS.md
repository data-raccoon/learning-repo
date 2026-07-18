The evidence does not yet justify replacing Mistral. It justifies giving Mistral one final run inside a substantially better harness.

Our previous runs mixed three failure classes: model reasoning, tool/permission problems, and lost browser evidence. Because those weren’t separated, we couldn’t fairly measure Mistral’s capability.

## Recommended architecture

Use a persistent Mistral Vibe session with a dedicated repair agent—not repeated one-shot prompts. Vibe supports resumable sessions, shared CLI/VS Code history, compaction, rewind, and agent profiles containing their own prompt, tools, model, and approval policy. [Mistral sessions](https://docs.mistral.ai/vibe/code/choose-cli-vscode-web-sessions), [CLI commands](https://docs.mistral.ai/vibe/code/cli/commands-shortcuts), [custom agents](https://docs.mistral.ai/vibe/code/vs-code-extension/agents).

The loop should be:

```text
External browser verifier
        ↓ compact structured evidence
Mistral diagnoses → edits → reruns verifier
        ↓
Repair ledger + diff + screenshot paths
```

The browser verifier should return text/JSON such as:

- boot and console errors
- failed gate codes
- resource values after each action
- button state and label
- tutorial state
- canvas dimensions and pixel-change/hash result
- screenshot file paths

Vibe supports custom MCP tools, so the verifier can become a first-class tool rather than output we manually paste into prompts. [Mistral MCP documentation](https://docs.mistral.ai/vibe/code/cli/mcp-servers).

Because our installed Vibe path discards MCP image blocks, the tool should return structured evidence and screenshot paths. Native image review can remain a separate QA step; Mistral does not need the full screenshot during every edit cycle.

Maintain a small `REPAIR_STATE.md` containing:

- current failing verifier gates
- latest relevant observations
- hypotheses attempted and disproven
- files changed
- next proposed experiment

This follows current context-engineering guidance: keep the active context small and high-signal, fetch detailed evidence just in time, and use structured notes across context boundaries. [Anthropic context-engineering guidance](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents).

## How Mistral should be instructed

Give it ownership of an outcome, not a predetermined patch:

> Own first-run playability. Run the external verifier, identify one causal hypothesis, make a scoped production-code change, and rerun the verifier. Do not weaken or edit tests merely to obtain a pass. Record disproven hypotheses. Stop and prepare a handoff after two independently tested hypotheses fail to improve the external result.

This is the right “altitude”: explicit objective, evidence loop, constraints, and stopping rule—but no selectors, line edits, or speculative diagnosis supplied by us.

Generator/evaluator separation and repeated browser validation have produced substantially better long-running application results than a single unconstrained coding agent. [Anthropic application-development harness](https://www.anthropic.com/engineering/harness-design-long-running-apps), [long-running agent harnesses](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents).

## Takeover policy

Give Mistral one fresh repair episode with a persistent session and at most three diagnosis–patch–verify cycles.

| Observed result | Interpretation | Action |
|---|---|---|
| Permission, path, tool, or empty-response failure | Harness failure | Repair harness; don’t escalate models |
| Failure becomes more specific or gate count falls | Useful trajectory progress | Continue Mistral |
| Patch passes the independent verifier | Successful repair | Let Mistral continue |
| Same failure after two distinct, evidence-based patches | Reasoning plateau | Escalate diagnosis |
| Repeats a disproven hypothesis, weakens tests, or causes structural damage twice | Reliability limit | Escalate immediately |
| Cannot preserve cross-file invariants after compaction/state ledger | Context/reasoning limit | Stronger model takes ownership |

This trajectory-based decision is more informative than routing from the task description alone. Current routing research similarly finds that allowing the cheaper model to explore briefly and routing based on its partial trajectory can outperform choosing the model upfront. [SWE-Router research paper](https://openreview.net/pdf/5dddb41624aa40faed655bcd2deaf8151437173a.pdf).

The stronger-model handoff should contain the exact verifier command and output, screenshots, current diff, architecture/source ownership, and the list of disproven hypotheses—especially that the stale-closure hypothesis was tested and rejected. The stronger model should receive the evidence and own the diagnosis, not merely implement another guessed fix.

So the next experiment should test Mistral plus the corrected harness. If it fails the explicit takeover thresholds, we will have a defensible conclusion that the remaining problem requires a stronger reasoning model rather than another orchestration adjustment.
