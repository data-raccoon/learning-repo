# Durable Execution – Kurzfassung

## Kernaussage

Durable Execution entkoppelt einen logischen KI-Run vom Lebenszyklus eines Prozesses. Checkpoints oder eine Event History speichern Entscheidungen und Ergebnisse, sodass ein anderer Worker nach Crash, Deployment, Timeout oder menschlicher Wartephase fortsetzen kann. Ein gespeicherter Chatverlauf allein reicht dafür nicht: Workflow-Code, Activities, Versionierung, Retries und externe Nebenwirkungen brauchen definierte Semantik.

## Garantiert

Unter den Annahmen eines verfügbaren, dauerhaften Stores, kompatibler Workflow-Versionen und deterministischen Replays kann ein Run ab dem gespeicherten Zustand wiederaufgenommen werden. Atomare Zustandsfortschreibung verhindert, dass mehrere Worker denselben Fortschritt committen. Harte Retry-, Zeit- und Versuchslimits begrenzen den kontrollierten Ausführungspfad.

Für externe Writes ist höchstens eine fachliche Wirkung nur erreichbar, wenn der Zieladapter einen stabilen Idempotency Key atomar und dauerhaft dedupliziert. Transactional Outbox/Inbox kann lokales Commit und Nachrichtenerzeugung koppeln; Sagas können bereits erfolgte, nicht atomar rückrollbare Schritte durch fachliche Kompensationen behandeln.

## Garantiert nicht

Durable Execution bedeutet nicht automatisch „exactly once“. Ein Crash zwischen externer Wirkung und lokalem Commit kann einen Retry und damit eine doppelte Wirkung auslösen. Idempotenzschlüssel ohne atomare Speicherung, ausreichende Retention und Bindung an Payload sowie Empfänger genügen nicht. Kompensation ist kein Rollback: Sie kann scheitern oder die ursprüngliche Welt nicht vollständig wiederherstellen. Replay beweist außerdem weder fachliche Korrektheit noch Verfügbarkeit bei Ausfall des Persistenzsystems.

## Einsatzkriterien

Der Ansatz lohnt sich bei langen Läufen, menschlichen Freigaben, Timern, mehreren externen Systemen, hohen Wiederholungskosten oder Auditpflichten. Vor der Wahl sind RPO/RTO, deterministisch replaybare Teile, Activity-Grenzen, Idempotenz der Zielsysteme, Outbox-Transaktionen, zulässige Kompensationen, Versionsmigration und Datenaufbewahrung zu klären. Abnahme benötigt Fault Injection an jedem Commit-Fenster sowie Replay historischer Event-Historien.

## Quellen

- [Temporal: Documentation](https://docs.temporal.io/)
- [Temporal: Workflow Execution](https://docs.temporal.io/workflow-execution)
- [Temporal: Deterministic Constraints](https://docs.temporal.io/workflow-definition#deterministic-constraints)
- [Temporal: Activities](https://docs.temporal.io/activities)
- [AWS Durable Execution: Idempotency and retries](https://docs.aws.amazon.com/durable-execution/patterns/best-practices/idempotency/)
- [LangGraph: Persistence](https://langchain-ai.github.io/langgraph/concepts/persistence/)
