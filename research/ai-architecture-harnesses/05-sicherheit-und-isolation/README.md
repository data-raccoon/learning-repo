# Sicherheit, Berechtigungen und Isolation

[Kurzfassung](KURZFASSUNG.md) · [Beispielimplementierung](beispiel/README.md) · [Gesamtübersicht](../README.md)

Stand und Abruf der verlinkten Quellen: 2026-07-22.

## Kurzfassung

Ein Agent ist keine Sicherheitsgrenze. Modelltexte, Tool-Beschreibungen, Retrieval-Inhalte und Nachrichten anderer Agenten sind potenziell feindliche Daten. Schutz entsteht durch Code außerhalb des Modells: authentisierte Identitäten, enge Capabilities (explizit vergebene Fähigkeiten), nicht umgehbare Autorisierung, kurzlebige Secrets, Egress- und Dateisystemregeln, Ressourcenlimits, isolierte Ausführung und überprüfbare Freigaben.

**Least Privilege** begrenzt den möglichen Schaden, verhindert aber nicht den Missbrauch der verbleibenden Rechte. MCP-OAuth authentisiert und bindet Tokens an Ressourcen, macht jedoch eine vom Modell gewählte Aktion nicht automatisch legitim. gVisor und Firecracker verkleinern unterschiedliche Host-Angriffsflächen, beseitigen aber weder Prompt Injection noch Datenabfluss über erlaubte Kanäle, Seitenkanäle oder Fehlkonfigurationen. Der robuste Default lautet deshalb: kein Credential im Modellkontext, keine direkte Nebenwirkung aus Modelloutput, deny-by-default Egress und ein eigener, kurzlebiger Ausführungskontext pro Vertrauensdomäne.

## Anwendungsbereich und Threat Model

Dieses Kapitel betrachtet ein Harness, das fremde Inhalte verarbeitet, Code oder Tools ausführen und externe Systeme verändern kann. Zu schützende Güter sind Identitäten, Tokens und Schlüssel, Nutzerdaten, Quellcode, Modell-/Prompt-Artefakte, Workflow-Zustand, Audit-Logs, Rechenbudget sowie externe Konten und Dienste.

Angreifer oder Fehlerquellen können sein:

- direkte und indirekte Prompt Injection in Nutzertext, Webseiten, Dokumenten oder Tool-Ergebnissen;
- kompromittierte Tools, MCP-Server, Abhängigkeiten, Images oder Modellendpunkte;
- bösartige oder fehlgeleitete Subagenten;
- gestohlene Tokens, confused-deputy-Situationen und zu breite Scopes;
- Parser-, Kernel-, Hypervisor- oder Sandbox-Schwachstellen;
- Denial of Service durch Endlosschleifen, Fork-/Speicherlast oder Kostenexplosion;
- Insider, Fehlkonfiguration und unvollständige Policies.

