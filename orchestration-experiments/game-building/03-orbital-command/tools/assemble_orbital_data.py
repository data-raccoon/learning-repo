"""Validate Orbital Command design artifacts and assemble the runtime data interface."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1] / "orbital-command"
DATA = ROOT / "data"


def load(name: str) -> object:
    return json.loads((DATA / name).read_text(encoding="utf-8"))


def require(condition: bool, code: str) -> None:
    if not condition:
        raise SystemExit("FAILED " + code)


def main() -> None:
    world, economy, technology, events, copy = (
        load("world.json"), load("economy.json"), load("technology.json"),
        load("events.json"), load("copy.json"),
    )
    require(isinstance(world, dict), "WORLD_OBJECT")
    require(set(world.get("starting_resources", {})) == {"energy", "alloys", "science", "credits", "morale"}, "WORLD_RESOURCES")
    require([role.get("id") for role in world.get("roles", [])] == ["engineering", "science", "operations"], "WORLD_ROLES")
    require(len(world.get("mission_goals", [])) == 3, "WORLD_GOALS")
    expected_modules = ["solar-array", "refinery", "research-lab", "trade-dock", "habitat-ring", "fusion-core", "quantum-lab", "observatory"]
    require(isinstance(economy, list) and [item.get("id") for item in economy] == expected_modules, "ECONOMY_MODULES")
    expected_tech = ["efficient-routing", "fusion-grid", "diplomatic-protocols", "deep-scan", "quantum-computing", "closed-loop-life-support"]
    require(isinstance(technology, list) and [item.get("id") for item in technology] == expected_tech, "TECHNOLOGY_IDS")
    require(isinstance(events, list) and len(events) >= 12, "EVENT_COUNT")
    require(all(len(event.get("choices", [])) == 2 for event in events), "EVENT_CHOICES")
    required_copy = {"title", "subtitle", "new_game", "continue_game", "advance_turn", "build_heading", "research_heading", "crew_heading", "mission_heading", "log_heading", "resources_heading", "event_heading", "save_notice", "loss_message", "victory_message", "reset_game", "help_text"}
    require(isinstance(copy, dict) and required_copy.issubset(copy), "COPY_KEYS")
    runtime_events = events[:12]
    content = {"world": world, "modules": economy, "technologies": technology, "events": runtime_events, "copy": copy}
    encoded = json.dumps(content, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    (DATA / "content.js").write_text("window.OC_DATA=" + encoded + ";\n", encoding="utf-8")
    print(f"PASS schemas=5 modules={len(economy)} technologies={len(technology)} events={len(runtime_events)} normalized_extra_events={len(events)-len(runtime_events)}")


if __name__ == "__main__":
    main()
