from __future__ import annotations

import cv2
from fastapi.testclient import TestClient

from pageready.api import create_app
from pageready.demo import generate_demo_documents
from pageready.service import BatchService


def test_demo_api_processes_and_exports_an_image_free_audit() -> None:
    client = TestClient(create_app(BatchService()))
    created = client.post("/api/batches/demo")
    assert created.status_code == 201
    batch_id = created.json()["id"]
    processed = client.post(f"/api/batches/{batch_id}/process")
    assert processed.status_code == 200
    pages = processed.json()["pages"]
    assert [page["status"] for page in pages] == ["Approved", "Approved", "Rescan requested", "Needs review"]
    image = client.get(pages[1]["processed_image_url"])
    assert image.status_code == 200
    assert image.headers["content-type"] == "image/png"
    audit = client.get(f"/api/batches/{batch_id}/audit")
    assert audit.status_code == 200
    assert "original_image_url" not in audit.text
    assert "iVBOR" not in audit.text


def test_api_rejects_new_batch_and_accepts_a_review_override() -> None:
    client = TestClient(create_app(BatchService()))
    batch_id = client.post("/api/batches/demo").json()["id"]
    assert client.post("/api/batches/demo").status_code == 400
    processed = client.post(f"/api/batches/{batch_id}/process").json()
    review_page = processed["pages"][-1]
    missing_note = client.post(f"/api/pages/{review_page['id']}/approve-warning", json={"note": " "})
    assert missing_note.status_code == 422
    approved = client.post(f"/api/pages/{review_page['id']}/approve-warning", json={"note": "Clerk reviewed original."})
    assert approved.status_code == 200
    assert approved.json()["status"] == "Approved with warning"


def test_session_reset_allows_a_fresh_demo_after_a_browser_refresh() -> None:
    client = TestClient(create_app(BatchService()))
    assert client.post("/api/batches/demo").status_code == 201
    assert client.post("/api/session/reset").status_code == 204
    assert client.post("/api/batches/demo").status_code == 201


def test_corrupt_upload_remains_visible_as_an_error_item() -> None:
    client = TestClient(create_app(BatchService()))
    uploaded = client.post("/api/batches/upload", files={"file": ("bad-image.txt", b"not an image", "text/plain")})
    assert uploaded.status_code == 201
    assert uploaded.json()["pages"][0]["error"]["code"] == "unsupported_or_corrupt"


def test_valid_upload_is_processed_without_a_second_browser_request() -> None:
    client = TestClient(create_app(BatchService()))
    ok, encoded = cv2.imencode(".png", generate_demo_documents()[0].image)
    assert ok
    uploaded = client.post("/api/batches/upload", files={"file": ("page.png", encoded.tobytes(), "image/png")})
    assert uploaded.status_code == 201
    page = uploaded.json()["pages"][0]
    assert page["status"] == "Approved"
    assert page["metrics"] is not None
    assert page["trace"]
