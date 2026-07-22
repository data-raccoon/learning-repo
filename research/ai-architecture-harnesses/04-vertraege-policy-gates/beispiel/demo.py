"""Small executable happy-path demonstration."""

import json

from harness import (Approval, PolicyDecision, PolicyEnforcementPoint, TrustedContext,
                     admission_gate, canonical_payload_hash, parse_action_request)


raw = json.dumps({
    "schema_version": 1, "message_type": "action_request", "request_id": "req-42",
    "principal_id": "alice", "action": "transfer", "target": "account/ops",
    "amount_cents": 2500, "risk": "high",
})
request = parse_action_request(raw)
approval = Approval("reviewer@example.org", canonical_payload_hash(request))
context = TrustedContext("alice", 10_000, frozenset({"account/ops"}))
pep = PolicyEnforcementPoint(lambda _: PolicyDecision(True, "policy-v7", "allowed"))
admitted, decision = admission_gate(raw, context, pep, approval)
print(f"ADMITTED {admitted.request_id} under {decision.policy_revision}")
