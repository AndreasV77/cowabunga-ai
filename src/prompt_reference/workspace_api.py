"""Music-workbench adapter for the reusable local document repository."""
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import Response
from pydantic import Field
from typing import Literal

from .models import Model
from .workspace import WorkspaceRepository, WorkspaceConflict
from .library import RecordRequest
from .reference_selection import capture_library, saved_library, build_reference_pack

NAMESPACE = "prompt-reference"


class DefaultsRequest(Model):
    revision: int = Field(default=0, ge=0)
    target_model: Literal["v6", "v6-wild", "v6-mini"] = "v6"
    supplementary: bool = False


class DraftForm(Model):
    concept_ids: list[str] = Field(default_factory=list, max_length=12)
    intent: str = Field(default="", max_length=4000)
    target_model: Literal["v6", "v6-wild", "v6-mini"] = "v6"
    supplementary: bool = False
    limit: int = Field(default=24, ge=1, le=100)


class DraftCopy(Model):
    draft_id: str = Field(min_length=1, max_length=128)
    revision: int = Field(ge=1)


class DraftRequest(Model):
    title: str = Field(min_length=1, max_length=120)
    form: DraftForm
    selected_ids: list[str] | None = Field(default=None, max_length=100)
    catalog_sha256: str | None = None
    revision: int = Field(default=0, ge=0)
    library_records: list[RecordRequest] | None = Field(default=None, max_length=50)
    copy_from: DraftCopy | None = None


def workspace_router(connect, service):
    router = APIRouter(prefix="/api")

    def packet_for(store, form):
        try:
            return service(store).build_context(form.concept_ids, form.intent,
                form.target_model, form.supplementary, form.limit)
        except ValueError as error:
            raise HTTPException(409, str(error)) from error

    def selection_for(store, request, previous=None):
        selection = {}
        if request.selected_ids is not None:
            packet = packet_for(store, request.form)
            if packet.catalog_sha256 != request.catalog_sha256:
                raise HTTPException(409, "References changed. Rebuild the selection before saving it.")
            if not set(request.selected_ids) <= {item.record.id for item in packet.items}:
                raise HTTPException(400, "Saved selection contains unavailable candidates")
            selection = {"selected_ids": sorted(set(request.selected_ids)), "packet": packet.model_dump(mode="json")}
        try:
            library = capture_library(store, request.library_records, saved_library(previous))
        except KeyError as error:
            raise HTTPException(404, str(error.args[0])) from error
        except ValueError as error:
            raise HTTPException(409 if "no longer active" in str(error) else 400, str(error)) from error
        if library.items:
            selection["library"] = library.model_dump(mode="json")
        return selection or None

    def read_draft(repository, id):
        try:
            return repository.get_draft(NAMESPACE, id)
        except KeyError as error:
            raise HTTPException(404, "Draft not found") from error

    @router.get("/preferences")
    def preferences():
        with connect() as store:
            saved = WorkspaceRepository(store.connection).get_preferences(NAMESPACE, "user", "local")
            return {"revision": saved.revision if saved else 0,
                    "target_model": saved.values["target_model"] if saved else "v6",
                    "supplementary": saved.values["supplementary"] if saved else False,
                    "prompt_language": "en"}

    @router.put("/preferences")
    def save_preferences(request: DefaultsRequest):
        with connect() as store:
            try:
                saved = WorkspaceRepository(store.connection).save_preferences(NAMESPACE, "user", "local",
                    {"target_model": request.target_model, "supplementary": request.supplementary}, request.revision)
            except WorkspaceConflict as error:
                raise HTTPException(409, str(error)) from error
            return {"revision": saved.revision, **saved.values, "prompt_language": "en"}

    @router.get("/drafts")
    def drafts():
        with connect() as store:
            return [{"id": draft.id, "title": draft.title, "revision": draft.revision,
                     "updated_at": draft.updated_at} for draft in WorkspaceRepository(store.connection).list_drafts(NAMESPACE)]

    @router.get("/drafts/{id}")
    def draft(id: str):
        with connect() as store:
            return read_draft(WorkspaceRepository(store.connection), id)

    @router.post("/drafts", status_code=201)
    def create_draft(request: DraftRequest):
        with connect() as store:
            previous = None
            if request.copy_from:
                previous = read_draft(WorkspaceRepository(store.connection), request.copy_from.draft_id)
                if previous.revision != request.copy_from.revision:
                    raise HTTPException(409, "Source draft changed. Reopen it before saving a copy.")
            selection = selection_for(store, request, previous)
            try:
                return WorkspaceRepository(store.connection).create_draft(NAMESPACE, request.title,
                    request.form.model_dump(mode="json"), selection)
            except ValueError as error:
                raise HTTPException(400, str(error)) from error

    @router.put("/drafts/{id}")
    def update_draft(id: str, request: DraftRequest):
        with connect() as store:
            if request.copy_from:
                raise HTTPException(400, "Copy sources apply only when creating a new draft.")
            repository = WorkspaceRepository(store.connection)
            previous = read_draft(repository, id)
            selection = selection_for(store, request, previous)
            try:
                return repository.update_draft(NAMESPACE, id, request.title,
                    request.form.model_dump(mode="json"), selection, request.revision)
            except WorkspaceConflict as error:
                raise HTTPException(409, str(error)) from error
            except ValueError as error:
                raise HTTPException(400, str(error)) from error

    @router.post("/drafts/{id}/restore-context")
    def restore(id: str):
        with connect() as store:
            saved = read_draft(WorkspaceRepository(store.connection), id)
            if not saved.selection or not saved.selection.get("packet"):
                return {"packet": None, "selected_ids": []}
            packet = packet_for(store, DraftForm.model_validate(saved.form))
            if packet.model_dump(mode="json") != saved.selection["packet"]:
                raise HTTPException(409, "References changed. Your direction was restored; rebuild its selection.")
            return {"packet": packet, "selected_ids": saved.selection["selected_ids"]}

    @router.get("/drafts/{id}/reference-pack")
    def export_references(id: str, revision: int | None = Query(default=None, ge=1)):
        with connect() as store:
            saved = read_draft(WorkspaceRepository(store.connection), id)
            if revision is not None and revision != saved.revision:
                raise HTTPException(409, "Saved draft changed. Reopen it before exporting.")
            pack = build_reference_pack(store, saved)
            return Response(pack.model_dump_json(indent=2), media_type="application/json",
                headers={"Content-Disposition": 'attachment; filename="draft-references.json"'})

    return router
