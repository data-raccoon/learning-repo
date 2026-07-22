# Beispiel: Evidence- und Release-Gate

Diese dependency-freie Python-Referenzimplementierung operationalisiert den stufenweisen Einführungsplan. Sie prüft ein versioniertes Manifest und gibt ausschließlich eine Entscheidung samt Handlungsplan aus. Sie besitzt absichtlich keinen Deployment-, Netzwerk-, Shell- oder Credential-Pfad.

## Eigenschaften

- kumulative Muss-Evidenz und Pflichtmetriken für Stufen 0–6;
- SHA-256- und Frischeprüfung lokaler Evidenzdateien;
- Mindest- und Höchstschwellen für SLOs und statistische Evals;
- acht universelle Stop-Signale, die explizit `false` sein müssen;
- stufenweiser Übergang, Canary-Mindestdauer und Mindeststichprobe;
- Entscheidungen `CANARY`, `PROMOTE`, `HOLD` oder `ROLLBACK`;
- fail closed bei unbekanntem, fehlendem, altem oder manipuliertem Nachweis.

Die eingebauten Listen in `STAGE_EVIDENCE` und `STAGE_METRICS` bilden die Policy. Das Manifest pinnt sie über `gate_policy_version`; eine abweichende Version wird abgewiesen. Anforderungen sind kumulativ. Dadurch kann ein Manifest für eine höhere Stufe frühere Kontrollen nicht stillschweigend entfernen.

## Ausführen

Im Ordner `beispiel`:

```powershell
& "$env:USERPROFILE\.venvs\all\Scripts\python.exe" demo.py
& "$env:USERPROFILE\.venvs\all\Scripts\python.exe" -m unittest -v
```

Erwartete Demo-Ausgabe:

```text
PRE-CANARY: CANARY
CANARY COMPLETE: PROMOTE
STOP SIGNAL: ROLLBACK to stage 0
```

Ein eigenes Manifest wird so geprüft:

```powershell
& "$env:USERPROFILE\.venvs\all\Scripts\python.exe" release_gate.py C:\path\release-manifest.json --output decision-plan.json
```

Exitcode `0` bedeutet `CANARY` oder `PROMOTE`, Exitcode `2` bedeutet `HOLD` oder `ROLLBACK`. Der Exitcode allein darf nicht als Deployment-Freigabe verwendet werden; der aufrufende, separat autorisierte Release-Controller muss zusätzlich die konkrete Entscheidung lesen.

## Manifestvertrag

Das JSON-Objekt enthält:

- `manifest_version` und `gate_policy_version`;
- `release_id`, `created_at` und `target_stage` (0–6);
- Pins für Code, Prompt, Policy, Schema, Eval-Datensatz und Modell;
- Evidenzobjekte mit ID, relativem Pfad, SHA-256, Status, Erhebungszeit und maximalem Alter;
- Messwerte mit ID, Wert, mindestens einer Schwelle und Frischeangaben;
- jeden bekannten Stop-Indikator als echten booleschen Wert;
- Rolloutphase, Ist-/Ziel-/Rollback-Stufe, Canary-Anteil, Beobachtungszeit und Stichprobe.

Relative Evidenzpfade dürfen den Manifestordner nicht verlassen. Zeitstempel benötigen eine UTC-Abweichung. Ein `status: pass` ist erforderlich, ersetzt aber weder Hash- noch Frischeprüfung.

## Sicherheitsgrenzen

Das Gate beweist nicht die fachliche Wahrheit einer Evidenzdatei. Es belegt, dass die vom Prozess verlangten, gepinnten Artefakte vorhanden, unverändert, frisch und als bestanden markiert sind und dass die gelieferten Messwerte die vorab kodierten Schwellen erfüllen. In Produktion sollten Manifest und Ergebnis zusätzlich signiert, die Policyänderung mit Vier-Augen-Review geschützt und Evidenz aus vertrauenswürdiger CI/Telemetry erzeugt werden.

`ROLLBACK` ist ein Plan, keine ausgeführte Rücksetzung. Externe Nebenwirkungen müssen weiterhin über Receipts und das fachliche Reconciliation-Runbook behandelt werden.
