"""Validate portable agent-pack manifests without third-party dependencies."""

from __future__ import annotations

import argparse
import json
from pathlib import Path, PurePosixPath
import re
import sys
from typing import Any


ID = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*\Z")
KINDS = {"role-pack", "workflow-pack", "operating-system"}
COMPONENT_KINDS = {
    "agent_definitions": "agent_definition",
    "skills": "skill",
    "workflows": "workflow",
    "resources": "resource",
}
REQUIRED = {
    "schema_version", "id", "kind", "name", "version", "description",
    "components", "entrypoints", "verification",
}
ALLOWED = REQUIRED | {"adapters"}


def _portable_path(value: Any) -> bool:
    if not isinstance(value, str) or not value:
        return False
    path = PurePosixPath(value.replace("\\", "/"))
    return not path.is_absolute() and ".." not in path.parts and not re.match(r"^[A-Za-z]:", value)


def _items(value: Any, name: str, errors: list[str]) -> list[Any]:
    if not isinstance(value, list):
        errors.append(f"{name} must be an array")
        return []
    return value


def validate_manifest(path: Path) -> list[str]:
    errors: list[str] = []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return [f"{path}: cannot read manifest: {exc}"]
    if not isinstance(data, dict):
        return [f"{path}: manifest must be an object"]

    missing = REQUIRED - set(data)
    extra = set(data) - ALLOWED
    if missing:
        errors.append(f"{path}: missing fields: {', '.join(sorted(missing))}")
    if extra:
        errors.append(f"{path}: unexpected fields: {', '.join(sorted(extra))}")
    if data.get("schema_version") != 1:
        errors.append(f"{path}: schema_version must be 1")
    if not isinstance(data.get("id"), str) or not ID.fullmatch(data["id"]):
        errors.append(f"{path}: id must be lowercase kebab-case")
    if data.get("kind") not in KINDS:
        errors.append(f"{path}: unsupported kind {data.get('kind')!r}")
    if path.parent.name != data.get("id"):
        errors.append(f"{path}: directory name must match pack id")

    components = data.get("components")
    component_refs: set[str] = set()
    if not isinstance(components, dict):
        errors.append(f"{path}: components must be an object")
        components = {}
    if set(components) != set(COMPONENT_KINDS):
        errors.append(f"{path}: components must declare exactly {', '.join(COMPONENT_KINDS)}")
    for collection, singular in COMPONENT_KINDS.items():
        seen: set[str] = set()
        for index, item in enumerate(_items(components.get(collection), f"{path}:{collection}", errors)):
            label = f"{path}:{collection}[{index}]"
            if not isinstance(item, dict):
                errors.append(f"{label} must be an object")
                continue
            item_id = item.get("id")
            if not isinstance(item_id, str) or not ID.fullmatch(item_id):
                errors.append(f"{label}.id must be lowercase kebab-case")
            elif item_id in seen:
                errors.append(f"{label}.id is duplicated")
            else:
                seen.add(item_id)
                component_refs.add(f"{singular}:{item_id}")
            relative = item.get("path")
            if not _portable_path(relative):
                errors.append(f"{label}.path must be a portable relative path")
            elif not (path.parent / Path(relative)).exists():
                errors.append(f"{label}.path does not exist: {relative}")
            elif collection == "agent_definitions" and Path(relative).suffix == ".json":
                definition_path = path.parent / Path(relative)
                try:
                    definition = json.loads(definition_path.read_text(encoding="utf-8"))
                except (OSError, json.JSONDecodeError) as exc:
                    errors.append(f"{label}.path is not valid agent-definition JSON: {exc}")
                else:
                    required_definition = {"schema_version", "id", "name", "description", "instructions", "permissions"}
                    if not isinstance(definition, dict) or set(definition) != required_definition:
                        errors.append(f"{label}.path has an invalid agent-definition field set")
                    elif definition.get("schema_version") != 1 or definition.get("id") != item_id:
                        errors.append(f"{label}.path identity must match the component")
            if not isinstance(item.get("description"), str) or not item["description"].strip():
                errors.append(f"{label}.description must be non-empty")
            capabilities = item.get("capabilities", [])
            if not isinstance(capabilities, list) or any(not isinstance(value, str) or not ID.fullmatch(value) for value in capabilities):
                errors.append(f"{label}.capabilities must contain kebab-case ids")

    entry_ids: set[str] = set()
    for index, entry in enumerate(_items(data.get("entrypoints"), f"{path}:entrypoints", errors)):
        label = f"{path}:entrypoints[{index}]"
        if not isinstance(entry, dict):
            errors.append(f"{label} must be an object")
            continue
        entry_id = entry.get("id")
        if not isinstance(entry_id, str) or not ID.fullmatch(entry_id):
            errors.append(f"{label}.id must be lowercase kebab-case")
        elif entry_id in entry_ids:
            errors.append(f"{label}.id is duplicated")
        else:
            entry_ids.add(entry_id)
        expected_prefix = entry.get("kind")
        component = entry.get("component")
        if expected_prefix not in {"agent_definition", "skill", "workflow"}:
            errors.append(f"{label}.kind is invalid")
        elif not isinstance(component, str) or component not in component_refs or not component.startswith(expected_prefix + ":"):
            errors.append(f"{label}.component must reference a declared {expected_prefix}")

    for group in ("adapters", "verification"):
        for index, item in enumerate(_items(data.get(group, []), f"{path}:{group}", errors)):
            label = f"{path}:{group}[{index}]"
            if not isinstance(item, dict):
                errors.append(f"{label} must be an object")
                continue
            if group == "adapters":
                relative = item.get("path")
                if not _portable_path(relative) or not (path.parent / Path(relative)).exists():
                    errors.append(f"{label}.path must name an existing portable path")
            else:
                argv = item.get("argv")
                if not isinstance(argv, list) or not argv or any(not isinstance(arg, str) or not arg for arg in argv):
                    errors.append(f"{label}.argv must be a non-empty string array")
    return errors


def validate_all(root: Path) -> list[str]:
    manifests = sorted(root.glob("*/agent-pack.json"))
    if not manifests:
        return [f"{root}: no agent-pack.json manifests found"]
    errors: list[str] = []
    for manifest in manifests:
        errors.extend(validate_manifest(manifest))
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", nargs="?", type=Path, default=Path(__file__).resolve().parent)
    args = parser.parse_args()
    errors = validate_all(args.root.resolve())
    if errors:
        print(f"Agent-pack validation failed with {len(errors)} error(s):")
        for error in errors:
            print(f"- {error}")
        return 1
    print("Agent-pack validation passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
