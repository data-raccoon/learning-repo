# Garantie-Taxonomie für KI-Harnesses

## Kurzfassung

Ein KI-Harness ist der ausführende Kontrollrahmen um ein oder mehrere Modelle: Er verwaltet Zustände, Identitäten, Berechtigungen, Budgets, Tool-Aufrufe, Validierung, Freigaben, Persistenz und Telemetrie. Seine Garantien enden an klaren Systemgrenzen. Ein Schema kann die Form einer Nachricht erzwingen, eine Zugriffskontrolle einen Aufruf verbieten und ein Zustandsautomat einen Übergang ausschließen. Keiner dieser Mechanismen beweist, dass eine Modellaussage wahr, vollständig oder fachlich angemessen ist.

Für Architekturentscheidungen werden vier Evidenzklassen getrennt:

1. **Deterministisch erzwingbar:** Eine korrekt implementierte Kontrollkomponente lässt eine verbotene Zustandsänderung innerhalb ihrer Autorität nicht zu.
2. **Unter expliziten Annahmen garantiert:** Die Aussage gilt nur, solange benannte Voraussetzungen gelten, etwa deterministisches Replay, persistente Historie und idempotente Activities.
3. **Statistisch messbar:** Eine Eigenschaft wird mit Stichproben, Konfidenzintervallen und einem definierten Einsatzspektrum geschätzt.
4. **Heuristisch:** Ein Verfahren kann nützlich sein, liefert aber weder Beweis noch belastbare Wahrscheinlichkeit ohne Evaluation.

Der empfohlene Default lautet: **deterministischer Kernel, probabilistische Blätter**. Code besitzt Autorität über Ablauf und Nebenwirkungen; Modelle liefern Vorschläge innerhalb enger Verträge.

## Anwendungsbereich

Diese Taxonomie gilt für Single-Agent-, Multi-Agent- und Multi-Modell-Systeme sowie für Workflow-Engines, Agent-SDKs und eigene Harnesses. Sie dient für Architektur-Reviews, Threat Models, Service-Level-Ziele, Release-Gates und Incident-Analysen. Sie bewertet keine Modellmarke und ist keine Zertifizierung.

Eine Garantieangabe ist nur vollständig, wenn sie fünf Teile nennt:

`Eigenschaft + Mechanismus + Geltungsbereich + Voraussetzungen + beobachtbare Verletzung`

Beispiel: „Der Adapter lehnt Schreibzugriffe außerhalb des Mandanten deterministisch ab, sofern jede Schreiboperation ausschließlich über diesen Adapter läuft, die Identität authentisch gebunden ist und die Policy-Version verfügbar ist; ein Deny-Log oder ein unerlaubter Commit ist das Prüfsignal.“

## Begriffe und Evidenzklassen

### Deterministisch erzwingbar

Eine Eigenschaft ist deterministisch erzwingbar, wenn alle relevanten Ausführungspfade durch einen nicht-probabilistischen Enforcer laufen und dessen Entscheidung atomar vor der geschützten Wirkung erfolgt. Typische Mechanismen sind Zustandsautomaten, Typ- und Schema-Prüfung, Capability-Listen, ACLs, harte Zeit- und Kostenbudgets, Transaktionen und kryptografisch gebundene Identitäten.

„Deterministisch“ beschreibt hier die Enforcement-Logik, nicht das Gesamtsystem. Ein Modell darf einen beliebigen Tool-Aufruf vorschlagen; der Adapter kann dennoch deterministisch nur freigegebene Kombinationen aus Identität, Ressource und Aktion ausführen.

### Unter expliziten Annahmen garantiert

