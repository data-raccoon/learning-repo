import tempfile
import time
import unittest
from pathlib import Path

from capability_proxy import (
    CapabilityIssuer,
    CapabilityToolProxy,
    CapabilityVerifier,
    Denied,
    MemoryAuditSink,
)


KEY = b"development-only-signing-key-32-bytes-minimum"


class CapabilityProxyTests(unittest.TestCase):
    def setUp(self) -> None:
        self.audit = MemoryAuditSink()
        self.issuer = CapabilityIssuer(KEY)
        self.proxy = CapabilityToolProxy(
            CapabilityVerifier(KEY, issuer="example-issuer", audience="tool-proxy"), self.audit
        )
        self.seen = []
        self.proxy.register("echo", self._echo)
        self.proxy.register("read_file", self._echo)
        self.proxy.register("fetch", self._echo)

    def _echo(self, arguments, context):
        self.seen.append((arguments, context))
        return dict(arguments)

    def token(self, **overrides):
        values = {
            "subject": "agent-7",
            "audience": "tool-proxy",
            "tools": ["echo", "read_file", "fetch"],
            "max_calls": 10,
            "budget_units": 10,
        }
        values.update(overrides)
        return self.issuer.issue(**values)

    def test_capability_is_not_passed_to_tool(self):
        token = self.token()
        result = self.proxy.execute(token, "echo", {"message": "safe"})
        self.assertEqual(result, {"message": "safe"})
        self.assertNotIn(token, repr(self.seen))
        self.assertNotIn(token, repr(self.audit.events))

    def test_explicit_token_passthrough_is_denied(self):
        token = self.token()
        with self.assertRaisesRegex(Denied, "passthrough"):
            self.proxy.execute(token, "echo", {"authorization": f"Bearer {token}"})
        self.assertEqual(self.seen, [])

    def test_wrong_audience_is_denied(self):
        token = self.token(audience="some-downstream-api")
        with self.assertRaisesRegex(Denied, "audience"):
            self.proxy.execute(token, "echo", {})

    def test_signature_tampering_is_denied(self):
        token = self.token()
        body, signature = token.split(".", 1)
        replacement = "A" if signature[0] != "A" else "B"
        with self.assertRaisesRegex(Denied, "signature"):
            self.proxy.execute(f"{body}.{replacement}{signature[1:]}", "echo", {})

    def test_path_traversal_is_denied_after_resolution(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp, "workspace")
            root.mkdir()
            token = self.token(path_roots=[str(root)])
            escaped = root / ".." / "secret.txt"
            with self.assertRaisesRegex(Denied, "outside"):
                self.proxy.execute(token, "read_file", {"path": str(escaped)})

    def test_egress_defaults_to_deny_and_checks_exact_host(self):
        token = self.token(egress=["api.example.com:443"])
        with self.assertRaisesRegex(Denied, "not allowed"):
            self.proxy.execute(token, "fetch", {"url": "https://api.example.com.evil.test/data"})
        with self.assertRaisesRegex(Denied, "not allowed"):
            self.proxy.execute(token, "fetch", {"url": "https://127.0.0.1/data"})
        self.assertEqual(
            self.proxy.execute(token, "fetch", {"url": "https://api.example.com/data"})["url"],
            "https://api.example.com/data",
        )

    def test_expired_capability_is_denied(self):
        token = self.issuer.issue(
            subject="agent-7", audience="tool-proxy", tools=["echo"], ttl_seconds=1,
            now=int(time.time()) - 2,
        )
        with self.assertRaisesRegex(Denied, "expired"):
            self.proxy.execute(token, "echo", {})

    def test_secrets_are_redacted_from_result_and_audit(self):
        token = self.token()
        result = self.proxy.execute(
            token, "echo", {"message": "api_key=super-secret", "password": "hunter2"}
        )
        self.assertEqual(result["password"], "[REDACTED]")
        self.assertNotIn("super-secret", repr(result))
        self.assertNotIn("hunter2", repr(self.audit.events))

    def test_call_budget_input_output_and_timeout_limits_are_enforced(self):
        one_call = self.token(max_calls=1)
        self.proxy.execute(one_call, "echo", {})
        with self.assertRaisesRegex(Denied, "call limit"):
            self.proxy.execute(one_call, "echo", {})

        costly = CapabilityToolProxy(
            CapabilityVerifier(KEY, issuer="example-issuer", audience="tool-proxy"), self.audit
        )
        costly.register("costly", self._echo, cost_units=2)
        with self.assertRaisesRegex(Denied, "budget limit"):
            costly.execute(self.token(tools=["costly"], budget_units=1), "costly", {})

        with self.assertRaisesRegex(Denied, "input size"):
            self.proxy.execute(self.token(max_input_bytes=2), "echo", {"value": "large"})
        with self.assertRaisesRegex(Denied, "output size"):
            self.proxy.execute(self.token(max_output_bytes=2), "echo", {"value": "large"})

        slow = CapabilityToolProxy(
            CapabilityVerifier(KEY, issuer="example-issuer", audience="tool-proxy"), self.audit
        )
        slow.register("slow", lambda arguments, context: (time.sleep(0.02), "done")[1])
        with self.assertRaisesRegex(Denied, "timeout"):
            slow.execute(self.token(tools=["slow"], timeout_ms=1), "slow", {})

    def test_unserializable_input_fails_closed_and_is_audited(self):
        with self.assertRaisesRegex(Denied, "invalid tool request"):
            self.proxy.execute(self.token(), "echo", {"bad": object()})
        self.assertEqual(self.audit.events[-1].decision, "deny")

    def test_unsigned_and_unregistered_calls_fail_closed(self):
        with self.assertRaises(Denied):
            self.proxy.execute("not.a-capability", "echo", {})
        with self.assertRaisesRegex(Denied, "not allowed"):
            self.proxy.execute(self.token(), "unknown", {})


if __name__ == "__main__":
    unittest.main()
