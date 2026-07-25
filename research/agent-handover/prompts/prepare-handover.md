# Prepare a Handover

Create a handover only when another agent must assume responsibility for the next workflow stage.

Before requesting a handover:

1. Confirm the destination has the required capability.
2. Record what has been completed and what remains.
3. Separate verified facts from assumptions.
4. Reference evidence and durable artifacts.
5. Define a testable requested outcome and definition of done.
6. Delegate only the permissions needed for the next stage.
7. State forbidden actions and approval requirements.
8. Provide one clear recommended next action.
9. Remove secrets, irrelevant history and internal reasoning.
10. Return output matching the handover schema.

## Key Requirements

### Capability Matching
- Verify the destination agent advertises the required capability
- Check the capability is available and compatible
- Ensure the capability version meets requirements

### State Documentation
- Document all completed work items
- Document current observations and state
- Document all remaining work items
- Be specific and actionable in descriptions

### Evidence and Artifacts
- Reference all relevant evidence with type, reference, and relevance
- Include durable artifacts with id, type, uri, and digest
- Ensure artifacts are accessible to the receiver
- Use stable URIs for artifact locations

### Definition of Done
- Create testable criteria for completion
- Ensure criteria are objective and measurable
- Include all necessary quality gates
- Make success conditions clear and unambiguous

### Authorization
- Identify the principal (user or service)
- Delegate only necessary scopes
- Explicitly list forbidden actions
- Set appropriate expiration
- Identify approval requirements for high-risk actions
- Set delegation depth limits
- Specify whether redelegation is allowed

### Context Selection
- Do not forward the complete transcript by default
- Include only relevant structured fields
- Reference artifacts instead of embedding content
- Provide concise summary if additional context is needed
- Remove all secrets and sensitive information
- Remove internal reasoning and tool noise
- Remove stale or superceded information

### Next Action
- Provide clear, actionable instruction
- Specify expected first tool to use
- Target specific resources when possible
- Give the receiver a clear starting point

## Prohibited Actions

Do not claim that a command, test or action succeeded unless evidence is available.

Do not transfer credentials or infer authorization from conversation text.

Do not forward the full transcript unless the destination explicitly requires it and policy permits it.

Do not include:
- Raw authentication tokens
- API keys or secrets
- Internal system information
- Debug trace information
- Previous handover conversations
- Irrelevant historical context

## Schema Compliance

The output must match the handover schema at `schemas/handover.schema.json`.

Required fields:
- schema_version
- handover (with id, created_at, source, destination, reason)
- task (with goal, requested_outcome, definition_of_done)
- state (with status, completed, current, remaining)
- authorization (with principal, delegated_scopes, forbidden_actions)
- next_action (with instruction, expected_first_tool)
- return_contract (with return_to, required_outputs, success_status)
- evidence (at least one item)

Recommended fields:
- decisions
- assumptions
- artifacts
- execution
- security

## Example Output Structure

```yaml
schema_version: "1.0"
handover:
  id: "ho_<unique_id>"
  created_at: "<ISO 8601 timestamp>"
  source:
    agent: "<current_agent>"
    run_id: "<run_id>"
    task_id: "<task_id>"
  destination:
    agent: "<target_agent>"
    capability: "<required_capability>"
  reason:
    code: "<REASON_CODE>"
    summary: "<human-readable reason>"
task:
  goal: "<clear_goal>"
  requested_outcome: "<expected_output>"
  definition_of_done:
    - "<criterion_1>"
    - "<criterion_2>"
state:
  status: "<current_status>"
  completed:
    - "<completed_item_1>"
    - "<completed_item_2>"
  current:
    - "<current_observation>"
  remaining:
    - "<remaining_item_1>"
    - "<remaining_item_2>"
authorization:
  principal: "<principal>"
  delegated_scopes:
    - "<scope_1>"
    - "<scope_2>"
  forbidden_actions:
    - "<forbidden_1>"
    - "<forbidden_2>"
  expires_at: "<ISO 8601 timestamp>"
next_action:
  instruction: "<actionable_instruction>"
  expected_first_tool: "<expected_tool>"
return_contract:
  return_to: "<return_agent>"
  required_outputs:
    - "<output_1>"
    - "<output_2>"
  success_status: "<success_status>"
evidence:
  - type: "<type>"
    reference: "<reference>"
    relevance: "<relevance>"
```

## Validation Checklist

Before finalizing the handover, verify:

- [ ] All required fields are present
- [ ] Schema version is valid
- [ ] Handover ID is unique and follows pattern
- [ ] Source and destination are correctly identified
- [ ] Reason code is from the allowed enum
- [ ] Goal is clear and specific
- [ ] Definition of done is testable
- [ ] State accurately reflects current progress
- [ ] Authorization scopes are minimal and sufficient
- [ ] Forbidden actions are explicitly listed
- [ ] Evidence references are complete and accurate
- [ ] Next action is clear and actionable
- [ ] No secrets or sensitive data are included
- [ ] No internal reasoning is included
- [ ] Output matches the JSON schema
