---
name: complete-eu-ai-act-conformity
description: Einziger Orchestrator für einen neuen oder fortzusetzenden vollständigen EU-AI-Act-Konformitätsvorgang bis zu einem belegten, geprüften und für die menschliche Entscheidung freigabereifen Dossier oder begründeten negativen Endzustand. Verwenden bei vollständigem Konformitätscheck, Dossier vervollständigen, offenen Nachweisen, Fortsetzung oder Freigabereife. Nicht für isolierte Phasen- oder Nicht-EU-Prüfungen verwenden.
---

# EU-AI-Act-Dossier bis zur Freigabereife führen

Führe den gesamten Vorgang. Behandle fehlende Informationen als fortsetzbaren Arbeitszustand, niemals als erfolgreiches Ende.

## Ressourcen und Module laden

1. Lies `references/workflow.md` und `references/state-model.md` vollständig.
2. Lies bei einer neuen oder offenen Einstufung `../assess-eu-ai-act/SKILL.md` vollständig und folge diesem Modul.
3. Lies nach feststehendem Pflichtenpfad `../prepare-eu-ai-act-dossier/SKILL.md` vollständig und folge diesem Modul.
4. Lies vor jedem Endzustand `../audit-eu-ai-act-dossier/SKILL.md` vollständig und folge diesem Modul.
5. Nutze die Stammcheckliste `../../../KI-Compliance-Checkliste.md`. Erfinde keine fehlenden Rechts- oder Tatsachenfeststellungen.
6. Nutze `references/dossier-state.schema.json` als maschinellen Vertrag und `scripts/validate_dossier_state.py` vor jeder Phasenübergabe.

## Vorgang beginnen oder fortsetzen

1. Suche unter `assessments/` nach einem passenden `dossier-state.json`.
2. Frage bei mehreren Treffern nach der Assessment-ID. Erzeuge bei keinem Treffer je eigenständigem Use Case einen Ordner und genau einen Zustand.
3. Lies bei einem bestehenden Vorgang zuerst den vollständigen Zustand, die Prüfakte, das Evidenzregister und den letzten Auditbericht.
4. Setze beim frühesten unvollständigen Gate fort. Wiederhole keine bereits belegten Fragen.
5. Aktualisiere immer zuerst `dossier-state.json`; leite Prüfakte, Dokumentenplan und Evidenzregister anschließend als menschenlesbare Projektionen daraus ab.

## Phasen steuern

1. `intake`: Mindestangaben und Use Cases erheben.
2. `classification_pending`: KI-System, Anwendungsbereich, Verbote, Rollen, Risikopfad und Art. 50 abschließend bestimmen.
3. `drafting`: anwendbare Anforderungen instanziieren und Dokumente aus belegten Tatsachen entwerfen; unbekannte Inhalte offen lassen.
4. `evidence_pending`: konkrete Nachweise anfordern, wenn fehlende Evidenz die weitere Prüfung blockiert; danach zu `drafting` zurückkehren.
5. `audit_pending`: nur setzen, wenn Anforderungen belegt oder begründet nicht anwendbar und Dokumente mindestens geprüft sind; Auditmodul ausführen.
6. `validation_failed`: Auditbefunde beheben und abhängig vom Befund zu `drafting`, `evidence_pending` oder `audit_pending` zurückkehren.
7. `dossier_freigabereit`: nur durch das Auditmodul nach bestandenem Audit setzen.
8. `nicht_freigabefaehig`: nur durch das Auditmodul bei belegter verbotener Praxis oder dokumentiert nicht behebbarem Verstoß setzen.

## Unterbrechungen behandeln

Wenn der Benutzer einen erforderlichen Nachweis noch nicht liefern kann:

- setze den Vorgang auf `evidence_pending`;
- schreibe die Anforderung in Dokumentenplan, Evidenzregister und Zustandsdatei;
- nenne genau den nächsten benötigten Nachweis und wie die Chain fortgesetzt wird;
- bezeichne dies als Pause, nicht als Abschluss oder Freigabeentscheidung.

Verwende `weitere_pruefung` nur in der bestehenden 25-Punkte-Prüfakte als Zwischenstand. Verwende es nie als Endzustand der Chain.

## Abschluss ausgeben

Ein erfolgreicher Lauf endet mit `dossier_freigabereit`, einem bestandenen `review/abschlusspruefung.md` und einem unausgefüllten `review/freigabeprotokoll.md`. Stelle dies nicht als rechtswirksame Freigabe dar. Diese bleibt einem namentlichen Menschen vorbehalten.
