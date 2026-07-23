import json
from pathlib import Path
import tempfile
import unittest

from agent_orchestrator.contracts import ContractError, load_job
from agent_orchestrator.paths import contained_path, validate_job_paths


class ContractPathTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        (self.root / "target").mkdir()
        (self.root / "target" / "context.txt").write_text("context", encoding="utf-8")

    def tearDown(self):
        self.temp.cleanup()

    def job_file(self, **updates):
        value = {
            "schema_version": 1, "id": "test", "objective": "test",
            "target_dir": "target", "mode": "read", "importance": "low",
            "risk": "low", "tool_class": "inference", "context": ["context.txt"],
        }
        value.update(updates)
        path = self.root / "job.json"
        path.write_text(json.dumps(value), encoding="utf-8")
        return path

    def test_valid_job_and_paths(self):
        job = load_job(self.job_file())
        self.assertEqual(validate_job_paths(self.root, job), (self.root / "target").resolve())

    def test_unknown_field_fails_closed(self):
        with self.assertRaises(ContractError):
            load_job(self.job_file(surprise=True))

    def test_command_job_requires_known_allowlist_entry(self):
        with self.assertRaises(ContractError):
            load_job(self.job_file(tool_class="commands"))
        with self.assertRaises(ContractError):
            load_job(self.job_file(tool_class="commands", allowed_commands=["powershell -Command whoami"]))
        job = load_job(self.job_file(tool_class="commands", allowed_commands=["python -m unittest -v"]))
        self.assertEqual(job.allowed_commands, ("python -m unittest -v",))

    def test_parent_and_absolute_paths_are_rejected(self):
        with self.assertRaises(ContractError):
            contained_path(self.root, "../escape")
        with self.assertRaises(ContractError):
            contained_path(self.root, str((self.root / "target").resolve()))

    def test_missing_context_is_rejected(self):
        job = load_job(self.job_file(context=["missing.txt"]))
        with self.assertRaises(ContractError):
            validate_job_paths(self.root, job)

    def test_allowed_write_paths_are_scoped_and_write_only(self):
        job = load_job(self.job_file(mode="write", tool_class="files_write", allowed_write_paths=["src", "assets/ui.png"]))
        validate_job_paths(self.root, job)
        self.assertEqual(job.allowed_write_paths, ("src", "assets/ui.png"))
        with self.assertRaises(ContractError):
            load_job(self.job_file(allowed_write_paths=["src"]))
        escaping = load_job(self.job_file(mode="write", tool_class="files_write", allowed_write_paths=["../escape"]))
        with self.assertRaises(ContractError):
            validate_job_paths(self.root, escaping)

    def test_context_symlink_is_rejected(self):
        link = self.root / "target" / "linked.txt"
        try:
            link.symlink_to(self.root / "target" / "context.txt")
        except OSError:
            self.skipTest("symlinks are unavailable in this Windows test environment")
        job = load_job(self.job_file(context=["linked.txt"]))
        with self.assertRaises(ContractError):
            validate_job_paths(self.root, job)

    def test_materialization_requires_transactional_declarations(self):
        (self.root / "target" / "schema.json").write_text('{"type":"object"}', encoding="utf-8")
        (self.root / "target" / "dialogue.md").write_text("# Dialogue\n", encoding="utf-8")
        values = {
            "mode": "write", "tool_class": "inference", "output_schema": "schema.json",
            "expected_artifacts": ["dialogue.md"], "allowed_write_paths": ["dialogue.md"],
            "materialization": {"path": "dialogue.md", "operation": "append", "template": "{text}\n"},
        }
        job = load_job(self.job_file(**values))
        self.assertEqual(job.materialization.path, "dialogue.md")
        validate_job_paths(self.root, job)
        with self.assertRaises(ContractError):
            load_job(self.job_file(**{**values, "expected_artifacts": []}))

    def test_append_materialization_requires_existing_target(self):
        (self.root / "target" / "schema.json").write_text('{"type":"object"}', encoding="utf-8")
        job = load_job(self.job_file(
            mode="write", tool_class="inference", output_schema="schema.json",
            expected_artifacts=["missing.md"], allowed_write_paths=["missing.md"],
            materialization={"path": "missing.md", "operation": "append", "template": "{text}"},
        ))
        with self.assertRaises(ContractError):
            validate_job_paths(self.root, job)


if __name__ == "__main__":
    unittest.main()
