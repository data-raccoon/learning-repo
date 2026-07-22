# Beispiel: Capability-basierter Tool-Proxy

Dieses dependency-freie Python-Beispiel zeigt einen kleinen, **default-deny**
Policy Enforcement Point vor Tool-Handlern. Es demonstriert:

- kurzlebige, HMAC-signierte Capabilities mit Issuer, Subject, Audience, Ablauf
  und eindeutiger ID;
- Allowlisting von Toolnamen, kanonisch aufgelösten Pfaden und exakten
  HTTPS-Egress-Zielen (`host:port`);
- Grenzen für Aufrufe, Eingabe-/Ausgabegröße, Zeit und abstrakte Budgeteinheiten;
- Verbot, die eingehende Capability an einen Tool-Handler weiterzureichen;
- Redaction verbreiteter Secret-Formen vor Ergebnis und Audit-Persistenz;
- Audit-Events für erlaubte und abgelehnte Entscheidungen, ohne Tokenwert.

`capability_proxy.py` enthält die Referenzimplementierung,
`test_capability_proxy.py` die ausführbaren Sicherheitsbeispiele.

## Ausführen

Im Ordner `beispiel/`:

```powershell
& "$env:USERPROFILE\.venvs\all\Scripts\python.exe" -m unittest -v
```

Die Implementierung verwendet ausschließlich die Python-Standardbibliothek.

## Sicherheitsgrenze und Nicht-Garantien

Dies ist **keine OS-Sandbox** und keine produktionsfertige
Authentisierungsbibliothek. Insbesondere kann ein Python-Thread nach einem
Timeout weiterlaufen; das Zeitlimit beendet keinen feindlichen Prozess. Der
Proxy führt außerdem keinen DNS-Lookup durch, kontrolliert keine Redirects,
schützt seinen HMAC-Schlüssel nicht durch einen Key-Management-Dienst und
garantiert keine manipulationssichere Audit-Speicherung. HMAC-Capabilities sind
signiert, aber nicht verschlüsselt; Claims dürfen daher keine Secrets enthalten.

Produktiv muss der Proxy ein **nicht umgehbarer externer Prozess** sein. Nicht
vertrauenswürdiger Code gehört pro Job in eine attestierte Laufzeitgrenze wie
[gVisor](https://gvisor.dev/docs/architecture_guide/security/) oder eine mit
`jailer` betriebene
[Firecracker-microVM](https://github.com/firecracker-microvm/firecracker/blob/main/docs/design.md).
Zusätzlich erforderlich sind hostseitiger Egress-Proxy/Firewall mit erneuter
DNS- und Redirect-Prüfung, cgroups beziehungsweise VM-Ressourcenlimits,
kurzlebige Downstream-Credentials aus einem Broker sowie ein externer,
manipulationsgeschützter Audit-Sink. Ein eingehender Capability- oder
OAuth-Token wird nie als Downstream-Credential benutzt.

## Erwartete Garantie

Wenn alle Tool-Aufrufe ausschließlich durch diesen Proxy vermittelt werden,
der Signaturschlüssel geschützt ist und die Policy vollständig ist, weist er
Aufrufe außerhalb der kodierten Tool-, Pfad-, Ziel- und Budgetgrenzen ab. Er
beweist weder die fachliche Zweckmäßigkeit einer erlaubten Aktion noch schützt
er vor Sandbox-Escapes, Seitenkanälen oder Exfiltration über erlaubte Ziele.
