# Verträge, Validierung und Policy-Gates

[Kurzfassung](KURZFASSUNG.md) · [Beispielimplementierung](beispiel/README.md) · [Gesamtübersicht](../README.md)

Stand und Abruf der verlinkten Quellen: 2026-07-22.

## Kurzfassung

Ein belastbares Agent-Harness behandelt Modellausgaben als nicht vertrauenswürdige Vorschläge. Constrained Decoding kann – innerhalb der vom Anbieter unterstützten Schema-Teilmenge und bei erfolgreicher, vollständiger Antwort – die **syntaktische Form** einer Ausgabe erzwingen. Es beweist weder, dass Werte wahr sind, noch dass eine beabsichtigte Aktion zulässig oder sicher ist. Diese Lücke schließen deterministische Validatoren und Policy-Gates: Sie prüfen maschinenlesbare Invarianten, bevor ein nicht umgehbarer Policy Enforcement Point (PEP) eine Aktion zulässt.

Der empfohlene Kontrollpfad lautet:

`Modellvorschlag → Schema-Prüfung → semantische Validatoren → Policy-Entscheidung → Freigabe/Commit → Tool-Adapter → Audit-Ereignis`

Eine technische Garantie gilt nur für die explizit kodierte Eigenschaft und nur, wenn alle Ausführungspfade durch diesen Kontrollpfad gehen. Ein OPA-Entscheid („allow“) allein ist keine Durchsetzung; Open Policy Agent (OPA) trennt ausdrücklich Policy-Entscheidung und Enforcement. Der aufrufende PEP muss bei Nichterreichbarkeit, undefiniertem Ergebnis und Fehlern festgelegt reagieren. Für risikoreiche Nebenwirkungen ist `fail closed` der sichere Default.

## Anwendungsbereich

Dieses Kapitel betrifft Verträge an allen Harness-Grenzen:

- Nachrichten zwischen Agenten und Modellen;
- Tool-Aufrufe und Tool-Ergebnisse;
- Zustandsübergänge und Übergaben (Handoffs);
- Zulassung einer einzelnen Aktion zur Laufzeit;
- Zulassung eines Modells, Prompts, Tools oder Artefakts für eine Umgebung;
- Release-Entscheidungen in CI/CD.

Nicht behandelt werden als Ersatz für Verträge: Promptformulierungen, Selbstkritik, Mehrheitsentscheide und LLM-as-Judge. Sie können Qualität beeinflussen, sind aber keine deterministischen Gates.

## 1. Verträge als schichtweiser Kontrollpfad

### 1.1 Getypte Nachrichten und JSON Schema

