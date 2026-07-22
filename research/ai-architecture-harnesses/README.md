# KI-Architektur und Harnesses mit technischen Garantien

Stand: 2026-07-22

## Kernaussage

Der belastbarste Default für produktive KI-Systeme ist ein **deterministischer Kernel mit probabilistischen Blättern**: Code kontrolliert Zustand, Identität, Berechtigungen, Budgets, Abbruch, Wiederholung und Commits; Modelle arbeiten nur innerhalb begrenzter Schritte. Eine Eigenschaft gilt erst dann als Garantie, wenn Mechanismus, Annahmen, Geltungsbereich und Failure Domain ausdrücklich benannt sind.

Weder ein überzeugender Prompt noch mehrere übereinstimmende Agenten beweisen Wahrheit. Schema-konformes JSON beweist keine fachliche Richtigkeit. Persistente Ausführung macht externe Nebenwirkungen nicht automatisch *exactly once*. Sandboxing reduziert Angriffsfläche, beseitigt aber weder Fehlkonfigurationen noch alle Seitenkanäle. Multi-Agent und Multi-Modell sind daher Optimierungen, die sich gegen eine einfachere Baseline in Evaluationen bewähren müssen—keine Zuverlässigkeitsgarantie an sich.

## Garantie-Legende

| Kennzeichen | Aussageklasse | Was als Nachweis zählt | Typisches Beispiel |
|---|---|---|---|
| **G1 – erzwingbar** | Deterministisch durch Code oder Infrastruktur erzwungen | Testbarer Enforcer und klarer Scope | JSON-Schema, ACL, hartes Budget, erlaubte Zustandsübergänge |
| **G2 – bedingt** | Unter expliziten technischen Annahmen garantiert | Annahmen, Failure Domain und Recovery-Protokoll | Durable Replay bei deterministischem Workflow und idempotenten Activities |
| **G3 – messbar** | Statistisch für eine definierte Verteilung belegt | Versionierter Eval-Satz, Metrik, Konfidenz und Zeitraum | Erfolgsrate, SLO, Regression Gate |
| **G4 – heuristisch** | Kann helfen, ist aber kein belastbarer Beweis | Empirischer Vergleich, niemals bloße Plausibilität | Prompting, Selbstkritik, LLM-as-Judge, Agentenmehrheit |

Die Klassen sind nicht austauschbar: Eine G3-Verbesserung wird nicht durch gute Durchschnittswerte zu G1, und ein G1-Format-Gate garantiert nur das Format, nicht den Wahrheitsgehalt.

## Navigation

### Grundlagen und Mechanismen

- [00 – Garantie-Taxonomie](00-garantie-taxonomie.md): Begriffe, Annahmen, Garantie-Ledger und Failure Domains.
- [01 – Workflow-first](01-workflow-first/): Langfassung, Kurzfassung und deterministischer Workflow-Kernel.
- [02 – Multi-Agent und Multi-Modell](02-multi-agent-und-multi-modell/): Langfassung, Kurzfassung und kontrolliertes Routing-/Ensemble-Beispiel.
- [03 – Durable Execution](03-durable-execution/): Langfassung, Kurzfassung und Event-History-/Replay-Beispiel.
- [04 – Verträge, Policy und Gates](04-vertraege-policy-gates/): Langfassung, Kurzfassung und fail-closed Contract-/Policy-Gates.
- [05 – Sicherheit und Isolation](05-sicherheit-und-isolation/): Langfassung, Kurzfassung und Capability-basierter Tool-Proxy.
- [06 – Evaluation und Observability](06-evaluation-observability/): Langfassung, Kurzfassung und Eval-/Tracing-Harness.
- [07 – Formale Methoden](07-formale-methoden/): Langfassung, Kurzfassung und begrenzter Zustandsraumprüfer.

### Synthese und Einführung

