"""Versioned quality thresholds for the deterministic quality gate."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class QualityPolicy(BaseModel):
    """Fail-safe policy settings kept outside presentation-layer code."""

    model_config = ConfigDict(frozen=True)

    version: str = "v0.2.0"
    minimum_blur: float = Field(default=100.0, ge=0)
    minimum_contrast: float = Field(default=25.0, ge=0)
    minimum_skew_confidence: float = Field(default=0.65, ge=0, le=1)
    correctable_skew_min_deg: float = Field(default=1.0, ge=0)
    correctable_skew_max_deg: float = Field(default=20.0, gt=0, le=25)
    verified_skew_max_deg: float = Field(default=0.75, ge=0, le=25)

