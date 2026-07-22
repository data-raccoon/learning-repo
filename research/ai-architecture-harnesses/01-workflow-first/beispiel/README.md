# Beispiel: deterministischer Workflow-Kernel

Dieses vollständig lokale Python-Beispiel setzt ein probabilistisches Blatt in einen festen Kontrollpfad:

```text
RECEIVED -> VALIDATED -> PROPOSED -> POLICY_CHECKED -> COMMITTED
     |          |           |              |
     +----------+-----------+--------------+-> REJECTED oder FAILED
```

`workflow.py` enthält den Kernel, `demo.py` einen ausführbaren In-Memory-Durchlauf und `test_workflow.py` positive sowie negative Tests. Es werden ausschließlich Module der Python-Standardbibliothek verwendet. Der Demo-Callback ist absichtlich deterministisch; an derselben Schnittstelle kann eine probabilistische Modellintegration injiziert werden, ohne ihr Zustands- oder Commit-Rechte zu geben.

## Ausführen

Im Ordner `beispiel/` mit dem für dieses Repository vorgegebenen Interpreter:

```powershell
& "$env:USERPROFILE\.venvs\all\Scripts\python.exe" demo.py
& "$env:USERPROFILE\.venvs\all\Scripts\python.exe" -m unittest -v
```

Es sind weder Netzwerkzugriff noch API-Key oder Installation erforderlich.

## Technische Eigenschaften

- Eine geschlossene Transitionstabelle entscheidet über alle Zustandswechsel.
- Der Modelladapter erhält nur den unveränderlichen `Request` und liefert einen unveränderlichen, untrusted `Proposal`.
- Vier Dispatches bilden das Schrittbudget: Validierung, Modellblatt, Gate und Commit.
- Die bekannten Kosten des Modellblatts werden **vor** seinem Aufruf vollständig reserviert. Reicht das Kostenbudget nicht, wird der Callback nicht ausgeführt.
- Das Commit-Gate prüft exakt den `Proposal`, der anschließend an den Commit-Adapter geht. Sein kanonischer SHA-256-Digest erscheint in den Audit-Events.
- Ablehnung, Budgetfehler, falscher Rückgabetyp sowie Modell- oder Commit-Ausnahmen enden fail-closed ohne erfolgreichen Commit-Zustand.
- Audit-Events sind unveränderliche Werte und werden über eine read-only Tupelansicht veröffentlicht.

Die Tests belegen unter anderem, dass bei ungültiger Eingabe kein Modellaufruf erfolgt, bei unzureichendem Kostenbudget keine Dispatch stattfindet, das Schrittlimit den Commit verhindert, ein negatives Gate keinen Commit zulässt und Adapterfehler nie als `COMMITTED` erscheinen.

## Garantiegrenze

Das Beispiel erzwingt die aufgeführten Eigenschaften innerhalb eines einzelnen Python-Prozesses, sofern Aufrufer ausschließlich den Kernel verwenden. Es garantiert weder die Wahrheit des Vorschlags noch Crash-Wiederaufnahme, verteilte Atomarität oder eine tatsächlich unveränderliche Audit-Ablage. Für Produktion müssten Zustand, Budgetreservierung und Audit-Append atomar in einem dauerhaften Store liegen; der Commit-Adapter müsste als einzige Zugriffsroute zur Nebenwirkung technisch erzwungen und idempotent gestaltet werden. Zeitbudgets erfordern zudem einen isolierbaren Adapter mit hartem Timeout.
