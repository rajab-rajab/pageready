"""Generate a reproducible task-success and safety evaluation artifact.

This is deliberately a small, deterministic smoke evaluation over the four
checked-in demo fixtures. It is not the 150-page holdout evaluation described
in docs/evaluation.md, and the output says so explicitly.
"""

from __future__ import annotations

import argparse
import json
import platform
import sys
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path

import cv2

from pageready.agent import Action, QualityGateAgent
from pageready.demo import generate_demo_documents


EXPECTED_ACTIONS = {
    "Approved": Action.APPROVE,
    "Rescan requested": Action.REQUEST_RESCAN,
    "Needs review": Action.HUMAN_REVIEW,
}


def main() -> int:
    parser = argparse.ArgumentParser(description="Evaluate PageReady's deterministic demo fixtures.")
    parser.add_argument("--output", type=Path, default=Path("runs/evaluation.json"))
    args = parser.parse_args()

    agent = QualityGateAgent()
    fixtures: list[dict[str, object]] = []
    outcomes: Counter[str] = Counter()
    failures: list[str] = []
    unsafe_approvals: list[str] = []
    for fixture in generate_demo_documents():
        _, trace = agent.process(fixture.image, document_id=f"evaluation-{fixture.filename}")
        observed = trace["selected_action"]
        expected_status = fixture.expected_outcome
        expected = EXPECTED_ACTIONS[expected_status]
        matched = observed == expected
        outcomes[observed] += 1
        if not matched:
            failures.append(fixture.filename)
        if observed == Action.APPROVE and expected is not Action.APPROVE:
            unsafe_approvals.append(fixture.filename)
        fixtures.append(
            {
                "fixture": fixture.filename,
                "expected_status": expected_status,
                "expected_action": expected,
                "observed_action": observed,
                "matched_expected_action": matched,
                "tool_sequence": [call["tool"] for call in trace["tool_calls"]],
                "trace_event_types": [event["event_type"] for event in trace["events"]],
            }
        )

    report = {
        "schema_version": "1.0",
        "generated_at_utc": datetime.now(UTC).isoformat(),
        "scope": "Deterministic four-fixture smoke evaluation; not a holdout or production-accuracy result.",
        "environment": {
            "platform": platform.platform(),
            "machine": platform.machine(),
            "python": sys.version.split()[0],
            "opencv": cv2.__version__,
        },
        "summary": {
            "fixtures": len(fixtures),
            "task_successes": sum(item["matched_expected_action"] for item in fixtures),
            "task_failures": len(failures),
            "failure_fixture_names": failures,
            "unsafe_approvals": len(unsafe_approvals),
            "unsafe_approval_fixture_names": unsafe_approvals,
            "outcomes": dict(sorted(outcomes.items())),
        },
        "fixtures": fixtures,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0 if not failures and not unsafe_approvals else 1


if __name__ == "__main__":
    raise SystemExit(main())
