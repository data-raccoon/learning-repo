# Formale Methoden für KI-Harnesses

[Kurzfassung](KURZFASSUNG.md) · [Beispielimplementierung](beispiel/README.md) · [Gesamtübersicht](../README.md)

## Kurzfassung

Eine ausführbare, dependency-freie Miniatur mit bounded Model Checker, kürzestem Gegenbeispiel und Runtime-Monitor befindet sich unter [`beispiel/`](beispiel/README.md).

Formale Methoden sind besonders wertvoll für den deterministischen Kernel eines KI-Harnesses: Zustandsautomat, Handoffs, Freigaben, Budgets, Retry-/Commit-Protokolle und Berechtigungen lassen sich als präzise Transitionen und Invarianten modellieren. Model Checking kann innerhalb eines endlichen, explizit begrenzten Zustandsraums alle modellierten Ausführungen untersuchen und Gegenbeispiele liefern. Runtime Verification prüft die tatsächlich beobachtete Ereignisspur gegen formale Regeln.

Die probabilistische Semantik freier Modelltexte wird dadurch nicht allgemein bewiesen. Ein korrektes abstraktes Modell ist nicht automatisch konform zum Produktivcode; abstrahierte Eingaben, unmodellierte Infrastruktur, fehlerhafte Instrumentierung und State-Space-Begrenzungen bleiben. Die belastbare Position lautet daher: formale Methoden für kritische Kontrollprotokolle, deterministische Runtime-Enforcer für konkrete Nebenwirkungen und statistische Evals für die Qualität probabilistischer Blätter.

## Anwendungsbereich

Geeignet sind vor allem diskrete Kontrollfragen:

- Welche Zustandsübergänge und Handoffs sind erlaubt?
- Kann eine Nebenwirkung ohne Autorisierung oder Freigabe committed werden?
- Können Retries doppelte Buchungen erzeugen?
- Bleiben Budget, Capability und Mandantengrenze über Delegationen erhalten?
- Kann ein Workflow deadlocken, livelocken oder für immer auf Freigabe warten?
- Ist Recovery nach Crash/Timeout im modellierten Fehlerfall möglich?

Weniger geeignet ist der universelle Beweis, dass ein Modelltext wahr, hilfreich, fair oder ungefährlich ist. Solche offenen semantischen Eigenschaften besitzen meist weder eine vollständige formale Spezifikation noch einen handhabbaren Zustandsraum.

## 1. Begriffe und Spezifikationsobjekt

Ein Harness wird als Zustandsübergangssystem beschrieben:

```text
State = (
  run_status,
  current_actor,
  capabilities,
  budget,
  approvals,
  pending_effects,
  committed_effects,
  idempotency_keys,
  retries,
  event_log
)

Init(State)
Next(State, State')
Spec == Init /\ [][Next]_State /\ Fairness
```

