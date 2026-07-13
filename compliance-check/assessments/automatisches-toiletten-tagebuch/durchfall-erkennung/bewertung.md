# EU-AI-Act-Vorprüfung: Automatisches Toiletten-Tagebuch

**Organisation:** Verkäufer und Entwickler; Rechtsträger und Sitz noch nicht angegeben  
**Use Case:** Lokale Erkennung und Protokollierung von „normalen“ und „Durchfall“-Ereignissen anhand von Geräuschen im Badezimmer  
**Prüfdatum:** 13. Juli 2026  
**Ergebnis:** Weitere Prüfung erforderlich

## Kurzfazit

Die App ist nach den vorliegenden Angaben voraussichtlich ein KI-System. Der Verkäufer entwickelt die Anwendung selbst und bringt sie unter eigener Verantwortung auf den Markt; damit ist er Anbieter im Sinne des EU AI Acts.

Eine verbotene KI-Praktik oder ein Hochrisiko-Anwendungsfall aus Anhang III ist derzeit nicht erkennbar. Eine endgültige Einstufung ist trotzdem noch nicht möglich: Entscheidend ist, ob die verbindliche Zweckbestimmung und die Werbung die App zu einem Medizinprodukt oder einem anderen Produkt nach Anhang I machen und ob dafür eine Drittstelle in die Konformitätsbewertung einzubeziehen ist. In diesem Fall könnte die App nach Artikel 6 Absatz 1 als Hochrisiko-KI gelten.

Bis zur Klärung dieses Produktpfads sollte die App nicht zur Store-Einreichung freigegeben werden.

## Bewerteter Sachverhalt

Die App soll als „automatisches Toiletten-Tagebuch“ weltweit verkauft werden. Sie verarbeitet Badezimmergeräusche lokal und führt eine Zeitreihe mit den Kategorien „normal“ und „Durchfall“. Die Aufzeichnung wird nicht einzelnen Personen zugeordnet. Sprache kann technisch miterfasst werden, soll aber weder analysiert noch gespeichert und unmittelbar verworfen werden.

Bewohner verwenden das Tagebuch persönlich. Sie entscheiden selbst, ob sie das Protokoll ihrem Hausarzt zeigen. Es gibt weder eine automatische Übermittlung an den Arzt noch eine automatische Diagnose, Behandlungsempfehlung oder sonstige Folgemaßnahme. Besucher können sich ebenfalls im Erfassungsbereich befinden.

## Einordnung nach dem EU AI Act

### KI-System und Anbieterrolle

Eine softwaregestützte Ableitung von Ereigniskategorien aus Audiodaten erfüllt voraussichtlich die Definition eines KI-Systems. Die technische Modellbeschreibung fehlt noch und muss diese Annahme bestätigen.

Da Verkäufer und Entwickler identisch sind und die App kommerziell bereitstellen, liegt die Anbieterrolle nahe. Das gilt auch bei einem Sitz außerhalb der EU, sobald die App in der EU in Verkehr gebracht wird. Bewohner, die sie ausschließlich persönlich und nicht beruflich nutzen, fallen dagegen nicht unter die Betreiberpflichten des AI Acts. Der Hausarzt wird nach dem beschriebenen Ablauf ebenfalls nicht Betreiber des KI-Systems, weil er nur ein vom Bewohner ausgewähltes Protokoll erhält. Erhält die Praxis später Zugriff auf die App oder deren KI-Funktionen, muss die Rollenbewertung wiederholt werden.

### Verbotene Praktiken

Nach dem beschriebenen Funktionsumfang ist keine verbotene Praxis erkennbar. Insbesondere werden Sprache, Stimme, Identität oder Emotionen nach Angabe nicht ausgewertet. Diese Bewertung setzt voraus, dass die technische Implementierung das tatsächlich ausschließt. Eine spätere Sprach-, Emotions- oder Personenanalyse wäre eine wesentliche Funktionsänderung und müsste neu geprüft werden.

### Risikoklasse

Das persönliche Toiletten-Tagebuch fällt nach aktuellem Sachverhalt unter keinen Anwendungsfall aus Anhang III. Es entscheidet nicht über Beschäftigung, Bildung, Versicherungen, öffentliche Leistungen oder den Zugang zu Gesundheitsdiensten.

Offen ist der Produktpfad: Die Formulierungen in Store, Werbung und Gebrauchsanweisung bestimmen, ob die Software einen medizinischen Zweck beansprucht. Falls sie ein von Anhang I erfasstes Produkt oder Sicherheitsbauteil ist und das betreffende Produktrecht eine Konformitätsbewertung durch eine Drittstelle verlangt, greift der Hochrisikopfad des Artikels 6 Absatz 1. Diese produktrechtliche Entscheidung muss separat durch eine dafür qualifizierte Stelle getroffen und dokumentiert werden.

## Pflichten, die jetzt einzuplanen sind

Der Anbieter muss bereits heute ausreichende KI-Kompetenz bei den mit Entwicklung, Betrieb und Aufsicht befassten Personen sicherstellen. Die Verbote aus Artikel 5 gelten ebenfalls bereits.

