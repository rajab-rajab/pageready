"""FastAPI boundary for the local PageReady Vision demo."""

from __future__ import annotations

import os
from pathlib import Path

from fastapi import FastAPI, File, HTTPException, Response, UploadFile
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from .schemas import OverrideRequest
from .service import BatchService


def create_app(service: BatchService | None = None) -> FastAPI:
    service = service or BatchService()
    app = FastAPI(title="PageReady Vision", version="0.2.0")

    def api_error(error: Exception) -> HTTPException:
        return HTTPException(status_code=400, detail=str(error))

    @app.post("/api/batches/demo", status_code=201)
    def create_demo_batch() -> dict[str, object]:
        try:
            return service.public_batch(service.create_demo_batch())
        except ValueError as error:
            raise api_error(error) from error

    @app.post("/api/session/reset", status_code=204)
    def reset_session() -> Response:
        service.reset_session()
        return Response(status_code=204)

    @app.post("/api/batches/upload", status_code=201)
    async def upload_to_batch(file: UploadFile = File(...)) -> dict[str, object]:
        try:
            service.add_upload(file.filename or "unnamed-upload", await file.read())
            # Processing is server-driven so an accepted upload never depends on
            # a browser-side follow-up request to leave the queued state.
            return service.public_batch(service.process())
        except ValueError as error:
            raise api_error(error) from error

    @app.post("/api/batches/{batch_id}/process")
    def process_batch(batch_id: str) -> dict[str, object]:
        try:
            batch = service.get_batch()
            if batch.id != batch_id:
                raise KeyError("Batch not found.")
            return service.public_batch(service.process())
        except (ValueError, KeyError) as error:
            raise api_error(error) from error

    @app.get("/api/batches/{batch_id}")
    def get_batch(batch_id: str) -> dict[str, object]:
        try:
            batch = service.get_batch()
            if batch.id != batch_id:
                raise KeyError("Batch not found.")
            return service.public_batch(batch)
        except (ValueError, KeyError) as error:
            raise api_error(error) from error

    @app.post("/api/pages/{page_id}/approve-warning")
    def approve_warning(page_id: str, request: OverrideRequest) -> dict[str, object]:
        try:
            return service.approve_with_warning(page_id, request.note).model_dump(mode="json")
        except (ValueError, KeyError) as error:
            raise api_error(error) from error

    @app.delete("/api/pages/{page_id}", status_code=204)
    def remove_page(page_id: str) -> Response:
        try:
            service.remove_page(page_id)
            return Response(status_code=204)
        except (ValueError, KeyError) as error:
            raise api_error(error) from error

    @app.get("/api/batches/{batch_id}/audit")
    def audit(batch_id: str) -> JSONResponse:
        try:
            batch = service.get_batch()
            if batch.id != batch_id:
                raise KeyError("Batch not found.")
            export = service.audit_export().model_dump(mode="json")
            return JSONResponse(export, headers={"Content-Disposition": "attachment; filename=pageready-audit.json"})
        except (ValueError, KeyError) as error:
            raise api_error(error) from error

    @app.delete("/api/batches/{batch_id}", status_code=204)
    def clear_batch(batch_id: str) -> Response:
        try:
            batch = service.get_batch()
            if batch.id != batch_id:
                raise KeyError("Batch not found.")
            service.clear()
            return Response(status_code=204)
        except (ValueError, KeyError) as error:
            raise api_error(error) from error

    @app.get("/api/images/{image_id}")
    def get_image(image_id: str) -> Response:
        try:
            return Response(content=service.get_image(image_id), media_type="image/png")
        except (ValueError, KeyError) as error:
            raise HTTPException(status_code=404, detail=str(error)) from error

    frontend_dir = Path(os.environ.get("PAGEREADY_FRONTEND_DIR", Path.cwd() / "frontend" / "dist"))
    assets_dir = frontend_dir / "assets"
    if assets_dir.is_dir():
        app.mount("/assets", StaticFiles(directory=assets_dir), name="frontend-assets")

        @app.get("/", include_in_schema=False)
        def console() -> FileResponse:
            return FileResponse(frontend_dir / "index.html")

    return app


app = create_app()
