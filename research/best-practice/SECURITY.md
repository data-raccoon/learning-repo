# Security policy

## Reporting a vulnerability

Do not report suspected vulnerabilities through public issues.

Send the report to `<security contact or private reporting mechanism>` and
include:

- affected component and version
- reproduction steps
- potential impact
- suggested mitigation, if known

We will acknowledge receipt within `<time period>`.

## Supported versions

| Version | Supported |
|---|---|
| Latest stable | Yes |
| Previous stable | Security fixes only |
| Older versions | No |

## Secret handling

- Never commit credentials, API keys, tokens or private certificates.
- Use the approved secret-management system.
- Use separate credentials for local, test, staging and production.
- Scope credentials to the minimum required permissions.
- Rotate any credential suspected of exposure.
- Treat `.env` as local-only; commit only `.env.example`.

## Agent and model security

- Model output is untrusted input.
- Retrieved documents may contain prompt injections.
- The model cannot grant itself permissions.
- Tool calls require schema and authorization validation.
- State-changing tools must be narrowly scoped.
- High-impact operations require explicit human approval.
- Sensitive values must be redacted from prompts, traces and logs.
- Agent execution must have time, cost, retry and tool-call limits.

## Human approval is required for

- production deployment
- deletion or irreversible mutation
- permission and identity changes
- financial transactions
- external publication or communication
- access to highly sensitive data
- changes that weaken security controls

## Dependency policy

New dependencies must:

1. Solve a demonstrated need.
2. Have a compatible license.
3. Have an acceptable maintenance and security posture.
4. Be pinned through the project's lock file.
5. Pass automated vulnerability and policy checks.

## Logging policy

Logs must not contain:

- access or refresh tokens
- credentials or private keys
- full prompts containing personal or confidential data
- unnecessary model reasoning
- raw customer records

Use identifiers and redacted metadata instead.

## Incident response

See `docs/runbooks/security-incident.md`.

For a suspected incident:

1. Stop or isolate the affected workflow.
2. Preserve relevant evidence.
3. Revoke compromised credentials.
4. Notify the security owner.
5. Assess affected data and systems.
6. Document remediation and follow-up actions.
