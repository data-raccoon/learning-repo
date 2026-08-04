import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PINS = {
    "minecraft_version": "26.2",
    "fabric_loader_version": "0.19.3",
    "fabric_api_version": "0.154.2+26.2",
    "fabric_loom_version": "1.17-SNAPSHOT",
    "gradle_version": "9.5.1",
    "java_version": "25",
}


def main() -> int:
    documents = [ROOT / "docs" / name for name in ("PRODUCT.md", "ARCHITECTURE.md", "ACCEPTANCE.md")]
    spec_path = ROOT / "mod-spec.json"
    if any(not path.is_file() or len(path.read_text(encoding="utf-8").strip()) < 80 for path in documents):
        return 1
    try:
        spec = json.loads(spec_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError):
        return 1
    if spec.get("engine") != "Fabric" or any(str(spec.get(key)) != value for key, value in PINS.items()):
        return 1
    if spec.get("verifiers") != ["compile-common", "compile-client", "unit-tests", "build"]:
        return 1
    for key in ("creative_artifacts", "engineer_artifacts"):
        values = spec.get(key)
        if not isinstance(values, list) or not values or len(values) != len(set(values)):
            return 1
        if any(not isinstance(value, str) or value.endswith("/") for value in values):
            return 1
    print(json.dumps({"status": "passed", "documents": 3, "mod_id": spec.get("mod_id")}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
