# Research-Brief: KI-Architektur und Harnesses mit technischen Garantien

Stand: 2026-07-22. Sprache aller Ergebnisdokumente: Deutsch.

## Auftrag

Erstelle eine belastbare, technologieoffene Architekturdokumentation. Unterscheide streng:

1. **deterministisch erzwingbar** (z. B. Schema, ACL, Budget, Zustandsautomat),
2. **unter expliziten Annahmen garantiert** (z. B. Durable Execution bei deterministischem Replay und idempotenten Activities),
3. **statistisch messbar** (Evals/SLOs),
4. **nur heuristisch** (Prompting, Selbstkritik, Mehrheitsentscheid).

Ein Harness umfasst den ausführenden Kontrollrahmen um Modelle: Routing, Zustandsführung, Tool-Grenzen, Validierung, Persistenz, Freigaben, Budgets, Telemetrie und Release-Gates. Keine Marketingaussage darf als End-to-End-Garantie dargestellt werden. Insbesondere garantiert syntaktisch gültiges JSON keine semantische Wahrheit; Persistenz garantiert keine Exactly-once-Nebenwirkung; ein Sandbox-Produkt beseitigt nicht alle Seitenkanäle oder Fehlkonfigurationen; LLM-as-Judge und Multi-Agent-Konsens sind keine Wahrheitsbeweise.

## Ergebnisartefakte und Ablagestruktur

- `README.md`: Einstieg, Navigationsindex, Kernaussage und Entscheidungsbaum.
- `00-garantie-taxonomie.md`: gemeinsame Begriffe, Annahmen, Garantie-Ledger und Failure Domains.
- Je ein Ordner `01-workflow-first/` bis `10-einfuehrungsplan/` mit:
  - `README.md`: vollständiges Ansatzdokument,
  - `KURZFASSUNG.md`: eigenständig lesbare Kurzfassung mit Direktquellen,
  - `beispiel/`: dependency-freie Referenzimplementierung, Tests und Ausführungsanleitung.
- `quellen.md`: kuratiertes Quellenregister mit Abrufdatum und Einordnung.
- `verify_examples.py`: zentraler Offline-Testlauf über alle Beispiele.

Die zehn Ansatz-Ordner behandeln Workflow-first, Multi-Agent/Multi-Modell, Durable Execution, Verträge/Policy-Gates, Sicherheit/Isolation, Evaluation/Observability, formale Methoden, die integrierte Referenzarchitektur, Harness-Conformance und den stufenweisen Einführungsplan.

Jedes Langdokument braucht: Kurzfassung am Anfang, Anwendungsbereich, technische Mechanismen, erreichbare Garantien samt Voraussetzungen, Nicht-Garantien/Failure Modes, Entscheidungskriterien, umsetzbare Checkliste und Inline-Quellenlinks.

## Verbindliche Recherchebasis

Primärquellen und offizielle Dokumentation:

