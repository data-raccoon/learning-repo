from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace
import sys
import tempfile
import unittest
from unittest.mock import patch


HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE))

import model_runtime  # noqa: E402


REGISTRY = HERE / "models.json"


class ModelRuntimeTests(unittest.TestCase):
    def setUp(self) -> None:
        self.profiles = model_runtime.load_registry(REGISTRY)
        self.packet = {
            "v": 1,
            "task": {
                "id": "task-1",
                "goal": "Review the bounded design.",
                "done": ["Identify one concrete risk."],
                "forbidden": ["Do not claim file edits."],
            },
            "task_sha256": "0" * 64,
            "excerpts": [
                {
                    "path": "README.md",
                    "start": 1,
                    "end": 1,
                    "sha256": "1" * 64,
                    "text": "# Design\n",
                }
            ],
        }

    def availability(self) -> dict:
        return {
            "profiles": [
                {"id": profile.id, "available": True}
                for profile in self.profiles.values()
            ]
        }

    def test_auto_route_is_rejected(self) -> None:
        with self.assertRaisesRegex(model_runtime.ModelRejected, "disabled"):
            model_runtime.route(
                self.profiles,
                self.availability(),
                {
                    "profile": "auto",
                    "capability": "summarization",
                    "importance": "normal",
                },
            )

    def test_explicit_profile_is_selected(self) -> None:
        selected = model_runtime.route(
            self.profiles,
            self.availability(),
            {
                "profile": "ollama-ministral-3-14b",
                "capability": "architecture",
                "importance": "critical",
            },
        )
        self.assertEqual("ollama-ministral-3-14b", selected.id)

    def test_explicit_profile_must_support_capability(self) -> None:
        with self.assertRaisesRegex(model_runtime.ModelRejected, "lacks capability"):
            model_runtime.route(
                self.profiles,
                self.availability(),
                {
                    "profile": "ollama-ministral-3-8b",
                    "capability": "coding",
                    "importance": "low",
                },
            )

    def test_vibe_active_model_prefers_environment_override(self) -> None:
        with patch.dict(
            model_runtime.os.environ,
            {"VIBE_ACTIVE_MODEL": "devstral-small", "USERPROFILE": "ignored"},
            clear=True,
        ):
            self.assertEqual("devstral-small", model_runtime._vibe_active_model())

    @patch("model_runtime._vibe_path", return_value=r"C:\tools\vibe.exe")
    @patch(
        "model_runtime._vibe_configured_models",
        return_value={"devstral-small", "mistral-medium-3.5"},
    )
    @patch("model_runtime._agy_path", return_value=r"C:\tools\agy.exe")
    @patch("model_runtime.ollama_inventory")
    def test_inventory_checks_registered_ollama_digests(self, ollama, _agy, _configured, _vibe) -> None:
        ollama.return_value = {
            "version": "test",
            "models": [
                {
                    "name": profile.model,
                    "digest": profile.digest,
                }
                for profile in self.profiles.values()
                if profile.provider == "ollama"
            ],
        }
        result = model_runtime.inventory(self.profiles)
        self.assertTrue(all(row["available"] for row in result["profiles"]))

    @patch("model_runtime._json_request")
    def test_ollama_invocation_attests_model_and_caps_tokens(self, request) -> None:
        profile = self.profiles["ollama-ornith-9b"]
        request.return_value = {
            "model": profile.model,
            "message": {"content": "Bounded review."},
            "prompt_eval_count": 100,
            "eval_count": 12,
        }
        result = model_runtime.run_ollama_canary(
            profile,
            self.packet,
            endpoint="http://127.0.0.1:11434",
            context_tokens=4096,
            output_tokens=128,
            timeout=30,
        )
        payload = request.call_args.kwargs["payload"]
        self.assertFalse(payload["think"])
        self.assertEqual(4096, payload["options"]["num_ctx"])
        self.assertEqual(128, payload["options"]["num_predict"])
        self.assertTrue(result["attestation"]["matched"])
        self.assertEqual(12, result["usage"]["completion_tokens"])

    @patch("model_runtime.subprocess.run")
    @patch("model_runtime._agy_path", return_value=r"C:\tools\agy.exe")
    def test_gemini_is_sandboxed_and_strips_api_credentials(
        self, _agy, run
    ) -> None:
        run.return_value = SimpleNamespace(
            returncode=0, stdout="Bounded proposal.\n", stderr=""
        )
        profile = self.profiles["gemini-auto-free"]
        with patch.dict(
            model_runtime.os.environ,
            {"GEMINI_API_KEY": "secret", "GOOGLE_CLOUD_PROJECT": "paid"},
            clear=True,
        ):
            result = model_runtime.run_gemini_canary(
                profile, self.packet, timeout=30
            )
        command = run.call_args.args[0]
        environment = run.call_args.kwargs["env"]
        prompt = command[command.index("--print") + 1]
        self.assertIn("--mode=plan", command)
        self.assertIn("--sandbox", command)
        self.assertIn("Do not request tools", prompt)
        self.assertNotIn("GEMINI_API_KEY", environment)
        self.assertNotIn("GOOGLE_CLOUD_PROJECT", environment)
        self.assertEqual("Bounded proposal.", result["text"])
        self.assertIsNone(result["attestation"]["reported_model"])

    @patch("model_runtime.subprocess.run")
    @patch("model_runtime._agy_path", return_value=r"C:\tools\agy.exe")
    def test_gemini_rejects_model_fallback(self, _agy, run) -> None:
        run.return_value = SimpleNamespace(
            returncode=0,
            stdout="Response from another model.\n",
            stderr="Model ID stale not in local config, defaulting to CCPA",
        )
        with self.assertRaisesRegex(model_runtime.ModelRejected, "not honored"):
            model_runtime.run_gemini_canary(
                self.profiles["gemini-auto-free"], self.packet, timeout=30
            )

    @patch("model_runtime.subprocess.run")
    @patch("model_runtime._vibe_path", return_value=r"C:\tools\vibe.exe")
    @patch(
        "model_runtime._vibe_configured_models", return_value={"devstral-small"}
    )
    def test_mistral_vibe_worker_enables_bounded_tools(
        self, _configured, _vibe, run
    ) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            target = root / "target"
            target.mkdir()
            config = root / "config.toml"
            config.write_text('active_model = "devstral-small"\n', encoding="utf-8")
            trajectory = root / "trajectory.json"
            observed = {}

            def execute(*args, **kwargs):
                agent = Path(kwargs["env"]["VIBE_HOME"]) / "agents" / "small-context-worker.toml"
                observed["agent"] = agent.read_text(encoding="utf-8")
                observed["command"] = args[0]
                observed["environment"] = kwargs["env"]
                observed["prompt"] = kwargs["input"]
                return SimpleNamespace(returncode=0, stdout="[]", stderr="")

            run.side_effect = execute
            packet = json.loads(json.dumps(self.packet))
            packet["task"]["write_roots"] = ["out/result.txt"]
            with patch("model_runtime._vibe_config_path", return_value=config):
                result = model_runtime.run_mistral_vibe_worker(
                    self.profiles["devstral-small"],
                    packet,
                    target=target,
                    write_roots=["out/result.txt"],
                    allowed_commands=[["git", "status", "--short"]],
                    trajectory_path=trajectory,
                    context_tokens=4096,
                    output_tokens=128,
                    max_turns=4,
                    command_timeout=10,
                    timeout=30,
                )
            observed["trajectory"] = trajectory.read_text(encoding="utf-8")
        self.assertIn("write_file", observed["command"])
        self.assertIn("limited_bash", observed["command"])
        self.assertNotIn("--auto-approve", observed["command"])
        self.assertIn('permission = "never"', observed["agent"])
        self.assertIn("out\\\\result.txt", observed["agent"])
        self.assertEqual("devstral-small", observed["environment"]["VIBE_ACTIVE_MODEL"])
        self.assertIn("Work directly in the current directory", observed["prompt"])
        self.assertTrue(result["success"])
        self.assertEqual("[]", observed["trajectory"])


if __name__ == "__main__":
    unittest.main()
