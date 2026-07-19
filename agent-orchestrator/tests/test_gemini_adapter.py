from pathlib import Path
from types import SimpleNamespace
import tempfile
import unittest
from unittest.mock import patch

from agent_orchestrator.adapters import GoogleAccountCliAdapter
from agent_orchestrator.contracts import Job, Model, ModelProfile


class GoogleAccountCliAdapterTests(unittest.TestCase):
    def setUp(self):
        self.target = Path("target")
        self.model = Model(
            "gemini-auto-free", "gemini-google-account", "Gemini 3.5 Flash (Medium)", 0.86, 0,
            0.0, 0.0, "2026-07-19", ("text",), ("planning",),
        )
        self.profile = ModelProfile(
            "gemini-auto-free-read", self.model.id, "antigravity-cli-read", "eligible",
            0.90, ("planning",), "files_read", 2, "test",
        )

    @staticmethod
    def job(mode="read"):
        tool_class = "files_write" if mode == "write" else "files_read"
        return Job(1, "gemini", "Inspect context", "target", mode, "normal", "low", tool_class)

    @patch("agent_orchestrator.adapters.subprocess.run")
    @patch("agent_orchestrator.adapters.shutil.which", return_value=r"C:\tools\agy.exe")
    def test_read_job_uses_headless_plan_mode(self, _which, run):
        run.return_value = SimpleNamespace(returncode=0, stdout="bounded result\n", stderr="")

        result = GoogleAccountCliAdapter().run(self.job(), self.target, self.model, self.profile)

        self.assertTrue(result.ok)
        self.assertEqual(result.final_text, "bounded result")
        self.assertEqual(result.usage, {})
        command = run.call_args.args[0]
        self.assertIn("--mode=plan", command)
        self.assertEqual(run.call_args.kwargs["cwd"], self.target)

    @patch("agent_orchestrator.adapters.subprocess.run")
    @patch("agent_orchestrator.adapters.shutil.which", return_value=r"C:\tools\agy.exe")
    def test_read_job_embeds_context_and_forbids_tools(self, _which, run):
        run.return_value = SimpleNamespace(returncode=0, stdout="answer\n", stderr="")
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory)
            (target / "brief.md").write_text("bounded context", encoding="utf-8")
            job = Job(1, "gemini", "Summarize", "target", "read", "normal", "low", "files_read", context=("brief.md",))
            result = GoogleAccountCliAdapter().run(job, target, self.model, self.profile)

        self.assertTrue(result.ok)
        command = run.call_args.args[0]
        prompt = command[command.index("--print") + 1]
        self.assertIn("bounded context", prompt)
        self.assertIn("Do not invoke any tool", prompt)

    @patch("agent_orchestrator.adapters.subprocess.run")
    @patch("agent_orchestrator.adapters.shutil.which", return_value=r"C:\tools\agy.exe")
    def test_write_job_uses_accept_edits_and_removes_billable_credentials(self, _which, run):
        run.return_value = SimpleNamespace(returncode=0, stdout="done\n", stderr="")
        with patch.dict("agent_orchestrator.adapters.os.environ", {"GEMINI_API_KEY": "secret", "GOOGLE_CLOUD_PROJECT": "paid"}, clear=True):
            result = GoogleAccountCliAdapter().run(self.job("write"), self.target, self.model, self.profile)

        self.assertTrue(result.ok)
        self.assertIn("--mode=accept-edits", run.call_args.args[0])
        self.assertIn("--new-project", run.call_args.args[0])
        environment = run.call_args.kwargs["env"]
        self.assertNotIn("GEMINI_API_KEY", environment)
        self.assertNotIn("GOOGLE_CLOUD_PROJECT", environment)

    @patch("agent_orchestrator.adapters.subprocess.run")
    @patch("agent_orchestrator.adapters.shutil.which", return_value=r"C:\tools\agy.exe")
    def test_command_job_puts_exact_allowlist_in_prompt(self, _which, run):
        observed = {}
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "target"
            target.mkdir()
            settings = Path(directory) / "settings.json"
            original = '{"colorScheme":"terminal"}\n'
            settings.write_text(original, encoding="utf-8")

            def capture(*args, **kwargs):
                observed.update(__import__("json").loads(settings.read_text(encoding="utf-8")))
                return SimpleNamespace(returncode=0, stdout="tests passed\n", stderr="")

            run.side_effect = capture
            job = Job(1, "qa", "Run tests", "target", "write", "low", "low", "commands", allowed_commands=("python -m unittest -v",))
            command_profile = ModelProfile(
                "gemini-auto-free-commands", self.model.id, "antigravity-cli-commands", "candidate",
                0.0, ("coding", "review", "tool-use"), "commands", 1, "test",
            )
            result = GoogleAccountCliAdapter(settings).run(job, target, self.model, command_profile)
            restored = settings.read_text(encoding="utf-8")
            resolved_target = target.resolve().as_posix()

        self.assertTrue(result.ok)
        command = run.call_args.args[0]
        prompt = command[command.index("--print") + 1]
        self.assertIn("- python -m unittest -v", prompt)
        self.assertIn("Do not append arguments", prompt)
        self.assertEqual(restored, original)
        self.assertEqual(observed["colorScheme"], "terminal")
        self.assertIn(f"read_file({resolved_target})", observed["permissions"]["allow"])
        self.assertIn("command(python -m unittest -v)", observed["permissions"]["allow"])
        self.assertNotIn("command(npm test)", observed["permissions"]["allow"])

    @patch("agent_orchestrator.adapters.shutil.which", return_value=None)
    def test_missing_cli_is_a_compact_adapter_failure(self, _which):
        with patch.dict("agent_orchestrator.adapters.os.environ", {}, clear=True):
            result = GoogleAccountCliAdapter().run(self.job(), self.target, self.model, self.profile)
        self.assertFalse(result.ok)
        self.assertIn("install", result.error)


if __name__ == "__main__":
    unittest.main()
