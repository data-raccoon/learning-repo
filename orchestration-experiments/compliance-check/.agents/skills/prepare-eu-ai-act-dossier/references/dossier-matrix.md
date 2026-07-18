# Risikobasierte EU-AI-Act-Dokumentenmatrix

## Routing

- `base`: immer für einen bewerteten Use Case.
- `transparency`: wenn Art. 50 einschlägig oder seine Anwendbarkeit nur über die konkrete Implementierung belegbar ist.
- `exception_6_3`: nur bei einem Anhang-III-Tatbestand, für den die Ausnahme beansprucht wird.
- `high_risk_provider`: bei Anbieterrolle für Hochrisiko-KI; bei Fremdanbieter als anzuforderndes Anbieterdossier.
- `high_risk_deployer`: bei Betreiberrolle für Hochrisiko-KI.
- `conformity`: bei Anbieterrolle für Hochrisiko-KI.
- `lifecycle`: bei Anbieterrolle für Hochrisiko-KI; betreiberbezogene Meldewege zusätzlich unter `high_risk_deployer`.
- `economic_actor`: abhängig von Bevollmächtigten-, Einführer- oder Händlerrolle.
- `product_gate`: sobald Art. 6 Abs. 1 möglich ist.

## Basispaket

| ID | Pflichtdokument | Mindestnachweis | Rechtsgrund |
|---|---|---|---|
| BAS-SYSTEM | System- und Zweckbestimmung einschließlich Version, Grenze, Ein-/Ausgaben, Nutzer, Betroffene und Aktionen | freigegebene Produktbeschreibung, Architektur- oder Systemunterlagen | Art. 3 |
| BAS-SCOPE | Vermerk zu KI-System und Anwendungsbereich | technische Modellbeschreibung und Vertriebs-/Einsatzgebiete | Art. 2–3 |
| BAS-ROLE | Rollen- und Akteursmatrix | Verträge, Marken-/Vertriebsmodell, Änderungsverantwortung | Art. 3, 22–25 |
| BAS-PROHIBITED | dokumentierte Prüfung sämtlicher Art.-5-Tatbestände | Funktionsspezifikation und Nutzungskonzept | Art. 5 |
| BAS-RISK | Einstufungsvermerk mit getrenntem Produkt- und Anhang-III-Pfad | Zweckbestimmung sowie gegebenenfalls externe Produktentscheidung | Art. 6, Anhänge I und III |
| BAS-LITERACY | KI-Kompetenzkonzept und Nachweis der Umsetzung | Rollenprofil, Schulungs-/Erfahrungsnachweise | Art. 4 |

## Bedingte Pakete

| ID | Paket | Pflichtdokument oder Nachweis | Mindestnachweis | Rechtsgrund |
|---|---|---|---|---|
| TRN-INTERACTION | transparency | Transparenzkonzept für direkte KI-Interaktion | UI/UX-Nachweis der rechtzeitigen Information | Art. 50 Abs. 1 |
| TRN-SYNTHETIC | transparency | Kennzeichnung maschinenlesbarer synthetischer Inhalte | technischer Test oder Dateibeispiel | Art. 50 Abs. 2 |
| TRN-DEEPFAKE | transparency | Offenlegungsprozess für Deepfakes | veröffentlichter Hinweis und Prozess | Art. 50 Abs. 4 |
| TRN-TEXT | transparency | Offenlegungsprozess für KI-Text im öffentlichen Interesse | redaktioneller Prozess und Ausgabebeispiel | Art. 50 Abs. 4 |
| EXC-6-3 | exception_6_3 | Ausnahmebewertung mit Kriterien, Profiling-Prüfung und Genehmiger | Tatsachen zur fehlenden erheblichen Wirkung | Art. 6 Abs. 3–4 |
| EXC-REGISTER | exception_6_3 | Registrierungsnachweis | Eintrag im EU-Register | Art. 49 Abs. 2 |
| EXT-PRODUCT | product_gate | externe sektorale Produktklassifizierung | datierter Vermerk einer qualifizierten Stelle mit Produkt, Version und Drittstellenpflicht | Art. 6 Abs. 1, Anhang I |
| EXT-SECTOR-CNF | product_gate | Nachweis des integrierten sektoralen Konformitätswegs | Zertifikat, Bericht oder bestätigter Verfahrensplan | Art. 43 |

## Hochrisiko-Anbieter

