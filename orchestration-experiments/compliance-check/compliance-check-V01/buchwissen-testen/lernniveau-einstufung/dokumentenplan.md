# Dokumentenplan – Buchwissen testen

**Assessment-ID:** ASSESSMENT-2026-002  
**Systemversion:** Planungsstand; kontrollierte Version noch festzulegen  
**Dokumentversion:** 0.1  
**Status:** draft  
**Owner:** Anbieter / Compliance  
**Reviewer:** offen  
**Datum:** 13. Juli 2026

## Routingentscheidung

| Paket | Zustand | Begründung |
|---|---|---|
| `base` | geöffnet | Für jeden bewerteten Use Case zwingend. |
| `transparency` | geöffnet | Direkte Interaktion mit Schülern und Erzeugung synthetischer Textinhalte; Art. 50 Abs. 1 und 2. |
| `exception_6_3` | nicht geöffnet | Keine Ausnahme nach Art. 6 Abs. 3 wird beansprucht; das System bleibt Hochrisiko-KI. |
| `high_risk_provider` | geöffnet | Anbieterrolle und Hochrisikopfad nach Anhang III Nr. 3 Buchst. b. |
| `high_risk_deployer` | geöffnet | Schulen und Bildungsträger nutzen das System in eigener Verantwortung. |
| `conformity` | geöffnet | Anbieter eines Hochrisiko-KI-Systems. |
| `lifecycle` | geöffnet | Anbieter eines Hochrisiko-KI-Systems. |
| `economic_actor` | bedingt offen | Anbieterrechtsträger, Sitz und Vertriebskette fehlen; Bevollmächtigter, Einführer und Händler können noch nicht abschließend geroutet werden. |
| `product_gate` | nicht geöffnet | Stand-alone-Bildungssoftware ohne Anhang-I-Produkt- oder Sicherheitsfunktion nach der abgeschlossenen Einstufung. |

## Instanziierte Anforderungen und Dokumente

