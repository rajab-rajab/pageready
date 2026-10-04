"""Safe, deterministic synthetic municipal document fixtures."""

from __future__ import annotations

from dataclasses import dataclass

import cv2
import numpy as np


@dataclass(frozen=True)
class DemoDocument:
    filename: str
    expected_outcome: str
    image: np.ndarray


def _base_document(title: str, *, seed: int, outer_border: bool = True) -> np.ndarray:
    """Draw a harmless municipal-style form without real-person data."""
    rng = np.random.default_rng(seed)
    page = np.full((700, 520, 3), 246, dtype=np.uint8)
    ink = (40, 52, 71)
    accent = (89, 108, 135)

    if outer_border:
        cv2.rectangle(page, (36, 34), (484, 666), ink, 2)
    cv2.circle(page, (80, 82), 26, accent, 3)
    cv2.circle(page, (80, 82), 14, accent, 2)
    cv2.putText(page, "CITY ARCHIVES", (122, 74), cv2.FONT_HERSHEY_SIMPLEX, 0.72, ink, 2)
    cv2.putText(page, title, (64, 128), cv2.FONT_HERSHEY_SIMPLEX, 0.64, ink, 2)
    cv2.line(page, (64, 142), (456, 142), accent, 2)
    for index, y in enumerate(range(190, 570, 48), start=1):
        width = int(rng.integers(250, 355))
        cv2.putText(page, f"FIELD {index:02d}", (68, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.36, accent, 1)
        cv2.line(page, (68, y), (68 + width, y), ink, 2)
    cv2.rectangle(page, (334, 586), (446, 628), accent, 2)
    cv2.putText(page, "DEMO RECORD", (342, 612), cv2.FONT_HERSHEY_SIMPLEX, 0.35, accent, 1)
    return page


def _rotate(image: np.ndarray, angle_deg: float) -> np.ndarray:
    height, width = image.shape[:2]
    matrix = cv2.getRotationMatrix2D((width / 2, height / 2), angle_deg, 1.0)
    return cv2.warpAffine(image, matrix, (width, height), borderValue=(246, 246, 246))


def generate_demo_documents() -> list[DemoDocument]:
    """Return the fixed four-page municipal batch used by every demo run."""
    clean = _base_document("PERMIT REGISTER", seed=11)
    # The synthetic outer border would rotate into the frame margin and
    # correctly trigger the clipping safeguard. This fixture models an
    # unclipped, recoverably skewed page instead, so it omits that border.
    skewed = _rotate(_base_document("COUNCIL MINUTES", seed=22, outer_border=False), 11.5)
    blurred = cv2.GaussianBlur(_base_document("PROPERTY CARD", seed=33), (31, 31), 0)
    low_contrast_source = _base_document("ZONING NOTICE", seed=44)
    # Keep enough edge detail for the focus check to pass while reducing the
    # tonal spread below the contrast threshold. The policy can then correctly
    # demonstrate its intended human-review route instead of rescan priority.
    low_contrast = cv2.addWeighted(low_contrast_source, 0.35, np.full_like(low_contrast_source, 210), 0.65, 0)
    return [
        DemoDocument("permit-register-clean.png", "Approved", clean),
        DemoDocument("council-minutes-skewed.png", "Approved", skewed),
        DemoDocument("property-card-blurred.png", "Rescan requested", blurred),
        DemoDocument("zoning-notice-low-contrast.png", "Needs review", low_contrast),
    ]
