"""Ephemeral batch orchestration for the local PageReady demo."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from uuid import uuid4

import cv2
import numpy as np

from .agent import Action, QualityGateAgent
from .demo import generate_demo_documents
from .schemas import AuditExport, AuditPage, IntakeError, PageJob, PageStatus, QualityMetricsContract, TraceEvent


@dataclass
class Batch:
    id: str
    pages: list[PageJob] = field(default_factory=list)
    images: dict[str, bytes] = field(default_factory=dict)
    processing: bool = False


class BatchService:
    """One active, intentionally non-persistent batch for the local demo."""

    def __init__(self, agent: QualityGateAgent | None = None) -> None:
        self.agent = agent or QualityGateAgent()
        self.batch: Batch | None = None

    def create_demo_batch(self) -> Batch:
        self._require_empty()
        batch = Batch(id=str(uuid4()))
        for index, document in enumerate(generate_demo_documents()):
            page = PageJob(
                id=str(uuid4()), filename=document.filename, source="demo", queue_index=index, status=PageStatus.QUEUED
            )
            batch.pages.append(page)
            batch.images[f"{page.id}:original"] = self._encode_png(document.image)
        self.batch = batch
        return batch

    def add_upload(self, filename: str, payload: bytes) -> PageJob:
        if self.batch is None:
            self.batch = Batch(id=str(uuid4()))
        batch = self.batch
        if batch.processing:
            raise ValueError("Cannot add files while the batch is processing.")
        if any(existing.source == "demo" for existing in batch.pages):
            raise ValueError("Clear the current queue before adding files to a demo batch.")
        page = PageJob(id=str(uuid4()), filename=filename or "unnamed-upload", source="upload", queue_index=len(batch.pages), status=PageStatus.QUEUED)
        image = cv2.imdecode(np.frombuffer(payload, dtype=np.uint8), cv2.IMREAD_COLOR)
        if image is None:
            page.error = IntakeError(code="unsupported_or_corrupt", message="The selected file is not a readable image.")
        else:
            batch.images[f"{page.id}:original"] = self._encode_png(image)
        batch.pages.append(page)
        return page

    def process(self) -> Batch:
        batch = self._require_batch()
        if batch.processing:
            raise ValueError("Batch processing is already in progress.")
        batch.processing = True
        try:
            for page in batch.pages:
                if page.error is not None or page.status is not PageStatus.QUEUED:
                    continue
                page.status = PageStatus.ANALYZING
                original = self._decode_png(batch.images[f"{page.id}:original"])
                output, trace = self.agent.process(original, document_id=page.id)
                page.metrics = QualityMetricsContract.model_validate(trace["initial_metrics"])
                page.trace = [TraceEvent.model_validate(event) for event in trace["events"]]
                page.warning_reason = None
                final_action = Action(trace["selected_action"])
                if trace["tool_calls"] and trace["tool_calls"][0]["tool"] == "auto_correct":
                    page.status = PageStatus.CORRECTED
                    batch.images[f"{page.id}:processed"] = self._encode_png(output)
                if final_action is Action.APPROVE:
                    page.status = PageStatus.APPROVED
                elif final_action is Action.REQUEST_RESCAN:
                    page.status = PageStatus.RESCAN_REQUESTED
                    page.warning_reason = trace["decision_reason"]
                else:
                    page.status = PageStatus.NEEDS_REVIEW
                    page.warning_reason = trace["decision_reason"]
            return batch
        finally:
            batch.processing = False

    def approve_with_warning(self, page_id: str, note: str) -> PageJob:
        page = self._find_page(page_id)
        if page.status is not PageStatus.NEEDS_REVIEW:
            raise ValueError("Only a page that needs review can be approved with a warning.")
        cleaned = note.strip()
        if not cleaned:
            raise ValueError("An override note is required.")
        page.override_note = cleaned
        page.status = PageStatus.APPROVED_WITH_WARNING
        page.trace.append(
            TraceEvent(
                event_id=str(uuid4()), timestamp_utc=datetime.now(UTC).isoformat(), event_type="clerk_override",
                actor="clerk", summary="Clerk approved the page while retaining the warning.",
                pipeline_version=self.agent.pipeline_version, policy_version=self.agent.policy.version,
                detail={"note": cleaned, "prior_warning": page.warning_reason},
            )
        )
        return page

    def get_batch(self) -> Batch:
        return self._require_batch()

    def get_image(self, image_id: str) -> bytes:
        batch = self._require_batch()
        try:
            return batch.images[image_id]
        except KeyError as error:
            raise KeyError("Image not found.") from error

    def audit_export(self) -> AuditExport:
        batch = self._require_batch()
        pages = [AuditPage.model_validate(page.model_dump(exclude={"original_image_url", "processed_image_url"})) for page in batch.pages]
        return AuditExport(batch_id=batch.id, policy_version=self.agent.policy.version, pipeline_version=self.agent.pipeline_version, pages=pages)

    def clear(self) -> None:
        self._require_batch()
        self.batch = None

    def reset_session(self) -> None:
        """Clear the intentionally ephemeral local demo session on browser refresh."""
        self.batch = None

    def remove_page(self, page_id: str) -> None:
        batch = self._require_batch()
        if batch.processing:
            raise ValueError("Cannot remove files while the batch is processing.")
        page = self._find_page(page_id)
        batch.pages.remove(page)
        batch.images.pop(f"{page.id}:original", None)
        batch.images.pop(f"{page.id}:processed", None)
        for index, remaining in enumerate(batch.pages):
            remaining.queue_index = index

    def public_batch(self, batch: Batch | None = None) -> dict[str, object]:
        batch = batch or self._require_batch()
        pages = []
        for page in batch.pages:
            public = page.model_copy(deep=True)
            if f"{page.id}:original" in batch.images:
                public.original_image_url = f"/api/images/{page.id}:original"
            if f"{page.id}:processed" in batch.images:
                public.processed_image_url = f"/api/images/{page.id}:processed"
            pages.append(public.model_dump(mode="json"))
        return {"id": batch.id, "processing": batch.processing, "pages": pages}

    def _require_empty(self) -> None:
        if self.batch is not None:
            raise ValueError("Clear the current queue before starting a new batch.")

    def _require_batch(self) -> Batch:
        if self.batch is None:
            raise ValueError("No active batch exists.")
        return self.batch

    def _find_page(self, page_id: str) -> PageJob:
        for page in self._require_batch().pages:
            if page.id == page_id:
                return page
        raise KeyError("Page not found.")

    @staticmethod
    def _encode_png(image: np.ndarray) -> bytes:
        ok, encoded = cv2.imencode(".png", image)
        if not ok:
            raise ValueError("Unable to encode processed image.")
        return encoded.tobytes()

    @staticmethod
    def _decode_png(payload: bytes) -> np.ndarray:
        image = cv2.imdecode(np.frombuffer(payload, dtype=np.uint8), cv2.IMREAD_COLOR)
        if image is None:
            raise ValueError("Stored image cannot be decoded.")
        return image
