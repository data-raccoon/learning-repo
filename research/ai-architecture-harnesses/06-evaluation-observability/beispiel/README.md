# Beispiel: Eval- und Observability-Harness

Diese ausschließlich mit der Python-Standardbibliothek gebaute Referenz zeigt den kleinsten vollständigen Regelkreis von einer versionierten Aufgabenbank bis zur Canary-Entscheidung. Der Agent ist absichtlich ein lokaler Fake: Die Architektur lässt sich ohne Netzwerk, Zugangsdaten oder schwankende Anbieterzustände prüfen.

## Enthaltene Garantien und Grenzen

- `cases.v1.json` versioniert Schema, Suite und einzelne Cases.
- Der exakte Outcome-Grader ist deterministisch. Derselbe Agenten-Snapshot, Seed, Case und Trial erzeugt dasselbe fachliche Resultat.
- Wiederholte Trials und das Wilson-95-%-Intervall machen Stichprobenunsicherheit sichtbar.
- Unvollständige Trials verbleiben im Nenner und blockieren das Release-Gate. Damit verschwinden Timeouts nicht durch Survivorship Bias.
- Das Regression-Gate blockiert kritische Fehler, unvollständige Stichproben und eine Verschlechterung jenseits der Toleranz (Punktschätzer und konservative Wilson-Untergrenze).
- Das Canary-Gate liefert nur `continue`, `rollback` oder `promote` anhand expliziter SLOs. Kritische Verletzungen erzwingen unabhängig von der Stichprobengröße sofort den Rollback; ohne kritischen Verstoß blockiert eine zu kleine Stichprobe die Promotion.
- Strukturierte JSONL-Traces werden rekursiv **vor** Speicherung redigiert. Das Beispiel entfernt sensible Schlüssel, E-Mail-Adressen und häufige Inline-Secrets.

Das Harness garantiert nicht, dass Cases repräsentativ, Grader fachlich vollständig oder Redaction-Regeln lückenlos sind. Ein grünes Gate belegt nur die kodierten Bedingungen für diese Stichprobe.

## Ausführen

Im Ordner `beispiel/` mit dem in den Repository-Anweisungen festgelegten Interpreter:

```powershell
& "$env:USERPROFILE\.venvs\all\Scripts\python.exe" -m unittest -v
& "$env:USERPROFILE\.venvs\all\Scripts\python.exe" demo.py
```

Die Demo schreibt `traces.jsonl` (absichtlich nicht vorab eingecheckt) und gibt den vollständigen Vergleichs- und Canary-Bericht als JSON aus.

## Dateien

| Datei | Zweck |
|---|---|
| `cases.v1.json` | Versionierte Cases und erwartete Outcomes |
| `eval_harness.py` | Agent, Grader, Trials, Wilson-Intervall, Gates und Tracing |
| `demo.py` | Reproduzierbarer End-to-End-Lauf |
| `test_eval_harness.py` | Tests für Regression, Redaction, Determinismus und unvollständige Stichproben |

Für Produktion müssten unter anderem persistente unveränderbare Evidence, segmentierte SLOs, Zugriffskontrolle, Retention, Schema-Validierung, unabhängige Holdouts und ein echter Deployment-Controller ergänzt werden.
