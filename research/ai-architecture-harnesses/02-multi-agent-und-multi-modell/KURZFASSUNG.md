# Multi-Agent und Multi-Modell – Kurzfassung

## Kernaussage

Mehr Agenten oder Modelle erhöhen Zuverlässigkeit nicht automatisch. Sie lohnen sich bei nachweislich unabhängigen Teilaufgaben, getrennten Fach- oder Sicherheitsdomänen, Kontextgrenzen oder kostenbewusstem Modell-Routing. Ein deterministischer Orchestrator sollte Topologie, Identität, Handoffs, Rechte, Budgets, Abbruch und Commit kontrollieren; Modelle liefern Vorschläge innerhalb dieser Grenzen.

## Garantiert

Ein nicht umgehbarer, fail-closed Orchestrator kann unter korrekter Implementierung erzwingen:

- Handoffs gehen nur an erlaubte, authentisierte Rollen;
- Handoff-Nachrichten erfüllen ein versioniertes Schema;
- Fan-out, Verschachtelung, Aufrufzahl, Laufzeit und nominales Budget bleiben begrenzt;
- parallele Worker verändern gemeinsamen Zustand nicht direkt;
- externe Wirkungen laufen nur über geprüfte, idempotente Adapter.

Checkpoint-basierte Fortsetzung ist nur mit dauerhaftem Store, kompatiblem Code und deduplizierten Nebenwirkungen belastbar. Qualitätsverbesserungen sind keine technische Garantie, sondern statistisch auf einem repräsentativen, versionierten Eval-Set nachzuweisen.

## Garantiert nicht

Mehrheit, Debatte und LLM-Judges beweisen keine Wahrheit. Unterschiedliche Modellnamen bedeuten keine unabhängigen Fehlerdomänen. Schema-konforme Übergaben können sachlich falsch sein oder relevante Details verlieren. Typische Risiken sind korrelierter Irrtum, Authority Laundering, Fehlrouting, Handoff-Schleifen, Kontextvergiftung, Budgetexplosion, Race Conditions und veraltete Ergebnisse.

## Einsatzkriterien

Vor Einführung sind Single-Call, Single-Agent und deterministischer Workflow als Baselines zu messen. Multi-Agent oder Multi-Modell ist nur sinnvoll, wenn ein Abhängigkeitsgraph echte Parallelität zeigt, Holdout-Evals einen belastbaren Qualitätsgewinn belegen, Kosten und p95-Latenz innerhalb der SLOs bleiben, Fehlerdiversität gemessen wird und Handoffs sowie Commit-Gates technisch kontrolliert sind. Bei hohem gemeinsamen Kontextbedarf oder sequenzieller Arbeit ist die einfachere Architektur vorzuziehen.

## Quellen

- [Anthropic: Building Effective Agents](https://www.anthropic.com/engineering/building-effective-agents)
- [Anthropic: Multi-Agent Research System](https://www.anthropic.com/engineering/multi-agent-research-system)
- [Microsoft: AI agent orchestration patterns](https://learn.microsoft.com/en-us/azure/architecture/ai-ml/guide/ai-agent-design-patterns)
- [AutoGen: Termination](https://microsoft.github.io/autogen/stable/user-guide/agentchat-user-guide/tutorial/termination.html)
- [Smit et al.: Should we be going MAD?](https://proceedings.mlr.press/v235/smit24a.html)
- [Cemri et al.: Why Do Multi-Agent LLM Systems Fail?](https://arxiv.org/abs/2503.13657)
