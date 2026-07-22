# Evaluation und Observability für KI-Harnesses

[Kurzfassung](KURZFASSUNG.md) · [Beispielimplementierung](beispiel/README.md) · [Gesamtübersicht](../README.md)

## Kurzfassung

Evaluation beantwortet empirisch, wie häufig ein konkretes System unter definierten Bedingungen ein gewünschtes Verhalten zeigt. Observability macht einzelne Ausführungen und Verteilungen untersuchbar. Beides ist unverzichtbar, aber weder ein hoher Eval-Score noch ein eingehaltenes Service Level Objective (SLO) beweist Korrektheit für unbekannte Eingaben oder künftige Modellversionen.

Der robuste Ansatz kombiniert deterministische Ergebnis- und Policy-Prüfer, mehrfache Trials für probabilistische Schritte, Trajectory-Evals für Prozessrisiken, gezielt kalibrierte LLM-Judges, menschliche Stichproben sowie Produktions-SLIs. Release-Gates dürfen nur jene Aussagen erzwingen, die ihre Prüfer tatsächlich abdecken. Traces sollen Zustandsübergänge, Tool-Aufrufe, Modell- und Konfigurationsversionen sowie Kosten sichtbar machen, aber Prompts, Tool-Argumente, Ergebnisse, Geheimnisse und personenbezogene Daten standardmäßig nicht im Klartext erfassen.

## Anwendungsbereich

Dieses Kapitel gilt für Single-Agent-, Multi-Agent- und Multi-Modell-Systeme sowie für deterministische Workflows mit probabilistischen Modellschritten. Es behandelt:

- Offline-Evaluation vor einem Release;
- Regressionstests und Release-Gates;
- Trajectory-Evaluation mehrstufiger Ausführungen;
- Produktionsbeobachtung, SLOs, Canaries und Incident-Analyse;
- Datenschutz und Zugriffsschutz für Eval-Artefakte und Telemetrie.

Es behandelt nicht den mathematischen Nachweis aller möglichen Abläufe; dafür siehe [Formale Methoden](../07-formale-methoden/).

## 1. Was gemessen wird

Eine Agent-Evaluation besteht mindestens aus Aufgabe, Ausführungsumgebung, einem oder mehreren Trials, aufgezeichneter Trajectory und Gradern. Die **Trajectory** ist die beobachtete Folge aus Modellantworten, Tool-Aufrufen, Zustandsänderungen und Ergebnissen. Das **Outcome** ist der resultierende Welt- oder Systemzustand. Ein Agent kann etwa „Überweisung ausgeführt“ schreiben, obwohl im Buchungssystem keine Transaktion existiert. Deshalb ist der verifizierbare Outcome grundsätzlich stärker als die Selbstaussage des Modells. Anthropic trennt diese Begriffe ausdrücklich und empfiehlt die Kombination aus codebasierten, modellbasierten und menschlichen Gradern ([Anthropic, Demystifying Evals](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents)).

Die Messeinheit muss zur Behauptung passen:

| Behauptung | Geeignete Evidenz | Reichweite |
|---|---|---|
| „Der Tool-Adapter lehnt Beträge über dem Limit ab“ | deterministischer Unit-/Property-Test plus Runtime-Policy | für geprüften Codepfad und spezifizierte Eingaben; Runtime-Gate kann den konkreten Aufruf erzwingen |
| „Der Agent löst typische Supportfälle zuverlässig“ | repräsentative Aufgabenbank, mehrere Trials, Konfidenzintervalle | statistisch für die Stichprobe und Annahmen |
| „Das System verletzt nie eine Sicherheitsinvariante“ | Runtime-Enforcement oder formale Verifikation | nur innerhalb des Enforcers beziehungsweise des formalen Modells |
| „99 % der gültigen Anfragen enden in 30 s“ | Produktions-SLI über definiertes Fenster | beobachtete Dienstgüte, kein Beweis für jede Anfrage |

## 2. Eval-Pyramide

### 2.1 Deterministische Grader zuerst

Codebasierte Grader sind reproduzierbar, schnell und erklärbar. Beispiele sind:

- Schema-, Typ- und Wertebereichsprüfung;
- Unit-, Integrations- und End-to-End-Tests;
- statische Analyse und Security-Scanner;
- Datenbankabfrage des Endzustands;
- Prüfung von ACL-Entscheidungen, Budget, Tool-Parametern und erlaubten Zustandsübergängen;
- Metamorphic und Property-based Tests, etwa „Umordnung irrelevanter Dokumente ändert die Berechtigung nicht“.

