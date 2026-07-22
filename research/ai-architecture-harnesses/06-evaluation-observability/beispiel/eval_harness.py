"""Dependency-free evaluation and observability reference harness."""

from __future__ import annotations

import hashlib
import json
import math
import random
import re
import time
import uuid
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Iterable, Mapping


@dataclass(frozen=True)
class EvalCase:
    id: str
    input: str
    expected: Mapping[str, str]
    critical: bool = False


@dataclass(frozen=True)
class CaseSuite:
    schema_version: str
    suite_id: str
    suite_version: str
    cases: tuple[EvalCase, ...]


@dataclass(frozen=True)
class TrialResult:
    run_id: str
    case_id: str
    trial: int
    status: str
    passed: bool
    critical: bool
    latency_ms: float
    output: Mapping[str, str] | None
    error: str | None = None


@dataclass(frozen=True)
class Summary:
    suite_version: str
    agent_version: str
    planned: int
    completed: int
    passed: int
    critical_failures: int
    pass_rate: float
    wilson_low: float
    wilson_high: float


def load_suite(path: str | Path) -> CaseSuite:
    raw = json.loads(Path(path).read_text(encoding="utf-8"))
    if raw.get("schema_version") != "eval-cases/v1":
        raise ValueError("unsupported case schema")
    cases = tuple(EvalCase(**item) for item in raw["cases"])
    if not cases or len({case.id for case in cases}) != len(cases):
        raise ValueError("suite must contain cases with unique ids")
    return CaseSuite(raw["schema_version"], raw["suite_id"], raw["suite_version"], cases)


class FakeAgent:
    """Offline stand-in whose controlled error rate emulates sampling variance."""

    def __init__(self, version: str, error_rate: float = 0.0, incomplete_rate: float = 0.0):
        if not (0 <= error_rate <= 1 and 0 <= incomplete_rate <= 1):
            raise ValueError("rates must be in [0, 1]")
        self.version = version
        self.error_rate = error_rate
        self.incomplete_rate = incomplete_rate

    def run(self, case: EvalCase, trial: int, seed: int) -> Mapping[str, str]:
        digest = hashlib.sha256(f"{seed}:{self.version}:{case.id}:{trial}".encode()).digest()
        rng = random.Random(int.from_bytes(digest[:8], "big"))
        if rng.random() < self.incomplete_rate:
            raise TimeoutError("simulated timeout")
        if rng.random() < self.error_rate:
            return {"route": "unknown", "language": case.expected["language"]}
        return dict(case.expected)


def deterministic_grader(case: EvalCase, output: Mapping[str, str]) -> bool:
    """Exact, side-effect-free outcome grader."""
    return output == case.expected


_SECRET_VALUE = re.compile(
    r"(?i)(bearer\s+)[A-Za-z0-9._~+/=-]+|"
    r"((?:api[_-]?key|token|password)\s*[=:]\s*)[^\s,;]+"
)
_EMAIL = re.compile(r"(?i)\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b")
_SENSITIVE_KEYS = {"authorization", "api_key", "apikey", "token", "password", "secret"}


