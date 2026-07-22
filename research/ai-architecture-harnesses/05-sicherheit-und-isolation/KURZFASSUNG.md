# Sicherheit und Isolation – Kurzfassung

## Kernaussage

Ein Agent ist keine Sicherheitsgrenze. Modelltexte, Retrieval, Tools und Agentennachrichten sind potenziell feindliche Daten. Schutz entsteht außerhalb des Modells durch authentisierte Identitäten, enge Capabilities, einen nicht umgehbaren Autorisierungspfad, kurzlebige Secrets, deny-by-default Netzwerkzugang, Dateisystem- und Ressourcenlimits sowie isolierte Ausführung. Prompt Injection lässt sich nicht zuverlässig wegprompten; die Architektur muss ihren möglichen Schaden begrenzen.

## Garantiert

Ein korrekt implementierter, vollständig vermittelnder Policy-Enforcer kann Operationen außerhalb einer erteilten Capability blockieren. OAuth kann unter sicheren Issuer- und Schlüsselannahmen falsche, abgelaufene oder für eine andere Ressource ausgestellte Tokens ablehnen. Netzwerk- und Dateisystem-Allowlisten können Zugriffe außerhalb kodierter Grenzen verhindern, wenn alle Pfade erfasst und kanonisch geprüft werden. Harte CPU-, RAM-, Prozess- und Zeitlimits begrenzen den isolierten Job. gVisor reduziert die direkte Host-Systemcall-Fläche; Firecracker schafft eine zusätzliche microVM-/KVM-Grenze. Beides ist Risikoreduktion unter Implementierungs- und Betriebsannahmen.

## Garantiert nicht

Least Privilege verhindert keinen Missbrauch erlaubter Rechte. OAuth beweist nicht, dass eine Aktion fachlich legitim ist. gVisor und Firecracker verhindern weder Prompt Injection noch Exfiltration über erlaubte Kanäle, Seitenkanäle oder Fehlkonfigurationen. Container oder microVM schützen nicht bei gefährlichen Host-Mounts, breit verfügbaren Credentials oder offenem Egress. Ein Injection-Detektor bleibt heuristisch und kann unbekannte Angriffe übersehen.

## Einsatzkriterien

Für vertrauenswürdigen internen Code mit kleinem Schadenpotenzial können Prozess- oder Containergrenzen plus enge Capabilities genügen. Bei fremdem Code, Multi-Tenancy, sensiblen Secrets oder wertvollen Hostdaten sind gVisor oder microVMs zu bevorzugen. Firecracker bietet eine deutlichere Gast-/Host-Grenze, benötigt aber KVM, Images und mehr Plattformbetrieb; gVisor integriert sich meist leichter in Containerumgebungen, verlangt jedoch Kompatibilitätstests. Unabhängig davon sind separate Identitäten, kurzlebige Credentials, read-only Inputs, deny-by-default Egress, harte Budgets und ein externer Commit-Adapter erforderlich.

## Quellen

- [OWASP: Agentic AI Threats and Mitigations](https://genai.owasp.org/resource/agentic-ai-threats-and-mitigations/)
- [NIST: Least Privilege](https://csrc.nist.gov/glossary/term/least_privilege)
- [MCP Authorization Specification](https://modelcontextprotocol.io/specification/2025-06-18/basic/authorization)
- [MCP Security Best Practices](https://modelcontextprotocol.io/docs/tutorials/security/security_best_practices)
- [gVisor Security Model](https://gvisor.dev/docs/architecture_guide/security/)
- [Firecracker Design](https://github.com/firecracker-microvm/firecracker/blob/main/docs/design.md)
