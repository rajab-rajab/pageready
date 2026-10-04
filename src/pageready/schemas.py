"""Validated domain contracts shared by the API, service, and audit exporter."""

from __future__ import annotations

from enum import StrEnum
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, HttpUrl, field_validator


class PageStatus(StrEnum):
    QUEUED = "Queued"
    ANALYZING = "Analyzing"
    CORRECTED = "Corrected"
    RESCAN_REQUESTED = "Rescan requested"
    NEEDS_REVIEW = "Needs review"
    APPROVED = "Approved"
    APPROVED_WITH_WARNING = "Approved with warning"


class IntakeError(BaseModel):
    code: str
    message: str


class QualityMetricsContract(BaseModel):
    width: int = Field(gt=0)
    height: int = Field(gt=0)
    skew_angle_deg: float
    skew_confidence: float = Field(ge=0, le=1)
    blur_laplacian_var: float = Field(ge=0)
    contrast_std_dev: float = Field(ge=0)
    content_touches_frame: bool
    analysis_notes: tuple[str, ...] = ()


class TraceEvent(BaseModel):
    model_config = ConfigDict(extra="forbid")

    event_id: str
    timestamp_utc: str
    event_type: str
    actor: Literal["system", "clerk"]
    summary: str
    pipeline_version: str
    policy_version: str
    detail: dict[str, Any] = Field(default_factory=dict)


class OverrideRequest(BaseModel):
    note: str = Field(min_length=1, max_length=1000)

    @field_validator("note")
    @classmethod
    def require_meaningful_note(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("An override note is required.")
        return cleaned


class PageJob(BaseModel):
    id: str
    filename: str
    source: Literal["demo", "upload"]
    queue_index: int = Field(ge=0)
    status: PageStatus
    error: IntakeError | None = None
    original_image_url: str | None = None
    processed_image_url: str | None = None
    metrics: QualityMetricsContract | None = None
    warning_reason: str | None = None
    trace: list[TraceEvent] = Field(default_factory=list)
    override_note: str | None = None


class AuditPage(BaseModel):
    id: str
    filename: str
    source: Literal["demo", "upload"]
    queue_index: int
    status: PageStatus
    error: IntakeError | None = None
    metrics: QualityMetricsContract | None = None
    warning_reason: str | None = None
    trace: list[TraceEvent] = Field(default_factory=list)
    override_note: str | None = None


class AuditExport(BaseModel):
    batch_id: str
    policy_version: str
    pipeline_version: str
    pages: list[AuditPage]
