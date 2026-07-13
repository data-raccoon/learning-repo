# System- und Zweckbestimmung – DOC-SYSTEM

**Assessment / System / Version:** ASSESSMENT-2026-001 / Automatisches Toiletten-Tagebuch / nicht angegeben  
**Dokumentversion / Status:** 0.2 / draft  
**Owner / Reviewer / Datum:** Produkt und Entwicklung / offen / 2026-07-13  
**Anforderungen / Rechtsgrund:** BAS-SYSTEM / Art. 3  
**Evidenz:** EVD-INTERVIEW-001 nicht akzeptierbar; EVD-SYSTEM-001, EVD-TECH-001 und EVD-PERFORMANCE-001 angefordert

## 1. Zweck und Geltungsbereich

Geplanter Zweck ist die lokale Erkennung von Badezimmergeräuschen als „normal“ oder „Durchfall“ und ihre nicht personenbezogene Zeitreihen-Protokollierung zur persönlichen Nutzung. Bewohner sollen einen Export optional manuell einem Hausarzt zeigen können. Dieser Zweck ist noch nicht verbindlich freigegeben.

## 2. Belegte Tatsachen

Es liegt nur die unbestätigte Arbeitsnotiz EVD-INTERVIEW-001 vor. Danach wird Rohschall lokal verarbeitet; Sprache kann technisch miterfasst werden, soll aber nicht ausgewertet oder gespeichert und sofort verworfen werden. Es gibt keine automatische Übertragung, Diagnose oder Behandlungsempfehlung.

## 3. Systemgrenze und vorgesehene Kontrollen

Vorgesehene Eingabe: Mikrofonsignal im Badezimmer. Vorgesehene Ausgabe: Ereigniskategorie und Zeitreiheneintrag. Nutzer: Bewohner; mitbetroffen können Besucher sein. Hausärzte erhalten nur einen statischen Export und keinen Systemzugang.

Offene Eingaben: Modell/Inferenzverfahren, App-/Modellversion, Hardware, Komponenten, Betriebssystem, Mikrofonaktivierung, Puffer, Datenfluss, Speicherorte/-dauern, Rohschalllöschung, Sprachfilter, Korrektur/Löschung, Export, Telemetrie, Updates und App-Store-Komponenten.

## 4. Autonomie, vorhersehbare Nutzung und ausgeschlossene Zwecke

Die Ereignisklassifikation erfolgt automatisiert; Bewohner entscheiden über Korrektur, Löschung und Weitergabe. Vorhersehbare Fehlanwendungen sind Diagnoseinterpretation, Dauerüberwachung, Zuordnung zu Personen, Arzt-/Versicherungszugang und Nutzung in Pflege-/Arbeitskontexten. Ausgeschlossen werden sollen Diagnose, Therapie, Notfallalarm, medizinische Überwachung, Personen-/Stimm-/Emotionsanalyse und automatische Drittweitergabe. Diese Grenzen sind noch nicht technisch und vertraglich belegt.

## 5. Verantwortlichkeiten und Betrieb

Produkt genehmigt Zweck und Marketing; Entwicklung bindet Modell/Architektur an eine Systemversion; QA validiert Leistung und Ausschlüsse; Recht prüft Produktstatus und Werbung. Jede Zweck-, Daten- oder Kontextänderung löst Neueinstufung aus.

## 6. Evidenz und amtliche Rechtsquellen

EVD-SYSTEM-001, EVD-TECH-001 und EVD-PERFORMANCE-001 sind erforderlich. Rechtsquelle: [Art. 3](https://ai-act-service-desk.ec.europa.eu/de/ai-act/article-3).

## 7. Änderungsverlauf

| Version | Datum | Änderung |
|---|---|---|
| 0.1 | 2026-07-13 | Kurzentwurf |
| 0.2 | 2026-07-13 | Systemgrenze, Autonomie, Fehlanwendung und Evidenzanforderungen ergänzt |

