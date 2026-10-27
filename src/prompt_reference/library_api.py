"""Local HTTP adapter for the independent reference library."""
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import Response

from .library import LibraryPage, LibraryScope, RecordKind, RecordRequest, search_library, export_record


def library_router(connect):
    router = APIRouter(prefix="/api/library")

    @router.get("/active-snapshots", response_model=dict[str, str])
    def active_snapshots():
        with connect() as store:
            return store.active_snapshots()

    @router.get("", response_model=LibraryPage)
    def search(q: str = Query(default="", max_length=300), scope: LibraryScope = "all",
               kind: RecordKind | None = None, limit: int = Query(default=20, ge=1, le=100)):
        with connect() as store:
            return search_library(store, q, scope, kind, limit)

    @router.post("/export")
    def export(request: RecordRequest):
        with connect() as store:
            try:
                bundle = export_record(store, request)
            except KeyError as error:
                raise HTTPException(404, str(error.args[0])) from error
            except ValueError as error:
                raise HTTPException(409, str(error)) from error
            return Response(bundle.model_dump_json(indent=2), media_type="application/json",
                headers={"Content-Disposition": 'attachment; filename="reference-record.json"'})

    return router