def redact(value: Any, key: str = "") -> Any:
    """Redact recursively before trace export; raw values are never retained."""
    if key.lower() in _SENSITIVE_KEYS:
        return "[REDACTED]"
    if isinstance(value, Mapping):
        return {str(k): redact(v, str(k)) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [redact(item) for item in value]
    if isinstance(value, str):
        value = _EMAIL.sub("[REDACTED_EMAIL]", value)
        return _SECRET_VALUE.sub(lambda m: (m.group(1) or m.group(2)) + "[REDACTED]", value)
    return value


class TraceRecorder:
    def __init__(self, run_id: str):
        self.run_id = run_id
        self._events: list[dict[str, Any]] = []

    def emit(self, event: str, attributes: Mapping[str, Any]) -> None:
        self._events.append({
            "schema_version": "trace-event/v1",
            "run_id": self.run_id,
            "sequence": len(self._events) + 1,
            "timestamp_ns": time.time_ns(),
            "event": event,
            "attributes": redact(attributes),
        })

    @property
    def events(self) -> tuple[Mapping[str, Any], ...]:
        return tuple(self._events)

    def write_jsonl(self, path: str | Path) -> None:
        with Path(path).open("w", encoding="utf-8", newline="\n") as stream:
            for event in self._events:
                stream.write(json.dumps(event, ensure_ascii=False, sort_keys=True) + "\n")


def run_evaluation(
    suite: CaseSuite, agent: FakeAgent, trials: int, seed: int = 2026,
    recorder: TraceRecorder | None = None,
) -> list[TrialResult]:
    if trials < 1:
        raise ValueError("trials must be positive")
    results: list[TrialResult] = []
    for case in suite.cases:
        for trial in range(trials):
            run_id = str(uuid.uuid5(uuid.NAMESPACE_URL, f"{suite.suite_version}:{agent.version}:{case.id}:{trial}:{seed}"))
            started = time.perf_counter()
            output: Mapping[str, str] | None = None
            error = None
            status = "completed"
            try:
                output = agent.run(case, trial, seed)
                passed = deterministic_grader(case, output)
            except TimeoutError as exc:
                status, passed, error = "incomplete", False, str(exc)
            latency = (time.perf_counter() - started) * 1000
            result = TrialResult(run_id, case.id, trial, status, passed, case.critical, latency, output, error)
            results.append(result)
            if recorder:
                recorder.emit("eval.trial", {**asdict(result), "input": case.input})
    return results


def wilson_interval(successes: int, total: int, z: float = 1.959963984540054) -> tuple[float, float]:
    if total <= 0:
        return (0.0, 1.0)
    p = successes / total
    denominator = 1 + z * z / total
    centre = (p + z * z / (2 * total)) / denominator
    radius = z * math.sqrt((p * (1 - p) + z * z / (4 * total)) / total) / denominator
    return max(0.0, centre - radius), min(1.0, centre + radius)


def summarize(suite: CaseSuite, agent: FakeAgent, results: Iterable[TrialResult], trials: int) -> Summary:
    rows = list(results)
    planned = len(suite.cases) * trials
    completed = sum(row.status == "completed" for row in rows)
    passed = sum(row.passed for row in rows)
    critical_failures = sum(row.critical and not row.passed for row in rows)
    # Incomplete trials remain in the denominator: no survivorship bias.
    low, high = wilson_interval(passed, planned)
    return Summary(suite.suite_version, agent.version, planned, completed, passed,
                   critical_failures, passed / planned if planned else 0.0, low, high)


def regression_gate(baseline: Summary, candidate: Summary, max_regression: float = 0.02) -> dict[str, Any]:
    reasons: list[str] = []
    if baseline.completed != baseline.planned or candidate.completed != candidate.planned:
        reasons.append("incomplete_sample")
    if candidate.critical_failures:
        reasons.append("critical_failure")
    delta = candidate.pass_rate - baseline.pass_rate
    if delta < -max_regression:
        reasons.append("point_estimate_regression")
    # Conservative uncertainty guard: candidate lower bound may not regress beyond
    # the baseline lower bound by more than the declared tolerance.
    if candidate.wilson_low + max_regression < baseline.wilson_low:
        reasons.append("confidence_bound_regression")
    return {"decision": "pass" if not reasons else "block", "reasons": reasons,
            "delta": delta, "max_regression": max_regression}


def canary_slo_decision(
    *, requests: int, successful: int, critical_violations: int,
    incomplete_traces: int, min_requests: int = 20, min_success_rate: float = 0.95,
    max_incomplete_trace_rate: float = 0.01,
) -> dict[str, Any]:
    if critical_violations:
        return {"decision": "rollback", "reason": "critical_violation"}
    if requests < min_requests:
        return {"decision": "continue", "reason": "insufficient_sample"}
    success_rate = successful / requests
    trace_rate = incomplete_traces / requests
    if success_rate < min_success_rate or trace_rate > max_incomplete_trace_rate:
        return {"decision": "rollback", "reason": "slo_breach"}
    return {"decision": "promote", "reason": "slo_met"}
