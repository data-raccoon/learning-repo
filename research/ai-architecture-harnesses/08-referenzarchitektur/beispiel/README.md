# Beispiel: deterministischer Kernel mit probabilistischem Blatt

Dieses dependency-freie Mini-System demonstriert die zentralen Kontrollpunkte der Referenzarchitektur. Das injizierte `FakeModel` erzeugt ausschließlich einen typisierten `Proposal`. Nur der deterministische `Kernel` darf Zustände wechseln, Budgets verbrauchen, die Policy prüfen, Freigaben validieren und den Tool-Adapter aufrufen.

## Enthaltene Garantien

- Eine explizite Transition-Allowlist verhindert unbekannte Zustandsübergänge.
- `BudgetLease` wird vor Modell- und Toolaufrufen verbraucht und versagt geschlossen.
- `PolicyGate` gleicht Aktion und Ziel nochmals mit dem ursprünglichen `Command` ab.
- Riskante Aktionen pausieren in `APPROVAL_PENDING`. Eine Freigabe bindet `run_id` und den SHA-256-Hash der kanonischen Aktion einschließlich Payload; jede Änderung macht sie ungültig.
- `IdempotentToolAdapter` leitet seinen Schlüssel serverseitig aus Lauf und Vorschlag ab. Ein Retry liefert dasselbe Receipt und erzeugt keinen zweiten sichtbaren Effekt.
- `AppendOnlyAudit` gibt nur unveränderliche Tupel zurück und verkettet Ereignisse per Hash. Dies zeigt Manipulationserkennung, ersetzt aber keinen dauerhaften WORM-/Datenbank-Speicher.

Nicht garantiert werden semantische Richtigkeit des Modellvorschlags, kryptografische Identität eines Approvers oder Exactly-once gegenüber beliebigen externen Systemen. Das Beispiel hält alle Daten im Arbeitsspeicher; Produktion benötigt transaktionale Persistenz und einen Zielsystem-spezifischen Idempotenzvertrag.

## Dateien

- `reference_architecture.py` – vollständige Mini-Implementierung
- `demo.py` – zweiphasiger Lauf mit risikoreicher Aktion und Freigabe
- `test_reference_architecture.py` – Happy Path sowie Negativ- und Retry-Tests

## Ausführen

Im Verzeichnis `beispiel/` mit der für dieses Repository vorgegebenen Python-Umgebung:

```powershell
& "$env:USERPROFILE\.venvs\all\Scripts\python.exe" demo.py
& "$env:USERPROFILE\.venvs\all\Scripts\python.exe" -m unittest -v
```

Erwartet werden ein Lauf bis `committed`, eine gültige Auditkette und fünf erfolgreiche Tests. Es erfolgen keine Netzwerkzugriffe, Dateiänderungen oder externen Toolaufrufe.
