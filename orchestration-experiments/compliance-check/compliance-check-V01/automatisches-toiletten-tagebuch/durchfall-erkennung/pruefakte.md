---
schema_id: "eu-ai-act-assessment"
schema_version: "1.0"
template_version: "1.0"
assessment_id: "ASSESSMENT-2026-001"
application_id: "APP-TOILETTEN-TAGEBUCH"
use_case_id: "APP-TOILETTEN-TAGEBUCH-UC-01"
system_name: "Automatisches Toiletten-Tagebuch"
system_version: "nicht angegeben"
intended_purpose: "Lokale Erkennung und Zeitreihen-Protokollierung normaler und Durchfall-Ereignisse zur persönlichen Nutzung und optionalen manuellen Vorlage beim Hausarzt"
lifecycle_phase: "entwicklung"
hospital_role: "anbieter"
risk_result: "offen"
assessment_status: "in_pruefung"
owner: "Verkäufer/Entwickler – Rechtsträger nicht angegeben"
reviewer: ""
started_at: "2026-07-13"
updated_at: "2026-07-13"
due_at: ""
legal_status_checked_at: "2026-07-13"
legal_status_source: "EU AI Act Service Desk und Europäische Kommission"
final_decision: "weitere_pruefung"
allowed_answers:
  - "offen"
  - "ja"
  - "nein"
  - "nicht_anwendbar"
  - "eskalieren"
allowed_statuses:
  - "offen"
  - "in_pruefung"
  - "nachweis_fehlt"
  - "erledigt"
  - "eskalieren"
allowed_final_decisions:
  - "freigegeben"
  - "freigegeben_mit_auflagen"
  - "nicht_freigegeben"
  - "weitere_pruefung"
---

# Prüfakte: Automatisches Toiletten-Tagebuch – Durchfall-Erkennung

Prüfstand: 13. Juli 2026. Diese Arbeitsakte bewertet ausschließlich den EU AI Act. Sie ersetzt keine Prüfung insbesondere nach MDR, DSGVO, ePrivacy-, Verbraucher- oder nationalem Gesundheitsrecht.

## Erfasster Sachverhalt

- Der Verkäufer ist zugleich Entwickler und will die App unter eigener Verantwortung weltweit, einschließlich des EU-Markts, anbieten.
- Mikrofoneingaben aus einem Badezimmer werden lokal verarbeitet. Sprache wird technisch miterfasst, nach Angabe aber weder inhaltlich noch biometrisch ausgewertet und sofort verworfen.
- Ausgegeben wird eine nicht personenbezogen geführte Zeitreihe mit den Kategorien „normal“ und „Durchfall“.
- Bewohner nutzen das Protokoll persönlich und entscheiden selbst, ob sie es ihrem Hausarzt zeigen. Eine automatische Übermittlung oder medizinische Entscheidung findet nicht statt.
- Nutzerkreis: Bewohner; Besucher können sich im Erfassungsbereich befinden. Der Hausarzt erhält nur ein vom Bewohner geteiltes Protokoll, nicht das KI-System selbst.

## Checkliste