Da die geplante Veröffentlichung erst in einigen Monaten erfolgen soll, sollte die App die Transparenzregeln des Artikels 50 von Beginn an erfüllen. Vor der ersten Nutzung sollte klar und verständlich erklärt werden, dass eine automatisierte Klassifikation von Geräuschen stattfindet. Ob diese Information im konkreten Interface rechtlich zwingend ist oder die KI-Natur bereits offensichtlich ist, sollte anhand der fertigen Oberfläche entschieden werden. Eine reine Ereignisklassifikation erzeugt nach dem bekannten Funktionsumfang keine synthetischen Audio-, Bild-, Video- oder Textinhalte.

Die umfangreichen Hochrisiko-Pflichten – unter anderem Risikomanagement, Daten-Governance, technische Dokumentation, Protokollierung, menschliche Aufsicht, Qualitätsmanagement, Konformitätsbewertung und Marktbeobachtung – werden erst dann abschließend zugeordnet, wenn der Produktpfad geklärt ist.

## Vor einer Freigabe fehlende Nachweise

1. Vollständiger Name, Sitz und Verantwortlichkeit des Anbieters; bei einem Drittlandanbieter gegebenenfalls der unionsrechtlich erforderliche Vertreter.
2. Verbindliche Zweckbestimmung, Store-Beschreibung, Werbung und Gebrauchsanweisung ohne widersprüchliche Gesundheits- oder Diagnoseversprechen.
3. Produkt- und Medizinproduktebewertung einschließlich Klassifizierung, CE-Status und geplantem Konformitätsweg.
4. Modell-, Versions- und Architekturunterlagen, die die KI-Eigenschaft und die Systemgrenze belegen.
5. Validierung der Erkennungsleistung mit Fehlerraten und Grenzen für unterschiedliche Badezimmer, Geräte, Nutzergruppen und Störgeräusche.
6. Technischer Nachweis, dass Rohschall und Sprache ausschließlich lokal verarbeitet, nicht inhaltlich oder biometrisch analysiert und unmittelbar gelöscht werden.
7. Fertige Nutzeroberfläche mit verständlicher KI-Information sowie Möglichkeiten, Einträge zu prüfen, zu korrigieren und zu löschen.
8. Exakte Länder und Veröffentlichungstermine sowie ein Verfahren für Änderungen, Beschwerden, Sicherheitsprobleme und gegebenenfalls Vorfälle.

Die Erfassung intimer Audiodaten, Gesundheitsbezüge und möglicherweise uninformierter Besucher wirft zusätzlich erhebliche Fragen nach Datenschutz-, Kommunikations-, Verbraucher- und nationalem Recht auf. Diese Fragen sind nicht Gegenstand dieser AI-Act-Vorprüfung, müssen aber vor einem weltweiten Vertrieb gesondert geklärt werden.

## Entscheidung

**Weitere Prüfung erforderlich.** Die App ist voraussichtlich keine Hochrisiko-KI nach Anhang III. Eine Freigabe kann erst erfolgen, nachdem insbesondere die produktrechtliche Zweckbestimmung und ein möglicher Hochrisikopfad über Anhang I verbindlich geklärt wurden. Bis dahin dürfen die offenen Punkte nicht als „nicht anwendbar“ behandelt werden.

## Offizielle Quellen

- [Artikel 2 – Anwendungsbereich](https://ai-act-service-desk.ec.europa.eu/de/ai-act/article-2)
- [Artikel 3 – Begriffsbestimmungen](https://ai-act-service-desk.ec.europa.eu/de/ai-act/article-3)
- [Artikel 4 – KI-Kompetenz](https://ai-act-service-desk.ec.europa.eu/de/ai-act/article-4)
- [Artikel 5 – Verbotene Praktiken](https://ai-act-service-desk.ec.europa.eu/de/ai-act/article-5)
- [Artikel 6 – Einstufung als Hochrisiko-KI](https://ai-act-service-desk.ec.europa.eu/de/ai-act/article-6)
- [Anhang I – Harmonisierungsrechtsvorschriften](https://ai-act-service-desk.ec.europa.eu/de/ai-act/annex-1)
- [Anhang III – Hochrisiko-Anwendungsfälle](https://ai-act-service-desk.ec.europa.eu/de/ai-act/annex-3)
- [Artikel 50 – Transparenzpflichten](https://ai-act-service-desk.ec.europa.eu/de/ai-act/article-50)
- [Artikel 113 – Inkrafttreten und Anwendung](https://ai-act-service-desk.ec.europa.eu/de/ai-act/article-113)
- [EU-Kommission: Zeitplan der Umsetzung](https://ai-act-service-desk.ec.europa.eu/de/ai-act/timeline/zeitplan-fuer-die-umsetzung-des-eu-ki-gesetzes)
- [EU-Kommission: AI Act – aktueller regulatorischer Rahmen](https://digital-strategy.ec.europa.eu/en/policies/regulatory-framework-ai)

Hinweis zum Rechtsstand: Der konsolidierte Verordnungstext und politische bzw. gesetzgeberische Änderungen sind getrennt zu verfolgen. Die Kommission meldete am 7. Mai 2026 eine politische Einigung zu angepassten Hochrisiko-Fristen; bis zur formellen Übernahme ist dies nicht mit bereits konsolidiertem Recht gleichzusetzen.
