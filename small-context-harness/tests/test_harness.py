from __future__ import annotations

import hashlib
import json
import sys
import tempfile
import unittest
from unittest.mock import patch
from pathlib import Path


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
                "profile": "auto",
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

    @patch("harness.invoke_model")
    @patch("harness.model_inventory")
    def test_canary_requires_exact_response(self, inventory, invoke) -> None:
        inventory.return_value = {
            "profiles": [
                {"id": "ollama-ministral-3-8b", "available": True}
            ]
        }
        invoke.return_value = {
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