| ID | Prüffrage oder Tätigkeit | Antwort | Status | Begründung | Nachweis / Dokumentlink | Verantwortlicher | Fälligkeit | EU-AI-Act-Referenz |
|---|---|---|---|---|---|---|---|---|
| BAS-01 | Sind Systemgrenze, Version, Eingaben, Ausgaben, Nutzer und automatische Aktionen vollständig beschrieben? | offen | nachweis_fehlt | Grundablauf ist beschrieben; Modell, Version, technische Systemgrenze, Speicherdauern und sämtliche App-Komponenten fehlen. | Produkt- und Architekturakte anfordern | Produktverantwortung | vor Release | [Art. 3](https://ai-act-service-desk.ec.europa.eu/de/ai-act/article-3) |
| BAS-02 | Fällt die Anwendung als KI-System und räumlich/sachlich in den Anwendungsbereich? | offen | nachweis_fehlt | Die Klassifikation aus Audiodaten spricht für ein KI-System. Zu belegen sind das verwendete Modell bzw. Inferenzverfahren. Das weltweite Inverkehrbringen soll nach Arbeitsannahme die EU einschließen. | Modellbeschreibung; Liste der Vertriebsgebiete | Entwicklung / Recht | vor Einstufungsabschluss | [Art. 2](https://ai-act-service-desk.ec.europa.eu/de/ai-act/article-2), [Art. 3](https://ai-act-service-desk.ec.europa.eu/de/ai-act/article-3) |
| BAS-03 | Sind Zweckbestimmung und vernünftigerweise vorhersehbare Verwendung verbindlich dokumentiert? | offen | nachweis_fehlt | „Automatisches Toiletten-Tagebuch“, persönliche Nutzung und Protokoll für den Hausarzt sind bekannt. Marketingaussagen, Gebrauchsanweisung und medizinische Leistungsversprechen fehlen. | Freigegebene Zweckbestimmung; Store-Text; Gebrauchsanweisung | Produkt / Recht | vor Store-Einreichung | [Art. 3](https://ai-act-service-desk.ec.europa.eu/de/ai-act/article-3) |
| BAS-04 | Liegt eine verbotene KI-Praktik vor? | nein | erledigt | Nach dem beschriebenen Funktionsumfang keine Manipulation, Sozialbewertung, biometrische Kategorisierung oder Emotionserkennung. Sprache soll nicht analysiert werden. Bei Funktionsänderung erneut prüfen. | Funktionsspezifikation; Tests zur Nichtauswertung von Sprache | Recht / Entwicklung | bei jeder wesentlichen Änderung | [Art. 5](https://ai-act-service-desk.ec.europa.eu/de/ai-act/article-5) |
| ROL-01 | Sind alle Rollen je Akteur bestimmt und Rollenwechsel geprüft? | ja | erledigt | Verkäufer und Entwickler sind identisch und stellen die App unter eigener Verantwortung bereit: Anbieterrolle. Bewohner handeln rein persönlich und gelten insoweit nicht als Betreiber nach dem AI Act. Der Hausarzt erhält nur einen Export. | Vertriebs- und Lizenzmodell bestätigen | Recht | vor Release bestätigen | [Art. 3](https://ai-act-service-desk.ec.europa.eu/de/ai-act/article-3), [Art. 25](https://ai-act-service-desk.ec.europa.eu/de/ai-act/article-25) |
| CLS-01 | Ist geprüft, ob das System Sicherheitsbauteil oder Produkt nach Anhang I ist und eine Drittstellenprüfung benötigt? | offen | nachweis_fehlt | Ob Zweckbestimmung und Werbeaussagen die App zu Medizinproduktsoftware machen, wurde nicht produktrechtlich bestimmt. Davon kann der Hochrisikopfad nach Art. 6 Abs. 1 abhängen. | MDR-/Produktrechtsbewertung; Klassifizierung; geplanter Konformitätsweg | Produktrecht / Recht | vor Release-Entscheidung | [Art. 6](https://ai-act-service-desk.ec.europa.eu/de/ai-act/article-6), [Anhang I](https://ai-act-service-desk.ec.europa.eu/de/ai-act/annex-1) |
| CLS-02 | Fällt der Use Case unter einen Bereich aus Anhang III? | nein | erledigt | Persönliches Symptom-Tagebuch ohne Entscheidung über Beschäftigung, Bildung, Leistungen, Versicherung, Strafverfolgung oder Zugang zu wesentlichen Diensten ist keinem beschriebenen Anhang-III-Fall zugeordnet. | Zweckbestimmung und Funktionsumfang | Recht | bei Zweckänderung | [Art. 6](https://ai-act-service-desk.ec.europa.eu/de/ai-act/article-6), [Anhang III](https://ai-act-service-desk.ec.europa.eu/de/ai-act/annex-3) |
| CLS-03 | Ist gegebenenfalls eine Ausnahme nach Art. 6 Abs. 3 dokumentiert und die Profiling-Grenze geprüft? | nicht_anwendbar | erledigt | Es wurde kein Anhang-III-Tatbestand festgestellt; daher wird keine Ausnahme nach Art. 6 Abs. 3 beansprucht. | Verweis auf CLS-02 | Recht | — | [Art. 6](https://ai-act-service-desk.ec.europa.eu/de/ai-act/article-6) |
| CLS-04 | Ist die Risikoklasse abschließend entschieden und begründet? | offen | nachweis_fehlt | Anhang III greift voraussichtlich nicht. Eine abschließende Einstufung bleibt bis zur Produkt- und Medizinproduktebewertung offen. | Freigegebener Einstufungsvermerk | Recht / Produktrecht | vor Release-Gate | [Art. 6](https://ai-act-service-desk.ec.europa.eu/de/ai-act/article-6) |
| TRN-01 | Sind einschlägige Transparenzpflichten umgesetzt? | offen | nachweis_fehlt | Die App sollte vor Nutzung klar mitteilen, dass eine automatisierte KI-Klassifikation erfolgt. Ob eine direkte Interaktion im Sinne von Art. 50 Abs. 1 vorliegt bzw. die KI-Natur offensichtlich ist, muss anhand der Oberfläche geprüft werden. Art. 50 Abs. 2 erscheint bei reiner Klassifikation nicht einschlägig. | UI-Flows; Datenschirm; Store-Text; Nutzerinformation | Produkt / UX / Recht | vor Release | [Art. 50](https://ai-act-service-desk.ec.europa.eu/de/ai-act/article-50) |
| PRO-01 | Ist bei Hochrisiko-KI ein Risikomanagementsystem eingerichtet? | offen | nachweis_fehlt | Nur bei bestätigter Hochrisiko-Einstufung verpflichtend; Produktpfad ist noch offen. | Risikomanagementakte oder begründete Nichtanwendbarkeit | Qualitätsmanagement | nach CLS-04 | [Art. 9](https://ai-act-service-desk.ec.europa.eu/de/ai-act/article-9) |
| PRO-02 | Erfüllen Daten und Daten-Governance die Hochrisiko-Anforderungen? | offen | nachweis_fehlt | Bedingt durch die noch offene Hochrisiko-Einstufung. Unabhängig davon sind Datensätze und Fehlerraten für die behauptete Erkennungsleistung zu validieren. | Datensatzbeschreibung; Bias-/Leistungsprüfung | Entwicklung / Qualität | nach CLS-04 | [Art. 10](https://ai-act-service-desk.ec.europa.eu/de/ai-act/article-10) |
| PRO-03 | Liegen technische Dokumentation und erforderliche Protokollierungsfunktionen vor? | offen | nachweis_fehlt | Bei Hochrisiko-KI gelten Art. 11 und 12. Derzeit fehlen Modell-, Versions-, Logging- und Löschungsnachweise. | Technische Dokumentation; Logging-Konzept | Entwicklung / Qualität | vor Release | [Art. 11](https://ai-act-service-desk.ec.europa.eu/de/ai-act/article-11), [Art. 12](https://ai-act-service-desk.ec.europa.eu/de/ai-act/article-12), [Anhang IV](https://ai-act-service-desk.ec.europa.eu/de/ai-act/annex-4) |
| PRO-04 | Sind Gebrauchsanweisung und wirksame menschliche Aufsicht vorgesehen? | offen | nachweis_fehlt | Bei Hochrisiko-KI wären Art. 13 und 14 verbindlich. Bewohner entscheiden zwar über die Weitergabe, müssen aber auch Fehlklassifikationen erkennen, korrigieren oder löschen können. | Gebrauchsanweisung; Korrektur-/Löschfunktion; UX-Test | Produkt / UX | vor Release | [Art. 13](https://ai-act-service-desk.ec.europa.eu/de/ai-act/article-13), [Art. 14](https://ai-act-service-desk.ec.europa.eu/de/ai-act/article-14) |
| PRO-05 | Sind Genauigkeit, Robustheit, Cybersicherheit und Qualitätsmanagement angemessen belegt? | offen | nachweis_fehlt | Leistungsgrenzen, Fehlalarme, Umgebungsgeräusche, unmittelbare Audiolöschung und Manipulationsschutz sind nicht belegt; Hochrisikopflichten hängen von CLS-04 ab. | Validierungsbericht; Sicherheitskonzept; QMS | Entwicklung / Qualität | vor Release | [Art. 15](https://ai-act-service-desk.ec.europa.eu/de/ai-act/article-15), [Art. 17](https://ai-act-service-desk.ec.europa.eu/de/ai-act/article-17) |
| DEP-01 | Sind Betreiberpflichten für den vorgesehenen Einsatz umzusetzen? | nicht_anwendbar | erledigt | Bewohner verwenden die App nach dem Sachverhalt ausschließlich persönlich und nicht beruflich. Der Hausarzt nutzt nicht das KI-System, sondern erhält gegebenenfalls ein statisches Protokoll. Bei Praxiszugang zur App neu prüfen. | Nutzungs- und Freigabekonzept | Recht | bei Vertriebsmodelländerung | [Art. 2](https://ai-act-service-desk.ec.europa.eu/de/ai-act/article-2), [Art. 26](https://ai-act-service-desk.ec.europa.eu/de/ai-act/article-26) |
| DEP-02 | Ist eine Grundrechte-Folgenabschätzung durch einen erfassten Betreiber erforderlich? | nicht_anwendbar | erledigt | Kein Betreiber im Sinne des AI Acts und kein festgestellter Anhang-III-Hochrisikofall. | Verweise auf DEP-01 und CLS-02 | Recht | bei Rollen-/Zweckänderung | [Art. 27](https://ai-act-service-desk.ec.europa.eu/de/ai-act/article-27) |
| DEP-03 | Sind Informations- und Auskunftswege gegenüber betroffenen Personen eingerichtet? | nicht_anwendbar | erledigt | Die speziellen Betreiberpflichten setzen nach aktuellem Sachverhalt keinen erfassten Betreiber voraus. Anbieterinformationen und andere Rechtsgebiete bleiben unberührt. | Verweis auf DEP-01; Nutzerinformation separat | Recht | bei Rollenänderung | [Art. 26](https://ai-act-service-desk.ec.europa.eu/de/ai-act/article-26), [Art. 86](https://ai-act-service-desk.ec.europa.eu/de/ai-act/article-86) |
| CNF-01 | Ist der richtige Konformitätsbewertungsweg bestimmt und abgeschlossen? | offen | nachweis_fehlt | Hängt insbesondere davon ab, ob ein Anhang-I-Produkt mit Drittstellenprüfung vorliegt. | Produktklassifizierung; Konformitätsplan | Produktrecht / Qualität | vor Inverkehrbringen | [Art. 43](https://ai-act-service-desk.ec.europa.eu/de/ai-act/article-43), [Anhang VI](https://ai-act-service-desk.ec.europa.eu/de/ai-act/annex-6) |
| CNF-02 | Sind EU-Konformitätserklärung, CE-Kennzeichnung und Registrierung erforderlich und umgesetzt? | offen | nachweis_fehlt | Die Pflichten folgen erst aus dem noch zu bestimmenden Hochrisiko-/Produktpfad. | Erklärung; CE-/Registrierungsnachweise oder begründete Nichtanwendbarkeit | Produktrecht / Qualität | vor Inverkehrbringen | [Art. 47](https://ai-act-service-desk.ec.europa.eu/de/ai-act/article-47), [Art. 48](https://ai-act-service-desk.ec.europa.eu/de/ai-act/article-48), [Art. 49](https://ai-act-service-desk.ec.europa.eu/de/ai-act/article-49), [Anhang V](https://ai-act-service-desk.ec.europa.eu/de/ai-act/annex-5) |
| LIF-01 | Ist ein Post-Market-Monitoring-System eingerichtet? | offen | nachweis_fehlt | Als Hochrisikopflicht abhängig von CLS-04; für eine vertriebene Erkennungs-App ist ein Verfahren für Fehlklassifikationen und Beschwerden jedenfalls ein sinnvoller Nachweis. | Post-Market-Plan; Beschwerdeprozess | Qualität | vor Release | [Art. 72](https://ai-act-service-desk.ec.europa.eu/de/ai-act/article-72) |
| LIF-02 | Besteht ein Prozess für schwerwiegende Vorfälle und Meldungen? | offen | nachweis_fehlt | Bei Hochrisiko-KI wäre Art. 73 anzuwenden. Einstufung und Verantwortlichkeiten sind noch offen. | Vorfallprozess; Meldewege | Qualität / Recht | vor Release | [Art. 73](https://ai-act-service-desk.ec.europa.eu/de/ai-act/article-73) |
| LIF-03 | Sind Korrekturmaßnahmen und Zusammenarbeit mit Behörden geregelt? | offen | nachweis_fehlt | Anbieterpflichten für Hochrisiko-KI hängen von CLS-04 ab; zuständige Rollen und Rückruf-/Updateprozess fehlen. | CAPA-, Rückruf- und Behördenprozess | Qualität / Recht | vor Release | [Art. 20](https://ai-act-service-desk.ec.europa.eu/de/ai-act/article-20), [Art. 21](https://ai-act-service-desk.ec.europa.eu/de/ai-act/article-21) |
| LIF-04 | Löst eine Änderung eine erneute Einstufung oder Konformitätsbewertung aus? | offen | nachweis_fehlt | Änderungen an Zweck, Sprachverarbeitung, Cloudbetrieb, Arztzugang oder Diagnoseaussagen können Rolle und Einstufung ändern. Ein formeller Change-Control-Prozess fehlt. | Änderungs- und Releaseprozess | Produkt / Qualität | vor Release | [Art. 25](https://ai-act-service-desk.ec.europa.eu/de/ai-act/article-25), [Art. 43](https://ai-act-service-desk.ec.europa.eu/de/ai-act/article-43) |
| GAT-01 | Liegen Einstufungsentscheidung, offene Auflagen, Freigabe und Prüfervermerk vollständig vor? | offen | nachweis_fehlt | Produktrechtliche Einstufung, technische Nachweise, Rechtsträger, EU-Vertriebsdetails und unabhängige Prüfung fehlen. | Unterzeichnetes Release-Gate | Geschäftsführung / Recht | vor Store-Einreichung | [Art. 6](https://ai-act-service-desk.ec.europa.eu/de/ai-act/article-6), [Art. 16](https://ai-act-service-desk.ec.europa.eu/de/ai-act/article-16) |

## Vorläufiges Gate

- Entscheidung: `weitere_pruefung`
- Begründung: Kein Anhang-III-Hochrisikofall und keine verbotene Praxis erkennbar. Die abschließende AI-Act-Einstufung hängt jedoch von der rechtlich verbindlichen Zweckbestimmung und davon ab, ob die App als Produkt nach Anhang I einer Drittstellen-Konformitätsbewertung unterliegt.
- Mindestauflagen vor Store-Einreichung: Produkt-/MDR-Einstufung, verbindliche Zweckbestimmung, Nachweis des KI-Verfahrens, UI-Transparenz, Leistungsvalidierung, technischer Nachweis der sofortigen Sprachverwerfung, EU-Akteur-/Vertriebsmodell und dokumentiertes Release-Gate.

## Rechtsstand

Geprüft am 13. Juli 2026. Die konsolidierte Verordnung nennt den 2. August 2026 als allgemeinen Anwendungsbeginn; Kapitel I und II gelten seit dem 2. Februar 2025. Die Kommission berichtet daneben über eine politische Einigung vom 7. Mai 2026 zu angepassten Fristen für Hochrisiko-Regeln. Diese Entwicklung ist bis zur formellen Konsolidierung getrennt vom geltenden Verordnungstext zu behandeln.

