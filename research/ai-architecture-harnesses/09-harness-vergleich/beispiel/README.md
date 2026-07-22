# Beispiel: neutraler Harness-Vertrag und Conformance-Suite

Dieses vollständig dependency-freie Python-Beispiel macht den Ansatz aus dem Harness-Vergleich ausführbar. Es wählt kein Produkt über eine pauschale Rangliste aus, sondern lässt ausschließlich Adapter zu, die alle deklarativen Muss-Kriterien erfüllen.

## Inhalt

- `harness_contract.py`: ABC für `run`, `resume`, `cancel` und `trace`, Werttypen, Capability-Matrix und Auswahlfunktion.
- `fake_adapters.py`: zwei deterministische Testadapter. `SnapshotHarness` verwendet kurzlebige Single-use-Snapshot-Tokens und unterstützt Cancel. `EventReplayHarness` verwendet einen an die Event-Historie gebundenen Cursor und bietet bewusst kein Cancel.
- `conformance.py`: wiederverwendbare Prüfung der angekündigten Kernfähigkeiten.
- `test_harness.py`: Negativ- und Invariantentests.
- `demo.py`: Capability-Auswahl, Lauf, Resume, Trace und Conformance in einem Durchlauf.

Die Resume-Tokens sind opaque, an Adapter und Run gebunden und dürfen nicht zwischen Implementierungen übersetzt werden. Eine Capability ist nur dann in `AdapterDescriptor.capabilities` anzugeben, wenn der Adapter den zugehörigen Vertrag tatsächlich erfüllt. Nicht unterstützte Operationen scheitern explizit; ein Aufrufer sollte sie durch die Anforderungsauswahl gar nicht erst erreichen.

## Ausführen

Im Ordner `beispiel/`:

```powershell
& "$env:USERPROFILE\.venvs\all\Scripts\python.exe" demo.py
& "$env:USERPROFILE\.venvs\all\Scripts\python.exe" -m unittest -v
```

Die Tests decken ab:

- Ausschluss bei fehlender Muss-Capability;
- Ablehnung adapterfremder, veralteter oder historisch falscher Resume-Tokens;
- terminales Cancel und ungültig gewordenes Resume;
- durchgängige Korrelation und monotone Sequenzen im Trace;
- keine versteckte oder pauschale Rangfolge unter geeigneten Adaptern;
- denselben Conformance-Kern für beide Resume-Semantiken.

## Garantien und Grenzen

Die Auswahl garantiert rein mechanisch `requirements.required ⊆ adapter.capabilities`. Die Suite prüft das Verhalten der Fakes und kann als Ausgangspunkt für echte Adapter dienen. Sie beweist nicht die Herstellerimplementierung, Verfügbarkeit eines externen Stores, Exactly-once-Nebenwirkungen oder fachliche Richtigkeit. Ein Produktionsadapter benötigt zusätzlich Crash-, Upgrade-, Persistenz-, Idempotenz- und Integrationstests gegen die exakt eingesetzte Version.
