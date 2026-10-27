"""Local web adapter. Reference/selection logic stays in the core modules."""
from pathlib import Path
from typing import Literal

from fastapi import FastAPI, HTTPException
from fastapi.responses import Response
from fastapi.staticfiles import StaticFiles
from pydantic import Field

from .concepts import CatalogService, ContextPacket, render_context, select_items
from .models import Model
from .store import Store
from .workspace_api import workspace_router
from .listening_api import listening_router
from .library_api import library_router
from .prompt_text_api import prompt_text_router


class ContextRequest(Model):
    concept_ids: list[str] = Field(min_length=1, max_length=12)
    intent: str = Field(default="", max_length=4000)
    target_model: Literal["v6", "v6-wild", "v6-mini"] = "v6"
    supplementary: bool = False
    limit: int = Field(default=24, ge=1, le=100)


class ExportRequest(ContextRequest):
    selected_ids: list[str] = Field(min_length=1, max_length=100)
    format: Literal["json", "markdown"] = "markdown"


def create_app(database: Path, catalog: Path, reviews: Path, frontend: Path | None = None) -> FastAPI:
    app = FastAPI(title="Cowabunga AI", version="0.11.0")

    def service(store: Store):
        try:
            return CatalogService(store, catalog, reviews)
        except (ValueError, OSError) as error:
            raise HTTPException(409, str(error)) from error

    def connect():
        if not database.is_file():
            raise HTTPException(503, "Reference database is missing. Import the source selections first.")
        return Store(database)

    def build(request: ContextRequest) -> ContextPacket:
        with connect() as store:
            try:
                return service(store).build_context(request.concept_ids, request.intent,
                    request.target_model, request.supplementary, request.limit)
            except ValueError as error:
                raise HTTPException(409 if "inactive" in str(error) else 400, str(error)) from error

    @app.get("/api/meta")
    def meta():
        with connect() as store:
            loaded = service(store)
            return {"app": "prompt-reference", "version": "0.11.0", "concepts": len(loaded.catalog.concepts),
                    "core": store.stats(v6_core=True), "corpus": store.stats()}

    @app.get("/api/concepts")
    def concepts(q: str = ""):
        with connect() as store:
            return service(store).find(q)

    @app.post("/api/context", response_model=ContextPacket)
    def context(request: ContextRequest):
        return build(request)

    @app.post("/api/export")
    def export(request: ExportRequest):
        try:
            packet = select_items(build(request), request.selected_ids)
        except ValueError as error:
            raise HTTPException(400, str(error)) from error
        if request.format == "markdown":
            return Response(render_context(packet), media_type="text/markdown",
                headers={"Content-Disposition": 'attachment; filename="prompt-context.md"'})
        return Response(packet.model_dump_json(indent=2), media_type="application/json",
            headers={"Content-Disposition": 'attachment; filename="prompt-context.json"'})

    app.include_router(workspace_router(connect, service))
    app.include_router(listening_router(connect))
    app.include_router(library_router(connect))
    app.include_router(prompt_text_router(connect))

    if frontend and frontend.is_dir():
        app.mount("/", StaticFiles(directory=frontend, html=True), name="workbench")
    else:
        @app.get("/")
        def missing_build():
            raise HTTPException(503, "Web interface is not built. Run npm ci and npm run build in web/.")
    return app