| Anforderungs-ID | Dokument-ID | Dokument | Status |
|---|---|---|---|
| BAS-SYSTEM | DOC-SYSTEM | [System- und Zweckbestimmung](dossier/system-und-zweckbestimmung.md) | drafted |
| BAS-SCOPE | DOC-SCOPE | [KI-System und Anwendungsbereich](dossier/ki-system-und-anwendungsbereich.md) | drafted |
| BAS-ROLE | DOC-ROLE | [Rollen- und Akteursmatrix](dossier/rollen-und-akteure.md) | drafted |
| BAS-PROHIBITED | DOC-PROHIBITED | [Prüfung verbotener Praktiken](dossier/art-5-pruefung.md) | drafted |
| BAS-RISK | DOC-CLASSIFICATION | [Risikoeinstufungsvermerk](dossier/risikoeinstufung.md) | drafted |
| BAS-LITERACY | DOC-LITERACY | [KI-Kompetenzkonzept](dossier/ki-kompetenz.md) | drafted |
| TRN-INTERACTION, TRN-SYNTHETIC | DOC-TRANSPARENCY | [Transparenzkonzept](dossier/transparenzkonzept.md) | drafted |
| HRP-RISK | DOC-RISK | [Risikomanagementakte](dossier/risikomanagement.md) | drafted |
| HRP-DATA | DOC-DATA | [Daten-Governance-Akte](dossier/daten-governance.md) | drafted |
| HRP-TECH | DOC-TECH | [Technische Dokumentation](dossier/technische-dokumentation.md) | drafted |
| HRP-LOG | DOC-LOG | [Logging-Konzept](dossier/logging-und-protokolle.md) | drafted |
| HRP-IFU | DOC-IFU | [Betriebsanleitung](dossier/betriebsanleitung.md) | drafted |
| HRP-OVERSIGHT | DOC-OVERSIGHT | [Menschliche Aufsicht](dossier/menschliche-aufsicht.md) | drafted |
| HRP-PERFORMANCE | DOC-PERFORMANCE | [Leistung, Robustheit und Cybersicherheit](dossier/leistung-robustheit-cybersicherheit.md) | drafted |
| HRP-QMS | DOC-QMS | [Qualitätsmanagementsystem](dossier/qualitaetsmanagement.md) | drafted |
| HRP-RETENTION | DOC-RETENTION | [Aufbewahrungskonzept](dossier/aufbewahrung.md) | drafted |
| CNF-PATH | DOC-CNF-PATH | [Konformitätsstrategie](dossier/konformitaetsstrategie.md) | drafted |
| CNF-ASSESSMENT | DOC-CNF-REPORT | Konformitätsbewertungsbericht | requested; darf nicht erfunden werden |
| CNF-DECLARATION | DOC-DECLARATION | [Entwurf EU-Konformitätserklärung](dossier/eu-konformitaetserklaerung-entwurf.md) | drafted; nicht unterschrieben |
| CNF-CE | DOC-CE | CE-Kennzeichnungsnachweis | requested |
| CNF-REGISTER | DOC-REGISTER | EU-Datenbankauszug | requested |
| LIF-CAPA | DOC-CAPA | [CAPA- und Behördenprozess](dossier/capa-und-behoerden.md) | drafted |
| LIF-PMS | DOC-PMS | [Post-Market-Monitoring-Plan](dossier/post-market-monitoring.md) | drafted |
| LIF-INCIDENT | DOC-INCIDENT | [Prozess für schwerwiegende Vorfälle](dossier/schwerwiegende-vorfaelle.md) | drafted |
| LIF-CHANGE | DOC-CHANGE | [Änderungs- und Neubewertungsprozess](dossier/aenderungsmanagement.md) | drafted |
| DEP-OPERATIONS | DOC-DEP-OPS | [Betreiber-Betriebskonzept](dossier/betreiber-betriebskonzept.md) | drafted |
| DEP-OVERSIGHT | DOC-DEP-OVERSIGHT | [Betreiber-Aufsicht](dossier/betreiber-aufsicht.md) | drafted |
| DEP-NOTICES | DOC-DEP-NOTICES | [Schüler- und Elterninformation](dossier/betroffeneninformation.md) | drafted |
| DEP-REPORTING | DOC-DEP-REPORTING | [Betreiber-Meldeprozess](dossier/betreiber-meldeprozess.md) | drafted |
| DEP-FRIA | DOC-FRIA | [FRIA-Arbeitsvorlage](dossier/grundrechte-folgenabschaetzung.md) | drafted; betreiberspezifisch zu entscheiden |
| DEP-EXPLANATION | DOC-EXPLANATION | [Erläuterungs- und Beschwerdeverfahren](dossier/erlaeuterungsrecht.md) | drafted |
| ACT-AR | DOC-ACTOR-ROUTING | [Wirtschaftsakteur-Routing](dossier/wirtschaftsakteure.md) | requested bis Sitz bekannt |
| ACT-IMPORTER | DOC-ACTOR-ROUTING | [Wirtschaftsakteur-Routing](dossier/wirtschaftsakteure.md) | requested bis Vertriebskette bekannt |
| ACT-DISTRIBUTOR | DOC-ACTOR-ROUTING | [Wirtschaftsakteur-Routing](dossier/wirtschaftsakteure.md) | requested bis Vertriebskette bekannt |

## Begründet nicht geöffnete Anforderungen

| ID | Status | Begründung |
|---|---|---|
| EXC-6-3, EXC-REGISTER | not_applicable | Keine Ausnahme nach Art. 6 Abs. 3; daher keine Ausnahmebewertung oder Registrierung nach Art. 49 Abs. 2. |
| TRN-DEEPFAKE | not_applicable | Keine Bild-, Ton- oder Videoinhalte und keine Deepfakes. |
| TRN-TEXT | not_applicable | Keine Veröffentlichung von Text zur Information der Öffentlichkeit über Angelegenheiten von öffentlichem Interesse. |
| EXT-PRODUCT, EXT-SECTOR-CNF | not_applicable | Stand-alone-Bildungssoftware; Art. 6 Abs. 1 wurde verneint. |

## Zweitabgleich gegen die Routingmatrix

Der Abgleich wurde am 13. Juli 2026 wiederholt. Alle für `annex_iii_high_risk` mit Anbieter- und Betreiberrolle vorgesehenen Pakete sind instanziiert. Die bedingten Wirtschaftsakteurrollen bleiben als Tatsachenanforderung offen; externe Zertifikate, Registereinträge und Freigaben werden nur angefordert.

## Änderungsverlauf

| Version | Datum | Änderung | Autor |
|---|---|---|---|
| 0.1 | 2026-07-13 | Erstentwurf aus abgeschlossener Einstufung | KI-gestützter Entwurf |

