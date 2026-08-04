from pathlib import Path
import shutil
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[2]
SOURCES = [
    ROOT / "src/main/java/com/manacore/core/api/events/ManaFlowEvent.java",
    ROOT / "src/main/java/com/manacore/core/api/events/ManaGatherEvent.java",
    ROOT / "src/main/java/com/manacore/core/api/events/ManaStoreEvent.java",
    ROOT / "src/test/java/com/manacore/core/api/events/ManaEventsTest.java",
    ROOT / ".mc-mod-agents/tools/contracts/ManaEventsContract.java",
]

def main() -> int:
    javac, java = shutil.which("javac"), shutil.which("java")
    if not javac or not java or any(not path.is_file() for path in SOURCES):
        return 1
    if any("net.minecraft" in path.read_text(encoding="utf-8") or "net.fabricmc" in path.read_text(encoding="utf-8") for path in SOURCES[:3]):
        return 1
    with tempfile.TemporaryDirectory(prefix="mana-api-events-") as output:
        compiled = subprocess.run([javac, "-encoding", "UTF-8", "-d", output, *map(str, SOURCES)], cwd=ROOT, timeout=90, check=False)
        if compiled.returncode:
            return compiled.returncode
        for name in ("com.manacore.core.api.events.ManaEventsTest", "com.manacore.core.api.events.ManaEventsContract"):
            tested = subprocess.run([java, "-ea", "-cp", output, name], cwd=ROOT, timeout=30, check=False)
            if tested.returncode:
                return tested.returncode
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
