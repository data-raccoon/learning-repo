# Ausfüllbare EU-AI-Act-Checkliste für Krankenhausanwendungen

## Zusammenfassung

Eine einzelne Datei `KI-Compliance-Checkliste.md` erstellen. Sie dient dem KI-Beauftragten als ausfüllbares Tracking-Instrument für alle vier Anwendungen und ist durch YAML-Metadaten, stabile Feld-IDs und feste Statuswerte auf spätere ChatGPT-Skills vorbereitet.

Anwendung 3 wird innerhalb der Felder durch kurze, eindeutig als „Beispiel A3“ markierte Hinweise erläutert. Diese Hinweise sind keine abschließende rechtliche Einstufung.

## Aufbau und Umsetzung

- YAML-Frontmatter mit:
  - Schema- und Template-Version
  - Assessment-, Anwendungs- und Use-Case-ID
  - Systemname, Version, Zweckbestimmung und Lebenszyklusphase
  - Anbieter-/Betreiberrolle
  - Bearbeitungsstatus, Verantwortliche, Prüfer und Fristen
  - Datum und Quelle des geprüften Rechtsstands
  - kontrollierten Werten wie `offen`, `ja`, `nein`, `nicht_anwendbar`, `eskalieren`
- Portfolioübersicht für Anwendungen 1–4 mit Gesamtstatus, vorläufiger Risikoklasse, Rolle, nächstem Prüfschritt und Freigabeentscheidung.
- Anwendung 3 vor der Prüfung in getrennte Use Cases zerlegen:
  - Aufnahme
  - Terminvergabe
  - Entlassbrief-Vorstrukturierung
  - Bettenbelegungssteuerung
  - Abrechnungsdokumente
- Jede Checklistenzeile erhält dieselben Felder:
  - stabile ID
  - Prüffrage oder Tätigkeit
  - Antwort
  - Status
  - Begründung, insbesondere bei `nein` oder `nicht_anwendbar`
  - Nachweis bzw. Dokumentlink
  - Verantwortlicher
  - Fälligkeit
  - direkte Referenz zum Artikel oder Anhang im offiziellen AI Act Explorer

## Prüfprozess

