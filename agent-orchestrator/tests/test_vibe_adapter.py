import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from agent_orchestrator.adapters import VibeAdapter, build_prompt
from agent_orchestrator.contracts import Job, Limits, Model, ModelProfile


class VibeAdapterTests(unittest.TestCase):
    def job(self) -> Job:
        return Job(
            schema_version=1,
            id="local-web",
            objective="Research and update notes.md",
            target_dir="target",
            mode="write",
            importance="low",
            risk="low",
            tool_class="files_write",
            limits=Limits(max_turns=2, max_tokens=100),
        )

    def model(self) -> Model:
        return Model(
            id="ministral-3b-q4-local",
            provider="local-ministral",
            remote_id="ministral-3b-q4",
            quality=0.48,
            context_tokens=32768,
            input_cost_per_million=0.0,
            output_cost_per_million=0.0,
            price_effective_at="2026-07-19",
            modalities=("text",),
            capabilities=("file-editing", "web-research"),
        )

    def profile(self) -> ModelProfile:
        return ModelProfile(
            id="local-ministral-files",
            model="ministral-3b-q4-local",
            harness="local-vibe-files",
            status="eligible",
            success_probability=0.78,
            capabilities=("file-editing", "web-research"),
            tool_class="files_write",
        )

    def test_local_vibe_enables_web_and_write_tools(self):
        completed = subprocess.CompletedProcess([], 0, stdout='{"role":"assistant","content":"done"}', stderr="")
        with tempfile.TemporaryDirectory() as directory:
            workspace = Path(directory)
            with patch("agent_orchestrator.adapters.shutil.which", return_value="vibe"), patch(
                "agent_orchestrator.adapters.subprocess.run", return_value=completed
            ) as run:
                result = VibeAdapter(workspace).run(self.job(), workspace, self.model(), self.profile())

        self.assertTrue(result.ok)
        command = run.call_args.args[0]
        enabled = [command[index + 1] for index, value in enumerate(command[:-1]) if value == "--enabled-tools"]
        self.assertEqual(enabled, ["read_file", "grep", "edit", "write_file", "web_search", "web_fetch"])
        environment = run.call_args.kwargs["env"]
        self.assertEqual(environment["VIBE_ACTIVE_MODEL"], "ministral-3b-q4")
        prompt = command[command.index("-p") + 1]
        self.assertIn("You may use web_search and web_fetch", prompt)
        self.assertNotIn("Do not use network tools", prompt)

    def test_web_is_denied_by_default(self):
        self.assertIn("Do not use network tools", build_prompt(self.job()))

    def test_model_fallback_warning_fails_closed(self):
        completed = subprocess.CompletedProcess([], 0, stdout='{"role":"assistant","content":"done"}', stderr="Model not configured; falling back")
        with tempfile.TemporaryDirectory() as directory, patch(
            "agent_orchestrator.adapters.shutil.which", return_value="vibe"
        ), patch("agent_orchestrator.adapters.subprocess.run", return_value=completed):
            result = VibeAdapter(Path(directory)).run(self.job(), Path(directory), self.model(), self.profile())
        self.assertFalse(result.ok)
        self.assertFalse(result.attestation["matched"])

    def test_non_fallback_worker_failure_preserves_model_attestation(self):
        completed = subprocess.CompletedProcess([], 1, stdout="", stderr="token limit exceeded")
        with tempfile.TemporaryDirectory() as directory, patch(
            "agent_orchestrator.adapters.shutil.which", return_value="vibe"
        ), patch("agent_orchestrator.adapters.subprocess.run", return_value=completed):
            result = VibeAdapter(Path(directory)).run(self.job(), Path(directory), self.model(), self.profile())
        self.assertFalse(result.ok)
        self.assertEqual(result.attestation, {"expected_model": "ministral-3b-q4", "matched": True})


if __name__ == "__main__":
    unittest.main()
