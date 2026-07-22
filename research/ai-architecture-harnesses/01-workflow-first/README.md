# Workflow-first: feste Kontrolle vor autonomer Agentenschleife

[Kurzfassung](KURZFASSUNG.md) · [Beispielimplementierung](beispiel/README.md) · [Gesamtübersicht](../README.md)

## Kurzfassung

„Workflow-first“ bedeutet: Die niedrigste Architekturkomplexität wählen, die den Anwendungsfall nachweislich erfüllt, und Kontrolle standardmäßig in Code halten. Ein **Workflow** orchestriert Modell- und Tool-Schritte über vorgegebene Pfade; ein **Agent** entscheidet dynamisch über nächsten Schritt und Tool-Nutzung. Diese Unterscheidung wird von Anthropic ausdrücklich so formuliert ([Building Effective Agents](https://www.anthropic.com/engineering/building-effective-agents)).

Der stärkste Default ist ein deterministischer Zustandsautomat mit probabilistischen Modellschritten als begrenzten Blättern. Er kann Reihenfolge, erlaubte Übergänge, Budgets, Freigaben und Tool-Rechte deterministisch erzwingen. Er kann nicht erzwingen, dass eine Modellantwort wahr ist. Autonomie wird nur dort geöffnet, wo die benötigten Schritte im Voraus tatsächlich nicht sinnvoll modellierbar sind und eine Evaluation einen messbaren Vorteil gegenüber der einfacheren Baseline zeigt.

## Anwendungsbereich

Der Ansatz eignet sich für produktive KI-Systeme mit wiederkehrenden Aufgaben, externen Nebenwirkungen, Compliance-Anforderungen, Kostenlimits oder definierten Erfolgsbedingungen. Dazu zählen Dokumentenverarbeitung, Support, Freigabeverfahren, Recherche, Softwareänderungen und Backoffice-Automatisierung.

Nicht jeder deterministische Prozess benötigt eine Workflow-Engine. Für kurze, synchrone, rein lesende Abläufe kann normaler Anwendungscode genügen. Durable Execution ist eine separate Entscheidung und wird unter [03 – Durable Execution](../03-durable-execution/) behandelt.

## Architekturkontinuum

| Stufe | Kontrollpfad | Geeignet, wenn | Hauptpreis |
|---|---|---|---|
| deterministischer Code ohne Modell | vollständig vorgegeben | Regeln reichen aus | geringe sprachliche Flexibilität |
| einzelner Modellaufruf | ein vorgegebener probabilistischer Schritt | Klassifikation/Extraktion/Entwurf genügt | inhaltliche Unsicherheit |
| Workflow mit Modellblättern | Übergänge in Code, Inhalte teils probabilistisch | Prozess und Gates sind bekannt | mehr Latenz und Zustandsführung |
| begrenzter Agent | dynamische Schleife innerhalb enger Capabilities | Schrittfolge ist teilweise offen | schwerere Tests, kumulative Fehler |
| Multi-Agent-System | dynamische Delegation/Koordination | nachgewiesene Spezialisierungs- oder Parallelvorteile | zusätzliche Kosten und Fehlermodi |

Microsoft empfiehlt ebenfalls die niedrigste Komplexitätsstufe, die Anforderungen zuverlässig erfüllt, und nennt Koordinationsaufwand, Latenz und neue Fehlermodi als Kosten von Multi-Agent-Orchestrierung ([Azure Architecture Center: Agent orchestration patterns](https://learn.microsoft.com/en-us/azure/architecture/ai-ml/guide/ai-agent-design-patterns)).

## Technische Mechanismen

### Zustandsautomat als Autorität

Der kanonische Run-Zustand liegt nicht im Chatverlauf, sondern in einem typisierten Store. Ein Übergang ist eine Funktion aus `(aktueller Zustand, validiertes Ereignis, Policy-Version)` und erzeugt entweder `(neuer Zustand, erlaubte Effekte)` oder eine Ablehnung.

```text
RECEIVED
  -> VALIDATED
  -> PLANNED
  -> POLICY_CHECKED
  -> [APPROVAL_REQUIRED -> APPROVED]
  -> EXECUTING
  -> VERIFYING
  -> COMMITTED | REJECTED | FAILED | CANCELLED
```

Das Modell darf etwa einen Plan vorschlagen, aber nicht `APPROVAL_REQUIRED` überspringen. Übergänge nutzen Compare-and-Set oder Transaktionen, damit zwei Worker nicht beide denselben Zustand fortschreiben.

### Probabilistische Blätter

Jeder Modellschritt erhält:

- einen eng definierten Auftrag und minimierten Kontext,
- eine versionierte Eingabe- und Ausgabestruktur,
- eine feste Capability-Liste,
- Token-, Zeit-, Kosten- und Versuchslimits,
- deterministische Vor- und Nachbedingungen,
- einen Fehlerpfad, der keine Nebenwirkung auslöst.

Modelloutput ist ein Vorschlag. Syntaktische Validierung prüft Form; fachliche Regeln und Tests prüfen nur die jeweils kodierten Eigenschaften. Unsichere Fälle werden abgelehnt, erneut bearbeitet oder an Menschen eskaliert.

### Workflow-Muster

**Prompt Chaining:** Eine feste Sequenz zerlegt eine Aufgabe in kleinere Modellschritte. Zwischenstufen können programmgesteuerte Gates besitzen. Geeignet bei klaren Abhängigkeiten; frühe Fehler müssen vor Folgeeffekten abgefangen werden.

**Deterministisches Routing:** Code routet anhand verifizierbarer Merkmale. Das garantiert den gewählten Pfad für diese Merkmale. Ein LLM-Router ist dagegen ein probabilistischer Klassifikator; Schema-Compliance macht seine Kategorie nicht richtig.

**Parallelisierung:** Unabhängige Teilaufgaben laufen parallel und werden deterministisch zusammengeführt. Der Join benötigt Timeout-, Teilfehler- und Reihenfolgeregeln. Voting bleibt heuristisch, bis sein Nutzen statistisch belegt ist.

**Evaluator–Optimizer:** Generator und Kritiker iterieren bis zu einem harten Limit. Ein LLM-Kritiker ist kein Freigabe-Gate für irreversible Wirkungen; deterministische Tests oder menschliche Freigabe bleiben nötig.

**Begrenzter Agent als Subworkflow:** Ein Agent darf innerhalb einer Sandbox eine offene Recherche oder Reparatur durchführen. Der äußere Workflow setzt Capabilities, Budget, Stop Conditions, Artefaktgrenzen und Commit-Gate. Anthropic empfiehlt bei Agenten Umgebungs-Feedback, Checkpoints, Stop Conditions, Sandbox-Tests und klare Tools ([Building Effective Agents](https://www.anthropic.com/engineering/building-effective-agents)).

Google ADK beschreibt Graph-Workflows als explizite Knoten und Kanten, die deterministische Kontrollpfade um agentische Schritte legen ([ADK: Graph-based agent workflows](https://adk.dev/graphs/)). Framework-Funktionen sind zeitabhängige Herstellerangaben; die Garantie folgt erst aus der konkreten Konfiguration und dem ausgeschlossenen Bypass.

### Stop Conditions und Budgets

Jede Schleife benötigt mindestens:

- maximale Modell- und Tool-Schritte,
- Wall-Clock-Deadline und per-call Timeout,
- Token-/Kostenbudget mit Reservierung vor Aufruf,
- maximale Parallelität und Kontextgröße,
- Abbruch bei wiederholtem identischem Fehler oder fehlendem Fortschritt,
- explizite Endzustände für Erfolg, Teilresultat, Fehler und Abbruch.

Ein vom Modell ausgegebenes „fertig“ ist nur ein Ereignisvorschlag. Der Kernel entscheidet anhand prüfbarer Abschlusskriterien.

## Erreichbare Garantien samt Voraussetzungen

| Garantie | Klasse | Voraussetzungen |
|---|---|---|
| Nur definierte Zustandsübergänge werden committed | deterministisch erzwingbar | zentraler Store; atomare Übergänge; kein direkter Bypass |
| Hochrisiko-Tool läuft erst nach Approval | deterministisch erzwingbar | Tool ausschließlich hinter Gate; Approval an Payload-Hash gebunden |
| Kein neuer Schritt startet nach Budgetende | deterministisch erzwingbar | vollständige Kostenpfade; atomare Vorabreservierung; fail-closed |
| Schleife endet spätestens nach N Dispatches | deterministisch erzwingbar | Kernel zählt jeden Dispatch; keine rekursiven Nebenpfade |
| Nach Crash wird am gespeicherten Punkt fortgesetzt | bedingt garantiert | dauerhafter Checkpoint/Event Store; kompatible Codeversion; korrekte Replay-Logik |
| Modellschritt erreicht Qualitätsziel Q | statistisch messbar | repräsentatives Eval-Set, definierter Scorer, Unsicherheit und Driftkontrolle |
| Selbstkritik verbessert den Entwurf | heuristisch, bis evaluiert | Nutzen muss gegen Single-Pass-Baseline belegt werden |

## Nicht-Garantien und Failure Modes

- Ein fester Ablauf macht probabilistische Zwischenergebnisse nicht wahr.
- Ein typisiertes Routing-Ergebnis macht die gewählte Route nicht fachlich korrekt.
- Ein „erfolgreicher“ Tool-Return beweist nicht zwingend die externe Wirkung; API-Vertrag und Verifikation sind nötig.
- Ein Schrittlimit verhindert unendliche Dispatches im kontrollierten Loop, aber nicht hängende externe Aufrufe ohne Timeout.
- Ein Human-in-the-Loop beweist keine korrekte Entscheidung; er schafft Verantwortungs- und Kontrollpunkt.
- Eine Sandbox ist nur so eng wie ihre tatsächlichen Datei-, Netzwerk-, Prozess- und Credential-Grenzen.
- Ein Agent kann innerhalb erlaubter Rechte falsche oder schädliche Aktionen wählen.
- Parallelität kann Race Conditions, inkonsistente Snapshots und nichtdeterministische Aggregation erzeugen.
- Ein dynamischer Planner kann unvollständige Pläne, zyklische Delegation oder irrelevante Schritte erzeugen.
- Framework-Abstraktionen können Prompts, Zustände und Retries verdecken; ihre Existenz ist keine Garantie.

## Wann Autonomie gerechtfertigt ist

Ein begrenzter Agent ist eine Option, wenn alle folgenden Punkte erfüllt sind:

1. Die benötigte Schrittfolge ist tatsächlich nicht vorab sinnvoll aufzählbar.
2. Externe Ground Truth kann während der Ausführung abgefragt werden.
3. Erfolg oder Fortschritt ist zumindest teilweise prüfbar.
4. Fehler sind reversibel oder vor Commit abfangbar.
5. Capabilities und Blast Radius sind klein.
6. Harte Stop Conditions und Budgets existieren.
7. Offline-Evals und Canary-Daten zeigen einen relevanten Vorteil gegenüber Workflow- oder Single-Call-Baseline.

Fehlt einer dieser Punkte bei hohem Schadenspotenzial, sollte der offene Teil in Vorschlagserzeugung zurückgestuft und der Commit deterministisch oder menschlich kontrolliert werden.

## Entscheidungskriterien

### Für einen festen Workflow

- bekannte Phasen, regulatorisch geforderte Reihenfolge oder klare Gates,
- irreversible oder teure Nebenwirkungen,
- hohe Anforderungen an Reproduzierbarkeit und Audit,
- geringe Vielfalt zulässiger Pfade,
- deterministisch prüfbare Erfolgskriterien.

### Für einen begrenzten Agenten

- unbekannte Zahl oder Reihenfolge von Such-/Reparaturschritten,
- heterogene Umgebungsbefunde bestimmen den nächsten Schritt,
- hohe Varianz der Aufgaben bei begrenztem, reversiblem Wirkraum,
- messbarer Mehrwert der Dynamik.

### Gegen Multi-Agent als Default

Mehrere Agenten werden nicht eingeführt, nur weil Rollen sprachlich plausibel wirken. Zuerst sind Single-Call, Single-Agent und deterministischer Workflow als Baselines zu messen. Erst nachgewiesene Qualitäts-, Parallelitäts-, Sicherheits- oder Spezialisierungsgewinne rechtfertigen Koordination, zusätzliche Kontexte und neue Failure Domains.

## Beispiel: kontrollierte Softwareänderung

1. Code authentisiert Auftrag, Repository und erlaubten Pfad.
2. Ein Modell erstellt einen strukturierten Änderungsplan.
3. Regeln prüfen Pfadgrenzen, verbotene Dateien und Budget.
4. Ein begrenzter Coding-Agent editiert nur einen isolierten Worktree.
5. Deterministische Formatter, Tests und Security-Checks laufen.
6. Bei hohem Risiko wird exakt der geprüfte Diff-Hash freigegeben.
7. Ein Commit-Adapter prüft Hash, Policy und Identität erneut.
8. Run, Artefakte und Gate-Ergebnisse werden append-only protokolliert.

Garantiert werden können Pfad- und Commit-Gates unter Ausschluss von Bypässen. Nicht garantiert wird, dass Tests alle fachlichen Anforderungen abdecken oder der freigegebene Code fehlerfrei ist.

## Umsetzbare Checkliste

- [ ] Einfachste belastbare Baseline festlegen und messen.
- [ ] Kanonischen Zustand außerhalb des Chatverlaufs speichern.
- [ ] Zustände, Übergänge, Endzustände und illegale Übergänge spezifizieren.
- [ ] Modellschritte als untrusted, versionierte Funktionen mit Verträgen behandeln.
- [ ] Tool-Rechte pro Schritt statt global vergeben.
- [ ] Alle Schleifen mit Schritt-, Zeit-, Token-, Kosten- und Parallelitätslimit versehen.
- [ ] Abschluss anhand externer oder deterministischer Kriterien prüfen.
- [ ] Hochrisiko-Commit von Planung und Generierung trennen.
- [ ] Approval an unveränderlichen Payload-Hash und Gültigkeitsdauer binden.
- [ ] Parallelpfade auf Snapshot-Konsistenz, Join und Teilfehler testen.
- [ ] Crash-, Timeout-, Retry- und Abbruchszenarien per Fault Injection prüfen.
- [ ] Autonomie nur nach Eval-Vorteil gegenüber einfacherer Baseline erweitern.
- [ ] Modell-, Prompt-, Tool-, Policy- und Workflow-Version je Run erfassen.

## Quellenhinweise

Primärquellen: [Anthropic: Building Effective Agents](https://www.anthropic.com/engineering/building-effective-agents), [Microsoft Azure Architecture Center: Agent orchestration patterns](https://learn.microsoft.com/en-us/azure/architecture/ai-ml/guide/ai-agent-design-patterns), [Google ADK: Graph workflows](https://adk.dev/graphs/) und [LangGraph: Workflows and agents](https://langchain-ai.github.io/langgraph/tutorials/workflows/). Die Frameworkseiten belegen angebotene Mechanismen zum jeweiligen Abrufstand 2026-07-22, nicht deren korrekte Verwendung oder eine End-to-End-Garantie.
