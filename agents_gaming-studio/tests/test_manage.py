from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


PACKAGE_ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = PACKAGE_ROOT.parent
ORCHESTRATOR_SRC = WORKSPACE / "agent-orchestrator" / "src"
sys.path.insert(0, str(ORCHESTRATOR_SRC))

spec = importlib.util.spec_from_file_location("gaming_agents_manage", PACKAGE_ROOT / "manage.py")
manage = importlib.util.module_from_spec(spec)
assert spec.loader
spec.loader.exec_module(manage)

from agent_orchestrator.adapters import FakeAdapter
from agent_orchestrator.contracts import load_job
from agent_orchestrator.registry import Registry
from agent_orchestrator.runner import JobRunner


def write_registry(root: Path) -> Registry:
    root.mkdir(parents=True)
    (root / "providers.toml").write_text('''
[[providers]]
id = "fake"
display_name = "Fake"
kind = "fake"
status = "active"
auth_kind = "none"
billing = "metered-api"
''', encoding="utf-8")
    (root / "models.toml").write_text('''
[[models]]
id = "reviewer"
provider = "fake"
remote_id = "reviewer"
quality = 0.8
context_tokens = 10000
input_cost_per_million = 0.0
output_cost_per_million = 0.0
price_effective_at = "2026-07-19"
modalities = ["text"]
capabilities = ["review", "reasoning"]

[[models]]
id = "builder"
provider = "fake"
remote_id = "builder"
quality = 0.9
context_tokens = 10000
input_cost_per_million = 0.0
output_cost_per_million = 0.0
price_effective_at = "2026-07-19"
modalities = ["text"]
capabilities = ["coding", "review", "reasoning", "file-editing"]
''', encoding="utf-8")
    (root / "harnesses.toml").write_text('''
[[harnesses]]
id = "fake-read"
kind = "fake-read"
provider = "fake"
tool_class = "files_read"
max_parallel = 1
status = "eligible"

[[harnesses]]
id = "fake-write"
kind = "fake-write"
provider = "fake"
tool_class = "files_write"
max_parallel = 1
status = "eligible"
''', encoding="utf-8")
    (root / "profiles.toml").write_text('''
[[profiles]]
id = "reviewer-read"
model = "reviewer"
harness = "fake-read"
status = "eligible"
success_probability = 0.99
capabilities = ["review", "reasoning"]
tool_class = "files_read"
max_parallel = 1
benchmark_version = "test"

[[profiles]]
id = "builder-write"
model = "builder"
harness = "fake-write"
status = "eligible"
success_probability = 0.99
capabilities = ["coding", "review", "reasoning", "file-editing"]
tool_class = "files_write"
max_parallel = 1
benchmark_version = "test"
''', encoding="utf-8")
    return Registry(root)


class GamingAgentsManagerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(dir=WORKSPACE, prefix=".gaming-agents-test-")
        self.sandbox = Path(self.temp.name)
        self.target = self.sandbox / "game"
        self.target_value = self.target.relative_to(WORKSPACE).as_posix()
        self.manager = manage.GamingAgentsManager(WORKSPACE, PACKAGE_ROOT)

    def tearDown(self):
        self.temp.cleanup()

    def initialize(self):
        return self.manager.init(self.target_value, "test-game")

    def write_director_outputs(self):
        state = self.target / ".game-agents"
        (state / "intent.md").write_text("# Intent\n\nBuild a deterministic offline score game for keyboard and pointer users. Keep the complete session under five minutes.\n", encoding="utf-8")
        docs = self.target / "docs"
        docs.mkdir(exist_ok=True)
        (docs / "game-brief.md").write_text("# Game Brief\n\nA deterministic offline score game with one clear action, visible feedback, restart, keyboard support, and a deliberately tiny MVP boundary.\n", encoding="utf-8")
        (docs / "acceptance-contract.md").write_text("# Acceptance Contract\n\nThe game boots offline, exposes the score action, changes visible state, supports keyboard input, restarts cleanly, and passes the independent unittest suite.\n", encoding="utf-8")
        game_spec = {
            "schema_version": 1,
            "game_id": "test-game",
            "engine": "python-test-fixture",
            "entrypoint": "src/game.py",
            "run_argv": ["{python}", "src/game.py"],
            "creative_artifacts": ["assets/tone.txt"],
            "engineer_artifacts": ["src/game.py", "tests/test_game.py"],
            "verifiers": [{"id": "game-tests", "argv": ["{python}", "-m", "unittest", "discover", "-s", "tests", "-v"], "timeout_seconds": 30}],
        }
        (docs / "game-spec.json").write_text(json.dumps(game_spec, indent=2) + "\n", encoding="utf-8")

    def approve_and_materialize(self):
        self.initialize()
        self.write_director_outputs()
        self.manager.approve(self.target_value)
        return self.manager.materialize_build(self.target_value)

    def test_rejects_traversal_foreign_paths_reserved_roots_and_bad_slug(self):
        with self.assertRaises(manage.GamingAgentsError):
            self.manager.init("../escape", "valid-game")
        with self.assertRaises(manage.GamingAgentsError):
            self.manager.init(str(self.target.resolve()), "valid-game")
        with self.assertRaises(manage.GamingAgentsError):
            self.manager.init("gaming-agents/nested", "valid-game")
        with self.assertRaises(manage.GamingAgentsError):
            self.manager.init(self.target_value, "Invalid Game")

    def test_init_creates_only_director_phase_and_valid_jobs(self):
        result = self.initialize()
        self.assertEqual(result["status"], "initialized")
        state = self.target / ".game-agents"
        self.assertTrue((state / "context" / "roles" / "game-director.md").is_file())
        director = load_job(state / "jobs" / "01-game-director.json")
        self.assertEqual(director.allowed_write_paths, ("docs/game-brief.md", "docs/acceptance-contract.md", "docs/game-spec.json"))
        self.assertFalse((state / "approval.json").exists())
        self.assertEqual(self.manager.validate(self.target_value)["phase"], "director")

    def test_missing_contract_blocks_approval(self):
        self.initialize()
        (self.target / ".game-agents" / "intent.md").write_text("A complete intent statement that is long enough to be deliberately approved by a human operator after review.\n", encoding="utf-8")
        with self.assertRaises(manage.GamingAgentsError):
            self.manager.approve(self.target_value)

    def test_stale_approval_blocks_build_materialization(self):
        self.initialize()
        self.write_director_outputs()
        self.manager.approve(self.target_value)
        with (self.target / "docs" / "game-brief.md").open("a", encoding="utf-8") as handle:
            handle.write("\nChanged after approval.\n")
        with self.assertRaises(manage.GamingAgentsError):
            self.manager.materialize_build(self.target_value)

    def test_materialized_qa_is_read_only_and_writers_have_ownership(self):
        self.approve_and_materialize()
        jobs = self.target / ".game-agents" / "jobs"
        creative = load_job(jobs / "02-creative-producer.json")
        engineer = load_job(jobs / "03-gameplay-engineer.json")
        qa = load_job(jobs / "04-qa-playtest.json")
        self.assertTrue(creative.allowed_write_paths)
        self.assertTrue(engineer.allowed_write_paths)
        self.assertEqual(qa.mode, "read")
        self.assertFalse(qa.allowed_write_paths)
        self.assertTrue(qa.verifiers)

    def test_cycle_in_materialized_graph_is_rejected(self):
        self.approve_and_materialize()
        path = self.target / ".game-agents" / "jobs" / "02-creative-producer.json"
        value = json.loads(path.read_text(encoding="utf-8"))
        value["dependencies"] = ["test-game-qa-playtest"]
        path.write_text(json.dumps(value, indent=2), encoding="utf-8")
        with self.assertRaises(manage.GamingAgentsError):
            self.manager.validate(self.target_value)

    def test_fake_adapter_workflow_reaches_independent_qa(self):
        self.initialize()
        state = self.target / ".game-agents"
        (state / "intent.md").write_text("# Intent\n\nBuild a deterministic offline score game for keyboard and pointer users. Keep the complete session under five minutes.\n", encoding="utf-8")
        registry = write_registry(self.sandbox / "registry")
        runtime = self.sandbox / "runtime"
        runtime.mkdir()
        director = load_job(state / "jobs" / "01-game-director.json")
        director_writes = {
            "docs/game-brief.md": "# Game Brief\n\nA deterministic offline score game with one action, visible feedback, restart, keyboard support, and a deliberately tiny MVP boundary.\n",
            "docs/acceptance-contract.md": "# Acceptance Contract\n\nThe game boots offline, changes score through a public action, supports keyboard input, restarts cleanly, and passes an independent test suite.\n",
            "docs/game-spec.json": json.dumps({
                "schema_version": 1, "game_id": "test-game", "engine": "python-test-fixture",
                "entrypoint": "src/game.py", "run_argv": ["{python}", "src/game.py"],
                "creative_artifacts": ["assets/tone.txt"],
                "engineer_artifacts": ["src/game.py", "tests/test_game.py"],
                "verifiers": [{"id": "game-tests", "argv": ["{python}", "-m", "unittest", "discover", "-s", "tests", "-v"], "timeout_seconds": 30}],
            }, indent=2) + "\n",
        }
        result = JobRunner(WORKSPACE, runtime, registry, {"fake-write": FakeAdapter(writes=director_writes)}).run(director)
        self.assertEqual(result["status"], "passed")
        self.manager.approve(self.target_value)
        self.manager.materialize_build(self.target_value)
        jobs = state / "jobs"
        creative = load_job(jobs / "02-creative-producer.json")
        creative_writes = {
            "docs/style-guide.md": "# Style Guide\n\nUse monochrome shapes, visible focus, concise motion, and one generated text-tone placeholder with explicit provenance.\n",
            "assets/asset-manifest.json": '{"schema_version":1,"assets":[{"path":"assets/tone.txt","category":"audio","author":"procedural","license":"CC0","placeholder":true}]}\n',
            "assets/tone.txt": "procedural tone placeholder\n",
        }
        result = JobRunner(WORKSPACE, runtime, registry, {"fake-write": FakeAdapter(writes=creative_writes)}).run(creative)
        self.assertEqual(result["status"], "passed")
        engineer = load_job(jobs / "03-gameplay-engineer.json")
        engineer_writes = {
            "src/game.py": "def score(value=0):\n    return value + 1\n",
            "tests/test_game.py": "import unittest\nfrom src.game import score\nclass GameTest(unittest.TestCase):\n    def test_score(self): self.assertEqual(score(), 1)\n",
            "docs/architecture.md": "# Architecture\n\nOne authoritative score function and one public deterministic transition.\n",
            "docs/implementation-handoff.md": "# Handoff\n\nThe deterministic score transition and independent test are ready for QA.\n",
        }
        result = JobRunner(WORKSPACE, runtime, registry, {"fake-write": FakeAdapter(writes=engineer_writes)}).run(engineer)
        self.assertEqual(result["status"], "passed")
        qa = load_job(jobs / "04-qa-playtest.json")
        qa_response = json.dumps({"decision": "pass", "findings": [], "evidence": ["game-tests"], "limitations": ["human fun not measured"]})
        result = JobRunner(WORKSPACE, runtime, registry, {"fake-read": FakeAdapter(final_text=qa_response)}).run(qa)
        self.assertEqual(result["status"], "passed")
        self.assertTrue(result["gates"]["verifiers"][0]["ok"])
        self.assertEqual(self.manager.validate(self.target_value)["phase"], "build")

    def test_offline_game_canary(self):
        canary = PACKAGE_ROOT / "examples" / "offline-canary"
        process = subprocess.run([sys.executable, "-m", "unittest", "-v"], cwd=canary, capture_output=True, text=True, timeout=30)
        self.assertEqual(process.returncode, 0, process.stdout + process.stderr)


if __name__ == "__main__":
    unittest.main()
