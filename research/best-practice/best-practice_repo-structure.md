### Recommended “Agent-Ready” Repository

The following structure supports both **human engineers and coding agents**. It emphasizes concise instructions, deterministic tooling, scoped permissions, automated evaluation, and human approval for risky operations—consistent with current OpenAI, GitHub, Anthropic, and MCP guidance. ([docs.github.com](https://docs.github.com/en/copilot/using-github-copilot/using-copilot-coding-agent-to-work-on-tasks/best-practices-for-using-copilot-to-work-on-tasks?utm_source=openai))

```text
repo/
├── README.md
├── AGENTS.md
├── ARCHITECTURE.md
├── CONTRIBUTING.md
├── SECURITY.md
├── Makefile
├── .env.example
│
├── src/
│   ├── domain/
│   ├── application/
│   ├── infrastructure/
│   └── agents/
│       ├── orchestrator.*
│       ├── agents/
│       ├── tools/
│       ├── prompts/
│       ├── guardrails/
│       └── schemas/
│
├── tests/
│   ├── unit/
│   ├── integration/
│   ├── contract/
│   └── security/
│
├── evals/
│   ├── datasets/
│   ├── graders/
│   ├── scenarios/
│   └── README.md
│
├── docs/
│   ├── decisions/
│   ├── runbooks/
│   └── threat-model.md
│
├── scripts/
│   ├── bootstrap.*
│   ├── check.*
│   └── eval.*
│
├── .github/
│   ├── copilot-instructions.md
│   ├── instructions/
│   │   ├── backend.instructions.md
│   │   └── tests.instructions.md
│   ├── agents/
│   │   ├── implementer.md
│   │   ├── reviewer.md
│   │   └── test-engineer.md
│   ├── ISSUE_TEMPLATE/
│   ├── pull_request_template.md
│   └── workflows/
│
└── .mcp.json
```

### Core files

| File | Contents |
|---|---|
| **`README.md`** | Purpose, quick start, prerequisites, common commands and links to deeper documentation. |
| **`AGENTS.md`** | Primary agent onboarding: repository map, build/test commands, coding conventions, boundaries, definition of done and forbidden actions. Nested `AGENTS.md` files may provide subsystem-specific guidance. |
| **`ARCHITECTURE.md`** | Components, dependency rules, data flows, trust boundaries and diagrams. Explain *why* the architecture exists. |
| **`CONTRIBUTING.md`** | Human and agent workflow: branch strategy, commit rules, required checks, review process and release procedure. |
| **`SECURITY.md`** | Secret handling, vulnerability reporting, dependency policy and actions requiring human approval. |
| **`Makefile`** | Stable agent-friendly commands such as `make setup`, `make test`, `make check` and `make eval`. Avoid requiring agents to infer commands. |
| **`.env.example`** | Required environment variables with safe placeholders—never real credentials. |

### Agent implementation

| Directory | Contents |
|---|---|
| **`src/agents/orchestrator.*`** | Main execution loop, routing, stopping conditions, retry limits and handoffs. Start with one agent; introduce specialists only where evaluation shows a benefit. ([openai.com](https://openai.com/business/guides-and-resources/a-practical-guide-to-building-ai-agents/?utm_source=openai)) |
| **`src/agents/agents/`** | Small, specialized agent definitions with explicit goals, inputs, outputs and permitted tools. |
| **`src/agents/tools/`** | Typed, independently tested tool adapters. Separate read-only tools from state-changing tools. |
| **`src/agents/prompts/`** | Version-controlled instructions and prompt templates; avoid embedding large prompts throughout application code. |
| **`src/agents/guardrails/`** | Input/output validation, prompt-injection defenses, authorization checks, action-risk classification and human-approval gates. Layer guardrails rather than depending on one filter. ([openai.com](https://openai.com/business/guides-and-resources/a-practical-guide-to-building-ai-agents/?utm_source=openai)) |
| **`src/agents/schemas/`** | Structured input, output, tool-call and handoff contracts. |

### Quality and operations

| Directory | Contents |
|---|---|
| **`tests/`** | Deterministic unit, integration, contract and security tests. Tests should not depend unnecessarily on live model output. |
| **`evals/`** | Representative tasks, expected outcomes, graders, regression thresholds and failure cases. Run evaluations when changing models, prompts, tools or orchestration. ([openai.com](https://openai.com/index/evals-drive-next-chapter-of-ai/?utm_source=openai)) |
| **`docs/decisions/`** | Architecture Decision Records documenting important trade-offs. |
| **`docs/runbooks/`** | Procedures for deployment, rollback, incidents, cost spikes and degraded agent performance. |
| **`docs/threat-model.md`** | Assets, trust boundaries, prompt-injection paths, tool misuse, data leakage and mitigations. |
| **`.github/workflows/`** | CI for formatting, tests, security scans, evaluations and policy checks. State-changing deployment should use protected environments. |
| **`.mcp.json`** | Optional MCP server configuration. Pin trusted servers, apply least privilege and require confirmation for consequential tool calls. ([modelcontextprotocol.io](https://modelcontextprotocol.io/docs/tutorials/security/security_best_practices?utm_source=openai)) |

### Agent-specific customization

- **`.github/copilot-instructions.md`** — concise repository-wide GitHub Copilot instructions.
- **`.github/instructions/*.instructions.md`** — path-specific language, testing or security rules.
- **`.github/agents/*.md`** — specialized profiles such as implementer, reviewer and test engineer, each with minimal necessary tools. ([docs.github.com](https://docs.github.com/en/copilot/how-tos/configure-custom-instructions-in-your-ide/add-repository-instructions-in-your-ide?tool=visualstudio&utm_source=openai))
- Add **`CLAUDE.md`** or **`GEMINI.md`** only when vendor-specific behavior is required; keep `AGENTS.md` as the vendor-neutral source of truth where possible. GitHub currently recognizes these agent-instruction formats in several agent environments. ([docs.github.com](https://docs.github.com/en/copilot/reference/custom-instructions-support?utm_source=openai))

**Key principle:** agents should not have to guess how to understand, modify, verify or safely operate the repository. Encode those answers in short instructions, executable commands, typed interfaces, tests and evaluations.
