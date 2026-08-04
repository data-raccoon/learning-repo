from pathlib import Path
import shutil
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[2]
SOURCES = [
    ROOT / "src/main/java/com/manacore/core/storage/ManaCoordinates.java",
    ROOT / "src/main/java/com/manacore/core/storage/ChunkManaMap.java",
    ROOT / "src/main/java/com/manacore/core/flow/GradientCalculator.java",
    ROOT / "src/main/java/com/manacore/core/flow/FlowEngine.java",
    ROOT / "src/main/java/com/manacore/core/gather/SphericalGatherer.java",
    ROOT / "src/main/java/com/manacore/core/config/ManaConfig.java",
    ROOT / "src/main/java/com/manacore/core/api/ManaAPI.java",
    ROOT / "src/test/java/com/manacore/core/api/ManaAPITest.java",
    ROOT / ".mc-mod-agents/tools/contracts/ManaApiFacadeContract.java",
]


def main() -> int:
    javac, java = shutil.which("javac"), shutil.which("java")
    if not javac or not java or any(not path.is_file() for path in SOURCES):
        return 1
    api_text = SOURCES[6].read_text(encoding="utf-8")
    if "net.minecraft" in api_text or "net.fabricmc" in api_text:
        return 1
    with tempfile.TemporaryDirectory(prefix="mana-api-facade-") as output:
        compiled = subprocess.run(
            [javac, "-encoding", "UTF-8", "-d", output, *map(str, SOURCES)],
            cwd=ROOT,
            timeout=90,
            check=False,
        )
        if compiled.returncode:
            return compiled.returncode
        for name in (
            "com.manacore.core.api.ManaAPITest",
            "com.manacore.core.api.ManaApiFacadeContract",
        ):
            tested = subprocess.run(
                [java, "-ea", "-cp", output, name],
                cwd=ROOT,
                timeout=30,
                check=False,
            )
            if tested.returncode:
                return tested.returncode
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
