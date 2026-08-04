import json
import hashlib
import os
from pathlib import Path
import tempfile
import unittest

from agent_orchestrator.contracts import ContractError
from agent_orchestrator.harness_contracts import load_harness
from agent_orchestrator.harness_runner import HarnessRunner, read_harness_status, resolve_harness
from agent_orchestrator.registry import Registry

from tests.helpers import write_registry


class StubRunner:
    def __init__(self, workspace, registry, runtime_root, outcomes=None, writes=None, tamper=None):
        self.workspace = workspace
        self.registry = registry
        self.runtime_root = runtime_root
        self.outcomes = {key: list(value) for key, value in (outcomes or {}).items()}
        self.writes = writes or {}
        self.tamper = tamper or {}
        self.calls = []

    def run(self, job, *, acceptance_gate=None):
        self.calls.append(job.id)
        target = self.workspace / job.target_dir
        for name, content in self.writes.get(job.id, {}).items():
            path = target / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
        outcome = self.outcomes.get(job.id, ["passed"])
        status = outcome.pop(0) if outcome else "passed"
        gate = acceptance_gate(target) if acceptance_gate and status == "passed" else {"ok": True, "artifacts": []}
        if not gate.get("ok", False):
            status = "failed"
        for name, content in self.tamper.get(job.id, {}).items():
            (target / name).write_text(content, encoding="utf-8")
        return {
            "run_id": f"run-{job.id}-{len(self.calls)}", "job": job.id, "status": status,
            "usage": {"prompt_tokens": 10, "completion_tokens": 5},
            "cost": {"kind": "estimated-token-cost", "amount_usd": 0.001},
            "artifacts": [
                {"path": name, "bytes": (target / name).stat().st_size,
                 "sha256": hashlib.sha256((target / name).read_bytes()).hexdigest()}
                for name in job.expected_artifacts if (target / name).is_file()
            ],
            "gates": {"harness": gate},
            **({"error": "synthetic failure"} if status == "failed" else {}),
        }


class HarnessTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.workspace = self.root / "workspace"
        self.orchestrator = self.workspace / "agent-orchestrator"
        self.case = self.orchestrator / "case"
        self.target = self.workspace / "target"
        self.case.mkdir(parents=True)
        self.target.mkdir()
        self.registry = Registry(write_registry(self.orchestrator))
        self.runtime = self.root / "runtime"

    def tearDown(self):
        self.temp.cleanup()

    def write_job(self, identifier, *, dependencies=(), mode="read", writes=(), artifacts=(), context=(),
                  profile="strong-read", max_tokens=100, target_dir="target", tool_class=""):
        value = {
            "schema_version": 1, "id": identifier, "objective": identifier,
            "target_dir": target_dir, "mode": mode, "importance": "low", "risk": "low",
            "tool_class": tool_class or ("files_write" if mode == "write" else "inference"),
            "dependencies": list(dependencies), "expected_artifacts": list(artifacts),
            "context": list(context), "model_profile": "strong-write" if mode == "write" else profile,
            "limits": {"timeout_seconds": 30, "max_turns": 1, "max_tokens": max_tokens},
        }
        if mode == "write":
            value["allowed_write_paths"] = list(writes)
        path = self.case / f"{identifier}.json"
        path.write_text(json.dumps(value), encoding="utf-8")
        return path

    def write_manifest(self, topology, nodes, *, handoffs=(), limits=None, repair_loop=None):
        value = {
            "schema_version": 1, "id": "test-harness", "topology": topology,
            "limits": limits or {"max_parallel": 2, "max_jobs": 10, "max_attempts": 10},
            "nodes": nodes, "handoffs": list(handoffs),
        }
        if repair_loop:
            value["repair_loop"] = repair_loop
        path = self.case / "harness.json"
        path.write_text(json.dumps(value), encoding="utf-8")
        return path

    def stub(self, **values):
        return StubRunner(self.workspace, self.registry, self.runtime, **values)

    def test_pipeline_loads_and_hash_is_stable(self):
        self.write_job("first")
        self.write_job("second", dependencies=("first",))
        path = self.write_manifest("pipeline", [
            {"job": "first.json", "role": "author"},
            {"job": "second.json", "role": "reviewer"},
        ])
        first = load_harness(path)
        second = load_harness(path)
        self.assertEqual(first.digest(), second.digest())
        self.assertEqual([item.id for item in first.nodes], ["first", "second"])

    def test_pipeline_rejects_branch(self):
        self.write_job("root")
        self.write_job("left", dependencies=("root",))
        self.write_job("right", dependencies=("root",))
        path = self.write_manifest("pipeline", [
            {"job": "root.json", "role": "root"},
            {"job": "left.json", "role": "left"},
            {"job": "right.json", "role": "right"},
        ])
        with self.assertRaisesRegex(ContractError, "connected chain"):
            load_harness(path)

    def test_parallel_overlapping_write_ownership_is_rejected(self):
        self.write_job("left", mode="write", writes=("src",))
        self.write_job("right", mode="write", writes=("src/file.txt",))
        self.write_job("join", dependencies=("left", "right"))
        path = self.write_manifest("fanout-fanin", [
            {"job": "left.json", "role": "left"}, {"job": "right.json", "role": "right"},
            {"job": "join.json", "role": "join"},
        ])
        with self.assertRaisesRegex(ContractError, "overlapping ownership"):
            load_harness(path)

    def test_canonical_nested_write_ownership_is_rejected(self):
        (self.target / "nested").mkdir()
        self.write_job("left", mode="write", writes=("nested",))
        self.write_job("right", mode="write", writes=("file.txt",), target_dir="target/nested")
        self.write_job("join", dependencies=("left", "right"))
        path = self.write_manifest("fanout-fanin", [
            {"job": "left.json", "role": "left"}, {"job": "right.json", "role": "right"},
            {"job": "join.json", "role": "join"},
        ])
        with self.assertRaisesRegex(ContractError, "canonical ownership"):
            resolve_harness(load_harness(path), self.workspace, self.stub())

    def test_read_node_rejects_write_capable_tool_class(self):
        self.write_job("only", tool_class="files_write")
        path = self.write_manifest("pipeline", [{"job": "only.json", "role": "only"}])
        with self.assertRaisesRegex(ContractError, "write-capable"):
            load_harness(path)

    def test_handoff_must_be_declared_on_both_jobs(self):
        self.write_job("producer", artifacts=("result.json",))
        self.write_job("consumer", dependencies=("producer",))
        path = self.write_manifest("pipeline", [
            {"job": "producer.json", "role": "producer"},
            {"job": "consumer.json", "role": "consumer"},
        ], handoffs=[{"from": "producer", "to": "consumer", "artifacts": [
            {"path": "result.json", "media_type": "application/json"}
        ]}])
        with self.assertRaisesRegex(ContractError, "not declared as context"):
            load_harness(path)

    def test_json_handoff_is_schema_checked_before_commit(self):
        (self.target / "schema.json").write_text(json.dumps({
            "type": "object", "required": ["answer"],
            "properties": {"answer": {"type": "string"}}, "additionalProperties": False,
        }), encoding="utf-8")
        self.write_job("producer", mode="write", writes=("result.json",), artifacts=("result.json",))
        self.write_job("consumer", dependencies=("producer",), context=("result.json",))
        path = self.write_manifest("pipeline", [
            {"job": "producer.json", "role": "producer"},
            {"job": "consumer.json", "role": "consumer"},
        ], handoffs=[{"from": "producer", "to": "consumer", "artifacts": [
            {"path": "result.json", "media_type": "application/json", "schema": "schema.json"}
        ]}])
        runner = self.stub(writes={"producer": {"result.json": '{"wrong": true}'}})
        result = HarnessRunner(self.workspace, runner).run(load_harness(path))
        self.assertEqual(result["status"], "failed")
        self.assertEqual(result["nodes"]["producer"]["status"], "failed")
        self.assertEqual(result["nodes"]["consumer"]["status"], "skipped")

    def test_immutable_handoff_detects_tampering(self):
        self.write_job("producer", mode="write", writes=("result.txt",), artifacts=("result.txt",))
        self.write_job("consumer", dependencies=("producer",), context=("result.txt",))
        path = self.write_manifest("pipeline", [
            {"job": "producer.json", "role": "producer"},
            {"job": "consumer.json", "role": "consumer"},
        ], handoffs=[{"from": "producer", "to": "consumer", "artifacts": [
            {"path": "result.txt", "media_type": "text/plain"}
        ]}])
        runner = self.stub(writes={"producer": {"result.txt": "good"}}, tamper={"producer": {"result.txt": "changed"}})
        result = HarnessRunner(self.workspace, runner).run(load_harness(path))
        self.assertEqual(result["nodes"]["consumer"]["status"], "failed")
        self.assertIn("immutable handoff changed", result["nodes"]["consumer"]["error"])

    def test_consumer_cannot_mutate_immutable_handoff(self):
        self.write_job("producer", mode="write", writes=("result.txt",), artifacts=("result.txt",))
        self.write_job("consumer", dependencies=("producer",), context=("result.txt",))
        path = self.write_manifest("pipeline", [
            {"job": "producer.json", "role": "producer"},
            {"job": "consumer.json", "role": "consumer"},
        ], handoffs=[{"from": "producer", "to": "consumer", "artifacts": [
            {"path": "result.txt", "media_type": "text/plain"}
        ]}])
        runner = self.stub(writes={"producer": {"result.txt": "good"}, "consumer": {"result.txt": "bad"}})
        result = HarnessRunner(self.workspace, runner).run(load_harness(path))
        self.assertEqual(result["nodes"]["consumer"]["status"], "failed")

    def test_first_passing_fan_in_is_manifest_ordered(self):
        self.write_job("left")
        self.write_job("right")
        self.write_job("join", dependencies=("left", "right"))
        path = self.write_manifest("fanout-fanin", [
            {"job": "left.json", "role": "candidate"},
            {"job": "right.json", "role": "candidate"},
            {"job": "join.json", "role": "join", "fan_in": {"strategy": "first-passing"}},
        ])
        result = HarnessRunner(self.workspace, self.stub()).run(load_harness(path))
        self.assertEqual(result["status"], "passed")
        self.assertEqual(result["nodes"]["join"]["selected_dependencies"], ["left"])

    def test_verifier_fan_in_selects_only_a_passed_dependency(self):
        (self.target / "selector.py").write_text(
            "import json\nprint(json.dumps({'selected_node': 'right'}))\n", encoding="utf-8"
        )
        self.write_job("left")
        self.write_job("right")
        self.write_job("join", dependencies=("left", "right"))
        path = self.write_manifest("fanout-fanin", [
            {"job": "left.json", "role": "candidate"},
            {"job": "right.json", "role": "candidate"},
            {"job": "join.json", "role": "join", "fan_in": {
                "strategy": "verifier",
                "verifier": {"id": "select", "argv": ["{python}", "selector.py"]},
            }},
        ])
        result = HarnessRunner(self.workspace, self.stub()).run(load_harness(path))
        self.assertEqual(result["status"], "passed")
        self.assertEqual(result["nodes"]["join"]["selected_dependencies"], ["right"])

    def test_all_fan_in_passes_all_successful_dependencies(self):
        self.write_job("left")
        self.write_job("right")
        self.write_job("join", dependencies=("left", "right"))
        path = self.write_manifest("fanout-fanin", [
            {"job": "left.json", "role": "candidate"},
            {"job": "right.json", "role": "candidate"},
            {"job": "join.json", "role": "join"},
        ])
        result = HarnessRunner(self.workspace, self.stub(outcomes={"left": ["failed"]})).run(load_harness(path))
        self.assertEqual(result["nodes"]["join"]["status"], "passed")
        self.assertEqual(result["nodes"]["join"]["selected_dependencies"], ["right"])

    def test_node_retry_is_bounded(self):
        self.write_job("only")
        path = self.write_manifest("pipeline", [
            {"job": "only.json", "role": "worker", "max_attempts": 2},
        ], limits={"max_parallel": 1, "max_jobs": 1, "max_attempts": 2})
        runner = self.stub(outcomes={"only": ["failed", "passed"]})
        result = HarnessRunner(self.workspace, runner).run(load_harness(path))
        self.assertEqual(result["status"], "passed")
        self.assertEqual(runner.calls, ["only", "only"])

    def test_budget_stops_new_nodes(self):
        self.write_job("first", max_tokens=100)
        self.write_job("second", dependencies=("first",), max_tokens=100)
        path = self.write_manifest("pipeline", [
            {"job": "first.json", "role": "first"}, {"job": "second.json", "role": "second"},
        ], limits={"max_parallel": 1, "max_jobs": 2, "max_attempts": 2, "max_tokens": 15})
        result = HarnessRunner(self.workspace, self.stub()).run(load_harness(path))
        self.assertEqual(result["nodes"]["second"]["status"], "budget-stopped")
        self.assertEqual(result["budget"]["stop_reason"], "max-tokens")

    def test_strict_usage_rejects_unmeasured_provider(self):
        self.write_job("only")
        path = self.write_manifest("pipeline", [{"job": "only.json", "role": "only"}],
                                   limits={"max_parallel": 1, "max_jobs": 1, "max_attempts": 1, "max_tokens": 100})
        provider = self.registry.providers["test-provider"]
        object.__setattr__(provider, "usage_reporting", "unavailable")
        with self.assertRaisesRegex(ContractError, "measured usage"):
            resolve_harness(load_harness(path), self.workspace, self.stub())

    def test_strict_cost_rejects_unmeasured_free_provider(self):
        self.write_job("only")
        path = self.write_manifest("pipeline", [{"job": "only.json", "role": "only"}],
                                   limits={"max_parallel": 1, "max_jobs": 1, "max_attempts": 1,
                                           "max_cost_usd": 1.0})
        provider = self.registry.providers["test-provider"]
        object.__setattr__(provider, "billing", "free-account-quota")
        object.__setattr__(provider, "usage_reporting", "unavailable")
        with self.assertRaisesRegex(ContractError, "strict cost"):
            resolve_harness(load_harness(path), self.workspace, self.stub())

    def test_unknown_repair_node_is_contract_error(self):
        self.write_job("work")
        self.write_job("verify", dependencies=("work",))
        self.write_job("repair", dependencies=("verify",), mode="write", writes=("fix.txt",))
        path = self.write_manifest("repair", [
            {"job": "work.json", "role": "work"},
            {"job": "verify.json", "role": "verify", "max_attempts": 2},
            {"job": "repair.json", "role": "repair"},
        ], limits={"max_parallel": 1, "max_jobs": 3, "max_attempts": 4},
            repair_loop={"work_node": "missing", "verify_node": "verify", "repair_node": "repair", "max_cycles": 1})
        with self.assertRaisesRegex(ContractError, "unknown nodes"):
            load_harness(path)

    def test_dry_run_creates_no_evidence(self):
        self.write_job("only")
        path = self.write_manifest("pipeline", [{"job": "only.json", "role": "only"}])
        result = HarnessRunner(self.workspace, self.stub()).run(load_harness(path), dry_run=True)
        self.assertTrue(result["dry_run"])
        self.assertFalse((self.runtime / "harness-runs").exists())

    def test_repair_loop_is_bounded_and_rechecks(self):
        self.write_job("work")
        self.write_job("verify", dependencies=("work",))
        self.write_job("repair", dependencies=("verify",), mode="write", writes=("fix.txt",))
        path = self.write_manifest("repair", [
            {"job": "work.json", "role": "work"},
            {"job": "verify.json", "role": "verify", "max_attempts": 2},
            {"job": "repair.json", "role": "repair", "max_attempts": 1},
        ], limits={"max_parallel": 1, "max_jobs": 3, "max_attempts": 4},
            repair_loop={"work_node": "work", "verify_node": "verify", "repair_node": "repair", "max_cycles": 1})
        runner = self.stub(outcomes={"verify": ["failed", "passed"]})
        result = HarnessRunner(self.workspace, runner).run(load_harness(path))
        self.assertEqual(result["status"], "passed")
        self.assertEqual(runner.calls, ["work", "verify", "repair", "verify"])

    def test_resume_reuses_only_unchanged_nodes(self):
        self.write_job("first", mode="write", writes=("result.txt",), artifacts=("result.txt",))
        self.write_job("second", dependencies=("first",), context=("result.txt",))
        path = self.write_manifest("pipeline", [
            {"job": "first.json", "role": "first"}, {"job": "second.json", "role": "second"},
        ], handoffs=[{"from": "first", "to": "second", "artifacts": [
            {"path": "result.txt", "media_type": "text/plain"}
        ]}])
        first_runner = self.stub(writes={"first": {"result.txt": "stable"}})
        first = HarnessRunner(self.workspace, first_runner).run(load_harness(path))
        second_runner = self.stub()
        second = HarnessRunner(self.workspace, second_runner).run(load_harness(path), resume=first["run_id"])
        self.assertEqual(second["status"], "passed")
        self.assertEqual(second_runner.calls, [])
        self.assertEqual(read_harness_status(self.runtime, second["run_id"])["run_id"], second["run_id"])

    def test_resume_reruns_changed_artifact_and_downstream(self):
        self.write_job("first", mode="write", writes=("result.txt",), artifacts=("result.txt",))
        self.write_job("second", dependencies=("first",), context=("result.txt",))
        path = self.write_manifest("pipeline", [
            {"job": "first.json", "role": "first"}, {"job": "second.json", "role": "second"},
        ], handoffs=[{"from": "first", "to": "second", "artifacts": [
            {"path": "result.txt", "media_type": "text/plain"}
        ]}])
        first = HarnessRunner(self.workspace, self.stub(writes={"first": {"result.txt": "stable"}})).run(load_harness(path))
        (self.target / "result.txt").write_text("changed", encoding="utf-8")
        runner = self.stub()
        result = HarnessRunner(self.workspace, runner).run(load_harness(path), resume=first["run_id"])
        self.assertEqual(result["status"], "passed")
        self.assertEqual(runner.calls, ["first", "second"])

    def test_resume_hashes_final_artifacts_without_handoffs(self):
        self.write_job("only", mode="write", writes=("final.txt",), artifacts=("final.txt",))
        path = self.write_manifest("pipeline", [{"job": "only.json", "role": "only"}])
        first = HarnessRunner(self.workspace, self.stub(writes={"only": {"final.txt": "stable"}})).run(load_harness(path))
        (self.target / "final.txt").write_text("changed", encoding="utf-8")
        runner = self.stub()
        HarnessRunner(self.workspace, runner).run(load_harness(path), resume=first["run_id"])
        self.assertEqual(runner.calls, ["only"])

    def test_resume_reuses_unchanged_final_artifact(self):
        self.write_job("only", mode="write", writes=("final.txt",), artifacts=("final.txt",))
        path = self.write_manifest("pipeline", [{"job": "only.json", "role": "only"}])
        first = HarnessRunner(self.workspace, self.stub(writes={"only": {"final.txt": "stable"}})).run(load_harness(path))
        runner = self.stub()
        HarnessRunner(self.workspace, runner).run(load_harness(path), resume=first["run_id"])
        self.assertEqual(runner.calls, [])

    def test_repair_resume_reuses_completed_run(self):
        self.write_job("work")
        self.write_job("verify", dependencies=("work",))
        self.write_job("repair", dependencies=("verify",), mode="write", writes=("fix.txt",))
        path = self.write_manifest("repair", [
            {"job": "work.json", "role": "work"},
            {"job": "verify.json", "role": "verify", "max_attempts": 2},
            {"job": "repair.json", "role": "repair", "max_attempts": 1},
        ], limits={"max_parallel": 1, "max_jobs": 3, "max_attempts": 4},
            repair_loop={"work_node": "work", "verify_node": "verify", "repair_node": "repair", "max_cycles": 1})
        first = HarnessRunner(self.workspace, self.stub(outcomes={"verify": ["failed", "passed"]})).run(load_harness(path))
        runner = self.stub()
        second = HarnessRunner(self.workspace, runner).run(load_harness(path), resume=first["run_id"])
        self.assertEqual(second["status"], "passed")
        self.assertEqual(runner.calls, [])


if __name__ == "__main__":
    unittest.main()