Diese Klasse umfasst konditionale Garantien. Durable Execution kann beispielsweise nach einem Worker-Ausfall fortsetzen, **wenn** die Event History dauerhaft und konsistent verfügbar ist, Replay-kompatibler Workflow-Code bereitsteht und externe Wirkungen korrekt als Activities behandelt werden. Temporal vergleicht beim Replay erzeugte Commands mit der vorhandenen Historie und meldet Nichtdeterminismus bei Abweichungen; externe API-, Datenbank- und LLM-Aufrufe gehören deshalb außerhalb des Replay-Pfads in Activities ([Temporal: Workflow Definition](https://docs.temporal.io/workflow-definition#deterministic-constraints)).

Die Voraussetzung ist Teil der Garantie, keine Fußnote. Fällt sie weg, muss der Betriebszustand als „Garantie nicht nachgewiesen“ sichtbar werden.

### Statistisch messbar

Qualität, Halluzinationsrate, Tool-Auswahl, Sicherheitserkennung und Latenz sind meist Verteilungen. Belastbare Aussagen benötigen:

- ein versioniertes Aufgaben- und Einsatzspektrum,
- getrennte Entwicklungs-, Test- und Canary-Daten,
- deterministische Scorer, wo möglich,
- Stichprobengröße, Unsicherheit und Fehlertypen,
- Segmentierung nach Modell, Prompt, Tool- und Policy-Version,
- kontinuierliche Überwachung auf Drift.

Eine gemessene Erfolgsrate ist keine Einzelfallgarantie. Anthropic empfiehlt mehrere Evaluationsschichten für Agenten, weil kein einzelner Layer alle Fehlermodi abdeckt ([Demystifying Evals for AI Agents](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents)).

### Heuristisch

Prompting, Chain-of-Thought, Selbstkritik, LLM-as-Judge, Mehrheitsentscheid und Multi-Agent-Debatte können Ergebnisse verbessern, sind aber ohne aufgabenspezifische Evaluation keine quantifizierte Absicherung. Auch Konsens korrelierter Modelle ist kein Wahrheitsbeweis. Die ICML-Studie von Smit et al. zeigt, dass Multi-Agent-Debatte empirisch und gegenüber geeigneten Baselines bewertet werden muss ([Should we be going MAD?](https://proceedings.mlr.press/v235/smit24a.html)).

## Technische Mechanismen

### Deterministischer Kernel, probabilistische Blätter

Der Kernel kontrolliert:

- kanonische Run-, Nutzer-, Mandanten- und Tool-Identitäten,
- erlaubte Zustände und Übergänge,
- Eingabe-/Ausgabeverträge und Größenlimits,
- Capability- und Policy-Entscheidungen,
- Zeit-, Token-, Geld-, Schritt- und Parallelitätsbudgets,
- Retry-, Deduplication- und Commit-Protokolle,
- Freigaben, Audit-Ereignisse und Abbruchbedingungen.

Probabilistische Blätter dürfen klassifizieren, planen, Inhalte erzeugen oder Kandidaten priorisieren. Ihre Ausgabe ist zunächst **untrusted data**. Sie erhält erst nach syntaktischer Validierung, semantischen Regeln, Policy-Prüfung und gegebenenfalls menschlicher Freigabe Wirkung. Anthropic unterscheidet entsprechend Workflows mit vorgegebenen Codepfaden von Agenten, die Prozess und Tool-Nutzung dynamisch steuern ([Building Effective Agents](https://www.anthropic.com/engineering/building-effective-agents)).

### Referenzfluss

```text
untrusted input
  -> Authentisierung/Kontextbindung
  -> deterministischer Zustandsautomat
  -> Modellschritt (Vorschlag)
  -> Schema + semantische Regeln
  -> Policy + Budget + Risikoklasse
  -> [Freigabe bei hohem Risiko]
  -> idempotenter Tool-Adapter
  -> expliziter Commit
  -> append-only Audit-Ereignis
```

Keine Komponente sollte zugleich Vorschlag, Freigabe und irreversible Ausführung kontrollieren.

## Garantie-Ledger

| Behauptung | Klasse | Mechanismus | Voraussetzungen | Nicht garantiert |
|---|---|---|---|---|
| „Nur erlaubte Übergänge werden akzeptiert“ | deterministisch erzwingbar | zentraler Zustandsautomat, atomare Compare-and-Set-Änderung | kein Bypass; vollständige Zustandsmodellierung | fachliche Richtigkeit eines erlaubten Übergangs |
| „Tool-Ausgabe entspricht Schema X“ | deterministisch erzwingbar | Parser/Validator oder constrained decoding plus serverseitige Prüfung | tatsächlich verwendetes Schema; Größen-/Tiefenlimits | Wahrheit, Vollständigkeit, sichere Bedeutung |
| „Budget B wird nicht überschritten“ | deterministisch erzwingbar | Reservierung vor Aufruf, harte Zähler, Fail-closed | alle Kostenpfade instrumentiert; atomare Buchung | Fertigstellung oder Qualität innerhalb B |
| „Run setzt nach Prozessausfall fort“ | bedingt garantiert | persistierte Event History/Checkpoints und Replay | dauerhafter Store; kompatibler deterministischer Workflow-Code | Fortsetzung nach Store-Verlust; korrekte externe Wirkung |
| „Retry erzeugt keine doppelte Zahlung“ | bedingt garantiert | stabiler Idempotency Key und deduplizierender Empfänger | Schlüssel wird über alle Versuche wiederverwendet; Empfänger garantiert Deduplizierung | Exactly-once ohne diese Voraussetzungen |
| „Qualität ≥ Zielwert im Einsatz“ | statistisch messbar | repräsentative Evals, Konfidenzgrenzen, Canary/SLO | stabile Verteilung und korrekte Messung | Erfolg jedes einzelnen Falls |
| „Mehrheitsvotum ist verlässlicher“ | heuristisch bis evaluiert | Ensemble/Voting | erst nach Vergleichstest statistisch einstufbar | Wahrheit durch Konsens |
| „Mensch hat freigegeben“ | deterministisch protokollierbar | signierte, gebundene Approval-Entscheidung | authentisierte Person; unverändertes Artefakt | fachliche Fehlerfreiheit der Entscheidung |

Jedes Projekt sollte dieses Ledger versionieren und für jede Garantie Owner, Enforcer, Prüfsignal, Test und Rest-Risiko ergänzen.

## Nicht-Garantien und Failure Domains

Eine lokale Garantie komponiert sich nicht automatisch zu einer End-to-End-Garantie:

- **Modell:** nichtdeterministische oder falsche Inhalte, Kontextverlust, Prompt Injection.
- **Orchestrator:** fehlerhafte Übergänge, konkurrierende Runs, verlorene Abbrüche, fehlerhafte Versionierung.
- **Tool-Adapter:** Bypass, zu breite Capability, falsche Parametermodellierung, fehlende Idempotenz.
- **Externer Dienst:** Timeouts nach erfolgreichem Commit, schwache Deduplication, inkonsistente Antworten.
- **Persistenz:** Verlust, Korruption, Event-Reihenfolge, unvollständige Backups, zu große Historien.
- **Policy/Identität:** veraltete Policy, fail-open, Token-Verwechslung, Mandantenbruch.
- **Mensch:** Approval Fatigue, falsche Darstellung, Freigabe eines später veränderten Artefakts.
- **Observability:** fehlende Korrelation, sensible Daten in Logs, Sampling-Lücken.
- **Deployment:** Modell-, Prompt-, Tool-, Policy- oder Workflow-Versionen passen nicht zusammen.

Besonders kritisch ist das Ungewissheitsfenster: Ein externer Dienst kann eine Wirkung committed haben, während die Bestätigung verloren geht. Persistenz des Workflows löst dieses Problem nicht. AWS dokumentiert ausdrücklich, dass Replay und Retry dieselbe Operation mehrfach ausführen können und weder at-least-once noch at-most-once pro Retry pauschal „genau einmal im gesamten Workflow“ bedeutet ([AWS: Idempotency and retries](https://docs.aws.amazon.com/durable-execution/patterns/best-practices/idempotency/)).

## Erreichbare Garantien samt Voraussetzungen

### Erreichbar

- **Pfadkontrolle:** Nur im Zustandsautomaten definierte Schritte werden dispatcht, sofern kein alternativer Ausführungspfad existiert.
- **Autoritätsbegrenzung:** Ein Tool kann nur die dem Adapter erteilten Capabilities nutzen, sofern Credentials nicht außerhalb verfügbar sind.
- **Ressourcenbegrenzung:** Ein neuer Schritt startet nur bei reserviertem Budget, sofern alle Pfade den zentralen Zähler verwenden.
- **Auditierbarkeit:** Jede akzeptierte Zustandsänderung besitzt ein korreliertes Ereignis, sofern Log und Commit atomar gekoppelt oder über eine Outbox verbunden sind.
- **Wiederaufnahme:** Ein Run rekonstruiert seinen letzten dauerhaften Zustand, sofern Historie, Codeversion und Replay-Regeln intakt sind.
- **Nebenwirkungs-Deduplizierung:** Wiederholte Requests mit demselben Schlüssel erzeugen höchstens eine fachliche Wirkung, sofern der Empfänger dies atomar erzwingt.

### Nicht garantiert

- semantische Wahrheit durch JSON Schema oder typisierte Nachrichten,
- Sicherheit durch Prompt-Guardrails allein,
- Exactly-once-Nebenwirkungen allein durch Checkpoints,
- vollständige Isolation durch die bloße Produktbezeichnung „Sandbox“,
- korrekte Entscheidungen durch Selbstkritik, LLM-Judge oder Agentenkonsens,
- End-to-End-Verfügbarkeit aus der Verfügbarkeit einer einzelnen Komponente,
- Datenschutz durch Redaction, wenn Rohdaten zuvor unkontrolliert repliziert wurden.

## Entscheidungskriterien

Vor jeder technischen Garantie sind folgende Fragen zu beantworten:

1. Welche konkrete unerwünschte Zustandsänderung soll unmöglich werden?
2. Welche Komponente besitzt tatsächlich Autorität über diese Änderung?
3. Gibt es Bypass-Pfade, alternative Credentials oder direkte Netzwerkzugriffe?
4. Welche Annahmen liegen außerhalb der Kontrolle des Enforcers?
5. Ist die Aussage binär prüfbar, nur statistisch messbar oder bloß plausibel?
6. Wie wird eine Verletzung beobachtet und welcher sichere Zustand folgt?
7. Wie verhalten sich Retry, Timeout, Abbruch und Crash unmittelbar vor/nach Commit?
8. Bleibt die Aussage bei Rollout einer neuen Modell-, Prompt-, Tool- oder Workflow-Version gültig?

Wenn keine klare Enforcer-Komponente identifiziert werden kann, ist die Behauptung keine deterministische Garantie.

## Umsetzbare Checkliste

- [ ] Für jede Zusage Klasse, Scope, Voraussetzungen, Enforcer und Prüfsignal dokumentieren.
- [ ] Modellausgaben durchgehend als nicht vertrauenswürdige Vorschläge behandeln.
- [ ] Zustandsübergänge zentral und fail-closed validieren.
- [ ] Jede externe Wirkung über einen einzigen kontrollierten Adapter führen.
- [ ] Tool-Capabilities pro Rolle, Run und Ressource minimieren.
- [ ] Budgets vor dem Dispatch atomar reservieren; harte Abbruchgrenzen testen.
- [ ] Retry-Semantik pro Operation festlegen; Idempotency Keys stabil persistieren.
- [ ] Approval an Identität, exakten Payload-Hash, Policy- und Ablaufversion binden.
- [ ] Crash-Punkte vor und nach jedem Commit per Fault Injection testen.
- [ ] Statistische Qualitätsziele mit Unsicherheit, Segmenten und Drift-Monitoring versehen.
- [ ] Heuristiken nie als Sicherheits- oder Wahrheitsbeweis beschreiben.
- [ ] Bei jeder Änderung das Garantie-Ledger und die Bypass-Analyse erneut prüfen.

## Quellenhinweise

Die verlinkten Framework- und Herstellerseiten beschreiben Produktmechanismen und können sich ändern; Abrufstand dieser Ausarbeitung ist 2026-07-22. Ihre Aussagen werden hier nicht als unabhängiger Nachweis fachlicher Gesamtqualität gewertet. Ergänzend: [NIST AI Risk Management Framework](https://www.nist.gov/itl/ai-risk-management-framework) ist ein organisatorischer Govern/Map/Measure/Manage-Rahmen, keine Runtime-Garantie.
