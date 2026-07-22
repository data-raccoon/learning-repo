"""Run from this directory with: python demo.py"""

import json
from dataclasses import asdict
from pathlib import Path

from eval_harness import (FakeAgent, TraceRecorder, canary_slo_decision,
                          load_suite, regression_gate, run_evaluation, summarize)


HERE = Path(__file__).parent


def main() -> None:
    suite = load_suite(HERE / "cases.v1.json")
    trials = 25
    baseline_agent = FakeAgent("baseline-1", error_rate=0.04)
    candidate_agent = FakeAgent("candidate-2", error_rate=0.03)
    trace = TraceRecorder("comparison-demo")
    baseline = summarize(suite, baseline_agent,
                         run_evaluation(suite, baseline_agent, trials, recorder=trace), trials)
    candidate = summarize(suite, candidate_agent,
                          run_evaluation(suite, candidate_agent, trials, recorder=trace), trials)
    trace.write_jsonl(HERE / "traces.jsonl")
    report = {
        "baseline": asdict(baseline),
        "candidate": asdict(candidate),
        "regression_gate": regression_gate(baseline, candidate, max_regression=0.03),
        "canary": canary_slo_decision(requests=100, successful=98,
                                      critical_violations=0, incomplete_traces=0),
        "trace_file": "traces.jsonl",
    }
    print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
