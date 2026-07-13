# Ablauf der Skill-Chain

## 1. Neuer Vorgang

1. Anwendung und eigenständige Use Cases bestimmen.
2. Assessment- und Anwendungs-Slug bilden.
3. `assessments/<anwendungs-slug>/<use-case-slug>/` anlegen.
4. `dossier-state.json` nach `state-model.md` mit Zustand `intake` erzeugen.
5. Einstufungsmodul durchführen.

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
| Evidenz | Anforderungen instanziiert | jede anwendbare Anforderung belegt oder begründet nicht anwendbar |
| Dokumentation | belastbare Tatsachen vorhanden | erforderliche Dokumente mindestens geprüft, nicht nur entworfen |
| Audit | keine bekannte Evidenzlücke | vollständiger KI-Review aller Abschlussinvarianten ohne kritischen Befund |
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

Mehrere Use Cases erhalten je eine eigene Prüfakte und einen eigenen Zustand. Eine optionale Anwendungsebene `uebersicht.md` fasst nur zusammen und ersetzt kein Use-Case-Dossier.

## 5. Nachweisregeln

- Akzeptiere technische oder organisatorische Tatsachen nur aus Originalunterlagen, Systemaufzeichnungen, Testergebnissen, unterschriebenen Erklärungen oder nachvollziehbaren externen Entscheidungen.
- Kennzeichne KI-generierte Texte als `ai_draft`; sie sind keine Evidenz.
- Verweise auf amtliche Rechtsquellen sind Rechtsgrundlagen, keine Belege für Produkteigenschaften.
- Prüfe Datei, Version, Aussteller, Datum, Geltungsbereich und Bezug zur bewerteten Systemversion.
- Lege keine Kopien sensibler Originale an, wenn ein kontrollierter Link genügt.
