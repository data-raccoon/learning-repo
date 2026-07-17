---
name: quality-gate
description: Assess whether a product, code change, data asset, AI workflow, or operating change is ready to advance. Use before release, deployment, milestone acceptance, or lifecycle transition when QA, reliability, security, privacy, platform, or operational evidence is required.
---

# Quality Gate

1. Freeze candidate scope and locate its Work Order, acceptance criteria, architecture decisions, and prior risks.
2. Run `qa_reliability` and `security_privacy` independently and read-only. Add other domain reviewers only when affected.
3. Require evidence-backed findings with severity, reproduction or verification steps, and an owner.
4. Classify the result as `pass`, `conditional`, or `fail`. A pass needs evidence for every applicable criterion and no blocker.
5. Record residual risk with `company/templates/risk-register.md`. Human approval is required to accept material residual risk.
6. Request explicit Founder approval for production deployment even after a pass.
7. Never let assurance agents edit the implementation they review.

