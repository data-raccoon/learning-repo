from pathlib import Path
import shutil
import subprocess
import tempfile


ROOT = Path(__file__).resolve().parents[2]
SOURCES = [
    ROOT / "src/main/java/com/manacore/core/storage/ChunkManaMap.java",
    ROOT / "src/main/java/com/manacore/core/storage/ManaCoordinates.java",
    ROOT / "src/main/java/com/manacore/core/ManaMath.java",
    ROOT / "src/test/java/com/manacore/core/storage/ChunkManaMapTest.java",
]


def main() -> int:
    javac = shutil.which("javac")
    java = shutil.which("java")
    if not javac or not java or any(not source.is_file() for source in SOURCES):
        return 1
    with tempfile.TemporaryDirectory(prefix="mana-core-storage-test-") as output:
        compiled = subprocess.run(
            [javac, "-encoding", "UTF-8", "-d", output, *map(str, SOURCES)],
            cwd=ROOT,
            timeout=90,
            check=False,
        )
        if compiled.returncode:
            return compiled.returncode
        tested = subprocess.run(
            [java, "-ea", "-cp", output, "com.manacore.core.storage.ChunkManaMapTest"],
            cwd=ROOT,
            timeout=30,
            check=False,
        )
        return tested.returncode


if __name__ == "__main__":
    raise SystemExit(main())
