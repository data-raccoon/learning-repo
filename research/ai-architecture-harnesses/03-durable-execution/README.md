# Durable Execution für agentische Systeme

[Kurzfassung](KURZFASSUNG.md) · [Beispielimplementierung](beispiel/README.md) · [Gesamtübersicht](../README.md)

## Kurzfassung

Durable Execution („dauerhafte Ausführung“) trennt den logischen Run von einem einzelnen Prozess. Entscheidungen und Ergebnisse werden als Checkpoints oder Event History persistiert; nach Ausfall rekonstruiert ein Worker den Zustand und setzt fort. Das ist besonders wertvoll für lange Modellläufe, menschliche Freigaben, Timeouts und externe Tools.

Die belastbare Aussage ist konditional: **Wiederaufnahme ist unter den Persistenz-, Replay-, Versions- und Verfügbarkeitsannahmen des Systems garantiert.** Sie bedeutet nicht, dass jede externe Nebenwirkung genau einmal stattfindet. Activity-Retries sind typischerweise at-least-once; Idempotency Keys, atomare Deduplication, Transactional Outbox und Sagas schließen die Lücke je nach Operation. Ein persistierter Chatverlauf allein ist keine Durable-Execution-Architektur.

## Anwendungsbereich

Durable Execution lohnt sich für Abläufe, die:

- länger als ein Prozess oder Request leben,
- auf Menschen, Timer, Queues oder externe Systeme warten,
- nach Crash oder Deployment fortgesetzt werden müssen,
- Retries und Kompensation explizit steuern,
- einen auditierbaren Zustandsverlauf benötigen.

Für kurze, rein lesende und leicht wiederholbare Aufrufe kann die zusätzliche Infrastruktur unverhältnismäßig sein. Durable Execution ist keine Ersatzlösung für Zugriffskontrolle, semantische Validierung, Isolation oder Evals.

### Einordnung der Aussagen

- **Deterministisch erzwingbar** sind lokale Invarianten wie atomare Versionsprüfung oder „kein Commit ohne passenden Approval-Hash“, wenn kein Bypass existiert.
- **Unter expliziten Annahmen garantiert** sind Wiederaufnahme und Deduplizierung: Sie hängen von dauerhafter Historie, replay-kompatiblem Code beziehungsweise atomarer Empfängerlogik ab.
- **Statistisch messbar** sind betriebliche Eigenschaften wie Recovery-Zeit, Retry-Rate und Verfügbarkeit; Messwerte sind keine Einzelfallgarantie.
- **Heuristisch** bleiben etwa eine vom Modell vorgeschlagene Retry- oder Kompensationsentscheidung, solange der Kernel sie nicht durch feste Regeln begrenzt und ihre Qualität nicht evaluiert ist.

## Technische Mechanismen

### Zustands- und Ausführungsmodell

#### Event History und Replay

