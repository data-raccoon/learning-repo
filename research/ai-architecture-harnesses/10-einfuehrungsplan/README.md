# Einführungsplan: vom Single Call zur High-Assurance-Architektur

[Kurzfassung](KURZFASSUNG.md) · [Beispielimplementierung](beispiel/README.md) · [Gesamtübersicht](../README.md)

Stand: 2026-07-22

## Kurzfassung

Die Einführung erfolgt risikogesteuert in sieben Stufen (0 bis 6). Jede Stufe liefert eine nutzbare, begrenzte Fähigkeit und endet mit einem überprüfbaren Gate. Der Default ist ein einzelner, read-only Modellaufruf; Workflow, Tools, Durable Execution, Multi-Agent und High-Assurance-Kontrollen kommen nur hinzu, wenn ein belegter Bedarf und messbarer Mehrwert bestehen.

Ein Gate ist kein Meeting, sondern ein Evidenzpaket: versionierte Anforderungen, bestandene deterministische Tests, statistische Evals mit vorab festgelegten Schwellen, Threat-Model-Änderung, Betriebsmetriken und ein getesteter Rollback. Ein Fehlschlag führt auf eine benannte sichere Vorstufe zurück. NISTs Funktionen **Govern, Map, Measure, Manage** liefern dafür einen organisatorischen Rahmen, aber keine technische Runtime-Garantie ([NIST AI RMF](https://www.nist.gov/itl/ai-risk-management-framework)).

## Anwendungsbereich und Leitplanken

Der Plan gilt für neue KI-Funktionen ebenso wie für die Härtung bestehender Prototypen. Er setzt ein fachlich verantwortliches Team, Softwarebetrieb, Security und Datenschutz voraus. Kalenderwochen werden bewusst nicht vorgegeben: Risikoreduktion und Evidence, nicht Zeitablauf, erlauben den Aufstieg.

Vier Klassen bleiben in jedem Gate getrennt:

- **deterministisch erzwingbar:** Schema, ACL, Zustandsübergang, Budget, Timeout, Allowlist;
- **unter expliziten Annahmen garantiert:** Recovery durch Replay, Deduplizierung und kompensierbare Abläufe;
- **statistisch messbar:** Aufgabenqualität, Fehlerrate, Latenz, Kosten und Sicherheitsdetektion;
- **heuristisch:** Selbstkritik, LLM-as-Judge, Debatte oder Konsens.

Die Empfehlung, mit einfachen, komponierbaren Mustern zu beginnen und Komplexität nur bei nachweislichem Bedarf zu erhöhen, entspricht der Praxiserfahrung von Anthropic ([Building Effective Agents](https://www.anthropic.com/engineering/building-effective-agents)).

## Vorbereitende Artefakte

Vor Stufe 0 werden folgende Vorlagen versioniert:

1. **Use-Case-Karte:** Nutzer, Zweck, erwarteter Nutzen, Datenklassen, externe Systeme, Schadensszenarien.
2. **Garantie-Ledger:** Aussage, Klasse, Scope, Annahmen, Enforcer, Test, Owner und Prüfintervall.
3. **Eval-Vertrag:** Datensatzversion, Splits, Metriken, Schwellen, Unsicherheitsdarstellung und Stop-Regeln.
4. **Release-Manifest:** Code-, Prompt-, Policy-, Schema-, Tool- und Modellversionen.
5. **Runbook:** Kill Switch, Provider-Ausfall, Datenleck, Doppelwirkung, Rollback und manuelle Reconciliation.

Eine Anforderung wie „zuverlässig“ ist nicht gate-fähig. Sie wird beispielsweise zerlegt in `schema_valid = 100 % der akzeptierten Antworten`, `task_success >= vorab festgelegte Schwelle auf Eval v3`, `p95 latency <= SLO` und `kein schreibender Aufruf ohne Allow-Decision in Negativtests`. Nur die erste und letzte Aussage können im spezifizierten Scope deterministisch erzwungen werden.

## Technische Mechanismen und erreichbare Garantien

Der Reifegrad wächst nicht durch mehr Agenten, sondern durch zusätzliche überprüfbare Kontrollstellen:

| Ab Stufe | Mechanismus | Erreichbare Aussage | Klasse und Voraussetzung |
|---|---|---|---|
| 1 | Schema-Validator vor jedem Consumer | Nicht konforme Ausgaben werden nicht verarbeitet | deterministisch, wenn kein Bypass existiert |
| 1 | atomare Budgets und Deadlines | Kein neuer Aufruf nach Erreichen des Limits | deterministisch; bereits laufende Providerarbeit kann fortbestehen |
| 2 | Zustandsautomat und Capability-Allowlist | Nur erlaubte Übergänge und Tools sind erreichbar | deterministisch bei exklusivem Kernel-/PEP-Pfad |
| 3 | Approval mit Payload-Hash | Nach Freigabe veränderte Payload wird abgewiesen | deterministisch bei vertrauenswürdiger Signatur und Kanonisierung |
| 3 | Idempotency Key, Outbox, Receipt | Retry verursacht höchstens eine sichtbare Wirkung | konditional: Ziel muss atomar deduplizieren oder Wirkung eindeutig feststellbar sein |
| 4 | Event History und deterministischer Replay | Lauf kann nach Worker-Ausfall rekonstruiert werden | konditional: Store verfügbar, Workflow replay-kompatibel, Activities gekapselt |
| 5 | gepaarte Evals gegen Baseline | Zusatzkomplexität verbessert ein Zielmaß | statistisch für die gemessene Verteilung, keine Einzelfallgarantie |
| 6 | Model Checking plus Runtime Conformance | spezifizierte Invarianten gelten im geprüften Modell und werden im Code überwacht | konditional auf Modelltreue, abgedeckten Zustandsraum und korrekte Enforcer |

Jede Zeile wird im Garantie-Ledger um Scope, Owner, automatisierte Evidence, Prüfintervall und Reaktion ergänzt. Fehlt eine Voraussetzung, wird die Aussage herabgestuft oder das Feature nicht freigegeben.

## Stufe 0 — Problem, Baseline und Risiko begrenzen

### Ziel

Beweisen, dass der Use Case ein Modell braucht und Erfolg messbar ist. Noch keine Tools, kein persistentes Gedächtnis, keine externen Nebenwirkungen.

### Umsetzung

- manuelle oder regelbasierte Baseline und ein Single-Call-Prototyp;
- repräsentatives, versioniertes Eval-Set einschließlich schwieriger und missbräuchlicher Eingaben;
- Datenflusskarte, Datenminimierung und Löschfristen;
- Threat-Model-Workshop mit Prompt Injection, Datenabfluss, Bias, Fehlentscheidung und Provider-Ausfall;
- vorab festgelegte Qualitäts-, Latenz-, Kosten- und Sicherheitsmetriken;
- Nutzereingaben und Modellantworten nur in einer nicht produktiven, zugriffsbeschränkten Umgebung.

### Gate G0: Problemzulassung

**Evidenz:** benannter fachlicher Owner; messbarer Nutzen; dokumentierte Zielpopulation; Baseline-Ergebnis; klassifizierte Daten; akzeptiertes Restrisiko; kein unkontrollierter Produktionszugriff.

**Definition of Done (DoD):** Das Eval kann reproduzierbar ausgeführt werden. Jede Metrik hat Richtung, Schwelle und Fehlerkosten. Die einfachere Nicht-KI-Alternative ist dokumentiert. Kritische Einzelfallentscheidungen werden nicht allein aus Durchschnittswerten freigegeben.

**Rollback:** Prototyp abschalten und zur manuellen/regelerbasierten Baseline zurückkehren; Testdaten nach Retention-Regel löschen.

## Stufe 1 — Gehärteter Single Call, read-only

### Ziel

Eine eng begrenzte produktive Assistenz ohne externe Schreibwirkung betreiben.

### Umsetzung

- typisierte Ein- und Ausgabe, Größenlimits und strikte Ablehnung unbekannter Felder;
- constrained decoding/Structured Outputs, wo verfügbar, plus unabhängiger Validator;
- Prompt-, Modell- und Schema-Pinning im Release-Manifest;
- Timeout, maximaler Retry-Zähler, Token-/Kostenlimit und Rate Limit;
- Kontextminimierung, Secret-Redaction und keine persistente freie Erinnerung;
- deterministische Tests für Parser, Validatoren und Fallbacks;
- Shadow Traffic oder kleiner Canary mit Nutzungs- und Qualitätsmonitoring.

Structured Outputs können Antworten an ein JSON-Schema binden, sofern keine Verweigerung oder vorzeitige Unterbrechung vorliegt; sie garantieren keine inhaltliche Wahrheit ([OpenAI](https://openai.com/index/introducing-structured-outputs-in-the-api/)). Deshalb ist „Schema gültig“ nur das erste Gate.

### Gate G1: Read-only-Produktion

**Evidenz:** Contract- und Fuzz-Tests bestanden; keine Secrets in Stichproben der Logs; Offline-Eval erfüllt vorab definierte Schwellen; Canary hält Fehler-, Latenz- und Kosten-SLO; Kill Switch getestet.

**DoD:** Jede akzeptierte Ausgabe wurde serverseitig validiert. Refusal, Timeout, Truncation und Providerfehler werden als eigene Zustände behandelt. Nutzer erkennen KI-generierte Inhalte und haben einen sicheren manuellen Weg.

**Rollback:** Traffic-Flag auf Baseline/Deaktivierung; Modell-Snapshot und Prompt gemeinsam auf das letzte Manifest zurücksetzen. Bereits ausgegebene Inhalte bleiben als mögliche Fehlantworten im Incident-Scope.

## Stufe 2 — Deterministischer Workflow mit Read-Tools

### Ziel

Mehrere Schritte und Datenquellen nutzen, ohne schreibende Nebenwirkungen. Der Kontrollpfad bleibt im Code.

### Umsetzung

- expliziter Zustandsautomat mit Allowlist der Übergänge und Terminalzuständen;
- Tool Registry mit kleinen read-only Capabilities, Ressource- und Egress-Allowlist;
- per-step Kontext, Schema, Budget, Timeout und Retry-Policy;
- Tool-Ergebnisse als untrusted Data mit Herkunft, Zeit und Integritätshash;
- Policy Enforcement Point vor jedem Tool-Aufruf;
- Ende-zu-Ende-Tracing mit redigierten Payloads;
- Tests gegen vergiftete Dokumente, unerlaubte Ziele, Schleifen und Toolausfälle.

OPA ist ein möglicher Policy Decision Point und trennt Policy-Entscheidung von Durchsetzung. Das Gate muss deshalb auch belegen, dass kein alternativer Pfad den Enforcer umgeht ([OPA](https://www.openpolicyagent.org/docs)).

### Gate G2: Workflow-Zulassung

**Evidenz:** vollständige Transition Coverage; Negativtests für jede Capability; Egress- und IAM-Prüfung; Ende-zu-Ende-Budgettests; Security-Eval für direkte und indirekte Prompt Injection; Trace-Vollständigkeit ohne sensible Vollpayloads.

**DoD:** Das Modell kann nur typisierte Vorschläge erzeugen. Es besitzt keine Tool-Credentials. Der Kernel erzwingt Zustände, Budgets und Abbruch. Unbekannter Zustand oder PDP-Ausfall endet sicher (`deny`/`failed`), nicht mit einem freien Agentenlauf.

**Rollback:** Workflow auf Stufe 1 schalten; alle Tool-Capabilities am Gateway entziehen; laufende Runs abbrechen und als `CANCELLED` auditieren.

## Stufe 3 — Schreibende Tools mit explizitem Commit

### Ziel

Begrenzte externe Wirkungen unter Least Privilege, Policy, Idempotenz und risikobasierter menschlicher Freigabe erlauben.

### Umsetzung

- Trennung `propose → validate → authorize → approve → commit → verify`;
- eigener Adapter pro fachlicher Aktion, keine generische Shell oder beliebige HTTP-URL;
- serverseitige Idempotency Keys, Outbox/Inbox, Provider-Receipt und Reconciliation Queue;
- Dry Run und sichtbarer Diff vor Freigabe;
- Approval bindet Identität, Payload-Hash, Scope und Ablaufzeit;
- kurzlebige, auf Ziel und Aktion begrenzte Credentials;
- Sandbox und default-deny Netzwerkzugriff entsprechend Risikoklasse;
- Fault Injection vor, während und nach externem Commit.

Bei MCP-Tools müssen Tokens für den vorgesehenen Resource Server bestimmt und dort validiert werden; Token-Passthrough ist verboten ([MCP Authorization](https://modelcontextprotocol.io/specification/2025-06-18/basic/authorization)). Persistenz allein beweist keine Exactly-once-Wirkung.

### Gate G3: Side-Effect-Zulassung

**Evidenz:** Autorisierungs-Matrix und Negativtests; keine direkten Modell-Credentials; Doppelzustellungstests; Crash-Test an jeder Commit-Grenze; Approval-Tamper-Test; Reconciliation-Runbook praktisch geübt; Security Sign-off je Risikoklasse.

**DoD:** Jede externe Wirkung hat ein eindeutiges `action_id`, Policy-Entscheidung, optionales Approval, Receipt und Ergebnisprüfung. Unklarer Commit-Status führt zu `MANUAL_RECONCILIATION`, nicht zu blindem Retry. Irreversible Hochrisikoaktionen bleiben gesperrt oder verlangen Vier-Augen-Freigabe.

**Rollback:** Write-Capability zentral revoken und auf Dry Run/read-only zurückschalten. Ausstehende Outbox-Einträge stoppen. Bereits erfolgte Wirkungen anhand Receipts inventarisieren und nur über dokumentierte fachliche Kompensation rückgängig machen.

## Stufe 4 — Durable Execution und Human-in-the-loop

### Ziel

Lange, unterbrechbare Prozesse nach Worker- oder Deployment-Ausfällen kontrolliert fortsetzen.

### Umsetzung

- dauerhaftes append-only Event Log und atomare Zustandsversionierung;
- deterministische Workflow-Logik; Zeit, Zufall, Modell- und Netzaufrufe als aufgezeichnete Activities;
- Workflow-Versionierung/Patching und Replay-Tests gegen historische Verläufe;
- begrenzte Retries mit klassifizierten Fehlern und Dead-Letter-/Reconciliation-Pfad;
- dauerhafte Approval-Waits mit Ablauf, Widerruf und Cancellation Propagation;
- Backup/Restore, Verschlüsselung, Retention und Migrationsproben;
- Runbooks für „stuck“, doppeltes Ergebnis, inkompatibles Replay und Store-Ausfall.

Temporal beschreibt die Wiederaufnahme über persistierte Event History und Replay; die erzeugten Commands müssen zur Historie passen ([Temporal Workflow Execution](https://docs.temporal.io/workflow-execution)). Diese Eigenschaft gilt nur bei eingehaltenen Determinismus- und Speicherannahmen.

### Gate G4: Recovery-Zulassung

**Evidenz:** Worker-Kill-Tests in jedem nichtterminalen Zustand; Restore aus Backup; Replay der letzten produktionsnahen Histories gegen neue Workflow-Version; Nachweis für Idempotenz oder Kompensation jeder Activity; Chaos-Test mit Provider-Timeout und verspäteter Antwort.

**DoD:** Ein Run lässt sich aus Event History und gepinnten Artefakten rekonstruieren. Kein Replay wiederholt eine Side Effect außerhalb ihres Adaptervertrags. Migrationen sind vorwärts- und rollback-kompatibel oder haben einen expliziten Drain-Plan. Manuelle Eingriffe erzeugen Audit-Ereignisse.

**Rollback:** Neue Starts auf vorige Workflow-Version routen; inkompatible Runs drainen oder mit alter Worker-Version abschließen; Write-Activities sperren, wenn Reconciliation unsicher ist. Ein Event Store wird nie durch Löschen „zurückgerollt“—Korrekturen sind neue Ereignisse.

## Stufe 5 — Kontrollierte Multi-Agent-/Multi-Modell-Erweiterung

### Ziel

Parallelisierung, Spezialisierung oder Modellredundanz nur dort einsetzen, wo sie gegenüber Stufe 2–4 messbar gewinnt.

### Umsetzung

- zuerst feste Parallelisierung unabhängiger Teilaufgaben; dynamische Delegation zuletzt;
- zentraler Kernel setzt maximale Tiefe, Breite, Calls, Kosten und Deadline;
- jedes Handoff ist eine typisierte, provenance-tragende untrusted Message;
- Worker erhalten disjunkte Minimal-Capabilities und keine gegenseitigen Credentials;
- Aggregation durch deterministische Regeln, wo möglich; Modell-Judge nur als kalibriertes Signal;
- gepaarter Vergleich gegen die einfachere Baseline auf identischem Eval-Set;
- Messung von Erfolgsqualität **und** neuen Fehlermodi, Latenz und Gesamtkosten.

### Gate G5: Komplexitätszulassung

**Evidenz:** vorab festgelegter minimaler Nutzeneffekt gegenüber Baseline; Unsicherheitsintervall; kein unvertretbarer Rückgang in Sicherheits-Slices; Budget-/Loop-Stresstest; Handoff-Schema- und Provenienztests; Abbruch jeder Teilgruppe getestet.

**DoD:** Der zusätzliche Agent oder das zusätzliche Modell löst einen benannten Failure Mode oder verbessert ein Zielmaß reproduzierbar. Ein Mehrheitsentscheid wird nicht als Wahrheit bezeichnet. Der Kernel bleibt einzige Autorität für Tools, Freigaben und Commit.

**Rollback:** Router deaktiviert zusätzliche Worker und verwendet den letzten zugelassenen Single-Modell-Pfad. Laufende Worker werden gecancelt; verspätete Resultate scheitern an `run_id`, Zustand und Versionsprüfung.

## Stufe 6 — High Assurance für ausgewählte Pfade

### Ziel

Für besonders kritische, klar begrenzte Prozesse zusätzliche formale, isolierende und Supply-Chain-Kontrollen einführen. Nicht das gesamte KI-System wird „formal verifiziert“.

### Umsetzung

- Invarianten und Liveness-Annahmen des Kernels formal spezifizieren, etwa „Commit nur nach Allow und gültiger Freigabe“;
- Model Checking für kleine, sicherheitskritische Zustandsräume; Model-Code-Conformance über generierte Tests und Runtime Assertions;
- getrennte Konten/Projekte, ephemere Sandbox, read-only Basis, kein Default-Egress;
- signierte und hash-gepinnte Artefakte, kontrollierter Build, Provenienz und Zwei-Personen-Review;
- Policy-Änderungen als Code mit Tests, Review, gestuftem Rollout und Audit;
- Red-Team- und Incident-Übungen einschließlich kompromittierter Datenquelle, Toolserver und Operator-Credential;
- SLO-Burn-Rate, Security-Signale und automatische Circuit Breaker.

TLA+ kann Safety- und Liveness-Eigenschaften eines Modells prüfen, überbrückt aber nicht automatisch die Modell-Code-Lücke ([Lamport](https://lamport.org/pubs/spec-and-verifying.pdf)). SLSA-Stufen erhöhen Anforderungen an Build-Provenienz und -Integrität; sie bescheinigen keine fachliche Korrektheit des KI-Systems ([SLSA v1.0](https://slsa.dev/spec/v1.0/levels)).

### Gate G6: High-Assurance-Zulassung

**Evidenz:** überprüfte Invarianten und dokumentierte Annahmen; Conformance-Tests gegen Implementierung; isolationsspezifische Escape-/Egress-Tests; attestierte Artefakte; Break-glass-Test; unabhängige Security- und Betriebsfreigabe; Recovery-Übung mit protokollierten Zeiten und Befunden.

**DoD:** Der genaue Assurance-Scope ist benannt—Komponente, Invariante, Umgebung und Version. Jede formale Aussage hat eine Traceability-Kette zu Runtime Assertion oder Test. Kritische Abweichungen lösen fail-closed oder einen dokumentierten degradierten read-only Modus aus.

**Rollback:** Signiertes letztes Release-Manifest redeployen; riskante Capabilities und Egress zentral sperren; alte Workflow-Version für kompatible Runs bereitstellen; bei Integritätszweifel Credentials rotieren und betroffene Artefakte quarantänisieren.

## Querschnittliche Release-Gates

Jeder Change wird nach seinem **Risiko-Delta**, nicht nur nach Dateityp, eingestuft. Ein Prompt kann Berechtigungsverhalten ebenso stark ändern wie Code.

| Änderung | Mindestprüfung | Erfordert erneutes höheres Gate |
|---|---|---|
| Prompt/Textbeispiel | Contract-Eval, Qualitäts-/Safety-Slices | wenn Toolwahl oder Datenumfang beeinflusst wird |
| Modell/Provider | vollständiges Offline-Eval, Datenschutz, Latenz/Kosten, Canary | ja, ab der Stufe mit Produktionstools |
| Schema/Validator | Kompatibilitäts-, Property- und Fuzz-Tests | wenn erlaubte Aktion oder Semantik erweitert wird |
| Policy/IAM | Policy-Unit- und Negativtests, Review, Shadow Decision | immer das entsprechende Side-Effect-Gate |
| Tool-Adapter | Contract-, Idempotenz-, Fault-Injection- und Reconciliation-Test | immer G3; bei durable Nutzung auch G4 |
| Workflow-Code | Transition Coverage und historische Replay-Tests | ab G2; bei persistierten Runs G4 |
| Eval-Set/Schwelle | Review auf Leakage, Repräsentativität und Regression | Governance-Freigabe, wenn Schwelle sinkt |

### Universelle Stop-Kriterien

Ein Rollout stoppt oder fällt auf die sichere Vorstufe zurück, wenn eines zutrifft:

- unbekannter oder unautorisierter Side Effect;
- fehlende Audit-Korrelation oder nicht rekonstruierbare Version;
- Überschreitung des festgelegten Error Budgets;
- signifikante Regression in einem kritischen Safety-Slice;
- ungeklärte Doppelwirkung oder wachsender Reconciliation-Backlog;
- Secret oder verbotene Datenklasse in Modellkontext/Telemetry;
- Replay-Inkompatibilität oder Policy-Enforcer-Bypass.

„Noch keine ausreichenden Daten“ ist kein bestandener Gate-Nachweis. Dann bleibt das System in Shadow/Canary oder auf der vorherigen Stufe.

## Mess- und Evidenzplan

### Deterministische Suite pro Commit

- Schema-, Parser-, Transition- und Policy-Unit-Tests;
- Property Tests für Budgets, Zustandsversionen und Approval-Bindung;
- Fuzzing von Toolargumenten, URLs, Encodings und Grenzwerten;
- Negativtests gegen jede verbotene Capability;
- Replay- und Migrationssuite ab Stufe 4;
- Supply-Chain- und Artefaktverifikation ab Stufe 6.

### Statistische Suite pro Release

- eingefrorenes Holdout plus aktuelle produktionsnahe Slices;
- Qualität, Abstention/Refusal, Sicherheitsdetektion und schwere Fehlhandlungen getrennt;
- Latenz und Kosten einschließlich Retries und Subagenten;
- Konfidenzintervalle beziehungsweise Unsicherheit und vordefinierte Vergleichsregel;
- manuelle Stichprobe nach risikobasierter, dokumentierter Auswahl;
- Driftvergleich nach Sprache, Mandant, Aufgabentyp und Datenquelle.

Ein LLM-as-Judge darf skalieren helfen, wird aber gegen menschlich oder deterministisch bewertete Fälle kalibriert. Es bleibt ein statistischer Grader und darf kein technisches Autorisierungs- oder Release-Gate allein entscheiden.

## Betriebsübergabe und Verantwortungen

| Verantwortung | Primärer Owner | Verpflichtende Evidence |
|---|---|---|
| fachliche Richtigkeit und Fehlerschaden | Product/Domain | Eval-Vertrag, Freigabeschwellen, manuelle Stichproben |
| Zustandsautomat und Recovery | Platform Engineering | Transition-, Crash-, Replay- und Restore-Tests |
| Toolrechte und Policy | Security + Tool Owner | Capability-Matrix, Negativtests, Decision Logs |
| Daten und Retention | Data/Privacy | Datenfluss, Rechtsgrundlage, Löschtest, Zugriffsaudit |
| Modell-/Promptänderung | ML/AI Engineering | gepinnte Versionen, Regression-Eval, Canary |
| Incident und Rollback | Operations | Runbook, On-call, Übungsprotokoll, RTO/RPO-Ziele |

Ein Owner darf Evidence liefern, aber bei High-Risk-Pfaden nicht allein die eigene Kontrolle abnehmen.

## Praktische Gate-Checkliste

Vor jeder Stufenerhöhung:

- [ ] Scope, Datenklassen, externe Wirkungen und neue Failure Domains sind aktuell.
- [ ] Garantie-Ledger trennt erzwingbar, konditional, statistisch und heuristisch.
- [ ] Alle deterministischen Tests und Negativtests bestehen reproduzierbar.
- [ ] Eval-Daten und Schwellen wurden vor Ergebnisbetrachtung versioniert.
- [ ] Modell, Prompt, Policy, Schema, Workflow und Tools sind gepinnt.
- [ ] Least-Privilege- und Bypass-Prüfung ist abgeschlossen.
- [ ] Observability erkennt Budget-, Policy-, Quality- und Recovery-Fehler getrennt.
- [ ] Canary-Umfang und automatische Stop-Kriterien sind konfiguriert.
- [ ] Rollback wurde in der Zielumgebung geübt, nicht nur beschrieben.
- [ ] Nach Rollback bleiben ausstehende Side Effects und Datenmigrationen beherrschbar.
- [ ] Restrisiken, Annahmen, Ausnahmegenehmigungen und Ablaufdaten sind signiert.

## Nicht-Garantien und typische Fehlwege

- Das Erreichen einer Stufe ist keine pauschale Zertifizierung des Gesamtsystems.
- Mehr Tests garantieren keine Fehlerfreiheit; sie liefern Evidence für einen definierten Scope.
- Canary und SLO schützen nicht jeden einzelnen Nutzerfall.
- Durable State garantiert weder korrekte Geschäftslogik noch Exactly-once-Nebenwirkungen.
- Menschliche Freigabe kann manipuliert oder falsch sein; Payload-Bindung verhindert nur unbemerkte Änderung danach.
- Eine Sandbox beseitigt keine Fehlkonfiguration, gestohlene Credentials oder alle Seitenkanäle.
- Multi-Agent-Konsens ist keine unabhängige Bestätigung, wenn Modelle, Daten oder Prompts korrelieren.
- Ein organisatorischer Rahmen wie NIST AI RMF strukturiert Risikomanagement, ersetzt aber keine Runtime-Enforcer.

Typische Anti-Patterns sind ein autonomer Agent als erste Produktionsversion, freie Tool-/URL-Parameter, globale Cloud-Credentials, unbegrenzte „retry until success“-Schleifen, ein einziger aggregierter Quality Score und Rollback-Pläne, die irreversible Außenwirkungen ignorieren.

## Entscheidungskriterien für die nächste Stufe

Die nächste Stufe wird nur gewählt, wenn die aktuelle Stufe einen konkreten Engpass zeigt:

- unzureichende Zerlegbarkeit mit einem Call → Stufe 2;
- notwendige Außenwirkung → Stufe 3;
- lange Pausen und Recovery-Anforderung → Stufe 4;
- nachgewiesener Nutzen durch Spezialisierung/Parallelität → Stufe 5;
- klar abgegrenzter Hochrisikopfad mit prüfbaren Invarianten → Stufe 6.

Fehlt dieser Nachweis, bleibt die einfachere Architektur der bevorzugte Produktionszustand.

## Weiterführende Dokumente

Siehe [Referenzarchitektur](../08-referenzarchitektur/), [Garantie-Taxonomie](../00-garantie-taxonomie.md), [Workflow-first](../01-workflow-first/), [Durable Execution](../03-durable-execution/), [Sicherheit und Isolation](../05-sicherheit-und-isolation/), [Evaluation und Observability](../06-evaluation-observability/) und [Formale Methoden](../07-formale-methoden/).
