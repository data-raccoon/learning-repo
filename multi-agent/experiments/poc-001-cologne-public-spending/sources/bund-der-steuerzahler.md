---
id: POC-001-SOURCE-BDST-001
status: active
owner: data_analytics_engineer
created: 2026-07-17
review_date: 2026-08-07
---

# Source Profile: Bund der Steuerzahler Schwarzbuch

## Classification

- **Publisher:** Bund der Steuerzahler Deutschland e.V. and its regional associations.
- **Evidence role:** `secondary_advocacy`.
- **Primary entry points:** [Schwarzbuch overview](https://www.steuerzahler.de/service/publikationen/das-schwarzbuch/) and [Schwarzbuch case platform](https://www.schwarzbuch.de/).
- **Update pattern:** Annual Schwarzbuch editions plus online cases, updates, follow-ups, and regional reporting.
- **Coverage:** Selected cases at federal, state, and municipal level; not a complete or representative inventory of public expenditure.

## Published research approach

The publisher describes a case-based research process. Potential cases commonly originate from citizen or member tips, press monitoring, and its own research. Researchers evaluate media reports and official communications, request a response from responsible institutions, and may add on-site impressions. Annual publication is an editorial selection of illustrative cases.

This process offers useful investigation patterns but does not expose a complete reproducible scoring model, sampling frame, fixed threshold set, or case-selection weighting. The POC therefore treats the resulting conclusions as attributed positions.

## Strengths for POC-001

- long-running collection of concrete municipal cases;
- readable reconstruction of costs, dates, decisions, and visible consequences;
- attention to planning failures, recurring costs, low utilization, and preventable escalation;
- links or clues to official documents and responsible institutions;
- follow-up reporting that can reveal changed decisions and realized savings;
- current emphasis on lifecycle and investment follow-on costs.

## Limitations and risks

- advocacy mission and editorial framing;
- lead-driven and publication-driven selection bias;
- unknown denominator: cases cannot establish prevalence across all Cologne spending;
- inconsistent detail and comparability across years and regional associations;
- values may reflect different dates, scopes, price bases, or estimates;
- strong language can collapse fact, inference, and recommendation;
- high-visibility capital projects may be overrepresented relative to routine services;
- later corrections or changed circumstances may not be present in the original case page.

## Permitted use

- create a review candidate;
- extract an attributed claim and its cited source trail;
- tag reusable failure patterns;
- define search features for systematic screening;
- identify relevant questions and alternative explanations;
- evaluate whether POC screening can rediscover documented patterns;
- study follow-up outcomes.

## Required corroboration

Before a BdSt claim contributes to a POC finding:

1. locate the underlying official decision, financial value, usage measure, or statement where reasonably possible;
2. reconcile dates, scope, price basis, and plan versions;
3. record the responsible institution's position;
4. test material alternative explanations;
5. distinguish BdSt wording from the POC's own inference;
6. assign claim-level confidence and a retrieval date.

## Initial Cologne seed cases

These cases seed the pattern library; they are not pre-approved findings.

| Seed case | Initial patterns | POC use | BdSt source |
| --- | --- | --- | --- |
| Heinrich-Böll-Platz | design consequence, recurring guarding cost, long unresolved remediation | Test lifecycle-cost reconstruction and remediation alternatives | [BdSt case page](https://www.steuerzahler.de/aktuelles/detail/seit-24-jahren-teuer-gesperrt-boell-platz-in-koeln/) |
| Cologne Opera renovation | repeated cost and schedule revisions, financing and interim consequences | Test scope-adjusted cost history and governance chronology | [BdSt case page](https://www.steuerzahler.de/beitraegekommunalkompass/news/sanierung-der-koelner-oper-jetzt-bei-665-mio-euro/) |
| Cologne Central Library renovation | changing estimates, scope and transparency questions | Test whether historical estimates are genuinely comparable | [BdSt case page](https://www.steuerzahler.de/aktuelles/detail/das-sanierungsdesaster-der-zentralbibliothek-in-koeln/) |
| Thurner Hof | investment without available public use, permits, changing use concept | Test output readiness, decision latency, and alternative-use options | [BdSt case page](https://www.steuerzahler.de/aktuelles/detail/thurner-hof-in-koeln-seit-20-jahren-zu/) |
| Bus line 127 to Lentpark | low measured use, recurring operating cost, lower-cost service alternative | Study a before-and-after service-model change | [Schwarzbuch 2018/19](https://www.steuerzahler.de/fileadmin/user_upload/Schwarzbuch2018_web.pdf) |

## Pattern tags seeded from the source

- `cost_growth`
- `schedule_delay`
- `low_utilization`
- `output_unavailable`
- `recurring_follow_on_cost`
- `weak_needs_validation`
- `scope_change`
- `alternative_not_tested`
- `decision_latency`
- `transparency_gap`
- `governance_failure_hypothesis`
- `funding_asymmetry`
- `preventive_intervention_opportunity`

Tags indicate a research question, not a conclusion.

## Source maintenance

For every ingested case retain the original URL, title, publisher, publication and retrieval dates, named author where available, edition, geography, attributed claims, referenced primary sources, later updates, and content snapshot or checksum where lawful and practical. Check for updates before relying on an older case.
