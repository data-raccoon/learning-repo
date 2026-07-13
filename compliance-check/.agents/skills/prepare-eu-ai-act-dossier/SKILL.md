---
name: prepare-eu-ai-act-dossier
description: Erstellt oder vervollständigt aus einer abgeschlossenen EU-AI-Act-Einstufung den risikobasierten Dokumentenplan, Compliance-Dokumente und das Evidenzregister eines vorhandenen Dossiers. Explizit für phasenbezogene Dokument- oder Evidenzarbeit verwenden; vollständige oder fortzusetzende Konformitätsvorgänge über complete-eu-ai-act-conformity steuern. Entwürfe werden nie als Evidenz behandelt; externe Entscheidungen werden nicht erfunden.
---

# Anwendbares EU-AI-Act-Dossier erstellen

Erzeuge nur anwendbare Dokumente, aber schließe jedes geöffnete Pflichtenpaket vollständig.

## Ressourcen laden

1. Lies `references/dossier-matrix.md` vollständig.
2. Lies `references/checklist-mapping.md` vollständig.
3. Lies `assets/document-templates.md` vor dem Erzeugen von Dokumenten.
4. Lies `../complete-eu-ai-act-conformity/references/state-model.md`, validiere den aktuellen `dossier-state.json` und bearbeite nur ein Dossier mit genau einem Use Case.
5. Lies Prüfakte, Bewertung und alle eingereichten Evidenzdateien, auf die du dich stützt.
6. Leite die Anforderungsliste vollständig aus Risikopfad, Rollen, Transparenzmerkmalen und der Dokumentenmatrix ab. Ordne jede Anforderung nach `checklist-mapping.md` mindestens einer Stamm-ID zu.

## Pflichten instanziieren

1. Instanziiere das Basispaket immer.
2. Öffne Transparenz, Art. 6 Abs. 3, Hochrisiko-Anbieter, Betreiber, Konformität, Lebenszyklus und Wirtschaftsakteure nur nach den Bedingungen der Matrix.
3. Öffne beim Produktpfad die externen Produkt-Gates. Ersetze MDR- oder sonstige sektorale Entscheidungen nicht durch eigene Behauptungen.
4. Markiere nicht geöffnete Anforderungen nur dann `not_applicable`, wenn die Begründung Tatsachen und Rechtsgrund nennt.
5. Gleiche die erzeugte Liste ein zweites Mal gegen jede Routingregel der Matrix ab. Aktualisiere zuerst `dossier-state.json` und leite anschließend `dokumentenplan.md` und `evidenzregister.md` mit stabilen IDs daraus ab.

## Dokumente entwerfen

- Verwende belegte Angaben und verlinke Evidenz unmittelbar.
- Kennzeichne unbekannte Inhalte als offene Eingabe, nicht als Platzhalterbehauptung.
- Setze neu erzeugte Dokumente auf `drafted` und den Dokumentstatus auf `draft`.
- Führe Version, Systemversion, Owner, Reviewer, Quellen und Änderungsverlauf im Dokumentkopf.
- Erzeuge keine Konformitätserklärung, CE- oder Registrierungsbestätigung als angeblich abgeschlossen. Ein unausgefüllter Entwurf darf nur `draft` sein.

## Evidenz anfordern und prüfen

1. Formuliere für jede Lücke genaues Dokument, Aussteller, Systemversion, Mindestinhalt und akzeptierte Form.
2. Setze die Anforderung auf `requested`. Setze den Gesamtzustand auf `evidence_pending`, sobald fehlende Evidenz die weitere Prüfung blockiert; Dokumententwürfe dürfen zuvor oder parallel entstehen.
3. Prüfe eingereichte Evidenz auf Authentizitätsmerkmale, Geltungsbereich, Aktualität, Systemversionsbezug und Widersprüche.
4. Setze Evidenz auf `accepted` oder `rejected`; begründe Ablehnungen.
5. Setze eine Anforderung erst auf `evidenced`, wenn alle erforderlichen Belege akzeptiert wurden.
6. Setze sie erst nach inhaltlicher Prüfung des zugehörigen Dokuments auf `verified`.

## Übergabe

Wenn Anforderungen belegt oder begründet nicht anwendbar und die zugehörigen Dokumente mindestens geprüft sind, setze `audit_pending`. Gib im orchestrierten Betrieb die Kontrolle an den Orchestrator zurück; nenne bei isolierter Nutzung `$audit-eu-ai-act-dossier` als nächsten Schritt. Setze niemals selbst einen Endzustand.
