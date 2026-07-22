# Vergleich von KI-Harnesses und ergänzenden Kontrolltechniken

[Kurzfassung](KURZFASSUNG.md) · [Beispielimplementierung](beispiel/README.md) · [Gesamtübersicht](../README.md)

Stand: 2026-07-22

## Kurzfassung

Die verglichenen Werkzeuge lösen unterschiedliche Schichten desselben Problems. LangGraph, Google ADK, Microsoft AutoGen beziehungsweise Agent Framework, OpenAI Agents SDK und CrewAI strukturieren Modell- und Tool-Interaktionen. Temporal koordiniert langlebige, fehlertolerante Geschäftsprozesse. Inspect AI führt reproduzierbare Evaluationen aus. Open Policy Agent (OPA) entscheidet deklarative Policies. Container, gVisor und Firecracker begrenzen die Auswirkung nicht vertrauenswürdiger Ausführung. Keines ersetzt die übrigen Schichten und keines liefert allein eine End-to-End-Garantie für fachliche Korrektheit.

Für einen kontrollierbaren Produktionsentwurf werden diese Fähigkeiten meist kombiniert: deterministischer Workflow oder Durable-Execution-Layer außen, Agent-SDK nur innerhalb begrenzter Schritte, OPA oder gleichwertige Policy-Entscheidung vor jeder relevanten Aktion, isolierte Tool-Ausführung sowie Inspect oder ein vergleichbares Eval-System im Releaseprozess. Welches konkrete Produkt passt, hängt von Workflow-Lebensdauer, Ausfallmodell, Sprache, Betriebsmodell, Providerbindung, Sicherheitsrisiko und Eval-Anforderungen ab.

Alle Featureaussagen sind zeitstandsbezogen. Herstellerdokumentation belegt, dass eine Funktion vorgesehen ist; sie beweist weder korrekte Konfiguration noch die Zuverlässigkeit der Gesamtanwendung.

## Anwendungsbereich und Bewertungsmaßstab

Ein Harness ist hier der Kontrollrahmen um probabilistische Modelle: Ausführungsgraph, Zustand, Routing, Tools, Validierung, Freigaben, Budgets, Telemetrie und Release-Gates. Bewertet werden:

1. **Kontrollfluss:** feste Graphen, dynamische Agent-Loops, Handoffs und Parallelität;
2. **Dauerhaftigkeit:** persistenter Zustand, Resume, Replay, Retry und Upgradefähigkeit;
3. **Kontrollpunkte:** typisierte Nachrichten, Guardrails, Human-in-the-Loop (HITL), Policy Enforcement;
4. **Begrenzung:** Iterationen, Zeit, Tokens, Kosten, Nebenwirkungen und Ressourcen;
5. **Beobachtbarkeit und Evaluation:** Traces, Logs, Scorer, Reproduzierbarkeit;
6. **Isolation:** Prozess-, Kernel- oder VM-Grenzen und Egress-Kontrolle;
7. **Garantiereichweite:** deterministisch, unter Annahmen, statistisch oder heuristisch.

Die Einordnung bezieht sich auf öffentlich dokumentierte Funktionen am Stichtag und nicht auf nicht dokumentierte Cloud- oder Enterprise-Erweiterungen.

## Vergleichsmatrix

