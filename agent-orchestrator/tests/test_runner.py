from pathlib import Path
from dataclasses import replace
import os
import stat
import sys
import tempfile
import unittest

from agent_orchestrator.adapters import FakeAdapter
from agent_orchestrator.contracts import Job, Verifier
from agent_orchestrator.registry import Registry
from agent_orchestrator.runner import JobRunner
from agent_orchestrator.snapshot import TargetSnapshot
from tests.helpers import write_registry


class RunnerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.workspace = self.root / "workspace"
        self.target = self.workspace / "target"
        self.target.mkdir(parents=True)
        self.config = write_registry(self.root / "registry")
        self.registry = Registry(self.config)
        self.orchestrator = self.workspace / "agent-orchestrator"
        self.orchestrator.mkdir()
        self.previous_runtime = os.environ.get("AGENT_ORCHESTRATOR_RUNTIME")
        os.environ["AGENT_ORCHESTRATOR_RUNTIME"] = str(self.root / "runtime")

    def tearDown(self):
        if self.previous_runtime is None:
            os.environ.pop("AGENT_ORCHESTRATOR_RUNTIME", None)
        else:
            os.environ["AGENT_ORCHESTRATOR_RUNTIME"] = self.previous_runtime
        self.temp.cleanup()

    def write_job(self, verifiers=()):
        return Job(
            1, "write", "Create result.txt", "target", "write", "normal", "low", "files_write",
            ("file-editing",), (), ("result.txt",), verifiers,
        )

    def test_success_keeps_artifact_and_records_hash(self):
        runner = JobRunner(self.workspace, self.orchestrator, self.registry, {"fake-write": FakeAdapter(writes={"result.txt": "ok\n"})})
        result = runner.run(self.write_job())
        self.assertEqual(result["status"], "passed")
        self.assertTrue(result["artifacts"][0]["sha256"])
        self.assertEqual((self.target / "result.txt").read_text(), "ok\n")

    def test_failure_quarantines_and_restores_exact_state(self):
        original = self.target / "original.txt"
        original.write_text("before\n", encoding="utf-8")
        adapter = FakeAdapter(fail=True, writes={"original.txt": "after\n", "new.txt": "new\n"})
        runner = JobRunner(self.workspace, self.orchestrator, self.registry, {"fake-write": adapter})
        result = runner.run(self.write_job())
        self.assertEqual(result["status"], "failed")
        self.assertTrue(result["rolled_back"])
        self.assertEqual(original.read_text(), "before\n")
        self.assertFalse((self.target / "new.txt").exists())
        self.assertTrue((self.orchestrator / result["quarantine"] / "changes.json").is_file())

    def test_readonly_snapshot_directory_can_be_discarded(self):
        # Set runtime directory to be within test temp dir for this test
        runtime_dir = self.orchestrator / ".runtime"
        os.environ["AGENT_ORCHESTRATOR_RUNTIME"] = str(runtime_dir)
        try:
            run_dir = runtime_dir / "readonly"
            run_dir.mkdir(parents=True)
            snapshot = TargetSnapshot(self.target, run_dir)
            snapshot.capture()
            os.chmod(snapshot.snapshot_dir, stat.S_IREAD)
            snapshot.discard()
            self.assertFalse(snapshot.snapshot_dir.exists())
        finally:
            os.environ["AGENT_ORCHESTRATOR_RUNTIME"] = str(self.root / "runtime")

    def test_failed_verifier_rolls_back(self):
        verifier = Verifier("fails", (sys.executable, "-c", "raise SystemExit(3)"), 10)
        runner = JobRunner(self.workspace, self.orchestrator, self.registry, {"fake-write": FakeAdapter(writes={"result.txt": "bad\n"})})
        result = runner.run(self.write_job((verifier,)))
        self.assertEqual(result["status"], "failed")
        self.assertFalse((self.target / "result.txt").exists())

    def test_write_outside_role_ownership_is_quarantined_and_rolled_back(self):
        job = replace(self.write_job(), allowed_write_paths=("result.txt",))
        adapter = FakeAdapter(writes={"result.txt": "ok\n", "docs/foreign.txt": "not owned\n"})
        runner = JobRunner(self.workspace, self.orchestrator, self.registry, {"fake-write": adapter})
        result = runner.run(job)
        self.assertEqual(result["status"], "failed")
        self.assertEqual(result["gates"]["ownership"]["violations"], ["docs/foreign.txt"])
        self.assertTrue(result["rolled_back"])
        self.assertFalse((self.target / "result.txt").exists())
        self.assertFalse((self.target / "docs" / "foreign.txt").exists())

    def test_missing_usage_is_not_reported_as_zero_cost(self):
        runner = JobRunner(self.workspace, self.orchestrator, self.registry, {"fake-write": FakeAdapter(writes={"result.txt": "ok\n"}, usage={})})
        result = runner.run(self.write_job())
        self.assertEqual(result["cost"], {"kind": "unavailable", "amount_usd": None})

    def test_free_quota_is_reported_without_requiring_token_usage(self):
        model = self.registry.models["weak"]
        provider = replace(self.registry.providers[model.provider], billing="free-account-quota", plan="free")
        self.assertEqual(JobRunner._cost(model, provider, {}), {
            "kind": "free-quota",
            "amount_usd": 0.0,
            "marginal_amount_usd": 0.0,
            "plan": "free",
            "quota_based": True,
        })

    def test_subscription_does_not_report_public_api_prices_as_run_cost(self):
        model = self.registry.models["strong"]
        provider = replace(self.registry.providers[model.provider], billing="included-subscription", plan="pro")
        self.assertEqual(JobRunner._cost(model, provider, {"prompt_tokens": 1000, "completion_tokens": 500}), {
            "kind": "included-subscription",
            "amount_usd": None,
            "marginal_amount_usd": 0.0,
            "plan": "pro",
            "fixed_subscription_cost_allocated": False,
        })

    def test_metered_api_uses_reference_token_prices(self):
        model = self.registry.models["weak"]
        provider = self.registry.providers[model.provider]
        self.assertEqual(JobRunner._cost(model, provider, {"prompt_tokens": 1000, "completion_tokens": 500}), {
            "kind": "estimated-token-cost",
            "amount_usd": 0.002,
        })

    def test_structured_output_gate_rejects_wrong_shape(self):
        schema = self.target / "schema.json"
        schema.write_text('{"type":"object","properties":{"answer":{"type":"string"}},"required":["answer"],"additionalProperties":false}', encoding="utf-8")
        job = Job(1, "schema", "Return JSON", "target", "read", "normal", "low", "inference",
                  ("summarization",), (), (), (), (), "weak-read", "schema.json")
        runner = JobRunner(self.workspace, self.orchestrator, self.registry, {"fake": FakeAdapter(final_text='{"wrong": true}')})
        result = runner.run(job)
        self.assertEqual(result["status"], "failed")
        self.assertIn("missing required", result["gates"]["output_schema"]["error"])

    def test_structured_output_gate_accepts_single_json_fence(self):
        schema = self.target / "schema.json"
        schema.write_text('{"type":"object","properties":{"answer":{"type":"string"}},"required":["answer"],"additionalProperties":false}', encoding="utf-8")
        job = Job(1, "schema-fence", "Return JSON", "target", "read", "normal", "low", "inference",
                  ("summarization",), (), (), (), (), "weak-read", "schema.json")
        adapter = FakeAdapter(final_text='```json\n{"answer": "ok"}\n```')
        result = JobRunner(self.workspace, self.orchestrator, self.registry, {"fake": adapter}).run(job)
        self.assertEqual(result["status"], "passed")


if __name__ == "__main__":
    unittest.main()
