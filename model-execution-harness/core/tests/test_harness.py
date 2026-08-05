from __future__ import annotations

import hashlib
import json
import sys
import tempfile
import unittest
from unittest.mock import patch
from pathlib import Path
from types import SimpleNamespace


HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE))

import harness  # noqa: E402


def write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value), encoding="utf-8")


class HarnessTests(unittest.TestCase):
    def setUp(self) -> None:
        self.vibe_preflight = patch(
            "harness.check_vibe_session_directory",
            return_value={"status": "passed", "session_root": "test"},
        )
        self.vibe_preflight.start()
        self.temp = tempfile.TemporaryDirectory()
        self.repo = Path(self.temp.name)
        self.target = self.repo / "target"
        self.target.mkdir()
        (self.target / "input.txt").write_text(
            "one\ntwo\nthree\nfour\n", encoding="utf-8"
        )
        self.task = {
            "v": harness.CONTRACT_VERSION,
            "id": "task-1",
            "kind": "coding",
            "depends_on": [],
            "goal": "Update an allowed artifact.",
            "target": "target",
            "model": {
                "profile": "ollama-ornith-9b",
                "capability": "summarization",
                "importance": "normal",
            },
            "context": [{"path": "input.txt", "start": 2, "end": 3}],
            "write_roots": ["out/result.txt"],
            "allowed_commands": [
                ["{python}", "-m", "unittest", "discover", "-s", "tests", "-v"]
            ],
            "done": ["out/result.txt exists"],
            "forbidden": ["No network"],
            "limits": {
                "packet_chars": 4000,
                "output_chars": 4000,
                "model_context_tokens": 4096,
                "model_session_tokens": 300000,
                "model_output_tokens": 256,
                "model_timeout_seconds": 30,
                "max_tool_calls": 24,
                "max_verifiers": 1,
                "verifier_timeout_seconds": 10,
            },
            "verifiers": [
                {
                    "id": "content",
                    "argv": [
                        "{python}",
                        "-c",
                        "from pathlib import Path; raise SystemExit(0 if Path('out/result.txt').read_text() == 'ok\\n' else 1)",
                    ],
                }
            ],
        }
        self.task_path = self.repo / "task.json"
        self.packet_path = self.repo / "packet.json"
        self.ack_path = self.repo / "ack.json"
        self.baseline_path = self.repo / "baseline.json"
        self.result_path = self.repo / "result.json"
        write_json(self.task_path, self.task)

    def tearDown(self) -> None:
        self.vibe_preflight.stop()
        self.temp.cleanup()

    def pack_and_accept(self) -> dict:
        harness.command_pack(self.task_path, self.packet_path, self.repo)
        harness.command_accept(
            self.packet_path, self.ack_path, worker="worker-1", reject_reason=None
        )
        return harness.read_json(self.packet_path)

    def test_pack_uses_only_requested_line_slice(self) -> None:
        summary = harness.command_pack(
            self.task_path, self.packet_path, self.repo
        )
        packet = harness.read_json(self.packet_path)
        self.assertEqual("two\nthree\n", packet["excerpts"][0]["text"])
        self.assertEqual(10, summary["excerpt_chars"])
        self.assertLessEqual(summary["packet_chars"], summary["packet_budget"])
        self.assertNotIn("one", packet["excerpts"][0]["text"])
        self.assertNotIn("four", packet["excerpts"][0]["text"])

    def test_pack_reference_contains_path_and_digest_without_source_text(self) -> None:
        self.task["context"] = [{"path": "input.txt"}]
        write_json(self.task_path, self.task)
        summary = harness.command_pack(self.task_path, self.packet_path, self.repo)
        packet = harness.read_json(self.packet_path)
        self.assertEqual(
            {"path", "sha256"},
            set(packet["excerpts"][0]),
        )
        self.assertEqual("input.txt", packet["excerpts"][0]["path"])
        self.assertEqual(0, summary["excerpt_chars"])
        self.assertEqual(1, summary["context_references"])
        self.assertEqual(0, summary["embedded_excerpts"])

    def test_snapshot_rejects_reference_changed_after_pack(self) -> None:
        self.task["context"] = [{"path": "input.txt"}]
        write_json(self.task_path, self.task)
        self.pack_and_accept()
        (self.target / "input.txt").write_text("changed\n", encoding="utf-8")
        with self.assertRaisesRegex(harness.Rejected, "context changed"):
            harness.command_snapshot(
                self.task_path,
                self.packet_path,
                self.ack_path,
                self.baseline_path,
                self.repo,
            )

    def test_pack_rejects_path_escape(self) -> None:
        self.task["context"][0]["path"] = "../outside.txt"
        write_json(self.task_path, self.task)
        with self.assertRaises(harness.Rejected):
            harness.command_pack(self.task_path, self.packet_path, self.repo)

    def test_pack_rejects_likely_secret(self) -> None:
        (self.target / ".env").write_text("API_KEY=abcdefghijk\n", encoding="utf-8")
        self.task["context"] = [{"path": ".env", "start": 1, "end": 1}]
        write_json(self.task_path, self.task)
        with self.assertRaisesRegex(harness.Rejected, "secret"):
            harness.command_pack(self.task_path, self.packet_path, self.repo)

    def test_task_rejects_unadmitted_worker_command(self) -> None:
        self.task["allowed_commands"] = [["powershell", "-Command", "whoami"]]
        write_json(self.task_path, self.task)
        with self.assertRaisesRegex(harness.Rejected, "not globally admitted"):
            harness.command_pack(self.task_path, self.packet_path, self.repo)

    def test_task_rejects_session_budget_below_context(self) -> None:
        self.task["limits"]["model_session_tokens"] = 2048
        write_json(self.task_path, self.task)
        with self.assertRaisesRegex(harness.Rejected, "must cover"):
            harness.command_pack(self.task_path, self.packet_path, self.repo)

    def test_pack_caps_the_complete_packet(self) -> None:
        self.task["limits"]["packet_chars"] = 256
        write_json(self.task_path, self.task)
        with self.assertRaisesRegex(harness.Rejected, "complete worker packet"):
            harness.command_pack(self.task_path, self.packet_path, self.repo)

    def test_tampered_packet_is_rejected(self) -> None:
        self.pack_and_accept()
        packet = harness.read_json(self.packet_path)
        packet["excerpts"][0]["text"] = "tampered"
        write_json(self.packet_path, packet)
        with self.assertRaisesRegex(harness.Rejected, "digest mismatch"):
            harness.validate_packet(packet)

    def test_gate_checks_digest_scope_and_verifier(self) -> None:
        packet = self.pack_and_accept()
        artifact = self.target / "out" / "result.txt"
        artifact.parent.mkdir()
        artifact.write_text("ok\n", encoding="utf-8")
        result = {
            "v": harness.CONTRACT_VERSION,
            "task_id": self.task["id"],
            "packet_sha256": harness.digest_value(packet),
            "status": "done",
            "summary": "Created the artifact.",
            "changed": [
                {
                    "path": "out/result.txt",
                    "sha256": hashlib.sha256(artifact.read_bytes()).hexdigest(),
                }
            ],
            "risks": [],
        }
        write_json(self.result_path, result)
        output = harness.command_gate(
            self.task_path,
            self.packet_path,
            self.ack_path,
            self.result_path,
            self.repo,
        )
        self.assertEqual("passed", output["status"])
        self.assertEqual(0, output["checks"][0]["exit_code"])

    def test_gate_rejects_file_outside_write_roots(self) -> None:
        packet = self.pack_and_accept()
        artifact = self.target / "input.txt"
        result = {
            "v": harness.CONTRACT_VERSION,
            "task_id": self.task["id"],
            "packet_sha256": harness.digest_value(packet),
            "status": "done",
            "summary": "Changed the wrong file.",
            "changed": [
                {
                    "path": "input.txt",
                    "sha256": hashlib.sha256(artifact.read_bytes()).hexdigest(),
                }
            ],
            "risks": [],
        }
        write_json(self.result_path, result)
        with self.assertRaisesRegex(harness.Rejected, "outside write_roots"):
            harness.command_gate(
                self.task_path,
                self.packet_path,
                self.ack_path,
                self.result_path,
                self.repo,
            )

    def test_baseline_gate_accepts_exact_reported_changes(self) -> None:
        packet = self.pack_and_accept()
        snapshot = harness.command_snapshot(
            self.task_path,
            self.packet_path,
            self.ack_path,
            self.baseline_path,
            self.repo,
        )
        artifact = self.target / "out" / "result.txt"
        artifact.parent.mkdir()
        artifact.write_text("ok\n", encoding="utf-8")
        result = {
            "v": harness.CONTRACT_VERSION,
            "task_id": self.task["id"],
            "packet_sha256": harness.digest_value(packet),
            "status": "done",
            "summary": "Created the exact artifact.",
            "changed": [
                {
                    "path": "out/result.txt",
                    "sha256": hashlib.sha256(artifact.read_bytes()).hexdigest(),
                }
            ],
            "risks": [],
        }
        write_json(self.result_path, result)
        output = harness.command_gate(
            self.task_path,
            self.packet_path,
            self.ack_path,
            self.result_path,
            self.repo,
            self.baseline_path,
        )
        self.assertEqual("passed", output["status"])
        self.assertEqual(1, output["baseline_audit"]["changed_paths"])
        self.assertEqual(snapshot["baseline_sha256"], output["baseline_audit"]["sha256"])

    @patch("harness.run_mistral_vibe_worker")
    @patch("harness.select_model")
    def test_execute_persists_trajectory_and_derives_result(
        self, select_model, run_worker
    ) -> None:
        self.task["model"] = {
            "profile": "devstral-small",
            "capability": "coding",
            "importance": "normal",
        }
        self.task["allowed_commands"] = [["git", "status", "--short"]]
        write_json(self.task_path, self.task)
        packet = self.pack_and_accept()
        harness.command_snapshot(
            self.task_path,
            self.packet_path,
            self.ack_path,
            self.baseline_path,
            self.repo,
        )
        trajectory = self.repo / "trajectory.json"
        select_model.return_value = (
            SimpleNamespace(
                id="devstral-small",
                provider="mistral-vibe",
                model="devstral-small",
            ),
            {},
        )

        def execute(*args, **kwargs):
            artifact = self.target / "out" / "result.txt"
            artifact.parent.mkdir()
            artifact.write_text("ok\n", encoding="utf-8")
            kwargs["trajectory_path"].write_text(
                '[{"role":"assistant","content":"full trajectory"}]',
                encoding="utf-8",
            )
            return {
                "success": True,
                "exit_code": 0,
                "error": "",
                "trajectory": str(kwargs["trajectory_path"]),
                "trajectory_sha256": hashlib.sha256(
                    kwargs["trajectory_path"].read_bytes()
                ).hexdigest(),
                "stderr": "",
                "context_window_tokens": 4096,
                "session_token_budget": 16384,
                "compaction_threshold_tokens": 4096,
                "attestation": {"expected_model": "devstral-small", "matched": True},
            }

        run_worker.side_effect = execute
        output = harness.command_execute(
            self.packet_path,
            self.ack_path,
            self.baseline_path,
            self.result_path,
            trajectory,
            self.repo,
            self.repo / "models.json",
            "http://127.0.0.1:11434",
        )
        result = harness.read_json(self.result_path)
        self.assertEqual("completed", output["status"])
        self.assertEqual(1, output["changed_files"])
        self.assertNotIn("full trajectory", json.dumps(output))
        self.assertEqual("out/result.txt", result["changed"][0]["path"])
        gated = harness.command_gate(
            self.task_path,
            self.packet_path,
            self.ack_path,
            self.result_path,
            self.repo,
            self.baseline_path,
        )
        self.assertEqual("passed", gated["status"])

    @patch("harness.run_mistral_vibe_worker")
    @patch("harness.select_model")
    def test_execute_rejects_chat_only_completion(
        self, select_model, run_worker
    ) -> None:
        self.task["model"] = {
            "profile": "mistral-medium-3.5",
            "capability": "planning",
            "importance": "normal",
        }
        write_json(self.task_path, self.task)
        self.pack_and_accept()
        harness.command_snapshot(
            self.task_path,
            self.packet_path,
            self.ack_path,
            self.baseline_path,
            self.repo,
        )
        trajectory = self.repo / "trajectory.json"
        select_model.return_value = (
            SimpleNamespace(
                id="mistral-medium-3.5",
                provider="mistral-vibe",
                model="mistral-medium-3.5",
            ),
            {},
        )

        def execute(*args, **kwargs):
            kwargs["trajectory_path"].write_text("[]", encoding="utf-8")
            return {
                "success": True,
                "exit_code": 0,
                "error": "",
                "trajectory": str(kwargs["trajectory_path"]),
                "trajectory_sha256": hashlib.sha256(
                    kwargs["trajectory_path"].read_bytes()
                ).hexdigest(),
                "stderr": "",
                "context_window_tokens": 4096,
                "session_token_budget": 16384,
                "compaction_threshold_tokens": 4096,
                "attestation": {"expected_model": "mistral-medium-3.5", "matched": True},
            }

        run_worker.side_effect = execute
        output = harness.command_execute(
            self.packet_path,
            self.ack_path,
            self.baseline_path,
            self.result_path,
            trajectory,
            self.repo,
            self.repo / "models.json",
            "http://127.0.0.1:11434",
        )
        result = harness.read_json(self.result_path)
        self.assertEqual("worker_failed", output["status"])
        self.assertEqual("failed", result["status"])
        self.assertIn("without changing a durable artifact", result["risks"][0])

    def test_baseline_gate_rejects_unreported_change(self) -> None:
        packet = self.pack_and_accept()
        harness.command_snapshot(
            self.task_path,
            self.packet_path,
            self.ack_path,
            self.baseline_path,
            self.repo,
        )
        artifact = self.target / "out" / "result.txt"
        artifact.parent.mkdir()
        artifact.write_text("ok\n", encoding="utf-8")
        (self.target / "out" / "extra.txt").write_text("unreported\n", encoding="utf-8")
        result = {
            "v": harness.CONTRACT_VERSION,
            "task_id": self.task["id"],
            "packet_sha256": harness.digest_value(packet),
            "status": "done",
            "summary": "Omitted one changed file.",
            "changed": [
                {
                    "path": "out/result.txt",
                    "sha256": hashlib.sha256(artifact.read_bytes()).hexdigest(),
                }
            ],
            "risks": [],
        }
        write_json(self.result_path, result)
        with self.assertRaisesRegex(harness.Rejected, "outside write_roots"):
            harness.command_gate(
                self.task_path,
                self.packet_path,
                self.ack_path,
                self.result_path,
                self.repo,
                self.baseline_path,
            )

    def test_baseline_gate_ignores_validated_result_envelope_inside_target(self) -> None:
        packet = self.pack_and_accept()
        harness.command_snapshot(
            self.task_path,
            self.packet_path,
            self.ack_path,
            self.baseline_path,
            self.repo,
        )
        artifact = self.target / "out" / "result.txt"
        artifact.parent.mkdir()
        artifact.write_text("ok\n", encoding="utf-8")
        target_result = self.target / ".state" / "result.json"
        target_result.parent.mkdir()
        write_json(
            target_result,
            {
                "v": harness.CONTRACT_VERSION,
                "task_id": self.task["id"],
                "packet_sha256": harness.digest_value(packet),
                "status": "done",
                "summary": "Created the exact artifact.",
                "changed": [
                    {
                        "path": "out/result.txt",
                        "sha256": hashlib.sha256(artifact.read_bytes()).hexdigest(),
                    }
                ],
                "risks": [],
            },
        )
        output = harness.command_gate(
            self.task_path,
            self.packet_path,
            self.ack_path,
            target_result,
            self.repo,
            self.baseline_path,
        )
        self.assertEqual(1, output["baseline_audit"]["changed_paths"])

    def test_baseline_gate_rejects_deleted_target_file(self) -> None:
        packet = self.pack_and_accept()
        harness.command_snapshot(
            self.task_path,
            self.packet_path,
            self.ack_path,
            self.baseline_path,
            self.repo,
        )
        (self.target / "input.txt").unlink()
        result = {
            "v": harness.CONTRACT_VERSION,
            "task_id": self.task["id"],
            "packet_sha256": harness.digest_value(packet),
            "status": "done",
            "summary": "Deleted an input.",
            "changed": [],
            "risks": [],
        }
        write_json(self.result_path, result)
        with self.assertRaisesRegex(harness.Rejected, "were deleted"):
            harness.command_gate(
                self.task_path,
                self.packet_path,
                self.ack_path,
                self.result_path,
                self.repo,
                self.baseline_path,
            )

    def test_snapshot_rejects_baseline_inside_target(self) -> None:
        self.pack_and_accept()
        with self.assertRaisesRegex(harness.Rejected, "outside the task target"):
            harness.command_snapshot(
                self.task_path,
                self.packet_path,
                self.ack_path,
                self.target / "baseline.json",
                self.repo,
            )

    def test_snapshot_requires_matching_accepted_acknowledgement(self) -> None:
        self.pack_and_accept()
        ack = harness.read_json(self.ack_path)
        ack["accepted"] = False
        ack["reason"] = "worker declined"
        write_json(self.ack_path, ack)
        with self.assertRaisesRegex(harness.Rejected, "accepted acknowledgement"):
            harness.command_snapshot(
                self.task_path,
                self.packet_path,
                self.ack_path,
                self.baseline_path,
                self.repo,
            )

    def test_gate_rejects_unbound_acknowledgement(self) -> None:
        packet = self.pack_and_accept()
        ack = harness.read_json(self.ack_path)
        ack["packet_sha256"] = "0" * 64
        write_json(self.ack_path, ack)
        result = {
            "v": harness.CONTRACT_VERSION,
            "task_id": self.task["id"],
            "packet_sha256": harness.digest_value(packet),
            "status": "done",
            "summary": "No changes.",
            "changed": [],
            "risks": [],
        }
        write_json(self.result_path, result)
        with self.assertRaisesRegex(harness.Rejected, "another task"):
            harness.command_gate(
                self.task_path,
                self.packet_path,
                self.ack_path,
                self.result_path,
                self.repo,
            )

    def test_v1_task_is_rejected_without_compatibility_mode(self) -> None:
        self.task["v"] = 1
        write_json(self.task_path, self.task)
        with self.assertRaisesRegex(harness.Rejected, "unsupported task version"):
            harness.command_pack(self.task_path, self.packet_path, self.repo)

    def test_target_manifest_uses_ordinal_posix_path_order(self) -> None:
        (self.target / "__pycache__").mkdir()
        (self.target / "__pycache__" / "cache.pyc").write_bytes(b"cache")
        (self.target / "AGENTS.md").write_text("agent\n", encoding="utf-8")
        (self.target / "README.md").write_text("readme\n", encoding="utf-8")
        labels = [item["path"] for item in harness.target_manifest(self.target)]
        self.assertEqual(sorted(labels), labels)
        self.assertLess(labels.index("AGENTS.md"), labels.index("__pycache__/cache.pyc"))

    def test_snapshot_output_self_validates_with_mixed_case_paths(self) -> None:
        (self.target / "__pycache__").mkdir()
        (self.target / "__pycache__" / "cache.pyc").write_bytes(b"cache")
        (self.target / "AGENTS.md").write_text("agent\n", encoding="utf-8")
        self.pack_and_accept()
        harness.command_snapshot(
            self.task_path,
            self.packet_path,
            self.ack_path,
            self.baseline_path,
            self.repo,
        )
        harness.validate_baseline(harness.read_json(self.baseline_path))

    def test_coding_task_requires_worker_loop_command(self) -> None:
        self.task["allowed_commands"] = []
        write_json(self.task_path, self.task)
        with self.assertRaisesRegex(harness.Rejected, "worker-loop test commands"):
            harness.command_pack(self.task_path, self.packet_path, self.repo)

    def test_write_roots_must_be_exact_and_non_overlapping(self) -> None:
        self.task["write_roots"] = ["out", "out/result.txt"]
        write_json(self.task_path, self.task)
        with self.assertRaisesRegex(harness.Rejected, "must not overlap"):
            harness.command_pack(self.task_path, self.packet_path, self.repo)

    def test_preflight_checks_registered_capacity_and_complete_packet(self) -> None:
        self.task["model"] = {
            "profile": "devstral-small",
            "capability": "coding",
            "importance": "high",
        }
        write_json(self.task_path, self.task)
        output = harness.command_preflight(
            self.task_path,
            self.repo,
            HERE / "models.json",
        )
        self.assertEqual("passed", output["status"])
        self.assertEqual(1, output["worker_test_commands"])
        self.assertEqual(1, output["independent_verifiers"])
        self.assertEqual(0, output["context_references"])
        self.assertEqual("passed", output["runtime_check"]["status"])

    def test_preflight_rejects_directory_write_root(self) -> None:
        self.task["write_roots"] = ["out"]
        (self.target / "out").mkdir()
        self.task["model"] = {
            "profile": "devstral-small",
            "capability": "coding",
            "importance": "high",
        }
        write_json(self.task_path, self.task)
        with self.assertRaisesRegex(harness.Rejected, "must name a file"):
            harness.command_preflight(self.task_path, self.repo, HERE / "models.json")

    def test_materialize_plan_writes_dependency_ordered_tasks(self) -> None:
        first = json.loads(json.dumps(self.task))
        first["id"] = "first"
        first["model"]["profile"] = "devstral-small"
        first["model"]["capability"] = "coding"
        second = json.loads(json.dumps(self.task))
        second["id"] = "second"
        second["model"]["profile"] = "devstral-small"
        second["model"]["capability"] = "coding"
        second["depends_on"] = ["first"]
        second["write_roots"] = ["out/second.txt"]
        plan_path = self.repo / "plan.json"
        write_json(
            plan_path,
            {"v": harness.CONTRACT_VERSION, "id": "plan-1", "completed": [], "tasks": [first, second]},
        )
        output = harness.command_materialize_plan(
            plan_path,
            self.repo / "materialized",
            self.repo,
            HERE / "models.json",
        )
        self.assertEqual("materialized", output["status"])
        self.assertEqual(2, len(output["tasks"]))
        self.assertTrue((self.repo / "materialized" / "01-first.task.json").is_file())

    def test_materialize_plan_rejects_unresolved_dependency(self) -> None:
        task = json.loads(json.dumps(self.task))
        task["model"]["profile"] = "devstral-small"
        task["model"]["capability"] = "coding"
        task["depends_on"] = ["missing"]
        plan_path = self.repo / "plan.json"
        write_json(
            plan_path,
            {"v": harness.CONTRACT_VERSION, "id": "plan-1", "completed": [], "tasks": [task]},
        )
        with self.assertRaisesRegex(harness.Rejected, "unresolved dependencies"):
            harness.command_materialize_plan(
                plan_path, self.repo / "tasks", self.repo, HERE / "models.json"
            )

    def test_materialize_plan_preflights_before_writing(self) -> None:
        task = json.loads(json.dumps(self.task))
        task["model"]["profile"] = "devstral-small"
        task["model"]["capability"] = "coding"
        task["context"][0]["start"] = 999
        task["context"][0]["end"] = 999
        plan_path = self.repo / "plan.json"
        output_dir = self.repo / "tasks"
        write_json(
            plan_path,
            {"v": harness.CONTRACT_VERSION, "id": "plan-1", "completed": [], "tasks": [task]},
        )
        with self.assertRaisesRegex(harness.Rejected, "starts after EOF"):
            harness.command_materialize_plan(
                plan_path, output_dir, self.repo, HERE / "models.json"
            )
        self.assertFalse(output_dir.exists())

    def test_diagnose_classifies_token_limit(self) -> None:
        stderr = self.repo / "stderr.txt"
        stderr.write_text("Token limit exceeded: 241176 > 240000", encoding="utf-8")
        output = harness.command_diagnose(None, stderr)
        self.assertEqual("token-limit", output["failure_kind"])

    @patch("harness.command_gate")
    @patch("harness.command_execute")
    @patch("harness.command_route")
    def test_run_stops_before_gate_when_worker_fails(
        self, command_route, command_execute, command_gate
    ) -> None:
        self.task["model"] = {
            "profile": "devstral-small",
            "capability": "coding",
            "importance": "high",
        }
        write_json(self.task_path, self.task)
        command_route.return_value = {"status": "routed", "profile": "devstral-small"}

        def fail_execute(packet, ack, baseline, result, trajectory, *args):
            packet_value = harness.read_json(packet)
            write_json(
                result,
                {
                    "v": harness.CONTRACT_VERSION,
                    "task_id": self.task["id"],
                    "packet_sha256": harness.digest_value(packet_value),
                    "status": "failed",
                    "summary": "Worker failed.",
                    "changed": [],
                    "risks": ["Token limit exceeded"],
                },
            )
            return {"status": "worker_failed", "stderr": ""}

        command_execute.side_effect = fail_execute
        output = harness.command_run(
            self.task_path,
            self.repo / "evidence",
            "worker-1",
            self.repo,
            HERE / "models.json",
            "http://127.0.0.1:11434",
        )
        self.assertEqual("worker_failed", output["status"])
        self.assertEqual("token-limit", output["diagnosis"]["failure_kind"])
        command_gate.assert_not_called()

    @patch("harness.command_execute")
    @patch("harness.command_route")
    def test_run_success_writes_compact_index_and_gate(
        self, command_route, command_execute
    ) -> None:
        self.task["model"] = {
            "profile": "devstral-small",
            "capability": "coding",
            "importance": "high",
        }
        write_json(self.task_path, self.task)
        command_route.return_value = {"status": "routed", "profile": "devstral-small"}

        def complete_execute(packet, ack, baseline, result, trajectory, *args):
            artifact = self.target / "out" / "result.txt"
            artifact.parent.mkdir()
            artifact.write_text("ok\n", encoding="utf-8")
            packet_value = harness.read_json(packet)
            write_json(
                result,
                {
                    "v": harness.CONTRACT_VERSION,
                    "task_id": self.task["id"],
                    "packet_sha256": harness.digest_value(packet_value),
                    "status": "done",
                    "summary": "Completed.",
                    "changed": [
                        {"path": "out/result.txt", "sha256": harness.digest_file(artifact)}
                    ],
                    "risks": [],
                },
            )
            trajectory.write_text("[]", encoding="utf-8")
            return {"status": "completed", "stderr": "", "changed_files": 1}

        command_execute.side_effect = complete_execute
        evidence = self.repo / "evidence"
        output = harness.command_run(
            self.task_path,
            evidence,
            "worker-1",
            self.repo,
            HERE / "models.json",
            "http://127.0.0.1:11434",
        )
        self.assertEqual("passed", output["status"])
        self.assertEqual("passed", output["gate"]["status"])
        self.assertTrue((evidence / "run.json").is_file())
        self.assertTrue((evidence / "gate.json").is_file())

    @patch("harness.run_model_canary")
    @patch("harness.model_inventory")
    def test_canary_requires_exact_response(self, inventory, run_canary) -> None:
        inventory.return_value = {
            "profiles": [
                {"id": "ollama-ministral-3-8b", "available": True}
            ]
        }
        run_canary.return_value = {
            "text": "SMALL_CONTEXT_CANARY_OK",
            "usage": {"prompt_tokens": 10, "completion_tokens": 5},
            "attestation": {"matched": True},
        }
        output = harness.command_canary(
            "ollama-ministral-3-8b",
            HERE / "models.json",
            "http://127.0.0.1:11434",
            30,
        )
        self.assertEqual("passed", output["status"])

    def test_v3_status_and_approval_use_one_initiative_manifest(self) -> None:
        manifest_path = self.target / "orchestration.json"
        manifest = {
            "v": 3,
            "id": "initiative-1",
            "tasks": [{
                "id": self.task["id"],
                "state": "blocked",
                "task": self.task,
                "blocked": "token-limit",
            }],
        }
        write_json(manifest_path, manifest)
        status = harness.command_status(self.target, self.repo)
        self.assertEqual("blocked", status["tasks"][0]["state"])
        approved = harness.command_approve(self.target, self.task["id"], self.repo)
        self.assertEqual("approved", approved["status"])
        updated = harness.read_json(manifest_path)
        self.assertEqual("ready", updated["tasks"][0]["state"])
        self.assertIsNone(updated["tasks"][0]["blocked"])


if __name__ == "__main__":
    unittest.main()
