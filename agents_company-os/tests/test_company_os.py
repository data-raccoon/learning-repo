from __future__ import annotations

import shutil
import tempfile
import unittest
from pathlib import Path

from scripts.validate_company_os import validate


ROOT = Path(__file__).resolve().parents[1]


class CompanyOSValidationTests(unittest.TestCase):
    def make_fixture(self) -> tuple[tempfile.TemporaryDirectory[str], Path]:
        temporary = tempfile.TemporaryDirectory()
        fixture = Path(temporary.name) / "company-os"
        shutil.copytree(
            ROOT,
            fixture,
            ignore=shutil.ignore_patterns(".git", "__pycache__", "*.pyc"),
        )
        return temporary, fixture

    def test_repository_is_valid(self) -> None:
        self.assertEqual(validate(ROOT), [])

    def test_duplicate_agent_fixture_is_rejected(self) -> None:
        temporary, fixture = self.make_fixture()
        self.addCleanup(temporary.cleanup)
        source = fixture / ".codex" / "agents" / "portfolio_strategist.toml"
        duplicate = fixture / ".codex" / "agents" / "duplicate.toml"
        duplicate.write_text(source.read_text(encoding="utf-8"), encoding="utf-8")
        errors = validate(fixture)
        self.assertTrue(any("Duplicate agent name" in error for error in errors), errors)

    def test_invalid_skill_fixture_is_rejected(self) -> None:
        temporary, fixture = self.make_fixture()
        self.addCleanup(temporary.cleanup)
        skill = fixture / ".agents" / "skills" / "venture-intake" / "SKILL.md"
        skill.write_text(skill.read_text(encoding="utf-8").replace("name: venture-intake", "name: wrong-name"), encoding="utf-8")
        errors = validate(fixture)
        self.assertTrue(any("does not match skill name" in error for error in errors), errors)

    def test_broken_reference_fixture_is_rejected(self) -> None:
        temporary, fixture = self.make_fixture()
        self.addCleanup(temporary.cleanup)
        agents = fixture / "AGENTS.md"
        agents.write_text(agents.read_text(encoding="utf-8") + "\nSee `company/missing.md`.\n", encoding="utf-8")
        errors = validate(fixture)
        self.assertTrue(any("Broken repository reference" in error for error in errors), errors)


if __name__ == "__main__":
    unittest.main()

