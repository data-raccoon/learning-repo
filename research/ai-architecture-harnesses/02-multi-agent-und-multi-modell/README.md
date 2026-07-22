# Multi-Agent- und Multi-Modell-Architekturen

[Kurzfassung](KURZFASSUNG.md) · [Beispielimplementierung](beispiel/README.md) · [Gesamtübersicht](../README.md)

Stand: 2026-07-22

## Kurzfassung

Mehr Agenten oder Modelle sind kein Zuverlässigkeitsmerkmal an sich. Sie sind sinnvoll, wenn eine Aufgabe nachweislich parallelisierbar ist, voneinander abgrenzbare Spezialrollen oder Sicherheitsdomänen besitzt, ein einzelnes Kontextfenster übersteigt oder ein kostenbewusstes Routing zwischen unterschiedlich geeigneten Modellen erlaubt. Sie sind nicht gerechtfertigt, wenn zusätzliche Rollen nur dieselben Informationen mit denselben Fehlerquellen erneut verarbeiten.

Der belastbarste Entwurf ist ein deterministischer Orchestrator mit probabilistischen Arbeitsschritten: Code kontrolliert Topologie, Identität, Berechtigungen, Handoff-Verträge, Zustandsübergänge, Parallelitäts- und Kostenbudgets, Abbruch sowie Commit. Modelle schlagen Klassifikation, Planung oder Inhalte vor; sie dürfen keine dieser Kontrollregeln selbst außer Kraft setzen. Multi-Agent- oder Multi-Modell-Betrieb wird erst zugelassen, wenn eine versionierte Evaluation gegenüber einer einfacheren Baseline einen vorher definierten Mehrwert bei Qualität, Kosten, Latenz und Risiko zeigt.

