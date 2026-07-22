"""Fail-closed evidence gate for staged AI releases (standard library only).

This module makes decisions and emits plans.  It deliberately has no deployment,
network, credential, or subprocess capability.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any


MANIFEST_VERSION = 1
POLICY_VERSION = "2026-07-22.1"
MAX_CLOCK_SKEW_SECONDS = 300

# Requirements are cumulative: a stage-3 candidate must retain evidence for 0..3.
STAGE_EVIDENCE: dict[int, tuple[str, ...]] = {
    0: ("use_case", "owner", "baseline_eval", "data_classification", "risk_acceptance"),
    1: ("contract_tests", "log_secret_review", "offline_eval", "canary_report", "kill_switch_drill"),
    2: ("transition_coverage", "capability_negative_tests", "egress_iam_review", "budget_tests", "injection_eval", "trace_review"),
    3: ("authorization_tests", "credential_separation", "duplicate_delivery_tests", "commit_crash_tests", "approval_tamper_test", "reconciliation_drill", "security_signoff"),
    4: ("worker_kill_tests", "backup_restore", "history_replay", "activity_idempotency", "provider_chaos_test"),
    5: ("paired_baseline_eval", "benefit_confidence", "safety_slice_eval", "loop_stress_test", "handoff_provenance_tests", "worker_cancel_test"),
    6: ("checked_invariants", "runtime_conformance", "isolation_tests", "artifact_attestation", "break_glass_test", "independent_signoff", "recovery_drill"),
}

STAGE_METRICS: dict[int, tuple[str, ...]] = {
    0: ("baseline_task_success",),
    1: ("task_success", "error_rate", "p95_latency_ms", "cost_per_request", "safety_detection_rate"),
    2: ("unauthorized_tool_calls", "budget_overruns", "prompt_injection_block_rate"),
    3: ("unauthorized_side_effects", "ambiguous_commits", "reconciliation_backlog"),
    4: ("replay_failures", "recovery_success_rate"),
    5: ("quality_lift", "critical_safety_regression", "orchestration_budget_overruns"),
    6: ("invariant_violations", "isolation_failures", "error_budget_burn_rate"),
}

STOP_SIGNALS = (
    "unauthorized_side_effect",
    "audit_correlation_missing",
    "error_budget_exceeded",
    "critical_safety_regression",
    "ambiguous_duplicate_effect",
    "secret_or_forbidden_data_exposed",
    "replay_incompatible",
    "policy_enforcer_bypass",
)


class Decision(str, Enum):
    CANARY = "CANARY"
    PROMOTE = "PROMOTE"
    HOLD = "HOLD"
    ROLLBACK = "ROLLBACK"


@dataclass(frozen=True)
class Finding:
    code: str
    message: str


@dataclass
class GateResult:
    decision: Decision
    release_id: str
    target_stage: int | None
    rollback_stage: int | None
    findings: list[Finding] = field(default_factory=list)
    next_actions: list[str] = field(default_factory=list)
    evaluated_at: str = ""
    policy_version: str = POLICY_VERSION

    def to_dict(self) -> dict[str, Any]:
        value = asdict(self)
        value["decision"] = self.decision.value
        return value


def canonical_json(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def parse_time(value: Any) -> datetime:
    if not isinstance(value, str):
        raise ValueError("timestamp is not a string")
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        raise ValueError("timestamp lacks timezone")
    return parsed.astimezone(timezone.utc)


def requirements_through(stage: int, source: dict[int, tuple[str, ...]]) -> set[str]:
    return {item for level in range(stage + 1) for item in source[level]}


class ReleaseGate:
    """Evaluate one immutable release manifest against the built-in gate policy."""

    def __init__(self, now: datetime | None = None) -> None:
        self.now = (now or datetime.now(timezone.utc)).astimezone(timezone.utc)

    def evaluate_path(self, manifest_path: Path) -> GateResult:
        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        except (OSError, UnicodeError, json.JSONDecodeError) as exc:
            return self._result({}, Decision.HOLD, [Finding("manifest_unreadable", str(exc))])
        return self.evaluate(manifest, manifest_path.resolve().parent)

    def evaluate(self, manifest: Any, base_dir: Path) -> GateResult:
        findings: list[Finding] = []
        if not isinstance(manifest, dict):
            return self._result({}, Decision.HOLD, [Finding("manifest_invalid", "root must be an object")])

        stage = manifest.get("target_stage")
        if not isinstance(stage, int) or isinstance(stage, bool) or stage not in STAGE_EVIDENCE:
            findings.append(Finding("stage_invalid", "target_stage must be an integer from 0 through 6"))
            stage = None
        self._validate_header(manifest, findings)
        self._validate_artifacts(manifest.get("artifacts"), findings)
        if stage is not None:
            self._validate_evidence(manifest.get("evidence"), stage, base_dir, findings)
            self._validate_metrics(manifest.get("metrics"), stage, findings)

        active_stops = self._validate_stop_signals(manifest.get("stop_signals"), findings)
        rollout = self._validate_rollout(manifest.get("rollout"), stage, findings)

        rollback_stage = rollout.get("rollback_stage") if rollout else None
        if active_stops:
            stop_findings = [Finding("stop_triggered", name) for name in active_stops]
            return self._result(
                manifest,
                Decision.ROLLBACK,
                stop_findings + findings,
                rollback_stage,
                [f"Route new traffic to stage {rollback_stage}.", "Freeze the candidate and open an incident; reconcile side effects before retrying."],
            )
        if findings:
            return self._result(
                manifest,
                Decision.HOLD,
                findings,
                rollback_stage,
                ["Do not change production traffic.", "Repair the evidence package and evaluate a new immutable manifest."],
            )

        phase = rollout["phase"]
        if phase == "pre_canary":
            return self._result(
                manifest,
                Decision.CANARY,
                [],
                rollback_stage,
                [f"Proposed canary: {rollout['traffic_percent']}% traffic for at least {rollout['min_observation_hours']} hours.", "Continuously re-evaluate stop signals; any active signal means rollback."],
            )
        return self._result(
            manifest,
            Decision.PROMOTE,
            [],
            rollback_stage,
            [f"Candidate may be promoted to stage {stage}.", f"Keep stage {rollback_stage} available as the named rollback target."],
        )

    def _validate_header(self, manifest: dict[str, Any], findings: list[Finding]) -> None:
        if manifest.get("manifest_version") != MANIFEST_VERSION:
            findings.append(Finding("manifest_version", f"must equal {MANIFEST_VERSION}"))
        if manifest.get("gate_policy_version") != POLICY_VERSION:
            findings.append(Finding("policy_version", f"must equal {POLICY_VERSION}"))
        for key in ("release_id", "created_at"):
            if not isinstance(manifest.get(key), str) or not manifest[key].strip():
                findings.append(Finding("header_missing", key))
        try:
            created = parse_time(manifest.get("created_at"))
            if (created - self.now).total_seconds() > MAX_CLOCK_SKEW_SECONDS:
                findings.append(Finding("manifest_from_future", "created_at is later than evaluation time"))
        except (ValueError, TypeError):
            findings.append(Finding("timestamp_invalid", "created_at"))

    def _validate_artifacts(self, artifacts: Any, findings: list[Finding]) -> None:
        required = {"code", "prompt", "policy", "schema", "eval_dataset", "model"}
        if not isinstance(artifacts, dict):
            findings.append(Finding("artifacts_missing", "artifacts must be an object"))
            return
        for name in sorted(required):
            pin = artifacts.get(name)
            if not isinstance(pin, str) or not pin.strip():
                findings.append(Finding("artifact_unpinned", name))

    def _validate_evidence(self, evidence: Any, stage: int, base_dir: Path, findings: list[Finding]) -> None:
        if not isinstance(evidence, list):
            findings.append(Finding("evidence_missing", "evidence must be a list"))
            return
        by_id: dict[str, dict[str, Any]] = {}
        for entry in evidence:
            if not isinstance(entry, dict) or not isinstance(entry.get("id"), str):
                findings.append(Finding("evidence_invalid", "each item needs a string id"))
                continue
            evidence_id = entry["id"]
            if evidence_id in by_id:
                findings.append(Finding("evidence_duplicate", evidence_id))
            by_id[evidence_id] = entry
        for evidence_id in sorted(requirements_through(stage, STAGE_EVIDENCE)):
            entry = by_id.get(evidence_id)
            if entry is None:
                findings.append(Finding("evidence_required", evidence_id))
                continue
            self._check_evidence_entry(entry, base_dir, findings)

    def _check_evidence_entry(self, entry: dict[str, Any], base_dir: Path, findings: list[Finding]) -> None:
        evidence_id = entry["id"]
        if entry.get("status") != "pass":
            findings.append(Finding("evidence_not_passed", evidence_id))
        relative = entry.get("path")
        expected_hash = entry.get("sha256")
        if not isinstance(relative, str) or not relative or not isinstance(expected_hash, str):
            findings.append(Finding("evidence_reference_invalid", evidence_id))
        else:
            path = (base_dir / relative).resolve()
            try:
                path.relative_to(base_dir.resolve())
            except ValueError:
                findings.append(Finding("evidence_path_escape", evidence_id))
            else:
                if not path.is_file():
                    findings.append(Finding("evidence_file_missing", evidence_id))
                elif len(expected_hash) != 64 or sha256_file(path) != expected_hash.lower():
                    findings.append(Finding("evidence_hash_mismatch", evidence_id))
        self._check_freshness(entry.get("collected_at"), entry.get("max_age_hours"), evidence_id, findings)

    def _check_freshness(self, timestamp: Any, max_age: Any, item_id: str, findings: list[Finding]) -> None:
        if not isinstance(max_age, (int, float)) or isinstance(max_age, bool) or not math.isfinite(max_age) or max_age <= 0:
            findings.append(Finding("freshness_invalid", item_id))
            return
        try:
            measured = parse_time(timestamp)
        except (ValueError, TypeError):
            findings.append(Finding("timestamp_invalid", item_id))
            return
        age = (self.now - measured).total_seconds()
        if age < -MAX_CLOCK_SKEW_SECONDS:
            findings.append(Finding("evidence_from_future", item_id))
        elif age > max_age * 3600:
            findings.append(Finding("evidence_expired", item_id))

    def _validate_metrics(self, metrics: Any, stage: int, findings: list[Finding]) -> None:
        if not isinstance(metrics, list):
            findings.append(Finding("metrics_missing", "metrics must be a list"))
            return
        by_id: dict[str, dict[str, Any]] = {}
        for item in metrics:
            if not isinstance(item, dict) or not isinstance(item.get("id"), str):
                findings.append(Finding("metric_invalid", "each metric needs a string id"))
                continue
            if item["id"] in by_id:
                findings.append(Finding("metric_duplicate", item["id"]))
            by_id[item["id"]] = item
        for metric_id in sorted(requirements_through(stage, STAGE_METRICS)):
            metric = by_id.get(metric_id)
            if metric is None:
                findings.append(Finding("metric_required", metric_id))
                continue
            value, minimum, maximum = metric.get("value"), metric.get("min"), metric.get("max")
            if not isinstance(value, (int, float)) or isinstance(value, bool) or not math.isfinite(value):
                findings.append(Finding("metric_invalid", metric_id))
            else:
                if minimum is not None:
                    if not isinstance(minimum, (int, float)) or isinstance(minimum, bool) or not math.isfinite(minimum):
                        findings.append(Finding("metric_threshold_invalid", metric_id))
                    elif value < minimum:
                        findings.append(Finding("metric_below_threshold", metric_id))
                if maximum is not None:
                    if not isinstance(maximum, (int, float)) or isinstance(maximum, bool) or not math.isfinite(maximum):
                        findings.append(Finding("metric_threshold_invalid", metric_id))
                    elif value > maximum:
                        findings.append(Finding("metric_above_threshold", metric_id))
                if minimum is None and maximum is None:
                    findings.append(Finding("metric_threshold_missing", metric_id))
            self._check_freshness(metric.get("measured_at"), metric.get("max_age_hours"), metric_id, findings)

    def _validate_stop_signals(self, signals: Any, findings: list[Finding]) -> list[str]:
        if not isinstance(signals, dict):
            findings.append(Finding("stop_signals_missing", "all stop signals must be explicitly false"))
            return []
        active: list[str] = []
        for name in STOP_SIGNALS:
            value = signals.get(name)
            if not isinstance(value, bool):
                findings.append(Finding("stop_signal_unknown", name))
            elif value:
                active.append(name)
        return active

    def _validate_rollout(self, rollout: Any, stage: int | None, findings: list[Finding]) -> dict[str, Any]:
        if not isinstance(rollout, dict):
            findings.append(Finding("rollout_missing", "rollout must be an object"))
            return {}
        phase = rollout.get("phase")
        if phase not in {"pre_canary", "canary"}:
            findings.append(Finding("rollout_phase_invalid", "phase must be pre_canary or canary"))
        current, rollback = rollout.get("current_stage"), rollout.get("rollback_stage")
        if stage is not None:
            if not isinstance(current, int) or isinstance(current, bool) or current < 0 or current > stage or stage > current + 1:
                findings.append(Finding("stage_jump_forbidden", "target must be current stage or one stage higher"))
            if not isinstance(rollback, int) or isinstance(rollback, bool) or rollback < 0 or rollback > stage:
                findings.append(Finding("rollback_stage_invalid", "rollback_stage must be a valid stage no higher than target"))
        traffic = rollout.get("traffic_percent")
        minimum_hours = rollout.get("min_observation_hours")
        observed_hours = rollout.get("observed_hours")
        min_samples = rollout.get("min_samples")
        samples = rollout.get("samples")
        numeric = (("traffic_percent", traffic), ("min_observation_hours", minimum_hours), ("observed_hours", observed_hours), ("min_samples", min_samples), ("samples", samples))
        for name, value in numeric:
            if not isinstance(value, (int, float)) or isinstance(value, bool) or not math.isfinite(value) or value < 0:
                findings.append(Finding("canary_value_invalid", name))
        if isinstance(traffic, (int, float)) and not isinstance(traffic, bool) and not 0 < traffic <= 100:
            findings.append(Finding("canary_traffic_invalid", "traffic_percent must be > 0 and <= 100"))
        if phase == "canary":
            if isinstance(observed_hours, (int, float)) and isinstance(minimum_hours, (int, float)) and observed_hours < minimum_hours:
                findings.append(Finding("canary_too_short", "minimum observation duration not reached"))
            if isinstance(samples, (int, float)) and isinstance(min_samples, (int, float)) and samples < min_samples:
                findings.append(Finding("canary_too_small", "minimum sample count not reached"))
        return rollout

    def _result(self, manifest: dict[str, Any], decision: Decision, findings: list[Finding], rollback_stage: int | None = None, actions: list[str] | None = None) -> GateResult:
        return GateResult(decision, str(manifest.get("release_id", "UNKNOWN")), manifest.get("target_stage") if isinstance(manifest.get("target_stage"), int) else None, rollback_stage, findings, actions or [], self.now.isoformat())


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Evaluate an AI release evidence manifest; never deploys anything.")
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--output", type=Path, help="optional JSON decision-plan output")
    args = parser.parse_args(argv)
    result = ReleaseGate().evaluate_path(args.manifest)
    rendered = json.dumps(result.to_dict(), ensure_ascii=False, indent=2)
    print(rendered)
    if args.output:
        args.output.write_text(rendered + "\n", encoding="utf-8")
    return 0 if result.decision in {Decision.CANARY, Decision.PROMOTE} else 2


if __name__ == "__main__":
    raise SystemExit(main())
