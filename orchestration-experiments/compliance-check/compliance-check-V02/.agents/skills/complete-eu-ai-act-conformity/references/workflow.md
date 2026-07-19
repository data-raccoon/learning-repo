# Ablauf der Skill-Chain

## 1. Neuer Vorgang

1. Anwendung und eigenständige Use Cases bestimmen.
2. Je Use Case Assessment-ID und Slugs bilden.
3. Je Use Case `assessments/<anwendungs-slug>/<use-case-slug>/` anlegen.
4. Dort genau eine `dossier-state.json` nach Schema 1.1 mit Zustand `intake` und genau einem `useCases`-Eintrag erzeugen.
5. Einstufungsmodul je Dossier durchführen; über `applicationId` zusammengehörige Use Cases gruppieren.

## 2. Bestehender Vorgang

1. Assessment-ID und Systemversion abgleichen.
2. Bei geänderter Zweckbestimmung, Version, Rolle oder Systemgrenze die betroffenen verifizierten Anforderungen wieder auf `open` setzen.
3. Beim frühesten unvollständigen Gate fortsetzen.
4. Neue Nachweise nie stillschweigend als Ersatz für widersprüchliche alte Nachweise verwenden; Konflikt dokumentieren und auditieren.

## 3. Gates

| Gate | Eintritt | Ausgang |
|---|---|---|
| Einstufung | Mindestangaben vorhanden | Use Cases, Rollen, Risikopfad und Transparenz abschließend dokumentiert |
| Dokumentenplan | Einstufung abgeschlossen | alle anwendbaren Anforderungen aus der Dokumentenmatrix instanziiert |
| Dokumentation und Evidenz | Einstufung abgeschlossen | Anforderungen instanziiert; Dokumente und Belege iterativ bis zur Prüfbarkeit vervollständigt |
| Audit | Zustand `audit_pending` | vollständiger Review aller Abschlussinvarianten ohne offenen Befund |
| Abschluss | Audit bestanden | `dossier_freigabereit` oder `nicht_freigabefaehig` |

## 4. Dateistruktur

```text
assessments/<anwendung>/<use-case>/
├── dossier-state.json
├── pruefakte.md
├── bewertung.md
├── dokumentenplan.md
├── evidenzregister.md
├── evidence/
├── dossier/
└── review/
    ├── abschlusspruefung.md
    ├── freigabeprotokoll.md
    └── abhilfeplan.md          # nur bei negativem Endzustand
```

Mehrere Use Cases erhalten je einen eigenen Ordner, eine eigene Prüfakte und einen eigenen Zustand mit genau einem `useCases`-Eintrag. Eine optionale Anwendungsebene `uebersicht.md` fasst nur zusammen und ersetzt kein Use-Case-Dossier.

## 5. Schreibreihenfolge

1. Zustand und stabile IDs in `dossier-state.json` ändern.
2. Zustand validieren.
3. `pruefakte.md`, `bewertung.md`, `dokumentenplan.md` und `evidenzregister.md` aus dem Zustand aktualisieren.
4. Bei Widerspruch den Zustand nicht aus einer Projektion überschreiben, sondern die Ursache prüfen.

## 6. Nachweisregeln

- Akzeptiere technische oder organisatorische Tatsachen nur aus Originalunterlagen, Systemaufzeichnungen, Testergebnissen, unterschriebenen Erklärungen oder nachvollziehbaren externen Entscheidungen.
- Kennzeichne KI-generierte Texte als `ai_draft`; sie sind keine Evidenz.
- Verweise auf amtliche Rechtsquellen sind Rechtsgrundlagen, keine Belege für Produkteigenschaften.
- Prüfe Datei, Version, Aussteller, Datum, Geltungsbereich und Bezug zur bewerteten Systemversion.
- Lege keine Kopien sensibler Originale an, wenn ein kontrollierter Link genügt.