Die Schreibweise lehnt sich an TLA+ an: `Init` beschreibt erlaubte Anfangszustände, `Next` die Übergangsrelation und temporale Formeln Eigenschaften ganzer Ausführungen. TLA+ kann Safety- und Liveness-Eigenschaften ausdrücken; TLC durchsucht endliche Instanzen eines Modells nach Verletzungen ([Lamport, Specifying and Verifying Systems](https://lamport.azurewebsites.net/pubs/spec-and-verifying.pdf)).

### Safety und Liveness

**Safety** bedeutet vereinfacht: „Etwas Schlechtes passiert nie.“ Eine Verletzung besitzt einen endlichen Gegenbeispiel-Prefix. Beispiele:

```text
NoCommitWithoutAuthorization ==
  [] (commit(e) => authorized(e.subject, e.action, e.resource))

ApprovalBeforeHighRiskCommit ==
  [] (commit(e) /\ high_risk(e) => approved(e.id, e.scope))

AtMostOneLogicalCommit ==
  [] (Cardinality(commits_by_key[e.idempotency_key]) <= 1)

BudgetNeverNegative == [] (budget >= 0)

TenantIsolation ==
  [] (read(actor, object) => actor.tenant = object.tenant \/ explicit_grant(actor, object))
```

**Liveness** bedeutet: „Etwas Gutes geschieht schließlich“, beispielsweise dass jeder angenommene Run irgendwann `completed`, `failed`, `cancelled` oder `escalated` erreicht. Liveness benötigt meist Annahmen über Fairness, verfügbare Dienste, Nachrichtenlieferung und menschliche Reaktion. Ohne diese Annahmen ist „jede Freigabe wird irgendwann beantwortet“ unhaltbar.

Safety und Liveness dürfen nicht verwechselt werden. Ein System kann sicher sein, weil es nie etwas committed, und dennoch nutzlos festhängen. Umgekehrt kann es jeden Run beenden, dabei aber unerlaubte Nebenwirkungen ausführen.

## 2. Invarianten für Agenten- und Multi-Modell-Harnesses

Die wichtigsten Invarianten liegen an den deterministischen Grenzen, nicht im Prompt:

### Identität und Delegation

- Ein Subagent erhält höchstens die Capabilities seines Auftraggebers, weiter eingeschränkt auf den Task.
- Ein Handoff ändert nicht stillschweigend Mandant, Nutzeridentität oder Risikoklasse.
- Eine Modellroute kann keine Policy umgehen; alle Providerpfade nutzen denselben Enforcement Point.
- Nur der Root-Orchestrator darf neue Worker erzeugen, falls das Architekturmodell One-Level-Delegation verlangt.

### Nebenwirkungen und Commit

- Ein Modell erzeugt nur einen Vorschlag; ausschließlich der Tool-Adapter kann committen.
- High-Risk-Commits benötigen eine gültige, noch nicht verbrauchte Freigabe mit passendem Scope.
- Derselbe Idempotency-Key führt höchstens zu einem logischen Effekt.
- Nach unbekanntem Timeout wird der externe Zustand abgefragt, bevor erneut committed wird.
- Abbruch entfernt keine bereits bestätigte Außenwirkung aus dem Audit-Log.

### Ressourcen und Terminierung

- Token-, Kosten-, Turn-, Zeit- und Subagentenbudgets sind monoton verbraucht und können durch Retry/Handoff nicht zurückgesetzt werden.
- Jeder Loop besitzt eine deterministische Stop-, Fail- oder Escalation-Kante.
- Ein terminaler Zustand erlaubt keine weiteren Tool-Commits.

### Information und Datenschutz

- Geheimnisse werden nie Teil eines Modellprompts, wenn das Zieltool sie serverseitig verwenden kann.
- Tool-Resultate einer Capability dürfen nur an Akteure mit mindestens derselben Leseberechtigung weitergegeben werden.
- Audit-Ereignisse enthalten keine verbotenen Payload-Felder.

Eine Invariante ist nur so gut wie ihre formale Definition. Begriffe wie „riskant“, „berechtigt“ oder „sensitiv“ müssen auf konkrete Zustandsvariablen und Entscheidungsfunktionen reduziert werden.

## 3. Model Checking

Beim **Model Checking** wird ein endliches Modell systematisch gegen Eigenschaften geprüft. Der praktische Ablauf:

1. Systemgrenze und Failure Domains festlegen.
2. Zustandsvariablen, Anfangszustände und atomare Aktionen definieren.
3. Umgebung und Fehler nondeterministisch modellieren: Nachrichtenreihenfolge, Duplicate, Drop, Crash, Retry, verspätete Freigabe.
4. Invarianten und Liveness-Eigenschaften getrennt formulieren.
5. Kleine endliche Bounds wählen und Symmetrie/Abstraktion nutzen.
6. Model Checker laufen lassen; jede Gegenbeispielspur als Design- und Testfall behandeln.
7. Coverage der Aktionen, Grenzen und Annahmen dokumentieren.

TLC kann Safety- und Liveness-Eigenschaften von TLA+-Spezifikationen prüfen ([Lamport](https://lamport.azurewebsites.net/pubs/spec-and-verifying.pdf)). Für Multi-Agent-Systeme unterstützt MCMAS symbolische Prüfung temporaler, epistemischer und strategischer Eigenschaften, also auch Aussagen über Wissen und Handlungsmöglichkeiten von Agenten ([Lomuscio, Qu und Raimondi, peer-reviewed](https://link.springer.com/article/10.1007/s10009-015-0378-x)). Das macht MCMAS interessant, wenn etwa „Agent A weiß vor Freigabe nicht, welches Geheimnis Agent B besitzt“ präzise modellierbar ist. Es beweist jedoch nicht, was ein Sprachmodell intern „weiß“; geprüft wird die formalisierte epistemische Relation.

### State-Space Explosion

Die Zustandszahl wächst kombinatorisch mit Agenten, Nachrichten, Budgets, Toolresultaten, Queue-Reihenfolgen und Fehlermöglichkeiten. Schon kleine Bounds können Millionen Zustände erzeugen. Typische Gegenmaßnahmen sind:

- Datenwerte auf Äquivalenzklassen abstrahieren, etwa `low/high risk` statt freier Text;
- kleine Instanzen prüfen, etwa zwei Agenten und zwei Requests;
- symmetrische Agenten oder Nachrichten reduzieren;
- unabhängige Aktionen mit Partial-Order-Reduktion zusammenfassen;
- Komponenten separat modellieren und Schnittstellenannahmen explizit machen;
- Safety zuerst, Liveness gezielt mit Fairnessannahmen prüfen;
- bounded Model Checking klar als begrenzt berichten.

Die Grenzen sind Teil der Aussage. „TLC fand bis 3 Agenten, 2 Retries und 4 Queue-Elementen keine Verletzung“ ist korrekt; „das System ist verifiziert“ verschweigt den Scope.

Die MCMAS-Publikation benennt State-Space Explosion als grundlegende Herausforderung. Ouyang et al. zeigen am produktiven ZooKeeper-Kontext den Granularitätskonflikt besonders konkret: feine Spezifikationen vergrößern den Zustandsraum, grobe Spezifikationen vergrößern die Modell-Code-Lücke. Ihre multi-granularen, komponierbaren Spezifikationen sind eine mögliche Engineering-Antwort, keine allgemeine Beseitigung des Problems ([EuroSys 2025, peer-reviewed](https://doi.org/10.1145/3689031.3696069)).

## 4. Modell-Code-Lücke

Ein Model Checker prüft das Modell, nicht automatisch den ausgeführten Code. Die **Modell-Code-Lücke** umfasst:

- im Modell atomare Aktionen, die im Code aus mehreren unterbrechbaren Schritten bestehen;
- abstrahierte Daten und Fehler, die reale Sonderfälle verbergen;
- unterschiedliche Retry-, Timeout- oder Queue-Semantik;
- fehlerhafte Übersetzung einer Policy in Implementierung;
- Framework-, SDK-, Datenbank- und Cloudverhalten außerhalb des Modells;
- spätere Codeänderungen ohne Aktualisierung der Spezifikation.

Gegenmaßnahmen:

- Spezifikation und Code gemeinsam versionieren und Review-Ownership festlegen;
- Zustandsübergänge im Code an wenige explizite Reducer/Commands binden;
- aus Gegenbeispielen ausführbare Regressionstests generieren;
- Trace-Ereignisse so instrumentieren, dass sie formalen Aktionen entsprechen;
- Model-based Testing: aus dem Modell Aktionsfolgen erzeugen und am System prüfen;
- Refinement-/Conformance-Mapping für jede Aktion dokumentieren;
- geänderte Module feiner, stabile Umgebung gröber spezifizieren;
- CI-Gate aus Model Check, Conformance-Tests und Runtime-Monitoren zusammensetzen.

Ouyang et al. berichten für ZooKeeper über TLA+-Modelle verschiedener Granularität und explizite Model-Code-Conformance-Prüfung. Die Fallstudie belegt den Nutzen des Ansatzes in diesem System; sie liefert keinen pauschalen Beweis, dass jedes so modellierte Produktivsystem konform ist ([ACM/EuroSys 2025](https://doi.org/10.1145/3689031.3696069)).

## 5. Runtime Verification

**Runtime Verification (RV)** prüft eine beobachtete Ausführungsspur während oder nach der Ausführung gegen eine formale Eigenschaft. Ein Monitor kann beispielsweise den Automaten

```text
proposed -> authorized -> approved? -> committed -> reconciled
```

verfolgen und `commit` aus einem unzulässigen Zustand ablehnen oder alarmieren. RV ergänzt Model Checking:

- Model Checking untersucht viele mögliche Abläufe eines abstrahierten Modells vorab.
- Runtime Verification untersucht reale, aber nur tatsächlich beobachtete Abläufe.

RV kann als **Enforcement** synchron vor einer Aktion oder als **Detection** asynchron nach Ereignissen laufen. Nur ein fail-closed, nicht umgehbarer synchroner Monitor kann die konkrete verbotene Transition deterministisch verhindern. Ein Alarm nach dem Commit verhindert den Effekt nicht.

Notwendige Annahmen:

- alle relevanten Ereignisse erreichen den Monitor;
- Ereignisidentität, Reihenfolge und Korrelation sind korrekt;
- der Monitor ist nicht über einen alternativen Toolpfad umgehbar;
- seine Spezifikation entspricht der beabsichtigten Policy;
- Fail-open/fail-closed und Monitorausfall sind explizit behandelt.

Die Forschung definiert RV als dynamische Auswertung von Execution Traces gegen formale Spezifikationen und hebt hervor, dass Erfassung und Übermittlung der Ereignisse kritisch sind; unvollständige oder unpräzise Traces können ein belastbares Urteil verhindern ([Taleb, Hallé und Khoury, 2023, Survey](https://doi.org/10.1016/j.cosrev.2023.100594)). Ein grüner Monitor beweist deshalb bei Telemetrielücken nichts über nicht beobachtete Aktionen.

## 6. Probabilistische Blätter formalisieren: Reichweite

Ein Sprachmodell kann im formalen Harness als nondeterministische oder adversariale Komponente modelliert werden:

```text
LLMOutput ∈ AllSchemaValidOutputs
```

Damit lässt sich beweisen: **Für jede schema-valide Modellausgabe**, die der Modellgrenze entspricht, verhindert der Kernel beispielsweise einen unautorisierten Commit. Das ist stärker und ehrlicher als die Annahme, das Modell befolge seinen Prompt.

Die Menge `AllSchemaValidOutputs` muss dennoch handhabbar abstrahiert werden. Freitext wird typischerweise auf Kontrollklassen wie `request_tool`, `answer`, `handoff`, `malformed` reduziert. Der Beweis umfasst dann die Parser- und Adaptersemantik nur, wenn diese korrekt modelliert oder konform getestet ist.

Nicht formal abgedeckt sind ohne zusätzliche Spezifikation unter anderem:

- Wahrheit und Vollständigkeit generierter Aussagen;
- gesellschaftliche Fairness offener Antworten;
- unbekannte Prompt-Injection-Varianten;
- semantische Äquivalenz beliebiger natürlicher Sprache;
- Modellanbieter-Verhalten außerhalb der dokumentierten API;
- physische oder organisatorische Folgen einer formal erlaubten Aktion.

Hier bleiben deterministische Domänenprüfer, Evals, Red Teaming und menschliche Freigaben notwendig; siehe [Evaluation und Observability](../06-evaluation-observability/).

## 7. Beispiel: High-Risk-Tool-Protokoll

### Zustände

`Draft`, `Validated`, `Authorized`, `AwaitingApproval`, `Approved`, `Committed`, `Failed`, `Cancelled`.

### Safety-Eigenschaften

- `Committed` ist nur nach `Authorized` erreichbar.
- Bei `high_risk` liegt vor `Committed` eine scope-passende Freigabe vor.
- `cost_spent <= cost_limit` und `turns <= turn_limit`.
- Pro Idempotency-Key existiert höchstens ein logischer Commit.
- `Cancelled` und `Failed` erlauben keinen neuen Commit.

### Liveness-Eigenschaften unter Annahmen

- Wenn Tool und Policy-Dienst verfügbar sind, das Retry-Budget reicht und eine erforderliche Freigabe schließlich beantwortet wird, erreicht jeder akzeptierte Run einen terminalen Zustand.
- Nach einem Crash wird ein nichtterminaler Run bei verfügbarer Persistenz schließlich fortgesetzt oder eskaliert.

### Zu modellierende Störungen

- Crash vor und nach externem Effekt, aber vor lokaler Bestätigung;
- doppelte und verspätete Nachrichten;
- Timeout mit unbekanntem Toolstatus;
- Widerruf einer Capability zwischen Planung und Commit;
- Freigabe für falsche Ressource oder abgelaufene Freigabe;
- konkurrierende Runs mit demselben Idempotency-Key;
- Budgetverbrauch durch Retry und Handoff.

Das Modell sollte nicht „LLM wählt immer die richtige Aktion“ annehmen. Es lässt jede erlaubte Kandidatenaktion zu und beweist, dass der Kernel gefährliche Kandidaten blockiert.

## 8. Erreichbare Garantien und Nicht-Garantien

| Mechanismus | Einordnung | Aussage bei erfüllten Voraussetzungen | Grenze |
|---|---|---|---|
| TLA+/TLC Model Check | formal, annahmengebunden | Eigenschaft gilt für alle untersuchten Zustände des endlichen Modells | Modell-Code-Lücke, Bounds, falsche Spezifikation |
| MCMAS | formal, annahmengebunden | temporale/epistemische/strategische Eigenschaft gilt im modellierten MAS | kein Beweis über interne Semantik realer LLMs |
| Runtime-Enforcer | deterministisch erzwingbar | beobachtete verbotene Transition wird am Enforcer blockiert | Bypass, fehlende Events, falsche Policy, Fail-open |
| asynchroner Runtime-Monitor | deterministische Erkennung für vollständige Spur | Verletzung der monitorbaren Eigenschaft wird erkannt | verhindert bereits erfolgte Nebenwirkung nicht |
| Model-based Tests | empirisch/deterministisch pro Test | konkrete generierte Fälle erfüllen Assertions | keine Vollständigkeit über ungetestete Ausführungen |
| Evals/SLOs | statistisch | Häufigkeit in Stichprobe/Beobachtungsfenster | kein formaler Beweis |

## 9. Failure Modes und Anti-Patterns

- **„TLA+ vorhanden“ als Gütesiegel:** Ein ungeprüftes oder triviales Modell erzeugt keine relevante Garantie.
- **LLM schreibt die Spezifikation und bestätigt sie selbst:** Das kann Entwurf beschleunigen, ersetzt aber weder Fachreview noch unabhängigen Check.
- **Happy-Path-Modell:** Crashs, Duplikate, Reordering und Widerrufe fehlen; genau dort liegen oft Protokollfehler.
- **Versteckte Fairnessannahmen:** Liveness wirkt bewiesen, weil der Scheduler oder Mensch unrealistisch fair modelliert ist.
- **Unbegrenzte Daten im endlichen Checker:** State-Space explodiert oder Bounds werden stillschweigend so klein, dass relevante Fälle fehlen.
- **Monitor nur im Logpfad:** Ein alternativer direkter Toolzugriff umgeht die vermeintliche Invariante.
- **Telemetry equals truth:** verlorene, gesampelte oder falsch geordnete Events führen zu falschen RV-Urteilen.
- **Modell und Code driften:** Die Spezifikation bleibt grün, während Produktivcode neue Transitionen erhält.

## 10. Entscheidungskriterien

- Hat die Eigenschaft hohen Schadenswert und lässt sie sich als diskrete Zustandsregel formulieren? Dann formal spezifizieren und zur Laufzeit erzwingen.
- Geht es um Nebenläufigkeit, Retry, Recovery oder Handoff? Dann Model Checking früh einsetzen; Beispiele allein decken Interleavings schlecht ab.
- Ist eine Eigenschaft nur auf beobachtbaren Ereignissen formulierbar? Dann Runtime Verification nutzen und Event-Vollständigkeit absichern.
- Ist das Kriterium semantisch offen oder subjektiv? Dann nicht künstlich als formalen Beweis darstellen; Evals und Human Review verwenden.
- Ist der Zustandsraum zu groß? Dann Abstraktion und komponentenweise Spezifikation einsetzen, Bounds offenlegen und verbleibendes Risiko akzeptieren oder Architektur vereinfachen.
- Kann Code-Conformance nicht plausibel hergestellt werden? Dann den Garantieclaim auf das Modell begrenzen und den produktiven Schutz durch kleine, geprüfte Enforcer realisieren.

## 11. Umsetzbare Checkliste

- [ ] Systemgrenze, Assets, Failure Domains und Umgebungsannahmen dokumentieren.
- [ ] Zustandsvariablen und atomare Aktionen des Kontrollkernels definieren.
- [ ] Safety, Liveness und reine Qualitätsziele strikt trennen.
- [ ] Autorisierung, Freigabe, Budget, Delegation, Idempotenz und Terminalität als Invarianten formulieren.
- [ ] Modelloutput nondeterministisch/adversarial statt prompt-treu modellieren.
- [ ] Crash, Duplicate, Reordering, Timeout, Partition und Widerruf einbeziehen.
- [ ] Fairness- und Verfügbarkeitsannahmen für jede Liveness-Aussage nennen.
- [ ] Bounds, Symmetriereduktionen, ausgelassene Variablen und erreichte Zustände berichten.
- [ ] Gegenbeispieltraces in Regressionstests und Designänderungen überführen.
- [ ] Jede formale Aktion auf konkrete Codepfade und Telemetrieereignisse abbilden.
- [ ] Modell-Code-Conformance in CI prüfen und bei Drift blockieren.
- [ ] Kritische Runtime-Monitore synchron, fail-closed und nicht umgehbar platzieren.
- [ ] Monitor- und Telemetrieausfall als eigene Zustände modellieren.
- [ ] Formale Evidence, Toolversion und Spezifikationshash mit dem Release archivieren.
- [ ] Nach jeder Architektur-, Policy-, Tool- oder Retry-Änderung Modell und Claims neu prüfen.

## Quellenhinweise

Die zentralen Primär- und Peer-Review-Quellen sind Lamports [TLA+-Überblick](https://lamport.azurewebsites.net/pubs/spec-and-verifying.pdf), die [MCMAS-Publikation](https://link.springer.com/article/10.1007/s10009-015-0378-x), die ZooKeeper-Fallstudie zu [multi-granularen Spezifikationen und Model-Code-Conformance](https://doi.org/10.1145/3689031.3696069) sowie der [Survey zu Unsicherheit in Runtime Verification](https://doi.org/10.1016/j.cosrev.2023.100594). Formale Toolfeatures und Syntax sind vor Anwendung gegen die konkret eingesetzte Version zu prüfen. Stand dieses Dokuments: 22. Juli 2026.
