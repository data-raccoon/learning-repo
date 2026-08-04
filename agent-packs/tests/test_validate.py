from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("agent_pack_validate", ROOT / "validate.py")
assert SPEC is not None and SPEC.loader is not None
validator = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(validator)


class AgentPackValidationTests(unittest.TestCase):
    def test_repository_packs_validate(self) -> None:
        self.assertEqual([], validator.validate_all(ROOT))

    def test_rejects_missing_component_path(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            pack = root / "sample"
            pack.mkdir()
            manifest = {
                "schema_version": 1,
                "id": "sample",
                "kind": "role-pack",
                "name": "Sample",
                "version": "1.0.0",
                "description": "A sample portable agent pack for validation.",
                "components": {
                    "agent_definitions": [{"id": "reviewer", "path": "missing.md", "description": "Review."}],
                    "skills": [],
                    "workflows": [],
                    "resources": []
                },
                "entrypoints": [{"id": "review", "kind": "agent_definition", "component": "agent_definition:reviewer"}],
                "verification": [{"id": "check", "argv": ["{python}", "check.py"]}]
            }
            (pack / "agent-pack.json").write_text(json.dumps(manifest), encoding="utf-8")
            errors = validator.validate_all(root)
            self.assertTrue(any("does not exist" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
