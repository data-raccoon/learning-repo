# Beispiel: Bounded Model Checking und Runtime Verification

Dieses dependency-freie Python-Beispiel modelliert einen kleinen High-Risk-Agentenworkflow. Der Model Checker enumeriert per Breitensuche alle erreichbaren Zustände bis `max_depth`, prüft Safety-Invarianten und liefert für eine Verletzung eine kürzeste Ereignisspur. Nichtterminale Zustände ohne Folgetransition werden als Deadlock und damit als einfache Liveness-Warnung gemeldet. Der synchrone Runtime-Monitor verwendet dieselbe Transitionsfunktion und lehnt verbotene Ereignisse fail-closed ab.

## Ausführen

Python 3.10 oder neuer genügt; es gibt keine externen Abhängigkeiten.

```powershell
& "$env:USERPROFILE\.venvs\all\Scripts\python.exe" demo.py
& "$env:USERPROFILE\.venvs\all\Scripts\python.exe" -m unittest discover -s tests -v
```

Dateien:

- `workflow_model.py`: Zustände, Ereignisse, Transitionen und Invarianten;
- `model_checker.py`: bounded Breitensuche, Vollständigkeitsindikator, Deadlocks und kürzestes Gegenbeispiel;
- `runtime_monitor.py`: Monitor derselben Ereignisregeln;
- `demo.py`: sichere, unsichere und blockierte Modellvariante;
- `tests/`: gültiges Modell, Safety-Verstoß, Deadlock, unzureichende Tiefe und Runtime-Enforcement.

## Was die Ergebnisse aussagen

`complete=True` bedeutet nur, dass ab dem gewählten Anfangszustand keine neue Zustandsvariante an der Tiefengrenze abgeschnitten wurde. Zusammen mit `counterexample=None` gilt die Safety-Aussage damit für den vollständigen **endlichen Zustandsraum dieses Modells**. `complete=False` bedeutet: Bis zur Grenze wurde keine Verletzung gefunden; außerhalb der Exploration ist keine Aussage möglich. Das erste Gegenbeispiel ist wegen der Breitensuche hinsichtlich der Anzahl von Ereignissen kürzest.

Die Deadlockprüfung ist lediglich eine Liveness-Näherung. Sie findet erreichbare nichtterminale Zustände ohne ausgehende Kante. Sie beweist weder Fairness noch „eventually“-Eigenschaften und erkennt keine Zyklen, in denen Fortschritt unendlich lange ausbleiben kann.

## Modellgrenze

Endlich modelliert sind genau ein Run, eine Risikoklasse, ein kleines Budget, eine Autorisierungsentscheidung, eine Freigabe und höchstens ein logischer Commit. Ereignisse sind atomar und seriell. Modellausgaben, Netzwerke, konkurrierende Runs, Persistenz, Crash-Zeitpunkte, Idempotency-Key-Kollisionen und reale Toolantworten sind nicht enthalten. Die beiden Optionen injizieren gezielt eine unsichere Commit-Kante beziehungsweise einen nicht antwortenden Approval-Service; sie simulieren kein vollständiges Fehlermodell.

## Modell-Code-Lücke

Der Checker prüft `workflow_model.py`, nicht einen Produktivdienst. Auch der Runtime-Monitor schützt nur Aufrufe, die tatsächlich durch `observe()` geleitet werden. Ein direkter Toolpfad, verlorene oder falsch korrelierte Events, eine falsche Risikoklassifikation sowie Nebenwirkungen vor der Monitorentscheidung umgehen den Claim. Im Produktivsystem müssten alle Effektpfade denselben nicht umgehbaren Adapter nutzen, Events müssten vollständig instrumentiert sein und Conformance-Tests müssten jede Modellaktion auf konkrete Codepfade abbilden. Eine Änderung an Retry-, Approval- oder Commit-Semantik erfordert eine gemeinsame Änderung und Prüfung von Modell, Monitor und Implementierung.

Dieses Lernbeispiel demonstriert Mechanik und Claims; es ersetzt weder TLC/TLA+ für realistische Nebenläufigkeit noch domänenspezifische Evals und Security Reviews.
