# Beispiel: Durable Workflow Harness

Dieses dependency-freie Python-Beispiel zeigt einen kleinen Bestell-Workflow:

```text
reservieren -> belasten -> versenden
                  | Fehler beim Versand
                  v
          erstatten -> Reservierung lösen
```

Es enthält:

- eine unveränderliche, geordnete Event History in SQLite;
- deterministisches, I/O-freies Replay;
- eine Transactional Outbox, atomar mit dem jeweiligen `ActivityScheduled`-Event;
- stabile Idempotency Keys aus Run-ID, logischer Operation und Operationsversion;
- einen simulierten Empfänger mit atomarer Inbox/Deduplizierung und Payload-Bindung;
- Crash-Injektion vor der Wirkung, nach der Wirkung vor lokalem Ack und nach lokalem Commit;
- eine Saga, die nach fehlgeschlagenem Versand Zahlung und Reservierung kompensiert.

## Ausführen

Benötigt wird Python 3.10+; Netzwerk und zusätzliche Pakete sind nicht erforderlich.

```powershell
& "$env:USERPROFILE\.venvs\all\Scripts\python.exe" demo.py
& "$env:USERPROFILE\.venvs\all\Scripts\python.exe" -m unittest -v
```

Die Befehle werden aus diesem Ordner ausgeführt. Demo-Datenbanken entstehen nur in
einem temporären Verzeichnis.

## Architektur und Commit-Grenzen

`WorkflowStore.schedule()` schreibt das `ActivityScheduled`-Event und den
Outbox-Eintrag in **einer lokalen SQLite-Transaktion**. Ein Relay (`dispatch_one`)
liefert aus der Outbox an `IdempotentReceiver`. Der Empfänger schreibt dort den
Idempotency Key und die simulierte fachliche Wirkung wiederum in **einer lokalen
Transaktion**. Activity-Ergebnis und Outbox-Acknowledgement werden anschließend
gemeinsam im Workflow-Store committed.

Zwischen Workflow- und Empfänger-Datenbank existiert keine verteilte Transaktion.
Stürzt der Prozess nach der Empfängerwirkung, aber vor dem Ack ab, bleibt der
Outbox-Eintrag offen und wird erneut geliefert. Der Empfänger erkennt denselben
Key, prüft denselben Payload-Hash und liefert das gespeicherte Ergebnis zurück.

Die History ist append-only: SQLite-Trigger verweigern `UPDATE` und `DELETE`.
`replay()` reduziert ausschließlich gespeicherte Events. Zeit, Zufall, Netzwerk
und Empfängerzugriffe liegen nicht im Replay-Pfad.

## Präzise Garantiegrenze

Dieses Beispiel behauptet **kein allgemeines Exactly-once**. Es zeigt höchstens
eine fachliche Anwendung pro Idempotency Key nur unter diesen Annahmen:

- alle Wirkungen gehen durch den einzigen `IdempotentReceiver`;
- Inbox-Eintrag und fachliche Änderung teilen dieselbe intakte ACID-Transaktion;
- der Key bleibt erhalten und bezeichnet immer denselben Payload;
- SQLite-Dateien sind dauerhaft und verfügbar;
- es gibt keinen administrativen oder programmatischen Bypass.

Die Zustellung selbst ist at-least-once. Eine reale HTTP-API ohne atomare
Empfänger-Deduplizierung könnte nach einem Timeout mehrfach wirken. Auch eine
Kompensation ist eine neue fachliche Wirkung, kein Zurückdrehen der Zeit; sie kann
in realen Systemen scheitern und benötigt dann Retry oder manuelle Eskalation.

## Tests

Die Tests prüfen die drei relevanten Crash-Grenzen, deterministisches Replay,
doppelte Zustellung, Payload-Konflikte, unveränderliche History und die komplette
Kompensationsfolge. Für Produktion fehlen bewusst unter anderem Leasing mehrerer
Worker, Backoff/Timeouts, Schema- und Workflow-Versionierung, Verschlüsselung,
Retention, Backups, Telemetrie und eine Dead-Letter-/Operator-Eskalation.
