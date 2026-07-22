# Einführungsplan – Kurzfassung

## Kernaussage

KI-Systeme sollten risikogesteuert vom einfachsten tragfähigen Aufbau zu komplexeren Architekturen wachsen. Ausgangspunkt ist ein messbarer, read-only Single Call; erst ein belegter Engpass rechtfertigt deterministische Workflows, schreibende Tools, Durable Execution, Multi-Agent-/Multi-Modell-Verfahren oder formale Absicherung. Jede Stufe endet mit einem technischen Gate: einem versionierten Evidenzpaket aus Anforderungen, deterministischen Negativtests, statistischen Evals, Betriebsmetriken, Threat Model und praktisch erprobtem Rollback.

Der Reifeweg umfasst sieben Stufen:

1. **Stufe 0:** Problem, Nicht-KI-Baseline, Daten und Risiken messbar machen.
2. **Stufe 1:** gehärteter, schema-validierter Single Call ohne Schreibrechte.
3. **Stufe 2:** expliziter Zustandsautomat mit ausschließlich read-only Tools und zentraler Policy-Durchsetzung.
4. **Stufe 3:** schreibende Aktionen über `propose → validate → authorize → approve → commit → verify`, Idempotenz und Reconciliation.
5. **Stufe 4:** persistierte Event-Historie, deterministischer Replay und dauerhafte Freigabewartepunkte.
6. **Stufe 5:** Multi-Agent/Multi-Modell nur bei reproduzierbarem Mehrwert gegenüber der einfacheren Baseline.
7. **Stufe 6:** formale Invarianten, Runtime-Conformance, Isolation und Supply-Chain-Kontrollen für eng begrenzte Hochrisikopfade.

## Garantiert

Bei exklusiven, nicht umgehbaren Enforcern lassen sich im definierten Scope technisch erzwingen:

- nur schema-konforme Daten erreichen nachgelagerte Komponenten;
- nach Budget- oder Deadline-Erreichen werden keine neuen Aufrufe gestartet;
- nur erlaubte Zustandsübergänge, Tools und Ziele sind erreichbar;
- nach einer Freigabe veränderte Payloads werden anhand ihrer Bindung abgewiesen;
- unbekannte Zustände oder Policy-Ausfälle enden fail-closed;
- formalisierte Invarianten gelten im untersuchten Modell, sofern Zustandsraum und Annahmen abgedeckt sind.

Recovery, Deduplizierung und höchstens eine sichtbare Außenwirkung sind nur unter dokumentierten Infrastruktur- und Adapterannahmen garantierbar.

## Garantiert nicht

- Schema-Konformität bedeutet weder Wahrheit noch fachliche Korrektheit.
- Evals, Canary, SLOs oder LLM-Judges garantieren keinen korrekten Einzelfall.
- Persistenz oder Replay erzeugen keine automatische Exactly-once-Wirkung.
- menschliche Freigabe verhindert keine Fehlentscheidung.
- Multi-Agent-Konsens ist kein Wahrheitsbeweis.
- Model Checking, Sandboxen, SLSA oder NIST-Rahmen zertifizieren nicht das Gesamtsystem.

## Einsatzkriterien

Eine höhere Stufe ist nur sinnvoll, wenn die aktuelle Architektur einen benannten Engpass zeigt: mehrere kontrollierte Schritte erfordern Stufe 2, notwendige Außenwirkungen Stufe 3, lange Unterbrechungen und Recovery Stufe 4, nachgewiesene Vorteile aus Spezialisierung oder Parallelität Stufe 5 und prüfbare Invarianten eines klar abgegrenzten Hochrisikopfads Stufe 6. Ohne solche Evidence bleibt die einfachere Vorstufe der Produktionsstandard. Unautorisierte Nebenwirkungen, fehlende Audit-Korrelation, kritische Safety-Regressionen, ungeklärte Doppelwirkungen, Secrets im Kontext oder ein Enforcer-Bypass erzwingen Rollout-Stopp beziehungsweise Rückfall auf die sichere Vorstufe.

## Direkte Quellen

- [NIST AI Risk Management Framework](https://www.nist.gov/itl/ai-risk-management-framework)
- [Anthropic: Building Effective Agents](https://www.anthropic.com/engineering/building-effective-agents)
- [Open Policy Agent Documentation](https://www.openpolicyagent.org/docs)
- [MCP Authorization Specification](https://modelcontextprotocol.io/specification/2025-06-18/basic/authorization)
- [Temporal: Workflow Execution](https://docs.temporal.io/workflow-execution)
- [Leslie Lamport: Specifying Systems and Verifying Specifications](https://lamport.org/pubs/spec-and-verifying.pdf)