Mehrheitsentscheid, Debatte, Selbstkritik und LLM-basierte Router sind heuristisch. Sie beweisen weder Wahrheit noch Unabhängigkeit. Das ICML-Papier von Smit et al. fand, dass untersuchte Multi-Agent-Debatten andere Prompting- und Ensembleverfahren nicht zuverlässig übertrafen und empfindlich auf Hyperparameter reagierten ([Smit et al., 2024](https://proceedings.mlr.press/v235/smit24a.html)).

## Anwendungsbereich

Dieses Dokument behandelt die Zerlegung einer KI-Anwendung in mehrere ausführende Agenten oder Modellaufrufe. „Agent“ bezeichnet hier eine Rolle mit eigenem Auftrag, Kontext und erlaubten Tools; „Modell“ den jeweiligen Inferenzdienst. Mehrere Agenten können dasselbe Modell verwenden, ein Agent kann mehrere Modelle verwenden. Diese Achsen sind getrennt zu entscheiden.

Geeignete Fälle:

- unabhängige Recherche- oder Analysezweige, deren Ergebnisse später zusammengeführt werden;
- klar getrennte Fach- oder Berechtigungsdomänen;
- unbekannte, erst während der Bearbeitung sichtbare Unteraufgaben;
- Routing einfacher Fälle auf kleine Modelle und schwieriger Fälle auf leistungsfähigere Modelle;
- Kandidatenerzeugung mit objektivem, deterministischem Verifier;
- Redundanz über tatsächlich unterschiedliche Fehlerdomänen.

Ungeeignete Fälle:

- ein einzelner Aufruf oder ein deterministischer Workflow erfüllt bereits das SLO;
- alle Rollen benötigen fortlaufend denselben vollständigen Kontext;
- die Aufgabe ist eng sequenziell und jeder Handoff verliert Information;
- „Konsens“ soll fehlende Ground Truth ersetzen;
- externe Nebenwirkungen würden konkurrierend und ohne Transaktionsprotokoll ausgeführt.

Diese Default-Position entspricht der Empfehlung, zunächst die niedrigste ausreichende Komplexität zu verwenden: Microsoft nennt den Single Agent mit Tools häufig den geeigneten Enterprise-Default und weist bei Multi-Agent auf Koordinationsaufwand, Latenz und zusätzliche Fehlermodi hin ([Azure Architecture Center](https://learn.microsoft.com/en-us/azure/architecture/ai-ml/guide/ai-agent-design-patterns)). Anthropic trennt feste Workflows von dynamisch gesteuerten Agenten und empfiehlt, Komplexität nur bei messbarem Mehrwert hinzuzufügen ([Building Effective Agents](https://www.anthropic.com/engineering/building-effective-agents)).

## Technische Mechanismen und Muster

### 1. Sequenzielle Pipeline

Ein programmierter Graph ruft spezialisierte Schritte in fester Reihenfolge auf, etwa Extraktion → Prüfung → Formulierung. Die Route ist deterministisch, die Modelloutputs bleiben probabilistisch. Jeder Übergang bekommt ein versioniertes Ein- und Ausgabeschema; ungültige oder semantisch unzulässige Daten werden nicht weitergereicht.

Geeignet ist das Muster für klare Abhängigkeiten. Sein Hauptfehler ist Kaskadierung: Ein früher Irrtum wird zur vermeintlichen Tatsache späterer Schritte. Daher müssen Handoff-Gates Fehler explizit kennzeichnen, Provenienz erhalten und bei unzureichender Evidenz stoppen statt „best effort“ fortzusetzen.

### 2. Parallele Aufteilung (Sectioning)

Code zerlegt die Aufgabe in disjunkte Arbeitspakete und führt sie parallel aus. Ein Aggregator prüft Vollständigkeit, Duplikate, Konflikte und Quellenbezug. Das kann Laufzeit verkürzen und separate Kontextfenster nutzbar machen. Anthropic beschreibt diesen Nutzen für offene Breitenrecherche, weist aber zugleich auf hohen Tokenverbrauch und ungeeignete, stark gekoppelte Domänen hin ([Multi-Agent Research System](https://www.anthropic.com/engineering/multi-agent-research-system)). Dessen interne Leistungszahlen sind Herstellerergebnisse für einen spezifischen Dienst, keine allgemeine Garantie.

Die Zerlegung ist nur dann echt parallel, wenn die Pakete wenige gemeinsame veränderliche Abhängigkeiten besitzen. Gemeinsamer Zustand wird über versionierte Snapshots gelesen; Schreibresultate werden als unveränderliche Vorschläge gesammelt und erst vom Orchestrator zusammengeführt.

### 3. Orchestrator–Worker

Ein Orchestrator plant dynamisch und delegiert an Worker. Das eignet sich, wenn Anzahl und Art der Unteraufgaben nicht vorab bekannt sind. Es verschiebt aber Fehlerrisiko in die Auftragszerlegung. Jeder Worker-Auftrag benötigt mindestens:

- eindeutige Aufgabe, Scope und Ausschlüsse;
- erlaubte Quellen, Daten und Tools;
- erwartetes, typisiertes Ergebnisformat;
- Zeit-, Token-, Kosten- und Tool-Aufrufbudget;
- Abbruch- und Eskalationskriterien;
- Korrelation (`run_id`, `task_id`, `parent_id`) und Provenienz.

Der Orchestrator darf weder unbeschränkt neue Worker erzeugen noch deren Resultate ungeprüft als Fakten übernehmen. Maximaler Fan-out, maximale Tiefe und Gesamtbudget werden außerhalb des Modells erzwungen. Anthropic berichtet als eigene Produktionserfahrung von Duplikaten, Lücken und exzessivem Fan-out bei unpräziser Delegation ([Multi-Agent Research System](https://www.anthropic.com/engineering/multi-agent-research-system)).

### 4. Handoff und dynamisches Routing

Bei einem Handoff geht die aktive Verantwortung von einer Rolle an eine andere über. Ein robustes Handoff ist kein freier Chattext, sondern ein Vertrag, zum Beispiel:

```json
{
  "schema_version": "1.0",
  "run_id": "r-123",
  "from": "triage",
  "to": "billing",
  "reason_code": "INVOICE_DISPUTE",
  "task": {"invoice_id": "inv-42"},
  "evidence_refs": ["doc:7#p3"],
  "assumptions": [],
  "requested_capability": "billing.read",
  "deadline": "2026-07-22T14:00:00Z"
}
```

Der Kontrollrahmen authentisiert Absender und Empfänger, validiert das Schema, prüft Ziel und Capability gegen eine Allowlist, begrenzt Handoff-Zahl und Schleifen, minimiert Kontext und protokolliert den Übergang. Ist der richtige Empfänger bereits aus stabilen Metadaten bestimmbar, ist regelbasiertes Routing vorzuziehen. Microsoft warnt bei dynamischen Handoffs vor Fehlrouting und Endlosschleifen ([Azure Handoff Pattern](https://learn.microsoft.com/en-us/azure/architecture/ai-ml/guide/ai-agent-design-patterns#handoff-orchestration)).

### 5. Multi-Modell-Routing

Routing kann regelbasiert oder gelernt sein:

- **Regelbasiert:** Datenklasse, Mandant, Sprache, Aufgabe, Modellfreigabe, Kontextgröße und Risikostufe wählen aus einer versionierten Allowlist. Das gewählte Ziel ist für dieselben kontrollierten Metadaten reproduzierbar.
- **Kaskade:** Ein günstiges Modell bearbeitet den Fall; nur bei messbarem Unsicherheits- oder Verifier-Signal eskaliert der Harness.
- **Gelernt/LLM-basiert:** Ein Router schätzt Eignung oder Schwierigkeit. Diese Entscheidung ist statistisch zu kalibrieren und braucht Fallbacks; sie ist keine Garantie.
- **Portfolio:** Mehrere Modelle erzeugen Kandidaten; ein deterministischer Test oder ein kalibrierter Scorer wählt. Ohne externen Verifier bleibt die Auswahl heuristisch.

Eine Routingentscheidung wird mit `policy_version`, `router_version`, Kandidatenmenge, Grundcode, geschätzten und tatsächlichen Kosten sowie Ergebnis des nachgelagerten Verifiers geloggt. Anbieterfehler, Rate Limits und Datenresidenz sind Teil der Route, nicht nachträgliche Sonderfälle.

### 6. Ensembles, Voting und Debatte

Mehrere Stichproben können Varianz reduzieren, wenn ihre Fehler hinreichend unabhängig sind. Diese Voraussetzung ist bei LLMs oft verletzt: gleicher Modellstamm, Systemprompt, Retrievalindex, Tool, Trainingsbias oder gemeinsam übernommener Zwischenstand erzeugen korrelierte Fehler. Eine nominelle Mehrheit aus fünf nahezu identischen Läufen ist nicht mit fünf unabhängigen Messungen gleichzusetzen.

Diversität muss operationalisiert werden: verschiedene Modellfamilien oder Versionen, unabhängige Retrievalpfade, getrennte Prompts, zufällige Reihenfolge und verdeckte Antworten vor dem Urteil. Danach werden paarweise Fehlerkorrelation, gemeinsame Fehlerrate und inkrementeller Nutzen gegenüber Self-Consistency gemessen. Debattierende Agenten dürfen vor ihrer Erstposition keine fremden Antworten sehen, wenn Unabhängigkeit Teil der Hypothese ist.

Ein LLM-Judge oder eine Mehrheitsstimme bleibt probabilistisch und kann systematischen Irrtum verstärken. Wo ein ausführbarer Test, Solver, Datenbank-Constraint oder menschlich verantwortete Freigabe verfügbar ist, hat dieser Vorrang. MAST klassifiziert unter anderem Systemdesign-, Inter-Agent-Abstimmungs- und Verifikationsfehler anhand von mehr als 1.600 annotierten Traces; die Arbeit ist als Preprint, nicht als peer-reviewter Endstand, zu behandeln ([Cemri et al., arXiv v3](https://arxiv.org/abs/2503.13657)).

### 7. Konfliktbehandlung

Konflikte werden nicht durch stilles Überschreiben gelöst. Der Aggregator erstellt eine Konfliktmenge mit Behauptung, Evidenz, Quelle, Zeitstempel und Unsicherheit. Die Auflösung folgt einer festen Rangfolge:

1. deterministische Ground Truth oder autoritative Datenquelle;
2. reproduzierbarer Test beziehungsweise formale Geschäftsregel;
3. erneute unabhängige Datenerhebung;
4. menschliche Entscheidung bei risikoreicher oder nicht auflösbarer Abweichung;
5. explizit als ungeklärt ausgeben.

Ein weiterer LLM-Aufruf kann Belege ordnen, ist aber keine Wahrheitsinstanz. Externe Aktionen dürfen erst nach Konfliktauflösung und Commit-Gate erfolgen.

### 8. Budgets und Abbruch

Mindestens folgende Grenzen werden atomar im Orchestrator geführt:

- maximale Agenten und Verschachtelungstiefe;
- maximale Modellaufrufe, Tool-Aufrufe und Handoffs;
- Token-, Geld- und Wandzeitbudget pro Run und Teilaufgabe;
- maximale Kontext- und Artefaktgröße;
- Wiederholungs- und Fehlerbudget;
- maximale Zahl noch ungeklärter Konflikte vor Eskalation.

Ein Worker reserviert Budget vor dem Aufruf; Abschluss oder Fehler verbucht den tatsächlichen Verbrauch. So kann paralleler Fan-out nicht dasselbe Restbudget mehrfach ausgeben. Abbruch erfolgt über harte Zähler und Deadlines, nicht allein über Modelltext wie „fertig“. AutoGen bietet kombinierbare Bedingungen für Nachrichten-, Token- und Zeitgrenzen; deren korrekte Konfiguration bleibt Verantwortung der Anwendung ([AutoGen Termination](https://microsoft.github.io/autogen/stable/user-guide/agentchat-user-guide/tutorial/termination.html)).

## Erreichbare Garantien und Voraussetzungen

| Aussage | Klasse | Voraussetzungen und Reichweite |
|---|---|---|
| Nur erlaubte Rolle erhält einen Handoff | deterministisch erzwingbar | authentisierte Identität, deny-by-default Ziel-/Capability-Policy, Enforcer nicht umgehbar |
| Fan-out, Tiefe, Aufrufzahl und nominelles Budget überschreiten konfigurierte Grenzen nicht | deterministisch erzwingbar | atomare Reservierung, alle Aufrufe laufen durch denselben Gateway, harte Deadlines |
| Ein syntaktisch gültiger Handoff entspricht dem Schema | deterministisch erzwingbar | versioniertes Schema und Reject-on-failure vor Zustandsänderung |
| Ein pausierter Lauf kann ab Checkpoint fortgesetzt werden | unter Annahmen garantiert | dauerhafter Store, kompatibler Code, deterministischer Replaypfad; Nebenwirkungen idempotent oder dedupliziert |
| Die Multi-Agent-Variante verbessert eine definierte Qualitätsmetrik | statistisch messbar | repräsentativer, versionierter Eval-Satz, Konfidenzintervalle, wiederholte Läufe, Kosten-/Latenzvergleich |
| Mehrheitsentscheid findet die Wahrheit | nicht garantiert / heuristisch | selbst bei Diversität bleiben gemeinsame Biases und falscher Konsens möglich |
| Unterschiedliche Modellnamen liefern unabhängige Fehler | nicht garantiert | Anbieter, Daten, Prompt, Retrieval und Tools können Fehlerdomänen teilen |
| Erfolgreicher Handoff bewahrt alle relevanten Informationen | nicht garantiert | Zusammenfassung, Kontextbegrenzung und Schema können relevante Details verlieren |

## Nicht-Garantien und Failure Modes

- **Korrelierter Irrtum:** Alle Agenten zitieren dieselbe falsche Quelle oder übernehmen dieselbe unbestätigte Prämisse.
- **Authority laundering:** Eine Vermutung wird durch Handoffs zu scheinbar bestätigtem Wissen, weil Provenienz und Unsicherheit verloren gehen.
- **Routing-Fehler:** Ein Klassifikator sendet den Fall an ein ungeeignetes Modell oder in eine Rolle mit falscher Datenfreigabe.
- **Handoff-Schleife:** Rollen reichen einen Fall weiter, ohne dass Zustand oder Evidenzfortschritt zunimmt.
- **Kaskadierter Format-/Semantikfehler:** Schema-konformer, aber sachlich falscher Output vergiftet Folgeschritte.
- **Kontextvergiftung:** Prompt Injection oder kompromittierte Tooldaten wandern zwischen Rollen.
- **Budgetexplosion:** dynamischer Fan-out, Debatte oder Evaluator-Schleifen verbrauchen unbeschränkt Tokens und Zeit.
- **Race Conditions:** parallele Agenten verändern denselben Zustand oder führen dieselbe Nebenwirkung aus.
- **Privilegienvereinigung:** Ein Orchestrator kombiniert Resultate oder Tokens so, dass die Gesamtanwendung mehr Rechte erhält als jede vorgesehene Rolle.
- **Falsche Redundanz:** Mehrere Agenten laufen auf demselben Endpoint, Modell und Retrievalindex; der gemeinsame Ausfall bleibt unberührt.
- **Judge-Bias und Positionsbias:** Der Aggregator bevorzugt Stil, Länge, Reihenfolge oder die eigene Modellfamilie statt Korrektheit.
- **Stale handoff:** Ein Ergebnis wird nach Änderung des Ausgangszustands committed; Versions- oder ETag-Prüfung fehlt.

## Entscheidungskriterien

Multi-Agent oder Multi-Modell darf eine einfachere Baseline nur ersetzen, wenn vorab festgelegte Gates erfüllt sind:

| Frage | Nachweis | Stop-Signal |
|---|---|---|
| Ist die Arbeit wirklich zerlegbar? | Abhängigkeitsgraph; Anteil unabhängiger Teilaufgaben | häufige Rückfragen oder gemeinsamer veränderlicher Zustand |
| Entsteht fachlicher Mehrwert? | Holdout-Eval mit End-to-End- und Teilmetriken | kein statistisch belastbarer Gewinn |
| Entsteht Systemmehrwert? | p50/p95-Latenz, Kosten, Durchsatz, Fehlerrate | Qualitätsgewinn verletzt SLO oder Budget |
| Sind Fehler divers? | Fehlerkorrelationsmatrix und gemeinsame Fehlermuster | hohe Korrelation trotz nomineller Vielfalt |
| Sind Handoffs kontrollierbar? | Schema-, ACL-, Schleifen- und Stale-State-Tests | Freitextübergaben oder implizite Autorität |
| Ist Betrieb beherrschbar? | Trace-Vollständigkeit, Replay-, Chaos- und Degradationstests | nicht lokalisierbare Kosten oder Fehler |
| Sind Aktionen sicher? | policy-geprüfte Adapter, Idempotenzschlüssel, Approval-Gates | Agenten besitzen direkte Schreibzugänge |

Die Eval vergleicht mindestens: Single Call, Single Agent mit denselben Tools, deterministische Workflowvariante und vorgeschlagene Multi-Agent-/Multi-Modellvariante. Budgets müssen gleich oder transparent normalisiert sein. Ein höheres Ergebnis durch vielfachen Tokenverbrauch wird als Qualitäts-Kosten-Kurve berichtet, nicht als pauschaler Architekturgewinn.

## Umsetzbare Checkliste

- [ ] Single-Call- und Single-Agent-Baseline versioniert messen.
- [ ] Für jeden Agenten Zweck, Eingabe, Ausgabe, Datenzugriff, Tools und Besitzer dokumentieren.
- [ ] Topologie und erlaubte Handoffs als Code/Policy definieren; standardmäßig verweigern.
- [ ] Handoffs typisieren, versionieren, authentisieren und mit Provenienz versehen.
- [ ] `run_id`, `task_id`, `parent_id`, Modell-/Prompt-/Policy-Version durchgängig propagieren.
- [ ] Fan-out, Tiefe, Handoffs, Tokens, Kosten, Tool-Aufrufe und Laufzeit hart begrenzen.
- [ ] Budget vor paralleler Arbeit atomar reservieren.
- [ ] Gemeinsamen Zustand nicht direkt aus parallelen Workern verändern lassen.
- [ ] Nebenwirkungen ausschließlich über policy-geprüfte, idempotente Adapter mit Commit-Gate ausführen.
- [ ] Konflikte sichtbar sammeln; keine Mehrheitsentscheidung als Wahrheit deklarieren.
- [ ] Modell- und Retrievaldiversität sowie Fehlerkorrelation messen.
- [ ] Router auf Fehlklassifikation, Drift, Fallback und Datenresidenz testen.
- [ ] Schleifen anhand begrenzter Übergänge und ausbleibenden Fortschritts abbrechen.
- [ ] Teilagenten und Gesamtsystem getrennt evaluieren; Stichproben und Seeds protokollieren.
- [ ] Degradationspfad definieren: weniger Worker, Single Agent, Read-only oder menschliche Übergabe.
- [ ] Zulassung widerrufen, wenn Qualitätsgewinn, Kosten- oder Sicherheits-SLO im Betrieb unterschritten wird.

## Quellen und Einordnung

- [Anthropic: Building Effective Agents](https://www.anthropic.com/engineering/building-effective-agents), Herstellerpraxis, 2024.
- [Anthropic: How we built our multi-agent research system](https://www.anthropic.com/engineering/multi-agent-research-system), Herstellerbericht und interne Evaluation, 2025.
- [Microsoft Azure Architecture Center: AI agent orchestration patterns](https://learn.microsoft.com/en-us/azure/architecture/ai-ml/guide/ai-agent-design-patterns), offizielle Architekturdokumentation, zeitabhängig.
- [Microsoft AutoGen: Termination](https://microsoft.github.io/autogen/stable/user-guide/agentchat-user-guide/tutorial/termination.html), offizielle Framework-Dokumentation, zeitabhängig.
- [Smit et al.: Should we be going MAD?](https://proceedings.mlr.press/v235/smit24a.html), peer-reviewed, ICML 2024.
- [Cemri et al.: Why Do Multi-Agent LLM Systems Fail?](https://arxiv.org/abs/2503.13657), Preprint, arXiv v3, 2025.

Siehe ergänzend [Workflow-first](../01-workflow-first/), [Durable Execution](../03-durable-execution/), [Sicherheit und Isolation](../05-sicherheit-und-isolation/) und [Evaluation und Observability](../06-evaluation-observability/).
