"""Validate the repository-local Company-OS without third-party dependencies."""

from __future__ import annotations

import argparse
import re
import sys
import tomllib
from pathlib import Path


EXPECTED_AGENTS = {
    "chief_of_staff": "workspace-write",
    "portfolio_strategist": "read-only",
    "finance_capital_allocator": "read-only",
    "legal_risk_governance": "read-only",
    "venture_product_lead": "workspace-write",
    "technology_architect": "workspace-write",
    "market_intelligence": "read-only",
    "customer_research": "read-only",
    "sales_partnerships": "workspace-write",
    "brand_growth": "workspace-write",
    "software_engineer": "workspace-write",
    "web_experience_designer": "workspace-write",
    "data_analytics_engineer": "workspace-write",
    "ai_automation_engineer": "workspace-write",
    "platform_devops": "workspace-write",
    "qa_reliability": "read-only",
    "security_privacy": "read-only",
    "operations_knowledge": "workspace-write",
}

COUNCIL = {
    "portfolio_strategist",
    "finance_capital_allocator",
    "legal_risk_governance",
    "venture_product_lead",
    "technology_architect",
}

EXPECTED_SKILLS = {
    "council-decision",
    "venture-intake",
    "initiative-planning",
    "delivery-handoff",
    "quality-gate",
    "weekly-operating-review",
}

REQUIRED_TEMPLATES = {
    "work-order.md",
    "agent-report.md",
    "council-decision.md",
    "venture-charter.md",
    "architecture-decision-record.md",
    "kpi-tree.md",
    "risk-register.md",
    "postmortem.md",
}

REQUIRED_FRONTMATTER = {"id", "status", "owner", "created", "review_date"}
ALLOWED_SANDBOXES = {"read-only", "workspace-write"}
REPO_PATH_PATTERN = re.compile(
    r"(?<![A-Za-z0-9_-])((?:company|ventures|products|shared|evals)/[A-Za-z0-9_./-]+\.md)"
)


def _read(path: Path, errors: list[str]) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        errors.append(f"Cannot read {path}: {exc}")
        return ""


def _frontmatter(text: str, path: Path, errors: list[str]) -> dict[str, str]:
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        errors.append(f"Missing YAML frontmatter in {path}")
        return {}
    try:
        end = next(index for index in range(1, len(lines)) if lines[index].strip() == "---")
    except StopIteration:
        errors.append(f"Unclosed YAML frontmatter in {path}")
        return {}

    values: dict[str, str] = {}
    for line in lines[1:end]:
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if ":" not in line:
            errors.append(f"Invalid frontmatter line in {path}: {line}")
            continue
        key, value = line.split(":", 1)
        values[key.strip()] = value.strip().strip('"\'')
    return values


def _validate_config(root: Path, errors: list[str]) -> None:
    path = root / ".codex" / "config.toml"
    try:
        config = tomllib.loads(_read(path, errors))
    except tomllib.TOMLDecodeError as exc:
        errors.append(f"Invalid TOML in {path}: {exc}")
        return
    agents = config.get("agents", {})
    if agents.get("max_threads") != 6:
        errors.append(".codex/config.toml must set agents.max_threads = 6")
    if agents.get("max_depth") != 1:
        errors.append(".codex/config.toml must set agents.max_depth = 1")


def _validate_agents(root: Path, errors: list[str]) -> None:
    directory = root / ".codex" / "agents"
    paths = sorted(directory.glob("*.toml"))
    if len(paths) != len(EXPECTED_AGENTS):
        errors.append(f"Expected 18 agent TOMLs, found {len(paths)}")

    seen: set[str] = set()
    for path in paths:
        try:
            data = tomllib.loads(_read(path, errors))
        except tomllib.TOMLDecodeError as exc:
            errors.append(f"Invalid TOML in {path}: {exc}")
            continue

        for field in ("name", "description", "developer_instructions"):
            value = data.get(field)
            if not isinstance(value, str) or not value.strip():
                errors.append(f"{path} requires non-empty string field {field}")

        name = data.get("name")
        if not isinstance(name, str):
            continue
        if name in seen:
            errors.append(f"Duplicate agent name: {name}")
        seen.add(name)
        if path.stem != name:
            errors.append(f"Agent filename {path.name} must match name {name}")

        sandbox = data.get("sandbox_mode")
        if sandbox not in ALLOWED_SANDBOXES:
            errors.append(f"Invalid sandbox_mode for {name}: {sandbox}")
        expected = EXPECTED_AGENTS.get(name)
        if expected is None:
            errors.append(f"Unexpected agent: {name}")
        elif sandbox != expected:
            errors.append(f"Agent {name} must use sandbox_mode {expected}")
        if "mcp_servers" in data:
            errors.append(f"Agent {name} must not configure MCP servers in v1")

    missing = set(EXPECTED_AGENTS) - seen
    if missing:
        errors.append(f"Missing agents: {', '.join(sorted(missing))}")
    if not COUNCIL.issubset(seen):
        errors.append("One or more required Council agents are missing")


