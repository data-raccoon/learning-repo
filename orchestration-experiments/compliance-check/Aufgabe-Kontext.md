## Kontext - Tranings-Beispiel

KRANKENHAUS ST. ULRICH
ZUR ERINNERUNG
1.
Es möchte den Verbrauch von medizinischen Verbrauchsmaterialien (Handschuhe, Spritzen, Verbandsmaterial, Gefäße) mit KI
optimieren. Ein ML-Modell analysiert historische Verbrauchsdaten, Belegungszahlen und saisonale Muster und schlägt
automatisch Bestellmengen vor. Ziel: Engpässe vermeiden, Überbestände reduzieren, Kosten senken.
2.
Es entwickelt eine App für Patienten und Angehörige, die häufig wiederkehrende Fragen beantwortet: Besuchszeiten, Abläufe vor
Operationen, Medikamenteneinnahme, Entlassungsprozesse, Nachsorge. Der Chatbot basiert auf einem Sprachmodell und wird
mit internen Dokumenten trainiert. Die App heisst "Ihre Fragen - Unsere Antworten" und kann im W-LAN des Krankenhauses
hochgeladen werden.
3.
Es möchte administrative Prozesse rund um Patientendaten automatisieren: Aufnahme, Terminplanung, Entlassbriefe,
Bettenbelegungssteuerung und Abrechnungsdokumente. Zentrale Datenquelle ist die Elektronische Patientenakte (EPA), die
seit 2025 in Deutschland für alle gesetzlich Versicherten verpflichtend ist. KI-Agenten sollen dabei teilweise autonom handeln:
Termine vergeben, Entlassbriefe vorstrukturieren, Bettenbelegung optimieren. Ein Arzt oder Pflegeperson bestätigt kritische
Aktionen — aber nicht jede.
4.
Das Krankenhaus führt seit sechs Monaten ein KI-System zur automatisierten Auswertung von CT- und Röntgenbildern ein. Der
Pilot in der Radiologie läuft, der komplette Roll-Out über alle in Frage kommenden Abteilungen ist für das nächste Quartal
geplant. Das System erkennt Muster, identifiziert Auffälligkeiten und priorisiert Behandlungspfade für das medizinische
Personal. Es gibt eine Schnittstelle zu einer in Indien von einem dortigen Dienstleister gehosteten Datenbank mit über 10 Mio.
anonymisierten CTs, insbesondere aus dem Gebiet der Onkologie.


## Kontext - EU-AI Act

DIE EU-KONFORMITÄTSERKLÄRUNG
(ART. 47)
Konformitätsbewertung ist das formelle Verfahren, mit dem der Anbieter prüft und bestätigt,
dass sein Hochrisiko-KI-System die Anforderungen der EU AI Act erfüllt. Sie muss spezifische
Angaben enthalten, um Transparenz und Rückverfolgbarkeit zu gewährleisten.
Identifikation: Name, Typ und eindeutige Kennung des KI-Systems.
Anbieter: Name und Anschrift des Anbieters (oder Bevollmächtigten).
Verantwortung: Erklärung der alleinigen Verantwortung des Anbieters.
Konformität: Bestätigung der Konformität mit dem AI Act und anderen EU-Vorschriften.
Datenschutz: Erklärung zur Einhaltung der DSGVO und verwandter Datenschutzgesetze,
falls zutreffend.
Normen: Verweise auf harmonisierte Normen oder gemeinsame Spezifikationen.
Bewertungsverfahren: Details zur benannten Stelle und zum
Konformitätsbewertungsverfahren, falls involviert.
Unterzeichnung: Ort, Datum, Name, Funktion und Unterschrift der bevollmächtigten Person.

DIE ZWEI VERFAHREN · ANHANG VI UND VII
Es gibt nur zwei Wege zur Konformitätsbewertung — welcher gilt, hängt am System.