Ein event-sourced Workflow speichert nicht nur einen veränderlichen Snapshot, sondern die relevanten Entscheidungen und Ergebnisse in geordneter Historie. Beim **Replay** wird Workflow-Code erneut ausgeführt und muss für dieselben Eingaben dieselbe Folge von Workflow-Commands erzeugen. Temporal vergleicht diese Commands mit der bestehenden Event History; eine Abweichung führt zu einem Nichtdeterminismusfehler ([Temporal: Workflow Definition](https://docs.temporal.io/workflow-definition#deterministic-constraints)).

Nichtdeterministische Operationen – Uhrzeit, Zufall, Datenbank-, API- und LLM-Aufrufe – dürfen nicht unkontrolliert im Replay-Pfad liegen. Sie werden als Activities ausgeführt oder ihre Ergebnisse über replay-sichere SDK-Primitive historisiert. Temporal beschreibt Activities als normale, potenziell nichtdeterministische Funktionen und empfiehlt Idempotenz ([Temporal: Activities](https://docs.temporal.io/activities)).

Temporal dokumentiert, dass Replay erzeugte Commands gegen die Historie prüft und nach einem Fehler ab dem letzten aufgezeichneten Ereignis weiterarbeitet ([Temporal: Workflow Execution](https://docs.temporal.io/workflow-execution#replays)). Dies belegt den Mechanismus; die tatsächliche Garantie hängt zusätzlich von Betrieb, Storage, Versionierung und korrekter Anwendung ab.

#### Checkpoints

Checkpoint-Systeme speichern den Zustand nach Knoten oder Supersteps. Ein produktionsfähiger Checkpoint benötigt mindestens:

- stabile Run-/Thread-ID und monotonen Versionsbezug,
- atomare Speicherung von Zustand und nächster ausführbarer Arbeit,
- Schutz gegen konkurrierende Writer,
- dauerhaftes Backend statt ausschließlich In-Memory,
- definierte Serialisierung, Migration, Verschlüsselung und Aufbewahrung,
- Markierung, welche Ergebnisse bereits extern committed wurden.

Ein Checkpoint reduziert Wiederholungsarbeit, beseitigt aber nicht das Commit-Ungewissheitsfenster externer Systeme.

#### LLM-Aufrufe als Activities

Ein LLM-Aufruf ist eine externe, nichtdeterministische Operation. Für Replay wird sein Ergebnis persistiert; es wird nicht bei jeder Rekonstruktion neu erzeugt. Ein erneuter **Activity-Versuch** kann jedoch nötig sein, wenn kein Abschlussereignis vorliegt. Deshalb werden gespeichert:

- Modell-/Provider-ID und relevante Version,
- Prompt-/Template-Version und normalisierter Input-Hash,
- Tool-/Schema-/Policy-Version,
- Versuch, Deadline, Token- und Kostenwerte,
- Ergebnis oder klassifizierter Fehler,
- gegebenenfalls redigierte statt rohe sensitive Inhalte.

Persistiertes verborgenes Reasoning sollte weder vorausgesetzt noch unnötig gespeichert werden. Für Audit zählen Inputs, Entscheidungen, Tool-Aufrufe, Outputs, Policies und Commit-Belege.

## Retry-Semantik und Idempotenz

### At-least-once, at-most-once, exactly-once

- **At-least-once:** Bei unklarem Ausgang wird erneut versucht. Fortschritt ist robuster, Nebenwirkungen können mehrfach auftreten.
- **At-most-once:** Ein unsicher abgeschlossener Versuch wird nicht erneut ausgeführt. Doppelte Wirkung wird begrenzt, dafür kann die Wirkung ausbleiben oder unbekannt bleiben.
- **Exactly-once als fachliche Wirkung:** Benötigt eine atomare Deduplication/Transaktion an der maßgeblichen Systemgrenze. Ein Workflow-Label allein reicht nicht.

AWS dokumentiert präzise, dass Replay und Retry dieselbe Operation mehrfach ausführen können. Die dortige at-most-once-Semantik gilt pro Retry-Versuch und garantiert nicht pauschal genau eine Ausführung über den gesamten Workflow; at-least-once ist nur für idempotente Operationen sicher ([AWS: Idempotency and retries](https://docs.aws.amazon.com/durable-execution/patterns/best-practices/idempotency/)).

### Idempotency Key

Ein stabiler Schlüssel wird **vor** der unsicheren Nebenwirkung dauerhaft erzeugt und bei jedem Retry identisch mitgesendet. Der Empfänger muss ihn atomar zusammen mit dem Ergebnis speichern und bei Duplikaten dasselbe Ergebnis zurückgeben.

```text
key = stable(run_id, logical_step_id, operation_version)
reserve/check key atomically at receiver
perform effect
store outcome for key in same atomic boundary
return outcome on duplicate request
```

Voraussetzungen:

- gleiche logische Operation erhält denselben Schlüssel,
- neue fachliche Operation erhält einen neuen Schlüssel,
- Scope umfasst Mandant und Operationsart,
- Aufbewahrungszeit deckt maximale Retry-/Replay-Dauer,
- Payload-Abweichung unter demselben Schlüssel wird abgelehnt,
- Deduplication geschieht im System, das die Wirkung besitzt.

Ein „check then act“ in zwei nichtatomaren Schritten ist race-anfällig und keine Garantie.

## Commit-Protokolle für externe Wirkungen

### Transactional Outbox

Wenn Fachzustand und zu sendendes Ereignis dieselbe Datenbank teilen, werden beide in einer Transaktion committed. Ein Relay versendet Outbox-Einträge at-least-once; Konsumenten deduplizieren anhand stabiler Event-ID.

**Bedingte Garantie:** Kein committed Fachzustand ohne zugehörigen Outbox-Eintrag, sofern beide Writes wirklich dieselbe ACID-Transaktion nutzen. **Nicht garantiert:** einmalige Zustellung oder einmalige Wirkung beim Konsumenten.

### Inbox/Deduplication

Der Konsument speichert Event-ID und fachliche Änderung atomar. Unter Unique Constraint und korrekter Transaktion wird dieselbe Event-ID höchstens einmal fachlich angewandt. Fehlerhafte Schlüsselwahl, abgelaufene Einträge oder ein Bypass brechen die Aussage.

### Saga und Kompensation

Eine Saga zerlegt einen verteilten Vorgang in lokale Transaktionen und führt bei späterem Fehler Kompensationsaktionen aus. Kompensation ist eine neue fachliche Wirkung, kein Zurückdrehen der Zeit. Sie kann selbst scheitern, muss idempotent und beobachtbar sein und gegebenenfalls manuell eskalieren.

Beispiel: Reservierung → Zahlung → Versand. Scheitert Versand, kann Zahlung erstattet und Reservierung gelöst werden. Die Garantie ist nicht „alles war nie passiert“, sondern ein definierter, eventualer Zielzustand unter der Annahme erfolgreicher oder manuell abgeschlossener Kompensation.

### Expliziter Commit

Planung und Wirkung werden getrennt:

1. Activity erzeugt einen unveränderlichen Wirkungsvorschlag.
2. Deterministische Validatoren und Policy prüfen ihn.
3. Bei hohem Risiko wird der exakte Payload-Hash freigegeben.
4. Commit-Activity prüft Hash, Idempotency Key, aktuelle Policy und Vorbedingungen erneut.
5. Ergebnis/Beleg wird historisiert; bei unklarem Ausgang erfolgt Statusabfrage statt blindem Retry.

## Human-in-the-Loop

Eine menschliche Freigabe ist ein dauerhaftes externes Ereignis. Der Workflow wartet ohne offenen Prozess und setzt nach dem Approval fort. Das Approval-Objekt sollte enthalten:

- Run-, Schritt- und Mandanten-ID,
- Identität und Rolle der freigebenden Person,
- Hash des exakt dargestellten Artefakts und der Tool-Parameter,
- Policy-/Workflow-Version, Entscheidung, Zeit und Ablaufdatum,
- Kommentar bzw. Grund bei Ablehnung oder Ausnahme.

Nach jeder inhaltlichen Änderung verfällt die Freigabe. Doppeltes Approval ist durch Ereignis-ID und Zustandsübergang zu deduplizieren. Ein Approval garantiert nachvollziehbare Autorisierung, nicht fachliche Fehlerfreiheit.

## Erreichbare Garantien samt Voraussetzungen

| Aussage | Klasse | Voraussetzungen |
|---|---|---|
| Run-Zustand kann nach Worker-Crash rekonstruiert werden | bedingt garantiert | durable, konsistente Historie; verfügbare Worker; replay-kompatibler Code |
| Bereits historisierte Modellresultate werden beim Replay wiederverwendet | bedingt garantiert | Modellaufruf korrekt als Activity/Task gekapselt; Ergebnis committed und lesbar |
| Kein erlaubter Zustandsübergang geht ohne Audit-Ereignis verloren | bedingt garantiert | Zustand und Ereignis atomar bzw. per Outbox gekoppelt |
| Gleiche Event-ID wird höchstens einmal fachlich angewandt | bedingt garantiert | atomare Inbox/Unique Constraint am Wirkungssystem; kein Bypass |
| Outbox-Eintrag existiert für jeden committed Fachzustand | deterministisch erzwingbar innerhalb einer DB | gemeinsame ACID-Transaktion und unveränderte Constraints |
| Hochrisiko-Commit entspricht freigegebenem Payload | deterministisch erzwingbar | Hash-Prüfung unmittelbar im alleinigen Commit-Adapter |
| Workflow beendet eine Activity irgendwann erfolgreich | nicht allgemein garantiert | externe Dienste, Worker und Ressourcen können dauerhaft ausfallen |
| Modellantwort ist korrekt, weil sie persistiert ist | keine Garantie | Persistenz konserviert auch Fehler |

## Nicht-Garantien und Failure Modes

- **Doppelte Wirkung:** Timeout nach externem Commit, aber vor lokaler Bestätigung.
- **Verlorene Wirkung:** at-most-once vermeidet Retry nach unklarem Versuch.
- **Poison Retry:** deterministischer Fehler wird ohne Klassifikation wiederholt.
- **Retry Storm:** fehlendes Backoff/Jitter oder gemeinsame Störung überlastet Abhängigkeiten.
- **Replay-Nichtdeterminismus:** Codeänderung, lokale Uhrzeit/Zufall oder I/O im Workflow-Pfad.
- **Versionsbruch:** alte Historie wird mit inkompatiblem Workflow- oder Schema-Code geladen.
- **Geschichte wächst unbeschränkt:** Replay wird langsam oder überschreitet Plattformlimits.
- **Split Brain:** mehrere Worker committen ohne atomare Versionsprüfung.
- **Stale Approval:** Artefakt oder Policy ändert sich nach Freigabe.
- **Kompensation scheitert:** Saga bleibt in manuell zu klärendem Zwischenzustand.
- **Datenleck:** Prompts, Tool-Argumente oder Resultate landen unredigiert in dauerhaften Logs.
- **Retention-Lücke:** Deduplication Key verfällt vor dem letzten möglichen Retry.
- **Provider-Retention:** vermeintlich dauerhafter State hängt von ungeprüfter Speicher- oder Backup-Konfiguration ab.

## Entscheidungskriterien

Durable Execution ist angebracht, wenn mindestens eines gilt:

- erwartete Laufzeit überschreitet Request-/Prozesslebensdauer,
- menschliche oder zeitgesteuerte Wartephasen,
- mehrere externe Systeme und nichttriviale Fehlerbehandlung,
- hohe Kosten einer vollständigen Wiederholung,
- regulatorischer oder operativer Auditbedarf.

Vor der Technologiewahl sind zu klären:

1. Muss Zustand nach Prozess-, Zonen- oder Regionsausfall erhalten bleiben?
2. Welche Recovery Point/Time Objectives gelten und sind sie getestet?
3. Welche Schritte sind deterministisch replaybar, welche Activities?
4. Welche Nebenwirkungen unterstützen Idempotency Keys oder Statusabfragen?
5. Wo ist die atomare Grenze für Outbox/Inbox?
6. Welche Kompensationen sind fachlich zulässig?
7. Wie werden Langläufer versioniert und alte Historien getestet?
8. Welche Daten dürfen dauerhaft gespeichert werden?

Eine leichte Checkpoint-Lösung genügt bei begrenztem Risiko und wenigen Schritten. Eine dedizierte Workflow-Engine lohnt sich bei langen Wartezeiten, vielen Retries, Signalen, Sagas und strengen Betriebsanforderungen. Framework-Funktionslisten sind zeitabhängig; entscheidend sind verifizierte Semantik und Betriebsmodell.

## Teststrategie

Eine Durable-Execution-Architektur wird nicht nur mit Happy-Path-Tests abgenommen. Notwendig sind kontrollierte Abstürze:

- vor Activity-Dispatch,
- nach Dispatch, vor Empfang der Antwort,
- nach externer Wirkung, vor lokalem Commit,
- nach lokalem Commit, vor Acknowledgement,
- während Approval, Cancellation und Deployment,
- bei doppelter oder verspäteter Nachricht,
- bei inkompatibler Code-/Schema-Version,
- bei Ausfall von Policy-, Secret-, Event- und Wirkungssystem.

Replay-Tests führen historische Produktions- oder synthetische Event-Historien gegen neue Workflow-Versionen aus. Invarianten prüfen unter anderem: kein Commit ohne Gate, Budget nie negativ, terminaler Zustand unveränderlich, pro logischer Operation höchstens eine fachliche Wirkung.

## Umsetzbare Checkliste

- [ ] Workflow-Logik und nichtdeterministische Activities strikt trennen.
- [ ] Event History/Checkpoints in dauerhaftem, gesichertem Store betreiben.
- [ ] Optimistic Concurrency oder Transaktionen für Zustandsfortschritt nutzen.
- [ ] Für jede Activity Retry-Klasse, Timeout, Backoff, Max Attempts und Fehlerklassifikation festlegen.
- [ ] Externe Writes mit stabilem, dauerhaftem Idempotency Key versehen.
- [ ] Payload-Hash und Empfänger-Scope an den Key binden.
- [ ] Statusabfrage für unklare Commit-Ausgänge bevorzugen.
- [ ] Fachzustand und Outbox atomar schreiben; Konsumenten per Inbox deduplizieren.
- [ ] Sagas mit idempotenten Kompensationen und manueller Eskalation modellieren.
- [ ] Approvals dauerhaft, authentisiert und an exakten Artefakt-Hash binden.
- [ ] Workflow-Code versionieren und alte Historien vor Deployment replayen.
- [ ] History-Wachstum, Retention, Backups und Wiederherstellung testen.
- [ ] Sensitive Payloads minimieren, verschlüsseln und in Logs redigieren.
- [ ] Fault Injection an jedem Commit-Fenster automatisieren.
- [ ] Dashboards für stuck Runs, Retry Storms, Nichtdeterminismus und offene Kompensationen einrichten.

## Quellenhinweise

Primärquellen: [Temporal-Dokumentation](https://docs.temporal.io/), insbesondere [Workflow Execution](https://docs.temporal.io/workflow-execution), [Workflow Definition und deterministisches Replay](https://docs.temporal.io/workflow-definition#deterministic-constraints) sowie [Activities](https://docs.temporal.io/activities); [AWS Durable Execution: Idempotency and retries](https://docs.aws.amazon.com/durable-execution/patterns/best-practices/idempotency/); [LangGraph Persistence](https://langchain-ai.github.io/langgraph/concepts/persistence/) und [LangGraph Functional API: Side Effects/Replay](https://langchain-ai.github.io/langgraph/how-tos/review-tool-calls-functional/). Dies sind Herstellerangaben zum Abrufstand 2026-07-22. Sie belegen dokumentierte Mechanismen, nicht eine anwendungsunabhängige End-to-End-Garantie.