Ein deterministischer Grader garantiert jedoch nur, dass seine kodierte Bedingung für den konkreten Prüfgegenstand erfüllt ist. Er kann falsch spezifiziert, unvollständig oder vom Agenten ausnutzbar sein. Zu enge String-Matches lehnen gültige Varianten ab; zu schwache Tests lassen semantisch falsche Ergebnisse passieren. Anthropic empfiehlt daher deterministische Grader, wo möglich, warnt aber vor brittlen Pfadprüfungen und rät bei offenen Lösungswegen eher zur Outcome-Prüfung ([Anthropic](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents)).

### 2.2 Trajectory-Evals

Nur den Endzustand zu prüfen reicht nicht, wenn der Weg selbst Risiko erzeugt. Ein Agent kann am Ende korrekt antworten, zuvor aber ein Geheimnis an ein nicht erlaubtes Tool gesendet, unnötig viele Subagenten gestartet oder eine irreversible Aktion vor Freigabe versucht haben. Trajectory-Grader sollten deshalb mindestens prüfen:

- erlaubte Tool- und Handoff-Kanten;
- Identität und delegierte Capability je Schritt;
- Reihenfolge sicherheitskritischer Ereignisse, etwa `authorize -> approve -> commit`;
- Anzahl von Turns, Retries, Tokens, Modellaufrufen und Subagenten;
- Schleifen, wiederholte Fehler und Abbruchgrund;
- Übereinstimmung zwischen behauptetem und beobachtetem Outcome.

Nicht jede konkrete Tool-Reihenfolge sollte vorgeschrieben werden. Eine prozessuale Assertion ist sinnvoll, wenn sie eine Invariante repräsentiert; sie ist schädlich, wenn sie bloß eine erwartete Lösungsstrategie konserviert. Mehrere Grader pro Aufgabe trennen Outcome, Safety, Effizienz und Kommunikationsqualität. Einzelne fehlgeschlagene Assertions bleiben sichtbar, statt in einem undurchsichtigen Gesamtscore zu verschwinden.

### 2.3 Probabilistische Systeme brauchen mehrere Trials

Temperatureinstellung, Sampling, Anbieter-Routing, Tool-Latenz und veränderliche Außenwelt erzeugen Varianz. Ein einzelner Lauf ist keine stabile Schätzung. Für jeden Kandidaten sind deshalb mehrere Trials mit dokumentierter Stichprobengröße, Konfiguration und Unsicherheit erforderlich. Paarvergleiche sollten möglichst dieselben Aufgaben und kontrollierte Umgebungen nutzen. Berichtet werden nicht nur Mittelwerte, sondern auch Verteilung, Fehlermoden, Konfidenzintervalle und bei riskanten Ereignissen die absolute Zahl der Verstöße.

