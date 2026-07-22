# Workflow-first – Kurzfassung

## Kernaussage

Der belastbare Default für produktive KI-Systeme ist ein deterministischer Workflow, in dem Modelle nur eng begrenzte, probabilistische Teilschritte ausführen. Code kontrolliert Zustand, Übergänge, Berechtigungen, Budgets, Freigaben und Commit. Ein autonomer Agent ist erst gerechtfertigt, wenn die Schrittfolge nicht sinnvoll vorab modellierbar ist und Evaluationen einen messbaren Vorteil gegenüber Single-Call, Single-Agent oder festem Workflow zeigen.

## Garantiert

Unter der Voraussetzung eines zentralen Stores, atomarer Übergänge und eines nicht umgehbaren Kontrollpfads kann der Harness erzwingen:

- nur definierte Zustandsübergänge werden übernommen;
- Hochrisiko-Tools laufen erst nach einer an den konkreten Payload gebundenen Freigabe;
- nach Budgetende startet kein neuer Dispatch;
- Schleifen enden nach einer festen Zahl von Schritten oder einer Deadline;
- Tool-Rechte bleiben auf den jeweiligen Schritt beschränkt.

Wiederaufnahme nach einem Crash ist nur konditional garantiert: Checkpoints, kompatible Versionen und korrekte Replay-Logik müssen vorhanden sein.

## Garantiert nicht

Ein fester Ablauf macht Modellantworten nicht wahr. Schema-konformes Routing beweist keine fachlich richtige Route. Ein erfolgreicher Tool-Return beweist nicht automatisch die beabsichtigte externe Wirkung. Selbstkritik, Voting und LLM-Evaluator bleiben heuristisch, solange kein externer Test ihre Aussage bestätigt. Auch ein Human-in-the-Loop garantiert keine richtige Entscheidung; er schafft einen verantworteten Kontrollpunkt.

## Einsatzkriterien

Ein fester Workflow passt bei bekannten Phasen, klaren Gates, Compliance-, Audit- oder Kostenanforderungen und irreversiblen Nebenwirkungen. Ein begrenzter Agent passt bei offenen Such- oder Reparaturschritten, wenn Ground Truth abfragbar, Fortschritt prüfbar, Fehler reversibel und der Wirkungsraum klein sind. Multi-Agent sollte kein Default sein: Koordination, Kontextübergaben und paralleler Zustand schaffen eigene Fehlerdomänen.

## Quellen

- [Anthropic: Building Effective Agents](https://www.anthropic.com/engineering/building-effective-agents)
- [Microsoft Azure Architecture Center: Agent orchestration patterns](https://learn.microsoft.com/en-us/azure/architecture/ai-ml/guide/ai-agent-design-patterns)
- [Google ADK: Graph-based agent workflows](https://adk.dev/graphs/)
- [LangGraph: Workflows and agents](https://langchain-ai.github.io/langgraph/tutorials/workflows/)