Anhang VI
Internes Verfahren
Wer prüft? Anbieter selbst
Wann? Regel: alle Hochrisiko-Systeme nach Anhang III

Anhang VII
Verfahren mit Notified Body
Wer prüft? Externe akkreditierte Prüfstelle
Wann? Ausnahme: biometrische Systeme (Anhang III Nr. 1) oder KI als Sicherheitskomponente in Produkten unter sektoralen Harmonisierungsvorschriften (MDR, Maschinenverordnung u.a.)

So führt man eine Konformitätsbewertung praktisch durch:

1. RISIKOKLASSE BESTÄTIGEN
Ist es wirklich Hochrisiko nach Art. 6 + Anhang III?

2. KONFORMITÄTSBEWERTUNGSVERFAHREN AUSWÄHLEN
Anhang VI (intern) oder Anhang VII (extern)? Biometrie oder sektorale Vorschriften = Anhang VII, sonst Anhang VI.

3 PRÜFUNG GEGEN DIE ACHT ANFORDERUNGEN (ABSCHNITT 2)
Art. 9 (Risikomanagement) · Art. 10 (Daten-Governance) · Art. 11
(Technische Doku) · Art. 12 (Aufzeichnung/Logging) · Art. 13
(Transparenz für Betreiber) · Art. 14 (Menschliche Aufsicht) · Art. 15
(Cybersicherheit) · Art. 17 (Qualitätsmanagement)

4 TECHNISCHE DOKUMENTATION FINALISIEREN
Anhang-IV-konform — Systembeschreibung, Architektur, Entwicklungsprozess (Trainingsdaten, Validierung, Testergebnisse).

(SCHRITT 5 — BEI ANHANG VII:
NOTIFIED BODY EINBINDEN)
QM-Audit, Doku-Prüfung, ggf. System-Tests, Zertifikat-Erteilung. In Deutschland: TÜV Süd, TÜV Rheinland, DEKRA — für KI-VO noch in der Zertifizierungsphase.

SCHRITT 6 — EU-KONFORMITÄTSERKLÄRUNG ERSTELLEN UND UNTERZEICHNEN
Anbieter-ID, System-ID, angewandte Normen, Datum, Unterschrift einer zeichnungsberechtigten Person.

SCHRITT 7 — CE ANBRINGEN + EU-DATENBANK-REGISTRIERUNG
Vor Inverkehrbringen. Typische Dauer für ein Hochrisiko-System: 6–18 Monate von der Risikoklassifizierung bis zur Markteinführung.

Wesentliche Änderung (Art. 43 Abs. 4): Bei wesentlicher Änderung muss die Konformitätsbewertung wiederholt werden. Lernende
Systeme sind in einer schwierigen Position — jedes Modell-Update aus Nutzerbewertungen kann eine wesentliche Änderung sein.
Faustregel: Wenn sich Risikomanagement, Datenbasis, Architektur oder Genauigkeit relevant verändern, ist neu zu bewerten.


## Trainings-Aufgabe

COMPLIANCE-TEMPLATE
Ihr möchtet den Prozess der Konformitätsbewertung möglichst automatisieren. Das gilt sowohl für den Fall, dass Ihr selbst in der Anbieterrolle sein
solltet als auch für den (häufigeren) Fall, dass Ihr die Konformitätsbewertung eines Anbieters nachvollziehen müßt. Bitte erstellt einen Entwurf
("Demo, kein Memo") für eine Diskussion mit der IT, dem DSB und dem CISO, wie ein solches "Tracking" aussehen könnte.
Fokus auf die Bereiche: Konformitätsbewertung, Dokumentation, Transparenz, Post-Market Monitoring und Meldepflicht.
Tipp 1: Integriert eine klickbare Referenz zum jeweiligen Paragraphen des EU AI Act für jede Tätigkeit.
Tipp 2: Baut ein Feld "Begründung" ein, um insbesondere eine Ablehnung oder Nicht-Anwendbarkeit zu erläutern.
