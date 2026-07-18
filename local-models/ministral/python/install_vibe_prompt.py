"""Install the project-maintained minimal prompt into Vibe's prompt directory."""

from pathlib import Path
import shutil


SOURCE = Path(__file__).resolve().parents[1] / ".vibe" / "prompts" / "local-files.md"
TARGET = Path.home() / ".vibe" / "prompts" / SOURCE.name


def main() -> None:
    TARGET.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(SOURCE, TARGET)
    print(f"Installed {TARGET} ({TARGET.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
