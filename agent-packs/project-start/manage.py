"""Create and validate bounded project-discovery and architecture workflows."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
from pathlib import Path, PurePosixPath
import re
import shutil
import sys
from typing import Any


PACKAGE_ROOT = Path(__file__).resolve().parent
WORKSPACE = PACKAGE_ROOT.parents[1]
HARNESS_PATH = WORKSPACE / "model-execution-harness" / "core" / "harness.py"
STATE = ".projectstart"
SLUG = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*\Z")
PLACEHOLDER = re.compile(r"\[TBD", re.IGNORECASE)
PROTECTED_ROOTS = {".agents", ".codex", ".git", "agent-packs", "local-models", "model-execution-harness"}
RENDERED = (
    "README.md",
    "AGENTS.md",
    "docs/PRODUCT.md",
    "docs/ARCHITECTURE.md",
    "docs/ACCEPTANCE.md",
    "docs/decisions/ADR-0001-initial-architecture.md",
    "bootstrap-plan.json",
)


class ProjectStartError(ValueError):
    """A fail-closed lifecycle or contract error."""


def read_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise ProjectStartError(f"cannot read JSON {path}: {error}") from error


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def exact(value: Any, fields: set[str], label: str) -> dict[str, Any]:
    if not isinstance(value, dict) or set(value) != fields:
        actual = set(value) if isinstance(value, dict) else set()
        raise ProjectStartError(f"{label} fields mismatch; missing={sorted(fields - actual)}, unknown={sorted(actual - fields)}")
    return value


def text(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip() or PLACEHOLDER.search(value):
        raise ProjectStartError(f"{label} must be complete non-placeholder text")
    return value.strip()


def texts(value: Any, label: str, *, allow_empty: bool = False) -> list[str]:
    if not isinstance(value, list) or (not value and not allow_empty):
        raise ProjectStartError(f"{label} must be {'an array' if allow_empty else 'a non-empty array'}")
    return [text(item, f"{label}[{index}]") for index, item in enumerate(value)]


def relative_file(value: Any, label: str) -> str:
    candidate = text(value, label).replace("\\", "/")
    path = PurePosixPath(candidate)
    if path.is_absolute() or ".." in path.parts or "." in path.parts or candidate.endswith("/") or any(character in candidate for character in "*?[]"):
        raise ProjectStartError(f"{label} must be an individual normalized relative file: {value}")
    if candidate.startswith(STATE + "/"):
        raise ProjectStartError(f"{label} must not target lifecycle state")
    return path.as_posix()


def slice_all(path: str) -> dict[str, Any]:
    return {"path": path, "start": 1, "end": 10_000_000}


def limits(*, critical: bool = False) -> dict[str, int]:
    return {
        "packet_chars": 80_000 if critical else 50_000,
        "output_chars": 30_000 if critical else 18_000,
        "model_context_tokens": 16_384 if critical else 8_192,
        "model_output_tokens": 4_096 if critical else 2_048,
        "model_timeout_seconds": 900 if critical else 600,
        "max_tool_calls": 16,
        "max_verifiers": 0,
        "verifier_timeout_seconds": 120,
    }


class ProjectStartManager:
    def __init__(self, workspace: Path = WORKSPACE, package_root: Path = PACKAGE_ROOT):
        self.workspace = workspace.resolve()
        self.package_root = package_root.resolve()

    def target(self, value: str, *, create: bool = False) -> Path:
        raw = PurePosixPath(value.replace("\\", "/"))
        if raw.is_absolute() or not raw.parts or ".." in raw.parts or "." in raw.parts:
            raise ProjectStartError("target must be a normalized repository-relative subdirectory")
        if raw.parts[0].casefold() in {item.casefold() for item in PROTECTED_ROOTS}:
            raise ProjectStartError(f"target root is reserved: {raw.parts[0]}")
        current = self.workspace
        for part in raw.parts:
            current = current / part
            if current.is_symlink():
                raise ProjectStartError(f"target contains a symbolic link: {value}")
        resolved = self.workspace.joinpath(*raw.parts).resolve(strict=False)
        try:
            resolved.relative_to(self.workspace)
        except ValueError as error:
            raise ProjectStartError("target escapes the workspace") from error
        if resolved == self.workspace:
            raise ProjectStartError("target must not be the workspace root")
        if create:
            resolved.mkdir(parents=True, exist_ok=True)
        if not resolved.is_dir():
            raise ProjectStartError(f"target does not exist: {value}")
        return resolved

    def target_value(self, target: Path) -> str:
        return target.relative_to(self.workspace).as_posix()

    def pack_path(self, pack_id: str) -> Path:
        if not SLUG.fullmatch(pack_id):
            raise ProjectStartError("stack-pack ID must be a lowercase kebab-case slug")
        path = self.package_root / "stack-packs" / f"{pack_id}.json"
        if not path.is_file():
            raise ProjectStartError(f"unknown stack pack: {pack_id}")
        return path

    def init(self, target_value: str, project_id: str, stack_pack: str) -> dict[str, Any]:
        if not SLUG.fullmatch(project_id):
            raise ProjectStartError("project ID must be a lowercase kebab-case slug")
        pack_path = self.pack_path(stack_pack)
        target = self.target(target_value, create=True)
        state = target / STATE
        if state.exists():
            raise ProjectStartError(f"ProjectStart state already exists: {state}")
        reserved_outputs = ("project-intent.json", "discovery.json", "project-design.json", "architecture-review.json", *RENDERED)
        collisions = [name for name in reserved_outputs if (target / name).exists()]
        if collisions:
            raise ProjectStartError("refusing to initialize over existing project files: " + ", ".join(collisions))
        for directory in (state / "context" / "agent-definitions", state / "context" / "templates", state / "context" / "catalog", state / "context" / "stack-packs", state / "tasks", state / "evidence"):
            directory.mkdir(parents=True, exist_ok=True)
        for source in (self.package_root / "agent-definitions").glob("*.md"):
            shutil.copyfile(source, state / "context" / "agent-definitions" / source.name)
        for source in (self.package_root / "templates").glob("*.json"):
            shutil.copyfile(source, state / "context" / "templates" / source.name)
        shutil.copyfile(self.package_root / "catalog" / "archetypes.json", state / "context" / "catalog" / "archetypes.json")
        shutil.copyfile(pack_path, state / "context" / "stack-packs" / pack_path.name)
        intent = read_json(self.package_root / "templates" / "project-intent.example.json")
        intent["project_id"] = project_id
        write_json(target / "project-intent.json", intent)
        write_json(state / "state.json", {
            "schema_version": 1,
            "project_id": project_id,
            "stack_pack": stack_pack,
            "phase": "intent",
            "created_at": datetime.now(timezone.utc).isoformat(),
        })
        return {"status": "initialized", "project_id": project_id, "target": self.target_value(target), "next": "complete project-intent.json"}

    def state(self, target: Path) -> dict[str, Any]:
        state = read_json(target / STATE / "state.json")
        exact(state, {"schema_version", "project_id", "stack_pack", "phase", "created_at"}, "state")
        if state["schema_version"] != 1 or not SLUG.fullmatch(str(state["project_id"])):
            raise ProjectStartError("invalid ProjectStart state")
        return state

    def validate_intent(self, target: Path) -> dict[str, Any]:
        value = read_json(target / "project-intent.json")
        exact(value, {"schema_version", "project_id", "product", "requirements", "constraints", "decision_policy"}, "intent")
        state = self.state(target)
        if value["schema_version"] != 1 or value["project_id"] != state["project_id"]:
            raise ProjectStartError("intent identity does not match initialized state")
        product = exact(value["product"], {"promise", "primary_user", "journeys", "mvp", "exclusions"}, "intent.product")
        text(product["promise"], "intent.product.promise")
        text(product["primary_user"], "intent.product.primary_user")
        for field in ("journeys", "mvp", "exclusions"):
            texts(product[field], f"intent.product.{field}")
        requirements = value["requirements"]
        if not isinstance(requirements, list) or not requirements:
            raise ProjectStartError("intent.requirements must be non-empty")
        ids: set[str] = set()
        for index, item in enumerate(requirements):
            item = exact(item, {"id", "category", "statement", "status", "authority"}, f"intent.requirements[{index}]")
            requirement_id = text(item["id"], f"intent.requirements[{index}].id")
            if requirement_id in ids:
                raise ProjectStartError(f"duplicate requirement ID: {requirement_id}")
            ids.add(requirement_id)
            text(item["category"], f"intent.requirements[{index}].category")
            text(item["statement"], f"intent.requirements[{index}].statement")
            if item["status"] not in {"known", "unknown", "not_applicable", "model_may_decide"}:
                raise ProjectStartError(f"invalid requirement status: {item['status']}")
            if item["authority"] not in {"human", "model"}:
                raise ProjectStartError(f"invalid requirement authority: {item['authority']}")
            if item["status"] == "unknown":
                raise ProjectStartError(f"unresolved requirement must be answered before discovery: {requirement_id}")
        constraints = exact(value["constraints"], {"integrations", "data_sensitivity", "persistence", "availability", "scale", "security_compliance", "team_operations", "budget_schedule"}, "intent.constraints")
        for key, item in constraints.items():
            text(item, f"intent.constraints.{key}")
        policy = exact(value["decision_policy"], {"human_decides", "model_may_decide"}, "intent.decision_policy")
        texts(policy["human_decides"], "intent.decision_policy.human_decides")
        texts(policy["model_may_decide"], "intent.decision_policy.model_may_decide")
        return value

    def archetypes(self, target: Path) -> dict[str, dict[str, Any]]:
        catalog = read_json(target / STATE / "context" / "catalog" / "archetypes.json")
        if not isinstance(catalog, dict) or catalog.get("schema_version") != 1 or not isinstance(catalog.get("archetypes"), list):
            raise ProjectStartError("invalid archetype catalog")
        result = {item.get("id"): item for item in catalog["archetypes"] if isinstance(item, dict) and isinstance(item.get("id"), str)}
        if len(result) != len(catalog["archetypes"]):
            raise ProjectStartError("archetype IDs must be present and unique")
        return result

    def stack_pack(self, target: Path) -> dict[str, Any]:
        state = self.state(target)
        pack = read_json(target / STATE / "context" / "stack-packs" / f"{state['stack_pack']}.json")
        exact(pack, {"schema_version", "id", "summary", "components", "allowed_dependency_families", "forbidden_patterns", "required_artifacts", "generator", "verification_profile"}, "stack pack")
        if pack["schema_version"] != 1 or pack["id"] != state["stack_pack"] or not isinstance(pack["components"], dict):
            raise ProjectStartError("stack pack identity or components are invalid")
        return pack

    def task(self, target: Path, *, task_id: str, goal: str, profile: str, capability: str, importance: str,
             context: list[str], output: str, done: list[str], forbidden: list[str]) -> dict[str, Any]:
        if not isinstance(profile, str) or not profile.strip() or profile == "auto":
            raise ProjectStartError("profile must name an explicit harness profile")
        return {
            "v": 1,
            "id": task_id,
            "goal": goal,
            "target": self.target_value(target),
            "model": {"profile": profile, "capability": capability, "importance": importance},
            "context": [slice_all(path) for path in context],
            "write_roots": [output],
            "done": done,
            "forbidden": forbidden,
            "limits": limits(critical=importance == "critical"),
            "verifiers": [],
        }

    def prepare_discovery(self, target_value: str, profile: str) -> dict[str, Any]:
        target = self.target(target_value)
        intent = self.validate_intent(target)
        state = self.state(target)
        task = self.task(
            target,
            task_id=f"{state['project_id']}-discovery",
            goal="Normalize the human intent, expose conflicts and consequential questions, and rank at most three admitted archetypes without designing the system.",
            profile=profile,
            capability="reasoning",
            importance="high",
            context=[
                "project-intent.json",
                f"{STATE}/context/agent-definitions/project-discovery.md",
                f"{STATE}/context/templates/discovery.schema.json",
                f"{STATE}/context/catalog/archetypes.json",
                f"{STATE}/context/stack-packs/{state['stack_pack']}.json",
            ],
            output="discovery.json",
            done=["The output conforms to discovery.schema.json.", "Unknowns remain questions rather than hidden assumptions.", "Candidate archetypes cite supplied requirements."],
            forbidden=["Do not design modules or artifacts.", "Do not browse, execute commands, edit lifecycle state, or choose unpinned technology."],
        )
        write_json(target / STATE / "tasks" / "01-discovery.task.json", task)
        state["phase"] = "discovery"
        write_json(target / STATE / "state.json", state)
        return {"status": "materialized", "phase": "discovery", "task": f"{STATE}/tasks/01-discovery.task.json", "requirements": len(intent["requirements"])}

    def validate_discovery(self, target: Path) -> dict[str, Any]:
        value = read_json(target / "discovery.json")
        exact(value, {"schema_version", "project_id", "normalized_requirements", "conflicts", "blocking_questions", "assumptions", "candidate_archetypes", "recommendation"}, "discovery")
        state = self.state(target)
        if value["schema_version"] != 1 or value["project_id"] != state["project_id"]:
            raise ProjectStartError("discovery identity is invalid")
        if not isinstance(value["normalized_requirements"], list) or not value["normalized_requirements"]:
            raise ProjectStartError("discovery must contain normalized requirements")
        normalized_ids: set[str] = set()
        for index, item in enumerate(value["normalized_requirements"]):
            item = exact(item, {"id", "statement", "status", "source_ids"}, f"normalized_requirements[{index}]")
            requirement_id = text(item["id"], f"normalized_requirements[{index}].id")
            if requirement_id in normalized_ids:
                raise ProjectStartError(f"duplicate normalized requirement ID: {requirement_id}")
            normalized_ids.add(requirement_id)
            text(item["statement"], f"normalized_requirements[{index}].statement")
            if item["status"] not in {"fact", "constraint", "preference", "model_decision"}:
                raise ProjectStartError("normalized requirement status is invalid")
            texts(item["source_ids"], f"normalized_requirements[{index}].source_ids")
        texts(value["conflicts"], "discovery.conflicts", allow_empty=True)
        texts(value["blocking_questions"], "discovery.blocking_questions", allow_empty=True)
        texts(value["assumptions"], "discovery.assumptions", allow_empty=True)
        candidates = value["candidate_archetypes"]
        if not isinstance(candidates, list) or not 1 <= len(candidates) <= 3:
            raise ProjectStartError("discovery must recommend 1..3 candidate archetypes")
        admitted = self.archetypes(target)
        seen: set[str] = set()
        for index, item in enumerate(candidates):
            item = exact(item, {"id", "fit", "reason"}, f"candidate_archetypes[{index}]")
            if item["id"] not in admitted or item["id"] in seen:
                raise ProjectStartError(f"candidate archetype is unknown or duplicated: {item['id']}")
            seen.add(item["id"])
            if item["fit"] not in {"strong", "possible", "weak"}:
                raise ProjectStartError("candidate fit is invalid")
            text(item["reason"], f"candidate_archetypes[{index}].reason")
        text(value["recommendation"], "discovery.recommendation")
        return value

    def accept_discovery(self, target_value: str) -> dict[str, Any]:
        target = self.target(target_value)
        self.validate_intent(target)
        discovery = self.validate_discovery(target)
        if discovery["conflicts"] or discovery["blocking_questions"]:
            raise ProjectStartError("resolve every discovery conflict and blocking question before acceptance")
        state = self.state(target)
        bound = [
            "project-intent.json", "discovery.json",
            f"{STATE}/context/agent-definitions/project-discovery.md",
            f"{STATE}/context/templates/project-intent.schema.json",
            f"{STATE}/context/templates/discovery.schema.json",
            f"{STATE}/context/templates/archetypes.schema.json",
            f"{STATE}/context/templates/stack-pack.schema.json",
            f"{STATE}/context/catalog/archetypes.json",
            f"{STATE}/context/stack-packs/{state['stack_pack']}.json",
        ]
        manifest = {
            "schema_version": 1,
            "project_id": state["project_id"],
            "accepted_at": datetime.now(timezone.utc).isoformat(),
            "sha256": {name: sha256(target / name) for name in bound},
        }
        write_json(target / STATE / "intent-approval.json", manifest)
        state["phase"] = "intent-approved"
        write_json(target / STATE / "state.json", state)
        return {"status": "accepted", "project_id": state["project_id"], "sha256": manifest["sha256"]}

    def verified_intent(self, target: Path) -> dict[str, Any]:
        approval = read_json(target / STATE / "intent-approval.json")
        if not isinstance(approval, dict) or approval.get("schema_version") != 1 or approval.get("project_id") != self.state(target)["project_id"]:
            raise ProjectStartError("intent approval is invalid")
        hashes = approval.get("sha256")
        if not isinstance(hashes, dict) or not hashes:
            raise ProjectStartError("intent approval has no bound inputs")
        stale = [name for name, expected in hashes.items() if not (target / name).is_file() or sha256(target / name) != expected]
        if stale:
            raise ProjectStartError("intent approval is stale for: " + ", ".join(sorted(stale)))
        return approval

    def materialize_architecture(self, target_value: str, profile: str) -> dict[str, Any]:
        target = self.target(target_value)
        approval = self.verified_intent(target)
        state = self.state(target)
        task = self.task(
            target,
            task_id=f"{state['project_id']}-architecture",
            goal="Create one minimal typed architecture that satisfies the accepted discovery result and selected stack pack.",
            profile=profile,
            capability="architecture",
            importance="critical",
            context=[
                "project-intent.json", "discovery.json",
                f"{STATE}/context/agent-definitions/project-architect.md",
                f"{STATE}/context/templates/project-design.schema.json",
                f"{STATE}/context/catalog/archetypes.json",
                f"{STATE}/context/stack-packs/{state['stack_pack']}.json",
            ],
            output="project-design.json",
            done=["The output conforms to project-design.schema.json.", "Modules are minimal, owned, and acyclic.", "The first vertical slice validates the riskiest boundary."],
            forbidden=["Do not generate source code, prose documents, commands, binaries, or new dependencies.", "Do not browse, edit lifecycle state, or answer an unresolved consequential question by guessing."],
        )
        write_json(target / STATE / "tasks" / "02-architecture.task.json", task)
        state["phase"] = "architecture"
        write_json(target / STATE / "state.json", state)
        return {"status": "materialized", "phase": "architecture", "task": f"{STATE}/tasks/02-architecture.task.json", "intent_sha256": approval["sha256"]}

    def validate_design(self, target: Path) -> dict[str, Any]:
        design = read_json(target / "project-design.json")
        fields = {"schema_version", "project_id", "stack", "selected_archetype", "modules", "data_stores", "external_interfaces", "security_model", "operational_model", "decisions", "risks", "acceptance_criteria", "artifact_plan", "first_vertical_slice", "open_questions", "confidence"}
        exact(design, fields, "design")
        state = self.state(target)
        if design["schema_version"] != 1 or design["project_id"] != state["project_id"]:
            raise ProjectStartError("design identity is invalid")
        stack = exact(design["stack"], {"pack_id", "components"}, "design.stack")
        pack = self.stack_pack(target)
        if stack["pack_id"] != pack["id"] or stack["components"] != pack["components"]:
            raise ProjectStartError("design stack must exactly match the admitted stack pack")
        selected = exact(design["selected_archetype"], {"id", "rationale", "deviations"}, "design.selected_archetype")
        archetypes = self.archetypes(target)
        if selected["id"] not in archetypes:
            raise ProjectStartError("selected archetype is not admitted")
        discovery_candidates = {item["id"] for item in self.validate_discovery(target)["candidate_archetypes"]}
        if selected["id"] not in discovery_candidates:
            raise ProjectStartError("selected archetype was not admitted by the accepted discovery shortlist")
        text(selected["rationale"], "design.selected_archetype.rationale")
        texts(selected["deviations"], "design.selected_archetype.deviations", allow_empty=True)
        modules = design["modules"]
        if not isinstance(modules, list) or not modules:
            raise ProjectStartError("design.modules must be non-empty")
        if len(modules) > int(archetypes[selected["id"]]["max_initial_modules"]):
            raise ProjectStartError("initial module count exceeds the selected archetype limit")
        module_ids: set[str] = set()
        dependencies: dict[str, list[str]] = {}
        for index, item in enumerate(modules):
            item = exact(item, {"id", "responsibility", "owner", "depends_on", "runtime", "public_interfaces"}, f"design.modules[{index}]")
            module_id = text(item["id"], f"design.modules[{index}].id")
            if module_id in module_ids:
                raise ProjectStartError(f"duplicate module ID: {module_id}")
            module_ids.add(module_id)
            text(item["responsibility"], f"design.modules[{index}].responsibility")
            text(item["owner"], f"design.modules[{index}].owner")
            dependencies[module_id] = texts(item["depends_on"], f"design.modules[{index}].depends_on", allow_empty=True)
            text(item["runtime"], f"design.modules[{index}].runtime")
            texts(item["public_interfaces"], f"design.modules[{index}].public_interfaces", allow_empty=True)
        for module_id, required in dependencies.items():
            unknown = set(required) - module_ids
            if unknown or module_id in required:
                raise ProjectStartError(f"module {module_id} has invalid dependencies: {sorted(unknown or {module_id})}")
        self._assert_acyclic(dependencies)
        stores = design["data_stores"]
        if not isinstance(stores, list):
            raise ProjectStartError("design.data_stores must be an array")
        store_ids: set[str] = set()
        for index, item in enumerate(stores):
            item = exact(item, {"id", "purpose", "owner", "schema_strategy", "migration_strategy", "sensitivity"}, f"design.data_stores[{index}]")
            for field in item:
                text(item[field], f"design.data_stores[{index}].{field}")
            if item["id"] in store_ids:
                raise ProjectStartError(f"duplicate data-store ID: {item['id']}")
            store_ids.add(item["id"])
        interfaces = design["external_interfaces"]
        if not isinstance(interfaces, list):
            raise ProjectStartError("design.external_interfaces must be an array")
        interface_ids: set[str] = set()
        for index, item in enumerate(interfaces):
            item = exact(item, {"id", "direction", "protocol", "owner", "validation", "failure_behavior"}, f"design.external_interfaces[{index}]")
            if item["direction"] not in {"inbound", "outbound", "bidirectional"}:
                raise ProjectStartError("external-interface direction is invalid")
            for field in ("id", "protocol", "owner", "validation", "failure_behavior"):
                text(item[field], f"design.external_interfaces[{index}].{field}")
            if item["id"] in interface_ids:
                raise ProjectStartError(f"duplicate external-interface ID: {item['id']}")
            interface_ids.add(item["id"])
        security = exact(design["security_model"], {"trust_boundaries", "authentication", "authorization", "secrets", "input_validation"}, "design.security_model")
        texts(security["trust_boundaries"], "design.security_model.trust_boundaries", allow_empty=True)
        for field in ("authentication", "authorization", "secrets", "input_validation"):
            text(security[field], f"design.security_model.{field}")
        operations = exact(design["operational_model"], {"deployment", "configuration", "observability", "backup_recovery"}, "design.operational_model")
        for field, item in operations.items():
            text(item, f"design.operational_model.{field}")
        decisions = design["decisions"]
        if not isinstance(decisions, list) or not decisions:
            raise ProjectStartError("design.decisions must be non-empty")
        decision_ids = [item.get("id") for item in decisions if isinstance(item, dict)]
        if len(decision_ids) != len(decisions) or len(set(decision_ids)) != len(decision_ids):
            raise ProjectStartError("decision IDs must be present and unique")
        for index, item in enumerate(decisions):
            item = exact(item, {"id", "question", "selected", "alternatives", "evidence", "consequences", "reversal_cost", "confidence", "revisit_trigger"}, f"design.decisions[{index}]")
            if not re.fullmatch(r"ADR-[0-9]{4}", item["id"]):
                raise ProjectStartError(f"invalid decision ID: {item['id']}")
            for field in ("question", "selected", "revisit_trigger"):
                text(item[field], f"design.decisions[{index}].{field}")
            texts(item["alternatives"], f"design.decisions[{index}].alternatives", allow_empty=True)
            texts(item["evidence"], f"design.decisions[{index}].evidence")
            texts(item["consequences"], f"design.decisions[{index}].consequences")
            if item["reversal_cost"] not in {"low", "medium", "high"} or item["confidence"] not in {"low", "medium", "high"}:
                raise ProjectStartError("decision confidence or reversal cost is invalid")
        risks = design["risks"]
        if not isinstance(risks, list):
            raise ProjectStartError("design.risks must be an array")
        risk_ids: set[str] = set()
        for index, item in enumerate(risks):
            item = exact(item, {"id", "description", "likelihood", "impact", "mitigation", "owner"}, f"design.risks[{index}]")
            for field in ("id", "description", "mitigation", "owner"):
                text(item[field], f"design.risks[{index}].{field}")
            if item["likelihood"] not in {"low", "medium", "high"} or item["impact"] not in {"low", "medium", "high"}:
                raise ProjectStartError("risk likelihood or impact is invalid")
            if item["id"] in risk_ids:
                raise ProjectStartError(f"duplicate risk ID: {item['id']}")
            risk_ids.add(item["id"])
        criteria = design["acceptance_criteria"]
        if not isinstance(criteria, list) or not criteria:
            raise ProjectStartError("design.acceptance_criteria must be non-empty")
        criterion_ids = [item.get("id") for item in criteria if isinstance(item, dict)]
        if len(criterion_ids) != len(criteria) or len(set(criterion_ids)) != len(criterion_ids):
            raise ProjectStartError("acceptance criterion IDs must be present and unique")
        intent_requirement_ids = {item["id"] for item in self.validate_intent(target)["requirements"]}
        for index, item in enumerate(criteria):
            item = exact(item, {"id", "requirement_ids", "preconditions", "action", "outcome", "authority", "verification", "evidence"}, f"design.acceptance_criteria[{index}]")
            if not re.fullmatch(r"AC-[0-9]{3}", item["id"]):
                raise ProjectStartError(f"invalid acceptance criterion ID: {item['id']}")
            traced = texts(item["requirement_ids"], f"design.acceptance_criteria[{index}].requirement_ids")
            unknown_requirements = set(traced) - intent_requirement_ids
            if unknown_requirements:
                raise ProjectStartError("acceptance criterion references unknown requirements: " + ", ".join(sorted(unknown_requirements)))
            for field in ("id", "preconditions", "action", "outcome", "authority", "verification", "evidence"):
                text(item[field], f"design.acceptance_criteria[{index}].{field}")
        artifacts = design["artifact_plan"]
        if not isinstance(artifacts, list) or not artifacts:
            raise ProjectStartError("design.artifact_plan must be non-empty")
        artifact_paths: list[str] = []
        for index, item in enumerate(artifacts):
            item = exact(item, {"path", "owner", "purpose"}, f"design.artifact_plan[{index}]")
            artifact_paths.append(relative_file(item["path"], f"design.artifact_plan[{index}].path"))
            text(item["owner"], f"design.artifact_plan[{index}].owner")
            text(item["purpose"], f"design.artifact_plan[{index}].purpose")
        if len(artifact_paths) != len(set(artifact_paths)):
            raise ProjectStartError("artifact paths must be unique")
        missing_required = set(pack["required_artifacts"]) - set(artifact_paths) - set(RENDERED)
        if missing_required:
            raise ProjectStartError("artifact plan omits stack-pack requirements: " + ", ".join(sorted(missing_required)))
        vertical = exact(design["first_vertical_slice"], {"goal", "artifacts", "acceptance_ids"}, "design.first_vertical_slice")
        text(vertical["goal"], "design.first_vertical_slice.goal")
        vertical_artifacts = texts(vertical["artifacts"], "design.first_vertical_slice.artifacts")
        if not set(vertical_artifacts).issubset(set(artifact_paths)):
            raise ProjectStartError("first vertical slice references undeclared artifacts")
        vertical_acceptance = texts(vertical["acceptance_ids"], "design.first_vertical_slice.acceptance_ids")
        if not set(vertical_acceptance).issubset(set(criterion_ids)):
            raise ProjectStartError("first vertical slice references unknown acceptance criteria")
        if design["open_questions"] != []:
            raise ProjectStartError("consequential open questions must be resolved before rendering")
        if design["confidence"] not in {"low", "medium", "high"}:
            raise ProjectStartError("design confidence is invalid")
        return design

    @staticmethod
    def _assert_acyclic(graph: dict[str, list[str]]) -> None:
        visiting: set[str] = set()
        visited: set[str] = set()

        def visit(node: str) -> None:
            if node in visiting:
                raise ProjectStartError("module dependency graph contains a cycle")
            if node in visited:
                return
            visiting.add(node)
            for dependency in graph[node]:
                visit(dependency)
            visiting.remove(node)
            visited.add(node)

        for node in graph:
            visit(node)

    def render(self, target_value: str) -> dict[str, Any]:
        target = self.target(target_value)
        self.verified_intent(target)
        intent = self.validate_intent(target)
        design = self.validate_design(target)
        existing = [name for name in RENDERED if (target / name).exists()]
        if existing:
            raise ProjectStartError("refusing to overwrite rendered files: " + ", ".join(existing))
        product = intent["product"]
        self._write_text(target / "README.md", f"# {design['project_id']}\n\n{product['promise']}\n\nSee `docs/PRODUCT.md`, `docs/ARCHITECTURE.md`, and `docs/ACCEPTANCE.md` before implementation.\n")
        self._write_text(target / "docs" / "PRODUCT.md", self._product_markdown(intent))
        self._write_text(target / "docs" / "ARCHITECTURE.md", self._architecture_markdown(design))
        self._write_text(target / "docs" / "ACCEPTANCE.md", self._acceptance_markdown(design))
        self._write_text(target / "docs" / "decisions" / "ADR-0001-initial-architecture.md", self._decisions_markdown(design))
        self._write_text(target / "AGENTS.md", self._agents_markdown(design))
        pack = self.stack_pack(target)
        write_json(target / "bootstrap-plan.json", {
            "schema_version": 1,
            "project_id": design["project_id"],
            "design_sha256": sha256(target / "project-design.json"),
            "stack_pack": pack["id"],
            "generator": pack["generator"],
            "verification_profile": pack["verification_profile"],
            "artifacts": design["artifact_plan"],
            "first_vertical_slice": design["first_vertical_slice"],
        })
        state = self.state(target)
        state["phase"] = "rendered"
        write_json(target / STATE / "state.json", state)
        return {"status": "rendered", "project_id": design["project_id"], "artifacts": list(RENDERED)}

    @staticmethod
    def _write_text(path: Path, value: str) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(value.rstrip() + "\n", encoding="utf-8")

    @staticmethod
    def _bullets(values: list[str]) -> str:
        return "\n".join(f"- {value}" for value in values) or "- None"

    def _product_markdown(self, intent: dict[str, Any]) -> str:
        product = intent["product"]
        return f"""# Product

