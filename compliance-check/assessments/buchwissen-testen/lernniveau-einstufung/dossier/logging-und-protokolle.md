# Logging- und Protokollkonzept – DOC-LOG

**Assessment / System / Version:** ASSESSMENT-2026-002 / Buchwissen testen / Planungsstand  
**Dokumentversion / Status:** 0.1 / draft  
**Owner / Reviewer / Datum:** Entwicklung und IT / offen / 2026-07-13  
**Anforderungen / Rechtsgrund:** HRP-LOG / Art. 12, 18–19  
**Evidenz:** EVD-012 – angefordert

## 1. Zweck und Geltungsbereich

Rekonstruktion von Betrieb, Modell-/Promptstand, Bewertung und menschlicher Aufsicht über den angemessenen Zeitraum.

## 2. Belegte Tatsachen

Keine Logging-Implementierung oder Aufbewahrungsdauer ist belegt.

## 3. Vorgesehene Protokollfelder und Kontrollen

Mindestens: Ereignis-ID, Zeit, Betreiber/Systemrelease, Modellanbieter und -version, Prompt-/Rubrikversion, Buch-/Eingabereferenz, Ausgabereferenz, Fehlerstatus, Warnungen, menschliche Prüfung, Override/Stop, Beschwerde-/Vorfallbezug und Integritätsmerkmal. Direkte Inhalte und Identifikatoren sind nur im erforderlichen Umfang zu protokollieren; Datenschutzprüfung bleibt separat.

Zugriffe, Manipulationsschutz, Export, Uhrzeitsynchronisation, Verfügbarkeit, Löschsperren und kontrollierte Aufbewahrung sind zu implementieren und zu testen.

## 4. Ergebnisse und Grenzen

Ohne EVD-012 keine Aussage zur technischen Erfüllung. Aufbewahrungsfristen werden in DOC-RETENTION festgelegt.

## 5. Verantwortlichkeiten und Betrieb

Entwicklung implementiert; IT betreibt; Qualität prüft Stichproben und Replay; Betreiber bewahren ihnen zugängliche Logs nach Anleitung auf.

## 6. Evidenz und amtliche Rechtsquellen

[Art. 12](https://ai-act-service-desk.ec.europa.eu/de/ai-act/article-12), [Art. 18](https://ai-act-service-desk.ec.europa.eu/de/ai-act/article-18), [Art. 19](https://ai-act-service-desk.ec.europa.eu/de/ai-act/article-19).

## 7. Änderungsverlauf

0.1 – 2026-07-13 – Feld- und Kontrollentwurf.

