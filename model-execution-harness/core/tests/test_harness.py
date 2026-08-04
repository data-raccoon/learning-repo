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
        self.temp = tempfile.TemporaryDirectory()
        self.repo = Path(self.temp.name)
        self.target = self.repo / "target"
        self.target.mkdir()
        (self.target / "input.txt").write_text(
            "one\ntwo\nthree\nfour\n", encoding="utf-8"
        )
        self.task = {
            "v": 1,
            "id": "task-1",
            "goal": "Update an allowed artifact.",
            "target": "target",
            "model": {
                "profile": "ollama-ornith-9b",
                "capability": "summarization",
                "importance": "normal",
            },
            "context": [{"path": "input.txt", "start": 2, "end": 3}],
            "write_roots": ["out"],
            "done": ["out/result.txt exists"],
            "forbidden": ["No network"],
            "limits": {
                "packet_chars": 4000,
                "output_chars": 4000,
                "model_context_tokens": 4096,
                "model_session_tokens": 16384,
                "model_output_tokens": 256,
                "model_timeout_seconds": 30,
                "max_tool_calls": 5,
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
            "v": 1,
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
            "v": 1,
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
            "v": 1,
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
            "v": 1,
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
        with self.assertRaisesRegex(harness.Rejected, "unreported changed paths"):
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
                "v": 1,
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
            "v": 1,
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
            "v": 1,
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


if __name__ == "__main__":
    unittest.main()