| ID | Pflichtdokument | Mindestnachweis | Rechtsgrund |
|---|---|---|---|
| HRP-RISK | kontinuierliche Risikomanagementakte | Gefahren, vorhersehbare Fehlanwendung, Maßnahmen, Tests und Restrisiken | Art. 9 |
| HRP-DATA | Daten- und Daten-Governance-Akte | Herkunft, Eignung, Relevanz, Repräsentativität, Fehler und Kontrollen | Art. 10 |
| HRP-TECH | technische Dokumentation nach Anhang IV | Architektur-, Modell-, Versions-, Entwicklungs- und Leistungsunterlagen | Art. 11, Anhang IV |
| HRP-LOG | Logging- und Aufbewahrungskonzept | erzeugte Beispielprotokolle und Aufbewahrungskontrolle | Art. 12, 18–19 |
| HRP-IFU | Betriebsanleitung | freigegebene Anleitung mit Zweck, Grenzen und erforderlichen Betreiberinformationen | Art. 13 |
| HRP-OVERSIGHT | Konzept menschlicher Aufsicht | Befugnisse, Kompetenz, Anzeige, Überstimmung, Stop und Tests | Art. 14 |
| HRP-PERFORMANCE | Genauigkeits-, Robustheits- und Cybersicherheitsakte | validierte Metriken, Grenzwerte, Tests und Sicherheitsnachweise | Art. 15 |
| HRP-QMS | Qualitätsmanagementsystem | kontrollierte Verfahren und Verantwortlichkeiten | Art. 17 |
| HRP-RETENTION | Dokumenten- und Protokollaufbewahrung | Aufbewahrungsplan und kontrollierter Ablageort | Art. 18–19 |

## Konformität und Lebenszyklus

| ID | Paket | Pflichtdokument oder Nachweis | Mindestnachweis | Rechtsgrund |
|---|---|---|---|---|
| CNF-PATH | conformity | Konformitätsstrategie | begründete Auswahl von Anhang VI, VII oder sektoraler Integration | Art. 43 |
| CNF-ASSESSMENT | conformity | abgeschlossene Konformitätsbewertung | Prüfbericht oder Zertifikat passend zur Systemversion | Art. 43 |
| CNF-DECLARATION | conformity | EU-Konformitätserklärung | unterschriebene Erklärung mit Anhang-V-Inhalten | Art. 47, Anhang V |
| CNF-CE | conformity | CE-Kennzeichnungsnachweis | Produkt-/UI-/Begleitdokumentnachweis | Art. 48 |
| CNF-REGISTER | conformity | erforderliche Registrierungen | Registerauszug für Anbieter und System | Art. 49, 71 |
| LIF-CAPA | lifecycle | Prozess für Nichtkonformität und Korrekturmaßnahmen | freigegebener CAPA-/Behördenprozess | Art. 20–21 |
| LIF-PMS | lifecycle | Post-Market-Monitoring-Plan | aktiver Plan mit Quellen, Kennzahlen, Auswertung und Feedback | Art. 72 |
| LIF-INCIDENT | lifecycle | Prozess für schwerwiegende Vorfälle | Meldekriterien, Fristen, Rollen, Formulare und Test | Art. 73 |
| LIF-CHANGE | lifecycle | Änderungs- und Neubewertungsprozess | Kriterien für Zweck-, Modell-, Daten-, Architektur- und Leistungsänderungen | Art. 25, Art. 43 Abs. 4 |

## Hochrisiko-Betreiber und Wirtschaftsakteure

| ID | Paket | Pflichtdokument oder Nachweis | Mindestnachweis | Rechtsgrund |
|---|---|---|---|---|
| DEP-OPERATIONS | high_risk_deployer | Betriebskonzept nach Anleitung | Verantwortliche, Eingabedatenkontrolle, Monitoring und Logaufbewahrung | Art. 26 |
| DEP-OVERSIGHT | high_risk_deployer | Benennung und Befähigung der Aufsicht | Benennung, Schulung, Befugnisse und Vertretung | Art. 26 |
| DEP-NOTICES | high_risk_deployer | Beschäftigten- und Betroffeneninformation | freigegebene Hinweise und Ausspielnachweis | Art. 26 |
| DEP-REPORTING | high_risk_deployer | Melde- und Eskalationsprozess | Prozess zu Anbieter, Einführer, Händler und Behörden | Art. 26 |
| DEP-FRIA | high_risk_deployer | Grundrechte-Folgenabschätzung, falls erforderlich | abgeschlossene Bewertung und Meldung | Art. 27 |
| DEP-EXPLANATION | high_risk_deployer | Verfahren für Erläuterungsrechte | Antrags-, Prüf- und Antwortprozess | Art. 86 |
| ACT-AR | economic_actor | Mandat und Pflichtenakte des Bevollmächtigten | schriftliches Mandat und Kontaktdaten | Art. 22 |
| ACT-IMPORTER | economic_actor | Einführer-Prüfakte | Prüfungen, Kennzeichnung, Unterlagen und Eskalationsprozess | Art. 23 |
| ACT-DISTRIBUTOR | economic_actor | Händler-Prüfakte | Prüfungen, Lagerung, Rückverfolgbarkeit und Eskalationsprozess | Art. 24 |

## Schließregel

Jede instanziierte Anforderung muss `verified` oder begründet `not_applicable` sein. Eine Pflicht kann nicht allein deshalb geschlossen werden, weil ein Dokument mit passendem Titel existiert.

