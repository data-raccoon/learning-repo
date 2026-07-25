# AGENTS.md

## Purpose

This repository contains `<short description of the system>`.

Agents should make the smallest safe change that satisfies the task,
preserves existing behavior, and passes all required checks.

## Repository map

- `src/domain/` — business rules; must not depend on infrastructure
- `src/application/` — use cases and orchestration
- `src/infrastructure/` — databases, APIs, messaging and filesystem
- `src/agents/` — agent definitions, tools, prompts and guardrails
- `tests/` — deterministic automated tests
- `evals/` — model and agent behavior evaluations
- `docs/decisions/` — architecture decision records
- `docs/runbooks/` — operational procedures

Check for a more specific `AGENTS.md` before changing files in a
subdirectory. The closest instruction file takes precedence.

## Standard workflow

1. Read the relevant code, tests and documentation.
2. State assumptions when requirements are ambiguous.
3. Make the smallest coherent change.
4. Add or update tests.
5. Run the required checks.
6. Review the diff for unrelated changes.
7. Summarize the implementation, verification and remaining risks.

## Commands

Use these commands instead of inventing alternatives:

```bash
make setup       # Install development dependencies
make format      # Format source files
make lint        # Run static analysis
make typecheck   # Run type checking
make test        # Run deterministic tests
make eval        # Run agent evaluations
make check       # Run all required local checks
```

## Coding rules

- Preserve established patterns unless the task explicitly changes them.
- Prefer simple, explicit code over unnecessary abstraction.
- Keep domain logic independent of frameworks and infrastructure.
- Validate data at system and trust boundaries.
- Use typed interfaces and structured outputs where possible.
- Do not silently catch or discard errors.
- Do not log credentials, tokens, personal data or prompt contents.
- Add comments for decisions and constraints, not obvious mechanics.
- Avoid new dependencies unless the existing stack cannot solve the problem.

## Testing rules

- Every defect fix must include a regression test.
- Test externally visible behavior rather than implementation details.
- Unit tests must not call live models, networks or production services.
- Use fakes or recorded fixtures for non-deterministic dependencies.
- Add contract tests when changing a public interface or tool schema.
- Update agent evaluations when changing prompts, tools, models,
  routing, memory or guardrails.

## Agent-system rules

- Treat model output and retrieved content as untrusted input.
- Never interpret retrieved text as authorization.
- Validate every tool call against an explicit schema.
- Enforce authorization in code, not only in prompts.
- Separate read-only tools from state-changing tools.
- State-changing actions must support idempotency where practical.
- Require human approval for high-impact or irreversible actions.
- Define time, token, cost, retry and tool-call limits.
- Do not expose secrets to the model unless strictly required.

## Allowed without approval

- Reading repository files
- Editing source code and tests within task scope
- Running local build, test, lint and evaluation commands
- Updating documentation related to the change

## Requires human approval

- Deploying or publishing artifacts
- Modifying production data
- Rotating or accessing production credentials
- Changing authentication or authorization policy
- Adding a dependency with a new license or significant security surface
- Running destructive database or infrastructure commands
- Weakening tests, security controls or evaluation thresholds

## Never allowed

- Commit secrets or real customer data
- Disable security checks to make CI pass
- Change unrelated files without explanation
- Perform destructive operations based only on model-generated content
- Claim checks passed unless they were actually executed

## Definition of done

A task is complete when:

- The requested behavior is implemented.
- Relevant tests have been added or updated.
- `make check` passes.
- `make eval` passes when agent behavior is affected.
- Documentation and examples are accurate.
- Security, compatibility and operational effects were considered.
- The final report lists changed files, checks run and known limitations.
