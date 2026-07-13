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


-----


# Skill-Chain bereinigen und lokales Assessment-Dashboard erstellen

## Zusammenfassung

- Die vier Skills bleiben bestehen: `assess` für Einstufung, `prepare` für Dokumente und Evidenz, `audit` als alleinige Abschlussinstanz und `complete` als Orchestrator. Ihre fachlich unterschiedlichen Aufgaben rechtfertigen die Trennung.
- Kein zusätzlicher Dashboard-Skill wird angelegt. Die Anzeige ist eine deterministische, schreibgeschützte HTML-Anwendung.
- Die Chain wird auf einen eindeutigen Zustands- und Datenvertrag gebracht. Assessment- und Beispielinhalte werden nicht fachlich bewertet oder verändert.
- Das Dashboard wird als einzelne `dashboard.html` mit eingebettetem CSS und JavaScript umgesetzt, über einen lokalen Python-Webserver geöffnet und per Ordnerauswahl mit Daten versorgt.

## Skill- und Chain-Korrekturen

- `complete-eu-ai-act-conformity` wird der einzige automatische Einstieg für vollständige oder fortzusetzende Verfahren. Die drei Fachmodule bleiben explizit einzeln nutzbar, geben im orchestrierten Betrieb aber immer an den Orchestrator zurück.
- Der Einstufungs-Skill startet die Dossiererstellung nur im orchestrierten Modus. Eine allein angeforderte Ersteinstufung endet mit Einstufungsbericht und klarer Übergabeempfehlung.
- Pro Use Case gilt genau ein Dossierordner mit genau einer `dossier-state.json`. Das bestehende `useCases`-Array bleibt kompatibel, muss in diesem Modell aber genau einen Eintrag enthalten. Mehrere Use Cases werden über `applicationId` gruppiert.
- `dossier-state.json` wird zur maschinellen Quelle der Wahrheit. `pruefakte.md`, `dokumentenplan.md` und `evidenzregister.md` sind menschenlesbare Projektionen und dürfen keinen abweichenden Status führen.
- Der Ablauf wird entkoppelt: Nach abgeschlossener Einstufung dürfen Dokumente entworfen werden; fehlende Belege führen zu `evidence_pending`. Sobald Dokumente und Evidenz prüfbereit sind, folgt `audit_pending`. Auditbefunde führen über `validation_failed` zurück zur passenden Arbeitsphase.
- Nur der Audit-Skill darf `dossier_freigabereit` oder `nicht_freigabefaehig` setzen. Eine menschliche Freigabe bleibt davon getrennt und `release.status` bleibt bis dahin `pending`.
- Die generischen Skill-Trigger werden mit der aktuell krankenhausspezifischen Stammcheckliste harmonisiert: Der 25-Punkte-Kern wird organisationsneutral formuliert; Gesundheitswesen/MDR bleibt ein optionaler Sektorpfad mit externen Nachweisen, keine eigene Rechtsprüfung.
- Doppelte oder konkurrierende Anweisungen werden entfernt. Matrix, Zustandsmodell, zulässige Werte und Übergaberegeln erhalten jeweils genau eine maßgebliche Quelle.

## Datenvertrag und Kompatibilität

- `schemaVersion` wird auf `1.1.0` angehoben; vorhandene `1.0.0`-Assessments bleiben lesbar und werden nicht automatisch umgeschrieben.
- Neu aufgenommen werden:
  - `checklistItems`: die 25 Stamm-IDs mit `answer`, `status`, `rationale`, `evidenceLinks`, `owner`, `dueAt`, `legalReferences` und zugeordneten granularen `requirementIds`.
  - `audit_pending` als kontrollierter Gesamtzustand.
  - Eine Regel, dass IDs innerhalb eines Dossiers eindeutig und alle Dokument-/Evidenzreferenzen relativ zum Dossierordner sein müssen.
- Granulare Anforderungen der Dossiermatrix bleiben unter `requirements`; über `checklistItems[].requirementIds` wird die bisher fehlende nachvollziehbare Verbindung zur Stammcheckliste hergestellt.
- Ein JSON-Schema und ein read-only Validierungswerkzeug prüfen Enumwerte, Pflichtfelder, eindeutige IDs, Referenzen und Abschlussinvarianten. Der Audit-Skill muss diese Prüfung vor einem Endzustand ausführen.
- Das Dashboard unterstützt beide Schemaversionen. Fehlende 1.1-Felder werden als „im Altschema nicht vorhanden“ dargestellt und nicht erfunden.

