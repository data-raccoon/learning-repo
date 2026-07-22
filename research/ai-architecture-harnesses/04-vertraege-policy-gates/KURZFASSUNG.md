# Verträge und Policy-Gates – Kurzfassung

## Kernaussage

Modellausgaben sind untrusted Vorschläge. Der robuste Kontrollpfad lautet: Modellvorschlag → lokale Schema-Prüfung → deterministische semantische Validatoren → Policy-Entscheidung → Freigabe/Commit → Tool-Adapter → Audit. Constrained Decoding verbessert die syntaktische Zuverlässigkeit, ist aber weder Wahrheits- noch Sicherheitsbeweis. Eine Policy-Entscheidung wirkt erst, wenn ein nicht umgehbarer Policy Enforcement Point (PEP) sie durchsetzt.

## Garantiert

Ein enges, versioniertes Schema mit lokalem Validator kann garantieren, dass eine vollständige Nachricht die kodierten Strukturregeln erfüllt. Constrained Decoding kann unter den dokumentierten Produkt- und Schemaannahmen syntaktische Konformität einer normal beendeten Ausgabe erzwingen. Reine Validatoren können explizit kodierte Invarianten prüfen. Ein fail-closed PEP kann verhindern, dass ohne positives Policy-Ergebnis über den erfassten Pfad ein Commit erfolgt. Signierte Provenienz kann unter Kryptografie- und Build-Annahmen die Artefaktherkunft belegen.

## Garantiert nicht

Schema-Konformität beweist keine Wahrheit, Aktualität, Berechtigung oder ungefährliche Wirkung. OPA trifft eine Entscheidung, erzwingt sie aber nicht selbst. Ein `allow` kann auf unvollständiger Policy oder manipulierten Attributen beruhen. TOCTOU kann Prüfung und Wirkung auseinanderziehen. Eval-Gates liefern nur statistische Evidenz für die getestete Verteilung; Provenienz beweist nicht die fachliche Korrektheit eines Artefakts.

## Einsatzkriterien

Schema plus lokale Validatoren reichen bei kleinen, stabilen Regeln. Ein externer Policy Decision Point wie OPA lohnt sich, wenn mehrere Dienste dieselben versionierten und auditierbaren Regeln brauchen. Kritische Pfade müssen `deny`, `undefined`, Timeout und Fehler als Ablehnung behandeln. Prüfung und Commit müssen atomar sein oder unmittelbar vor der Wirkung erneut gegen autoritativen Zustand erfolgen. Bei irreversiblen, rechtlich relevanten oder nicht vollständig formalisierbaren Wirkungen ist eine an den exakten Payload gebundene menschliche Freigabe nötig.

## Quellen

- [JSON Schema: Grundlagen](https://json-schema.org/understanding-json-schema/basics)
- [OpenAI: Structured Outputs](https://openai.com/index/introducing-structured-outputs-in-the-api/)
- [Open Policy Agent: Dokumentation](https://www.openpolicyagent.org/docs)
- [OPA: Operational Readiness and Failure Modes](https://www.openpolicyagent.org/docs/operations)
- [Kubernetes: Admission Controllers](https://kubernetes.io/docs/reference/access-authn-authz/admission-controllers/)
- [SLSA v1.0: Security Levels](https://slsa.dev/spec/v1.0/levels)
