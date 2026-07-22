# Beispiel: kontrollierter Multi-Agent-/Multi-Modell-Harness

Dieses lauffähige Python-Beispiel hält die Kontrolllogik außerhalb der Modelle. Es benötigt nur Python 3.10+ und die Standardbibliothek; `FakeModel` macht Demo und Tests reproduzierbar und vollständig offline.

## Enthaltene Mechanismen

- `DeterministicRouter`: feste Route aus Aufgabentyp und Empfängerrolle auf eine registrierte Modell-ID.
- `Handoff`: unveränderlicher, zur Laufzeit validierter Vertrag mit Schema-Version, Korrelation, Rollen, Grundcode, Aufgabentyp und Scope.
- `Orchestrator.validate_disjoint`: weist leere oder überlappende Worker-Scopes vor jedem Modellaufruf zurück.
- `AtomicBudget`: reserviert Aufrufe und Token unter einem Lock vor parallelem Fan-out. Ein Worker kann das für einen anderen reservierte Restbudget nicht ausgeben.
- `resolve_votes`: zählt höchstens eine Stimme je deklarierter Fehlerdomäne, legt Gleichstände und fehlendes Quorum offen und unterscheidet unbestätigten Konsens von deterministisch verifiziertem Ergebnis.
- `compare_baseline_and_ensemble`: berichtet Accuracy, Enthaltungen, Aufrufe und Tokens für eine einfache Baseline und ein Ensemble auf denselben gelabelten Fällen.

## Ausführen

Im Ordner `beispiel/`:

```powershell
& "$env:USERPROFILE\.venvs\all\Scripts\python.exe" demo.py
& "$env:USERPROFILE\.venvs\all\Scripts\python.exe" -m unittest discover -s tests -v
```

Erwartete Demo-Ausgabe:

```text
market: stable via small-analyst
risk: low via special-verifier
baseline accuracy=50%, calls=2
ensemble accuracy=100%, calls=6
```

## Sicherheits- und Garantiegrenzen

Der Harness erzwingt bei vollständiger Nutzung seines Aufrufpfads Schema-/Kantenprüfung, disjunkte Scopes und nominelle Call-/Token-Budgets. Die Reservierung ist innerhalb eines Prozesses threadsicher. Für mehrere Prozesse oder Hosts müsste dieselbe Operation als Transaktion in einem konsistenten externen Store implementiert werden.

`failure_domain` ist eine deklarierte Eigenschaft, kein Unabhängigkeitsbeweis. Die Tests zeigen deshalb zwei wichtige Nicht-Garantien: Viele korrelierte Stimmen bilden kein unabhängiges Quorum; selbst ein Quorum aus verschiedenen Fehlerdomänen kann sachlich falsch sein. Ohne objektiven Verifier heißt der Status bewusst `consensus_unverified`.

Die Evaluation ist eine didaktische Baseline, keine belastbare Statistik. Eine Produktionszulassung braucht einen versionierten repräsentativen Holdout-Satz, wiederholte Läufe, Konfidenzintervalle sowie Kosten- und Latenz-SLOs. Modelladapter sollten außerdem echte Provider-Nutzung anhand gemessener statt selbst gemeldeter Tokens abrechnen.

## Erweiterung auf reale Modelle

Ein Adapter implementiert lediglich das `Model`-Protokoll (`model_id`, `failure_domain`, `invoke`). Der Provider-Client gehört hinter diesen Adapter. Handoff-Validierung und Budgetreservierung bleiben davor; externe Schreibaktionen gehören hinter ein separates Policy- und Commit-Gate. Secrets, Netzaufrufe und SDK-Abhängigkeiten sind absichtlich nicht Teil dieses Beispiels.
