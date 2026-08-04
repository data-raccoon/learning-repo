from __future__ import annotations

import importlib.util
import hashlib
import contextlib
import io
import json
from pathlib import Path
import tempfile
import unittest


PACKAGE_ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("mc_mod_manage", PACKAGE_ROOT / "manage.py")
assert SPEC is not None and SPEC.loader is not None
manage = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(manage)
PROFILE = "ollama-ornith-9b"


class ManagerTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.workspace = Path(self.temporary.name)
        self.manager = manage.MCModAgentsManager(self.workspace, PACKAGE_ROOT)
        self.target = self.workspace / "project"
        self.manager.init("project", "test-mod", PROFILE)

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def write(self, relative: str, value: str | bytes) -> Path:
        path = self.target / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        if isinstance(value, bytes):
            path.write_bytes(value)
        else:
            path.write_text(value, encoding="utf-8")
        return path

    def complete_intent(self) -> None:
        self.write(
            ".mc-mod-agents/intent.md",
            "# Mod Intent\n\nProject ID: `test-mod`\n\n"
            "Players build a server-authoritative signal beacon from one crafted item. "
            "The MVP serves multiplayer technical players in short sessions.\n\n"
            "## Inspirations\nVanilla redstone feedback without copied assets.\n\n"
            "## Out of Scope\nWorld generation, custom entities, and external integrations are excluded.\n",
        )

    def valid_spec(self) -> dict:
        value = json.loads((PACKAGE_ROOT / "context/templates/mod-spec.example.json").read_text(encoding="utf-8"))
        value["mod_id"] = "test-mod"
        value["creative_artifacts"] = [path.replace("my-example-mod", "test-mod") for path in value["creative_artifacts"]]
        return value

    def complete_design(self) -> dict:
        self.complete_intent()
        body = (
            "This approved design defines the signal beacon MVP with explicit server authority, "
            "client feedback, deterministic rules, failure behavior, and retained verification evidence."
        )
        self.write("docs/PRODUCT.md", "# Product\n\n" + body)
        self.write("docs/ARCHITECTURE.md", "# Architecture\n\n" + body)
        self.write("docs/ACCEPTANCE.md", "# Acceptance\n\n" + body)
        spec = self.valid_spec()
        self.write("mod-spec.json", json.dumps(spec, indent=2) + "\n")
        return spec

    def approve(self) -> dict:
        self.complete_design()
        return self.manager.approve("project")

    def complete_assets(self, spec: dict) -> None:
        self.write("docs/style-guide.md", "# Style guide\n\nOriginal high-contrast placeholder resources use non-color shape cues.")
        entries = []
        for relative in spec["creative_artifacts"]:
            self.write(relative, "{}\n" if relative.endswith(".json") else b"test-resource")
            entries.append({
                "path": relative,
                "category": "lang" if relative.endswith(".json") else "texture",
                "provenance": "original",
                "placeholder": True,
                "checksum": "0" * 64,
                "size_bytes": 2,
                "format": "JSON" if relative.endswith(".json") else "PNG",
            })
        manifest = {"schema_version": 1, "mod_id": "test-mod", "assets": entries}
        self.write("assets/asset-manifest.json", json.dumps(manifest, indent=2) + "\n")

    def complete_engineering(self, spec: dict) -> None:
        for relative in spec["engineer_artifacts"]:
            self.write(relative, b"jar" if relative.endswith(".jar") else "generated test fixture\n")
        self.write("docs/IMPLEMENTATION.md", "# Implementation\n\nAll approved behavior and remaining manual smoke tests are traced here.")

    def test_init_emits_a_valid_small_context_architect_task(self) -> None:
        task = json.loads((self.target / ".mc-mod-agents/tasks/01-mod-architect.task.json").read_text(encoding="utf-8"))
        self.manager._harness_validate_task(task)
        self.assertEqual(2, task["v"])
        self.assertEqual("planning", task["kind"])
        self.assertTrue(all(set(item) == {"path"} for item in task["context"]))
        self.assertEqual("architecture", task["model"]["capability"])
        self.assertEqual(PROFILE, task["model"]["profile"])
        self.assertEqual(
            ["docs/PRODUCT.md", "docs/ARCHITECTURE.md", "docs/ACCEPTANCE.md", "mod-spec.json"],
            task["write_roots"],
        )
        self.assertFalse((self.target / ".mc-mod-agents/jobs").exists())

    def test_init_rejects_repository_control_roots(self) -> None:
        with self.assertRaisesRegex(manage.MCModAgentsError, "target root is reserved"):
            self.manager.init("model-execution-harness/mod", "bad-target", PROFILE)

    def test_validate_rejects_placeholder_intent_before_architect_run(self) -> None:
        with self.assertRaisesRegex(manage.MCModAgentsError, "unresolved placeholders"):
            self.manager.validate("project")

    def test_example_spec_matches_the_runtime_contract(self) -> None:
        self.complete_design()
        validated = self.manager._validate_spec(self.target)
        self.assertEqual(2, validated["schema_version"])
        self.assertEqual("25", validated["java_version"])
        self.assertEqual(list(manage.STANDARD_VERIFIERS), validated["verifiers"])

    def test_spec_rejects_directories_and_unowned_root_files(self) -> None:
        spec = self.complete_design()
        spec["creative_artifacts"][0] = "src/main/resources/assets/test-mod/lang/"
        self.write("mod-spec.json", json.dumps(spec))
        with self.assertRaisesRegex(manage.MCModAgentsError, "must name a file"):
            self.manager._validate_spec(self.target)
        spec = self.valid_spec()
        spec["engineer_artifacts"].append("manage.py")
        self.write("mod-spec.json", json.dumps(spec))
        with self.assertRaisesRegex(manage.MCModAgentsError, "outside the approved engineering roots"):
            self.manager._validate_spec(self.target)

    def test_spec_rejects_changed_pin_and_executable_verifier(self) -> None:
        spec = self.complete_design()
        spec["java_version"] = "17"
        self.write("mod-spec.json", json.dumps(spec))
        with self.assertRaisesRegex(manage.MCModAgentsError, "pinned to 25"):
            self.manager._validate_spec(self.target)
        spec = self.valid_spec()
        spec["verifiers"] = [{"id": "unsafe", "argv": ["python", "-c", "pass"]}]
        self.write("mod-spec.json", json.dumps(spec))
        with self.assertRaisesRegex(manage.MCModAgentsError, "fixed standard verifier"):
            self.manager._validate_spec(self.target)

    def test_approval_binds_intent_and_context(self) -> None:
        self.approve()
        intent = self.target / ".mc-mod-agents/intent.md"
        intent.write_text(intent.read_text(encoding="utf-8") + "\nChanged after approval.\n", encoding="utf-8")
        with self.assertRaisesRegex(manage.MCModAgentsError, "approval is stale"):
            self.manager.materialize_build("project", PROFILE)

    def test_staged_lifecycle_places_gate_evidence_before_qa(self) -> None:
        spec = self.complete_design()
        self.manager.approve("project")
        assets = self.manager.materialize_build("project", PROFILE)
        self.assertEqual("assets", assets["phase"])
        asset_task = json.loads((self.target / assets["task"]).read_text(encoding="utf-8"))
        self.manager._harness_validate_task(asset_task)

        with self.assertRaisesRegex(manage.MCModAgentsError, "asset phase output is missing"):
            self.manager.materialize_engineer("project", PROFILE)
        self.complete_assets(spec)
        with self.assertRaisesRegex(manage.MCModAgentsError, "record a passing asset gate"):
            self.manager.materialize_engineer("project", PROFILE)
        asset_gate = {
            "status": "passed",
            "task_id": "test-mod-asset-producer",
            "packet_sha256": "b" * 64,
            "worker": "test-worker",
            "verified_files": [],
            "checks": [{"id": "asset-contract", "exit_code": 0, "stdout_tail": "", "stderr_tail": ""}],
            "risks": [],
        }
        asset_gate_path = self.write("asset-gate-result.json", json.dumps(asset_gate))
        self.manager.record_asset_gate("project", str(asset_gate_path))
        engineering = self.manager.materialize_engineer("project", PROFILE)
        engineer_task = json.loads((self.target / engineering["task"]).read_text(encoding="utf-8"))
        self.manager._harness_validate_task(engineer_task)
        self.assertEqual(set(manage.STANDARD_VERIFIERS), {item["id"] for item in engineer_task["verifiers"]})

        with self.assertRaisesRegex(manage.MCModAgentsError, "record a passing engineer gate"):
            self.manager.materialize_qa("project", PROFILE)
        self.complete_engineering(spec)
        gate = {
            "status": "passed",
            "task_id": "test-mod-mod-engineer",
            "packet_sha256": "a" * 64,
            "worker": "test-worker",
            "verified_files": [],
            "checks": [
                {"id": verifier_id, "exit_code": 0, "stdout_tail": "", "stderr_tail": ""}
                for verifier_id in manage.STANDARD_VERIFIERS
            ],
            "risks": [],
        }
        gate_path = self.write("gate-result.json", json.dumps(gate))
        self.manager.record_build_gate("project", str(gate_path))
        qa = self.manager.materialize_qa("project", PROFILE)
        qa_task = json.loads((self.target / qa["task"]).read_text(encoding="utf-8"))
        self.manager._harness_validate_task(qa_task)
        context_paths = {item["path"] for item in qa_task["context"]}
        self.assertIn(".mc-mod-agents/evidence/build-gate.json", context_paths)
        self.assertEqual(["qa-report-contract"], [item["id"] for item in qa_task["verifiers"]])

    def test_validate_uses_current_harness_and_reports_phase(self) -> None:
        self.complete_intent()
        result = self.manager.validate("project")
        self.assertEqual("architect", result["phase"])
        self.assertEqual(["test-mod-mod-architect"], result["tasks"])

    def test_trusted_asset_verifier_checks_manifest_digest(self) -> None:
        payload = b'{"item.test-mod.example":"Example"}\n'
        relative = "src/main/resources/assets/test-mod/lang/en_us.json"
        self.write("mod-spec.json", json.dumps({"mod_id": "test-mod", "creative_artifacts": [relative]}))
        self.write(relative, payload)
        manifest = {
            "schema_version": 1,
            "mod_id": "test-mod",
            "assets": [{
                "path": relative,
                "category": "lang",
                "provenance": "original",
                "placeholder": False,
                "checksum": hashlib.sha256(payload).hexdigest(),
                "size_bytes": len(payload),
                "format": "JSON",
            }],
        }
        self.write("assets/asset-manifest.json", json.dumps(manifest))
        verifier_path = self.target / ".mc-mod-agents/tools/verify_assets.py"
        verifier_spec = importlib.util.spec_from_file_location("test_asset_verifier", verifier_path)
        assert verifier_spec is not None and verifier_spec.loader is not None
        verifier = importlib.util.module_from_spec(verifier_spec)
        verifier_spec.loader.exec_module(verifier)
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(0, verifier.main())
        manifest["assets"][0]["checksum"] = "0" * 64
        self.write("assets/asset-manifest.json", json.dumps(manifest))
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(1, verifier.main())


if __name__ == "__main__":
    unittest.main()
