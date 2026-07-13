# Risikomanagementakte – DOC-RISK

**Assessment / System / Version:** ASSESSMENT-2026-002 / Buchwissen testen / Planungsstand  
**Dokumentversion / Status:** 0.1 / draft  
**Owner / Reviewer / Datum:** Qualität / offen / 2026-07-13  
**Anforderungen / Rechtsgrund:** HRP-RISK / Art. 9  
**Evidenz:** EVD-009, EVD-014 bis EVD-016, EVD-026 – angefordert

## 1. Zweck und Geltungsbereich

Kontinuierliches Risikomanagement über Entwicklung, Validierung, Inverkehrbringen, Betrieb und Modellwechsel.

## 2. Belegte Tatsachen

Punktzahl und Feedback beeinflussen die Lernniveau-Einstufung. Schüler aller Altersstufen sind betroffen; Modelle sollen kostenabhängig wechseln; die Prüftiefe der Lehrkraft ist noch nicht verbindlich.

## 3. Vorläufiges Risikoregister

Bewertungen für Schwere, Wahrscheinlichkeit und Restrisiko sind offen und dürfen erst nach Tests freigegeben werden.

| Risiko-ID | Ursache / Fehlanwendung | Betroffene | mögliche Folge | vorgesehene Maßnahme | erforderlicher Test | Owner | Status |
|---|---|---|---|---|---|---|---|
| R-001 | falsche oder halluzinierte Musterantwort | Schüler | falsche Punktzahl/Lernniveau | Grounding, Rubrik, Lehrkraftprüfung | fachlicher Goldstandardtest | Pädagogik/QA | open |
| R-002 | Bias nach Alter, Sprache, Schulform oder Antwortstil | Schülergruppen | systematische Benachteiligung | segmentierte Validierung und Schwellen | Gruppenvergleich | Data/QA | open |
| R-003 | Lehrkraft übernimmt Ausgabe ohne ausreichende Prüfung | Schüler | unangemessene Einstufung | verbindliche Mindestprüfung, Override, Begründung | Aufsichtstest | Produkt/Betreiber | open |
| R-004 | kostengetriebener Modellwechsel verändert Leistung | Schüler/Betreiber | unbemerkte Qualitätsverschlechterung | Modellregister, Revalidierung, Rollback | Parallel-/Regressionstest | Entwicklung/QA | open |
| R-005 | ungeeignete oder manipulierte Buch-/Antwortdaten | Schüler | fehlerhafte oder schädliche Inhalte | Eingabekontrollen, Quellenbindung | adversarial input test | Entwicklung | open |
| R-006 | Prompt Injection oder Datenabfluss | Schüler/Schule | Offenlegung oder Kontrollverlust | Isolation, Filter, Zugriffsschutz | Security-Test | Security | open |
| R-007 | altersunangemessene Fragen/Feedback | Minderjährige | psychische/unterrichtliche Beeinträchtigung | Altersprofile, Inhaltsregeln, menschliche Prüfung | Alters-/Inhaltstest | Produkt/Pädagogik | open |
| R-008 | unklare KI-Information | Schüler/Eltern | Täuschung/Übervertrauen | Art.-50-Hinweis und Betreiberinformation | UX-/Barrierefreiheitstest | UX/Recht | open |
| R-009 | Log fehlt oder ist unvollständig | Anbieter/Betreiber | Entscheidung nicht rekonstruierbar | revisionsfähige Protokolle | Log-Replay-Test | Entwicklung/IT | open |
| R-010 | ungeplante Nutzung für Noten, Zugang oder Sanktionen | Schüler | stärkere Grundrechtswirkung | Zweckbegrenzung, technische/vertragliche Sperren, Monitoring | Misuse-Szenariotest | Produkt/Recht | open |

## 4. Ergebnisse und Grenzen

Dies ist ein Gefahreninventar, keine freigegebene Risikobewertung. Schwere, Wahrscheinlichkeit, Akzeptanzkriterien, Testergebnisse und Restrisiken fehlen.

## 5. Verantwortlichkeiten und Betrieb

Qualität führt das Register; Risiko-Owner liefern Tests und Maßnahmen. Freigabe darf erst nach dokumentierter Restrisikoentscheidung erfolgen. PMS und CAPA speisen neue Erkenntnisse zurück.

## 6. Evidenz und amtliche Rechtsquellen

[Art. 9](https://ai-act-service-desk.ec.europa.eu/de/ai-act/article-9); Evidenzanforderungen im [Evidenzregister](../evidenzregister.md).

## 7. Änderungsverlauf

0.1 – 2026-07-13 – Vorläufiges Risikoinventar erstellt.

