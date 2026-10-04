from __future__ import annotations

import cv2
import numpy as np

from pageready.agent import Action, AgentPolicy, QualityGateAgent
from pageready.analysis import PageAnalyzer


def make_page(*, rotation_deg: float = 0.0) -> np.ndarray:
    page = np.full((500, 400, 3), 255, dtype=np.uint8)
    for y in range(70, 430, 35):
        cv2.line(page, (55, y), (345, y), (20, 20, 20), 3)
    if rotation_deg == 0:
        return page
    matrix = cv2.getRotationMatrix2D((200, 250), rotation_deg, 1.0)
    return cv2.warpAffine(page, matrix, (400, 500), borderValue=(255, 255, 255))


def test_skew_estimate_is_close_for_small_rotation() -> None:
    metrics = PageAnalyzer().analyze(make_page(rotation_deg=12.0))
    assert metrics.skew_confidence >= 0.65
    assert abs(abs(metrics.skew_angle_deg) - 12.0) <= 1.5


def test_golden_path_corrects_and_verifies_a_rotated_page() -> None:
    policy = AgentPolicy(minimum_blur=1.0, minimum_contrast=1.0)
    output, trace = QualityGateAgent(policy=policy).process(
        make_page(rotation_deg=12.0), document_id="rotation-fixture"
    )
    assert output.shape == (500, 400, 3)
    assert trace["selected_action"] == Action.APPROVE
    assert [call["tool"] for call in trace["tool_calls"]] == [
        "auto_correct",
        "verify_corrected_page",
    ]
    provenance = next(event for event in trace["events"] if event["event_type"] == "runtime_provenance")
    assert provenance["detail"]["opencv_version"]


def test_blurry_page_requests_rescan() -> None:
    page = cv2.GaussianBlur(make_page(), (31, 31), 0)
    _, trace = QualityGateAgent().process(page, document_id="blur-fixture")
    assert trace["selected_action"] == Action.REQUEST_RESCAN


def test_content_at_frame_escalates_without_claiming_truncation() -> None:
    page = make_page()
    cv2.rectangle(page, (0, 120), (30, 180), (0, 0, 0), -1)
    _, trace = QualityGateAgent().process(page, document_id="frame-fixture")
    assert trace["selected_action"] == Action.HUMAN_REVIEW
