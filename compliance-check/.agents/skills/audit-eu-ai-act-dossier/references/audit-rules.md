# Regeln für die Abschlussprüfung

## Prüfbereiche

1. **Identität:** Assessment, Systemname, Systemversion und Use Cases stimmen in Zustand, Prüfakte, Dokumentenplan und allen Dossierdokumenten überein.
2. **Einstufung:** Produktpfad und Anhang-III-Pfad sind getrennt, Rollen sind je Akteur belegt, Art. 6 Abs. 3 und Art. 50 wurden richtig verzweigt.
3. **Pflichtumfang:** Alle nach der Dokumentenmatrix anwendbaren Anforderungen sind instanziiert; keine Pflicht wurde durch unbegründete Nichtanwendbarkeit entfernt.
4. **Dokumentinhalt:** Dokumente enthalten die gesetzlichen Mindestinhalte und passen zur gültigen Version.
5. **Evidenz:** Tatsachen beruhen auf akzeptierter, versionsbezogener Evidenz. KI-Entwürfe und bloße Selbstauskünfte ohne Verantwortlichen sind kein ausreichender Nachweis.
6. **Konsistenz:** Zweck, Leistungsangaben, Grenzen, Nutzerinformationen und technische Dokumentation widersprechen sich nicht.
7. **Lebenszyklus:** Änderungen, Marktbeobachtung, Korrekturmaßnahmen und Vorfälle sind bei anwendbarem Hochrisikopfad operationalisiert.
8. **Rechtsstand:** verwendete Vorschriften wurden am Audittag amtlich geprüft; Entwürfe und politische Einigungen sind getrennt.

## Befundklassen

- `critical`: verbotene Praxis, falscher Risikopfad, fehlendes gesetzliches Pflichtdokument, unbelegte Abschlussbehauptung, fehlgeschlagene Konformitätsbewertung oder nicht beherrschter wesentlicher Widerspruch.
- `major`: wesentlicher Inhalts- oder Evidenzmangel, der vor Freigabereife behoben werden muss.
- `minor`: formaler Mangel ohne Einfluss auf Einstufung oder Pflichterfüllung; auch dieser ist vor dem Abschluss zu schließen.

## Statusregeln

- `draft` ist niemals abschlussfähig.
- `reviewed` verlangt benannten Reviewer und dokumentierte Inhaltsprüfung.
- `approved` verlangt die intern zuständige Freigabe.
- `external` verlangt Aussteller, Datum, Geltungsbereich und Versionsbezug.
- `not_applicable` verlangt konkrete Tatsachen und Rechtsgrund, nicht nur „nicht relevant“.
- `verified` verlangt mindestens ein geprüftes Dokument und einen akzeptierten Tatsachennachweis.

## Abschlussbericht

Der Bericht enthält Prüfdatum, Prüfer, Systemversion, geprüfte Quellen, Umfang, Befunde, geschlossene Befunde, Restunsicherheit und Ergebnis. Er verwendet verständliche Sprache; interne Maschinenstatus dürfen in einer technischen Anlage stehen.