OWASP ordnet unter anderem Tool Misuse, Privilege Compromise sowie Goal-, Memory- und Inter-Agent-Risiken als agentische Bedrohungen ein; die Sammlung ist ein Threat-Model-Leitfaden, keine Zertifizierung einer Implementierung ([OWASP, Agentic AI – Threats and Mitigations](https://genai.owasp.org/resource/agentic-ai-threats-and-mitigations/)).

## 1. Capabilities und Least Privilege

NIST definiert Least Privilege als Beschränkung einer Entität auf genau die Ressourcen und Autorisierungen, die sie für ihre Funktion benötigt ([NIST CSRC, Least Privilege](https://csrc.nist.gov/glossary/term/least_privilege)). Für Agenten reicht eine grobe Rolle wie „Researcher“ nicht. Eine Capability sollte mindestens binden:

- **Subjekt:** konkrete Nutzer-, Workflow-, Agenten- und Dienstidentität;
- **Operation:** etwa `read`, `propose`, `create-draft`, `commit`, niemals nur „Zugriff“;
- **Ressource:** Mandant, Repository, Verzeichnis, Tabelle, Kalender oder Empfänger;
- **Parametergrenzen:** Ziel-Allowlist, Betrag, Dateityp, Zeilen-/Datensatzlimit;
- **Zeit und Anzahl:** kurze Gültigkeit, einmalige Nutzung, Rate- und Kostenbudget;
- **Kontext:** Auftrag, Genehmigungs-ID, Datenklassifikation und Risikostufe.

Der Harness hält diese Capabilities serverseitig. Das Modell darf eine Aktion vorschlagen, aber weder seine Identität noch Scopes, Zielgrenzen oder Freigaben selbst behaupten. Read- und Write-Credentials werden getrennt; produktive und nichtproduktive Konten ebenso. Privilegien werden just in time erhöht und nach dem Schritt entzogen.

**Technische Garantie:** Ein korrekt implementierter, nicht umgehbarer Referenzmonitor kann Zugriffe außerhalb der erteilten Capability verweigern. Voraussetzungen sind vollständige Mediation, unverfälschbare Identität und keine alternativen Credentials oder Kanäle. **Nicht garantiert:** Eine erlaubte Aktion ist zweckmäßig. Prompt Injection kann weiterhin innerhalb eines erlaubten Lesebereichs Daten auswählen oder innerhalb eines erlaubten Schreibbereichs Schaden anrichten.

## 2. MCP-Authentisierung und -Autorisierung

Die MCP-Autorisierungsspezifikation vom 18. Juni 2025 baut für HTTP-Transporte auf OAuth auf. Sie verlangt unter anderem den Bearer Token im `Authorization`-Header statt in der URI, Tokenvalidierung durch den MCP-Server, Bindung an die beabsichtigte Audience/Ressource, PKCE und passende Fehlercodes. Ungültige oder abgelaufene Tokens sind mit 401 abzulehnen; unzureichende Scopes mit 403 ([MCP Authorization 2025-06-18](https://modelcontextprotocol.io/specification/2025-06-18/basic/authorization)).

Wesentliche Architekturregeln:

1. Der MCP-Server akzeptiert nur Tokens, die ausdrücklich für ihn ausgestellt wurden.
2. Ein eingehender Token wird niemals unverändert an eine Downstream-API weitergereicht. Für diese API nutzt der MCP-Server einen separaten OAuth-Client und einen separat ausgestellten Token.
3. Scopes werden minimal und schrittweise angefordert; Wildcard- oder „full access“-Scopes sind kein Default.
4. Nutzerzustimmung wird an konkreten Client, Redirect URI und Scope gebunden; Redirect URIs werden exakt verglichen.
5. Tokens sind kurzlebig, verschlüsselt gespeichert, nie Teil von URL, Prompt, Trace oder Tool-Ergebnis und gezielt widerrufbar.
6. Jede Tool-Ausführung autorisiert zusätzlich serverseitig Ressource und Operation; ein Scope-Claim allein ist keine ausreichende Geschäftsregel.

MCP verbietet Token-Passthrough, weil falsche Audience-Bindung Kontrollen und Auditierbarkeit unterläuft und einen confused deputy (missbrauchten Stellvertreter) ermöglicht. Die Security Best Practices verlangen für Proxy-Szenarien clientgebundene Zustimmung und beschreiben außerdem SSRF-, Session- und lokale MCP-Server-Risiken ([MCP Security Best Practices](https://modelcontextprotocol.io/docs/tutorials/security/security_best_practices)).

**Garantiegrenze:** Korrektes OAuth kann Client/Token/Ressource kryptografisch binden und abgelaufene oder unpassende Tokens abweisen. Es beweist nicht, dass der Nutzer den konkreten semantischen Effekt verstanden hat, dass der Client uncompromittiert ist oder dass der Server eine zulässige Tool-Funktion sicher implementiert. `stdio` bei lokalen Servern reduziert Netzwerkexposition, macht den gestarteten Prozess aber nicht vertrauenswürdig.

## 3. Secrets und Identitätsgrenzen

Secrets gehören in einen externen Secret Store oder in eine Workload-Identity-Lösung, nicht in Prompts, Repository, Checkpoints oder allgemeine Umgebungsdumps. Der Tool-Adapter löst ein kurzlebiges Credential erst nach Autorisierung ein. Modell und Sandbox erhalten möglichst nur eine opake Capability oder einen lokalen Broker-Endpunkt.

Pflichtkontrollen:

- getrennte Identitäten pro Tool, Mandant, Umgebung und Vertrauensstufe;
- automatische Rotation, kurze TTL und Widerruf;
- kein langlebiger Cloud-Key in Container-Image oder Workspace;
- Redaction vor Tracing, Persistenz und Fehlermeldungen;
- Schutz gegen Secret-Rückgabe durch Tools;
- Audit von Ausstellung, Nutzung, Elevation und Widerruf, jedoch ohne Tokenwert.

Secrets aus dem sichtbaren Prompt nachträglich „nicht zu verraten“ ist nur eine heuristische Aufforderung. Sobald ein Credential im Modellkontext oder in einer untrusted Sandbox liegt, muss es als potenziell kompromittiert gelten.

## 4. Netzwerk-, Dateisystem- und Ressourcenisolation

### 4.1 Netzwerk

Egress ist standardmäßig gesperrt. Erlaubnisse nennen Ziel, Protokoll, Port und gegebenenfalls Methode/Pfad. DNS-Antworten und Redirects werden erneut gegen die Policy geprüft; private, Loopback-, Link-local- und Cloud-Metadatenbereiche sind gesperrt. Ein vertrauenswürdiger Proxy kann TLS-Ziel, Rate, Datenmenge und Audit erzwingen. Firecracker selbst filtert ausgehenden Verkehr nicht und verlangt Host-seitige Filterung ([Firecracker Design, Threat Containment](https://github.com/firecracker-microvm/firecracker/blob/main/docs/design.md)).

SSRF-Schutz muss nach jeder Weiterleitung und gegen DNS-Rebinding wirken. Eine URL-Allowlist allein genügt nicht, wenn der Name später auf interne Adressen aufgelöst werden kann. Erlaubter Internetzugang bleibt ein Exfiltrationskanal; Datenklassifikation und Output-Filter müssen zusätzlich vor dem Proxy liegen.

### 4.2 Dateisystem

Jeder Job erhält einen neuen Workspace mit read-only Basisimage. Nur explizite Eingaben werden read-only eingebunden; Ausgaben gehen in ein separates, größenbegrenztes Verzeichnis. Host-Sockets, Home-Verzeichnis, SSH-/Cloud-Konfiguration, Package-Caches und Orchestrator-Control-Plane werden nicht gemountet. Pfade werden nach kanonischer Auflösung geprüft; Symlinks, Hardlinks, Mount-Wechsel und Archiv-Extraktion benötigen eigene Schutzregeln.

Persistente Ergebnisse werden erst nach Malware-/Secret-Prüfung und Policy-Freigabe aus der Sandbox übernommen. Ein Container-Layer ist kein Ersatz für Dateiberechtigungen oder einen separaten Ausführungsmandanten.

### 4.3 Ressourcen und Lebensdauer

CPU, RAM, Prozesszahl, offene Dateien, Dateisystemgröße, Netzwerkbytes, Tokens, Tool-Aufrufe, Kosten und Wall-Clock-Zeit erhalten harte Limits. Nach Timeout wird die gesamte Prozess-/VM-Gruppe beendet, nicht nur der Elternprozess. Der Zustand wird nur über definierte Artefakte übernommen. Diese Grenzen können Ressourcenverbrauch oberhalb der gesetzten Limits verhindern, sofern alle Verbrauchspfade erfasst sind; sie garantieren keine Verfügbarkeit bei Host- oder Control-Plane-Erschöpfung.

## 5. gVisor und Firecracker

### 5.1 gVisor

gVisor ist ein Userspace-Application-Kernel. Seine Sentry implementiert die unterstützte Systemaufrufoberfläche selbst; Systemaufrufe der Workload werden nicht direkt an den Host durchgereicht. Ziel ist, die Host-Kernel-Angriffsfläche gegenüber gewöhnlichen Containern zu reduzieren ([gVisor Security Model](https://gvisor.dev/docs/architecture_guide/security/)). Das ist attraktiv für kurzlebige, containerkompatible Tool-Runner mit vielen Linux-Anwendungen.

Kosten und Grenzen:

- nicht jede Linux-Funktion oder jedes `ioctl` ist kompatibel;
- Systemcall-/I/O-intensive Workloads können Overhead erfahren; Plattformen haben unterschiedliche Performance-, Kompatibilitäts- und Sicherheitsprofile ([gVisor Performance Guide](https://gvisor.dev/docs/architecture_guide/performance/));
- gVisor schützt nach eigener Dokumentation im Allgemeinen nicht vor Hardware-Seitenkanälen;
- ein verwundbarer, falsch konfigurierter oder zu weit angebundener Sandbox-Prozess bleibt riskant;
- Netzwerk, Credentials, Host-Mounts und Control Plane müssen separat abgesichert werden.

### 5.2 Firecracker

Firecracker startet pro Prozess eine schlanke KVM-microVM mit kleinem Gerätemodell. Das Design schichtet KVM-Gastgrenze, thread-spezifische seccomp-Filter, Namespaces, cgroups und Privilegienentzug. Für Produktion empfiehlt das Projekt den mitgelieferten `jailer` ([Firecracker Design](https://github.com/firecracker-microvm/firecracker/blob/main/docs/design.md)). Das passt zu stark nicht vertrauenswürdigem Code und klaren Jobgrenzen, setzt aber Linux/KVM, Gastkernel-/Image-Lifecycle und Host-Netzkonfiguration voraus.

Firecracker behandelt vCPU-Threads explizit als potenziell bösartig, erklärt aber zugleich, dass Egress nicht vom VMM gefiltert wird. Der Jailer vertraut bestimmten Pfaden; Betreiber müssen verhindern, dass unprivilegierte Nutzer diese oder ihre Elternverzeichnisse verändern ([Firecracker Production Host Setup](https://github.com/firecracker-microvm/firecracker/blob/main/docs/prod-host-setup.md)). KVM-, VMM-, Hostkernel-, Geräte- und Hardwarefehler bleiben im Threat Model.

### 5.3 Auswahl statt pauschalem Sieger

| Kriterium | gVisor | Firecracker |
|---|---|---|
| Primäre Grenze | eigener Userspace-Kernel zwischen Workload und Host | Hardwarevirtualisierte microVM über KVM |
| Operatives Modell | containernahe Sandbox | Gastkernel und Root-Dateisystem pro microVM |
| Typischer Vorteil | einfache Containerintegration, reduzierte Host-Systemcall-Fläche | starke VM-artige Mandantengrenze, kleines Gerätemodell |
| Typischer Preis | Syscall-Kompatibilität und workloadabhängiger Overhead | Image-/Kernelbetrieb, KVM-Bedarf, Boot-/Speicheraufwand |
| Nicht enthalten | vollständiger Seitenkanal-, Egress- oder Credential-Schutz | Egress-Filter, Prompt-Injection- oder Credential-Schutz |

Die Auswahl folgt dem Threat Model und wird mit realen Workloads, Escape-Tests, Patch-SLO und Benchmark validiert. Besonders kritische Systeme können Schichten kombinieren, doch zusätzliche Schichten erzeugen auch Konfigurations- und Betriebsrisiken.

## 6. Prompt Injection als Kontrollflussproblem

Direkte und indirekte Prompt Injection vermischt Daten mit Anweisungen. Ein Modell kann deren Absicht nicht verlässlich klassifizieren; Prompt-Hierarchie, Delimiter, „ignore previous instructions“-Filter und ein zweites Modell sind heuristische Abwehr, keine technische Garantie.

Die belastbare Architektur begrenzt deshalb die Wirkung eines erfolgreichen Angriffs:

- Retrieval- und Tool-Inhalte bleiben als untrusted/tainted mit Herkunft markiert;
- fremder Inhalt kann keine Capability, Systemregel oder Freigabe erzeugen;
- Planung und Ausführung sind getrennt; nur strukturierte Vorschläge verlassen den Modellschritt;
- Tool-Auswahl und Argumente durchlaufen deterministische Schema-, Mandanten- und Policy-Prüfung;
- sensible Daten werden vor dem Modell minimiert; Ausgaben vor Egress auf Datenklasse geprüft;
- Schreibaktionen zeigen dem Menschen den exakten, nachträglich unveränderlichen Commit-Inhalt;
- Agent-zu-Agent-Nachrichten werden genauso authentisiert, begrenzt und validiert wie externe Eingaben;
- Memory-Aufnahme benötigt Provenienz, Schema, Quarantäne und gegebenenfalls Freigabe.

Ein Content-Filter kann bekannte Muster blockieren und statistisch gemessen werden. Er garantiert nicht, unbekannte oder semantisch verschleierte Injection zu erkennen. Die stärkere Garantie ist: *Selbst bei vollständig kompromittierter Modellentscheidung kann sie nur innerhalb der expliziten Capability und über die erzwungenen Adapter wirken.*

## 7. Erreichbare Garantien und Voraussetzungen

| Kontrollschicht | Kategorie | Erreichbare Aussage | Zentrale Voraussetzungen |
|---|---|---|---|
| Capability-basierter PEP | deterministisch erzwingbar | nicht autorisierte Operationen über erfasste Pfade werden abgewiesen | vollständige Mediation, korrekte Policy, geschützte Identität |
| OAuth Audience/Expiry-Prüfung | unter Kryptografie-/Issuer-Annahmen | falsche, abgelaufene oder für andere Ressourcen ausgestellte Tokens werden abgewiesen | korrekte Validierung, sichere Schlüssel/Issuer, kein Bypass |
| Netzwerk-/Dateisystem-Allowlist | deterministisch erzwingbar | Zugriffe außerhalb kodierter Ziele werden an der Grenze blockiert | kanonische Auflösung, alle Pfade erfasst, unangreifbare Enforcement-Schicht |
| CPU-/RAM-/Zeitlimit | deterministisch erzwingbar | der isolierte Job überschreitet die konfigurierte Ressource nicht | korrekte Kernel-/VMM-Konfiguration und Abrechnung |
| gVisor | Risikoreduktion unter Implementierungsannahmen | Workload hat nicht direkt die normale Host-Systemcall-Fläche | aktueller, korrekt konfigurierter Runtime; keine gefährlichen Mounts/Rechte |
| Firecracker | Risikoreduktion unter Hardware-/VMM-Annahmen | Gast ist durch microVM-/KVM- und Jailer-Schichten vom Host getrennt | gehärteter Host, Jailer, Images, Egress und Patchstand korrekt |
| Prompt-/Injection-Detektor | statistisch messbar/heuristisch | bekannte Testangriffe werden mit gemessener Rate erkannt | repräsentatives Eval; laufende Aktualisierung |

Keine dieser Einzelkontrollen garantiert End-to-End-Sicherheit. Die Garantie gilt jeweils nur für die benannte Eigenschaft innerhalb ihrer Failure Domain.

## 8. Nicht-Garantien und Failure Modes

- Das Modell erhält einen Broad-Scope-Token und exfiltriert ihn über ein erlaubtes Tool.
- Ein autorisierter MCP-Server reicht einen Token mit falscher Audience weiter.
- Der PEP prüft Toolnamen, aber nicht normalisierte Parameter oder Mandantenzugehörigkeit.
- Ein Redirect, DNS-Rebinding oder Proxy-Bypass erreicht interne Dienste.
- Ein beschreibbarer Host-Mount, Docker-Socket oder Kube-Credential hebt die Sandbox praktisch auf.
- Ein gemeinsamer Workspace oder Memory-Store ermöglicht Datenfluss zwischen Mandanten/Jobs.
- Logs, Crash Dumps oder Traces speichern Secrets trotz sicherem Primärpfad.
- gVisor-Inkompatibilität führt zum stillen Fallback auf einen schwächeren Runtime-Modus.
- Firecracker läuft ohne Jailer oder mit manipulierbaren Jailer-Pfaden.
- Ein erlaubter Kanal transportiert schädliche Daten; Isolation kontrolliert Zugriff, nicht Bedeutung.
- Menschliche Freigabe wird durch unvollständige, veraltete oder irreführende Darstellung entwertet.

## 9. Entscheidungskriterien

Für vertrauenswürdigen internen Code mit geringem Schadenpotenzial können Prozess-/Containergrenzen plus enge Capabilities genügen. Bei fremdem Code, Multi-Tenancy, sensiblen Secrets oder wertvollen Hostdaten ist eine stärkere Sandbox wie gVisor oder eine microVM zu bevorzugen. Firecracker bietet eine klarere Gast-/Host-Grenze, verlangt aber mehr Plattformbetrieb; gVisor passt oft leichter in Container-Orchestrierung, verlangt Kompatibilitätstests.

Unabhängig vom Runtime-Typ sind separate Identität, deny-by-default Egress, read-only Inputs, harte Budgets und ein externer Commit-Adapter Pflicht. Für irreversible oder regulatorisch relevante Aktionen kommt eine transaktionsgebundene menschliche Freigabe hinzu.

## 10. Umsetzbare Checkliste

- [ ] Threat Model benennt Assets, Trust Boundaries, Angreifer, Side Effects und akzeptiertes Restrisiko.
- [ ] Modell, Agenten und Sandboxes besitzen keine langlebigen oder breit gültigen Credentials.
- [ ] Jede Capability bindet Subjekt, Operation, Ressource, Parametergrenzen, Zweck, TTL und Budget.
- [ ] Jeder Zugriff läuft über einen nicht umgehbaren, fail-closed PEP; direkte SDK-/Shell-/Netzwerkpfade sind entfernt.
- [ ] MCP prüft Issuer, Signatur, Audience, Ablauf und Scope; Token-Passthrough ist ausgeschlossen.
- [ ] Downstream-APIs erhalten separat ausgestellte Tokens; Scope-Elevation ist explizit und auditierbar.
- [ ] Secrets werden vor Prompt, Checkpoint, Trace, Log und Tool-Ergebnis redigiert.
- [ ] Egress ist deny-by-default; DNS, Redirects, private Netze, Metadatenendpunkte und Datenvolumen sind kontrolliert.
- [ ] Workspace ist pro Job/Mandant neu; Root-Dateisystem und Inputs sind read-only; Host-Sockets und Home fehlen.
- [ ] CPU, RAM, Prozesse, Dateien, Netzwerk, Zeit, Tokens, Aufrufe und Kosten haben harte Limits.
- [ ] gVisor-/Firecracker-Modus wird attestiert; ein Fallback auf schwächere Isolation blockiert den Job.
- [ ] Firecracker nutzt in Produktion Jailer plus Host-Egress-Filter; gVisor-Kompatibilität wird pro Workload getestet.
- [ ] Runtime, Hostkernel, Gastkernel/Images und Policies folgen einem Patch-SLO mit Escape-Regressionstests.
- [ ] Tool-, Retrieval-, Memory- und Agentennachrichten bleiben tainted; nur Policy/Code darf Autorität erzeugen.
- [ ] Hochriskante Commits binden eine Freigabe kryptografisch oder transaktional an exakt gezeigte Parameter.
- [ ] Audit-Logs sind manipulationsgeschützt, korreliert, datensparsam und auf Wiederherstellung getestet.
