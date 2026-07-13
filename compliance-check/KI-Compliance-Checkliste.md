---
schema_id: "eu-ai-act-core-checklist"
schema_version: "2.1.0"
template_version: "2.1.0"
language: "de"
assessment:
  assessment_id: "ASSESSMENT-YYYY-NNN"
  application_id: "APP-NN"
  use_case_id: "APP-NN-UC-NN"
  system_name: ""
  system_version: ""
  intended_purpose: ""
  lifecycle_phase: "planung"
  organisation_role: "offen"
  risk_result: "offen"
  owner: ""
  reviewer: ""
  started_at: ""
  updated_at: ""
  due_at: ""
  legal_status_checked_at: ""
  final_decision: "weitere_pruefung"
allowed_values:
  answer:
    - "offen"
    - "ja"
    - "nein"
    - "nicht_anwendbar"
    - "eskalieren"
  status:
    - "nicht_begonnen"
    - "in_pruefung"
    - "nachweis_fehlt"
    - "erledigt"
    - "eskaliert"
  role:
    - "offen"
    - "anbieter"
    - "betreiber"
    - "anbieter_und_betreiber"
    - "sonstige"
  risk_result:
    - "offen"
    - "kein_ki_system"
    - "verboten"
    - "nicht_hochrisiko"
    - "hochrisiko_anhang_i"
    - "hochrisiko_anhang_iii"
  final_decision:
    - "freigegeben"
    - "freigegeben_mit_auflagen"
    - "nicht_freigegeben"
    - "weitere_pruefung"
legal_source:
  regulation: "Verordnung (EU) 2024/1689"
  explorer: "https://ai-act-service-desk.ec.europa.eu/de/ai-act-explorer"
---

# Organisationsneutrale EU-AI-Act-Checkliste

> **Arbeitsinstrument, keine Rechtsberatung.** Diese Checkliste enthält den organisationsneutralen Kern für Erstbewertung und Compliance-Tracking. Sie ist für jeden eigenständigen Use Case separat auszufüllen. Sektorale Produkt-, Datenschutz- oder Sicherheitsentscheidungen sind nur als externe Nachweise einzubeziehen, wenn sie den AI-Act-Pfad bestimmen.

## 1. Anwendung

1. Für jede Anwendung und jede fachlich eigenständige KI-Funktion eine eigene Kopie dieser Checkliste verwenden.
2. Nur die im YAML-Block definierten Antwort- und Statuswerte verwenden.
3. `nein`, `nicht_anwendbar` und `eskalieren` immer begründen.
4. Fehlende Informationen nicht durch Annahmen ersetzen: Antwort `offen`, Status `nachweis_fehlt`.
5. Anbieter- und Betreiberpflichten nur öffnen, wenn die jeweilige Rolle festgestellt wurde.
6. Eine KI-gestützte Vorbefüllung darf keine endgültige Einstufung oder Freigabe ohne menschlichen Prüfvermerk setzen.

## 2. Kopfdaten

| Feld | Eintrag |
|---|---|
| Assessment-ID |  |
| Anwendung / Use Case |  |
| Systemname und Version |  |
| Zweckbestimmung |  |
| Lebenszyklusphase |  |
| Fachlich verantwortlich |  |
| Technisch verantwortlich |  |
| Anbieter |  |
| Betreiber |  |
| Beginn / Fälligkeit |  |
| geprüfter Rechtsstand |  |

## 3. Gesetzliche Mindestprüfung

### A. Anwendungsbereich, Verbote und Rolle

