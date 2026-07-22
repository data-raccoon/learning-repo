# Formale Methoden für KI-Harnesses – Kurzfassung

## Kernaussage

Das [`beispiel/`](beispiel/README.md) macht die Abgrenzung praktisch sichtbar: vollständige endliche Exploration, unvollständige Tiefengrenze, Safety-Gegenbeispiel und Runtime-Enforcement werden getrennt ausgewiesen.

Formale Methoden gehören in den deterministischen Kontrollkern eines KI-Harnesses: Zustände, Handoffs, Berechtigungen, Freigaben, Budgets, Retries, Commits und Recovery lassen sich als Transitionen und Invarianten modellieren. Model Checking untersucht alle Abläufe innerhalb eines explizit begrenzten Modells und liefert Gegenbeispiele; Runtime Verification prüft reale Ereignisspuren. Freie Modelltexte werden dagegen sinnvoll als nondeterministische oder adversariale Eingaben behandelt: Der Kernel muss für jede schema-valide Modellausgabe sicher bleiben.

## Garantiert

- Ein erfolgreicher Model Check zeigt, dass eine Eigenschaft für alle untersuchten Zustände des konkret modellierten, endlichen Zustandsraums gilt.
- Ein synchroner, fail-closed und nicht umgehbarer Runtime-Enforcer blockiert eine beobachtete verbotene Transition.
- Ein vollständiger asynchroner Monitor erkennt Verletzungen monitorbarer Regeln in der beobachteten Spur.
- Model-based Tests bestätigen deterministisch die Assertions für die konkret erzeugten Testfälle.

Garantien sind stets an Spezifikation, Bounds, Umgebungsannahmen, Eventvollständigkeit und Code-Konformität gebunden.

## Garantiert nicht

- Ein geprüftes Modell beweist nicht automatisch die Korrektheit des Produktivcodes: Abstraktion, atomare Modellaktionen, Infrastruktur und spätere Codeänderungen erzeugen eine Modell-Code-Lücke.
- Bounded Model Checking deckt keine Zustände außerhalb der offengelegten Grenzen ab.
- Formale Methoden beweisen ohne vollständige Spezifikation weder Wahrheit, Vollständigkeit oder Fairness freier Texte noch Schutz gegen jede Prompt Injection.
- Liveness gilt nur unter expliziten Fairness-, Liefer- und Verfügbarkeitsannahmen.
- Ein Alarm nach einem Commit verhindert die bereits eingetretene Nebenwirkung nicht.

## Einsatzkriterien

- Hoher Schadenswert plus diskret formulierbare Regel: als Invariante spezifizieren und zur Laufzeit erzwingen.
- Nebenläufigkeit, Handoffs, Retries, Crash-Recovery oder Idempotenz: früh Model Checking einsetzen und Duplicate, Reordering, Timeout, Partition und Widerruf modellieren.
- Nur beobachtbare Eigenschaft: Runtime Verification wählen und Vollständigkeit, Reihenfolge sowie Bypass-Sicherheit der Events absichern.
- Offene semantische Qualität: Evals und Human Review statt eines künstlichen Beweisclaims verwenden.
- Zu großer Zustandsraum: Daten abstrahieren, Komponenten getrennt prüfen, Bounds dokumentieren und die Architektur gegebenenfalls vereinfachen.
- Jede formale Aktion auf Codepfad und Telemetrieereignis abbilden; Gegenbeispiele in Regressionstests übernehmen und Conformance in CI prüfen.

## Direkte Quellen

- [Leslie Lamport: Specifying and Verifying Systems with TLA+](https://lamport.azurewebsites.net/pubs/spec-and-verifying.pdf)
- [MCMAS: Model Checking Multi-Agent Systems](https://link.springer.com/article/10.1007/s10009-015-0378-x)
- [EuroSys 2025: Multi-granular Specifications and Model-Code Conformance](https://doi.org/10.1145/3689031.3696069)
- [Survey: Runtime Verification under Uncertainty](https://doi.org/10.1016/j.cosrev.2023.100594)