Eval-Umgebungen müssen pro Trial isoliert und zurückgesetzt sein. Gemeinsame Caches, Dateien, Git-Historie oder erschöpfte Ressourcen können Ergebnisse korrelieren und damit die Interpretation verfälschen ([Anthropic](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents)). Ein Framework wie [Inspect AI](https://inspect.aisi.org.uk/) stellt dafür Aufgaben, Datasets, Solver/Agenten, Scorer, Logs und Sandbox-Anbindungen bereit. Diese Features unterstützen Reproduzierbarkeit; sie beweisen weder die Repräsentativität eines Datasets noch die Korrektheit eines Scorers.

## 3. LLM-as-Judge richtig einordnen

Ein **LLM-as-Judge** bewertet Ausgaben anhand einer natürlichsprachlichen Rubrik. Das ist nützlich für Stil, Vollständigkeit, Gesprächsqualität oder offene Aufgaben, für die kein vollständiger deterministischer Oracle existiert. Es ist ein probabilistischer Messsensor, kein Verifier.

Bekannte Risiken sind:

- **Positionsbias:** In Paarvergleichen kann die Reihenfolge der Kandidaten das Urteil verändern; eine systematische Studie über viele Modelle und Aufgaben bestätigt, dass dies nicht nur Zufall ist ([Shi et al., 2025, peer-reviewed](https://aclanthology.org/2025.ijcnlp-long.18/)).
- **Verbosity-/Stilbias:** längere, selbstsichere oder oberflächlich gut formatierte Antworten können bevorzugt werden, obwohl sie nicht korrekter sind; LLM-Judge-Forschung dokumentiert mehrere solcher Bias-Klassen ([ICLR 2025](https://proceedings.iclr.cc/paper_files/paper/2025/file/fdca08d371e4b6c031397909e20043bd-Paper-Conference.pdf)).
- **Self-Preference und gemeinsame blinde Flecken:** ein Judge kann Stil oder Annahmen aus derselben Modellfamilie bevorzugen. Ein anderer Anbieter ist deshalb nicht automatisch unabhängig.
- **Prompt- und Rubriksensitivität:** kleine Änderungen an Kriterien, Referenzen oder Antwortformat können Scores verschieben.
- **Halluzinierte Begründung:** eine plausible Judge-Erklärung ist kein Nachweis, dass das Urteil stimmt.

Mindestmaßnahmen:

1. Jede Dimension separat und mit konkreten Ankern bewerten.
2. Kandidatenreihenfolge randomisieren und gespiegelt erneut prüfen.
3. Modell-, Prompt-, Rubrik- und Sampling-Version pinnen und protokollieren.
4. `unknown`/`nicht entscheidbar` erlauben, wenn Evidenz fehlt.
5. Judge regelmäßig gegen verblindete menschliche Fachexperten kalibrieren; Übereinstimmung und Fehlertypen berichten.
6. High-Risk-Entscheidungen nie ausschließlich durch einen LLM-Judge freigeben.
7. Wo möglich, Aussagen durch Quellen, Tests oder den realen Endzustand erden.

Mehrheitsentscheidungen mehrerer Judges reduzieren unter Umständen Varianz, beseitigen aber korrelierte Fehler und geteilte Biases nicht. Konsens ist keine Wahrheit.

## 4. Aufgabenbank und Release-Gates

Eine belastbare Suite enthält:

- reale, datenschutzkonform kuratierte Fälle;
- erwartbare Normalfälle, Grenzfälle und Gegenbeispiele;
- positive und negative Trigger-Fälle, um Über- und Unterauslösung zu messen;
- adversariale Aufgaben für Prompt Injection, Tool-Missbrauch und Grader-Hacking;
- getrennte Capability- und Regression-Sets;
- zeitlich getrennte Holdouts, damit auf die Suite nicht direkt optimiert wird;
- Segmentierung nach Sprache, Nutzergruppe, Risikoklasse, Tool und Modellroute.

Ein Release-Gate sollte **mehrdimensional** sein. Beispiel:

```text
RELEASE :=
  alle deterministischen Safety-Assertions bestehen
  UND keine kritische Policy-Verletzung in N Trials
  UND Qualitätsuntergrenze mit vorab definiertem Unsicherheitskriterium
  UND Latenz-/Kostenbudget erfüllt
  UND menschliche Stichprobe ohne ungeklärte kritische Abweichung
```

Das Gate garantiert deterministisch, dass ein Build bei Nichterfüllung nicht durch diesen Gate-Pfad veröffentlicht wird. Es garantiert nicht, dass die Schwellen fachlich richtig sind oder das Produktionsverhalten identisch bleibt. Grader, Daten, Harness, Systemprompt, Toolversionen und Modell-Snapshot gehören deshalb gemeinsam in die versionierte Release-Evidence.

## 5. Observability und Telemetrie

OpenTelemetry definiert semantische Konventionen, um Traces, Metriken und Logs einheitlich zu benennen; die GenAI-Konventionen erfassen unter anderem Modell, Tokenverbrauch, Finish-Reason und Agent-/Tool-Operationen ([OpenTelemetry GenAI](https://opentelemetry.io/docs/specs/semconv/gen-ai/)). Die Konvention ist unter aktiver Weiterentwicklung und ihre Implementierung ist eine Hersteller-/Integrationsfrage, keine Vollständigkeitsgarantie.

Empfohlene Trace-Struktur:

```text
request/session
  workflow-run (run_id, tenant, policy_version)
    model-call (provider, model_snapshot, prompt_template_hash, tokens)
    handoff (source_agent, target_agent, delegated_capability)
    tool-call (tool, authorization_decision_id, idempotency_key)
    approval (actor/pseudonym, decision, scope)
    commit (external_effect_id, result, retry_count)
    grader (grader_version, assertion, score/verdict)
```

Korrelation braucht stabile Run-, Trace-, Task- und Commit-IDs. Ereignisse sollten monotone Sequenznummern und Zeitstempel enthalten; verteilte Uhren sind nicht automatisch total geordnet. Wesentliche Audit-Ereignisse gehören in ein gegen nachträgliche Änderung geschütztes System. Sampling darf seltene Safety-Verstöße nicht wegfiltern: kritische Policy-Denials, Freigaben, Commits und ungeklärte Fehler werden vollständig erfasst, während voluminöse Debug-Inhalte gezielt gesampelt werden können.

### Datenschutz und Geheimnisse

Prompts, Systemanweisungen, Retrieval-Inhalte, Tool-Schemas, Argumente und Resultate können personenbezogene Daten, Quellcode, Tokens oder Geschäftsgeheimnisse enthalten. OpenTelemetry weist darauf hin, dass Inhaltsaufzeichnung deshalb standardmäßig aus bleiben sollte; bei Opt-in können vollständige Inhalte in Span-Attributen landen ([OpenTelemetry, GenAI Observability](https://opentelemetry.io/blog/2026/genai-observability/)).

Kontrollen:

- Metadaten statt Inhalte als Default; explizite Allowlist je Feld;
- Redaction vor Export, nicht erst im Backend;
- keine Secrets, Zugriffstokens oder verborgenes Reasoning persistieren;
- Mandanten- und Rollen-Isolation für Trace-Zugriff;
- Verschlüsselung, definierte Aufbewahrungs- und Löschfristen;
- regionale Ablage und Zweckbindung entsprechend Rechtsgrundlage;
- Zugriff und Export der Telemetrie selbst auditieren;
- separate, stärker geschützte Quarantäne für Incident-Payloads.

Redaction ist ein Parser- und Konfigurationsproblem und kann unvollständig sein. Hashes pseudonymisieren Identifikatoren oft nur, weil kleine Werteräume rückrechenbar sind. „Keine Inhalte im Trace“ verhindert zudem nicht, dass Inhalte in Anbieterlogs, Fehlermeldungen oder Tool-Systemen gespeichert werden.

## 6. SLIs, SLOs und Canaries

Ein **Service Level Indicator (SLI)** ist eine Messgröße; ein **SLO** ist ihr Ziel über ein Zeitfenster. Geeignete Agent-SLIs umfassen:

- Anteil erfolgreicher, extern verifizierter Outcomes;
- Rate kritischer Policy-Verstöße und nicht autorisierter Tool-Versuche;
- P50/P95/P99 End-to-End-Latenz und Tool-Latenz;
- Timeout-, Retry-, Abbruch- und Human-Escalation-Rate;
- Kosten oder Tokens pro erfolgreichem Outcome;
- Anteil unvollständiger Traces und Telemetrie-Verzögerung;
- Qualitätsindikatoren, jeweils mit Grader-Version und Unsicherheit.

SLOs werden pro Risikoklasse und Nutzerpfad definiert. Ein gemittelter Erfolgswert kann ein schwaches Segment verdecken. Googles SRE-Leitfaden empfiehlt explizite Ziele und Error Budgets statt unrealistischer 100-%-Ziele ([Google SRE](https://sre.google/sre-book/service-level-objectives/)). Für Safety-Invarianten ist ein Error Budget jedoch oft die falsche Semantik: verbotene Geldtransfers dürfen nicht durch ein Qualitätsbudget legitimiert werden. Solche Ereignisse brauchen präventive Gates und sofortige Incident-Reaktion.

Canary-Releases routen zunächst einen begrenzten, risikoarmen Anteil an eine neue Modell-/Prompt-/Harness-Version. Automatischer Rollback wird an harte Betriebsmetriken gekoppelt; subjektive Qualitätssignale dienen eher als Stop-and-review. Shadow-Traffic darf keine externen Nebenwirkungen auslösen und benötigt dieselben Datenschutzregeln wie Produktion. Ein erfolgreicher Canary zeigt nur, dass im beobachteten Ausschnitt kein Gate ausgelöst wurde.

## 7. Erreichbare Garantien und Nicht-Garantien

| Mechanismus | Einordnung | Garantiert bei korrekter Implementierung | Garantiert nicht |
|---|---|---|---|
| deterministischer Release-Grader | deterministisch erzwingbar | kein Release über diesen Pfad bei fehlgeschlagener Assertion | Vollständigkeit/Richtigkeit der Assertion |
| repräsentative Multi-Trial-Eval | statistisch messbar | nichts universell; liefert Schätzung samt Unsicherheit | Verhalten auf allen Eingaben oder nach Drift |
| LLM-Judge | heuristisch/statistisch | kein Wahrheitsbeweis | objektive, biasfreie Bewertung |
| SLO/Error Budget | statistisch/operativ | messbare Ziel- und Eskalationsregel, wenn Daten vollständig sind | Erfolg jeder einzelnen Anfrage |
| Trace/Audit-Log | unter Annahmen | Rekonstruktion der erfassten Ereignisse | Vollständigkeit, wenn Instrumentation umgangen wird |
| Canary | statistisch/operativ | begrenzte Exposition gemäß Router-Policy | Abwesenheit seltener oder segmentierter Fehler |

## 8. Nicht-Garantien und Failure Modes

- **Benchmark-Overfitting und Leakage:** Modell, Prompt oder Team optimiert auf bekannte Aufgaben; der Score generalisiert nicht.
- **Veraltete Ground Truth:** Außenwelt, APIs und fachliche Regeln ändern sich, während Referenzen statisch bleiben.
- **Goodhart-Effekt:** Ein aggregierter Score wird Ziel und verdrängt nicht gemessene Qualität oder Safety.
- **Grader-Hacking:** Der Agent erfüllt die Messoberfläche oder beeinflusst einen Judge, ohne das fachliche Problem zu lösen.
- **Korrelierte Trials:** gemeinsame Caches, Rate Limits oder Providerfehler verletzen die angenommene Unabhängigkeit.
- **Survivorship Bias:** abgebrochene oder technisch fehlerhafte Läufe verschwinden aus dem Nenner.
- **Tracing-Lücken:** Sampling, Exportausfall oder fehlende Instrumentierung lassen riskante Schritte unsichtbar.
- **Telemetry Poisoning:** untrusted Tool- oder Modelltexte werden als Logfelder übernommen und können Analyse oder Anzeige täuschen.
- **Canary-Mismatch:** risikoarme Canary-Nutzer repräsentieren nicht die später exponierten Segmente.
- **Silent Drift:** Anbieter aktualisiert Modell oder Safety-Layer, ohne dass die lokale Versionsbezeichnung ausreichend differenziert.

## 9. Entscheidungskriterien

- Ist ein maschinenprüfbarer Endzustand vorhanden? Dann outcome-basiert deterministisch graden.
- Ist der Prozess selbst sicherheitsrelevant? Dann zusätzlich Trajectory-Invarianten prüfen und zur Laufzeit erzwingen.
- Ist das Kriterium subjektiv? Dann LLM-Judge nur mit klarer Rubrik, Kalibrierung und menschlicher Stichprobe einsetzen.
- Kann ein Fehler irreversiblen Schaden verursachen? Dann Eval nicht als Schutzbarriere verwenden; Policy-Gate, Capability-Begrenzung und Freigabe vor die Nebenwirkung setzen.
- Ist die Außenwelt veränderlich? Dann Fixture/Snapshot für Reproduzierbarkeit und getrennte Live-Canaries für Aktualität nutzen.
- Sind vollständige Inhalte zur Diagnose wirklich notwendig? Wenn nein, nur Metadaten erfassen; wenn ja, enges Opt-in mit Redaction und kurzer Aufbewahrung.

## 10. Umsetzbare Checkliste

- [ ] Behauptungen in deterministisch, annahmengebunden, statistisch und heuristisch klassifizieren.
- [ ] Outcomes, Safety, Qualität, Kosten und Latenz als getrennte Dimensionen definieren.
- [ ] Deterministische Grader für jedes maschinenprüfbare Kriterium schreiben.
- [ ] Positive, negative, Grenz- und adversariale Fälle aufnehmen.
- [ ] Pro probabilistischer Konfiguration mehrere Trials und Unsicherheit berichten.
- [ ] Eval-Umgebung pro Trial isolieren und Ausgangszustand verifizieren.
- [ ] Modell, Prompt, Tools, Policy, Dataset, Scorer und Harness versionieren.
- [ ] Trajectories regelmäßig manuell auf Graderfehler und neue Fehlermoden prüfen.
- [ ] LLM-Judges gegen Experten kalibrieren; Positionsswap und `unknown` testen.
- [ ] Release-Gates mit harten Safety-Assertions und expliziten Schwellen definieren.
- [ ] End-to-End-Traces mit korrelierbaren IDs und Zustandsübergängen instrumentieren.
- [ ] Inhaltsaufzeichnung standardmäßig deaktivieren; Redaction vor Export testen.
- [ ] SLOs segmentieren und Error-Budget-/Rollback-Prozess festlegen.
- [ ] Canaries auf risikoarme Pfade begrenzen; Shadow-Nebenwirkungen blockieren.
- [ ] Eval-Sättigung, Dataset-Leakage, Drift und Telemetrielücken regelmäßig auditieren.

## Quellenhinweise

Zusätzlich zu den Inline-Links: Das [NIST AI RMF](https://airc.nist.gov/airmf-resources/airmf/5-sec-core/) ordnet Tests, Evaluation, Verifikation und Validierung in einen fortlaufenden Measure-/Manage-Prozess ein und fordert die Dokumentation von Unsicherheit. Es ist ein freiwilliger Risikomanagementrahmen, keine technische Runtime-Garantie. Alle Framework- und Konventionsfeatures entsprechen dem dokumentierten Stand vom 22. Juli 2026 und sind vor Einsatz gegen die tatsächlich verwendete Version zu prüfen.