## Promise

{product['promise']}

## Primary User

{product['primary_user']}

## Representative Journeys

{self._bullets(product['journeys'])}

## MVP

{self._bullets(product['mvp'])}

## Explicit Exclusions

{self._bullets(product['exclusions'])}

## Constraints

""" + "\n".join(f"- **{key.replace('_', ' ').title()}:** {value}" for key, value in intent["constraints"].items())

    def _architecture_markdown(self, design: dict[str, Any]) -> str:
        selected = design["selected_archetype"]
        modules = "\n".join(f"- **{item['id']}** ({item['runtime']}, owner: {item['owner']}): {item['responsibility']} Dependencies: {', '.join(item['depends_on']) or 'none'}." for item in design["modules"])
        stores = "\n".join(f"- **{item['id']}** (owner: {item['owner']}): {item['purpose']} Schema: {item['schema_strategy']} Migration: {item['migration_strategy']} Sensitivity: {item['sensitivity']}." for item in design["data_stores"]) or "- None"
        interfaces = "\n".join(f"- **{item['id']}** ({item['direction']}, {item['protocol']}, owner: {item['owner']}): validation={item['validation']}; failure={item['failure_behavior']}." for item in design["external_interfaces"]) or "- None"
        security = "\n".join(f"- **{key.replace('_', ' ').title()}:** {value if isinstance(value, str) else '; '.join(value)}" for key, value in design["security_model"].items())
        operations = "\n".join(f"- **{key.replace('_', ' ').title()}:** {value}" for key, value in design["operational_model"].items())
        risks = "\n".join(f"- **{item['id']}** ({item['likelihood']}/{item['impact']}, owner: {item['owner']}): {item['description']} Mitigation: {item['mitigation']}" for item in design["risks"]) or "- None"
        return f"""# Architecture

