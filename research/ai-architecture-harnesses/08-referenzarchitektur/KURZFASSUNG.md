# Referenzarchitektur – Kurzfassung

## Kernaussage

Die empfohlene Architektur trennt einen deterministischen Kontrollkern von probabilistischen Modellblättern. Der Kernel besitzt Identität, Zustandsautomat, Budgets, Abbruchlogik, Policy-Enforcement, Freigaben und Commit-Rechte. Modelle klassifizieren, extrahieren, planen oder erzeugen lediglich typisierte Kandidaten; sie vergeben keine Rechte und führen keine Außenwirkung selbst aus. Externe Aktionen laufen ausschließlich über validierende, autorisierende und idempotente Tool-Adapter. Zusätzliche Agenten oder Modelle werden nur nach messbarem Mehrwert gegenüber einem einfachen Workflow zugelassen.

## Garantiert

Bei lückenloser, korrekter Umsetzung kann der Kernel erzwingen:

- nur erlaubte Zustandsübergänge und Toolpfade;
- harte Grenzen für Calls, Zeit, Kosten, Parallelität und Delegation;
- keinen schreibenden Adapteraufruf ohne aktuelle Allow-Entscheidung;
- keine Verwendung einer Freigabe für einen veränderten Payload;
- Verwerfen syntaktisch ungültiger Modellausgaben;
- Wiederaufnahme aus persistierter Historie unter Replay-, Store- und Versionsannahmen;
- höchstens einen fachlichen Effekt pro Retry nur dann, wenn Ziel oder Adapter atomare Idempotenz beziehungsweise eindeutige Reconciliation unterstützt.

## Garantiert nicht

- Schema-Konformität beweist keine Wahrheit oder sichere Geschäftsbedeutung.
- Persistenz oder Checkpointing erzeugt kein allgemeines Exactly-once über fremde Systeme.
- Sandboxing beseitigt nicht alle Kernel-, Hypervisor-, Seitenkanal- und Konfigurationsrisiken.
- Policy-as-Code schützt nicht vor falschen Regeln oder einem umgangenen Enforcement Point.
- Human Approval, LLM-Judges, Selbstkritik oder Modellmehrheiten sind keine Wahrheitsbeweise.
- Eine formale Spezifikation beweist ohne Conformance-Nachweis nicht den Produktivcode.

## Einsatzkriterien

- Fester Workflow als Default, wenn Schritte und Abschlussbedingungen vorab modellierbar sind; dynamische Agenten nur bei echtem offenen Suchraum, prüfbarem Outcome, Sandbox und harten Caps.
- Durable Execution bei langen Pausen, Human-in-the-loop, Retries, Kompensationen oder deploymentübergreifendem Resume; für kurze idempotente Einzelschritte genügt oft eine transaktionale Queue.
- Jedes Tool nach Identität, Zweck, Ziel, Datenklasse und Risiko autorisieren; Schreibtools deny-by-default und aus der Modellzone unerreichbar halten.
- Bei untrusted Code kurzlebige microVMs oder verstärkte Sandboxes, read-only Inputs, kein Secret im Gast und deny-by-default Egress einsetzen.
- Zweites Modell nur nach kontrolliertem A/B-Nachweis von Qualitätsgewinn gegenüber zusätzlichen Kosten, Latenz und Fehlerfläche.

## Direkte Quellen

- [Anthropic: Building Effective Agents](https://www.anthropic.com/engineering/building-effective-agents)
- [Temporal: Workflow Execution](https://docs.temporal.io/workflow-execution)
- [Open Policy Agent](https://www.openpolicyagent.org/docs)
- [MCP Authorization Specification](https://modelcontextprotocol.io/specification/2025-06-18/basic/authorization)
- [OWASP: Agentic AI Threats and Mitigations](https://genai.owasp.org/resource/agentic-ai-threats-and-mitigations/)
- [Firecracker Design](https://github.com/firecracker-microvm/firecracker/blob/main/docs/design.md)
