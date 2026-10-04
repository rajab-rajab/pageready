from __future__ import annotations

import pytest

from pageready.schemas import PageStatus
from pageready.service import BatchService


def test_batch_processes_all_four_seeded_pages_and_keeps_audit_image_free() -> None:
    service = BatchService()
    batch = service.create_demo_batch()
    service.process()
    assert [page.status for page in batch.pages] == [PageStatus.APPROVED, PageStatus.APPROVED, PageStatus.RESCAN_REQUESTED, PageStatus.NEEDS_REVIEW]
    audit = service.audit_export().model_dump_json()
    assert "original_image_url" not in audit
    assert "processed_image_url" not in audit
    assert "iVBOR" not in audit


def test_override_requires_review_and_keeps_trace() -> None:
    service = BatchService()
    batch = service.create_demo_batch()
    service.process()
    page = batch.pages[-1]
    service.approve_with_warning(page.id, "Source register remains readable.")
    assert page.status is PageStatus.APPROVED_WITH_WARNING
    assert page.trace[-1].event_type == "clerk_override"
    with pytest.raises(ValueError, match="Only a page"):
        service.approve_with_warning(batch.pages[0].id, "No warning exists.")


def test_active_batch_blocks_a_second_batch_and_clear_allows_one() -> None:
    service = BatchService()
    batch = service.create_demo_batch()
    with pytest.raises(ValueError, match="Clear the current queue"):
        service.create_demo_batch()
    service.clear()
    assert service.create_demo_batch().id != batch.id
