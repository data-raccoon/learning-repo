# Quellenregister

Stand und Abrufdatum aller Webquellen: **2026-07-22**. „Primärquelle“ bezeichnet hier offizielle Spezifikationen, Projekt-/Herstellerdokumentation oder einen Originalbeitrag der verantwortlichen Organisation; das ist kein unabhängiger Wirksamkeitsnachweis. Features von Frameworks und Cloud-Diensten sind zeitabhängig. Preprints sind nicht als peer-reviewte Evidenz zu lesen.

## Architektur, Workflows und Multi-Agent

### Anthropic

- **Building effective agents** — Anthropic; Erik S. und Barry Zhang. **Typ:** Primärquelle (Engineering-Beitrag). [URL](https://www.anthropic.com/engineering/building-effective-agents). **Relevanz/Grenze:** Trennt vorgegebene Workflows von dynamisch gesteuerten Agenten und empfiehlt einfache, testbare Muster, Ground Truth, Sandboxing und Stop Conditions. Erfahrungsbericht des Anbieters, keine formale oder unabhängige End-to-End-Garantie.
- **How we built our multi-agent research system** — Anthropic. **Typ:** Primärquelle (Engineering-Beitrag). [URL](https://www.anthropic.com/engineering/multi-agent-research-system). **Relevanz/Grenze:** Beschreibt Orchestrator-Worker, parallele Subagenten und Evaluation eines realen Research-Systems. Interne Ergebnisse sind auf Aufgabe, Modelle und Eval-Design begrenzt und belegen keine generelle Überlegenheit von Multi-Agent-Systemen.
- **Demystifying evals for AI agents** — Anthropic. **Typ:** Primärquelle (Engineering-Beitrag). [URL](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents). **Relevanz/Grenze:** Praktische Grundlage für mehrstufige Agent- und Trajectory-Evals; betont, dass kein einzelner Evaluationslayer alles abdeckt. Anbieterleitfaden, kein universeller Qualitätsbeweis.

### Microsoft, Google und LangGraph

- **AI Agent Orchestration Patterns** — Microsoft, Azure Architecture Center. **Typ:** Primärquelle (Architekturleitfaden). [URL](https://learn.microsoft.com/en-us/azure/architecture/ai-ml/guide/ai-agent-design-patterns). **Relevanz/Grenze:** Ordnet sequenzielle, parallele, Group-Chat- und Handoff-Muster ein und empfiehlt die niedrigste ausreichende Komplexität. Referenzmuster sind keine Laufzeitgarantien.
- **Termination** — Microsoft AutoGen. **Typ:** Primärquelle (Hersteller-/Projektdokumentation). [URL](https://microsoft.github.io/autogen/stable/user-guide/agentchat-user-guide/tutorial/termination.html). **Relevanz/Grenze:** Dokumentiert explizite und kombinierbare Abbruchbedingungen. Eine Abbruchbedingung begrenzt Ausführung, garantiert aber weder Zielerreichung noch fachliche Richtigkeit.
- **Graph-based workflows** — Google, Agent Development Kit (ADK). **Typ:** Primärquelle (Herstellerdokumentation). [URL](https://adk.dev/graphs/). **Relevanz/Grenze:** Belegt graphbasierte, explizite Kontrollpfade um KI-Schritte. Der Graph erzwingt den modellierten Ablauf, nicht korrekte Modellinhalte.
- **Workflows and Agents** — LangGraph/LangChain. **Typ:** Primärquelle (Projektdokumentation). [URL](https://langchain-ai.github.io/langgraph/tutorials/workflows/). **Relevanz/Grenze:** Zeigt feste Workflow- und dynamische Agentenmuster. Beispiele sind keine Zusage für Produktionszuverlässigkeit.
- **Persistence** — LangGraph/LangChain. **Typ:** Primärquelle (Projektdokumentation). [URL](https://langchain-ai.github.io/langgraph/concepts/persistence/). **Relevanz/Grenze:** Beschreibt Threads, Checkpoints, Wiederaufnahme, Human-in-the-Loop und Fault-Tolerance-Funktionen. In-Memory-Speicher ist nicht restart-durable; Persistenz allein sichert keine externe Nebenwirkung.
- **How to review tool calls (Functional API)** — LangGraph/LangChain. **Typ:** Primärquelle (Projektdokumentation). [URL](https://langchain-ai.github.io/langgraph/how-tos/review-tool-calls-functional/). **Relevanz/Grenze:** Veranschaulicht Tasks, Interrupts und Replay-Anforderungen bei Tool-Aufrufen. Garantien hängen von deterministischem Replay und korrekt gekapselten Nebenwirkungen ab.

### CrewAI und OpenAI Agents SDK

- **CrewAI Documentation** — CrewAI. **Typ:** Primärquelle (Herstellerdokumentation). [URL](https://docs.crewai.com/). **Relevanz/Grenze:** Dokumentiert Crews, Flows, Zustand, Persistenz und Guardrails. Herstellerangaben; keine unabhängige Garantie für Sicherheit, Richtigkeit oder Durability des Gesamtsystems.
- **Agents** — OpenAI Agents SDK. **Typ:** Primärquelle (Herstellerdokumentation). [URL](https://openai.github.io/openai-agents-python/agents/). **Relevanz/Grenze:** Dokumentiert Agenten, Tools, Handoffs und Laufzeitkonfiguration. Diese Bausteine erzwingen nicht automatisch sichere Delegation oder korrekte Ergebnisse.
- **Guardrails** — OpenAI Agents SDK. **Typ:** Primärquelle (Herstellerdokumentation). [URL](https://openai.github.io/openai-agents-python/guardrails/). **Relevanz/Grenze:** Beschreibt Input-, Output- und Tool-Guardrails sowie deren Ausführungsstellen. Wirksamkeit ist auf implementierte Prüfungen beschränkt; modellbasierte Guardrails bleiben probabilistisch.

## Durable Execution und Nebenwirkungen

- **Temporal Documentation** — Temporal Technologies. **Typ:** Primärquelle (Hersteller-/Projektdokumentation). [URL](https://docs.temporal.io/). **Relevanz/Grenze:** Grundlage für crash-resiliente, durable Workflow-Ausführung über persistierte Event History und Replay. Gilt unter Temporal-Betriebs- und Determinismusannahmen; externe Activities werden dadurch nicht automatisch exactly once.
- **Idempotency and retries** — Amazon Web Services, AWS Durable Execution SDK Developer Guide. **Typ:** Primärquelle (Herstellerdokumentation). [URL](https://docs.aws.amazon.com/durable-execution/patterns/best-practices/idempotency/). **Relevanz/Grenze:** Präzisiert At-least-once-/At-most-once-Semantik, Idempotenzschlüssel und Retry-Risiken; ausdrücklich keine pauschale Exactly-once-Aussage für den ganzen Workflow.

## Verträge, Policy und Supply Chain

- **Introducing Structured Outputs in the API** — OpenAI. **Typ:** Primärquelle (Herstellerbeitrag). [URL](https://openai.com/index/introducing-structured-outputs-in-the-api/). **Relevanz/Grenze:** Beschreibt constrained decoding und Schema-Adhärenz. Syntaktische Konformität garantiert weder Semantik noch Wahrheit oder Vollständigkeit.
- **Open Policy Agent Documentation** — Open Policy Agent/CNCF. **Typ:** Primärquelle (Projektdokumentation). [URL](https://www.openpolicyagent.org/docs). **Relevanz/Grenze:** Grundlage für deklarative Policies und externe Policy Decision Points. OPA entscheidet nur über bereitgestellte Fakten; Enforcement und vollständige Datenerfassung liegen beim integrierenden System.
- **Operations** — Open Policy Agent/CNCF. **Typ:** Primärquelle (Projektdokumentation). [URL](https://www.openpolicyagent.org/docs/operations). **Relevanz/Grenze:** Dokumentiert Betriebs- und Readiness-Aspekte. Fail-open oder fail-closed wird vom Enforcer bestimmt, nicht durch OPA allein garantiert.
- **Decision Logs** — Open Policy Agent/CNCF. **Typ:** Primärquelle (Projektdokumentation). [URL](https://www.openpolicyagent.org/docs/management-decision-logs). **Relevanz/Grenze:** Beschreibt auditierbare Entscheidungslogs und Maskierung. Logs belegen protokollierte Entscheidungen, nicht die Vollständigkeit aller Systemhandlungen; sensible Felder müssen aktiv geschützt werden.
- **SLSA v1.0: Security Levels** — Supply-chain Levels for Software Artifacts (SLSA), OpenSSF. **Typ:** Primärquelle (Standardspezifikation). [URL](https://slsa.dev/spec/v1.0/levels). **Relevanz/Grenze:** Definiert steigende Anforderungen an Provenienz und Build-Integrität. Trifft keine Aussage über fachliche Korrektheit, Modellsicherheit oder Laufzeitverhalten.

## Authentisierung, Agentensicherheit und Isolation

### MCP und Threat Modeling

- **Authorization** (MCP Specification, Revision 2025-06-18) — Model Context Protocol. **Typ:** Primärquelle (Protokollspezifikation). [URL](https://modelcontextprotocol.io/specification/2025-06-18/basic/authorization). **Relevanz/Grenze:** Normative Basis für OAuth, Audience Binding, Tokenvalidierung und das Verbot von Token-Passthrough. Korrekte Implementierung und sichere Deployment-Konfiguration bleiben Voraussetzungen.
- **Security Best Practices** — Model Context Protocol. **Typ:** Primärquelle (Sicherheitsleitfaden). [URL](https://modelcontextprotocol.io/docs/tutorials/security/security_best_practices). **Relevanz/Grenze:** Behandelt Confused Deputy, Consent, Tokendiebstahl und Audit-Trails. Empfehlungen reduzieren Risiken, beweisen aber keine vollständige Protokoll- oder Anwendungssicherheit.
- **Agentic AI – Threats and Mitigations** — OWASP GenAI Security Project, Agentic Security Initiative. **Typ:** Primärquelle (Community-Sicherheitsleitfaden). [URL](https://genai.owasp.org/resource/agentic-ai-threats-and-mitigations/). **Relevanz/Grenze:** Liefert ein Threat-Model für Tool Misuse sowie Goal-, Memory-, Privilege- und Inter-Agent-Risiken. Taxonomie und Mitigations sind kein Zertifikat und keine Vollständigkeitsgarantie.

### Sandbox-Techniken

- **gVisor Documentation** — gVisor Project. **Typ:** Primärquelle (Projektdokumentation). [URL](https://gvisor.dev/docs/). **Relevanz/Grenze:** Dokumentiert eine Sandbox mit Userspace Application Kernel und ihren Betriebsmodi. Isolation hängt von Konfiguration, Plattform und unterstützten Systemaufrufen ab.
- **Security Model** — gVisor Project. **Typ:** Primärquelle (Projektdokumentation). [URL](https://gvisor.dev/docs/architecture_guide/security/). **Relevanz/Grenze:** Erklärt die Reduktion direkter Host-Kernel-Interaktion und das Sicherheitsmodell. Reduzierte Angriffsfläche ist keine Beseitigung aller Exploits oder Seitenkanäle.
- **Firecracker Design** — Firecracker Project/Amazon Web Services. **Typ:** Primärquelle (Projektdesign). [URL](https://github.com/firecracker-microvm/firecracker/blob/main/docs/design.md). **Relevanz/Grenze:** Beschreibt KVM-microVMs, seccomp, cgroups, Namespaces, Jailer und Defense in Depth. Die tatsächliche Isolation setzt korrektes Host-, Kernel- und Jailer-Setup voraus.

## Evaluation, Observability und Risikomanagement

- **Inspect AI** — UK AI Security Institute; GitHub-Repository. **Typ:** Primärquelle (Open-Source-Projekt). [URL](https://github.com/UKGovernmentBEIS/inspect_ai). **Relevanz/Grenze:** Implementierungsquelle für reproduzierbare Evals, Scorer, Logs und Sandboxes. Reproduzierbarkeit hängt von versionierten Modellen, Daten, Abhängigkeiten und Umgebungen ab.
- **Inspect AI Documentation** — UK AI Security Institute. **Typ:** Primärquelle (Projektdokumentation). [URL](https://inspect.aisi.org.uk/). **Relevanz/Grenze:** Dokumentiert Eval-Aufgaben, Solver, Scorer, Logs und Sandbox-Integration. Das Framework garantiert nicht die Validität eines gewählten Eval-Satzes oder Scorers.
- **Gen AI Attributes** — OpenTelemetry. **Typ:** Primärquelle (Spezifikation/Registry). [URL](https://opentelemetry.io/docs/specs/semconv/registry/attributes/gen-ai/). **Relevanz/Grenze:** Standardisiert Attribute für GenAI-Telemetrie. Der verlinkte Registry-Stand weist auf eine Migration hin; Stabilitätsstatus prüfen. Tool-Argumente, Ergebnisse und Instruktionen können sensible Daten enthalten.
- **AI Risk Management Framework** — National Institute of Standards and Technology (NIST). **Typ:** Primärquelle (staatlicher Rahmen). [URL](https://www.nist.gov/itl/ai-risk-management-framework). **Relevanz/Grenze:** Strukturiert Risikomanagement in Govern, Map, Measure und Manage. Organisatorischer Rahmen, keine Runtime-Garantie oder Produktzertifizierung.
- **Artificial Intelligence Risk Management Framework: Generative Artificial Intelligence Profile (NIST AI 600-1)** — NIST. **Typ:** Primärquelle (staatliche Publikation). [URL](https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.600-1.pdf). **Relevanz/Grenze:** Konkretisiert den AI RMF für generative KI und zugehörige Risiken. Profilempfehlungen müssen in prüfbare Kontrollen übersetzt werden und garantieren allein keine Risikobeherrschung.

## Formale Methoden

- **Specifying and Verifying Systems With TLA+** — Leslie Lamport. **Typ:** Primärquelle (Originalaufsatz des Methodenautors). [URL](https://lamport.org/pubs/spec-and-verifying.pdf). **Relevanz/Grenze:** Einführung in Spezifikation, Safety/Liveness und Verifikation mit TLA+. Beweise und Model Checking gelten für das Modell; die Übereinstimmung von Modell und Implementierung muss separat abgesichert werden.
- **MCMAS: an open-source model checker for the verification of multi-agent systems** — Alessio Lomuscio, Hongyang Qu und Franco Raimondi; *International Journal on Software Tools for Technology Transfer*. **Typ:** Peer Review. [URL](https://link.springer.com/article/10.1007/s10009-015-0378-x). **Relevanz/Grenze:** Modellprüfung zeitlicher, epistemischer und strategischer Eigenschaften von Multi-Agent-Systemen. Endliche Abstraktion und State-Space-Explosion begrenzen Reichweite und Skalierbarkeit.

## Peer-reviewte und wissenschaftliche Gegenprüfung

- **Should we be going MAD? A Look at Multi-Agent Debate Strategies for LLMs** — Andries Petrus Smit, Nathan Grinsztajn, Paul Duckworth, Thomas D. Barrett und Arnu Pretorius; ICML 2024, PMLR 235. **Typ:** Peer Review. [URL](https://proceedings.mlr.press/v235/smit24a.html). **Relevanz/Grenze:** Vergleicht Multi-Agent Debate mit anderen Prompt-/Ensemble-Strategien und warnt vor pauschaler Überlegenheit. Ergebnisse gelten für untersuchte Aufgaben, Modelle und Abstimmungen.
- **Multi-Grained Specifications for Distributed System Model Checking and Verification** — Lingzhi Ouyang, Xudong Sun, Ruize Tang, Yu Huang, Madhav Jivrajani, Xiaoxing Ma und Tianyin Xu; EuroSys 2025. **Typ:** Peer Review. [URL](https://doi.org/10.1145/3689031.3696069). **Relevanz/Grenze:** Untersucht TLA+-Modelle, Model-Code-Conformance und Granularitäts-/State-Space-Trade-offs an verteilten Systemen. Übertragbarkeit auf LLM-Harnesses erfordert eine eigene, kontrollrelevante Abstraktion.
- **Why Do Multi-Agent LLM Systems Fail?** — Mert Cemri et al. **Typ:** Preprint (arXiv:2503.13657). [URL](https://arxiv.org/abs/2503.13657). **Relevanz/Grenze:** Entwickelt MAST, eine empirische Taxonomie von Spezifikations-, Koordinations-, Verifikations- und Terminierungsfehlern. Preprint; Taxonomie und untersuchte Frameworks/Aufgaben sind nicht notwendig vollständig oder allgemein gültig.
- **Generating Structured Outputs from Language Models: Benchmark and Studies** — Saibo Geng, Hudson Cooper, Michał Moskal, Samuel Jenkins, Julian Berman, Nathan Ranchin, Robert West, Eric Horvitz und Harsha Nori. **Typ:** Preprint (arXiv:2501.10868). [URL](https://arxiv.org/abs/2501.10868). **Relevanz/Grenze:** Benchmarkt constrained-decoding-Ansätze hinsichtlich Compliance, Abdeckung, Effizienz und Qualität. Preprint; Schema-Compliance bleibt von semantischer Korrektheit getrennt und Ergebnisse altern mit Framework-Versionen.

## Ergänzende Quellen aus den Langdokumenten

### Workflow-, Agenten- und Framework-Details

- **Workflow Agents** — Google, Agent Development Kit (ADK). **Typ:** Primärquelle (Herstellerdokumentation). [URL](https://adk.dev/agents/workflow-agents/). **Relevanz/Grenze:** Dokumentiert sequenzielle, parallele und Loop-Workflow-Agenten. Die Kontrollstruktur begrenzt Pfade, garantiert aber keine korrekten Modellentscheidungen innerhalb eines Schritts.
- **Persistence** und **Interrupts** — LangGraph/LangChain. **Typ:** Primärquelle (Projektdokumentation). [Persistence](https://docs.langchain.com/oss/python/langgraph/persistence), [Interrupts](https://docs.langchain.com/oss/python/langgraph/interrupts). **Relevanz/Grenze:** Aktuelle Dokumentationspfade für Checkpointer, Threads, Resume und Human-in-the-Loop. Resume kann Knotencode erneut ausführen; Nebenwirkungen vor Interrupts müssen deshalb replay-sicher sein.
- **Microsoft Agent Framework** und **Migration Guide: From AutoGen** — Microsoft. **Typ:** Primärquelle (Herstellerdokumentation). [Overview](https://learn.microsoft.com/en-us/agent-framework/overview/), [Migration Guide](https://learn.microsoft.com/en-us/agent-framework/migration-guide/from-autogen/). **Relevanz/Grenze:** Beschreibt Agent Framework als Nachfolger von AutoGen/Semantic Kernel sowie typisierte Workflows, Checkpointing und HITL. Reifegrad und Ausführungsmodell sind versionsabhängig; dokumentierte Features sind keine End-to-End-Zusage.
- **Handoff orchestration** — Microsoft, Azure Architecture Center. **Typ:** Primärquelle (Architekturleitfaden). [URL](https://learn.microsoft.com/en-us/azure/architecture/ai-ml/guide/ai-agent-design-patterns#handoff-orchestration). **Relevanz/Grenze:** Vertieft dynamische Übergaben, Fehlrouting und Schleifenrisiken. Das Muster ist eine Entwurfshilfe, kein Beleg für korrekte Handoffs.
- **Handoffs** und **Sessions** — OpenAI Agents SDK. **Typ:** Primärquelle (Herstellerdokumentation). [Handoffs](https://openai.github.io/openai-agents-python/handoffs/), [Sessions](https://openai.github.io/openai-agents-python/sessions/). **Relevanz/Grenze:** Dokumentiert Agentenübergaben und persistierbare Gesprächshistorie. Weder Übergabe noch Session-Speicherung garantieren semantische Konsistenz, sichere Berechtigungsvererbung oder exactly-once Nebenwirkungen.
- **Flows** — CrewAI. **Typ:** Primärquelle (Herstellerdokumentation). [URL](https://docs.crewai.com/en/concepts/flows). **Relevanz/Grenze:** Dokumentiert Routing, Zustand, Persistenz und Resume in Flows. Aussagen sind versionsabhängige Herstellerangaben; Commit-, Retry- und Store-Semantik müssen separat getestet werden.

### Durable Execution im Detail

- **What is Temporal?** — Temporal Technologies. **Typ:** Primärquelle (Herstellerdokumentation). [URL](https://docs.temporal.io/temporal). **Relevanz/Grenze:** Erläutert das Ausführungsmodell und die Positionierung der Temporal-Plattform. Überblicksdokumentation ersetzt keine Prüfung konkreter Persistenz-, Cluster- und Failure-Domain-Annahmen.
- **Workflow Execution** und **Replay** — Temporal Technologies. **Typ:** Primärquelle (Herstellerdokumentation). [Workflow Execution](https://docs.temporal.io/workflow-execution), [Replay-Abschnitt](https://docs.temporal.io/workflow-execution#replays). **Relevanz/Grenze:** Beschreibt Event History, Wiederaufnahme und Replay von Workflowcode. Die Aussage betrifft Workflowzustand unter Betriebsannahmen, nicht automatisch einmalige externe Effekte.
- **Workflow Definition: Deterministic constraints** — Temporal Technologies. **Typ:** Primärquelle (Herstellerdokumentation). [URL](https://docs.temporal.io/workflow-definition#deterministic-constraints). **Relevanz/Grenze:** Definiert Determinismusanforderungen für replay-kompatiblen Workflowcode. Inkompatible Codeänderungen und ungekapselte Nichtdeterministik können die Bedingung verletzen.
- **Activities** — Temporal Technologies. **Typ:** Primärquelle (Herstellerdokumentation). [URL](https://docs.temporal.io/activities). **Relevanz/Grenze:** Ordnet nichtdeterministische und externe Arbeit Activities zu und behandelt Wiederholbarkeit. Activities können erneut laufen; Idempotenz oder Deduplikation bleibt Anwendungsverantwortung.

### Verträge, Admission und Identität

- **What is a schema?** — JSON Schema Project. **Typ:** Primärquelle (Standards-/Projektdokumentation). [URL](https://json-schema.org/understanding-json-schema/basics). **Relevanz/Grenze:** Erläutert die Grundsemantik von JSON Schema, einschließlich des uneingeschränkten leeren Schemas. Ein gültiges Schema prüft nur formulierte Strukturbedingungen, nicht fachliche Wahrheit.
- **Admission Controllers Reference** — Kubernetes Project/CNCF. **Typ:** Primärquelle (Projektdokumentation). [URL](https://kubernetes.io/docs/reference/access-authn-authz/admission-controllers/). **Relevanz/Grenze:** Belegt Admission nach Authentisierung/Autorisierung und Ablehnungssemantik. Die Kontrolle gilt nur für Änderungen, die den API-Server und die aktivierten Controller tatsächlich durchlaufen.
- **Least Privilege** — National Institute of Standards and Technology, Computer Security Resource Center. **Typ:** Primärquelle (staatliches Glossar). [URL](https://csrc.nist.gov/glossary/term/least_privilege). **Relevanz/Grenze:** Definiert die Beschränkung auf notwendige Ressourcen und Autorisierungen. Die Definition liefert kein fertiges Capability-Modell und beweist nicht dessen korrekte Umsetzung.

### Isolation und Hostbetrieb

- **Performance Guide** — gVisor Project. **Typ:** Primärquelle (Projektdokumentation). [URL](https://gvisor.dev/docs/architecture_guide/performance/). **Relevanz/Grenze:** Beschreibt Performance-Eigenschaften und workloadabhängigen Overhead von gVisor. Messwerte und Trade-offs sind plattform- und workloadabhängig und keine Sicherheitsgarantie.
- **Production Host Setup Recommendations** — Firecracker Project/Amazon Web Services. **Typ:** Primärquelle (Projektdokumentation). [URL](https://github.com/firecracker-microvm/firecracker/blob/main/docs/prod-host-setup.md). **Relevanz/Grenze:** Dokumentiert Voraussetzungen und Härtung des Produktionshosts, einschließlich Jailer-Vertrauensgrenzen. Empfehlungen wirken nur bei korrektem Host-, Pfad-, Kernel- und Netzwerk-Setup.

### Evaluation, Telemetrie und SLOs

- **5 AI RMF Core** — National Institute of Standards and Technology, AI Resource Center. **Typ:** Primärquelle (staatlicher Rahmen). [URL](https://airc.nist.gov/airmf-resources/airmf/5-sec-core/). **Relevanz/Grenze:** Konkretisiert Govern, Map, Measure und Manage sowie fortlaufende Test-, Evaluations-, Verifikations- und Validierungsaktivitäten. Freiwilliger Organisationsrahmen, keine Runtime-Garantie.
- **Semantic Conventions for Generative AI** — OpenTelemetry. **Typ:** Primärquelle (Spezifikation). [URL](https://opentelemetry.io/docs/specs/semconv/gen-ai/). **Relevanz/Grenze:** Definiert gemeinsame Telemetriesemantik für GenAI-Operationen. Die Konvention ist in Entwicklung und garantiert weder vollständige Instrumentierung noch datenschutzgerechte Inhaltsaufzeichnung.
- **Inside the LLM Call: GenAI Observability with OpenTelemetry** — James Newton-King (Microsoft), OpenTelemetry. **Typ:** Primärquelle (Projektbeitrag). [URL](https://opentelemetry.io/blog/2026/genai-observability/). **Relevanz/Grenze:** Zeigt erfasste Modell-, Token-, Agenten- und Toolsignale und warnt vor sensiblen Inhalten. Ein Demonstrationsbeitrag; sichtbare Telemetrie beweist nicht ihre Vollständigkeit.
- **Service Level Objectives** — Chris Jones, John Wilkes und Niall Murphy mit Cody Smith; Google Site Reliability Engineering. **Typ:** Primärquelle (Praxisleitfaden). [URL](https://sre.google/sre-book/service-level-objectives/). **Relevanz/Grenze:** Definiert SLI/SLO/SLA und motiviert realistische Ziele. SLOs sind Mess- und Steuerungsinstrumente; sie erzwingen keine Safety-Invariante.

### Zusätzliche wissenschaftliche Gegenprüfung

- **Judging the Judges: A Systematic Study of Position Bias in LLM-as-a-Judge** — Lin Shi, Chiyu Ma, Wenhua Liang, Xingjian Diao, Weicheng Ma und Soroush Vosoughi; IJCNLP-AACL 2025. **Typ:** Peer Review. [URL](https://aclanthology.org/2025.ijcnlp-long.18/). **Relevanz/Grenze:** Untersucht Positionsbias in paarweisen und listenweisen LLM-Judges. Ergebnisse gelten für die untersuchten Modelle, Aufgaben und Metriken und machen LLM-Judges nicht generell unbrauchbar oder zuverlässig.
- **Justice or Prejudice? Quantifying Biases in LLM-as-a-Judge** — Jiayi Ye, Yanbo Wang, Yue Huang, Dongping Chen, Qihui Zhang, Nuno Moniz, Tian Gao, Werner Geyer, Chao Huang, Pin-Yu Chen, Nitesh V. Chawla und Xiangliang Zhang; ICLR 2025. **Typ:** Peer Review. [URL](https://proceedings.iclr.cc/paper_files/paper/2025/file/fdca08d371e4b6c031397909e20043bd-Paper-Conference.pdf). **Relevanz/Grenze:** Quantifiziert mehrere Bias-Klassen, darunter Verbosity und Self-Preference. Empirische Befunde sind auf die getesteten Modelle, Datensätze und Perturbationen begrenzt.
- **Uncertainty in runtime verification: A survey** — Rania Taleb, Sylvain Hallé und Raphaël Khoury; *Computer Science Review* 50 (2023), 100594. **Typ:** Peer Review. [URL](https://doi.org/10.1016/j.cosrev.2023.100594). **Relevanz/Grenze:** Systematisiert Unsicherheit bei Runtime Verification, insbesondere in beobachteten Ereignissen und Monitorurteilen. Ein Monitor kann nur über die spezifizierten Eigenschaften und tatsächlich erfassten Traces urteilen.

### Alternativer Primärlink

- **Specifying and Verifying Systems With TLA+** — Leslie Lamport. **Typ:** Primärquelle (Originalaufsatz des Methodenautors). [Alternativer URL-Host](https://lamport.azurewebsites.net/pubs/spec-and-verifying.pdf). **Relevanz/Grenze:** Inhaltlich dieselbe TLA+-Quelle wie oben; der zusätzliche Link wird registriert, weil Langdokumente diesen Host verwenden. Verifikation des Modells schließt die Modell-Code-Lücke nicht.

## Zitier- und Evidenzregeln für diese Dokumentation

1. Eine Framework-Funktion wird mit der jeweiligen Primärquelle belegt und als zeitabhängig markiert.
2. Herstellerinterne Evals werden als solche benannt und nicht ohne unabhängige Gegenprüfung generalisiert.
3. Peer Review erhöht die wissenschaftliche Belastbarkeit, ersetzt aber nicht die Prüfung von Scope, Annahmen und externer Validität.
4. Preprints werden ausdrücklich als Preprints zitiert.
5. Aus Mechanismen werden nur die Eigenschaften abgeleitet, die der Enforcer tatsächlich kontrolliert; End-to-End-Garantien benötigen ein explizites Garantie-Ledger.
