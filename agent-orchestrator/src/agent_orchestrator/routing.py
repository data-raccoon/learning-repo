"""Capability-first routing with explicit explanations."""

from __future__ import annotations

from dataclasses import asdict
from typing import Any

from .contracts import IMPORTANCE_THRESHOLDS, Job, ModelProfile
from .registry import Registry


TOOL_RANK = {"inference": 0, "files_read": 1, "files_write": 2, "commands": 3}


class RoutingError(RuntimeError):
    pass


def _marginal_cost_key(registry: Registry, profile: ModelProfile) -> tuple[float, float]:
    model = registry.models[profile.model]
    billing = registry.providers[model.provider].billing
    if billing in {"free-account-quota", "included-subscription"}:
        return (0.0, 0.0)
    if billing == "metered-api":
        input_cost = model.input_cost_per_million
        output_cost = model.output_cost_per_million
        if input_cost is not None and output_cost is not None and input_cost >= 0 and output_cost >= 0:
            return (input_cost, output_cost)
    return (float("inf"), float("inf"))


def _supports_tool(profile: ModelProfile, requested: str) -> bool:
    if requested == "files_read":
        return profile.tool_class in {"files_read", "files_write", "commands"}
    return profile.tool_class == requested or (
        requested == "files_write" and profile.tool_class == "commands"
    )


def route_job(registry: Registry, job: Job, *, allow_candidate: bool = False) -> dict[str, Any]:
    considered: list[dict[str, Any]] = []
    eligible: list[ModelProfile] = []
    for profile in registry.profiles.values():
        reasons: list[str] = []
        model = registry.models[profile.model]
        provider = registry.providers[model.provider]
        harness = registry.harnesses[profile.harness]
        availability, availability_reason = registry.provider_availability(provider)
        candidate_eval = allow_candidate and bool(job.model_profile) and profile.id == job.model_profile and profile.status == "candidate"
        if profile.status != "eligible" and not candidate_eval:
            reasons.append(f"profile status is {profile.status}")
        if availability != "available":
            reasons.append(availability_reason)
        if harness.status != "eligible" and not (candidate_eval and harness.status == "candidate"):
            reasons.append(f"harness status is {harness.status}")
        if not set(job.required_capabilities).issubset(profile.capabilities):
            missing = sorted(set(job.required_capabilities) - set(profile.capabilities))
            reasons.append("missing capabilities: " + ", ".join(missing))
        if not _supports_tool(profile, job.tool_class):
            reasons.append(f"tool class {profile.tool_class} cannot satisfy {job.tool_class}")
        if job.mode == "write" and profile.tool_class not in {"files_write", "commands"}:
            reasons.append("write job requires a write-capable profile")
        if job.risk in {"high", "critical"} and profile.benchmark_version == "unbenchmarked":
            reasons.append("unbenchmarked profiles cannot accept high-risk work")
        if job.model_profile and job.model_profile != profile.id:
            reasons.append("different from explicit profile override")
        accepted = not reasons
        considered.append({"profile": profile.id, "accepted": accepted, "reasons": reasons})
        if accepted:
            eligible.append(profile)
    if not eligible:
        raise RoutingError("no eligible profile", considered)
    if allow_candidate:
        selected = eligible[0]
        strategy = "explicit candidate profile for isolated evaluation"
    elif job.importance == "critical" or any(cap in {"architecture", "planning"} for cap in job.required_capabilities):
        selected = max(eligible, key=lambda item: registry.models[item.model].quality)
        strategy = "strongest eligible profile for critical planning or architecture"
    else:
        threshold = IMPORTANCE_THRESHOLDS[job.importance]
        passing = [item for item in eligible if item.success_probability >= threshold]
        if not passing:
            raise RoutingError(f"no eligible profile reaches success threshold {threshold}", considered)
        selected = min(
            passing,
            key=lambda item: (
                registry.models[item.model].quality,
                *_marginal_cost_key(registry, item),
            ),
        )
        strategy = f"weakest eligible profile meeting {threshold:.2f} success threshold"
    model = registry.models[selected.model]
    provider = registry.providers[model.provider]
    harness = registry.harnesses[selected.harness]
    return {
        "selected_profile": selected.id,
        "model": model.id,
        "remote_model": model.remote_id,
        "provider": model.provider,
        "billing": provider.billing,
        "plan": provider.plan,
        "harness": harness.id,
        "strategy": strategy,
        "expected_success": selected.success_probability,
        "considered": considered,
    }