1. Systemgrenze und Zweckbestimmung festhalten; prüfen, ob ein KI-System vorliegt und ob verbotene Praktiken betroffen sind ([Art. 3](https://ai-act-service-desk.ec.europa.eu/de/ai-act/article-3), [Art. 5](https://ai-act-service-desk.ec.europa.eu/de/ai-act/article-5)).
2. Rolle je Use Case bestimmen: Anbieter, Betreiber oder Rollenwechsel durch Eigenentwicklung, Umbenennung oder wesentliche Änderung ([Art. 16](https://ai-act-service-desk.ec.europa.eu/de/ai-act/article-16), [Art. 25](https://ai-act-service-desk.ec.europa.eu/de/ai-act/article-25), [Art. 26](https://ai-act-service-desk.ec.europa.eu/de/ai-act/article-26)).
3. Risikoklasse über Art. 6, Anhang I und Anhang III bestimmen; eine Ausnahme nach Art. 6 Abs. 3 und deren Dokumentations-/Registrierungsfolgen separat begründen.
4. Pflichtenpfad abhängig von Rolle und Einstufung öffnen:
   - Anforderungen an Hochrisiko-KI: Art. 8–15
   - Qualitätsmanagement des Anbieters: Art. 17
   - technische Dokumentation: Art. 11 und Anhang IV
   - Betreiberpflichten und gegebenenfalls Grundrechte-Folgenabschätzung: Art. 26–27
5. Konformitätsweg korrekt auswählen:
   - Anhang III Nr. 2–8: interne Kontrolle nach Anhang VI
   - Anhang III Nr. 1: Art. 43 abhängig von Normenanwendung
   - Produkt-KI nach Anhang I: Integration in das einschlägige sektorale Konformitätsverfahren
6. Konformitätserklärung, CE-Kennzeichnung und Registrierung prüfen ([Art. 47](https://ai-act-service-desk.ec.europa.eu/de/ai-act/article-47), Art. 48–49, Anhang V).
7. Transparenz gegenüber Betreibern und betroffenen Personen prüfen, einschließlich direkter KI-Interaktion und KI-generierter Inhalte ([Art. 13](https://ai-act-service-desk.ec.europa.eu/de/ai-act/article-13), [Art. 50](https://ai-act-service-desk.ec.europa.eu/de/ai-act/article-50), Art. 86).
8. Betrieb und Lebenszyklus abdecken: Logging, menschliche Aufsicht, Korrekturmaßnahmen, wesentliche Änderungen, Post-Market Monitoring und Vorfallmeldungen (Art. 12, 14, 19–20, 43 Abs. 4, 72–73).
9. Abschluss-Gate mit Entscheidung `freigegeben`, `freigegeben_mit_auflagen`, `nicht_freigegeben` oder `weitere_pruefung`, einschließlich Begründung und Freigabevermerken.

## Referenzhinweise für Anwendung 3

- Inline-Hinweise zeigen, dass die fünf Funktionen getrennt bewertet werden müssen.
- Die administrative Nutzung von Patientendaten wird nicht automatisch als Hochrisiko eingestuft.
- Bei Termin- oder Bettensteuerung wird ausdrücklich geprüft, ob Zugang, Anspruch oder Priorisierung von Gesundheitsdiensten wesentlich beeinflusst werden.
- Bei Entlassbriefen werden Autonomie, menschliche Bestätigung, Fehlerfolgen und Protokollierung als Beispielthemen genannt.
- Für Fremdsysteme zeigt das Beispiel den Betreiberpfad; Eigenentwicklung, wesentliche Änderung oder Bereitstellung unter eigenem Namen löst eine erneute Rollenprüfung aus.
- Fehlende Angaben werden als offene Evidenzanforderungen dokumentiert, nicht durch erfundene Annahmen ersetzt.

## Qualitätssicherung

- YAML muss syntaktisch valide und durch spätere Skills eindeutig auslesbar sein.
- Feld-IDs müssen eindeutig und Statuswerte konsistent sein.
- Jede Tätigkeit muss ein Begründungsfeld und einen offiziellen EU-Link besitzen.
- Verzweigungen werden anhand vier typischer Fälle geprüft:
  - Nicht-Hochrisiko-System mit Art.-50-Pflichten
  - Anhang-III-Hochrisiko-System
  - Krankenhaus nur in Betreiberrolle
  - Produkt-KI nach Anhang I, etwa medizinische Bildauswertung
- Rechtsstand und Anwendungsfristen werden mit Prüfdatum ausgewiesen; geltendes Recht und politisch vereinbarte, aber noch nicht konsolidierte Änderungen werden getrennt dargestellt.

## Annahmen

- Das Dokument behandelt ausschließlich den EU AI Act; DSGVO, MDR und IT-Sicherheitsrecht erhalten keine eigenen Compliance-Prüfpfade.
- Anwendung 3 erscheint nur als kurzer Inline-Beispieltext, nicht als vollständig ausgefüllte Bewertung.
- Die Checkliste korrigiert Ungenauigkeiten des Ausgangskontexts: Art. 17 ist das Qualitätsmanagementsystem und nicht Teil der Anforderungen aus Art. 8–15; die Angaben der EU-Konformitätserklärung richten sich nach Anhang V; Anhang VII gilt nicht pauschal für jede sektorale Produkt-KI.
- Die Datei bleibt ein Arbeits- und Demonstrationsinstrument und ersetzt keine rechtliche Einzelfallprüfung.


-----


Ich möchte folgende Änderungen diskutieren:
a) Strikte trennung von Plan/Checkliste und Beispiel in 2 verschiedene Dateien. 
b) Dabei soll das Beispiel Meschen-lesbar sein und keine/kaum maschienen-artefakte enthalten. Es ist ein Output-Beispiel, wenn man dem Plan folgt.
c) Reduziere die Zahl der Punkte auf das Gesetzliche Minimum.


-----


Die drei Änderungen sind sinnvoll und verbessern die Nutzbarkeit deutlich. Ich würde die bestehende Datei nicht nur aufteilen, sondern konzeptionell verschlanken.

Vorgeschlagene Aufteilung:

1. `KI-Compliance-Checkliste.md`
   - wiederverwendbarer Prüfprozess
   - YAML, stabile IDs und kontrollierte Statuswerte
   - keine Anwendung-3-Beispiele
   - nur gesetzlich erforderliche Prüfschritte
   - für spätere Skills optimiert

2. `Beispiel-Anwendung-3.md`
   - vollständig menschenlesbares Ergebnis
   - kein YAML, keine Feld-IDs, keine technischen Skill-Anweisungen
   - normale deutsche Statusbegriffe statt `nicht_begonnen` usw.
   - fünf getrennte Teilanwendungen
   - nachvollziehbare Begründungen, offene Fragen und Rechtsgrundlagen
   - zeigt, wie ein fertiger Bericht nach Anwendung der Checkliste aussieht

Für das gesetzliche Minimum würde ich die derzeit 83 Prüfpunkte auf ungefähr 20–25 reduzieren. Entfernt oder zusammengeführt würden insbesondere:

- doppelte Dokumentations- und Abschlusskontrollen
- operative Empfehlungen ohne unmittelbare gesetzliche Grundlage
- getrennte Zeilen für einzelne Aspekte derselben gesetzlichen Pflicht
- Skill-Regeln aus dem fachlichen Prüfkatalog
- Fristen- und Quellenpflege als eigene Checklistenzeilen
- mehrfach wiederholte Rollen-, Logging- und Monitoringprüfungen

Der verbleibende Kern wäre:

1. System und Zweckbestimmung
2. KI-System gemäß Art. 3
3. KI-Kompetenz gemäß Art. 4
4. verbotene Praxis gemäß Art. 5
5. Anbieter-/Betreiberrolle
6. Hochrisikoprüfung nach Art. 6 und Anhang I
7. Hochrisikoprüfung nach Art. 6 und Anhang III
8. Ausnahme nach Art. 6 Abs. 3
9. Transparenzpflicht nach Art. 50
10. Risikomanagement
11. Daten-Governance
12. technische Dokumentation
13. Logging
14. Betreiberinformationen
15. menschliche Aufsicht
16. Genauigkeit, Robustheit und Cybersicherheit
17. Qualitätsmanagement und Aufbewahrung
18. Betreiberpflichten und gegebenenfalls Grundrechte-Folgenabschätzung
19. Konformitätsbewertung
20. Konformitätserklärung, CE und Registrierung
21. Post-Market Monitoring
22. Korrekturmaßnahmen und Vorfallmeldung
23. wesentliche Änderungen
24. Abschlussentscheidung

Für das Beispiel zu Anwendung 3 empfehle ich eine ehrliche vorläufige Bewertung: Die vorhandenen Kontextinformationen werden ausgewertet, fehlende Hersteller- oder Systemnachweise bleiben ausdrücklich offen. Damit demonstriert das Beispiel nicht nur ein „schönes Endergebnis“, sondern den realistischen Output eines KI-Beauftragten: belastbare Aussagen, vorläufige Einstufungen und klar benannte Evidenzlücken.

Eine noch zu entscheidende Frage ist, ob `Beispiel-Anwendung-3.md` diesen realistischen Zwischenstand zeigen oder als fiktiv vollständig abgeschlossener Musterfall mit zusätzlich erfundenen Annahmen erscheinen soll. Ich empfehle den realistischen Zwischenstand.


-----


# Skill-Chain für ein freigabereifes EU-AI-Act-Dossier

## Zusammenfassung

Den bestehenden Einstufungs-Skill zu einer modularen, fortsetzbaren Skill-Chain ausbauen. `weitere_pruefung` wird ausschließlich ein Zwischenzustand. Erfolgreicher Abschluss ist `dossier_freigabereit`; bei einem nicht behebbaren Verstoß endet die Chain mit `nicht_freigabefaehig` und Abhilfeplan.

Die Skills werden aus `skills/` nach `.agents/skills/` migriert, damit Codex CLI und IDE-Erweiterung sie als Projekt-Skills erkennen. Der bisherige Ordner wird anschließend entfernt, um doppelte oder veraltete Skill-Versionen zu vermeiden. Dies entspricht der [offiziellen Codex-Projektstruktur](https://learn.chatgpt.com/docs/build-skills#where-to-save-skills).

## Skill-Chain und Zustandsmodell

Vier fokussierte Skills erstellen:

- `complete-eu-ai-act-conformity`: Einstieg und Orchestrator; erkennt neuen oder fortzusetzenden Vorgang, ruft die passenden Module auf und beendet den Ablauf erst bei einem zulässigen Endzustand.
- `assess-eu-ai-act`: bestehenden Skill auf Einstufung, Rollen, Verbote, Art. 50 und anwendbaren Pflichtenpfad begrenzen.
- `prepare-eu-ai-act-dossier`: erzeugt Dokumentenplan und belastbare Entwürfe, fordert nicht ableitbare Nachweise gezielt an und prüft eingereichte Evidenz.
- `audit-eu-ai-act-dossier`: kontrolliert Vollständigkeit, Rechtsstand, Widersprüche, Nachweisqualität und Abschlussreife.

Pro Anwendung wird ein `dossier-state.json` als maschinenlesbare Zustandsquelle geführt. Er enthält Use Cases, Rollen, Risikopfad, Rechtsstand, Anforderungen, Dokumente, Evidenz, Verantwortliche und Fristen. Zulässige Gesamtzustände:

- `intake`
- `classification_pending`
- `evidence_pending`
- `drafting`
- `validation_failed`
- `dossier_freigabereit`
- `nicht_freigabefaehig`

Jede einzelne Anforderung erhält `open`, `requested`, `drafted`, `evidenced`, `verified` oder `not_applicable`. Ein KI-erzeugter Entwurf zählt niemals als tatsächlicher Nachweis.

## Dossier und Pflichtverzweigung

Für jeden Vorgang entstehen neben Prüfakte und menschenlesbarer Bewertung:

- Dokumentenplan mit Artikelbezug, Pflichtinhalt, Verantwortlichem und erforderlicher Evidenz.
- Evidenzregister mit Links auf Originaldateien, Quelle, Version, Datum und Prüfergebnis.
- Bedingtes Compliance-Dossier mit ausschließlich anwendbaren Unterlagen.
- Abschlussprüfung und leeres Freigabeprotokoll für den menschlichen Entscheider.
- Bei negativem Ausgang ein Abhilfeplan mit Verstoß, erforderlicher Produktänderung und Wiederaufnahmebedingungen.

Eine zentrale Dokumentenmatrix routet mindestens folgende Pakete:

- Basispaket: Systemgrenze, Zweckbestimmung, AI-Act-Anwendungsbereich, Rollen, Risikoeinstufung, Art.-5-Prüfung und KI-Kompetenz.
- Transparenzpaket: Art.-50-Einstufung, Nutzerinformation und Umsetzungsnachweise.
- Art.-6-Abs.-3-Paket: dokumentierte Ausnahmeprüfung und gegebenenfalls Registrierungsnachweis.
- Hochrisiko-Anbieterpaket: Art. 8–21, technische Dokumentation nach Anhang IV, QMS, Daten-Governance, Logging, Gebrauchsanweisung, menschliche Aufsicht, Leistung, Robustheit und Cybersicherheit.
- Konformitätspaket: Art. 43, Konformitätserklärung, CE-Kennzeichnung und Registrierung; Zertifikate oder externe Entscheidungen dürfen nur als echte Evidenz vermerkt werden.
- Betreiberpaket: Art. 26, gegebenenfalls Art. 27 und 86, Aufsicht, Monitoring, Logs und Informationswege.
- Lebenszykluspaket: Korrekturmaßnahmen, Änderungssteuerung, Post-Market Monitoring und Vorfallmeldung.
- Akteurspakete für Bevollmächtigte, Einführer und Händler, sofern diese Rollen vorliegen.
- Produktpfad: Eine erforderliche sektorale Produkt- oder Medizinprodukteinstufung wird als externes Pflicht-Gate verlangt, aber nicht durch eine erfundene AI-Act-Bewertung ersetzt.

MDR, DSGVO, IT-Sicherheit und Nicht-EU-Recht bleiben außerhalb des Prüfumfangs. Externe Entscheidungen daraus werden nur verlangt, wenn sie eine AI-Act-Einstufung oder ein AI-Act-Dokument unmittelbar bestimmen.

## Abschlusslogik und Validierung

`dossier_freigabereit` ist nur zulässig, wenn:

- jeder Use Case abschließend eingestuft ist;
- jede anwendbare Pflicht `verified` und jede Nichtanwendbarkeit rechtlich begründet ist;
- keine offene Frage, fehlende Evidenz oder widersprüchliche Zweckbestimmung verbleibt;
- alle erforderlichen Dokumente vorhanden, versioniert, verlinkt und einem Verantwortlichen zugeordnet sind;
- der aktuelle Rechtsstand unmittelbar vor dem Abschluss erneut über amtliche EU-Quellen geprüft wurde;
- technische, organisatorische oder externe Tatsachen durch echte Nachweise und nicht nur durch KI-Text belegt sind;
- die Abschlussprüfung ohne kritischen Befund bestanden ist.

Bei fehlenden Unterlagen pausiert die Chain mit einer konkreten Evidenzanforderung und setzt denselben Vorgang nach Bereitstellung fort. Dieser Zustand ist kein Abschluss. Bei verbotener Praxis oder dauerhaft nicht erfüllbarer Pflicht wird `nicht_freigabefaehig` gesetzt.

Ein PowerShell-Validator ohne zusätzliche Laufzeitabhängigkeiten prüft JSON-Schema, Statuswerte, eindeutige IDs, Pflichtdokumente, Evidenzlinks, offene Punkte und Abschlussbedingungen.

## Tests und Migration

- Skill-Metadaten, Pfade, Referenzen und implizite sowie explizite Auslösung für alle vier Skills prüfen.
- Den vorhandenen Toiletten-Tagebuch-Vorgang migrieren und nachweisen, dass er bei fehlender Produktklassifizierung nicht fälschlich `dossier_freigabereit` erreicht.
- Routingtests für Nicht-Hochrisiko mit Art. 50, Anhang-III-Hochrisiko, reinen Betreiber, Anhang-I-Produktpfad, Art.-6-Abs.-3-Ausnahme und verbotene Praxis durchführen.
- Fortsetzungstest: fehlenden Nachweis registrieren, Evidenz ergänzen, erneut auditieren und Status korrekt weiterführen.
- Negativtests sicherstellen: Entwurf statt Evidenz, veralteter Rechtsstand, fehlender Prüfer, widersprüchliche Zweckbestimmung oder defekter Link verhindern den Abschluss.
- Menschenlesbare Berichte bleiben frei von YAML, internen IDs und Maschinenstatus; maschinenlesbare Zustände bleiben in Prüfakte und JSON-Manifest.
- Die bestehende 25-Punkte-Checkliste bleibt gesetzliches Mindest-Gate; die Dokumentenmatrix ergänzt nur die zur Erfüllung dieser Pflichten erforderlichen Unterlagen.

