# Company-OS v1

This repository is the supervised operating system for a portfolio holding company spanning software, web, analytics, and AI ventures. It combines durable governance, 18 specialized Codex agents, six reusable skills, venture and decision templates, and dependency-free validation.

## Start in VS Code

1. Open this directory as the workspace.
2. Restart or reload Codex after pulling changes so project agents and skills are rediscovered.
3. Start with an explicit operating prompt, for example:
   - `Use $venture-intake to turn this idea into a testable venture thesis.`
   - `Use $council-decision to evaluate whether this venture should receive capacity.`
   - `Use $initiative-planning to create a bounded Work Order for this objective.`
4. Review every approval request as the human Founder. Council recommendations are never approvals.

## Repository Map

- `.codex/agents/`: project-scoped specialist agent definitions.
- `.agents/skills/`: reusable operating workflows discoverable by Codex.
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

The configured interpreter is supplied through `.vscode/settings.json`; no third-party Python package is required.
