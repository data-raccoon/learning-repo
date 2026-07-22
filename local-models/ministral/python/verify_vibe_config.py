"""Validate the project-local Vibe config and authenticated local model endpoint."""

from __future__ import annotations

import json
import tomllib
import urllib.error
import urllib.request
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = PROJECT_ROOT / ".vibe" / "config.toml"
AGENT_PATH = PROJECT_ROOT / ".vibe" / "agents" / "local-files.toml"
API_KEY_PATH = Path(r"C:\LLMs\config\api_key.txt")


def main() -> None:
    config = tomllib.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    agent = tomllib.loads(AGENT_PATH.read_text(encoding="utf-8"))
    providers = {item["name"]: item for item in config.get("providers", [])}
    models = {item["alias"]: item for item in config.get("models", [])}

    provider = providers.get("local-llama")
    model = models.get("local-ministral-3b-q4")
    if not provider or not model:
        raise SystemExit("Project-local provider or model entry is missing.")
    if provider.get("api_base") != "http://127.0.0.1:8081/v1":
        raise SystemExit("The provider must remain bound to the loopback endpoint.")
    if provider.get("api_key_env_var") != "LOCAL_LLM_API_KEY":
        raise SystemExit("Unexpected API-key environment variable.")
    if model.get("name") != "ministral-3b-q4" or model.get("provider") != "local-llama":
        raise SystemExit("Unexpected local model mapping.")
    active_model = config.get("active_model")
    configured_aliases = {item.get("alias") for item in config.get("models", [])}
    if active_model not in configured_aliases:
        raise SystemExit(f"The active model is not configured: {active_model}")

    required_tools = {"read_file", "grep", "edit", "write_file", "web_search", "web_fetch"}
    enabled_tools = set(agent.get("enabled_tools", []))
    if not required_tools.issubset(enabled_tools):
        raise SystemExit(f"Local agent is missing tools: {sorted(required_tools - enabled_tools)}")
    for tool in ("edit", "write_file", "web_search", "web_fetch"):
        if agent.get("tools", {}).get(tool, {}).get("permission") != "always":
            raise SystemExit(f"Local agent tool must be always available: {tool}")
    key = API_KEY_PATH.read_text(encoding="ascii").strip()
    request = urllib.request.Request(
        provider["api_base"] + "/models",
        headers={"Authorization": f"Bearer {key}"},
    )
    try:
        with urllib.request.urlopen(request, timeout=10) as response:
            endpoint = json.load(response)
    except urllib.error.URLError as error:
        raise SystemExit(f"Local model endpoint is unavailable: {error}") from error

    model_ids = [item.get("id") for item in endpoint.get("data", [])]
    if "ministral-3b-q4" not in model_ids:
        raise SystemExit(f"Expected model alias not returned by endpoint: {model_ids}")

    print(
        json.dumps(
            {
                "config": str(CONFIG_PATH),
                "provider": provider["name"],
                "model_alias": model["alias"],
                "endpoint_model_ids": model_ids,
                "ready": True,
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