Ein Vertrag soll nicht nur „gültiges JSON“, sondern eine möglichst enge Datenmenge beschreiben: Pflichtfelder, Typen, Enumerationen, Wertebereiche, Stringmuster, maximale Längen und das Verbot unbekannter Felder. Ein leeres JSON Schema akzeptiert dagegen jedes JSON-Dokument; die offizielle Einführung zeigt damit, dass „Schema vorhanden“ noch keine wirksame Einschränkung bedeutet ([JSON Schema, Grundlagen](https://json-schema.org/understanding-json-schema/basics)).

Praktische Regeln:

- jede Nachricht trägt `schema_version`, `message_type`, `request_id` und eine gebundene Auftraggeberidentität;
- `additionalProperties: false` verhindert stilles Einschleusen unbekannter Aktionsparameter;
- IDs, Geldbeträge, Pfade, URLs und Zeitangaben erhalten kanonische Darstellungen und enge Grenzen;
- Eingabe- und Ausgabe-Schemata werden getrennt versioniert;
- Parser und Validator werden fest versioniert und mit Negativtests geprüft;
- unbekannte Schema-Versionen werden abgewiesen, nicht „best effort“ interpretiert.

Eine Schema-Prüfung garantiert deterministisch: *Die empfangene Darstellung erfüllt die kodierten Strukturregeln des konkret verwendeten Validators.* Sie garantiert nicht: fachliche Wahrheit, Aktualität, Berechtigung, schadlose Wirkung oder Kompatibilität mit einem anderen Validator. Format- und Implementierungsgrenzen – etwa Unicode-Normalisierung, Zahlenpräzision, reguläre Ausdrücke und Referenzauflösung – gehören deshalb in Tests und Threat Model.

### 1.2 Constrained Decoding

Constrained Decoding (beschränkte Dekodierung) entfernt während der Generierung Tokens, die an der aktuellen Position nicht zur erlaubten Grammatik passen. OpenAI beschreibt hierfür dynamische Einschränkung anhand eines JSON-Schemas und grenzt dies von bloßem JSON-Modus ab ([OpenAI, Structured Outputs](https://openai.com/index/introducing-structured-outputs-in-the-api/)).

**Erreichbare Garantie:** Wenn der konkrete Dienst das deklarierte Schema vollständig unterstützt, die Anfrage in den dokumentierten strikten Modus gelangt und eine vollständige normale Antwort zurückkehrt, kann die ausgegebene Zeichen-/Tokenfolge schema-konform erzwungen werden. Der Consumer muss trotzdem erneut lokal validieren, weil Transport, Versionswechsel, Fehlermeldungen, Abbruch oder Integrationsfehler außerhalb der Dekodierung liegen.

**Nicht garantiert:** Die Werte können frei erfunden, widersprüchlich oder gefährlich sein. Die Herstellerdokumentation nennt ausdrücklich Fehler innerhalb gültiger JSON-Werte als verbleibende Grenze. Auch ein syntaktisch gültiger Tool-Aufruf wie `{"recipient":"attacker@example","amount":100000}` ist keine Autorisierung. Ein wissenschaftlicher Benchmark zeigt zudem, dass Schema-Compliance von Modell, Schema und Framework abhängt; er ist ein Preprint und daher Gegenprüfung, kein Produktversprechen ([Generating Structured Outputs, arXiv:2501.10868](https://arxiv.org/abs/2501.10868)).

Folgerung: Constrained Decoding ist ein Interoperabilitätsmechanismus, kein Sicherheits- oder Wahrheitsbeweis.

### 1.3 Deterministische semantische Validatoren

Nach der Strukturprüfung folgen reine, versionierte Regeln über normalisierte Eingaben, zum Beispiel:

- `amount <= remaining_budget`;
- Zielkonto steht in einer serverseitigen Allowlist;
- Dateipfad liegt nach sicherer Auflösung innerhalb eines erlaubten Roots;
- Zustandsübergang ist im aktuellen Zustandsautomaten zulässig;
- referenzierte Ressource gehört zum authentifizierten Mandanten;
- Tool und Argumente sind für Risikoklasse und Auftrag erlaubt.

Solche Validatoren garantieren die kodierte Eigenschaft für die geprüfte Repräsentation, wenn Implementierung, Konfiguration und vertrauenswürdige Eingabedaten korrekt sind. Sie garantieren weder Vollständigkeit der Regeln noch die Wahrheit externer Daten. Zeitabhängige Daten, DNS, Dateisystemzustand oder Berechtigungen können sich zwischen Prüfung und Nutzung ändern (Time-of-check/Time-of-use, TOCTOU). Kritische Prüfung und Commit müssen deshalb atomar sein oder im Tool-Adapter nochmals gegen denselben autoritativen Zustand erfolgen.

## 2. Policy-as-Code mit PDP und PEP

OPA ist ein allgemeiner Policy Decision Point (PDP): Die Anwendung übergibt strukturierte Daten, OPA wertet deklarative Rego-Policies aus und liefert eine Entscheidung. OPA entkoppelt ausdrücklich Entscheidung von Durchsetzung ([OPA-Grundlagen](https://www.openpolicyagent.org/docs)). Daraus folgt eine zwingende Architekturgrenze:

- **PDP:** berechnet etwa `allow`, Ablehnungsgründe, Auflagen und Policy-Version;
- **PEP:** sitzt im einzigen wirksamen Pfad zur Ressource und setzt die Entscheidung durch;
- **Tool-Adapter:** bindet Identität und Parameter an den tatsächlichen API-Aufruf und protokolliert den Commit.

Eine OPA-Policy ist nur dann eine technische Schranke, wenn kein Modell, Agent, Plugin oder alternativer Client den PEP umgehen oder selbst Credentials verwenden kann. Policies und Referenzdaten müssen signiert/versioniert verteilt, ihre Aktivierung beobachtet und Entscheidungen an die aktive Revision gebunden werden.

OPA kann beim Start ohne geladene Policies `undefined` liefern. Ob der aufrufende Enforcer dann offen oder geschlossen ausfällt, entscheidet nicht OPA, sondern die Integration ([OPA, Operational Readiness and Failure Modes](https://www.openpolicyagent.org/docs/operations)). Für Schreib-, Export-, Zahlungs-, Deployment- und Administrationspfade gilt daher:

1. Readiness einschließlich erwarteter Bundle-Revision prüfen;
2. `deny` und `undefined` gleich behandeln;
3. Timeout, Netzwerkfehler und unparsebare Antwort ablehnen;
4. Notfallausnahmen separat authentifizieren, befristen und auditieren;
5. nur ausdrücklich als niedrig-riskant klassifizierte Lesepfade dürfen bewusst `fail open` sein.

OPA-Decision-Logs können Eingabe, Ergebnis, Policy-/Bundle-Metadaten und `decision_id` für Audits enthalten. Weil Eingaben Secrets oder personenbezogene Daten enthalten können, unterstützt OPA das Löschen und Maskieren von Feldern vor dem Upload ([OPA, Decision Logs](https://www.openpolicyagent.org/docs/management-decision-logs)). Logging ist Nachweisbarkeit, keine Verhinderung; Log-Ausfälle dürfen nicht unbemerkt die gewählte Compliance-Eigenschaft aufheben.

## 3. Admission- und Release-Gates

Ein **Admission Gate** entscheidet unmittelbar vor Ausführung oder Zustandsänderung. Beispiele sind ein Tool-PEP, ein Workflow-Transition-Guard oder ein Deployment-Admission-Controller. Das Kubernetes-Modell veranschaulicht die Semantik: Validierende Webhooks werden nach erfolgreicher Authentisierung/Autorisierung aufgerufen; lehnt einer ab, scheitert die Anfrage ([Kubernetes, Admission Controllers](https://kubernetes.io/docs/reference/access-authn-authz/admission-controllers/)). Das ist nur für Anfragen garantiert, die tatsächlich über den API-Server laufen.

Ein **Release Gate** entscheidet, welche Version in welche Umgebung gelangt. Sinnvolle deterministische Bedingungen sind:

- Schemas und Policies kompilieren und bestehen Negativ-/Mutationstests;
- Artefaktdigest, Signatur und erwartete Build-Provenienz stimmen;
- genehmigte Modell-, Prompt-, Tool- und Policy-Versionen sind im Manifest gepinnt;
- kritische Findings, fehlende Freigaben oder Migrationen blockieren;
- Rollback-Artefakt und kompatibler Zustandsmigrationspfad existieren.

SLSA beschreibt ansteigende Garantien zur Build-Provenienz und Härtung der Build-Plattform. Diese betreffen Herkunft und Manipulationsresistenz eines Artefakts, nicht dessen fachliche Korrektheit ([SLSA v1.0, Security Levels](https://slsa.dev/spec/v1.0/levels)). Eval-Schwellen können zusätzlich ein Release blockieren, liefern aber nur statistische Evidenz für die getestete Verteilung. Ein „95 % bestanden“-Gate macht die übrigen Fälle nicht sicher.

## 4. Garantie-Ledger

| Mechanismus | Kategorie | Präzise erreichbare Aussage | Voraussetzungen | Keine Aussage über |
|---|---|---|---|---|
| Striktes Schema + lokaler Validator | deterministisch erzwingbar | Nachricht liegt in der kodierten Strukturmenge | festgelegter Draft/Validator; vollständige Nachricht | Wahrheit, Absicht, Berechtigung |
| Constrained Decoding | unter Produkt-/Protokollannahmen syntaktisch erzwingbar | erfolgreiche normale Ausgabe folgt der unterstützten Grammatik | unterstütztes Schema, strikter Modus, vollständige Antwort | Semantik, Sicherheit, externe Fakten |
| Reiner semantischer Validator | deterministisch erzwingbar | explizite Invariante gilt für normalisierte Prüfdaten | korrekte Regel/Implementierung; stabile Daten bis Commit | Vollständigkeit der Invarianten |
| OPA-Entscheidung allein | keine Enforcement-Garantie | Policy wurde gegen gelieferten Input ausgewertet | passende Policy-/Datenrevision | tatsächliche Blockade der Aktion |
| Nicht umgehbarer, fail-closed PEP | deterministisch erzwingbar | ohne positives Policy-Ergebnis kein Commit über diesen Pfad | alle Pfade erfasst; Credentials nur im Adapter | korrekte Policy, kompromittierter PEP |
| Eval-Release-Gate | statistisch messbar | Artefakt erfüllt Schwelle auf festem Eval-Set | repräsentatives, geschütztes Set; reproduzierbarer Runner | Verhalten außerhalb der Stichprobe |
| Signierte Provenienz | unter Kryptografie-/Build-Annahmen | Herkunft entspricht verifizierter Attestation | geschützte Schlüssel und gehärteter Builder | Funktions- oder Modellsicherheit |

## 5. Nicht-Garantien und Failure Modes

- **Schema als Scheinsicherheit:** sehr weite Strings oder freie Maps verlagern die gesamte Gefahr in unvalidierte Werte.
- **Validator-Divergenz:** Producer und Consumer interpretieren Draft, Formate oder Zahlen unterschiedlich.
- **Policy-Lücken:** eine korrekt ausgewertete Policy kann fachlich unvollständig oder auf manipulierte Attribute gestützt sein.
- **Bypass:** Shell, Netzwerk, SDK oder direkt verfügbares Secret umgehen den PEP.
- **Fail-open durch Unfall:** Timeout oder `undefined` wird als Erlaubnis behandelt.
- **TOCTOU:** Ressource oder Berechtigung ändert sich nach der Prüfung.
- **Mutation im Validator:** ein Admission-Webhook erzeugt Nebenwirkungen, obwohl ein späteres Gate ablehnt; Kubernetes warnt bei solchen Webhook-Side-Effects vor notwendiger Reconciliation ([Kubernetes, Admission Controllers](https://kubernetes.io/docs/reference/access-authn-authz/admission-controllers/)).
- **Policy-Rollout-Drift:** verschiedene Instanzen entscheiden mit verschiedenen Bundle-Versionen.
- **Audit-Leak:** vollständige Tool-Argumente, Tokens oder sensible Modellinhalte landen im Decision Log.
- **Gate-Gaming:** Modelle/Prompts werden auf ein bekanntes Eval-Set optimiert, ohne Generalisierung.

## 6. Entscheidungskriterien

Schema plus deterministische Validatoren genügen, wenn die Regeln lokal, stabil und klein sind. Ein externer PDP wie OPA lohnt sich, wenn dieselben Autorisierungs- oder Compliance-Regeln über mehrere Dienste hinweg konsistent verteilt, versioniert und auditiert werden müssen. Er erhöht jedoch Betriebs- und Ausfallkomplexität.

Ein menschlicher Commit ist angezeigt, wenn die Wirkung irreversibel, rechtlich bedeutsam, hochpreisig oder für den Validator nicht vollständig formalisierbar ist. Die UI muss dann exakt die gebundene Aktion anzeigen; eine Freigabe eines Plans darf nicht pauschal spätere, veränderte Tool-Argumente autorisieren.

Release-Gates sollten nur Eigenschaften „garantieren“, die binär und reproduzierbar geprüft werden. Qualitätsmetriken, Judge-Scores und Red-Team-Ergebnisse werden als statistische Evidenz mit Konfidenz, Datensatzversion und Stichprobengröße geführt.

## 7. Umsetzbare Checkliste

- [ ] Für jede Grenze existiert ein enges, versioniertes Schema mit Größenlimits und `additionalProperties: false`.
- [ ] Jeder empfangene Modelloutput wird lokal erneut validiert; Parsingfehler führen zu keiner Nebenwirkung.
- [ ] Semantische Invarianten sind reine, versionierte Funktionen mit Positiv-, Negativ-, Grenz- und Mutationstests.
- [ ] Identität, Mandant, Zweck, Budget und Risikoklasse stammen aus vertrauenswürdigem Harness-Zustand, nicht aus dem Modelltext.
- [ ] Alle externen Nebenwirkungen laufen ausschließlich über einen PEP/Tool-Adapter; Modelle besitzen keine direkten Credentials.
- [ ] `deny`, `undefined`, Timeout und PDP-Fehler sind pro Pfad explizit festgelegt; kritische Pfade sind fail-closed.
- [ ] Policy- und Datenrevision werden mit Entscheidung und Commit korreliert.
- [ ] Prüfung und Commit sind atomar oder der Adapter revalidiert autoritativ unmittelbar vor der Wirkung.
- [ ] Decision Logs sind manipulationsgeschützt, korrelierbar, aufbewahrungsbegrenzt und vor Export redigiert.
- [ ] Release-Manifeste pinnen Modell, Prompt, Tools, Schemas, Policies und Eval-Datensatz.
- [ ] Herkunfts-/Signaturgates werden nicht als Beweis fachlicher Korrektheit bezeichnet.
- [ ] Für jede behauptete Garantie sind Annahmen, Failure Domain, Messsignal und Reaktion dokumentiert.
