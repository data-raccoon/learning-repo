---
id: data-source-inventory-001
status: active
owner: data_analytics_engineer
created: 2026-07-17
review_date: 2026-08-17
---

# Cologne Data Source Inventory

## Purpose

Maintain a lightweight radar of publicly accessible data sources that may support future experiments. An entry documents what appears to exist, why access may be interesting, and what remains unknown. Inclusion is not a decision to build a POC or product.

This first version deliberately avoids a mandatory discovery pipeline, numeric ranking, or universal data model. Source cards may be incomplete and should become more precise when someone actually inspects or uses the source.

## Source Card Metadata

| Field | Meaning |
| --- | --- |
| ID | Stable internal identifier that does not depend on the source URL. |
| Publisher | Organization responsible for the source data. |
| Subject | Short description of the information domain. |
| Access and formats | How the source currently appears to be obtainable. |
| Geographic scope | Spatial coverage and available geographic levels. |
| Time coverage | Snapshot, history, or live/operational character. |
| Update behavior | Published cadence or current observation; not an availability guarantee. |
| License and attribution | Known reuse terms, or an explicit verification gap. |
| Access effort | Initial qualitative hypothesis: low, medium, or high. |
| Why it is interesting | Potential information value or reusable access advantage. |
| Main difficulty | Expected extraction, semantic, quality, or operational friction. |
| Potential questions | Examples only; not committed product hypotheses. |
| Unknowns / next check | Facts to verify before relying on the source. |

## What “Normalized” Means Here

Normalized data is a derived technical representation that makes a source easier and safer to reuse while preserving its original meaning and provenance.

Typical normalization steps include:

- rename source-specific columns to stable, documented field names;
- represent dates consistently, for example as ISO `YYYY-MM-DD` values;
- make units explicit and consistent without silently converting meaning;
- store identifiers as stable strings and keep leading zeros;
- represent missing, suppressed, zero, and not-applicable values differently;
- transform coordinates into a documented common reference system when required;
- connect geographic records through explicit district or area identifiers;
- add source URL, retrieval time, reporting date, license, and raw-snapshot reference;
- document every transformation and retain the immutable original data.

Example:

```text
Source row:
STADTTEIL=101 | Stand=31.12.25 | Einwohner=30.123 | Wert=* 

Normalized representation:
area_type=city_district
area_id="101"
reference_date="2025-12-31"
population=30123
suppressed_value=null
suppression_reason="statistical_confidentiality"
source_record_id="..."
```

Normalization does **not** mean:

- interpreting or explaining why a value exists;
- forcing every Cologne source into one universal schema;
- replacing the raw source;
- filling unknown values with guesses;
- treating revised and historical values as interchangeable;
- aggregating away important source limitations.

For an early access spike, a small source-specific normalized sample is enough. A shared schema should emerge only after genuine reuse appears.

## Initial Inventory

### SRC-K-001 — Open Data Cologne Catalog and DKAN API

