---
name: prepare-eu-ai-act-dossier
description: Erstellt und vervollständigt aus einer abgeschlossenen EU-AI-Act-Einstufung den risikobasierten Dokumentenplan, die erforderlichen Compliance-Dokumente und das Evidenzregister. Verwenden zum Unterlagen erstellen, Nachweise anfordern oder prüfen, Dossier fortsetzen und offene AI-Act-Pflichten schließen. Entwürfe werden nie als Evidenz behandelt; externe Zertifikate oder Produktentscheidungen werden nicht erfunden.
---

# Anwendbares EU-AI-Act-Dossier erstellen

Erzeuge nur anwendbare Dokumente, aber schließe jedes geöffnete Pflichtenpaket vollständig.

## Ressourcen laden

1. Lies `references/dossier-matrix.md` vollständig.
2. Lies `assets/document-templates.md` vor dem Erzeugen von Dokumenten.
3. Lies `../complete-eu-ai-act-conformity/references/state-model.md` und den aktuellen `dossier-state.json`.
4. Lies Prüfakte, Bewertung und alle eingereichten Evidenzdateien, auf die du dich stützt.
5. Leite die Anforderungsliste vollständig aus Risikopfad, Rollen, Transparenzmerkmalen und der Dokumentenmatrix ab. Dokumentiere für jedes geöffnete und nicht geöffnete Paket die Begründung.

## Pflichten instanziieren

1. Instanziiere das Basispaket immer.
2. Öffne Transparenz, Art. 6 Abs. 3, Hochrisiko-Anbieter, Betreiber, Konformität, Lebenszyklus und Wirtschaftsakteure nur nach den Bedingungen der Matrix.
3. Öffne beim Produktpfad die externen Produkt-Gates. Ersetze MDR- oder sonstige sektorale Entscheidungen nicht durch eigene Behauptungen.
4. Markiere nicht geöffnete Anforderungen nur dann `not_applicable`, wenn die Begründung Tatsachen und Rechtsgrund nennt.
5. Gleiche die erzeugte Liste ein zweites Mal gegen jede Routingregel der Matrix ab und erzeuge anschließend `dokumentenplan.md` und `evidenzregister.md` mit stabilen IDs.

## Dokumente entwerfen

- Verwende belegte Angaben und verlinke Evidenz unmittelbar.
- Kennzeichne unbekannte Inhalte als offene Eingabe, nicht als Platzhalterbehauptung.
- Setze neu erzeugte Dokumente auf `drafted` und den Dokumentstatus auf `draft`.
- Führe Version, Systemversion, Owner, Reviewer, Quellen und Änderungsverlauf im Dokumentkopf.
- Erzeuge keine Konformitätserklärung, CE- oder Registrierungsbestätigung als angeblich abgeschlossen. Ein unausgefüllter Entwurf darf nur `draft` sein.

## Evidenz anfordern und prüfen

1. Formuliere für jede Lücke genaues Dokument, Aussteller, Systemversion, Mindestinhalt und akzeptierte Form.
2. Setze die Anforderung auf `requested` und den Gesamtzustand auf `evidence_pending`.
3. Prüfe eingereichte Evidenz auf Authentizitätsmerkmale, Geltungsbereich, Aktualität, Systemversionsbezug und Widersprüche.
4. Setze Evidenz auf `accepted` oder `rejected`; begründe Ablehnungen.
5. Setze eine Anforderung erst auf `evidenced`, wenn alle erforderlichen Belege akzeptiert wurden.
6. Setze sie erst nach inhaltlicher Prüfung des zugehörigen Dokuments auf `verified`.

## Übergabe

Wenn keine bekannte Lücke verbleibt, setze den Vorgang auf `drafting` und übergib an `$audit-eu-ai-act-dossier`. Setze niemals selbst `dossier_freigabereit`.