| Werkzeug | Primäre Rolle | Dokumentierte Stärken | Technisch erzwingbar, wenn korrekt integriert | Wesentliche Lücke / Nicht-Garantie |
|---|---|---|---|---|
| LangGraph | zustandsbehaftete Agent-/Workflow-Graphen | explizite Knoten/Kanten, Checkpoints, Interrupts, Parallel-Supersteps, Resume | Graphkanten, Zustandsform, Interruptpositionen; persistente Wiederaufnahme mit dauerhaftem Checkpointer | kein allgemeines Exactly-once für Tool-Nebenwirkungen; Modellinhalt bleibt probabilistisch |
| Temporal | Durable-Execution-Plattform | persistierte Event History, Replay, Timer, Retries, Signals, langlebige Workflows | Workflow-Fortschritt und Wiederaufnahme unter Determinismus-/Betriebsannahmen | keine Agentsemantik, Inhaltsvalidierung, Tool-ACL oder automatische Exactly-once-Nebenwirkung |
| Google ADK | Agenten und Graph-/Template-Workflows | sequenzielle, parallele, Loop- und Graph-Flows; Sessions, Tools, Evaluation/Observability | explizite Graphroute und Code-Gates im gewählten Workflow | dynamische Agententscheidung und Modellinhalt nicht garantiert; Durability hängt vom Runtime-/Store-Setup ab |
| Microsoft AutoGen | Multi-Agent-Teams und eventgetriebene Agenten | Teams, Group Chat, Handoffs, GraphFlow; kombinierbare Termination Conditions | harte Stop-Bedingungen, wenn alle Runs darüber geführt werden | Gruppeninteraktion ist heuristisch; Microsoft lenkt Neuentwicklung zum Agent Framework |
| Microsoft Agent Framework | typisierte Agenten und graphbasierte Workflows | Datenflusskanten, Executors, HITL, Checkpoints, Middleware/Telemetry | explizite Routen, Typgrenzen und Stop-/Approval-Gates im Anwendungscode | am Stichtag jung und im Wandel; dokumentiert aktuell Fokus auf Single-Process, verteilte Ausführung geplant |
| OpenAI Agents SDK | schlanke Agent-Loops, Tools und Handoffs | Tools, Handoffs, Sessions, Tracing, Agent-/Tool-Guardrails, HITL | Max-Turns und synchrone Code-/Tool-Gates; Sessionpersistenz mit geeignetem Backend | Agent-Guardrails decken nicht automatisch alle Zwischenstufen; mehrere Toolklassen umgehen den Function-Tool-Guardrail-Pfad |
| CrewAI | Rollen-/Task-orientierte Crews und Flows | Crews für Zusammenarbeit, Flows für Zustand, Routing, Persistenz und Resume | explizite Flow-Kanten und Codevalidierung soweit implementiert | Herstelleraussagen sind kein Nachweis für Crash-Semantik oder Exactly-once; Crew-Konsens bleibt heuristisch |
| Inspect AI | Eval-Harness, nicht primär Produktionsorchestrator | Datasets, Solvers/Agents, Scorer, Logs, Limits, Sandboxes, Multi-Provider | reproduzierbare Evalkonfiguration und deterministische Scorer bei fixierten Artefakten | Eval-Ergebnis garantiert keine Produktionsleistung; Model Grading bleibt probabilistisch |
| OPA | Policy Decision Point | Rego Policy-as-Code, Bundles, Decision Logs, Tests, lokale/Sidecar-Entscheidung | Allow/Deny oder strukturierte Policyentscheidung für vollständig erfasste Eingaben | OPA setzt die Entscheidung nicht selbst durch; Enforcer bestimmt fail-open/fail-closed; keine semantische Wahrheitsprüfung |
| Container + seccomp/LSM | Basisisolation und Ressourcengrenzen | Namespaces, cgroups, Capability-Reduktion, syscall-/Pfadprofile | konfigurierte Ressourcen- und Zugriffsbeschränkungen im Kernel | geteilter Host-Kernel, Fehlkonfiguration und erlaubte Angriffsfläche bleiben |
| gVisor | Userspace-Anwendungskernel | eigene Systemaufrufimplementierung, reduzierte Host-Kernel-Fläche, Defense in Depth | größere Trennung vom Host-Kernel für unterstützte Schnittstellen | keine absolute Isolation; Seitenkanäle, Hostressourcen und Kompatibilitätslücken bleiben |
| Firecracker | KVM-basierte microVMs | VM-Grenze, minimales Gerätemodell, seccomp, cgroups, namespaces, jailer | starke Workload-Grenze und Ressourcenlimits bei gehärtetem Host-Setup | filtert Gast-Egress nicht selbst; KVM/Host/Setup bleiben Teil der Trusted Computing Base |

## Technische Mechanismen und Einzelprofile

### LangGraph

**Geeignet für:** Anwendungen, die Agententscheidungen mit einem sichtbaren, zustandsbehafteten Graphen verbinden und an definierten Stellen pausieren, prüfen oder fortsetzen sollen.

