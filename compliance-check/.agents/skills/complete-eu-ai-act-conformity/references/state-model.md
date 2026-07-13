# Zustandsmodell für `dossier-state.json`

## Kontrollierte Werte

Gesamtzustand:

`intake`, `classification_pending`, `evidence_pending`, `drafting`, `validation_failed`, `dossier_freigabereit`, `nicht_freigabefaehig`

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

## Mindeststruktur

```json
{
  "schemaVersion": "1.0.0",
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

## Abschlussinvarianten

Für `dossier_freigabereit` müssen alle folgenden Bedingungen erfüllt sein:

- jeder Use Case besitzt Zweckbestimmung, mindestens eine Rolle, endgültige Klassifizierung und einen geschlossenen Risikopfad;
- alle durch Risikopfad, Rollen und Routing-Flags bestimmten Anforderungen der Dokumentenmatrix sind instanziiert;
- jede Anforderung ist `verified` oder `not_applicable`;
- jede Nichtanwendbarkeit hat eine substanzielle Begründung;
- jedes referenzierte Dokument existiert, hat Version und Owner und ist `reviewed`, `approved` oder `external`;
- jede verifizierte tatsachenabhängige Anforderung verweist auf mindestens einen akzeptierten Nachweis;
- kein akzeptierter Nachweis hat Quellentyp `ai_draft`;
- Rechtsstand wurde am Tag des Abschlussaudits in amtlichen EU-Quellen geprüft;
- Review ist `passed`, Konsistenzprüfung `passed`, Prüfer und Datum sind gesetzt und kritische Befunde sind null;
- Freigabeprotokoll existiert, kann aber für die spätere menschliche Freigabe unausgefüllt bleiben.

Für `nicht_freigabefaehig` müssen Reviewbericht und Abhilfeplan existieren und der entscheidende Verstoß belegt sein.
