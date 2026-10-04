"""Capture reproducible local quality-gate benchmark evidence.

This script records local measurements only. Running it on an ARM64 machine is
necessary but not sufficient to claim AWS Graviton results: the host details in
the output must show that execution was actually on the chosen AWS instance.
"""

from __future__ import annotations

import argparse
import json
import platform
import statistics
import sys
from datetime import UTC, datetime
from pathlib import Path
from time import perf_counter

import cv2
import numpy as np

from pageready.agent import QualityGateAgent
from pageready.demo import generate_demo_documents


def main() -> int:
    parser = argparse.ArgumentParser(description="Benchmark PageReady's deterministic quality gate.")
    parser.add_argument("--runs", type=int, default=10)
    parser.add_argument("--warmup", type=int, default=2)
    parser.add_argument("--output", type=Path, default=Path("runs/benchmark.json"))
    args = parser.parse_args()
    if args.runs < 1 or args.warmup < 0:
        parser.error("--runs must be at least 1 and --warmup cannot be negative")

    agent = QualityGateAgent()
    results: list[dict[str, object]] = []
    for fixture in generate_demo_documents():
        for _ in range(args.warmup):
            agent.process(fixture.image, document_id=f"warmup-{fixture.filename}")
        timings: list[float] = []
        outcomes: list[str] = []
        for run in range(args.runs):
            started = perf_counter()
            _, trace = agent.process(fixture.image, document_id=f"{fixture.filename}-{run}")
            timings.append((perf_counter() - started) * 1000)
            outcomes.append(trace["selected_action"])
        ordered = sorted(timings)
        results.append({"fixture": fixture.filename, "expected_outcome": fixture.expected_outcome, "observed_outcomes": sorted(set(outcomes)), "runs": args.runs, "median_ms": round(statistics.median(timings), 3), "p95_ms": round(ordered[max(0, int(len(ordered) * 0.95) - 1)], 3)})

    report = {
        "schema_version": "1.0",
        "generated_at_utc": datetime.now(UTC).isoformat(),
        "claim_guardrail": "Local benchmark only. Do not claim AWS Graviton or COOL results unless this report was captured on documented AWS ARM64/Graviton hardware with the intended runtime.",
        "environment": {"platform": platform.platform(), "machine": platform.machine(), "processor": platform.processor(), "python": sys.version.split()[0], "opencv": cv2.__version__, "numpy": np.__version__},
        "benchmark": {"warmup_runs": args.warmup, "measured_runs": args.runs, "fixtures": results},
        "baseline_comparison": {"status": "not-recorded", "note": "Run the same command on the comparison environment and record both reports."},
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
