import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
REPORT = ROOT / ".mc-mod-agents" / "evidence" / "qa-report.json"
BUILD_GATE = ROOT / ".mc-mod-agents" / "evidence" / "build-gate.json"
REQUIRED = {"mod_id", "inspection_date", "inspector", "findings", "summary", "verifier_results", "coverage"}
OWNERS = {"mod-architect", "asset-producer", "mod-engineer", "root-orchestrator"}
SEVERITIES = {"blocking", "critical", "major", "minor", "info"}


def main() -> int:
    try:
        report = json.loads(REPORT.read_text(encoding="utf-8"))
        build = json.loads(BUILD_GATE.read_text(encoding="utf-8"))["gate"]
        mod_id = json.loads((ROOT / "mod-spec.json").read_text(encoding="utf-8"))["mod_id"]
    except (OSError, KeyError, TypeError, UnicodeError, json.JSONDecodeError):
        return 1
    if set(report) != REQUIRED or report.get("mod_id") != mod_id:
        return 1
    findings = report.get("findings")
    summary = report.get("summary")
    verifier_results = report.get("verifier_results")
    coverage = report.get("coverage")
    if not isinstance(findings, list) or not isinstance(summary, dict):
        return 1
    if not isinstance(verifier_results, list) or not isinstance(coverage, dict):
        return 1
    if any(item.get("owner") not in OWNERS or item.get("severity") not in SEVERITIES for item in findings if isinstance(item, dict)):
        return 1
    if any(not isinstance(item, dict) for item in findings):
        return 1
    counts = {severity: sum(1 for item in findings if item.get("severity") == severity) for severity in SEVERITIES}
    if summary.get("total_findings") != len(findings) or any(summary.get(key) != value for key, value in counts.items()):
        return 1
    expected = {item["id"]: item["exit_code"] for item in build.get("checks", [])}
    observed = {item.get("verifier_id"): item.get("exit_code") for item in verifier_results if isinstance(item, dict)}
    if observed != expected:
        return 1
    if any(value not in {"passed", "failed", "not_tested", "not_applicable"} for value in coverage.values()):
        return 1
    print(json.dumps({"status": "passed", "findings": len(findings), "verifiers": len(observed)}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
