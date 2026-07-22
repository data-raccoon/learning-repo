# Vergleich von KI-Harnesses – Kurzfassung

## Kernaussage

Die untersuchten Werkzeuge sind keine austauschbaren Gesamtlösungen, sondern Schichten. LangGraph, Google ADK, Microsoft AutoGen/Agent Framework, OpenAI Agents SDK und CrewAI strukturieren Modell- und Toolinteraktionen. Temporal liefert Durable Execution, Inspect AI Evaluation, OPA Policyentscheidungen; Container, gVisor und Firecracker begrenzen Ausführungsrechte. Eine produktive Architektur kombiniert nur die benötigten Schichten. Produktnamen garantieren nichts: Entscheidend sind ein nicht umgehbarer Enforcement Point, persistenter Zustand, Idempotenz, harte Limits, Isolation und versionierte Evidence.

## Garantiert

Bei korrekter Integration sind begrenzte Aussagen möglich:

- Ein Graphexecutor kann ausschließlich deklarierte Kontrollkanten zulassen.
- Ein fail-closed Enforcer kann Aktionen ohne passende OPA- oder Code-Policyentscheidung verhindern.
- Temporal kann Workflowzustand unter Persistenz-, Replay- und Versionsannahmen nach Ausfällen rekonstruieren.
- LangGraph und vergleichbare Graph-Harnesses können Zustand und definierte Interrupts mit geeignetem persistentem Checkpointer wiederaufnehmen.
- Inspect AI kann bei fixierten Artefakten und deterministischem Scorer eine reproduzierbare Messprozedur liefern.
- Gehartete Container, gVisor oder Firecracker erzwingen die jeweils konfigurierte Ressourcen- und Zugriffsfläche innerhalb ihrer Systemannahmen.

## Garantiert nicht

- Kein Werkzeug garantiert fachliche Wahrheit, vollständige Prompt-Injection-Abwehr oder korrekte Modellentscheidungen.
- Session oder Checkpoint bedeutet weder transaktionalen Workflowzustand noch Exactly-once für externe Nebenwirkungen.
- SDK-Guardrails decken nicht automatisch Handoffs, Hosted Tools, Zwischenagenten oder alternative Toolpfade ab.
- OPA entscheidet nur; ohne lückenlosen Enforcer sperrt es keine Aktion.
- Sandboxes sind keine absolute Isolation und kontrollieren Egress nur bei entsprechender Konfiguration.
- Multi-Agent-Konsens und LLM-as-Judge bleiben heuristische beziehungsweise statistische Signale.

## Einsatzkriterien

- Sekundenkurzer, risikoarmer Ablauf: direkte API oder kleiner expliziter Graph statt unnötiger Multi-Agent-Komplexität.
- Sichtbarer Graph, HITL und Zustandsinspektion: LangGraph, ADK oder Agent Framework versionsspezifisch testen.
- Langlebiger Geschäftsprozess mit Timern und Recovery: Temporal außen, Agent-SDK nur in Activities; Idempotenz/Outbox separat lösen.
- Organisationsweite, auditierbare Regeln: OPA; für wenige lokale Regeln kann typisierter Code genügen.
- Eval-Release-Gate: Inspect AI mit eigenen risikobasierten Aufgaben, deterministischen Scorern und Unsicherheitsangaben.
- Untrusted Code: Isolationsstufe nach Bedrohung und Betriebsaufwand wählen; Egress, Secrets, Mounts und Limits immer separat absichern.

## Direkte Quellen

- [LangGraph: Persistence](https://docs.langchain.com/oss/python/langgraph/persistence)
- [Temporal: Workflow Execution](https://docs.temporal.io/workflow-execution)
- [OpenAI Agents SDK: Guardrails](https://openai.github.io/openai-agents-python/guardrails/)
- [Inspect AI](https://inspect.aisi.org.uk/)
- [Open Policy Agent](https://www.openpolicyagent.org/docs)
- [gVisor Security Model](https://gvisor.dev/docs/architecture_guide/security/)