- Anthropic, Building Effective Agents: https://www.anthropic.com/engineering/building-effective-agents — Workflows haben vorgegebene Codepfade; Agenten steuern dynamisch; einfach beginnen, Sandbox, Stop Conditions, Ground Truth.
- Anthropic, Multi-Agent Research System: https://www.anthropic.com/engineering/multi-agent-research-system — Orchestrator-Worker, parallele Subagenten, Evaluation.
- Anthropic, Demystifying Evals for AI Agents: https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents — mehrstufige Trajectory-Evals; kein einzelner Evaluationslayer deckt alles ab.
- Microsoft Azure Architecture Center, Agent orchestration patterns: https://learn.microsoft.com/en-us/azure/architecture/ai-ml/guide/ai-agent-design-patterns — niedrigste ausreichende Komplexität; sequenziell, parallel, group chat, handoff; Multi-Agent erhöht Kosten/Fehlermodi.
- Microsoft AutoGen termination: https://microsoft.github.io/autogen/stable/user-guide/agentchat-user-guide/tutorial/termination.html — explizite, kombinierbare Abbruchbedingungen.
- Google ADK graph workflows: https://adk.dev/graphs/ — deterministische Kontrollpfade um KI-Schritte.
- LangGraph workflows/agents: https://langchain-ai.github.io/langgraph/tutorials/workflows/ — feste Workflows versus dynamische Agenten.
- LangGraph persistence: https://langchain-ai.github.io/langgraph/concepts/persistence/ — Checkpoints, HITL, fault tolerance; In-Memory ist nicht restart-durable.
- LangGraph functional API/determinism: https://langchain-ai.github.io/langgraph/how-tos/review-tool-calls-functional/ — Side Effects als Tasks kapseln, Replay-Anforderungen.
- Temporal docs: https://docs.temporal.io/ — durable/crash-resilient execution durch persistierte Event History.
- AWS Durable Execution idempotency: https://docs.aws.amazon.com/durable-execution/patterns/best-practices/idempotency/ — at-least-once braucht Idempotenz; keine pauschale Exactly-once-Garantie.
- OpenAI Structured Outputs: https://openai.com/index/introducing-structured-outputs-in-the-api/ — constrained decoding/schema adherence; semantische Richtigkeit bleibt außerhalb.
- OpenAI Agents SDK: https://openai.github.io/openai-agents-python/agents/ und https://openai.github.io/openai-agents-python/guardrails/ — Tools, Handoffs, Sessions, Tracing/Guardrails; Tool-Guardrails für jeden Aufruf.
- CrewAI docs: https://docs.crewai.com/ — Crews versus Flows, State/Persistenz/Guardrails; Herstellerdokumentation, keine unabhängige Garantie.
- MCP Authorization 2025-06-18: https://modelcontextprotocol.io/specification/2025-06-18/basic/authorization — OAuth, audience binding, Access-Token-Validierung, Token-Passthrough verboten.
- MCP Security Best Practices: https://modelcontextprotocol.io/docs/tutorials/security/security_best_practices — confused deputy, per-client consent, Token-Diebstahl und Audit-Trail.
- OWASP Agentic AI Threats: https://genai.owasp.org/resource/agentic-ai-threats-and-mitigations/ — Threat Model, Tool Misuse, Goal/Memory/Privilege/Inter-Agent-Risiken.
- OPA docs: https://www.openpolicyagent.org/docs — deklarative Policies und externe Policy Decision Points.
- OPA operations: https://www.openpolicyagent.org/docs/operations — readiness, fail-open/fail-closed ist Entscheidung des Enforcers.
- OPA decision logs: https://www.openpolicyagent.org/docs/management-decision-logs — Audit-Daten, Maskierung sensibler Felder.
- gVisor docs/security: https://gvisor.dev/docs/ und https://gvisor.dev/docs/architecture_guide/security/ — Userspace application kernel, reduzierte Host-Kernel-Angriffsfläche, Kompatibilitäts- und Restrisikohinweise.
- Firecracker design: https://github.com/firecracker-microvm/firecracker/blob/main/docs/design.md — KVM/microVM, seccomp, cgroups, namespaces, jailer, defense in depth.
- Inspect AI: https://github.com/UKGovernmentBEIS/inspect_ai und https://inspect.aisi.org.uk/ — reproduzierbare Agent-Evals, Scorer, Logs, Sandboxes.
- OpenTelemetry GenAI semantic attributes: https://opentelemetry.io/docs/specs/semconv/registry/attributes/gen-ai/ — standardisierte Telemetrie; Tool-Argumente/-Resultate können sensitiv sein.
- SLSA levels: https://slsa.dev/spec/v1.0/levels — Provenienz und steigende Build-Integrität, keine Aussage über fachliche Korrektheit.
- NIST AI RMF: https://www.nist.gov/itl/ai-risk-management-framework und GenAI Profile https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.600-1.pdf — Govern/Map/Measure/Manage; organisatorischer Rahmen, keine Runtime-Garantie.
- TLA+ overview/paper: https://lamport.org/pubs/spec-and-verifying.pdf — Spezifikation von Safety/Liveness und Model Checking; Modell-Code-Lücke explizit machen.
- MCMAS paper: https://link.springer.com/article/10.1007/s10009-015-0378-x — Model Checking für Multi-Agent-Systeme; State-Space-Grenzen.

Peer-reviewed / wissenschaftliche Gegenprüfung:

- Smit et al., ICML 2024, Should we be going MAD?: https://proceedings.mlr.press/v235/smit24a.html — Multi-Agent-Debatte ist empirisch zu bewerten, nicht automatisch überlegen.
- Ouyang et al., EuroSys 2025: https://doi.org/10.1145/3689031.3696069 — TLA+ und Model-Code-Conformance, Granularitäts-/State-Space-Trade-off.
- MAST, Why Do Multi-Agent LLM Systems Fail?: https://arxiv.org/abs/2503.13657 — systematische Multi-Agent-Fehlermodi; Preprint entsprechend kennzeichnen.
- Generating Structured Outputs benchmark: https://arxiv.org/abs/2501.10868 — Schema-Compliance und Frameworkvergleich; Preprint entsprechend kennzeichnen.

## Architekturposition, die zu prüfen und sauber zu begründen ist

Der stärkste Default ist **deterministischer Kernel, probabilistische Blätter**:

- Code besitzt Zustandsautomat, Identität, Berechtigungen, Budgets, Zeitlimits, Retry- und Commit-Logik.
- Modelle dürfen innerhalb eng definierter Schritte klassifizieren, planen, Inhalte erzeugen oder Kandidaten vorschlagen.
- Jede externe Nebenwirkung passiert über einen policy-geprüften, idempotenten Tool-Adapter mit explizitem Commit bzw. menschlicher Freigabe bei hohem Risiko.
- Outputs werden syntaktisch erzwungen und semantisch durch deterministische Regeln/Tests geprüft.
- Durable State und append-only Ereignisse ermöglichen Resume und Audit; Geheimnisse/Reasoning werden minimiert bzw. redigiert.
- Multi-Agent oder Multi-Modell wird nur nach Eval-Nachweis gegenüber einer einfacheren Baseline zugelassen.

## Stil- und Qualitätsregeln

- Präzises, verständliches Deutsch; englische Fachbegriffe beim ersten Auftreten erklären.
- Aussage und Quelle unmittelbar verbinden; keine erfundenen Zahlen, Features oder Garantien.
- Bei Framework-Features den Stand als zeitabhängig markieren; Herstellerangaben von unabhängiger Evidenz unterscheiden.
- Tabellen nur, wenn sie echte Vergleiche erleichtern.
- Interne Links relativ und funktionsfähig.
- `RESEARCH_BRIEF.md` nicht verändern.
