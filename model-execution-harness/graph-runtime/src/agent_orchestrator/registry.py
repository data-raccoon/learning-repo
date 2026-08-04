"""Load versioned TOML registries and inspect runtime availability."""

from __future__ import annotations

from dataclasses import asdict
import os
from pathlib import Path
import shutil
import tomllib
from typing import Any

from .contracts import Harness, Model, ModelProfile, Provider


class RegistryError(ValueError):
    pass


class Registry:
    def __init__(self, config_dir: Path):
        self.config_dir = config_dir
        self.providers = self._load("providers.toml", "providers", Provider)
        self.models = self._load("models.toml", "models", Model, tuple_fields={"modalities", "capabilities"})
        self.harnesses = self._load("harnesses.toml", "harnesses", Harness)
        self.profiles = self._load("profiles.toml", "profiles", ModelProfile, tuple_fields={"capabilities"})
        self._validate_links()

    def _load(self, filename: str, key: str, cls: type, tuple_fields: set[str] | None = None) -> dict[str, Any]:
        path = self.config_dir / filename
        try:
            rows = tomllib.loads(path.read_text(encoding="utf-8")).get(key, [])
        except (OSError, tomllib.TOMLDecodeError) as error:
            raise RegistryError(f"cannot load {path}: {error}") from error
        result = {}
        for row in rows:
            values = dict(row)
            for field_name in tuple_fields or set():
                values[field_name] = tuple(values.get(field_name, []))
            item = cls(**values)
            if item.id in result:
                raise RegistryError(f"duplicate {key} id: {item.id}")
            result[item.id] = item
        return result

    def _validate_links(self) -> None:
        for provider in self.providers.values():
            if provider.usage_reporting not in {"measured", "unavailable"}:
                raise RegistryError(f"provider {provider.id} has invalid usage_reporting")
        for model in self.models.values():
            if model.provider not in self.providers:
                raise RegistryError(f"model {model.id} references unknown provider {model.provider}")
        for harness in self.harnesses.values():
            if harness.provider not in self.providers:
                raise RegistryError(f"harness {harness.id} references unknown provider {harness.provider}")
        for profile in self.profiles.values():
            if profile.model not in self.models or profile.harness not in self.harnesses:
                raise RegistryError(f"profile {profile.id} has an unknown model or harness")

    @staticmethod
    def _env_file_has(path: Path, key: str) -> bool:
        if not path.is_file():
            return False
        try:
            return any(line.split("=", 1)[0].strip() == key for line in path.read_text(encoding="utf-8").splitlines() if "=" in line)
        except OSError:
            return False

    def provider_availability(self, provider: Provider) -> tuple[str, str]:
        if provider.status == "deferred":
            return "unavailable", "provider adapter is deferred by milestone policy"
        if provider.executable and not shutil.which(provider.executable):
            if provider.executable == "agy" and os.environ.get("LOCALAPPDATA"):
                installed = Path(os.environ["LOCALAPPDATA"]) / "agy" / "bin" / "agy.exe"
                if installed.is_file():
                    return "available", "Antigravity CLI is installed in the external per-user application directory"
            return "unavailable", f"missing executable: {provider.executable}"
        if provider.auth_env:
            if os.environ.get(provider.auth_env):
                return "available", f"credential found in {provider.auth_env}"
            home = Path.home()
            if provider.id.startswith("mistral") and self._env_file_has(home / ".vibe" / ".env", provider.auth_env):
                return "available", "credential is configured in the external Vibe environment"
            if provider.id == "local-ministral" and Path(r"C:\LLMs\config\api_key.txt").is_file():
                if Path(r"C:\LLMs\models\mistral\Ministral-3-3B-Instruct-2512-Q4_K_M.gguf").is_file():
                    return "available", "external local credential and model are present"
            if provider.id == "local-colibri" and Path(r"C:\LLMs\config\colibri_api_key.txt").is_file():
                model_dir = Path(r"C:\LLMs\models\colibri")
                if model_dir.is_dir() and (model_dir / "config.json").is_file():
                    return "available", "external local credential and model are present"
            return "unavailable", f"credential {provider.auth_env} is not configured"
        if provider.auth_kind == "google-account-oauth":
            return "available", "CLI is present; the external OS-keyring account session is verified when a job runs"
        return "available", "no credential required"

    def inventory(self) -> dict[str, Any]:
        providers = []
        for provider in self.providers.values():
            availability, reason = self.provider_availability(provider)
            providers.append({**asdict(provider), "availability": availability, "availability_reason": reason})
        return {
            "providers": providers,
            "models": [asdict(item) for item in self.models.values()],
            "harnesses": [asdict(item) for item in self.harnesses.values()],
            "profiles": [asdict(item) for item in self.profiles.values()],
        }