## Selected Archetype

**{selected['id']}** — {selected['rationale']}

Deviations:

{self._bullets(selected['deviations'])}

## Modules

{modules}

## Data Stores

{stores}

## External Interfaces

{interfaces}

## Security Model

{security}

## Operational Model

{operations}

## Risks

{risks}

## Confidence

{design['confidence']}
"""

    @staticmethod
    def _acceptance_markdown(design: dict[str, Any]) -> str:
        sections = []
        for item in design["acceptance_criteria"]:
            sections.append(f"""## {item['id']}

- **Preconditions:** {item['preconditions']}
- **Requirements:** {', '.join(item['requirement_ids'])}
- **Action:** {item['action']}
- **Observable outcome:** {item['outcome']}
- **Authority:** {item['authority']}
- **Verification:** {item['verification']}
- **Retained evidence:** {item['evidence']}
""")
        return "# Acceptance\n\n" + "\n".join(sections)

    @staticmethod
    def _decisions_markdown(design: dict[str, Any]) -> str:
        sections = []
        for item in design["decisions"]:
            sections.append(f"""## {item['id']}: {item['question']}

- **Selected:** {item['selected']}
- **Alternatives:** {', '.join(item['alternatives']) or 'None'}
- **Evidence:** {', '.join(item['evidence'])}
- **Consequences:** {', '.join(item['consequences'])}
- **Reversal cost:** {item['reversal_cost']}
- **Confidence:** {item['confidence']}
- **Revisit trigger:** {item['revisit_trigger']}
""")
        return "# Initial Architecture Decisions\n\nStatus: Proposed pending review and human approval.\n\n" + "\n".join(sections)

    @staticmethod
    def _agents_markdown(design: dict[str, Any]) -> str:
        modules = "\n".join(f"- `{item['id']}` is owned by `{item['owner']}` and depends only on: {', '.join(item['depends_on']) or 'none'}." for item in design["modules"])
        return f"""# Project Agent Instructions

