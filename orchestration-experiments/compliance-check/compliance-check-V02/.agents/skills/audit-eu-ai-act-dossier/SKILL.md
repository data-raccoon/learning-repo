---
name: audit-eu-ai-act-dossier
description: Prüft ein vorhandenes EU-AI-Act-Dossier fachlich und maschinell auf Vollständigkeit, konsistente Einstufung, echte Evidenz, aktuelle amtliche Rechtsquellen und Abschlussreife. Explizit für Abschlussprüfung, Dossier-Audit oder erneute Prüfung nach behobenen Befunden verwenden; vollständige Vorgänge über complete-eu-ai-act-conformity steuern. Nur dieser Skill darf einen Dossier-Endzustand setzen.
---

# EU-AI-Act-Dossier abschließend auditieren

Führe einen adversarialen Review durch. Ein vorhandenes Dokument beweist nicht, dass sein Inhalt richtig oder vollständig ist.

## Ressourcen laden

1. Lies `references/audit-rules.md` vollständig.
2. Lies `../complete-eu-ai-act-conformity/references/state-model.md`.
3. Lies `../prepare-eu-ai-act-dossier/references/dossier-matrix.md`.
4. Lies `../prepare-eu-ai-act-dossier/references/checklist-mapping.md`.
5. Lies den vollständigen Vorgangsordner einschließlich Originalnachweisen.
6. Führe `../complete-eu-ai-act-conformity/scripts/validate_dossier_state.py` gegen den aktuellen Zustand aus. Behandle jeden Fehler als mindestens `major` und setze keinen Endzustand.

## Audit durchführen

1. Prüfe erneut, ob Zweck, Systemversion, Rollen und Risikopfad noch zu allen Dokumenten passen.
2. Prüfe jede instanziierte Anforderung gegen Rechtsgrund, Dokumentinhalt und Evidenz.
3. Öffne am Audittag die verwendeten amtlichen EU-Quellen erneut. Trenne konsolidiertes Recht von Vorschlägen und politischen Einigungen.
4. Prüfe alle Links und lokalen Evidenzpfade.
5. Gleiche Risikopfad, Rollen und sämtliche Routing-Flags erneut gegen jede Zeile der Dokumentenmatrix ab. Prüfe, dass kein erforderliches Paket oder Dokument fehlt.
6. Prüfe die Abschlussinvarianten aus `state-model.md` einzeln und dokumentiere das Ergebnis jeder Invariante.
7. Dokumentiere Befunde in `review/abschlusspruefung.md` mit Schweregrad, Anforderung, Evidenz, Abhilfe und Owner.

## Ergebnis setzen

- Bei mindestens einem kritischen Befund: setze `validation_failed`, sofern Abhilfe möglich ist.
- Bei einer belegten verbotenen Praxis oder einem dokumentiert nicht behebbaren Verstoß: erzeuge `review/abhilfeplan.md` und setze `nicht_freigabefaehig`.
- Nur wenn alle Abschlussinvarianten erfüllt sind: setze `dossier_freigabereit`.
- Lasse `release.status` auf `pending`, bis ein namentlicher Mensch entscheidet.
- Gib im orchestrierten Betrieb nach Zustandsänderung die Kontrolle an den Orchestrator zurück.

Lies Zustand, Dokumentenmatrix, Evidenzregister und Abschlussbericht nach jeder Statusänderung erneut. Setze einen Endzustand nur, wenn der erneute vollständige Abgleich dasselbe Ergebnis liefert.
