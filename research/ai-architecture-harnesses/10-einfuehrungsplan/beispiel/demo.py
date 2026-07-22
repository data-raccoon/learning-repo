"""Create self-contained evidence and demonstrate CANARY, PROMOTE, and ROLLBACK."""

from __future__ import annotations

import json
import tempfile
from datetime import datetime, timezone
from pathlib import Path

from release_gate import POLICY_VERSION, STOP_SIGNALS, ReleaseGate, sha256_file


def build_manifest(root: Path, phase: str = "pre_canary") -> dict:
    now = datetime.now(timezone.utc).isoformat()
    evidence_ids = (
        "use_case", "owner", "baseline_eval", "data_classification", "risk_acceptance",
        "contract_tests", "log_secret_review", "offline_eval", "canary_report", "kill_switch_drill",
    )
    evidence = []
    for evidence_id in evidence_ids:
        path = root / f"{evidence_id}.txt"
        path.write_text(f"PASS: reproducible demo evidence for {evidence_id}\n", encoding="utf-8")
        evidence.append({"id": evidence_id, "path": path.name, "sha256": sha256_file(path), "status": "pass", "collected_at": now, "max_age_hours": 24})
    values = {
        "baseline_task_success": (0.70, 0.65, None),
        "task_success": (0.91, 0.85, None),
        "error_rate": (0.01, None, 0.02),
        "p95_latency_ms": (850, None, 1000),
        "cost_per_request": (0.03, None, 0.05),
        "safety_detection_rate": (0.99, 0.98, None),
    }
    metrics = [{"id": key, "value": value, "min": minimum, "max": maximum, "measured_at": now, "max_age_hours": 24} for key, (value, minimum, maximum) in values.items()]
    return {
        "manifest_version": 1,
        "gate_policy_version": POLICY_VERSION,
        "release_id": "assistant-readonly-1.2.0",
        "created_at": now,
        "target_stage": 1,
        "artifacts": {"code": "git:abc123", "prompt": "sha256:prompt", "policy": "git:policy1", "schema": "v3", "eval_dataset": "eval:v5", "model": "provider:model-snapshot"},
        "evidence": evidence,
        "metrics": metrics,
        "stop_signals": {name: False for name in STOP_SIGNALS},
        "rollout": {"phase": phase, "current_stage": 0, "rollback_stage": 0, "traffic_percent": 5, "min_observation_hours": 12, "observed_hours": 0 if phase == "pre_canary" else 12, "min_samples": 500, "samples": 0 if phase == "pre_canary" else 700},
    }


def main() -> None:
    with tempfile.TemporaryDirectory(prefix="release-gate-demo-") as temporary:
        root = Path(temporary)
        manifest = build_manifest(root)
        gate = ReleaseGate()
        print("PRE-CANARY:", gate.evaluate(manifest, root).decision.value)
        manifest["rollout"].update({"phase": "canary", "observed_hours": 12, "samples": 700})
        print("CANARY COMPLETE:", gate.evaluate(manifest, root).decision.value)
        manifest["stop_signals"]["policy_enforcer_bypass"] = True
        result = gate.evaluate(manifest, root)
        print("STOP SIGNAL:", result.decision.value, "to stage", result.rollback_stage)


if __name__ == "__main__":
    main()
