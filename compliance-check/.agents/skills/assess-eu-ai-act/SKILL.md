---
name: assess-eu-ai-act
description: Erhebt interaktiv den Sachverhalt einer geplanten, entwickelten oder eingesetzten Anwendung und bestimmt nach dem EU AI Act Use Cases, KI-System-Eigenschaft, Anwendungsbereich, verbotene Praktiken, Rollen, Hochrisikopfad und Art.-50-Transparenz. Verwenden für Ersteinstufung oder Neueinstufung innerhalb einer EU-AI-Act-Dossier-Chain. Erzeugt keine Freigabe und ersetzt nicht die Dossiererstellung oder Abschlussprüfung.
---

# Anwendung nach dem EU AI Act einstufen

Erzeuge eine belastbare Pflichtenroute, keinen abschließenden Konformitätsnachweis.

## Ressourcen laden

1. Lies `../../../KI-Compliance-Checkliste.md` vollständig.
2. Lies `references/interview.md` vor Fragen vollständig.
3. Lies `references/legal-routing.md` vor der Einstufung vollständig.
4. Lies `assets/output-template.md` vor dem Bericht.
5. Wenn der Skill über den Orchestrator läuft, lies dessen `references/state-model.md` und aktualisiere `dossier-state.json`.

## Interview führen

1. Spiegele das vorläufige Verständnis in einem Satz.
2. Stelle pro Runde zwei bis vier adaptive Fragen.
3. Erlaube „weiß ich nicht“ und übersetze es in eine konkrete Evidenzanforderung.
4. Wiederhole keine belegten Angaben.
5. Trenne Use Cases bei abweichendem Zweck, Betroffenenkreis, Entscheidung, Autonomie oder Fehlerfolge.
6. Beende die Einstufung erst, wenn der Mindestinformationssatz vorliegt oder fehlende Tatsachen ausdrücklich als offene Nachweise erfasst sind.

## Rechtsstand verifizieren

- Nutze ausschließlich amtliche EU-Quellen und beginne beim [AI Act Explorer](https://ai-act-service-desk.ec.europa.eu/de/ai-act-explorer).
- Öffne jeden verwendeten Artikel oder Anhang direkt.
- Prüfe den Umsetzungszeitplan und trenne geltendes Recht, verabschiedete Änderungen, Vorschläge und politische Einigungen.
- Speichere Prüftag und Quellen. Ohne Internet darf `classificationFinal` nicht auf `true` gesetzt werden.

## Einstufen

1. Prüfe Art. 2 und 3, danach Art. 4 und 5.
2. Bestimme Anbieter, Betreiber, Bevollmächtigte, Einführer, Händler und mögliche Rollenwechsel.
3. Prüfe Art. 6 Abs. 1 mit beiden Produktpfadbedingungen.
4. Prüfe Art. 6 Abs. 2 anhand des konkreten Anhang-III-Eintrags.
5. Prüfe Art. 6 Abs. 3 nur bei zuvor festgestelltem Anhang-III-Tatbestand; Profiling schließt den Filter aus.
6. Prüfe Art. 50 unabhängig von der Risikoklasse.
7. Arbeite die 25 Stamm-IDs ab und bewahre deren Spalten und Werte.
8. Setze `classificationFinal` nur, wenn Rollen und Risikopfad nicht von einer offenen Tatsachen- oder externen Produktentscheidung abhängen.

## Ergebnisse schreiben

- Erzeuge oder aktualisiere `pruefakte.md` und `bewertung.md`.
- Schreibe in `dossier-state.json` Use Cases, Rollen, Risikopfad, Rechtsstand und erste Anforderungen.
- Setze den Gesamtzustand bei offener Einstufung auf `classification_pending`, sonst auf `drafting`.
- Übergib anschließend an `$prepare-eu-ai-act-dossier`; bezeichne die Einstufung nie als vollständige Konformitätsprüfung.

## Grenzen

Leite Hochrisiko nicht allein aus Gesundheitsdaten, Krankenhausnutzung, Kritikalität oder Schadenspotenzial ab. Führe keine eigenständige MDR-, DSGVO- oder Sicherheitsprüfung durch. Verlange deren Ergebnis nur als externen Nachweis, wenn es den AI-Act-Pfad bestimmt.

