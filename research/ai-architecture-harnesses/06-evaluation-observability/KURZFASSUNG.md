# Evaluation und Observability für KI-Harnesses – Kurzfassung

## Kernaussage

Evaluation misst, wie häufig ein konkretes KI-System unter definierten Bedingungen erfolgreich ist; Observability macht einzelne Ausführungen, Fehler und Verteilungen nachvollziehbar. Beides liefert belastbare Evidenz, aber keinen universellen Korrektheitsbeweis. Eine robuste Praxis kombiniert deterministische Outcome- und Policy-Prüfer, mehrere Trials für probabilistische Schritte, Trajectory-Evals, kalibrierte LLM-Judges, menschliche Stichproben und Produktions-SLIs. Geprüft werden soll bevorzugt der reale Endzustand, nicht die Selbstaussage des Modells.

## Garantiert

- Ein deterministisches Release-Gate verhindert über den abgedeckten Releasepfad die Freigabe, wenn eine kodierte Assertion fehlschlägt.
- Ein nicht umgehbarer Runtime-Gate kann eine konkrete, verbotene Tool-Aktion blockieren.
- Vollständig instrumentierte Traces mit stabilen Run-, Task- und Commit-IDs erlauben die Rekonstruktion der tatsächlich erfassten Ereignisse.
- Ein SLO definiert eine messbare Ziel- und Eskalationsregel für ein festgelegtes Zeitfenster.

Diese Aussagen gelten nur bei korrekter Implementierung, vollständiger Instrumentierung und passend spezifizierten Regeln.

## Garantiert nicht

- Hohe Eval-Scores beweisen weder Erfolg auf unbekannten Eingaben noch Verhalten nach Modell-, Daten- oder Umgebungsdrift.
- LLM-as-Judge ist kein Verifier: Positions-, Stil-, Self-Preference- und Rubrikbias bleiben möglich; Judge-Konsens ist keine Wahrheit.
- Ein grüner Canary schließt seltene oder segmentierte Fehler nicht aus.
- Tracing garantiert keine Vollständigkeit, wenn Sampling, Exportausfälle oder alternative Toolpfade Ereignisse verbergen.
- Redaction garantiert nicht, dass sensible Inhalte nie in Anbieterlogs, Fehlertexten oder Drittsystemen landen.

## Einsatzkriterien

- Maschinenprüfbarer Endzustand vorhanden: deterministischen Outcome-Grader einsetzen.
- Prozess selbst sicherheitsrelevant: zusätzlich Tool-, Handoff-, Autorisierungs- und Commit-Reihenfolgen prüfen und kritische Regeln zur Laufzeit erzwingen.
- Subjektives Kriterium: LLM-Judge mit klarer Rubrik, Reihenfolge-Swap, `unknown`-Option und Kalibrierung gegen verblindete Fachurteile verwenden.
- Probabilistische Komponente: mehrere isolierte Trials, Konfidenzintervalle, Fehlermoden und absolute Zahl kritischer Verstöße berichten.
- Irreversibler Schaden möglich: Eval niemals als einzige Schutzbarriere; Capability-Begrenzung, Policy-Gate und gegebenenfalls menschliche Freigabe vor den Commit setzen.
- Telemetrie: Inhalte standardmäßig auslassen, Redaction vor Export durchführen und kritische Sicherheitsereignisse vollständig erfassen.

## Direkte Quellen

- [Anthropic: Demystifying Evals for AI Agents](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents)
- [Inspect AI](https://inspect.aisi.org.uk/)
- [OpenTelemetry: GenAI Semantic Conventions](https://opentelemetry.io/docs/specs/semconv/gen-ai/)
- [Google SRE: Service Level Objectives](https://sre.google/sre-book/service-level-objectives/)
- [NIST AI RMF – Measure](https://airc.nist.gov/airmf-resources/airmf/5-sec-core/)
