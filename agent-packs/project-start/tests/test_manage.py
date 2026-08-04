from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import tempfile
import unittest


PACKAGE_ROOT = Path(__file__).resolve().parents[1]
PROFILE = "mistral-medium-3.5"
SPEC = importlib.util.spec_from_file_location("projectstart_manage", PACKAGE_ROOT / "manage.py")
assert SPEC is not None and SPEC.loader is not None
projectstart = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(projectstart)


class ProjectStartTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.workspace = Path(self.temporary.name)
        self.manager = projectstart.ProjectStartManager(self.workspace, PACKAGE_ROOT)
        self.target = self.workspace / "new-project"
        self.manager.init("new-project", "new-project", "generic-software-v1")

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def write_json(self, relative: str, value: object) -> Path:
        path = self.target / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")
        return path

    def complete_intent(self) -> dict:
        intent = {
            "schema_version": 1,
            "project_id": "new-project",
            "product": {
                "promise": "Turn one source text file into a deterministic summary report.",
                "primary_user": "A technical analyst working locally.",
                "journeys": ["The analyst supplies a text file and receives a validated report."],
                "mvp": ["Read one UTF-8 file", "Write one machine-readable report"],
                "exclusions": ["Web interface", "Shared online state"],
            },
            "requirements": [
                {"id": "REQ-001", "category": "runtime", "statement": "Run as a local command-line program.", "status": "known", "authority": "human"},
                {"id": "REQ-002", "category": "architecture", "statement": "Select reversible internal module boundaries.", "status": "model_may_decide", "authority": "model"},
            ],
            "constraints": {
                "integrations": "not_applicable",
                "data_sensitivity": "Public test data only.",
                "persistence": "Output files only; no database.",
                "availability": "Local on-demand execution.",
                "scale": "One file up to ten megabytes per run.",
                "security_compliance": "No credentials and no network access.",
                "team_operations": "One Python-capable maintainer.",
                "budget_schedule": "One-week MVP with no external spend.",
            },
            "decision_policy": {
                "human_decides": ["Product scope", "External spend", "Deployment"],
                "model_may_decide": ["Internal module boundaries", "Test seams"],
            },
        }
        self.write_json("project-intent.json", intent)
        return intent

    def valid_discovery(self, *, blockers: bool = False) -> dict:
        return {
            "schema_version": 1,
            "project_id": "new-project",
            "normalized_requirements": [
                {"id": "NREQ-001", "statement": "Run locally as a CLI.", "status": "constraint", "source_ids": ["REQ-001"]},
                {"id": "NREQ-002", "statement": "Keep module decisions reversible.", "status": "model_decision", "source_ids": ["REQ-002"]},
            ],
            "conflicts": [],
            "blocking_questions": ["Which runtime is approved?"] if blockers else [],
            "assumptions": [],
            "candidate_archetypes": [
                {"id": "cli-automation", "fit": "strong", "reason": "REQ-001 explicitly requires local command execution."}
            ],
            "recommendation": "Use the CLI archetype with one process and no persistent service.",
        }

    def valid_design(self) -> dict:
        return {
            "schema_version": 1,
            "project_id": "new-project",
            "stack": {"pack_id": "generic-software-v1", "components": {}},
            "selected_archetype": {
                "id": "cli-automation",
                "rationale": "REQ-001 requires local on-demand command execution and no service.",
                "deviations": [],
            },
            "modules": [
                {"id": "cli", "responsibility": "Parse inputs and present results.", "owner": "implementation-owner", "depends_on": ["summary-domain"], "runtime": "local process", "public_interfaces": ["command arguments", "exit code"]},
                {"id": "summary-domain", "responsibility": "Produce a deterministic summary model.", "owner": "implementation-owner", "depends_on": [], "runtime": "in-process", "public_interfaces": ["summarize text"]},
            ],
            "data_stores": [],
            "external_interfaces": [],
            "security_model": {
                "trust_boundaries": ["Input files are untrusted."],
                "authentication": "not_applicable",
                "authorization": "The invoking operating-system user controls local files.",
                "secrets": "No secrets are required or accepted.",
                "input_validation": "Reject unreadable, non-UTF-8, and oversized input before processing.",
            },
            "operational_model": {
                "deployment": "A local package executed on demand.",
                "configuration": "Command arguments with documented defaults.",
                "observability": "Structured standard-error diagnostics and deterministic exit codes.",
                "backup_recovery": "Input remains immutable and output can be regenerated.",
            },
            "decisions": [
                {
                    "id": "ADR-0001",
                    "question": "Which initial architecture should be used?",
                    "selected": "One CLI process with a pure summary domain.",
                    "alternatives": ["Local web application"],
                    "evidence": ["REQ-001", "The intent excludes a web interface."],
                    "consequences": ["Simple deployment", "No shared online state"],
                    "reversal_cost": "low",
                    "confidence": "high",
                    "revisit_trigger": "A human approves a graphical or shared-state requirement.",
                }
            ],
            "risks": [
                {"id": "RISK-001", "description": "Large malformed inputs could consume excess memory.", "likelihood": "medium", "impact": "medium", "mitigation": "Validate the ten-megabyte limit before reading fully.", "owner": "implementation-owner"}
            ],
            "acceptance_criteria": [
                {"id": "AC-001", "requirement_ids": ["REQ-001"], "preconditions": "A valid UTF-8 input file exists.", "action": "The user invokes the command with its path.", "outcome": "One deterministic machine-readable report is written.", "authority": "The local process owns validation and output.", "verification": "Automated CLI integration test.", "evidence": "Test exit code, output digest, and captured diagnostics."}
            ],
            "artifact_plan": [
                {"path": "src/main.py", "owner": "implementation-owner", "purpose": "CLI adapter."},
                {"path": "src/summary.py", "owner": "implementation-owner", "purpose": "Pure summary domain."},
                {"path": "tests/test_cli.py", "owner": "implementation-owner", "purpose": "Vertical integration test."},
            ],
            "first_vertical_slice": {
                "goal": "Summarize one valid file through the public command.",
                "artifacts": ["src/main.py", "src/summary.py", "tests/test_cli.py"],
                "acceptance_ids": ["AC-001"],
            },
            "open_questions": [],
            "confidence": "high",
        }

    def reach_architecture(self) -> dict:
        self.complete_intent()
        self.manager.prepare_discovery("new-project", PROFILE)
        self.write_json("discovery.json", self.valid_discovery())
        self.manager.accept_discovery("new-project")
        self.manager.materialize_architecture("new-project", PROFILE)
        design = self.valid_design()
        self.write_json("project-design.json", design)
        return design

    def valid_review(self) -> dict:
        return {
            "schema_version": 1,
            "project_id": "new-project",
            "design_sha256": projectstart.sha256(self.target / "project-design.json"),
            "findings": [],
            "coverage": {"AC-001": "supported"},
            "recommendation": "PASS",
        }

    def test_init_copies_frozen_context_and_rejects_placeholder_intent(self) -> None:
        self.assertTrue((self.target / ".projectstart/context/catalog/archetypes.json").is_file())
        self.assertTrue((self.target / ".projectstart/context/stack-packs/generic-software-v1.json").is_file())
        with self.assertRaisesRegex(projectstart.ProjectStartError, "placeholder"):
            self.manager.prepare_discovery("new-project", PROFILE)

    def test_discovery_task_uses_default_harness_contract(self) -> None:
        self.complete_intent()
        result = self.manager.prepare_discovery("new-project", PROFILE)
        task = json.loads((self.target / result["task"]).read_text(encoding="utf-8"))
        self.manager.harness_validate_task(task)
        self.assertEqual(PROFILE, task["model"]["profile"])
        self.assertEqual("reasoning", task["model"]["capability"])
        self.assertEqual(["discovery.json"], task["write_roots"])

    def test_discovery_blockers_prevent_acceptance(self) -> None:
        self.complete_intent()
        self.manager.prepare_discovery("new-project", PROFILE)
        self.write_json("discovery.json", self.valid_discovery(blockers=True))
        with self.assertRaisesRegex(projectstart.ProjectStartError, "blocking question"):
            self.manager.accept_discovery("new-project")

    def test_intent_approval_is_hash_bound(self) -> None:
        self.complete_intent()
        self.manager.prepare_discovery("new-project", PROFILE)
        self.write_json("discovery.json", self.valid_discovery())
        self.manager.accept_discovery("new-project")
        intent_path = self.target / "project-intent.json"
        intent_path.write_text(intent_path.read_text(encoding="utf-8") + "\n", encoding="utf-8")
        with self.assertRaisesRegex(projectstart.ProjectStartError, "stale"):
            self.manager.materialize_architecture("new-project", PROFILE)

    def test_design_rejects_cycles_open_questions_and_globs(self) -> None:
        design = self.reach_architecture()
        design["modules"][1]["depends_on"] = ["cli"]
        self.write_json("project-design.json", design)
        with self.assertRaisesRegex(projectstart.ProjectStartError, "cycle"):
            self.manager.validate_design(self.target)
        design = self.valid_design()
        design["open_questions"] = ["Should this become a service?"]
        self.write_json("project-design.json", design)
        with self.assertRaisesRegex(projectstart.ProjectStartError, "open questions"):
            self.manager.validate_design(self.target)
        design = self.valid_design()
        design["artifact_plan"][0]["path"] = "src/*.py"
        self.write_json("project-design.json", design)
        with self.assertRaisesRegex(projectstart.ProjectStartError, "individual normalized relative file"):
            self.manager.validate_design(self.target)

    def test_render_is_deterministic_and_refuses_overwrite(self) -> None:
        self.reach_architecture()
        result = self.manager.render("new-project")
        self.assertEqual(list(projectstart.RENDERED), result["artifacts"])
        architecture = (self.target / "docs/ARCHITECTURE.md").read_text(encoding="utf-8")
        self.assertIn("cli-automation", architecture)
        self.assertIn("summary-domain", architecture)
        plan = json.loads((self.target / "bootstrap-plan.json").read_text(encoding="utf-8"))
        self.assertEqual("documentation-only", plan["generator"]["id"])
        with self.assertRaisesRegex(projectstart.ProjectStartError, "refusing to overwrite"):
            self.manager.render("new-project")

    def test_review_must_match_design_and_have_no_major_pass_finding(self) -> None:
        self.reach_architecture()
        self.manager.render("new-project")
        self.manager.materialize_review("new-project", PROFILE)
        review = self.valid_review()
        review["findings"] = [{"id": "ARCH-001", "severity": "major", "category": "complexity", "description": "A major concern remains unresolved.", "evidence": "project-design.json module list", "owner": "project-architect"}]
        self.write_json("architecture-review.json", review)
        with self.assertRaisesRegex(projectstart.ProjectStartError, "PASS review"):
            self.manager.record_review("new-project", str(self.target / "architecture-review.json"))
        review = self.valid_review()
        review["design_sha256"] = "0" * 64
        self.write_json("architecture-review.json", review)
        with self.assertRaisesRegex(projectstart.ProjectStartError, "not bound"):
            self.manager.record_review("new-project", str(self.target / "architecture-review.json"))

    def test_complete_lifecycle_approves_current_hashes(self) -> None:
        self.reach_architecture()
        self.manager.render("new-project")
        review_task = self.manager.materialize_review("new-project", PROFILE)
        task = json.loads((self.target / review_task["task"]).read_text(encoding="utf-8"))
        self.manager.harness_validate_task(task)
        review_path = self.write_json("architecture-review.json", self.valid_review())
        self.manager.record_review("new-project", str(review_path))
        approval = self.manager.approve("new-project")
        self.assertEqual("approved", approval["status"])
        self.assertIn("project-design.json", approval["sha256"])
        status = self.manager.validate("new-project")
        self.assertEqual("approved", status["phase"])
        self.assertEqual(3, len(status["tasks"]))
        architecture = self.target / "docs/ARCHITECTURE.md"
        architecture.write_text(architecture.read_text(encoding="utf-8") + "\nDrift.\n", encoding="utf-8")
        with self.assertRaisesRegex(projectstart.ProjectStartError, "architecture approval is stale"):
            self.manager.validate("new-project")

    def test_protected_roots_are_rejected(self) -> None:
        with self.assertRaisesRegex(projectstart.ProjectStartError, "reserved"):
            self.manager.init("model-execution-harness/new", "bad-project", "generic-software-v1")

    def test_init_refuses_to_overwrite_an_existing_project(self) -> None:
        existing = self.workspace / "existing"
        existing.mkdir()
        (existing / "README.md").write_text("# Existing\n", encoding="utf-8")
        with self.assertRaisesRegex(projectstart.ProjectStartError, "refusing to initialize"):
            self.manager.init("existing", "existing", "generic-software-v1")


if __name__ == "__main__":
    unittest.main()