LangGraph speichert mit einem Checkpointer den Graphzustand an Superstep-Grenzen; Threads und Checkpoints ermöglichen Resume, Human-in-the-Loop, Fehlertoleranz und Zustandsinspektion ([Persistence](https://docs.langchain.com/oss/python/langgraph/persistence)). Ein reiner In-Memory-Saver ist ausdrücklich nur für Entwicklung und Tests geeignet. Interrupts speichern Zustand und setzen denselben Thread später fort; beim Resume startet der betroffene Knoten von vorn, weshalb vorherige Nebenwirkungen idempotent sein müssen ([Interrupts](https://docs.langchain.com/oss/python/langgraph/interrupts)).

**Erreichbar:** deterministische Topologie und Gates; wiederaufnehmbarer Graph unter persistentem Checkpointer, stabiler Thread-ID, kompatibler Serialisierung und replay-sicherem Knotencode.

**Nicht erreichbar durch LangGraph allein:** Wahrheit der Modellausgabe, globale Transaktion über Tools, Exactly-once-Nebenwirkungen, Netzwerk-/Dateisystemisolation oder zentrale Autorisierung. Checkpointing speichert Fortschritt; es macht eine bereits ausgeführte Zahlung nicht automatisch deduplizierbar.

**Auswahlkriterien:** Python/JavaScript-nahe Graphsteuerung, feingranulare Zustandsinspektion und Agent-HITL sind wichtiger als jahrelange Workflow-Historien oder sprachübergreifende Durable-Execution-Infrastruktur.

### Temporal

**Geeignet für:** lang laufende, geschäftskritische Prozesse mit Crash-/Restart-Anforderungen, Timern, Retries, menschlichen Wartezeiten und verteilten Activities.

Temporal persistiert eine Event History und rekonstruiert Workflowzustand durch Replay. Der Workflowcode muss bei derselben Historie deterministische Commands erzeugen; Interaktion mit der Außenwelt gehört in Activities ([Workflow Execution](https://docs.temporal.io/workflow-execution)). Der Hersteller beschreibt Workflow-Ausführung als „effectively once“, doch diese Aussage gilt für die Workflowfunktion, nicht pauschal für externe Nebenwirkungen. Activities können erneut ausgeführt werden; Adapter benötigen Idempotenzschlüssel, Deduplikation, Outbox oder Saga-Kompensation.

**Erreichbar unter Annahmen:** fortgesetzter Workflow-Fortschritt nach Worker-/Serverausfällen bei korrekt betriebenem Service, verfügbarer Persistenz, deterministischem Replay und kompatiblen Codeänderungen.

**Nicht erreichbar durch Temporal allein:** Agent-Routingqualität, Schemawahrheit, Toolberechtigung, Prompt-Injection-Abwehr und Exactly-once bei einem nicht-idempotenten Fremdsystem.

**Auswahlkriterien:** Temporal ist ein äußerer Zuverlässigkeitskernel, wenn Ausfallwiederaufnahme wichtiger ist als ein agentenspezifisches API. Ein Agent-SDK kann innerhalb von Activities laufen; Modellaufrufe und Ergebnisse müssen als Aktivitätsergebnisse in der Historie stabilisiert werden.

### Google Agent Development Kit (ADK)

**Geeignet für:** provider-flexible Agentenanwendungen mit Template-Workflows oder expliziten Graphen, besonders im Google-Ökosystem, aber mit dokumentierten Adaptern zu weiteren Modellen.

ADK dokumentiert sequenzielle, parallele und Loop-Workflow-Agenten sowie Graph Workflows mit expliziten Routen; die Navigation weist außerdem Sessions, Resume, Evaluation und Observability als eigene Bereiche aus ([Workflow Agents](https://adk.dev/agents/workflow-agents/), [Graph Workflows](https://adk.dev/graphs/)). Ein deterministischer Graph kann festlegen, welcher Knoten folgen darf. Ein LLM-gesteuerter Router bleibt hingegen probabilistisch.

**Erreichbar:** feste Kontrollpfade, Zähler, Schemaprüfungen und Tool-Allowlisting, sofern im Anwendungscode beziehungsweise in Callbacks lückenlos umgesetzt.

**Nicht erreichbar durch ADK allein:** garantierte fachliche Richtigkeit, automatische Exactly-once-Aktionen oder eine vom gewählten Deployment unabhängige Crash-Garantie. „Session vorhanden“ ist nicht gleichbedeutend mit durable, atomarem Workflow-Replay.

**Auswahlkriterien:** gewünschte ADK-Sprachvariante, Deploymentziel, benötigter Graph-/Sessionumfang und reale Tests der Persistenzsemantik. Versionsspezifische Parität zwischen Python, TypeScript, Go und Java/Kotlin darf nicht angenommen werden.

### Microsoft AutoGen und Microsoft Agent Framework

**Geeignet für:** Multi-Agent-Experimente und Teams (AutoGen) beziehungsweise neue typisierte, graphbasierte Workflows im Microsoft-Umfeld (Agent Framework).

AutoGen AgentChat stellt Round-Robin-, Selector-, Swarm- und weitere Teamformen bereit. Seine Termination Conditions können unter anderem Nachrichten-, Token- und Zeitgrenzen kombinieren ([AutoGen Termination](https://microsoft.github.io/autogen/stable/user-guide/agentchat-user-guide/tutorial/termination.html)). Solche Bedingungen erzwingen ein Ende, wenn der Lauf ausschließlich über diese API erfolgt; textbasierte Erfolgsbedingungen bleiben semantisch unsicher.

Microsoft bezeichnet Agent Framework als Weiterentwicklung aus AutoGen und Semantic Kernel. Die offizielle Migration beschreibt einen typisierten, graphbasierten Datenfluss mit Executors, Request/Response-HITL und Checkpointing. Sie nennt für Agent Framework derzeit Single-Process-Komposition; verteilte Ausführung sei geplant ([Migration from AutoGen](https://learn.microsoft.com/en-us/agent-framework/migration-guide/from-autogen/), [Overview](https://learn.microsoft.com/en-us/agent-framework/overview/)). Das ist eine wichtige Reife- und Betriebsgrenze am Stichtag.

**Erreichbar:** harte Abbruchgrenzen; im Agent Framework explizite, typisierte Routen und Anwendungsgates. Checkpoint-Resume nur im dokumentierten Umfang und mit getestetem Store.

**Nicht erreichbar:** Multi-Agent-Konsens als Wahrheit, implizite Sicherheit durch Rollenprompts oder automatische verteilte Transaktionen.

**Auswahlkriterien:** AutoGen für bestehende Systeme, Forschung und dessen Teamabstraktionen; Agent Framework für Neuentwicklung, wenn die aktuelle Sprach-/Featurematrix ausreicht. Migration, API-Stabilität und fehlende verteilte Runtime müssen in der Architekturentscheidung sichtbar sein.

### OpenAI Agents SDK

**Geeignet für:** schlanke Agent-Loops mit Function Tools, Handoffs, Sessions, Tracing und programmatischen Guardrails.

Das SDK modelliert Handoffs als Übergabe an spezialisierte Agenten ([Handoffs](https://openai.github.io/openai-agents-python/handoffs/)). Sessions können Gesprächshistorie über verschiedene Backends verwalten ([Sessions](https://openai.github.io/openai-agents-python/sessions/)). Guardrails haben jedoch wichtige Grenzen: Input-Guardrails laufen nur beim ersten, Output-Guardrails nur beim finalen Agenten. Tool-Guardrails laufen für eigene Function Tools bei jedem Aufruf, gelten laut Dokumentation aber nicht automatisch für Handoffs, Hosted Tools, eingebaute Ausführungstools oder `Agent.as_tool()` ([Guardrails](https://openai.github.io/openai-agents-python/guardrails/)). Blocking-Guardrails müssen gewählt werden, wenn vor einem potenziellen Tool-Effekt gestoppt werden soll; parallele Guardrails können zu spät auslösen.

**Erreichbar:** Max-Turns, typisierte Function-Tool-Schemas und blockierende Code-Gates an tatsächlich abgedeckten Grenzen; persistente Gesprächshistorie mit geeignetem Backend.

**Nicht erreichbar:** vollständige Policy-Abdeckung allein durch Agent-Level-Guardrails, durable Workflow-Semantik allein durch Sessions, Wahrheit strukturierter Ausgaben oder Providerunabhängigkeit ohne Adapter und Tests.

**Auswahlkriterien:** geringe Frameworkschwere und direkte OpenAI-Integration versus Bedarf an explizitem Graph, starker Durable Execution oder neutralem Telemetrie-/Provider-Layer.

### CrewAI

**Geeignet für:** rollenbasierte Crews und task-orientierte Automationen; Flows, wenn explizitere Zustands- und Kontrollpfade benötigt werden.

Die aktuelle Herstellerdokumentation unterscheidet Agents/Crews von Flows und beschreibt für Flows Routing, Zustandsverwaltung, Persistenz und Resume sowie für Tasks Prozesse, Guardrails und HITL ([CrewAI-Dokumentation](https://docs.crewai.com/), [Flows](https://docs.crewai.com/en/concepts/flows)). Diese Aussagen müssen durch versionsfixierte Integrations-, Crash- und Migrationstests konkretisiert werden: „persistiert“ sagt ohne Commit-Grenzen, Store und Wiederholungssemantik noch nichts über doppelte Nebenwirkungen aus.

**Erreichbar:** programmierte Flow-Routen und Pydantic-/Codevalidierung im abgedeckten Pfad; Rollen- und Prozessstruktur als Implementationskonvention.

**Nicht erreichbar:** objektive Korrektheit durch Crew-Zusammenarbeit, verteilte Exactly-once-Ausführung oder Sicherheitsisolation durch Rollenbeschreibungen.

**Auswahlkriterien:** Produktivität des rollenbasierten Modells und vorhandene Integrationen gegen Anforderungen an transparente Kontrollsemantik, API-Stabilität, selbst betriebenen Zustand und unabhängige Observability testen.

### Inspect AI

**Geeignet für:** Offline-/CI-Evaluation von Modellen und Agenten, nicht als primärer Produktionsworkflow.

Inspect AI ist ein Open-Source-Eval-Framework des UK AI Security Institute und Meridian Labs. Es bietet Datasets, Agents/Solvers, Tools, Scorer, Logs, Limits, Multi-Agent-Primitiven und Sandbox-Backends; externe Agenten können ebenfalls evaluiert werden ([Inspect](https://inspect.aisi.org.uk/)). Ein Evalpaket sollte Dataset-Hash, Task-/Scorer-Code, Modellkennung, Parameter, Seeds soweit unterstützt, Sandbox-Image und vollständige Logs festhalten.

**Erreichbar:** deterministische Auswertung bei deterministischem Scorer und fixierten Artefakten; wiederholbare Messprozedur innerhalb dokumentierter Umgebungsannahmen.

**Nicht erreichbar:** identische LLM-Ausgabe, Repräsentativität des Datensatzes, Produktions-SLO oder Wahrheit eines LLM-as-Judge-Scores.

**Auswahlkriterien:** Inspect ergänzt jeden Runtime-Harness als Release-Gate. Entscheidend sind eigene, risikobasierte Aufgaben und Scorer; die Zahl vorgefertigter Benchmarks allein ist kein Qualitätsnachweis für den Anwendungsfall.

### Open Policy Agent (OPA)

**Geeignet für:** zentral definierte, dezentral ausführbare Policies für Identität, Datenklasse, Tool, Argumente, Risiko, Budgetstufe und Approval-Anforderung.

OPA trennt Policyentscheidung von Enforcement: Die Anwendung übergibt strukturierte Eingaben, Rego liefert eine Entscheidung ([OPA-Grundlagen](https://www.openpolicyagent.org/docs)). Bundles verteilen versionierte Policy; Decision Logs unterstützen Audit und Debugging und können sensible Felder maskieren ([Decision Logs](https://www.openpolicyagent.org/docs/management-decision-logs)). Der Enforcer muss `undefined`, Timeout oder Unerreichbarkeit bewusst fail-closed oder fail-open behandeln; OPA weist darauf hin, dass die Betriebsweise diese Semantik bestimmt ([Operations](https://www.openpolicyagent.org/docs/operations)).

**Erreichbar:** reproduzierbare Policyentscheidung für eine konkrete Policy-/Datenversion und vollständig gelieferte Eingabe; deny-by-default, wenn der Enforcer jede Aktion synchron prüft und Nichtentscheidungen verweigert.

**Nicht erreichbar:** OPA führt die Sperre nicht selbst aus, kennt nicht automatisch versteckte Modellintentionen und bewertet keine sachliche Wahrheit. Fehlende Inputattribute erzeugen keine magische Sicherheit.

**Auswahlkriterien:** OPA lohnt sich bei mehreren Diensten, prüfbaren Regeln und unabhängiger Policy-Lifecycle-Verwaltung. Für wenige lokale Regeln kann eine typisierte Codefunktion einfacher und ebenso erzwingbar sein.

### Isolation: Container, gVisor und Firecracker

Isolation ist eine Laufzeitschicht, kein Agentenframework. Sie soll den Blast Radius (Auswirkungsradius) von generiertem oder fremdem Code begrenzen.

**Gehärteter Container:** Namespaces, cgroups, read-only Root-FS, nicht-root, Capability-Drop, seccomp, AppArmor/SELinux/Landlock und explizites Egress. Er bietet hohe Dichte und Kompatibilität, teilt aber den Host-Kernel. Ein Default-Container ohne Profil ist keine Hochsicherheitsgrenze.

**gVisor:** implementiert einen großen Teil der Linux-Systemoberfläche in einem Userspace-Anwendungskernel und reicht unterstützte Systemaufrufe nicht direkt an den Host durch. Dadurch sinkt die exponierte Host-Kernel-Fläche; spezialisierte Schnittstellen und Kompatibilität sind eingeschränkt. Die eigene Dokumentation betont, dass eine Sandbox keine sichere Gesamtarchitektur ersetzt und Hardware-Seitenkanäle nicht pauschal verschwinden ([Security Model](https://gvisor.dev/docs/architecture_guide/security/)).

**Firecracker:** kapselt je Prozess eine KVM-microVM mit minimiertem Gerätemodell. Die empfohlene Produktionskonfiguration ergänzt die VM-Grenze durch seccomp, cgroups, namespaces und den Jailer. Firecracker filtert laut Design den Gast-Netzverkehr nicht; Egress muss der Host kontrollieren ([Firecracker Design](https://github.com/firecracker-microvm/firecracker/blob/main/docs/design.md)).

**Auswahlkriterien:** Container für vertrauensnähere, gut profilierbare Tools; gVisor für höhere Dichte mit zusätzlicher Kernelentkopplung; Firecracker für stärkere Mandanten-/Workloadtrennung bei akzeptablem Betriebsaufwand. Praktische Benchmarks müssen Startzeit, I/O, benötigte Syscalls, Imageversorgung, Patchprozess und Forensik abdecken. Für hochriskante Werkzeuge sind kurzlebige Instanzen, kein Geheimnis im Gast, read-only Inputs, Ergebnis-Scanning, harte CPU/RAM/PID/Disk-Zeit-Limits und deny-by-default Egress unabhängig von der Technik erforderlich.

## Kombinationsmuster

### A. Kurzlebiger, kontrollierter Agentenworkflow

`API → OPA-Gate → LangGraph/ADK/Agent Framework → isolierte Tool-Adapter → Output-Gate → Audit`

Passend für Minuten bis Stunden, sichtbare Graphzustände und HITL. Persistenter Checkpointer ist Pflicht, sobald Prozessneustarts überlebt werden müssen. Jeder Tool-Aufruf trägt Run-ID, Policyentscheidung und Idempotenzschlüssel.

### B. Lang laufender Geschäftsprozess

`Temporal Workflow → Activities mit Agent-SDK → OPA vor Tools → gVisor/Firecracker für Code → Outbox/Idempotenz → Inspect-Release-Gate`

Temporal hält Zeit, Retry und Zustand; das Agent-SDK bleibt ein probabilistisches Blatt. Modellaufrufe geschehen in Activities, damit Replay keine neue Antwort erzeugt. Fremdsysteme werden nicht durch Temporal allein genau-einmalig.

### C. Eval- und Zulassungspfad

`versionierter Kandidat → Inspect Eval → deterministische Scorer + kalibrierte Judges → Risiko-/Kosten-SLO → Policy-Release-Gate → Canary`

Ein Judge-Score kann eine statistische Freigabebedingung sein, aber keine deterministische Inhaltsgarantie. Sicherheitsinvarianten erhalten deterministische Tests und negative Fälle.

## Erreichbare Garantien samt Voraussetzungen

| Garantiebehauptung | Zulässige Formulierung | Voraussetzungen |
|---|---|---|
| Kontrollfluss | „Nur deklarierte Kanten können genommen werden.“ | nicht umgehbarer Graphexecutor, versionierte Definition, keine freie Toolroute daneben |
| Policy | „Diese Aktion wird ohne Allow-Entscheidung nicht ausgeführt.“ | fail-closed Enforcer vor jeder Aktion, authentisierte vollständige Inputs, geschützter Policy-Store |
| Budget | „Run überschreitet N Aufrufe beziehungsweise reservierte Kosten nicht.“ | atomare Zählung/Reservierung am zentralen Gateway, alle Pfade erfasst |
| Resume | „Der Workflow setzt nach Ausfall aus persistierter Historie fort.“ | verfügbarer Store/Service, kompatibler Code, deterministisches Replay, getestete Recovery |
| Nebenwirkung | „Wiederholte Ausführung erzeugt höchstens einen fachlichen Effekt.“ | Empfänger akzeptiert Idempotenzschlüssel oder transaktionale Outbox/Deduplikation |
| Isolation | „Der Prozess besitzt nur die konfigurierte Datei-, Netzwerk- und Ressourcenfläche.“ | korrektes Host-/Sandboxprofil, keine privilegierten Bypässe, fortlaufendes Patchen und Tests |
| Eval | „Version X erreicht auf Datensatz Y Metrik Z mit angegebenem Intervall.“ | fixierte Artefakte, ausreichende Stichprobe, dokumentierte Runs und Scorer |

Keine Kombination garantiert, dass eine unbekannte Behauptung wahr ist, dass ein Modell nie manipuliert wird oder dass Software und Hardware frei von Schwachstellen sind.

## Nicht-Garantien, Failure Modes und Anti-Patterns

- **Framework als Sicherheitsgrenze:** Ein SDK-Guardrail wird mit einer Sandbox oder Autorisierung verwechselt.
- **Session als Durable Execution:** Gesprächshistorie wird als transaktionaler Workflowzustand behandelt.
- **Checkpoint als Exactly-once:** Resume wiederholt Code vor einem Checkpoint und damit eine nicht-idempotente Aktion.
- **OPA ohne Enforcer:** Die Anwendung fragt eine Policy ab, ignoriert aber Fehler oder erlaubt bei `undefined`.
- **Guardrail-Lücke:** Nur Ein- und Endausgabe werden geprüft; Zwischenagenten, Handoffs oder Hosted Tools bleiben unkontrolliert.
- **In-Memory in Produktion:** Neustart löscht Checkpoints oder Teamzustand.
- **Unversionierte Resume-Pfade:** alter Zustand wird mit inkompatibler Graph- oder Promptversion fortgesetzt.
- **Framework-Monokultur:** Runtime, Policies, Evals und Isolation werden derselben Abstraktion anvertraut und nicht unabhängig geprüft.
- **Sandbox ohne Egress-/Secret-Design:** isolierter Code kann weiterhin Daten exfiltrieren oder Metadatendienste erreichen.
- **Herstellerbenchmark als Architekturbeweis:** ein fremder Benchmark ersetzt keine lokale Baseline und kein Threat Model.
- **Multi-Agent standardmäßig:** zusätzliche Rollen erhöhen Kosten und Fehleroberfläche ohne gemessenen inkrementellen Nutzen; siehe [Multi-Agent und Multi-Modell](../02-multi-agent-und-multi-modell/).

## Entscheidungskriterien

1. **Laufzeit und Ausfallmodell:** Sekunden ohne Resume, Stunden mit Checkpoint oder Monate mit Event History?
2. **Kontrolltopologie:** genügt eine Funktion, braucht es einen festen Graph oder wirklich dynamische Delegation?
3. **Nebenwirkungsrisiko:** read-only Recherche, reversible Änderung oder irreversible Zahlung/Publikation?
4. **Policykomplexität:** lokale Regel oder organisationsweit versionierte, auditierbare Policy?
5. **Isolation:** vertrauenswürdiger Adapter, fremde Bibliothek oder aktiv untrusted Code?
6. **Ökosystem:** Sprache, Hosting, Provider, Datenresidenz, bestehende Observability und Betriebskompetenz.
7. **Reife:** benötigte Funktion in der eingesetzten Version stabil, dokumentiert und durch Crash-/Upgrade-Tests bestätigt?
8. **Portabilität:** sind Modellclient, Zustandsstore, Tracing und Toolprotokoll austauschbar oder proprietär gekoppelt?
9. **Messbarkeit:** lässt sich der Vorteil gegenüber direktem Call oder kleinerem Workflow auf einem Holdout-Satz zeigen?

Eine sachgerechte Auswahl kann daher beispielsweise Temporal plus ein kleines SDK ergeben, LangGraph ohne Temporal, Agent Framework in einem Microsoft-zentrierten Stack, CrewAI für schnelle rollenbasierte Automationen oder nur direkte API-Aufrufe plus OPA und Inspect. Es gibt keinen pauschalen Sieger über diese verschiedenartigen Anforderungen.

## Umsetzbare Checkliste

- [ ] Use Case, Threat Model, Failure Domains und SLOs vor der Produktauswahl dokumentieren.
- [ ] Direkten Modellaufruf und einfachsten Workflow als Baseline messen.
- [ ] Benötigte Funktionen gegen exakt fixierte Frameworkversion und Sprache prüfen.
- [ ] Kontrollfluss, Policy, Persistenz, Eval und Isolation als getrennte Schichten benennen.
- [ ] Für jedes Herstellerfeature die konkrete Konfiguration und Betriebsannahme festhalten.
- [ ] Durable Store statt In-Memory wählen; Backup, Restore und Datenmigration testen.
- [ ] Crash an jeder Aktivitäts-/Knotengrenze injizieren und doppelte Nebenwirkungen prüfen.
- [ ] Alle externen Aktionen mit Idempotenz, Outbox oder Kompensation absichern.
- [ ] Toolpfade inventarisieren; Guardrail-Abdeckung einschließlich Handoffs und eingebauter Tools testen.
- [ ] Policy-Enforcer bei Timeout, `undefined`, veraltetem Bundle und OPA-Ausfall fail-closed testen.
- [ ] Harte Limits für Zeit, Iterationen, Tokens, Kosten, Prozesse, Speicher, Disk und Netzwerk setzen.
- [ ] Sandbox-Egress, Mounts, Secrets, Privilegien und Host-Patching explizit konfigurieren.
- [ ] Traces und Decision Logs korrelieren; sensible Prompt-, Tool- und Policydaten redigieren.
- [ ] Eval-Artefakte hashen, deterministische und statistische Scorer trennen, Konfidenzintervalle berichten.
- [ ] Upgrade-/Rollback-Test mit pausierten und laufenden Workflows durchführen.
- [ ] Architekturentscheidung mit Ablaufdatum versehen und bei Frameworkänderungen neu prüfen.

## Primärquellen

- [LangGraph: Persistence](https://docs.langchain.com/oss/python/langgraph/persistence) und [Interrupts](https://docs.langchain.com/oss/python/langgraph/interrupts).
- [Temporal: What is Temporal?](https://docs.temporal.io/temporal) und [Workflow Execution](https://docs.temporal.io/workflow-execution).
- [Google ADK: Workflow Agents](https://adk.dev/agents/workflow-agents/) und [Graph Workflows](https://adk.dev/graphs/).
- [Microsoft AutoGen: Termination](https://microsoft.github.io/autogen/stable/user-guide/agentchat-user-guide/tutorial/termination.html), [Agent Framework Overview](https://learn.microsoft.com/en-us/agent-framework/overview/) und [Migration from AutoGen](https://learn.microsoft.com/en-us/agent-framework/migration-guide/from-autogen/).
- [OpenAI Agents SDK: Handoffs](https://openai.github.io/openai-agents-python/handoffs/), [Sessions](https://openai.github.io/openai-agents-python/sessions/) und [Guardrails](https://openai.github.io/openai-agents-python/guardrails/).
- [CrewAI: Documentation](https://docs.crewai.com/) und [Flows](https://docs.crewai.com/en/concepts/flows).
- [Inspect AI](https://inspect.aisi.org.uk/).
- [Open Policy Agent](https://www.openpolicyagent.org/docs), [Operations](https://www.openpolicyagent.org/docs/operations) und [Decision Logs](https://www.openpolicyagent.org/docs/management-decision-logs).
- [gVisor Security Model](https://gvisor.dev/docs/architecture_guide/security/).
- [Firecracker Design](https://github.com/firecracker-microvm/firecracker/blob/main/docs/design.md).

Siehe ergänzend [Garantie-Taxonomie](../00-garantie-taxonomie.md), [Durable Execution](../03-durable-execution/), [Verträge und Policy-Gates](../04-vertraege-policy-gates/), [Sicherheit und Isolation](../05-sicherheit-und-isolation/) und [Evaluation und Observability](../06-evaluation-observability/).