- **Publisher:** City of Cologne / Open Data Cologne editorial team
- **Source:** [Open Data Cologne](https://www.offenedaten-koeln.de/)
- **Subject:** Cross-domain catalog covering population, transport, environment, administration, planning, culture, health, and other municipal topics.
- **Access and formats:** Web catalog, dataset pages, downloadable resources, and a documented DKAN API; formats vary by dataset.
- **Geographic scope:** Primarily Cologne, with dataset-specific spatial levels.
- **Time coverage:** Dataset-specific.
- **Update behavior:** Dataset-specific; catalog metadata may not equal resource freshness.
- **License and attribution:** Dataset-specific and must be captured from each dataset or resource record.
- **Access effort:** Medium.
- **Why it is interesting:** It is the main discovery surface and may allow programmatic metadata harvesting across many domains.
- **Main difficulty:** Metadata consistency, resource-link stability, and actual data freshness can vary independently.
- **Potential questions:** Which datasets change frequently? Which domains contain machine-readable but underused resources? Which sources share geographic identifiers?
- **Unknowns / next check:** Test current DKAN API behavior, pagination, resource URL stability, rate expectations, and metadata completeness.

### SRC-K-002 — Municipal Geographic Reference System

- **Publisher:** City of Cologne, Office for Urban Development and Statistics
- **Sources:** [Cologne districts](https://www.offenedaten-koeln.de/dataset/stadtteile-k%C3%B6ln), [Cologne boroughs](https://www.offenedaten-koeln.de/dataset/stadtbezirke-k%C3%B6ln)
- **Subject:** Boundaries and identifiers for boroughs, districts, statistical quarters, blocks, postal areas, and related municipal divisions.
- **Access and formats:** JSON, KMZ, Shapefile, CSV descriptions, and a broader GeoPackage depending on the resource.
- **Geographic scope:** Multiple nested and overlapping Cologne area systems.
- **Time coverage:** Current boundaries plus some historical resources.
- **Update behavior:** Irregular, especially when electoral or administrative boundaries change.
- **License and attribution:** The district list is published under Data Licence Germany Zero 2.0; verify each geometry resource separately.
- **Access effort:** Medium.
- **Why it is interesting:** It can become the geographic join layer across otherwise disconnected sources.
- **Main difficulty:** Multiple coordinate systems, changing boundaries, similar area concepts, and IDs that must remain strings.
- **Potential questions:** Which public observations belong to the same district, quarter, postal area, or electoral area?
- **Unknowns / next check:** Inventory all area levels, identifiers, valid-from dates, geometry validity, and crosswalk tables.

### SRC-K-003 — Cologne District Information Reports

- **Publisher:** City of Cologne, Office for Urban Development and Statistics
- **Source:** [Small-area statistics](https://www.stadt-koeln.de/artikel/62998/index.html)
- **Subject:** Population, households, social structure, mobility, housing, economy, politics, and living conditions by district and borough.
- **Access and formats:** Annual PDF reports; from 2020 onward, Excel data attachments are embedded in the downloaded PDF according to the publisher.
- **Geographic scope:** 86 districts, nine boroughs, and city totals; separate postal-area reports also exist.
- **Time coverage:** Published reports include multiple years from 2005 through current editions, with uneven structure across periods.
- **Update behavior:** Approximately annual, with possible revisions.
- **License and attribution:** Verify the reuse terms of each report and embedded data attachment before publication.
- **Access effort:** High.
- **Why it is interesting:** Rich, longitudinal small-area data exists but is not exposed as a simple stable table endpoint.
- **Main difficulty:** Extracting PDF attachments, changing workbook layouts, suppressed values, revisions, footnotes, and semantic changes.
- **Potential questions:** Which indicators changed across areas and years? Where do apparent trends result from revisions or changed definitions?
- **Unknowns / next check:** Automate attachment extraction for two editions and compare workbook schemas and disclosure-control markers.

### SRC-K-004 — Statistical Area Information Application

- **Publisher:** City of Cologne
- **Source:** [Statistical area information](https://www.stadt-koeln.de/artikel/65104/index.html)
- **Subject:** Area lookup and indicators including sociodemographic structure, election results, and registered vehicles.
- **Access and formats:** Interactive map application with downloadable tabular data and linked geodata.
- **Geographic scope:** Address lookup into higher-level areas; published indicators at permitted aggregate levels.
- **Time coverage:** Indicator-specific.
- **Update behavior:** Not yet assessed.
- **License and attribution:** Geodata and statistical data terms must be verified per downloaded resource.
- **Access effort:** High.
- **Why it is interesting:** The application exposes rich relationships between addresses, area hierarchies, and indicators that are not obvious from catalog browsing.
- **Main difficulty:** Discovering stable download endpoints, reconstructing indicator definitions, and respecting privacy-driven aggregation boundaries.
- **Potential questions:** How do different municipal geographies overlap? Which indicators are available at which spatial resolution?
- **Unknowns / next check:** Inspect browser network calls and official documentation without bypassing access controls; record stable public endpoints only.

### SRC-K-005 — Cologne Statistical Atlas

- **Publisher:** City of Cologne
- **Source:** [Cologne Statistical Atlas](https://www.stadt-koeln.de/artikel/71231/index.html)
- **Subject:** Thematic maps and charts for statistical indicators across boroughs and districts.
- **Access and formats:** Interactive map applications plus downloadable tables.
- **Geographic scope:** City, borough, district, and other supported statistical areas.
- **Time coverage:** Indicator-specific.
- **Update behavior:** Continued by the municipal statistics office; exact cadence varies.
- **License and attribution:** The publisher states CC BY 3.0 Germany for the open data used by the atlas; verify attribution requirements for each extracted resource.
- **Access effort:** Medium to high.
- **Why it is interesting:** Indicator definitions and thematic views may reveal data relationships not apparent in raw files.
- **Main difficulty:** Separating application behavior, downloadable data, metadata, and reusable map assets.
- **Potential questions:** Which indicators produce surprising spatial contrasts? Which views can be reproduced more accessibly?
- **Unknowns / next check:** Map indicator identifiers to downloadable tables and check whether historical values are available consistently.

### SRC-K-006 — Cologne Municipal Budget

- **Publisher:** City of Cologne
- **Source:** [Cologne municipal budget](https://www.stadt-koeln.de/artikel/60791/index.html)
- **Subject:** Budget statutes, result and financial plans, product areas, departments, districts, appendices, and amendment records.
- **Access and formats:** Multiple large PDF volumes; the 2025/2026 budget includes a volume of roughly 60 MB plus drafts and amendment documents.
- **Geographic scope:** Whole city with organizational, product-area, and some district views.
- **Time coverage:** Historical budgets and current multi-year planning.
- **Update behavior:** Budget-cycle based, with drafts, amendments, approval, and later reporting potentially representing different states.
- **License and attribution:** Reuse terms require explicit verification; public availability alone is not a commercial reuse licence.
- **Access effort:** High.
- **Why it is interesting:** Public financial structure is information-rich but difficult to compare across documents, organizational units, and versions.
- **Main difficulty:** PDF tables, accounting semantics, hierarchy reconstruction, document-version relationships, and changing classifications.
- **Potential questions:** What changed from draft to approved budget? Which product areas gained or lost planned resources? How do multi-year plans shift?
- **Unknowns / next check:** Determine text/table extractability, stable account or product identifiers, and whether machine-readable annexes exist elsewhere.

### SRC-K-007 — Council Information and OParl

- **Publisher:** City of Cologne / Cologne Council Information System
- **Sources:** [Council information access](https://www.stadt-koeln.de/politik-und-verwaltung/stadtrat/index.html), [City description of the OParl initiative](https://www.stadt-koeln.de/leben-in-koeln/digitalisierung-koeln/modellkommune-open-government-des-bundes)
- **Subject:** Meetings, agendas, papers, consultations, decisions, organizations, people, files, and locations.
- **Access and formats:** Public council web interface; the city has described OParl-based machine-readable access, but the current production endpoint and completeness have not been verified for this inventory.
- **Geographic scope:** City council, committees, and district representations where public information is available.
- **Time coverage:** Council pages reference meetings since 2008; API and attachment history require verification.
- **Update behavior:** Event- and meeting-driven.
- **License and attribution:** Unresolved. Verify current endpoint terms, document rights, and attachment-specific restrictions.
- **Access effort:** High.
- **Why it is interesting:** It combines structured political processes with large volumes of attachments and potentially extractable geographic references.
- **Main difficulty:** Endpoint discovery, linked entity traversal, attachment extraction, revisions, topic classification, location inference, and personal data in public documents.
- **Potential questions:** What is being decided, where, by whom, at which stage, and which places or budgets are affected?
- **Unknowns / next check:** Confirm official OParl availability, licence, pagination, historical completeness, deleted or replaced records, and attachment access.

### SRC-K-008 — KVB Operational Open Data

- **Publisher:** Kölner Verkehrs-Betriebe AG
- **Source:** [KVB Open Data](https://kvb.koeln/service/open_data.html)
- **Subject:** Stops, elevators, escalators, disruption states, and other KVB operational resources.
- **Access and formats:** Public JSON and CSV endpoints for several resources.
- **Geographic scope:** KVB service area, primarily Cologne.
- **Time coverage:** Current operational state; history may need to be collected by consumers.
- **Update behavior:** Operational. KVB states that data and delivery methods may change without notice.
- **License and attribution:** Verify the current KVB usage terms for every intended reuse.
- **Access effort:** Medium.
- **Why it is interesting:** A historical dataset can be created from transient operational states that are otherwise difficult to analyze over time.
- **Main difficulty:** Schema and endpoint instability, entity matching, outages versus missing data, polling design, and absent history.
- **Potential questions:** Which facilities are repeatedly unavailable? How long do disruptions persist? Which stops are most affected?
- **Unknowns / next check:** Measure response stability, identifiers, timestamps, actual refresh cadence, error behavior, and permitted polling.

### SRC-K-009 — VRS GTFS Scheduled Transit Data

- **Publisher:** Verkehrsverbund Rhein-Sieg GmbH
- **Source:** [VRS GTFS dataset](https://offenedaten-koeln.de/dataset/vrs-verkehrsdaten-gtfs)
- **Subject:** Scheduled public transport stops, routes, trips, calendars, and related static timetable entities.
- **Access and formats:** Downloadable GTFS ZIP, including a DHID-based variant.
- **Geographic scope:** VRS network, including Cologne.
- **Time coverage:** Current planned timetable; not equivalent to real-time operation.
- **Update behavior:** The catalog states daily updates between midnight and 1 a.m.
- **License and attribution:** CC BY 4.0 according to the catalog; additional VRS usage terms should be reviewed.
- **Access effort:** Medium.
- **Why it is interesting:** GTFS provides a rich network model that can be joined with places, services, and municipal areas.
- **Main difficulty:** Large relational text files, service calendars, route variants, transfers, changing IDs, and the distinction between planned and actual service.
- **Potential questions:** Which places are reachable under a stated schedule? Where does planned service density differ across time or areas?
- **Unknowns / next check:** Inspect current feed size, ID stability, DHID coverage, licence notice inside the feed, and historic snapshot feasibility.

### SRC-K-010 — Cologne Traffic Load Calendar

- **Publisher:** City of Cologne, Traffic Management Office
- **Source:** [Cologne traffic volume](https://offenedaten-koeln.de/dataset/verkehrsaufkommen-stadt-k%C3%B6ln)
- **Subject:** Utilization and traffic state on important road segments.
- **Access and formats:** Public JSON with Esri-style polyline geometry and traffic-state codes.
- **Geographic scope:** Selected important Cologne roads, not the complete road network.
- **Time coverage:** Current state; historical analysis requires snapshots.
- **Update behavior:** The catalog states updates approximately every five to ten minutes.
- **License and attribution:** Data Licence Germany Zero 2.0 according to the dataset metadata.
- **Access effort:** Medium.
- **Why it is interesting:** Frequent observations allow a new historical resource to be constructed from an ephemeral feed.
- **Main difficulty:** Sensor gaps, special status codes, geometry parsing, road-segment identity, event effects, and responsible polling.
- **Potential questions:** Which segments repeatedly show congestion? How do event days differ? Where are data gaps persistent?
- **Unknowns / next check:** Verify current endpoint, timestamps, licence inside responses, rate expectations, and whether values reflect sensors or editorial status.

### SRC-K-011 — Cologne Parks and Amenities

- **Publisher:** City of Cologne, Office for Landscape Management and Green Spaces
- **Source:** [Cologne parks](https://www.offenedaten-koeln.de/dataset/parkanlagen-koeln)
- **Subject:** Parks and amenities such as playgrounds, dog areas, slackline facilities, and beer gardens.
- **Access and formats:** JSON, point JSON, WMS, and additional garden-path files.
- **Geographic scope:** Cologne parks and related facilities.
- **Time coverage:** Current inventory; history not indicated.
- **Update behavior:** Last catalog adjustment shown as 2022-08-10; actual resource freshness must be checked.
- **License and attribution:** Data Licence Germany Zero 2.0 according to the dataset metadata.
- **Access effort:** Low to medium.
- **Why it is interesting:** It combines geometry and amenity attributes and can be joined with mobility or area context.
- **Main difficulty:** Completeness, stale metadata, geometry differences between resources, and ambiguous amenity definitions.
- **Potential questions:** Which amenities are documented in which areas? How well are parks connected to scheduled transit or cycling infrastructure?
- **Unknowns / next check:** Compare resource modification dates with catalog dates and validate a sample against the official map.

### SRC-K-012 — Cologne Binding Development Plans

- **Publisher:** City of Cologne, Office for Real Estate, Surveying and Cadastre
- **Source:** [Cologne development plans](https://www.offenedaten-koeln.de/dataset/bebauungsplaene-koeln-bauungsplaene)
- **Subject:** Legally binding land-use and building rules for defined areas, including use type, density, building form, transport, and green spaces.
- **Access and formats:** JSON and WMS plus links to planning information and documents.
- **Geographic scope:** Plan areas across Cologne.
- **Time coverage:** Current plans and procedural states; historical/version coverage needs assessment.
- **Update behavior:** Dataset metadata was adjusted in 2025; cadence is not yet established.
- **License and attribution:** Data Licence Germany Zero 2.0 according to the dataset metadata; linked plan documents may have separate terms.
- **Access effort:** High.
- **Why it is interesting:** Structured plan geometries can open access to legally and semantically complex planning documents.
- **Main difficulty:** Linking geometry, procedural status, plan identifiers, drawings, textual rules, amendments, and legal validity.
- **Potential questions:** Which areas are governed by which plans? Which plans changed status? What types of use or density are specified?
- **Unknowns / next check:** Inspect identifiers, document links, plan-version relationships, WMS layers, and the boundary between open metadata and protected plan documents.

### SRC-K-013 — Cologne Cycling Network

- **Publisher:** City of Cologne, Office for Sustainable Mobility Development
- **Source:** [Cologne cycling network](https://offenedaten-koeln.de/dataset/radverkehrsnetz)
- **Subject:** Planned cycling network with categories describing mixed or separated traffic principles.
- **Access and formats:** WMS and WFS.
- **Geographic scope:** Cologne road and cycling network planning.
- **Time coverage:** Current planning state; no history indicated.
- **Update behavior:** Irregular according to the dataset metadata.
- **License and attribution:** Data Licence Germany Zero 2.0 according to the dataset metadata.
- **Access effort:** Medium to high.
- **Why it is interesting:** WFS data can be combined with roads, transit, facilities, and administrative geographies but is less accessible than a simple download.
- **Main difficulty:** OGC service discovery, layer schema, line geometry, planned-versus-built interpretation, and version tracking.
- **Potential questions:** Where do network categories change? How does the planned network connect to destinations or public transport?
- **Unknowns / next check:** Inspect service capabilities, available layers, feature attributes, geometry validity, and whether implementation status exists separately.

### SRC-K-014 — Cologne Budgets and Annual Accounts

- **Publisher:** City of Cologne, Kämmerei / municipal finance administration.
- **Sources:** [Budgets](https://www.stadt-koeln.de/artikel/60791/index.html) and [annual accounts](https://www.stadt-koeln.de/politik-und-verwaltung/finanzen/jahresabschluesse).
- **Subject:** Planned and actual municipal revenue, expenditure, balance-sheet, cash-flow, product-group, objective, and indicator information.
- **Access and formats:** Large, multi-part PDF documents; some tables are text-extractable, but layouts and accessibility vary.
- **Geographic scope:** City of Cologne core administration; consolidated accounts extend to defined municipal entities for selected reporting years.
- **Time coverage:** Multiple budgets and annual accounts are published; exact comparable coverage depends on document type and product structure.
- **Update behavior:** Budget-cycle and annual reporting publications rather than an API cadence.
- **License and attribution:** Publicly accessible; commercial reuse and document-level terms require explicit verification before republication.
- **Access effort:** High.
- **Why it is interesting:** It is the primary official evidence for connecting intended resource allocation with actual financial execution and documented product goals.
- **Main difficulty:** Large PDFs, changing structures and identifiers, plan versions, accounting distinctions, reorganizations, incomplete indicator histories, and lack of a ready-made relational dataset.
- **Potential questions:** Which product groups show recurring variances? Where can resources be connected to stable output measures? Which important areas lack observable performance evidence?
- **Unknowns / next check:** Test table extraction and identifier stability across a small representative sample; verify page-level provenance, terms, and accessibility constraints.

### SRC-K-015 — Cologne Municipal Participation Reports

- **Publisher:** City of Cologne.
- **Source:** [Municipal participation reports](https://www.stadt-koeln.de/artikel/06283/index.html).
- **Subject:** Governance, ownership, financial, staffing, and purpose information for municipal companies and participations.
- **Access and formats:** Annual PDF reports, with structure and detail varying by reporting year and entity.
- **Geographic scope:** Cologne's portfolio of municipal participations, not the municipal core budget alone.
- **Time coverage:** Reports are published for multiple years; comparable entity histories require validation.
- **Update behavior:** Annual publication.
- **License and attribution:** Publicly accessible; reuse terms and third-party material require verification.
- **Access effort:** High.
- **Why it is interesting:** Material public services and financial activity sit outside the core administration, so this source can expose scope that a budget-only view would miss.
- **Main difficulty:** Entity changes, group structures, differing accounting scopes, PDF extraction, and separating public-service objectives from financial performance.
- **Potential questions:** Which public-service objectives and financial flows are visible by entity? Where can participation evidence be reconciled with consolidated municipal reporting?
- **Unknowns / next check:** Select a small entity sample, inspect stable identifiers and tables, and document reconciliation limits with the core budget and consolidated accounts.

### SRC-K-016 — Bund der Steuerzahler Schwarzbuch and Case Platform

- **Publisher:** Bund der Steuerzahler Deutschland e.V. and its regional associations.
- **Sources:** [Schwarzbuch overview](https://www.steuerzahler.de/service/publikationen/das-schwarzbuch/) and [case platform](https://www.schwarzbuch.de/).
- **Subject:** Editorially selected cases of alleged, potential, prevented, or corrected public-spending waste, including municipal cases and follow-up reporting.
- **Access and formats:** Web articles and annual PDF publications; individual cases may link to or quote official decisions, statements, cost figures, and media reports.
- **Geographic scope:** Germany at federal, state, and municipal level; Cologne cases are present but coverage is not comprehensive.
- **Time coverage:** Long-running annual series plus online updates; detail and structure vary by edition and regional publisher.
- **Update behavior:** Annual flagship publication with irregular online cases and follow-ups.
- **License and attribution:** Publicly accessible copyrighted editorial material; facts must be independently sourced and reuse must respect quotation, attribution, and publication terms.
- **Access effort:** Medium.
- **Evidence role:** Secondary advocacy source for leads, failure patterns, source discovery, method evaluation, and outcome follow-up; not authoritative evidence of waste.
- **Why it is interesting:** It provides a curated history of understandable cases, recurring failure patterns, official counterpositions, and examples in which criticism preceded a changed decision.
- **Main difficulty:** Editorial selection bias, advocacy framing, unknown denominator, heterogeneous substantiation, changing project scope, and potentially outdated conclusions.
- **Potential questions:** Which patterns can be detected systematically in Cologne data? Which claims can be traced to primary sources? Which follow-up cases reveal effective corrective actions?
- **Unknowns / next check:** Build a versioned Cologne case index, verify referenced primary documents, record later developments, and assess coverage bias by expenditure category.
- **POC contract:** [POC-001 BdSt source profile](../../initiatives/cologne-tax-improvements/sources/bund-der-steuerzahler.md).

### SRC-K-017 — gpaNRW Municipal Audit of Cologne

- **Publisher:** Gemeindeprüfungsanstalt Nordrhein-Westfalen (gpaNRW).
- **Sources:** [Cologne audit report 2024/2025](https://gpanrw.de/sites/default/files/2026-01/Gesamtbericht_Stadt_Koeln_2024_2025.pdf) and [gpaNRW download center](https://gpanrw.de/service/downloadcenter/aktuelle-downloads).
- **Subject:** External municipal audit findings, recommendations, good practices, process criteria, and intermunicipal comparisons across defined administrative domains.
- **Access and formats:** Public, text-extractable PDF reports plus selected XLSX benchmark resources; no credentials required.
- **Geographic scope:** Cologne report with comparison to other independent cities in North Rhine-Westphalia; additional thematic and municipal reports are available.
- **Time coverage:** Periodic audit rounds rather than continuous monitoring; the initial POC source is the Cologne 2024/2025 report.
- **Update behavior:** New audit rounds and thematic downloads are published periodically.
- **License and attribution:** Publicly accessible official publications; retain attribution and verify terms before republishing extracted tables or substantial text.
- **Access effort:** Low to medium.
- **Evidence role:** Official external assurance evidence within the report's stated audit period and scope.
- **Why it is interesting:** It supplies structured findings and recommendations, defined process expectations, positive controls, and peer context that complement advocacy-led cases.
- **Main difficulty:** Thematic coverage, reporting lag, changing methodologies, structural differences between cities, and limited direct quantification of fiscal or outcome effects.
- **Potential questions:** Which recommendations remain actionable? Which strengths prevent false-positive flags? Where do peer differences persist after accounting for service and organizational structure?
- **Unknowns / next check:** Extract the consolidated finding-recommendation tables, retain identifiers and page provenance, and reconcile three contrasting cases with current Cologne records.
- **POC contract:** [POC-001 gpaNRW source profile](../../initiatives/cologne-tax-improvements/sources/gpanrw-municipal-audit.md).

### SRC-K-018 — BBSR INKAR Regional Indicators

- **Publisher:** Federal Institute for Research on Building, Urban Affairs and Spatial Development (BBSR).
- **Source:** [INKAR online atlas and database downloads](https://www.inkar.de/).
- **Subject:** Approximately 600 standardized indicators covering demography, education, labour, economy, housing, transport, environment, public services, and selected municipal SDG measures.
- **Access and formats:** Free full-database ZIP downloads, interactive tables, CSV/XLS exports, documentation, and maps; no credentials required.
- **Geographic scope:** Multiple comparable spatial levels from municipalities and districts to functional regions, Germany, and parts of Europe.
- **Time coverage:** Long time series for many indicators; the 07/2025 edition describes data on a common territorial status of 2023.
- **Update behavior:** Versioned releases with revised or extended observations and downloadable prior editions.
- **License and attribution:** Presented by the publisher as a free Open Data offer whose data and maps may be exported and reused; retain the recommended citation and verify dataset-level source metadata.
- **Access effort:** Low.
- **Evidence role:** Official statistical context for need, structure, service access, outcome trends, and geographic comparison; not causal program evidence.
- **Why it is interesting:** It adds standardized outcome and structural context that financial records, audits, and individual cases usually lack.
- **Main difficulty:** Reporting lag, spatial aggregation, territorial and definition changes, underlying-source heterogeneity, peer selection, and causal overinterpretation.
- **Potential questions:** Is a Cologne trend local or widespread? Which needs and outcomes should contextualize an expenditure case? Where are citywide indicators too coarse for a recommendation?
- **Unknowns / next check:** Inspect the current full-download schema and metadata, then extract no more than twelve indicators across three initial case domains with explicit temporal and spatial fit.
- **POC contract:** [POC-001 INKAR source profile](../../initiatives/cologne-tax-improvements/sources/inkar-regional-indicators.md).

### SRC-K-019 — Cologne Public Procurement Lifecycle

- **Publishers:** City of Cologne procurement platforms, Vergabemarktplatz NRW, and EU Tenders Electronic Daily where applicable.
- **Sources:** [City procurement platform](https://vergabeplattform.stadt-koeln.de/NetServer/), [City procurement service](https://www.stadt-koeln.de/wirtschaft/ausschreibungsservice/index.html), [Vergabemarktplatz NRW](https://www.evergabe.nrw.de/), and [TED](https://ted.europa.eu/).
- **Subject:** Planned procurements, competitions, awards, cancellations, modifications, contract periods, lots, values where published, and supplier information.
- **Access and formats:** Public HTML and documents, with structured EU eForms or exports where available; some participation features or documents require registration.
- **Geographic scope:** City of Cologne buying activity published locally, at NRW level, or above EU thresholds.
- **Time coverage:** Current and archived notices with platform-dependent retention and searchability.
- **Update behavior:** Event-driven and potentially frequent during active procedures.
- **License and attribution:** Official public notices; document reuse, bulk access, and platform terms require verification.
- **Access effort:** Low to medium.
- **Evidence role:** Primary authoritative evidence of the published procurement event, not of need quality, value for money, or delivery outcome.
- **Why it is interesting:** It exposes current decision windows and connects spending intent to contracted delivery and later changes.
- **Main difficulty:** Multiple identifiers and platforms, expired documents, missing values, thresholds, framework call-offs, version changes, and incomplete below-threshold coverage.
- **Potential questions:** Which audit recommendations reach contract requirements? Where do awards, modifications, and actual expenditure diverge? Which recurring services lack outcome reporting?
- **Unknowns / next check:** Capture lifecycle events for the two current POC cases and test cross-platform identifier and document linkage.
- **POC contract:** [POC-001 procurement source profile](../../initiatives/cologne-tax-improvements/sources/cologne-procurement-lifecycle.md).

### SRC-K-020 — Cologne Operational Performance and Asset Data

- **Publisher or custodian:** City of Cologne and accountable operating units.
- **Sources:** [Building Management reports](https://www.stadt-koeln.de/politik-und-verwaltung/gebaeudewirtschaft-der-stadt-koeln/berichte), [2024 Energy Report](https://www.stadt-koeln.de/mediaasset/content/pdf26/34977_energiebericht_2024_bfrei.pdf), [climate monitoring](https://www.klimaschutz-monitoring.koeln/), and separately approved aggregated operational or asset extracts.
- **Subject:** Service volume, timeliness, backlog, cost recovery, quality, utilization, asset condition, energy, emissions, maintenance, investment, and delivery evidence.
- **Access and formats:** Public PDF reports and dashboards plus controlled system extracts whose formats depend on the custodian; no controlled access is assumed in v1.
- **Geographic scope:** Cologne services, facilities, assets, and accountable operating units.
- **Time coverage:** Source-specific operational periods and versioned reports; current system records may be more timely than publications.
- **Update behavior:** Annual reports, dashboard updates, and operational-system cadences.
- **License and attribution:** Public reports retain their published terms; controlled data require purpose, custodian approval, access, retention, and deletion conditions.
- **Access effort:** Low for public reports; high and approval-dependent for controlled aggregates.
- **Evidence role:** Primary observation of operations or asset condition within documented definitions and coverage.
- **Why it is interesting:** It is the missing bridge between planned or contracted expenditure and realized service, cost, quality, utilization, or asset outcome.
- **Main difficulty:** Fragmented systems, inconsistent definitions, missing stable identifiers, privacy, confidentiality, reporting lag, data quality, and unavailable internal records.
- **Potential questions:** Did a recommendation change realized cost or service? Which backlogs or assets warrant priority? Are expected savings and emissions reductions being achieved?
- **Unknowns / next check:** Complete the two privacy-safe initial extraction slices for ordered burials and municipal buildings without ingesting restricted records.
- **POC contract:** [POC-001 operational and asset-data source profile](../../initiatives/cologne-tax-improvements/sources/cologne-operational-asset-data.md).

## Cross-Source Notes

- Public accessibility does not by itself establish a commercial reuse licence. Verify terms at dataset and resource level.
- Catalog modification dates, resource modification dates, and actual reference dates are different concepts and should be stored separately.
- Interactive applications may reveal public download endpoints, but no access control, technical protection, or usage restriction should be bypassed.
- Sources containing public names, political roles, addresses, social indicators, or small-area statistics require privacy and interpretation review even when legally public.
- Operational feeds need caching, polite polling, failure detection, and clear distinction between “no event” and “no data.”
- Every extracted sample should retain provenance to the exact source resource and retrieval timestamp.
