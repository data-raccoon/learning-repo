from pathlib import Path
import shutil
import subprocess
import tempfile


ROOT = Path(__file__).resolve().parents[2]
SOURCES = [
    ROOT / "src/main/java/com/manacore/core/storage/ChunkManaMap.java",
    ROOT / "src/main/java/com/manacore/core/storage/ManaCoordinates.java",
    ROOT / "src/main/java/com/manacore/core/ManaMath.java",
    ROOT / "src/main/java/com/manacore/core/flow/GradientCalculator.java",
    ROOT / "src/test/java/com/manacore/core/flow/GradientCalculatorTest.java",
    ROOT / ".mc-mod-agents/tools/contracts/GradientCalculatorContract.java",
]


def main() -> int:
    javac = shutil.which("javac")
    java = shutil.which("java")
    if not javac or not java or any(not source.is_file() for source in SOURCES):
        return 1
    with tempfile.TemporaryDirectory(prefix="mana-core-gradient-test-") as output:
        compiled = subprocess.run(
            [javac, "-encoding", "UTF-8", "-d", output, *map(str, SOURCES)],
            cwd=ROOT,
            timeout=90,
            check=False,
        )
        if compiled.returncode:
            return compiled.returncode
        for test_class in (
            "com.manacore.core.flow.GradientCalculatorTest",
            "com.manacore.core.flow.GradientCalculatorContract",
        ):
            tested = subprocess.run(
                [java, "-ea", "-cp", output, test_class],
                cwd=ROOT,
                timeout=30,
                check=False,
            )
            if tested.returncode:
                return tested.returncode
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
