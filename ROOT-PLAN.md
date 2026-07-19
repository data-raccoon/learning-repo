# Vendor-neutrale Multi-Model-Orchestrierung

## Zusammenfassung

Im neuen Top-Level-Bereich `agent-orchestrator/` entsteht ein Python-basierter Orchestrierungskern. Die aktuell laufende Codex-Instanz verwendet ihn über die repo-lokale Skill `.agents/skills/orchestrate-models`.

Der erste Meilenstein führt folgende Worker tatsächlich aus:

- lokale Ministral-Modelle über `llama.cpp` und OpenAI-kompatible Endpunkte;
- lokale sowie Cloud-Modelle über Mistral Vibe;
- mehrere Modelle parallel, soweit Provider, Zielordner und lokale GPU-Slots dies erlauben.

OpenAI/ChatGPT und Mammouth werden zunächst vollständig im Provider-/Modell-Inventar abgebildet, bleiben mangels eingerichteter Subprozess-Authentifizierung jedoch `unavailable` und werden noch nicht geroutet. Spätere Adapter verwenden `codex exec` beziehungsweise Mammouths OpenAI-kompatible API. Codex unterstützt dafür bereits JSONL, strukturierte Outputs, Sandbox-Modi und ChatGPT- oder API-Authentifizierung. [OpenAI Codex Non-interactive Mode](https://developers.openai.com/codex/noninteractive), [OpenAI Authentication](https://developers.openai.com/codex/auth), [Mammouth API](https://info.mammouth.ai/docs/api-quick-start/)

## Architektur und öffentliche Schnittstellen

- Der Kern trennt vier Entitäten:
  - `Provider`: Authentifizierung, Endpoint, Verfügbarkeit und Abrechnungsart.
  - `Model`: konkrete Modell-ID, Kontext, Modalitäten, Preise und deklarierte Fähigkeiten.
  - `Harness`: direkte API, Vibe CLI, später Codex CLI oder ein lokaler Runtime-Treiber.
  - `ModelProfile`: evaluierte Fähigkeiten der exakten Kombination aus Provider, Modell, Harness, Version und Quantisierung.
- Versionierte TOML-Registries enthalten Ministral lokal, mehrere Mistral-Cloud-Modelle sowie vorbereitete OpenAI/ChatGPT- und Mammouth-Einträge. Dynamisch ermittelte Providerdaten ergänzen die Registry, überschreiben aber keine geprüften Capability-Profile.
- Preise erhalten Quelle und `effective_at`. Abonnements werden als `included_subscription` oder `unknown_marginal_cost` geführt und nicht irreführend als kostenlos bewertet.
- Ein versioniertes JSON-Jobformat definiert:
  - Ziel, Rolle, Wichtigkeit und Risikoklasse;
  - einen kanonischen Ziel-Unterordner;
  - Read-/Write-Modus und erlaubte Toolklasse;
  - benötigte Capabilities und erwartete Artefakte;
  - ausschließlich innerhalb des Zielordners liegende Kontextdateien;
  - Abhängigkeiten, Output-Schema, benannte Verifier sowie Zeit-, Turn- und Token-Stoppgrenzen.
- Die CLI stellt bereit:
  - `doctor` – Installationen, Authentifizierung und Runtime-Verfügbarkeit prüfen;
  - `inventory` – Provider, Modelle, Profile, Kosten und Status anzeigen;
  - `route` – Routingentscheidung erklären, ohne einen Worker zu starten;
  - `run` – einen Job ausführen;
  - `run-graph` – einen DAG mit zulässiger Parallelität ausführen;
  - `status` – kompakte Run-Evidenz liefern;
  - `runtime start|status|stop` – registrierte lokale Laufzeiten verwalten;
  - `eval run` – Capability-Profile erzeugen oder erneuern.
- Standardausgabe ist ein kompaktes JSON-Resultat mit Run-ID, Route, Status, Artefaktpfaden, Gate-Ergebnissen, Tokenverbrauch, Kostenart, Dauer und Fehlercode. Vollständige Modellantworten und Trajektorien bleiben in `.runtime/` und gelangen nicht in den Kontext der Haupt-KI.

## Ausführung, Routing und Sicherheit

- Die Root-KI ist der einzige Scheduler; Worker dürfen keine weiteren Worker starten.
- Jeder Worker erhält seinen Ziel-Unterordner als alleinigen Workdir. Alle benötigten Verträge, Daten und Anweisungen müssen dort bereits vorhanden sein; fehlender Kontext beendet den Job als Planungsfehler.
- Kleine oder noch nicht qualifizierte Modelle erhalten ausschließlich vermittelte Dateioperationen. Shell, Netzwerk, Skills, Connectoren und Subagenten bleiben deaktiviert.
- Qualifizierte Coding-Agenten dürfen nur allowlistete Commands mit strukturierten Argumenten und Working Directory innerhalb des Zielordners ausführen. Pfade werden vor jedem Lauf kanonisch aufgelöst; Symlink-/Traversal-Ausbrüche werden abgewiesen.
- Schreibjobs sperren ihren Zielordner gegen andere Worker. Read-only-Jobs dürfen parallel laufen; Schreibjobs mit überlappenden Zielpfaden werden serialisiert. Der lokale Ministral-Server bleibt wegen seines einzelnen Slots auf Parallelität `1`.
- Vor einem Schreibjob wird der vollständige Zustand des Zielordners außerhalb davon in `.runtime/` gesichert. Schlägt ein Gate fehl:
  - wird ein Quarantäne-Patch samt neu erzeugter Dateien und Run-Evidenz bewahrt;
  - wird exakt der vorherige Zustand wiederhergestellt;
  - werden keine Änderungen außerhalb des Zielordners berührt.
- Acceptance basiert auf unabhängigen Verifiern, Artefakthashes und strukturellen Guards. Die Haupt-KI liest nur Zusammenfassungen; vollständige Diffs werden nur bei fehlgeschlagenen oder explizit angeforderten Reviews geladen.
- Routing erfolgt in dieser Reihenfolge:
  1. Verfügbarkeit, Pfadpolicy, Risiko und zwingende Capabilities filtern;
  2. bei kritischer Planung/Architektur das stärkste zugelassene Profil wählen;
  3. bei sonstigen Jobs das schwächste Profil wählen, dessen Eval-Konfidenz den Qualitätswert der Jobklasse erfüllt;
  4. Kosten und Latenz als Tiebreaker verwenden;
  5. bei qualifiziertem Fehlschlag genau eine Stufe eskalieren, sofern der Fehler als Modell- und nicht als Harness-/Planungsfehler klassifiziert wurde.
- Ausgangswerte für erwartete Erfolgswahrscheinlichkeit: `critical 0.98`, `high 0.95`, `normal 0.85`, `low 0.75`. Kritische Jobs verlangen zusätzlich unabhängige Prüfung.
- Keine finanzielle Obergrenze wird erzwungen. Trotzdem gelten Stoppgrenzen gegen Schleifen, und tatsächliche beziehungsweise geschätzte Gesamtkosten inklusive Retries werden protokolliert.

## Codex-Integration und Migration

- Die Skill `orchestrate-models` wird mit dem offiziellen Skill-Gerüst erzeugt, erhält `SKILL.md` und `agents/openai.yaml` und wird mit dem Skill-Validator geprüft.
- Eine knappe Root-`AGENTS.md` erklärt Codex:
  - wann Delegation sinnvoll ist;
  - dass Jobs über die Orchestrator-CLI laufen;
  - dass große Worker-Artefakte nicht in den Hauptkontext kopiert werden;
  - dass ein Worker niemals direkt außerhalb seines Zielordners gestartet wird.
- Die vorhandenen experimentellen Runner werden zunächst nicht entfernt. Ihre universellen Mechanismen – Job-Specs, Hashes, Run Records, strukturierte Outputs, Vibe-Multimodalität und lokale Runtime-Steuerung – werden in den neuen Kern überführt.
- Nach Parität werden die Game-Building-Runner zu dünnen Kompatibilitäts-Wrappern oder dokumentierten historischen Experimenten.
- Company-OS, Software-OS, Mental-Health-OS und weitere Systeme bleiben normale Use Cases. Sie können eigene Jobvorlagen und Policy-Overrides besitzen, verändern aber weder das globale Datenmodell noch die Kern-Routinglogik.

## Test- und Abnahmekriterien

- Schema- und Pfadtests lehnen unbekannte Felder, absolute Fremdpfade, `..`, Symlink-Ausbrüche, fehlende Kontextdateien und überlappende Writer ab.
- Fake-Adapter testen Routing, Retries, Parallel-DAGs, Timeouts, JSONL-Ereignisse, Kostenaggregation und Provider-Ausfälle deterministisch.
- Ein lokaler Live-Canary startet Ministral bei Bedarf, prüft Authentifizierung und GPU-Prozess, führt einen read-only Job aus und stoppt nur einen vom Orchestrator selbst gestarteten Prozess.
- Ein lokaler File-only-Canary beweist, dass das Modell Dateien im Zielordner lesen und schreiben, aber keinen Command ausführen oder außerhalb lesen kann.
- Ein Mistral-Cloud-Canary führt einen strukturierten read-only Job über Vibe aus und erfasst Modell, Usage, Dauer, Artefakthash und Providerstatus.
- Ein Paralleltest führt unabhängige Cloud-Jobs gleichzeitig aus, serialisiert überlappende Writer und begrenzt lokale Jobs auf den registrierten Runtime-Slot.
- Ein Fehlerfall erzeugt einen Quarantäne-Patch, stellt den exakten Ausgangszustand wieder her und bewahrt Diagnose-Evidenz.
- Eval-Fixtures decken Architektur/Planung, Coding, Reparatur, Review, strukturierte Extraktion, Tool-Nutzung, langen Kontext und Multimodalität ab.
- OpenAI/ChatGPT und Mammouth erscheinen korrekt als `unavailable`, werden nicht ausgewählt und erhalten erst nach späterer Authentifizierung und bestandenen Live-/Capability-Gates den Status `eligible`.
- Die Abnahme verlangt keine manuelle Prüfung jedes Edits: grüne unabhängige Gates, unveränderte Fremdpfade, valide Hashes und ein kompakter Run-Report genügen.

## Annahmen

- Implementierungssprache ist Python 3.14 mit möglichst wenigen Abhängigkeiten; Konfiguration nutzt TOML, Austausch- und Evidenzformate nutzen JSON/JSONL.
- Windows ist die zuerst qualifizierte Plattform; Provider- und Scheduler-Kern bleiben plattformneutral.
- `agent-orchestrator/` ist der neue Plattformname und `.runtime/` bleibt vollständig unversioniert.
- OpenAI/ChatGPT- und Mammouth-Ausführung folgt in einem zweiten Inkrement; ihre Registry-, Routing- und Contract-Tests gehören bereits zum ersten.
- Das bestehende lokale Ministral-Modell, `llama.cpp`, Vibe 2.20 und externe Secret-Dateien werden wiederverwendet; Schlüssel, Modellgewichte, PID- und Logdateien gelangen nicht ins Repository.
