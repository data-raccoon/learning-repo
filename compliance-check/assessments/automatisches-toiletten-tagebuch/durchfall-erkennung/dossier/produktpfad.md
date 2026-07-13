# Produktpfad und externe Entscheidung – DOC-PRODUCT-GATE

**Assessment / System / Version:** ASSESSMENT-2026-001 / Automatisches Toiletten-Tagebuch / nicht angegeben  
**Dokumentversion / Status:** 0.2 / draft  
**Owner / Reviewer / Datum:** Produktrecht / offen / 2026-07-13  
**Anforderungen / Rechtsgrund:** EXT-PRODUCT, EXT-SECTOR-CNF / Art. 6 Abs. 1, Anhang I, Art. 43  
**Evidenz:** EVD-SYSTEM-001, EVD-PRODUCT-001 und bedingt EVD-SECTOR-CNF-001 – angefordert

## 1. Zweck und Geltungsbereich

Kontrolliertes Gate für die externe sektorale Produktklassifizierung und den daraus folgenden AI-Act-Produktpfad.

## 2. Belegte Tatsachen

Die App soll Ereignisse als „normal“ oder „Durchfall“ protokollieren und optional einen Hausarzt-Export ermöglichen. Zweckbestimmung, Werbung, Gebrauchsanweisung und Systemversion sind nicht freigegeben. Keine externe Produktentscheidung liegt vor.

## 3. Erforderliche externe Entscheidung

Eine nachweislich qualifizierte unabhängige Stelle muss anhand der verbindlichen EVD-SYSTEM-001 dokumentieren:

1. einschlägigen sektoralen Rechtsakt aus Anhang I oder begründetes Nichtvorliegen;
2. Produkt- oder Sicherheitsbauteilstatus und gegebenenfalls Klasse;
3. ob für das konkrete Produkt eine Drittstellen-Konformitätsbewertung im Hinblick auf Inverkehrbringen/Inbetriebnahme vorgeschrieben ist;
4. konkreten sektoralen Konformitätsweg, beteiligte Stelle und Systemversionsbezug;
5. Annahmen, ausgeschlossene Aussagen und Änderungs-/Neubewertungsauslöser.

## 4. Entscheidungslogik und Grenzen

- Kein Anhang-I-Produkt: Art. 6 Abs. 1 greift nicht; voraussichtlich nicht hochriskant, sofern kein anderer Pfad entsteht.
- Anhang-I-Produkt ohne vorgeschriebene Drittstellenbewertung: Art. 6 Abs. 1 greift nicht.
- Anhang-I-Produkt mit vorgeschriebener Drittstellenbewertung: `annex_i_high_risk`; Hochrisiko-Anbieter-, Konformitäts- und Lebenszykluspakete öffnen.

Dieser Entwurf ist keine MDR- oder sektorale Entscheidung. EVD-PRODUCT-001 darf nicht intern ersetzt werden.

## 5. Verantwortlichkeiten und Betrieb

Produkt/Recht frieren EVD-SYSTEM-001 ein; Produktrecht beauftragt qualifizierte Stelle; Qualität prüft Authentizität/Version; AI-Act-Verantwortlicher aktualisiert State und Dokumentenplan.

## 6. Evidenz und amtliche Rechtsquellen

[Art. 6](https://ai-act-service-desk.ec.europa.eu/de/ai-act/article-6), [Anhang I](https://ai-act-service-desk.ec.europa.eu/de/ai-act/annex-1), [Art. 43](https://ai-act-service-desk.ec.europa.eu/de/ai-act/article-43).

## 7. Änderungsverlauf

0.1 – 2026-07-13 – Externe Entscheidung angefordert.  
0.2 – 2026-07-13 – Aussteller-, Inhalts-, Versions- und Folgerouting-Anforderungen präzisiert.