| ID | Prüffrage / Tätigkeit | Antwort | Status | Begründung | Nachweis / Link | Verantwortlich | Fällig | AI-Act-Referenz |
|---|---|---|---|---|---|---|---|---|
| `BAS-01` | Zweckbestimmung, Systemversion, Nutzer, betroffene Personen, Ein- und Ausgaben, ausgelöste Aktionen sowie Systemgrenze dokumentieren. | `offen` | `nicht_begonnen` |  |  |  |  | [Art. 3](https://ai-act-service-desk.ec.europa.eu/de/ai-act/article-3), [Anhang IV](https://ai-act-service-desk.ec.europa.eu/de/ai-act/annex-4) |
| `BAS-02` | Prüfen und begründen, ob ein KI-System im Sinne des AI Act vorliegt und der AI Act räumlich und sachlich anwendbar ist. | `offen` | `nicht_begonnen` |  |  |  |  | [Art. 2](https://ai-act-service-desk.ec.europa.eu/de/ai-act/article-2), [Art. 3 Nr. 1](https://ai-act-service-desk.ec.europa.eu/de/ai-act/article-3) |
| `BAS-03` | Ausreichende KI-Kompetenz der Personen sicherstellen, die das System betreiben oder seine Nutzung verantworten. | `offen` | `nicht_begonnen` |  |  |  |  | [Art. 4](https://ai-act-service-desk.ec.europa.eu/de/ai-act/article-4) |
| `BAS-04` | Sämtliche verbotenen Praktiken gegen Zweckbestimmung, Funktionen und tatsächliche Nutzung prüfen; bei Betroffenheit Stop und Nichtfreigabe. | `offen` | `nicht_begonnen` |  |  |  |  | [Art. 5](https://ai-act-service-desk.ec.europa.eu/de/ai-act/article-5) |
| `ROL-01` | Rollen aller Beteiligten bestimmen; insbesondere prüfen, ob Eigenentwicklung, eigener Name, geänderte Zweckbestimmung oder wesentliche Änderung Anbieterpflichten der bewertenden Organisation auslösen. | `offen` | `nicht_begonnen` |  |  |  |  | [Art. 3](https://ai-act-service-desk.ec.europa.eu/de/ai-act/article-3), [Art. 25](https://ai-act-service-desk.ec.europa.eu/de/ai-act/article-25) |

### B. Risikoklassifizierung und Transparenz

| ID | Prüffrage / Tätigkeit | Antwort | Status | Begründung | Nachweis / Link | Verantwortlich | Fällig | AI-Act-Referenz |
|---|---|---|---|---|---|---|---|---|
| `CLS-01` | Prüfen, ob das System selbst ein Produkt oder Sicherheitsbauteil nach Anhang I ist und das Produkt einer Drittstellen-Konformitätsbewertung unterliegt. | `offen` | `nicht_begonnen` |  |  |  |  | [Art. 6 Abs. 1](https://ai-act-service-desk.ec.europa.eu/de/ai-act/article-6), [Anhang I](https://ai-act-service-desk.ec.europa.eu/de/ai-act/annex-1) |
| `CLS-02` | Sämtliche in Betracht kommenden Hochrisiko-Tatbestände des Anhangs III gegen die konkrete Zweckbestimmung prüfen. | `offen` | `nicht_begonnen` |  |  |  |  | [Art. 6 Abs. 2](https://ai-act-service-desk.ec.europa.eu/de/ai-act/article-6), [Anhang III](https://ai-act-service-desk.ec.europa.eu/de/ai-act/annex-3) |
| `CLS-03` | Falls Anhang III betroffen ist: Ausnahme nach Art. 6 Abs. 3 einschließlich Profiling-Ausschluss prüfen, begründen und gegebenenfalls registrieren. | `offen` | `nicht_begonnen` |  |  |  |  | [Art. 6 Abs. 3–4](https://ai-act-service-desk.ec.europa.eu/de/ai-act/article-6), [Art. 49 Abs. 2](https://ai-act-service-desk.ec.europa.eu/de/ai-act/article-49) |
| `CLS-04` | Risikoklasse mit Tatsachen, Rechtsgrundlage, Unsicherheiten und Prüfer dokumentieren. | `offen` | `nicht_begonnen` |  |  |  |  | [Art. 6](https://ai-act-service-desk.ec.europa.eu/de/ai-act/article-6) |
| `TRN-01` | Unabhängig von der Hochrisikoklasse prüfen und umsetzen, ob Menschen über KI-Interaktion oder künstlich erzeugte bzw. manipulierte Inhalte informiert werden müssen. | `offen` | `nicht_begonnen` |  |  |  |  | [Art. 50](https://ai-act-service-desk.ec.europa.eu/de/ai-act/article-50) |

### C. Mindestanforderungen bei Anbieterrolle für Hochrisiko-KI

Dieser Abschnitt ist nur anwendbar, wenn die bewertende Organisation Anbieter eines Hochrisiko-KI-Systems ist. Bei einem Fremdanbieter dienen die Punkte als Mindestliste der anzufordernden Anbieternachweise.

| ID | Prüffrage / Tätigkeit | Antwort | Status | Begründung | Nachweis / Link | Verantwortlich | Fällig | AI-Act-Referenz |
|---|---|---|---|---|---|---|---|---|
| `PRO-01` | Kontinuierliches Risikomanagement für bekannte und vorhersehbare Risiken, Fehlanwendungen, Maßnahmen, Tests und Restrisiken nachweisen. | `offen` | `nicht_begonnen` |  |  |  |  | [Art. 9](https://ai-act-service-desk.ec.europa.eu/de/ai-act/article-9) |
| `PRO-02` | Bei datenbasierten Modellen rechtmäßige Daten-Governance sowie Eignung, Relevanz, Repräsentativität und Fehlerkontrolle der Daten nachweisen. | `offen` | `nicht_begonnen` |  |  |  |  | [Art. 10](https://ai-act-service-desk.ec.europa.eu/de/ai-act/article-10) |
| `PRO-03` | Aktuelle technische Dokumentation, automatische Ereignisaufzeichnung und vollständige Betriebsanleitung bereitstellen. | `offen` | `nicht_begonnen` |  |  |  |  | [Art. 11](https://ai-act-service-desk.ec.europa.eu/de/ai-act/article-11), [Art. 12](https://ai-act-service-desk.ec.europa.eu/de/ai-act/article-12), [Art. 13](https://ai-act-service-desk.ec.europa.eu/de/ai-act/article-13), [Anhang IV](https://ai-act-service-desk.ec.europa.eu/de/ai-act/annex-4) |
| `PRO-04` | Wirksame menschliche Aufsicht sowie angemessene Genauigkeit, Robustheit und Cybersicherheit technisch ermöglichen und dokumentieren. | `offen` | `nicht_begonnen` |  |  |  |  | [Art. 14](https://ai-act-service-desk.ec.europa.eu/de/ai-act/article-14), [Art. 15](https://ai-act-service-desk.ec.europa.eu/de/ai-act/article-15) |
| `PRO-05` | Qualitätsmanagement betreiben und technische Dokumentation sowie kontrollierte Protokolle für die vorgeschriebenen Zeiträume aufbewahren. | `offen` | `nicht_begonnen` |  |  |  |  | [Art. 17](https://ai-act-service-desk.ec.europa.eu/de/ai-act/article-17), [Art. 18](https://ai-act-service-desk.ec.europa.eu/de/ai-act/article-18), [Art. 19](https://ai-act-service-desk.ec.europa.eu/de/ai-act/article-19) |

### D. Mindestanforderungen bei Betreiberrolle für Hochrisiko-KI

| ID | Prüffrage / Tätigkeit | Antwort | Status | Begründung | Nachweis / Link | Verantwortlich | Fällig | AI-Act-Referenz |
|---|---|---|---|---|---|---|---|---|
| `DEP-01` | System anleitungsgemäß betreiben; qualifizierte menschliche Aufsicht, geeignete Eingabedaten, Betriebsüberwachung, Protokollaufbewahrung sowie vorgeschriebene Informationen und Meldungen sicherstellen. | `offen` | `nicht_begonnen` |  |  |  |  | [Art. 26](https://ai-act-service-desk.ec.europa.eu/de/ai-act/article-26) |
| `DEP-02` | Vor erster Nutzung prüfen, ob eine Grundrechte-Folgenabschätzung erforderlich ist; gegebenenfalls durchführen, melden und aktuell halten. | `offen` | `nicht_begonnen` |  |  |  |  | [Art. 27](https://ai-act-service-desk.ec.europa.eu/de/ai-act/article-27) |
| `DEP-03` | Falls einschlägig: Betroffene über KI-gestützte Entscheidungen informieren und Verfahren für das Recht auf Erläuterung vorhalten. | `offen` | `nicht_begonnen` |  |  |  |  | [Art. 26](https://ai-act-service-desk.ec.europa.eu/de/ai-act/article-26), [Art. 86](https://ai-act-service-desk.ec.europa.eu/de/ai-act/article-86) |

### E. Konformität und Registrierung bei Hochrisiko-KI

| ID | Prüffrage / Tätigkeit | Antwort | Status | Begründung | Nachweis / Link | Verantwortlich | Fällig | AI-Act-Referenz |
|---|---|---|---|---|---|---|---|---|
| `CNF-01` | Zutreffendes Konformitätsverfahren bestimmen und vor Inverkehrbringen bzw. Inbetriebnahme abschließen: Anhang VI, Anhang VII oder integriertes sektorales Produktverfahren. | `offen` | `nicht_begonnen` |  |  |  |  | [Art. 43](https://ai-act-service-desk.ec.europa.eu/de/ai-act/article-43), [Anhang VI](https://ai-act-service-desk.ec.europa.eu/de/ai-act/annex-6), [Anhang VII](https://ai-act-service-desk.ec.europa.eu/de/ai-act/annex-7) |
| `CNF-02` | EU-Konformitätserklärung, CE-Kennzeichnung und erforderliche Anbieter-, System- und Betreiberregistrierungen vollständig nachweisen. | `offen` | `nicht_begonnen` |  |  |  |  | [Art. 47](https://ai-act-service-desk.ec.europa.eu/de/ai-act/article-47), [Art. 48](https://ai-act-service-desk.ec.europa.eu/de/ai-act/article-48), [Art. 49](https://ai-act-service-desk.ec.europa.eu/de/ai-act/article-49), [Anhang V](https://ai-act-service-desk.ec.europa.eu/de/ai-act/annex-5), [Art. 71](https://ai-act-service-desk.ec.europa.eu/de/ai-act/article-71) |

### F. Betrieb, Änderungen und Vorfälle bei Hochrisiko-KI

| ID | Prüffrage / Tätigkeit | Antwort | Status | Begründung | Nachweis / Link | Verantwortlich | Fällig | AI-Act-Referenz |
|---|---|---|---|---|---|---|---|---|
| `LIF-01` | Prozess für Nichtkonformität, Korrekturmaßnahmen, Information und Zusammenarbeit mit Behörden einrichten. | `offen` | `nicht_begonnen` |  |  |  |  | [Art. 20](https://ai-act-service-desk.ec.europa.eu/de/ai-act/article-20), [Art. 21](https://ai-act-service-desk.ec.europa.eu/de/ai-act/article-21) |
| `LIF-02` | Anbieterplan zur aktiven, systematischen Beobachtung nach dem Inverkehrbringen nachweisen und Betreiberinformationen zuführen. | `offen` | `nicht_begonnen` |  |  |  |  | [Art. 72](https://ai-act-service-desk.ec.europa.eu/de/ai-act/article-72) |
| `LIF-03` | Prozess zur Erkennung, Eskalation, Untersuchung und fristgerechten Meldung schwerwiegender Vorfälle einrichten. | `offen` | `nicht_begonnen` |  |  |  |  | [Art. 73](https://ai-act-service-desk.ec.europa.eu/de/ai-act/article-73) |
| `LIF-04` | Änderungen an Zweck, Modell, Daten, Architektur und Leistung kontrollieren und vorab auf eine neue Konformitätsbewertung prüfen. | `offen` | `nicht_begonnen` |  |  |  |  | [Art. 43 Abs. 4](https://ai-act-service-desk.ec.europa.eu/de/ai-act/article-43) |

### G. Abschluss

| ID | Prüffrage / Tätigkeit | Antwort | Status | Begründung | Nachweis / Link | Verantwortlich | Fällig | AI-Act-Referenz |
|---|---|---|---|---|---|---|---|---|
| `GAT-01` | Einstufung, anwendbare Pflichten, Nachweise, offene Punkte und Auflagen prüfen und eine namentlich verantwortete Entscheidung dokumentieren. | `offen` | `nicht_begonnen` |  |  |  |  | [Art. 16](https://ai-act-service-desk.ec.europa.eu/de/ai-act/article-16), [Art. 26](https://ai-act-service-desk.ec.europa.eu/de/ai-act/article-26) |

## 4. Entscheidung

| Feld | Eintrag |
|---|---|
| Risikoklasse und Rechtsgrundlage |  |
| Rolle der Organisation |  |
| Anwendbare Pflichtenmodule |  |
| Offene Nachweise |  |
| Auflagen mit Verantwortlichen und Fristen |  |
| Entscheidung | `freigegeben` / `freigegeben_mit_auflagen` / `nicht_freigegeben` / `weitere_pruefung` |
| Gültige Systemversion und Zweckbestimmung |  |
| Nächste Prüfung / Auslöser für Neubewertung |  |
| Entscheider, Datum und Prüfvermerk |  |

## 5. Rechtsstand

Vor jeder Freigabe sind der aktuelle [AI Act Explorer](https://ai-act-service-desk.ec.europa.eu/de/ai-act-explorer), der [Umsetzungszeitplan](https://ai-act-service-desk.ec.europa.eu/de/ai-act/timeline/zeitplan-fuer-die-umsetzung-des-eu-ki-gesetzes) und [Art. 113](https://ai-act-service-desk.ec.europa.eu/de/ai-act/article-113) zu prüfen. Politische Einigungen oder Gesetzgebungsvorschläge werden getrennt vom geltenden konsolidierten Recht dokumentiert.