## Product and Architecture Authority

Read `docs/PRODUCT.md`, `docs/ARCHITECTURE.md`, `docs/ACCEPTANCE.md`, and `bootstrap-plan.json` before editing. Human approval remains authoritative. Do not change the stack pack or architecture decisions implicitly.

## Module Boundaries

{modules}

## Change Rules

- Implement the smallest vertical change that satisfies explicit acceptance criteria.
- Do not add dependencies, deployables, stores, queues, caches, or external services without an approved decision update.
- Preserve trust boundaries, ownership, validation, migration, and failure behavior.
- Never commit credentials or fabricate build, test, security, performance, or runtime evidence.
- Run the stack pack's trusted verification profile and review the resulting diff before declaring completion.
"""

    def materialize_review(self, target_value: str, profile: str) -> dict[str, Any]:
        target = self.target(target_value)
        self.verified_intent(target)
        design = self.validate_design(target)
        missing = [name for name in RENDERED if not (target / name).is_file()]
        if missing:
            raise ProjectStartError("rendered architecture is incomplete: " + ", ".join(missing))
        state = self.state(target)
        task = self.task(
            target,
            task_id=f"{state['project_id']}-architecture-review",
            goal="Independently audit the rendered architecture and return one evidence-based review object.",
            profile=profile,
            capability="review",
            importance="high",
            context=[
                "project-intent.json", "discovery.json", "project-design.json",
                "docs/PRODUCT.md", "docs/ARCHITECTURE.md", "docs/ACCEPTANCE.md",
                "bootstrap-plan.json",
                f"{STATE}/context/agent-definitions/architecture-reviewer.md",
                f"{STATE}/context/templates/review.schema.json",
                f"{STATE}/context/catalog/archetypes.json",
                f"{STATE}/context/stack-packs/{state['stack_pack']}.json",
            ],
            output="architecture-review.json",
            done=["The review is bound to the current project-design.json SHA-256.", "Every finding has evidence and one owner.", "PASS is used only when no blocking or major finding remains."],
            forbidden=["Do not edit or repair project files.", "Do not reuse the architect trajectory, browse, execute commands, or invent test evidence."],
        )
        write_json(target / STATE / "tasks" / "03-architecture-review.task.json", task)
        state["phase"] = "review"
        write_json(target / STATE / "state.json", state)
        return {"status": "materialized", "phase": "review", "task": f"{STATE}/tasks/03-architecture-review.task.json", "design_sha256": sha256(target / "project-design.json")}

    def validate_review(self, target: Path, path: Path | None = None) -> dict[str, Any]:
        source = path or target / "architecture-review.json"
        review = read_json(source)
        exact(review, {"schema_version", "project_id", "design_sha256", "findings", "coverage", "recommendation"}, "review")
        if review["schema_version"] != 1 or review["project_id"] != self.state(target)["project_id"]:
            raise ProjectStartError("review identity is invalid")
        if review["design_sha256"] != sha256(target / "project-design.json"):
            raise ProjectStartError("review is not bound to the current design")
        if review["recommendation"] not in {"PASS", "REVISE", "REJECT"}:
            raise ProjectStartError("review recommendation is invalid")
        if not isinstance(review["findings"], list) or not isinstance(review["coverage"], dict):
            raise ProjectStartError("review findings and coverage have invalid types")
        for criterion_id, status in review["coverage"].items():
            text(criterion_id, "review.coverage key")
            if status not in {"supported", "unsupported", "not_applicable"}:
                raise ProjectStartError(f"invalid review coverage status for {criterion_id}")
        severities = []
        for index, finding in enumerate(review["findings"]):
            finding = exact(finding, {"id", "severity", "category", "description", "evidence", "owner"}, f"review.findings[{index}]")
            if finding["severity"] not in {"blocking", "major", "minor", "info"}:
                raise ProjectStartError("review finding severity is invalid")
            if finding["category"] not in {"requirements", "complexity", "boundaries", "data", "security", "operations", "testing", "traceability"}:
                raise ProjectStartError("review finding category is invalid")
            if finding["owner"] not in {"human", "project-architect", "stack-pack-owner", "root-controller"}:
                raise ProjectStartError("review finding owner is invalid")
            for field in ("id", "category", "description", "evidence", "owner"):
                text(finding[field], f"review.findings[{index}].{field}")
            severities.append(finding["severity"])
        if review["recommendation"] == "PASS" and ({"blocking", "major"} & set(severities)):
            raise ProjectStartError("PASS review cannot contain blocking or major findings")
        return review

    def record_review(self, target_value: str, review_path: str) -> dict[str, Any]:
        target = self.target(target_value)
        source = Path(review_path).resolve()
        review = self.validate_review(target, source)
        if review["recommendation"] != "PASS":
            raise ProjectStartError("architecture review must pass before recording approval evidence")
        destination = target / STATE / "evidence" / "architecture-review.json"
        write_json(target / "architecture-review.json", review)
        write_json(destination, review)
        state = self.state(target)
        state["phase"] = "review-passed"
        write_json(target / STATE / "state.json", state)
        return {"status": "recorded", "path": destination.relative_to(target).as_posix(), "sha256": sha256(destination)}

    def approve(self, target_value: str) -> dict[str, Any]:
        target = self.target(target_value)
        self.verified_intent(target)
        self.validate_design(target)
        review_path = target / STATE / "evidence" / "architecture-review.json"
        review = self.validate_review(target, review_path)
        if review["recommendation"] != "PASS":
            raise ProjectStartError("architecture review has not passed")
        state = self.state(target)
        bound = [
            "project-intent.json", "discovery.json", "project-design.json", "architecture-review.json",
            *RENDERED,
            f"{STATE}/evidence/architecture-review.json",
            f"{STATE}/context/catalog/archetypes.json",
            f"{STATE}/context/stack-packs/{state['stack_pack']}.json",
            f"{STATE}/context/agent-definitions/project-discovery.md",
            f"{STATE}/context/agent-definitions/project-architect.md",
            f"{STATE}/context/agent-definitions/architecture-reviewer.md",
            f"{STATE}/context/templates/discovery.schema.json",
            f"{STATE}/context/templates/project-design.schema.json",
            f"{STATE}/context/templates/review.schema.json",
            f"{STATE}/context/templates/project-intent.schema.json",
            f"{STATE}/context/templates/archetypes.schema.json",
            f"{STATE}/context/templates/stack-pack.schema.json",
        ]
        manifest = {
            "schema_version": 1,
            "project_id": state["project_id"],
            "approved_by": "human-cli",
            "approved_at": datetime.now(timezone.utc).isoformat(),
            "sha256": {name: sha256(target / name) for name in bound},
        }
        write_json(target / STATE / "architecture-approval.json", manifest)
        state["phase"] = "approved"
        write_json(target / STATE / "state.json", state)
        return {"status": "approved", "project_id": state["project_id"], "sha256": manifest["sha256"]}

    def verified_architecture(self, target: Path) -> dict[str, Any]:
        approval = read_json(target / STATE / "architecture-approval.json")
        if not isinstance(approval, dict) or approval.get("schema_version") != 1 or approval.get("project_id") != self.state(target)["project_id"]:
            raise ProjectStartError("architecture approval is invalid")
        hashes = approval.get("sha256")
        if not isinstance(hashes, dict) or not hashes:
            raise ProjectStartError("architecture approval has no bound artifacts")
        stale = [name for name, expected in hashes.items() if not (target / name).is_file() or sha256(target / name) != expected]
        if stale:
            raise ProjectStartError("architecture approval is stale for: " + ", ".join(sorted(stale)))
        return approval

    @staticmethod
    def harness_validate_task(task: Any) -> None:
        if not HARNESS_PATH.is_file():
            raise ProjectStartError("model-execution-harness/core/harness.py is unavailable")
        harness_dir = str(HARNESS_PATH.parent)
        if harness_dir not in sys.path:
            sys.path.insert(0, harness_dir)
        spec = importlib.util.spec_from_file_location("projectstart_harness", HARNESS_PATH)
        if spec is None or spec.loader is None:
            raise ProjectStartError("cannot load the model execution harness")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        try:
            module.validate_task(task)
        except Exception as error:
            raise ProjectStartError(f"model-execution task validation failed: {error}") from error

    def validate(self, target_value: str) -> dict[str, Any]:
        target = self.target(target_value)
        self.validate_intent(target)
        tasks = sorted((target / STATE / "tasks").glob("*.task.json"))
        checked = []
        for path in tasks:
            task = read_json(path)
            self.harness_validate_task(task)
            if task["target"] != self.target_value(target):
                raise ProjectStartError(f"task target mismatch: {path.name}")
            missing = [item["path"] for item in task["context"] if not (target / item["path"]).is_file()]
            if missing:
                raise ProjectStartError(f"task context is missing for {path.name}: {', '.join(missing)}")
            checked.append(task["id"])
        state = self.state(target)
        if state["phase"] == "approved":
            self.verified_architecture(target)
        return {"status": "valid", "project_id": state["project_id"], "phase": state["phase"], "tasks": checked}


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(description=__doc__)
    commands = root.add_subparsers(dest="command", required=True)
    initialize = commands.add_parser("init")
    initialize.add_argument("--target", required=True)
    initialize.add_argument("--id", required=True)
    initialize.add_argument("--stack-pack", default="generic-software-v1")
    for name in ("accept-discovery", "render", "approve", "validate"):
        command = commands.add_parser(name)
        command.add_argument("--target", required=True)
    for name in ("prepare-discovery", "materialize-architecture", "materialize-review"):
        command = commands.add_parser(name)
        command.add_argument("--target", required=True)
        command.add_argument("--profile", required=True)
    record = commands.add_parser("record-review")
    record.add_argument("--target", required=True)
    record.add_argument("--review", required=True)
    return root


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    manager = ProjectStartManager()
    try:
        if args.command == "init":
            result = manager.init(args.target, args.id, args.stack_pack)
        elif args.command == "prepare-discovery":
            result = manager.prepare_discovery(args.target, args.profile)
        elif args.command == "accept-discovery":
            result = manager.accept_discovery(args.target)
        elif args.command == "materialize-architecture":
            result = manager.materialize_architecture(args.target, args.profile)
        elif args.command == "render":
            result = manager.render(args.target)
        elif args.command == "materialize-review":
            result = manager.materialize_review(args.target, args.profile)
        elif args.command == "record-review":
            result = manager.record_review(args.target, args.review)
        elif args.command == "approve":
            result = manager.approve(args.target)
        else:
            result = manager.validate(args.target)
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return 0
    except ProjectStartError as error:
        print(json.dumps({"status": "error", "error": str(error)}, indent=2, ensure_ascii=False))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
