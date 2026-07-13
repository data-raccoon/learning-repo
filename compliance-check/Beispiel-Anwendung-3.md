# Beispielbewertung: Administrative KI-Agenten rund um Patientendaten

**Krankenhaus St. Ulrich – realistischer Zwischenstand**  
**Bewertungsstand:** 13. Juli 2026  
**Ergebnis:** Weitere Prüfung erforderlich

> Dieses Dokument zeigt, wie ein menschenlesbares Ergebnis nach Anwendung der EU-AI-Act-Checkliste aussehen kann. Es beruht ausschließlich auf den bislang vorliegenden Angaben. Fehlende Hersteller- und Systeminformationen werden nicht durch erfundene Tatsachen ersetzt. Es handelt sich um eine Demo, nicht um ein Rechtsgutachten.

## 1. Kurzfazit

Das Krankenhaus plant KI-Agenten für Aufnahme, Terminplanung, Entlassbriefe, Bettenbelegung und Abrechnungsdokumente. Die Agenten sollen teilweise autonom handeln; kritische Aktionen werden teilweise, aber nicht durchgehend, von ärztlichem oder pflegerischem Personal bestätigt.

Eine abschließende Einstufung ist derzeit nicht möglich. Die fünf Funktionen haben unterschiedliche Zweckbestimmungen und Risiken und müssen getrennt bewertet werden. Nach den vorhandenen Angaben ist keine verbotene KI-Praxis erkennbar. Ebenso lässt sich aber noch nicht ausschließen, dass Termin- oder Bettenentscheidungen den Zugang zu Gesundheitsdiensten wesentlich beeinflussen und dadurch ein Tatbestand aus [Art. 6](https://ai-act-service-desk.ec.europa.eu/de/ai-act/article-6) in Verbindung mit [Anhang III](https://ai-act-service-desk.ec.europa.eu/de/ai-act/annex-3) betroffen ist.

Vor einem Produktivbetrieb sind insbesondere Anbieterrolle, genaue Entscheidungslogik, Autonomie, menschliche Aufsicht, mögliche Auswirkungen auf den Zugang zu Gesundheitsleistungen und Herstellerunterlagen zu klären.

## 2. Betrachtete Teilanwendungen

| Teilanwendung | Was nach aktuellem Stand vorgesehen ist | Vorläufige Bewertung |
|---|---|---|
| Aufnahme | Administrative Verarbeitung von Patientendaten bei der Krankenhausaufnahme | Wahrscheinlich keine Hochrisiko-Anwendung, sofern nur Daten erfasst, geprüft und weitergeleitet werden. Offen ist, ob der Agent Entscheidungen über Aufnahme oder Zugang trifft. |
| Terminvergabe | Automatische Vergabe von Behandlungsterminen | Erhöhter Klärungsbedarf. Reine Kalenderoptimierung wäre nicht automatisch hochriskant. Eine patientenbezogene Priorisierung oder Einschränkung des Zugangs zu Gesundheitsdiensten kann anders zu bewerten sein. |
| Entlassbrief-Vorstrukturierung | Erstellen eines strukturierten Entwurfs für medizinisches Personal | Nach aktuellem Stand eher vorbereitende Unterstützung. Entscheidend sind Inhalt, klinische Relevanz und die Frage, ob vor Verwendung stets eine qualifizierte Person prüft und verantwortlich freigibt. |
| Bettenbelegungssteuerung | Optimierung der Belegung und teilweise autonome Steuerung | Erhöhter Klärungsbedarf. Reine Kapazitätsplanung ist anders zu bewerten als eine patientenbezogene Zuteilung, die Aufnahme, Behandlungspfad oder Zugang wesentlich beeinflusst. |
| Abrechnungsdokumente | Vorstrukturierung oder Erstellung administrativer Unterlagen | Wahrscheinlich keine Hochrisiko-Anwendung, solange keine Entscheidung über Leistungsansprüche oder Gesundheitszugang getroffen wird. Zweck und Entscheidungswirkung sind noch zu belegen. |

## 3. Anwendungsbereich und verbotene Praktiken

Die beschriebenen Agenten sind voraussichtlich KI-Systeme im Sinne von [Art. 3](https://ai-act-service-desk.ec.europa.eu/de/ai-act/article-3). Für eine belastbare Feststellung fehlen jedoch Angaben zur technischen Funktionsweise, zu eingesetzten Modellen und zu regelbasierten Komponenten.

Aus der Beschreibung ergeben sich derzeit keine Hinweise auf eine verbotene Praxis nach [Art. 5](https://ai-act-service-desk.ec.europa.eu/de/ai-act/article-5). Insbesondere sind keine biometrische Kategorisierung, Emotionserkennung, Social Scoring oder manipulative Verfahren beschrieben. Diese Aussage ist vorläufig, weil eine vollständige Funktionsliste fehlt.

Das Krankenhaus muss außerdem sicherstellen, dass die Personen, die die Agenten einsetzen oder beaufsichtigen, über eine für ihren Verantwortungsbereich ausreichende KI-Kompetenz verfügen ([Art. 4](https://ai-act-service-desk.ec.europa.eu/de/ai-act/article-4)). Ein Schulungs- und Befähigungsnachweis liegt noch nicht vor.

## 4. Rolle des Krankenhauses

Die Rolle ist noch offen. Aus dem Kontext geht nicht hervor, ob das Krankenhaus:

- ein fertiges Fremdsystem unverändert einsetzt,
- ein System im eigenen Auftrag entwickeln lässt,
- selbst Modelle oder Agenten entwickelt,
- die Zweckbestimmung eines Fremdsystems verändert oder
- das System unter eigenem Namen in Betrieb nimmt.

Bei unveränderter Nutzung eines Fremdsystems nach Herstelleranleitung wäre das Krankenhaus voraussichtlich Betreiber. Eigenentwicklung, Bereitstellung unter eigenem Namen, eine geänderte Zweckbestimmung oder eine wesentliche Änderung können nach [Art. 25](https://ai-act-service-desk.ec.europa.eu/de/ai-act/article-25) dazu führen, dass das Krankenhaus Anbieterpflichten übernimmt.

Diese Rollenentscheidung ist Voraussetzung für die weitere Prüfung. Ohne sie lässt sich nicht bestimmen, ob das Krankenhaus selbst eine Konformitätsbewertung durchführen muss oder die Konformität eines externen Anbieters nachvollziehen muss.

## 5. Vorläufige Risikoklassifizierung

Die Nutzung von Patientendaten und der Einsatz in einem Krankenhaus führen für sich genommen nicht automatisch zur Einstufung als Hochrisiko-KI-System. Maßgeblich sind die konkrete Zweckbestimmung und die in [Art. 6](https://ai-act-service-desk.ec.europa.eu/de/ai-act/article-6), [Anhang I](https://ai-act-service-desk.ec.europa.eu/de/ai-act/annex-1) und [Anhang III](https://ai-act-service-desk.ec.europa.eu/de/ai-act/annex-3) beschriebenen Tatbestände.

### Produktbezogene Hochrisiko-Einstufung

Bislang ist nicht erkennbar, dass die administrativen Agenten selbst ein Medizinprodukt oder ein Sicherheitsbauteil eines regulierten Produkts sind. Die vom Anbieter festgelegte Zweckbestimmung und vorhandene Produktzertifizierungen wurden aber noch nicht vorgelegt. Eine Einstufung nach Art. 6 Abs. 1 kann deshalb noch nicht abschließend ausgeschlossen werden.

### Hochrisiko-Anwendungsfälle aus Anhang III

Besonders relevant ist Anhang III Nr. 5 Buchstabe a. Er betrifft bestimmte Systeme, mit denen Behörden oder in deren Namen beurteilen, ob natürliche Personen Anspruch auf grundlegende öffentliche Unterstützungsleistungen und -dienste einschließlich Gesundheitsdiensten haben oder ob diese gewährt, eingeschränkt, widerrufen oder zurückgefordert werden. Ob das Krankenhaus eine Behörde ist oder bei diesen Entscheidungen im Namen einer Behörde handelt, ist nicht angegeben und muss ausdrücklich geklärt werden.

Die vorliegenden Angaben zeigen nicht, dass das Krankenhaus einen solchen Anspruch bewertet. Termin- und Bettensteuerung könnten den tatsächlichen Zugang jedoch wesentlich beeinflussen. Deshalb muss geklärt werden:

- Werden Patienten lediglich innerhalb bereits feststehender Behandlungen eingeplant?
- Werden Personen zurückgestellt, abgewiesen oder unterschiedlich priorisiert?
- Welche Merkmale fließen in die Priorisierung ein?
- Kann das System eine Aufnahme, Behandlung oder Entlassung faktisch verhindern oder verzögern?
- Handelt es sich um Notfalltriage oder Priorisierung medizinischer Nothilfe im Sinne von Anhang III Nr. 5 Buchstabe d?

Sollte ein Tatbestand aus Anhang III erfüllt sein, ist anschließend die Ausnahme nach Art. 6 Abs. 3 zu prüfen. Dafür reicht die Bezeichnung als „Vorstrukturierung“ nicht aus. Es muss nachgewiesen werden, dass das System das Entscheidungsergebnis nicht wesentlich beeinflusst und gegebenenfalls nur eine eng begrenzte Verfahrens- oder Vorbereitungsaufgabe erfüllt. Bei Profiling natürlicher Personen greift diese Ausnahme nicht.

### Vorläufiges Ergebnis

| Teilanwendung | Vorläufige Risikoeinschätzung | Sicherheit der Einschätzung |
|---|---|---|
| Aufnahme | Eher nicht hochriskant, sofern rein administrativ | Niedrig bis mittel |
| Terminvergabe | Offen; möglicher Bezug zum Gesundheitszugang | Niedrig |
| Entlassbrief-Vorstrukturierung | Eher nicht hochriskant, sofern vorbereitend und wirksam geprüft | Niedrig bis mittel |
| Bettenbelegungssteuerung | Offen; möglicher wesentlicher Einfluss auf Aufnahme oder Versorgung | Niedrig |
| Abrechnungsdokumente | Eher nicht hochriskant, sofern rein dokumentarisch | Niedrig bis mittel |

## 6. Menschliche Aufsicht und Autonomie

Der Kontext nennt eine menschliche Bestätigung für kritische Aktionen, aber nicht für jede Aktion. Das reicht für eine positive Bewertung noch nicht aus. Für jeden Agenten ist festzuhalten:

- welche Aktionen ohne Freigabe ausgeführt werden,
- welche Aktionen als kritisch gelten und wer dies festgelegt hat,
- wer die erforderliche fachliche Kompetenz und Entscheidungsbefugnis besitzt,
- ob Ausgaben verständlich geprüft werden können,
- ob eine Aktion rechtzeitig verhindert, abgebrochen oder rückgängig gemacht werden kann und
- wie Fehler, Übersteuerungen und Korrekturen protokolliert werden.

Falls eine Teilanwendung als Hochrisiko eingestuft wird, ergeben sich konkrete Pflichten zur menschlichen Aufsicht aus [Art. 14](https://ai-act-service-desk.ec.europa.eu/de/ai-act/article-14) und für das Krankenhaus als Betreiber aus [Art. 26](https://ai-act-service-desk.ec.europa.eu/de/ai-act/article-26).

Für Entlassbriefe wäre als Mindestkontrolle zu erwarten, dass eine qualifizierte Person den vollständigen Entwurf vor Verwendung inhaltlich prüft, erforderliche Änderungen vornimmt und die Verantwortung für die freigegebene Fassung übernimmt. Ob dies tatsächlich vorgesehen ist, ist noch offen.

## 7. Transparenz

Eine direkte Interaktion von Patienten mit den administrativen Agenten ist nicht beschrieben. Sollte ein Agent unmittelbar mit Patienten kommunizieren, muss geprüft werden, ob die Betroffenen nach [Art. 50](https://ai-act-service-desk.ec.europa.eu/de/ai-act/article-50) darüber informiert werden müssen, dass sie mit einem KI-System interagieren.

Bei automatisch erzeugten Texten sind die anbieterbezogenen Kennzeichnungspflichten und Ausnahmen des Art. 50 Abs. 2 zu prüfen. Für intern vorbereitete Entlassbriefentwürfe ist außerdem entscheidend, ob es sich lediglich um eine unterstützende Standardbearbeitung handelt und wie stark der Inhalt verändert oder neu erzeugt wird. Eine Veröffentlichung zur Information der Öffentlichkeit ist nach dem beschriebenen Zweck nicht vorgesehen.

Wenn eine Entscheidung auf der Ausgabe eines in Anhang III aufgeführten Hochrisiko-KI-Systems beruht und eine Person rechtlich oder ähnlich erheblich beeinträchtigt, kann außerdem das Recht auf eine klare und aussagekräftige Erläuterung nach [Art. 86](https://ai-act-service-desk.ec.europa.eu/de/ai-act/article-86) relevant werden.

## 8. Konformitätsbewertung und Betreiberprüfung

Ob eine Konformitätsbewertung erforderlich ist und wer sie durchführen muss, kann erst nach Rollen- und Risikoklassifizierung entschieden werden.

Falls das Krankenhaus Anbieter eines Hochrisiko-KI-Systems wird, muss es unter anderem die Anforderungen aus Art. 9 bis 15 erfüllen, ein Qualitätsmanagementsystem nach Art. 17 betreiben und das zutreffende Verfahren nach [Art. 43](https://ai-act-service-desk.ec.europa.eu/de/ai-act/article-43) abschließen. Danach folgen gegebenenfalls EU-Konformitätserklärung, CE-Kennzeichnung und Registrierung.

Falls das Krankenhaus ausschließlich Betreiber eines Hochrisiko-Systems ist, muss es vor allem die Herstellerunterlagen nachvollziehen und seine Betreiberpflichten aus Art. 26 erfüllen. Außerdem ist zu prüfen, ob für das Krankenhaus als öffentliche Stelle oder privater Erbringer öffentlicher Dienste vor der ersten Nutzung eine Grundrechte-Folgenabschätzung nach [Art. 27](https://ai-act-service-desk.ec.europa.eu/de/ai-act/article-27) erforderlich ist.

Derzeit liegen weder eine Konformitätserklärung noch technische Dokumentation, Betriebsanleitung, Registrierung oder eine begründete Nicht-Hochrisiko-Bewertung des Anbieters vor.

## 9. Betrieb, Änderungen und Vorfälle

Für Hochrisiko-KI muss der Anbieter ein System zur Beobachtung nach dem Inverkehrbringen betreiben ([Art. 72](https://ai-act-service-desk.ec.europa.eu/de/ai-act/article-72)). Das Krankenhaus muss als Betreiber den Betrieb überwachen und relevante Risiken, Fehlfunktionen und Vorfälle an den Anbieter und gegebenenfalls die zuständigen Stellen weitergeben.

Für schwerwiegende Vorfälle sind Erkennung, interne Eskalation, Untersuchung und die fristgerechte Meldung nach [Art. 73](https://ai-act-service-desk.ec.europa.eu/de/ai-act/article-73) vorzubereiten. Ein entsprechender Prozess ist bislang nicht beschrieben.

Updates an Modell, Datenbasis, Architektur, Zweckbestimmung oder Autonomie müssen kontrolliert werden. Bei einer wesentlichen Änderung ist nach Art. 43 Abs. 4 eine neue Konformitätsbewertung erforderlich. Das ist insbesondere relevant, wenn die Agenten aus Nutzungsdaten weiterlernen oder ihre Handlungsmöglichkeiten nachträglich erweitert werden.

## 10. Fehlende Nachweise

Für eine belastbare Entscheidung werden mindestens folgende Informationen benötigt:

1. getrennte Zweckbestimmung für jeden der fünf Use Cases,
2. Systemarchitektur und eingesetzte Modelle oder Fremdkomponenten,
3. Anbieter, Vertragsmodell und Verantwortlichkeiten,
4. Herstellerklassifizierung und Begründung der Risikoklasse,
5. Produktstatus und gegebenenfalls sektorale Zertifizierung,
6. vollständige Beschreibung automatischer Aktionen und menschlicher Freigaben,
7. Kriterien für Termin-, Aufnahme- und Bettenpriorisierung,
8. Angaben zu Profiling und betroffenen Personengruppen,
9. technische Dokumentation, Betriebsanleitung und Leistungsgrenzen,
10. Logging-, Überwachungs-, Änderungs- und Vorfallkonzept,
11. Nachweis der erforderlichen KI-Kompetenz und
12. gegebenenfalls Konformitätserklärung, CE-Kennzeichnung und Registrierung.

## 11. Entscheidung und nächste Schritte

**Entscheidung:** Weitere Prüfung erforderlich.  
**Produktivfreigabe:** Auf Grundlage der vorliegenden Informationen nicht erteilbar.  
**Grund:** Rollen, Systemgrenzen, Risikoklassifizierung, Autonomie und erforderliche Nachweise sind noch nicht ausreichend bestimmt.

Als nächste Schritte sollte das Krankenhaus:

1. die fünf Use Cases organisatorisch und technisch trennen,
2. je Use Case Zweck, Ausgaben, Entscheidungswirkung und Autonomie dokumentieren,
3. Anbieter- und Betreiberrolle verbindlich festlegen,
4. insbesondere Termin- und Bettensteuerung gegen Anhang III Nr. 5 prüfen,
5. Herstellerunterlagen und fehlende Evidenz anfordern,
6. die Wirksamkeit menschlicher Aufsicht konkretisieren und
7. anschließend Risikoklasse, Pflichtenpfad und Freigabe erneut entscheiden.

Die Entscheidung muss wiederholt werden, wenn sich Zweckbestimmung, Systemversion, Autonomie, Datenbasis oder Einsatzkontext wesentlich ändern.
