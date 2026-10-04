"""Tool-calling, fail-safe quality-gate agent.

The planner is intentionally deterministic in this milestone so every decision
is replayable. Its interface is a true tool loop: observe, choose, execute,
observe again, then finish or escalate. A model-backed planner can later use
the same tool contract without weakening these safety constraints.
"""

from __future__ import annotations

from dataclasses import asdict
from datetime import UTC, datetime
from enum import StrEnum
from hashlib import sha256
from time import perf_counter, time
from typing import Any, Protocol
from uuid import uuid4

import cv2
import numpy as np

from .analysis import PageAnalyzer, PageMetrics
from .policy import QualityPolicy


class Action(StrEnum):
    APPROVE = "approve"
    AUTO_CORRECT = "auto_correct"
    REQUEST_RESCAN = "request_rescan"
    HUMAN_REVIEW = "send_to_human_review"


AgentPolicy = QualityPolicy


class TraceSink(Protocol):
    def write(self, trace: dict[str, Any]) -> None: ...


class InMemoryTraceSink:
    def __init__(self) -> None:
        self.traces: list[dict[str, Any]] = []

    def write(self, trace: dict[str, Any]) -> None:
        self.traces.append(trace)


class QualityGateAgent:
    """Performs the golden perception -> decision -> action -> verification loop."""

    pipeline_version = "v0.2.0"

    def __init__(
        self,
        analyzer: PageAnalyzer | None = None,
        policy: AgentPolicy | None = None,
        trace_sink: TraceSink | None = None,
    ) -> None:
        self.analyzer = analyzer or PageAnalyzer()
        self.policy = policy or AgentPolicy()
        self.trace_sink = trace_sink or InMemoryTraceSink()

    def process(self, image: np.ndarray, *, document_id: str | None = None) -> tuple[np.ndarray, dict[str, Any]]:
        started = perf_counter()
        document_id = document_id or str(uuid4())
        input_checksum = self._checksum(image)
        initial = self.analyze_page(image)
        tool_calls: list[dict[str, Any]] = []
        events = [
            self._event("input_received", "Received image for quality analysis.", {"input_checksum_sha256": input_checksum}),
            self._event(
                "runtime_provenance",
                "Recorded the OpenCV runtime that produced the visual evidence.",
                {"opencv_version": cv2.__version__},
            ),
            self._event("image_analyzed", "Collected OpenCV quality evidence.", {"metrics": asdict(initial)}),
        ]
        output = image.copy()

        action, reason = self._plan(initial)
        planned_action = action
        events.append(self._event("action_selected", "Selected deterministic policy action.", {"action": action.value, "reason": reason}))
        if action is Action.AUTO_CORRECT:
            # The Hough estimate uses image-coordinate orientation (positive Y
            # points down), which is the same convention as OpenCV's rotation
            # matrix. Applying the measured residual angle therefore deskews it.
            output, correction = self.auto_correct(image, angle_deg=initial.skew_angle_deg)
            tool_calls.append(correction)
            events.append(self._event("tool_invoked", "Applied OpenCV deskew correction.", correction))
            verified = self.verify_corrected_page(output)
            verification = {"tool": "verify_corrected_page", "status": "success", "post_correction_metrics": asdict(verified)}
            tool_calls.append(verification)
            events.append(self._event("correction_verified", "Re-analyzed the corrected image.", verification))
            if (
                verified.skew_confidence >= self.policy.minimum_skew_confidence
                and abs(verified.skew_angle_deg) <= self.policy.verified_skew_max_deg
                and not verified.content_touches_frame
            ):
                action = Action.APPROVE
                reason = "Correction was verified within the configured skew tolerance."
            else:
                action = Action.HUMAN_REVIEW
                reason = "Correction could not be verified confidently; escalation is required."
        elif action is Action.REQUEST_RESCAN:
            rescan = {"tool": "request_rescan", "status": "queued", "reason": reason}
            tool_calls.append(rescan)
            events.append(self._event("rescan_requested", "Queued a rescan request.", rescan))
        elif action is Action.HUMAN_REVIEW:
            review = {"tool": "send_to_human_review", "status": "queued", "reason": reason}
            tool_calls.append(review)
            events.append(self._event("human_review_requested", "Queued a human review request.", review))

        events.append(self._event("outcome_resolved", "Resolved the page quality outcome.", {"planned_action": planned_action.value, "final_action": action.value, "reason": reason}))

        trace = {
            "trace_id": str(uuid4()),
            "document_id": document_id,
            "timestamp_unix": time(),
            "input_checksum_sha256": input_checksum,
            "pipeline_version": self.pipeline_version,
            "policy_version": self.policy.version,
            "initial_metrics": asdict(initial),
            "selected_action": action.value,
            "decision_reason": reason,
            "tool_calls": tool_calls,
            "events": events,
            "execution_runtime_ms": round((perf_counter() - started) * 1000, 3),
        }
        self.trace_sink.write(trace)
        return output, trace

    def analyze_page(self, image: np.ndarray) -> PageMetrics:
        return self.analyzer.analyze(image)

    def verify_corrected_page(self, image: np.ndarray) -> PageMetrics:
        return self.analyzer.analyze(image)

    def auto_correct(self, image: np.ndarray, *, angle_deg: float) -> tuple[np.ndarray, dict[str, Any]]:
        height, width = image.shape[:2]
        matrix = cv2.getRotationMatrix2D((width / 2, height / 2), angle_deg, 1.0)
        corrected = cv2.warpAffine(
            image,
            matrix,
            (width, height),
            flags=cv2.INTER_CUBIC,
            borderMode=cv2.BORDER_REPLICATE,
        )
        return corrected, {
            "tool": "auto_correct",
            "status": "success",
            "params": {"action": "deskew", "angle_deg": round(angle_deg, 3)},
            "action_outcome": "Rotated the image and passed it to verification.",
        }

    def _plan(self, metrics: PageMetrics) -> tuple[Action, str]:
        if metrics.content_touches_frame:
            return Action.HUMAN_REVIEW, "Content reaches the frame margin; clipping cannot be ruled out."
        if metrics.blur_laplacian_var < self.policy.minimum_blur:
            return Action.REQUEST_RESCAN, "Focus evidence is below the minimum blur threshold."
        if metrics.contrast_std_dev < self.policy.minimum_contrast:
            return Action.HUMAN_REVIEW, "Contrast evidence is below the safety threshold."
        if metrics.skew_confidence < self.policy.minimum_skew_confidence:
            return Action.HUMAN_REVIEW, "Skew evidence has insufficient confidence for automatic correction."
        magnitude = abs(metrics.skew_angle_deg)
        if self.policy.correctable_skew_min_deg <= magnitude <= self.policy.correctable_skew_max_deg:
            return Action.AUTO_CORRECT, "Confident, recoverable small skew was detected."
        if magnitude > self.policy.correctable_skew_max_deg:
            return Action.HUMAN_REVIEW, "Skew exceeds the validated automatic-correction range."
        return Action.APPROVE, "All configured quality checks passed."

    @staticmethod
    def _checksum(image: np.ndarray) -> str:
        return sha256(np.ascontiguousarray(image).tobytes()).hexdigest()

    def _event(self, event_type: str, summary: str, detail: dict[str, Any]) -> dict[str, Any]:
        return {
            "event_id": str(uuid4()),
            "timestamp_utc": datetime.now(UTC).isoformat(),
            "event_type": event_type,
            "actor": "system",
            "summary": summary,
            "pipeline_version": self.pipeline_version,
            "policy_version": self.policy.version,
            "detail": detail,
        }
