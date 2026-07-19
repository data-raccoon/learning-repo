# System- und Zweckbestimmung – DOC-SYSTEM

**Assessment / System:** ASSESSMENT-2026-002 / Buchwissen testen  
**Gültige Systemversion:** offen; Planungsstand mit variablen Modellen  
**Dokumentversion / Status:** 0.1 / draft  
**Owner / Reviewer / Datum:** Produkt / offen / 2026-07-13  
**Anforderungen / Rechtsgrund:** BAS-SYSTEM / Art. 3  
**Evidenz:** [EVD-001 bis EVD-003](../evidenzregister.md) – nicht akzeptiert bzw. angefordert

## 1. Zweck und Geltungsbereich

Das System soll Fragen aus Buchinhalten erzeugen, Schülerantworten bewerten und Punktzahl sowie Feedback bereitstellen, damit Lehrkräfte das Lernniveau einstufen können. Zielgebiete sind Deutschland, Österreich und die Schweiz. Dieser Entwurf gilt nur für diesen Use Case.

## 2. Belegte Tatsachen

Es liegen ausschließlich unbestätigte Benutzerangaben vor. Schüler sehen KI-generierte Fragen; Lehrkräfte treffen die formelle Einstufung. Drittanbietermodelle werden promptbasiert angepasst und sollen kostenabhängig wechseln.

## 3. Systemgrenze und vorgesehener Ablauf

Vorgesehene Eingaben: Buchinhalt, vom Anbieter gesetzte Bewertungsmaßstäbe, Prompts und Schülerantworten. Vorgesehene Ausgaben: Fragen, Punktzahl und Feedback. Vorgesehene Nutzer: Schüler und Lehrkräfte; vorgesehene Betreiber: Schulen und Träger. Betroffene Personen: Schüler aller Altersstufen.

Offen sind Hosting, Benutzerverwaltung, Datenspeicherung, Schnittstellen, konkrete Modelle, Modellversionen, Promptversionen, Logging, automatische Aktionen, Rücknahmefunktionen sowie die Trennung zwischen Anbieter- und Betreiberkomponenten.

## 4. Autonomie, Verwendung und ausgeschlossene Zwecke

Die KI erzeugt und bewertet Inhalte autonom innerhalb der konfigurierten Aufgabe. Sie soll keine formelle Einstufung ohne Lehrkraft auslösen. Ausgeschlossen sind Emotionserkennung, biometrische Auswertung, Profiling, disziplinarische Sanktionen und vollautomatische Bildungsentscheidungen. Diese Ausschlüsse sind technisch und vertraglich noch umzusetzen.

## 5. Verantwortlichkeiten und Betrieb

Der Anbieter verantwortet Zweck, Maßstäbe, Prompts und Gesamtsystem. Betreiber verantworten konkrete Nutzung und menschliche Aufsicht. Ein kontrolliertes Versionsschema muss mindestens Anwendung, Modell, Promptset, Bewertungsrubrik und Daten-/Konfigurationsstand binden.

## 6. Evidenz und Rechtsquellen

EVD-001 bis EVD-003 sind einzureichen. Rechtsquelle: [Art. 3](https://ai-act-service-desk.ec.europa.eu/de/ai-act/article-3) und [Anhang IV](https://ai-act-service-desk.ec.europa.eu/de/ai-act/annex-4).

## 7. Änderungsverlauf

0.1 – 2026-07-13 – Erstentwurf; alle technischen Details offen.

