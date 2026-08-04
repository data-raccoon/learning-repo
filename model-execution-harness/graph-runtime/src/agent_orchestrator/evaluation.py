"""Capability-profile audit and live candidate evidence."""

from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any

from .contracts import Job
from .registry import Registry
from .runner import JobRunner


EVAL_DIMENSIONS = (
    "architecture", "planning", "coding", "review", "extraction", "classification",
    "summarization", "file-editing", "tool-use", "multimodal",
)


def audit_profiles(registry: Registry) -> dict[str, Any]:
    rows = []
    for profile in registry.profiles.values():
        model = registry.models[profile.model]
        provider = registry.providers[model.provider]
        availability, reason = registry.provider_availability(provider)
        rows.append({
            "profile": profile.id,
            "status": profile.status,
            "availability": availability,
            "availability_reason": reason,
            "success_probability": profile.success_probability,
            "benchmark_version": profile.benchmark_version,
            "capabilities": {name: name in profile.capabilities for name in EVAL_DIMENSIONS},
        })
    return {"benchmark_contract": "capability-audit-v1", "profiles": rows}


def run_candidate(runner: JobRunner, job: Job, destination: Path) -> dict[str, Any]:
    if not job.model_profile:
        raise ValueError("candidate evaluation requires an explicit model_profile")
    profile = runner.registry.profiles.get(job.model_profile)
    if profile is None or profile.status != "candidate":
        raise ValueError("candidate evaluation requires an explicit candidate profile")
    result = runner.run(job, allow_candidate=True)
    candidate = {
        "kind": "model-profile-candidate",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "job": job.id,
        "run": result,
        "promotion": "not-promoted",
        "note": "A live result is evidence only; profile promotion requires independent review.",
    }
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(candidate, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return candidate
