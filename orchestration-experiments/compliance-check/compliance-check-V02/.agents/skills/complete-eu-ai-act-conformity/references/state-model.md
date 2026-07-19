# Zustandsmodell für `dossier-state.json`

`dossier-state.json` ist die einzige maschinelle Quelle der Wahrheit. `pruefakte.md`, `bewertung.md`, `dokumentenplan.md` und `evidenzregister.md` sind daraus abgeleitete Projektionen. Bei Abweichungen gilt der validierte JSON-Zustand.

## Version und Dossiergrenze

- Schreibe neue oder materiell fortgeschriebene Vorgänge mit `schemaVersion: "1.1.0"`.
- Lies `1.0.0` weiterhin, ergänze fehlende 1.1-Felder aber nicht durch Annahmen.
- Führe pro Use-Case-Ordner genau eine Zustandsdatei und darin genau ein Element in `useCases`.
- Gruppiere mehrere Use Cases derselben Anwendung ausschließlich über `applicationId`.
- Verwende innerhalb eines Dossiers eindeutige IDs und nur relative Pfade ohne `..`, Laufwerksbuchstaben oder führenden Slash.
- Nutze `dossier-state.schema.json` als Vertrag und `../scripts/validate_dossier_state.py` zur deterministischen Prüfung.

## Kontrollierte Werte

Gesamtzustand:

`intake`, `classification_pending`, `drafting`, `evidence_pending`, `audit_pending`, `validation_failed`, `dossier_freigabereit`, `nicht_freigabefaehig`

Anforderungsstatus:

`open`, `requested`, `drafted`, `evidenced`, `verified`, `not_applicable`

Dokumentstatus:

`draft`, `reviewed`, `approved`, `external`

Evidenzstatus:

`submitted`, `accepted`, `rejected`

Evidenzquellen:

`original_document`, `system_record`, `test_record`, `signed_statement`, `external_decision`, `official_register`, `ai_draft`

Risikopfade:

`open`, `no_ai_system`, `prohibited`, `not_high_risk`, `annex_iii_exception`, `annex_iii_high_risk`, `annex_i_high_risk`

Rollen:

`provider`, `deployer`, `authorized_representative`, `importer`, `distributor`

Stammantworten:

`offen`, `ja`, `nein`, `nicht_anwendbar`, `eskalieren`

Stammstatus:

`nicht_begonnen`, `in_pruefung`, `nachweis_fehlt`, `erledigt`, `eskaliert`

## Mindeststruktur

```json
{
  "schemaVersion": "1.1.0",
  "assessmentId": "ASSESSMENT-YYYY-NNN",
  "applicationId": "APP-NN",
  "systemName": "",
  "systemVersion": "",
  "state": "intake",
  "updatedAt": "YYYY-MM-DD",
  "legalStatus": {
    "checkedAt": "",
    "sources": [],
    "consolidatedLawSeparatedFromProposals": false
  },
  "useCases": [
    {
      "id": "UC-01",
      "name": "",
      "intendedPurpose": "",
      "roles": [],
      "riskRoute": "open",
      "classificationFinal": false,
      "routingFlags": {
        "productGateOpen": false,
        "interactionTransparency": false,
        "syntheticContent": false,
        "deepfakeDisclosure": false,
        "publicInterestTextDisclosure": false,
        "friaRequired": false,
        "explanationRequired": false
      }
    }
  ],
  "checklistItems": [
    {
      "id": "BAS-01",
      "answer": "offen",
      "status": "nicht_begonnen",
      "rationale": "",
      "evidenceLinks": [],
      "owner": "",
      "dueAt": "",
      "legalReferences": ["Art. 3"],
      "requirementIds": ["BAS-SYSTEM"]
    }
  ],
  "requirements": [
    {
      "id": "BAS-SYSTEM",
      "package": "base",
      "legalBasis": ["Art. 3"],
      "status": "open",
      "rationale": "",
      "owner": "",
      "dueAt": "",
      "documentIds": [],
      "evidenceIds": []
    }
  ],
  "documents": [
    {
      "id": "DOC-SYSTEM",
      "title": "System- und Zweckbestimmung",
      "path": "dossier/system-und-zweckbestimmung.md",
      "status": "draft",
      "version": "0.1",
      "owner": ""
    }
  ],
  "evidence": [
    {
      "id": "EVD-001",
      "title": "",
      "path": "evidence/datei.ext",
      "sourceType": "original_document",
      "status": "submitted",
      "issuer": "",
      "version": "",
      "date": "",
      "appliesToSystemVersion": ""
    }
  ],
  "review": {
    "reviewer": "",
    "completedAt": "",
    "result": "pending",
    "criticalFindings": 0,
    "consistencyCheck": "pending",
    "reportPath": "review/abschlusspruefung.md"
  },
  "release": {
    "status": "pending",
    "decider": "",
    "date": "",
    "protocolPath": "review/freigabeprotokoll.md"
  },
  "remediationPlanPath": ""
}
```

## Übergänge

1. `intake` → `classification_pending`, bis Tatsachengrundlage und Einstufung vollständig sind.
2. `classification_pending` → `drafting`, sobald genau ein Use Case endgültig klassifiziert ist.
3. `drafting` ↔ `evidence_pending`; Dokumententwürfe dürfen vor vollständiger Evidenz entstehen, unbelegte Tatsachen bleiben offen.
4. `drafting` → `audit_pending`, wenn alle Anforderungen `verified` oder begründet `not_applicable` und Dokumente mindestens `reviewed` sind.
5. `audit_pending` → Endzustand oder `validation_failed`.
6. `validation_failed` → `drafting`, `evidence_pending` oder erneut `audit_pending`, abhängig vom Befund.

## Abschlussinvarianten

Für `dossier_freigabereit` müssen alle folgenden Bedingungen erfüllt sein:

- genau ein Use Case besitzt Zweckbestimmung, mindestens eine Rolle, endgültige Klassifizierung und einen geschlossenen Risikopfad;
- alle 25 Stamm-IDs sind genau einmal vorhanden und jede granulare Anforderung ist mindestens einer Stamm-ID zugeordnet;
- alle durch Risikopfad, Rollen und Routing-Flags bestimmten Anforderungen der Dokumentenmatrix sind instanziiert;
- jede Anforderung ist `verified` oder `not_applicable`;
- jede Nichtanwendbarkeit hat eine substanzielle Begründung;
- jedes referenzierte Dokument existiert, hat Version und Owner und ist `reviewed`, `approved` oder `external`;
- jede verifizierte tatsachenabhängige Anforderung verweist auf mindestens einen akzeptierten Nachweis;
- kein akzeptierter Nachweis hat Quellentyp `ai_draft`;
- Rechtsstand wurde am Tag des Abschlussaudits in amtlichen EU-Quellen geprüft;
- Review ist `passed`, Konsistenzprüfung `passed`, Prüfer und Datum sind gesetzt und kritische Befunde sind null;
- Freigabeprotokoll existiert; `release.status` bleibt bis zur namentlichen menschlichen Entscheidung `pending`.

Für `nicht_freigabefaehig` müssen Reviewbericht und Abhilfeplan existieren und der entscheidende Verstoß belegt sein.
