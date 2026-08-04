from pathlib import Path
import shutil
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[2]
SOURCES = [
    ROOT / "src/main/java/com/manacore/core/config/ManaConfig.java",
    ROOT / "src/test/java/com/manacore/core/config/ManaConfigTest.java",
    ROOT / ".mc-mod-agents/tools/contracts/ManaConfigContract.java",
]

def main() -> int:
    javac, java = shutil.which("javac"), shutil.which("java")
    if not javac or not java or any(not path.is_file() for path in SOURCES):
        return 1
    if "net.minecraft" in SOURCES[0].read_text(encoding="utf-8") or "net.fabricmc" in SOURCES[0].read_text(encoding="utf-8"):
        return 1
    with tempfile.TemporaryDirectory(prefix="mana-config-") as output:
        compiled = subprocess.run([javac, "-encoding", "UTF-8", "-d", output, *map(str, SOURCES)], cwd=ROOT, timeout=90, check=False)
        if compiled.returncode:
            return compiled.returncode
        for name in ("com.manacore.core.config.ManaConfigTest", "com.manacore.core.config.ManaConfigContract"):
            tested = subprocess.run([java, "-ea", "-cp", output, name], cwd=ROOT, timeout=30, check=False)
            if tested.returncode:
                return tested.returncode
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
