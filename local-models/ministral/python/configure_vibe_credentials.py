"""Register the local llama.cpp API key for Mistral Vibe.

The model/provider configuration remains project-local in .vibe/config.toml.
Vibe loads secrets from %USERPROFILE%/.vibe/.env.
"""

from pathlib import Path


KEY_NAME = "LOCAL_LLM_API_KEY"
SOURCE = Path(r"C:\LLMs\config\api_key.txt")
TARGET = Path.home() / ".vibe" / ".env"


def main() -> None:
    api_key = SOURCE.read_text(encoding="utf-8").strip()
    if not api_key:
        raise RuntimeError(f"API key file is empty: {SOURCE}")

    existing = TARGET.read_text(encoding="utf-8").splitlines() if TARGET.exists() else []
    replacement = f"{KEY_NAME}={api_key}"
    updated: list[str] = []
    replaced = False

    for line in existing:
        if line.startswith(f"{KEY_NAME}="):
            if not replaced:
                updated.append(replacement)
                replaced = True
        else:
            updated.append(line)

    if not replaced:
        updated.append(replacement)

    TARGET.parent.mkdir(parents=True, exist_ok=True)
    TARGET.write_text("\n".join(updated) + "\n", encoding="utf-8")
    print(f"Configured {KEY_NAME} in {TARGET}")


if __name__ == "__main__":
    main()
