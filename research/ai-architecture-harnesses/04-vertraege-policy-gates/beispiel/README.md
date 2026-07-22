# Beispiel: Verträge und fail-closed Policy-Gates

Dieses ausführbare Minimalbeispiel zeigt einen Kontrollpfad ohne externe
Abhängigkeiten:

`untrusted JSON → Strukturvertrag → Semantik → Approval-Hash → PDP/PEP → Gate`

`harness.py` enthält unveränderliche `dataclass`-Nachrichten und `Enum`-Werte,
eine strikte JSON-Grenze, serverseitige Invarianten, einen fail-closed PEP sowie
Admission- und Release-Gates. `demo.py` führt einen erlaubten Transfer bis zur
Admission aus. Ein realer Side-Effect-Adapter würde ausschließlich das Ergebnis
des Gates entgegennehmen und selbst keine alternative, ungeprüfte Route anbieten.

## Ausführen

Im Verzeichnis `beispiel/`:

```powershell
& "$env:USERPROFILE\.venvs\all\Scripts\python.exe" demo.py
& "$env:USERPROFILE\.venvs\all\Scripts\python.exe" -m unittest -v
```

Die Tests decken kaputtes JSON, unbekannte und doppelte Felder, zu lockere
Python-Typen, Policy-Ausfall/`undefined`, manipulierte Approval-Payloads,
semantische Ablehnung und ein blockierendes Release-Gate ab.

## Sicherheitsmodell und Grenzen

- Identität, Budget und Allowlist stammen aus `TrustedContext`, also aus
  serverseitigem Zustand und nicht aus Modelltext.
- Eine Freigabe bindet den kanonisierten, normalisierten Payload per SHA-256.
  Das Beispiel authentifiziert die freigebende Person jedoch nicht
  kryptografisch. Produktiv braucht es eine authentisierte Approval-Quelle,
  Ablaufzeit, Nonce/Replay-Schutz und ein manipulationsgeschütztes Audit-Log.
- Der PEP behandelt Exception, `None`, untypisierte Antwort, `deny` und fehlende
  Policy-Revision als Ablehnung. Technisch wirksam ist das nur, wenn alle
  Credentials und Side Effects ausschließlich hinter diesem PEP liegen.
- Die lokale Strukturprüfung ist bewusst **kein vollständiger JSON-Schema-
  Validator**. Sie implementiert genau diesen Vertrag; `$ref`, Draft-Semantik,
  Format-Vokabulare, beliebig verschachtelte Schemata und Schema-Evolution sind
  nicht enthalten. Produktiv sollte ein fest versionierter, gepflegter Validator
  eingesetzt und weiterhin lokal am Consumer validiert werden.
- SHA-256 bindet Bytes bzw. die definierte Kanonisierung, beweist aber weder die
  Richtigkeit des Inhalts noch Zustimmung ohne authentisierte Approval-Daten.
- Autoritativer Zustand kann sich zwischen Prüfung und Wirkung ändern (TOCTOU).
  Produktiv müssen Prüfung und Commit atomar sein oder im Adapter unmittelbar
  vor dem Commit erneut geprüft werden.
- `ReleaseCandidate` repräsentiert bereits verifizierte Prüfergebnisse. Die
  eigentlichen Signatur-, Provenienz- und Testverifizierer liegen außerhalb
  dieses dependency-freien Beispiels.
