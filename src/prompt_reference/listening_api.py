"""HTTP adapter for local, draft-bound listening reports."""
from fastapi import APIRouter, HTTPException
from pydantic import Field

from .listening import ListeningAssessment, ListeningDocument, ListeningRepository
from .models import Model
from .workspace import WorkspaceRepository, WorkspaceConflict
from .workspace_api import NAMESPACE


class ListeningRequest(Model):
    title: str = Field(min_length=1, max_length=120)
    draft_revision: int = Field(ge=1)
    revision: int = Field(default=0, ge=0)
    assessment: ListeningAssessment


def listening_router(connect):
    router = APIRouter(prefix="/api/drafts/{draft_id}/listening")

    def repositories(store, draft_id):
        workspace = WorkspaceRepository(store.connection)
        try:
            parent = workspace.get_draft(NAMESPACE, draft_id)
        except KeyError as error:
            raise HTTPException(404, "Draft not found") from error
        return ListeningRepository(workspace, draft_id), parent

    def read(repository, id):
        try:
            return repository.get(id)
        except KeyError as error:
            raise HTTPException(404, "Listening report not found") from error

    @router.get("", response_model=list[ListeningDocument])
    def list_reports(draft_id: str):
        with connect() as store:
            repository, _ = repositories(store, draft_id)
            return repository.list()

    @router.post("", response_model=ListeningDocument, status_code=201)
    def create(draft_id: str, request: ListeningRequest):
        with connect() as store:
            repository, parent = repositories(store, draft_id)
            if parent.revision != request.draft_revision:
                raise HTTPException(409, "Draft changed. Reload it before attaching a new report.")
            try:
                return repository.create(request.title, request.assessment, parent)
            except ValueError as error:
                raise HTTPException(400, str(error)) from error

    @router.put("/{id}", response_model=ListeningDocument)
    def update(draft_id: str, id: str, request: ListeningRequest):
        with connect() as store:
            repository, _ = repositories(store, draft_id)
            old = read(repository, id)
            if old.draft_snapshot.revision != request.draft_revision:
                raise HTTPException(409, "A listening report must retain its original draft snapshot.")
            try:
                return repository.update(id, request.title, request.assessment, request.revision)
            except WorkspaceConflict as error:
                raise HTTPException(409, str(error)) from error
            except ValueError as error:
                raise HTTPException(400, str(error)) from error

    @router.get("/{id}", response_model=ListeningDocument)
    def get(draft_id: str, id: str):
        with connect() as store:
            repository, _ = repositories(store, draft_id)
            return read(repository, id)

    return router