## `dashboard.html`

- Startansicht mit „Assessment-Ordner auswählen“. Primär wird `showDirectoryPicker()` verwendet; als Fallback dient ein Datei-Input mit Verzeichnisauswahl.
- Die HTML sucht rekursiv nach `dossier-state.json`. Der jeweilige Elternordner bildet die Dossiergrenze; Anwendungen werden über `applicationId`, Dossiers über `assessmentId` plus Pfad identifiziert.
- Dashboard-Funktionen:
  - Kennzahlen für Assessments, Zustände, Risikopfade, offene/angeforderte/verifizierte Anforderungen, Evidenz- und Reviewstatus.
  - Suche und Filter nach Anwendung, Zustand, Risikopfad, Aktualisierungsdatum und offenen Nachweisen.
  - Gruppierung Anwendung → Use Case → Dossier.
  - Detailansicht mit Übersicht, 25-Punkte-Checkliste, granularen Anforderungen, Dokumenten, Evidenzmetadaten und Review.
  - Dokumentbaum für referenzierte und zusätzliche Markdown-Dateien in Dossier- und Reviewordnern.
- Markdown wird durch eine kleine eigene, sichere Renderlogik dargestellt: Überschriften, Absätze, Listen, Tabellen, Blockquotes, Hervorhebungen, Links sowie Inline- und Block-Code. Rohes HTML wird immer escaped; Links erlauben nur sichere Protokolle und normalisierte dossierinterne Pfade.
- Evidenzdateien werden aus Datenschutzgründen nicht automatisch geöffnet oder in den Speicher geladen. Angezeigt werden zunächst nur die Metadaten aus dem Zustandsmodell; eine Datei wird erst nach bewusstem Nutzerklick gelesen.
- Ungültiges JSON, doppelte IDs, unbekannte Enumwerte, fehlende Dateien und nicht unterstützte Schemaversionen erscheinen als verständliche Warnungen, ohne die übrigen Assessments zu blockieren.
- Die Oberfläche ist responsive, tastaturbedienbar, kontrastreich, druckbar und enthält keine Netzwerkaufrufe, Telemetrie oder CDN-Abhängigkeiten.
- Betrieb: Repository-Verzeichnis mit `python -m http.server 8000` bereitstellen, `http://localhost:8000/dashboard.html` in Edge oder Chrome öffnen und dort den `assessments`-Ordner auswählen.

## Test- und Abnahmekriterien

- Skill-Szenarien: neue Einstufung, standalone Einstufung, vollständige Chain, Fortsetzung bei Evidenzlücke, mehrere Use Cases einer Anwendung, Versionsänderung, Auditfehler und beide kontrollierten Endzustände.
- Vertragsprüfung: alle vier Skills bestehen die Skill-Validierung; Zustandsdateien bestehen das JSON-Schema; jede granulare Anforderung ist mindestens einer Stamm-ID zugeordnet.
- Dashboard-Tests: leerer Ordner, vorhandene 1.0- und neue 1.1-Dossiers, gemischte Zustände, fehlerhaftes JSON, doppelte IDs, fehlende Markdown-Datei, unbekannter Status, große Dokumentmenge und Sonderzeichen/Umlaute.
- Sicherheitstests: Markdown mit HTML/Script-Inhalten, unsicheren Links und `../`-Pfaden wird neutralisiert; ohne Nutzeraktion werden keine Evidenzinhalte gelesen.
- Abnahme: Alle gültigen Dossiers erscheinen ohne manuelle Indexdatei, Filter und Kennzahlen stimmen mit den Zustandsdateien überein, sämtliche Markdown-Dokumente sind navigierbar und ein fehlerhaftes Dossier beeinträchtigt keine anderen.

## Annahmen

- Assessment- und Beispielinhalte dienen nur als strukturelle Testdaten und werden weder juristisch bewertet noch geändert.
- Das Dashboard ist ausschließlich lesend; Bearbeitung, Freigaben und Statusänderungen bleiben Aufgabe der Skill-Chain.
- Zielbrowser sind aktuelle Edge- oder Chrome-Versionen auf `localhost`.
- Der lokale Python-Server stellt nur die HTML bereit; der Assessment-Zugriff erfolgt bewusst über die Browser-Ordnerfreigabe.
