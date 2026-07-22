import json
import unittest
from dataclasses import replace

from harness import (Approval, ContractError, GateRejected, PolicyDecision,
                     PolicyEnforcementPoint, ReleaseCandidate, TrustedContext,
                     admission_gate, canonical_payload_hash, parse_action_request,
                     release_gate)


BASE = {
    "schema_version": 1, "message_type": "action_request", "request_id": "req-1",
    "principal_id": "alice", "action": "transfer", "target": "account/ops",
    "amount_cents": 500, "risk": "high",
}


class ContractTests(unittest.TestCase):
    def test_malformed_json_is_rejected(self):
        with self.assertRaises(ContractError):
            parse_action_request('{"schema_version":')

    def test_unknown_field_is_rejected(self):
        value = dict(BASE, injected="shell")
        with self.assertRaises(ContractError):
            parse_action_request(json.dumps(value))

    def test_duplicate_and_bool_as_integer_are_rejected(self):
        with self.assertRaises(ContractError):
            parse_action_request(json.dumps(dict(BASE, amount_cents=True)))
        duplicate = json.dumps(BASE)[:-1] + ',"target":"other"}'
        with self.assertRaises(ContractError):
            parse_action_request(duplicate)


class GateTests(unittest.TestCase):
    def setUp(self):
        self.context = TrustedContext("alice", 1000, frozenset({"account/ops"}))
        self.allow = PolicyEnforcementPoint(
            lambda _: PolicyDecision(True, "policy-v1", "ok"))
        self.raw = json.dumps(BASE)
        request = parse_action_request(self.raw)
        self.approval = Approval("reviewer", canonical_payload_hash(request))

    def test_policy_outage_fails_closed(self):
        def unavailable(_):
            raise TimeoutError("PDP unavailable")
        with self.assertRaises(GateRejected):
            admission_gate(self.raw, self.context, PolicyEnforcementPoint(unavailable),
                           self.approval)

    def test_undefined_policy_result_fails_closed(self):
        with self.assertRaises(GateRejected):
            admission_gate(self.raw, self.context, PolicyEnforcementPoint(lambda _: None),
                           self.approval)

    def test_hash_tampering_is_blocked(self):
        tampered = dict(BASE, amount_cents=501)
        with self.assertRaises(GateRejected):
            admission_gate(json.dumps(tampered), self.context, self.allow, self.approval)

    def test_semantic_gate_blocks_untrusted_target(self):
        value = dict(BASE, target="account/attacker")
        request = parse_action_request(json.dumps(value))
        approval = Approval("reviewer", canonical_payload_hash(request))
        with self.assertRaises(GateRejected):
            admission_gate(json.dumps(value), self.context, self.allow, approval)

    def test_valid_request_is_admitted(self):
        request, decision = admission_gate(self.raw, self.context, self.allow, self.approval)
        self.assertEqual(request.request_id, "req-1")
        self.assertEqual(decision.policy_revision, "policy-v1")

    def test_release_gate_blocks_failed_check(self):
        good = ReleaseCandidate("sha256:" + "a" * 64, True, True, True, True)
        release_gate(good, self.allow)
        with self.assertRaises(GateRejected):
            release_gate(replace(good, tests_passed=False), self.allow)


if __name__ == "__main__":
    unittest.main()
