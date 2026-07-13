# Dokumentenplan – Automatisches Toiletten-Tagebuch

**Assessment-ID:** ASSESSMENT-2026-001  
**Systemversion:** nicht angegeben  
**Dokumentversion / Status:** 0.2 / draft  
**Owner / Reviewer / Datum:** Compliance / offen / 2026-07-13

## Routingentscheidung

| Paket | Zustand | Begründung |
|---|---|---|
| `base` | geöffnet | Für jeden bewerteten Use Case zwingend. |
| `transparency` | teilweise geöffnet | Direkte KI-Interaktion beziehungsweise deren konkrete UI-Umsetzung ist zu belegen; keine synthetischen Inhalte, Deepfakes oder Veröffentlichung von Text im öffentlichen Interesse vorgesehen. |
| `exception_6_3` | nicht geöffnet | Kein Anhang-III-Tatbestand und keine Ausnahme nach Art. 6 Abs. 3 beansprucht. |
| `product_gate` | geöffnet | Medizinprodukt- oder sonstiger Anhang-I-Produktstatus und Drittstellenpflicht sind offen. |
| `high_risk_provider` | noch nicht geöffnet | Nur zu öffnen, wenn EXT-PRODUCT beide Bedingungen des Art. 6 Abs. 1 bestätigt. |
| `high_risk_deployer` | nicht geöffnet | Bewohner nutzen die App persönlich/nicht beruflich; der Hausarzt erhält nur einen Export. |
| `conformity` | noch nicht geöffnet | Abhängig von bestätigtem Hochrisikopfad; der sektorale Produktweg bleibt unter EXT-SECTOR-CNF angefordert. |
| `lifecycle` | noch nicht geöffnet | Pflichtpaket erst bei bestätigter Anbieterrolle für Hochrisiko-KI. |
| `economic_actor` | bedingt offen | Rechtsträger, Sitz und App-Store-/Vertriebskette fehlen; Bevollmächtigten-, Einführer- und Händlerrolle sind zu klären. |

## Instanziierte Anforderungen

| Anforderungs-ID | Dokument-ID | Dokument / Nachweis | Status |
|---|---|---|---|
| BAS-SYSTEM | DOC-SYSTEM | [System- und Zweckbestimmung](dossier/system-und-zweckbestimmung.md) | drafted |
| BAS-SCOPE | DOC-SCOPE | [Anwendungsbereich und KI-System](dossier/anwendungsbereich-und-ki-system.md) | drafted |
| BAS-ROLE | DOC-ROLE | [Rollen- und Akteursmatrix](dossier/rollen-und-akteure.md) | drafted |
| BAS-PROHIBITED | DOC-PROHIBITED | [Prüfung verbotener Praktiken](dossier/art-5-pruefung.md) | drafted |
| BAS-RISK | DOC-RISK | [Risikoeinstufung](dossier/risikoeinstufung.md) | drafted |
| BAS-LITERACY | DOC-LITERACY | [KI-Kompetenzkonzept](dossier/ki-kompetenz.md) | drafted |
| TRN-INTERACTION | DOC-TRANSPARENCY | [Transparenzkonzept](dossier/transparenzkonzept.md) | drafted |
| EXT-PRODUCT | DOC-PRODUCT-GATE | [Produktpfad und externe Entscheidung](dossier/produktpfad.md) | requested |
| EXT-SECTOR-CNF | DOC-PRODUCT-GATE | sektoraler Konformitätsweg abhängig von EXT-PRODUCT | requested |
| ACT-AR, ACT-IMPORTER, ACT-DISTRIBUTOR | DOC-ACTOR-ROUTING | [Wirtschaftsakteur-Routing](dossier/wirtschaftsakteure.md) | requested bis Rechtsträger/Sitz/Vertrieb feststehen |

## Begründet nicht geöffnete Anforderungen

| ID / Paket | Zustand | Begründung |
|---|---|---|
| TRN-SYNTHETIC | not_applicable | Das System klassifiziert Geräusche; es erzeugt keine synthetischen Audio-, Bild-, Video- oder Textinhalte. |
| TRN-DEEPFAKE | not_applicable | Keine generierten/manipulierten Bild-, Ton- oder Videoinhalte. |
| TRN-TEXT | not_applicable | Keine Veröffentlichung von KI-Text zu Angelegenheiten öffentlichen Interesses. |
| EXC-6-3, EXC-REGISTER | not_applicable | Kein Anhang-III-Tatbestand, daher keine Ausnahme und keine Ausnahme-Registrierung. |
| DEP-* | nicht geöffnet | Keine Betreiberrolle im beruflichen Kontext nach dem bekannten Use Case. |
| HRP-* | abhängig | Erst nach positiver Produktklassifizierung mit Drittstellenpflicht öffnen. |
| CNF-* | abhängig | Erst nach bestätigter Hochrisikoeinstufung öffnen; EXT-SECTOR-CNF bleibt separat angefordert. |
| LIF-* | abhängig | Erst nach bestätigter Hochrisiko-Anbieterrolle öffnen. |

## Priorisierte Evidenzanforderungen

1. EVD-PRODUCT-001: externe Produkt-/Medizinprodukteklassifizierung mit Aussage zur Drittstellenpflicht.
2. EVD-SYSTEM-001: freigegebene Zweckbestimmung, Store-/Werbetexte und Gebrauchsanweisung.
3. EVD-TECH-001: Modell-, Architektur-, Datenfluss-, Lokalverarbeitungs- und Löschungsnachweis.
4. EVD-ROLE-001: Rechtsträger, Sitz, Vertriebsgebiete und App-Store-/Wirtschaftsakteurkette.
5. EVD-ART5-001: Funktionsspezifikation und Tests zur Nichtauswertung von Sprache, Stimme, Identität und Emotion.
6. EVD-TRN-001: UI-Flows mit KI-Hinweis, Korrektur und Löschung.
7. EVD-LITERACY-001: Rollenprofile, Schulungsplan und Umsetzungsnachweise.

## Zweitabgleich

Am 13. Juli 2026 erneut gegen alle 41 Matrix-IDs geprüft. Die Hochrisikopakete bleiben bewusst uninstanziiert, bis die externe Produktentscheidung Risikopfad und sektoralen Konformitätsweg bestimmt. Der Gesamtzustand bleibt `evidence_pending`.

## Änderungsverlauf

| Version | Datum | Änderung | Autor |
|---|---|---|---|
| 0.1 | 2026-07-13 | Erster Dokumentenplan | KI-gestützter Entwurf |
| 0.2 | 2026-07-13 | Vollständiges Paketrouting und stabile Nachweis-IDs ergänzt | KI-gestützter Entwurf |

