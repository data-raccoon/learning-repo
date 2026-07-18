# Full QA Protocol for Mistral Cloud

## Why the previous pass failed

The earlier pass proved that isolated state and simulation helpers could reach expected
states. It did not prove that a new player could see a game field, take a first action,
or progress through the production UI. Its visual assertions accepted any nonzero canvas
and any populated UI root. Generated scenarios also bypassed the real economy by directly
funding state.

## Separation of responsibilities

1. **Outer evidence collector:** launches the real page with empty storage, records
   screenshots, console/runtime failures, viewport and canvas measurements, enabled
   controls, and public UI-driven state changes.
2. **Mistral multimodal QA auditor:** receives the original full-resolution PNG through
   Vibe's native image-attachment channel plus production source read-only. It traces
   initialization, layout, interactions, economy, persistence, accessibility, and
   responsive behavior. It does not edit code and does not treat generated tests as
   authoritative.
3. **Outer acceptance decision:** rejects unsupported PASS claims and maps accepted
   findings to owners.
4. **Separate repair jobs:** each P0/P1 failure class receives a narrow implementation
   job. No repair is hidden inside the audit.
5. **Regression gate:** reruns clean-profile first-use scenarios and captures new visual
   evidence before existing simulation checks.

## Mandatory first-use gates

A release cannot pass unless all are demonstrated through production boot and public
interfaces:

- a distinct play field is visible and materially sized at desktop and mobile widths;
- within ten seconds a new player has either an enabled meaningful action or a documented
  passive resource path toward one;
- performing the first action changes production state and visible output;
- the canvas backing size matches its CSS display size within device-pixel-ratio rules;
- UI panels do not fully occlude the play field;
- action dispatch reaches the production simulation handler;
- pointer hit-testing reaches each first-use control with no overlay intercepting it;
- a pressed control keeps the same DOM identity across at least one simulation tick and
  completes pointer-down/pointer-up activation;
- keyboard activation uses native control behavior and focus survives live simulation
  updates;
- the first producer, first mote, first capture, first upgrade, first phase transition,
  doctrine choice, Retuning, save/reload, and reset are reachable without direct test
  state mutation;
- keyboard and narrow-viewport operation preserve those paths.

`HTMLElement.click()` may be used as a narrow handler-wiring probe, but it cannot satisfy a
public interaction gate. The physical gate must preserve viewport geometry and nonzero event
timing, then confirm both visible output and state change. The journey must perform another
interaction after the first action legitimately changes the control structure.

## Required report structure

Every finding needs an ID, P0–P3 severity, observed/inferred classification, evidence,
reproduction steps, affected files/lines, user impact, likely failure class, repair
direction, and a regression test stated in observable terms. The report ends with a
release verdict and a checklist marking each required path as PASS, FAIL, or UNTESTED.

The reproducible auditor job is `.orchestration/jobs/full_qa_pass.json`. The project-local
runner supplies `first-run-1440x900.png` directly to `AgentLoop.act(images=...)`; it does
not ask the text-only `read_file` tool to decode the PNG. Vibe Work with
`.orchestration/qa/BROWSER_QA_PROMPT.md` remains a manual fallback.
