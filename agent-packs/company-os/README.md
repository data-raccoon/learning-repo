# Company-OS v1

This portable operating-system pack combines durable governance, a neutral
registry of 19 specialist roles, six reusable skills, venture and decision
templates, optional IDE adapters, and dependency-free validation.

## Use the pack

1. Read `agent-pack.json` and select an entry point or component.
2. Let the controller choose the model, tools, limits, and optional adapter.
3. Start with an explicit operating request, for example:
   - `Use $venture-intake to turn this idea into a testable venture thesis.`
   - `Use $council-decision to evaluate whether this venture should receive capacity.`
   - `Use $initiative-planning to create a bounded Work Order for this objective.`
4. Review every approval request as the human Founder. Council recommendations are never approvals.

## Repository Map

- `agent-definitions/`: canonical model-neutral role instructions and permissions.
- `company/agent-registry.md`: role cells, decision ownership, access, and outputs.
- `skills/`: portable skill sources.
- `adapters/`: optional Codex, Vibe, and VS Code projections; these are not
  canonical role or skill ownership.
- `company/`: charter, governance, role registry, decisions, and canonical templates.
- `ventures/`: one evidence and decision space per venture.
- `products/`: stack-agnostic product implementations linked to ventures.
- `shared/`: capabilities with demonstrated reuse across ventures.
- `evals/`: IDE routing and governance smoke scenarios.
- `scripts/` and `tests/`: dependency-free structural validation.

Domain-specific work is kept outside this reusable operating system. The current Cologne public-spending POC lives at `../initiatives/cologne-tax-improvements/`.

## Validate

```powershell
& "${env:USERPROFILE}\.venvs\all\Scripts\python.exe" scripts\validate_company_os.py
& "${env:USERPROFILE}\.venvs\all\Scripts\python.exe" -m unittest discover -s tests -v
```

The optional VS Code interpreter setting is stored under
`adapters/vscode/settings.json`; no third-party Python package is required.
