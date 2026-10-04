"""OpenCV evidence collection for PageReady Vision.

The analyzer purposefully reports *content near the image frame*, rather than
claiming that it can infer a physical document boundary from text contours.
That distinction keeps the first MVP honest and allows the policy to fail safe.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import cv2
import numpy as np


@dataclass(frozen=True)
class PageMetrics:
    width: int
    height: int
    skew_angle_deg: float
    skew_confidence: float
    blur_laplacian_var: float
    contrast_std_dev: float
    content_touches_frame: bool
    analysis_notes: tuple[str, ...]

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


class PageAnalyzer:
    """Collect conservative, explainable visual-quality evidence.

    Small skew is estimated from horizontal Hough line candidates. Values with
    weak agreement receive low confidence and must not be auto-corrected by the
    policy layer.
    """

    def __init__(
        self,
        *,
        hough_threshold: int = 45,
        min_line_length: int = 40,
        max_line_gap: int = 12,
        frame_margin_px: int = 8,
    ) -> None:
        self.hough_threshold = hough_threshold
        self.min_line_length = min_line_length
        self.max_line_gap = max_line_gap
        self.frame_margin_px = frame_margin_px

    def analyze_path(self, image_path: str | Path) -> PageMetrics:
        image = cv2.imread(str(image_path), cv2.IMREAD_COLOR)
        if image is None:
            raise ValueError(f"Unable to read image: {image_path}")
        return self.analyze(image)

    def analyze(self, image: np.ndarray) -> PageMetrics:
        if image.ndim not in (2, 3):
            raise ValueError("Expected a grayscale or BGR image array")

        gray = image if image.ndim == 2 else cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        height, width = gray.shape[:2]
        skew_angle, skew_confidence, line_count = self._estimate_small_skew(gray)
        blur = float(cv2.Laplacian(gray, cv2.CV_64F).var())
        contrast = float(gray.std())
        frame_touch = self._content_touches_frame(gray)

        notes: list[str] = []
        if line_count == 0:
            notes.append("No horizontal line candidates; skew is not reliable.")
        elif skew_confidence < 0.65:
            notes.append("Horizontal line candidates disagree; skew is not reliable.")
        if frame_touch:
            notes.append("Dark content reaches the frame margin; manual review is required.")

        return PageMetrics(
            width=width,
            height=height,
            skew_angle_deg=round(skew_angle, 3),
            skew_confidence=round(skew_confidence, 3),
            blur_laplacian_var=round(blur, 3),
            contrast_std_dev=round(contrast, 3),
            content_touches_frame=frame_touch,
            analysis_notes=tuple(notes),
        )

    def _estimate_small_skew(self, gray: np.ndarray) -> tuple[float, float, int]:
        """Estimate residual skew within +/- 25 degrees from horizontal lines.

        This is not an orientation classifier. A portrait/landscape orientation
        decision belongs to a later, separately evaluated feature.
        """
        edges = cv2.Canny(gray, 50, 150, apertureSize=3)
        lines = cv2.HoughLinesP(
            edges,
            rho=1,
            theta=np.pi / 180,
            threshold=self.hough_threshold,
            minLineLength=self.min_line_length,
            maxLineGap=self.max_line_gap,
        )
        if lines is None:
            return 0.0, 0.0, 0

        # OpenCV bindings have returned both (N, 1, 4) and (N, 4) here.
        # Normalising avoids coupling the analyzer to one wheel's array shape.
        segments = np.asarray(lines).reshape(-1, 4)
        candidates: list[float] = []
        for x1, y1, x2, y2 in segments:
            angle = float(np.degrees(np.arctan2(y2 - y1, x2 - x1)))
            # Lines are undirected: normalise them to horizontal residual angle.
            if angle > 90:
                angle -= 180
            elif angle <= -90:
                angle += 180
            if abs(angle) <= 25:
                candidates.append(angle)

        if not candidates:
            return 0.0, 0.0, 0

        values = np.asarray(candidates, dtype=np.float64)
        median = float(np.median(values))
        median_abs_deviation = float(np.median(np.abs(values - median)))
        inliers = values[np.abs(values - median) <= max(2.0, 2.5 * median_abs_deviation)]
        if len(inliers) == 0:
            return 0.0, 0.0, len(candidates)

        estimated = float(np.median(inliers))
        agreement = max(0.0, 1.0 - min(1.0, median_abs_deviation / 8.0))
        coverage = min(1.0, len(inliers) / 8.0)
        confidence = agreement * coverage
        return estimated, confidence, len(candidates)

    def _content_touches_frame(self, gray: np.ndarray) -> bool:
        """Return a conservative ink-at-frame signal, not a truncation verdict."""
        _, dark_content = cv2.threshold(
            gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU
        )
        margin = min(self.frame_margin_px, max(1, min(gray.shape[:2]) // 8))
        frame = np.concatenate(
            (
                dark_content[:margin, :].ravel(),
                dark_content[-margin:, :].ravel(),
                dark_content[:, :margin].ravel(),
                dark_content[:, -margin:].ravel(),
            )
        )
        # A few isolated pixels are harmless compression noise. Require a small
        # occupancy rate before escalating.
        return bool(np.count_nonzero(frame) / frame.size > 0.015)