def _validate_skills(root: Path, errors: list[str]) -> None:
    directory = root / ".agents" / "skills"
    seen: set[str] = set()
    for skill_dir in sorted(path for path in directory.iterdir() if path.is_dir()) if directory.exists() else []:
        skill_path = skill_dir / "SKILL.md"
        text = _read(skill_path, errors)
        metadata = _frontmatter(text, skill_path, errors)
        name = metadata.get("name", "")
        description = metadata.get("description", "")
        if name != skill_dir.name:
            errors.append(f"Skill folder {skill_dir.name} does not match skill name {name}")
        if not description or len(description) < 60:
            errors.append(f"Skill {skill_dir.name} needs a trigger-rich description")
        if set(metadata) - {"name", "description"}:
            errors.append(f"Skill {skill_dir.name} frontmatter may only contain name and description")
        if "TODO" in text:
            errors.append(f"Skill {skill_dir.name} still contains TODO text")
        seen.add(name)

        ui_path = skill_dir / "agents" / "openai.yaml"
        ui_text = _read(ui_path, errors)
        if f"${name}" not in ui_text:
            errors.append(f"Skill {name} UI default prompt must mention ${name}")

    if seen != EXPECTED_SKILLS:
        errors.append(
            "Skill set mismatch: expected "
            + ", ".join(sorted(EXPECTED_SKILLS))
            + "; found "
            + ", ".join(sorted(seen))
        )


def _validate_templates(root: Path, errors: list[str]) -> None:
    directory = root / "company" / "templates"
    found = {path.name for path in directory.glob("*.md")}
    if found != REQUIRED_TEMPLATES:
        errors.append(
            "Template set mismatch: missing "
            + ", ".join(sorted(REQUIRED_TEMPLATES - found))
            + "; unexpected "
            + ", ".join(sorted(found - REQUIRED_TEMPLATES))
        )
    ids: set[str] = set()
    for path in sorted(directory.glob("*.md")):
        metadata = _frontmatter(_read(path, errors), path, errors)
        missing = REQUIRED_FRONTMATTER - set(metadata)
        if missing:
            errors.append(f"{path} missing frontmatter fields: {', '.join(sorted(missing))}")
        artifact_id = metadata.get("id")
        if artifact_id in ids:
            errors.append(f"Duplicate template id: {artifact_id}")
        if artifact_id:
            ids.add(artifact_id)


def _validate_references(root: Path, errors: list[str]) -> None:
    markdown_paths = [
        path
        for path in root.rglob("*.md")
        if ".git" not in path.parts and path.name != "README.md"
    ]
    for source in markdown_paths:
        text = _read(source, errors)
        for relative in REPO_PATH_PATTERN.findall(text):
            if "<" in relative or ">" in relative:
                continue
            target = root / Path(relative)
            if not target.is_file():
                errors.append(f"Broken repository reference in {source}: {relative}")


def validate(root: Path) -> list[str]:
    """Return validation errors for a Company-OS repository root."""

    root = root.resolve()
    errors: list[str] = []
    for path in (
        root / "AGENTS.md",
        root / ".vscode" / "settings.json",
        root / "company" / "charter.md",
        root / "company" / "operating-model.md",
        root / "company" / "decision-rights.md",
        root / "company" / "agent-registry.md",
        root / "company" / "glossary.md",
        root / "ventures" / "_template" / "charter.md",
    ):
        if not path.is_file():
            errors.append(f"Missing required file: {path}")

    _validate_config(root, errors)
    _validate_agents(root, errors)
    _validate_skills(root, errors)
    _validate_templates(root, errors)
    _validate_references(root, errors)
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", nargs="?", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    errors = validate(args.root)
    if errors:
        print(f"Company-OS validation failed with {len(errors)} error(s):")
        for error in errors:
            print(f"- {error}")
        return 1
    print("Company-OS validation passed: 18 agents, 6 skills, governance, templates, and references are valid.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