- [08 – Referenzarchitektur](08-referenzarchitektur/): integrierter Kontroll-/Datenfluss und ausführbare Mini-Referenzarchitektur.
- [09 – Harness-Vergleich](09-harness-vergleich/): Frameworkvergleich und ausführbarer Adapter-/Conformance-Vertrag.
- [10 – Einführungsplan](10-einfuehrungsplan/): Reifestufen und ausführbares Evidence-/Release-Gate.
- [Quellenregister](quellen.md): kuratierte Primärquellen, peer-reviewte Arbeiten und ausdrücklich markierte Preprints.

Jeder Ansatz-Ordner folgt derselben Struktur: `README.md` (Langfassung), `KURZFASSUNG.md` und `beispiel/` (Implementierung, Tests und Ausführungsanleitung).

Alle Beispiele verwenden ausschließlich die Python-Standardbibliothek und laufen offline mit Fake-Modellen. Gesamttest vom Repository-Root:

```powershell
& "$env:USERPROFILE\.venvs\all\Scripts\python.exe" research\ai-architecture-harnesses\verify_examples.py
```

Framework-Funktionen und Dokumentationsstände ändern sich. Die Vergleichsaussagen sind deshalb auf das Abrufdatum bezogen und vor einer Implementierungsentscheidung erneut gegen die verlinkten Herstellerquellen zu prüfen.

## Entscheidungsbaum

```text
Ist der Prozess fachlich als feste Schritte und Invarianten beschreibbar?
├─ Ja → Workflow/State Machine als Kontrollkern verwenden.
│       Braucht der Prozess Wiederaufnahme nach Absturz oder langer Pause?
│       ├─ Ja → Durable Execution; Replay deterministisch halten,
│       │       Nebenwirkungen idempotent bzw. transaktional absichern.
│       └─ Nein → einfacher Workflow mit persistiertem Audit-Log genügt oft.
└─ Nein → Ist modellgesteuerte Exploration tatsächlich erforderlich?
        ├─ Nein → Single Call, Retrieval oder deterministisches Routing wählen.
        └─ Ja → begrenzten Agent-Loop mit Tool-Allowlist, Budget,
                Stop Conditions, Checkpoints und Freigaben einsetzen.

Sind mehrere unabhängige Teilaufgaben oder spezialisierte Modelle nachweislich nützlich?
├─ Nein → bei Single-Agent/Single-Modell bleiben.
└─ Ja → Multi-Agent/Multi-Modell hinter identischen Verträgen und Gates testen;
        nur bei messbarem Gewinn gegenüber der Baseline zulassen.

Kann eine Aktion Geld, Daten, Rechte oder externe Systeme wesentlich verändern?
├─ Ja → Policy-Enforcement + Idempotenz/Outbox + expliziter Commit;
│       bei hohem Risiko menschliche Freigabe.
└─ Nein → automatische Ausführung innerhalb enger Capabilities möglich.

Ist die geforderte Aussage eine echte Garantie?
├─ Durch Enforcer vollständig entscheidbar → als G1 mit Scope dokumentieren.
├─ Nur unter Systemannahmen beweisbar → als G2 mit Annahmen dokumentieren.
├─ Nur empirisch bewertbar → als G3 mit Eval und SLO dokumentieren.
└─ Nur plausibilitätssteigernd → als G4 kennzeichnen, nicht als Gate allein nutzen.
```

## Empfohlene Lesepfade

- **Architekturentscheidung:** 00 → 01 → 08 → 10.
- **Agenten und Modellrouting:** 00 → 02 → 06 → 09.
- **Zuverlässige Nebenwirkungen:** 00 → 03 → 04 → 08.
- **Security Review:** 00 → 04 → 05 → 08.
- **High Assurance:** 00 → 03 → 07 → 08 → 10.

Für eine schnelle Orientierung zuerst `KURZFASSUNG.md` im jeweiligen Ansatz-Ordner lesen; die dortige Langfassung enthält Annahmen, Failure Modes, Entscheidungskriterien und umsetzbare Checklisten.
