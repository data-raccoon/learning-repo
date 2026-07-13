---
name: complete-eu-ai-act-conformity
description: Steuert einen neuen oder fortzusetzenden EU-AI-Act-Konformitätsvorgang für eine Anwendung bis zu einem vollständig belegten, geprüften und für die menschliche Entscheidung freigabereifen Dossier oder zu einem begründeten negativen Endzustand. Verwenden bei vollständigem Konformitätscheck, Dossier vervollständigen, offene Nachweise schließen, Prüfung fortsetzen oder Freigabereife herstellen. Nicht als eigenständige MDR-, DSGVO-, IT-Sicherheits- oder Nicht-EU-Prüfung verwenden.
---

# EU-AI-Act-Dossier bis zur Freigabereife führen

Führe den gesamten Vorgang. Behandle fehlende Informationen als fortsetzbaren Arbeitszustand, niemals als erfolgreiches Ende.

## Ressourcen und Module laden

1. Lies `references/workflow.md` und `references/state-model.md` vollständig.
2. Lies bei einer neuen oder offenen Einstufung `../assess-eu-ai-act/SKILL.md` vollständig und folge diesem Modul.
3. Lies nach feststehendem Pflichtenpfad `../prepare-eu-ai-act-dossier/SKILL.md` vollständig und folge diesem Modul.
4. Lies vor jedem Endzustand `../audit-eu-ai-act-dossier/SKILL.md` vollständig und folge diesem Modul.
5. Nutze die Stammcheckliste `../../../KI-Compliance-Checkliste.md`. Erfinde keine fehlenden Rechts- oder Tatsachenfeststellungen.

## Vorgang beginnen oder fortsetzen

1. Suche unter `assessments/` nach einem passenden `dossier-state.json`.
2. Frage bei mehreren Treffern nach der Assessment-ID. Erzeuge bei keinem Treffer einen neuen anwendungsspezifischen Ordner.
3. Lies bei einem bestehenden Vorgang zuerst den vollständigen Zustand, die Prüfakte, das Evidenzregister und den letzten Auditbericht.
4. Setze beim frühesten unvollständigen Gate fort. Wiederhole keine bereits belegten Fragen.
5. Aktualisiere `dossier-state.json` nach jeder materiellen Antwort, jedem Dokument, jedem Nachweis und jedem Audit.

## Phasen steuern

1. `intake`: Mindestangaben und Use Cases erheben.
2. `classification_pending`: KI-System, Anwendungsbereich, Verbote, Rollen, Risikopfad und Art. 50 abschließend bestimmen.
3. `evidence_pending`: konkrete Nachweise mit Zweck, akzeptierten Belegarten, Verantwortlichem und Fälligkeit anfordern.
4. `drafting`: nur die anwendbaren Dokumente entwerfen und mit belegten Tatsachen füllen.
5. `validation_failed`: Auditbefunde einzeln beheben und erneut prüfen.
6. `dossier_freigabereit`: nur nach bestandenem Audit setzen.
7. `nicht_freigabefaehig`: nur bei belegter verbotener Praxis oder einem dokumentierten, nicht behebbaren Verstoß setzen und einen Abhilfeplan erzeugen.

## Unterbrechungen behandeln

Wenn der Benutzer einen erforderlichen Nachweis noch nicht liefern kann:

- setze den Vorgang auf `evidence_pending`;
- schreibe die Anforderung in Dokumentenplan, Evidenzregister und Zustandsdatei;
- nenne genau den nächsten benötigten Nachweis und wie die Chain fortgesetzt wird;
- bezeichne dies als Pause, nicht als Abschluss oder Freigabeentscheidung.

Verwende `weitere_pruefung` nur in der bestehenden 25-Punkte-Prüfakte als Zwischenstand. Verwende es nie als Endzustand der Chain.

## Abschluss ausgeben

Ein erfolgreicher Lauf endet mit `dossier_freigabereit`, einem bestandenen `review/abschlusspruefung.md` und einem unausgefüllten `review/freigabeprotokoll.md`. Stelle dies nicht als rechtswirksame Freigabe dar. Diese bleibt einem namentlichen Menschen vorbehalten.

