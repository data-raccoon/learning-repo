## Summary

<!-- What changed and why? -->

## Scope

<!-- Which components and behaviors are affected? -->

## Verification

- [ ] Formatting and linting pass
- [ ] Type checking passes
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Agent evaluations pass or are not applicable
- [ ] I reviewed the final diff for unrelated changes

Commands executed:

```text
make check
make eval
```

## Agent behavior changes

- [ ] Prompts or instructions changed
- [ ] Tool definitions or permissions changed
- [ ] Model or model parameters changed
- [ ] Routing, memory or orchestration changed
- [ ] Guardrails or approval policy changed
- [ ] No agent behavior changed

If applicable, describe evaluation results:

<!-- Baseline, candidate result and important failures -->

## Security and privacy

- [ ] No secrets or real customer data were added
- [ ] Input and output validation were considered
- [ ] Authorization is enforced outside model instructions
- [ ] Logging and trace redaction were considered
- [ ] Consequential actions have an appropriate approval mechanism

## Compatibility

- [ ] No public interface changed
- [ ] Public interface changes are documented
- [ ] Migration or rollback instructions are included

## Risks and rollback

**Known risks:**

<!-- Describe remaining risks. -->

**Rollback procedure:**

<!-- Describe how to revert safely. -->
