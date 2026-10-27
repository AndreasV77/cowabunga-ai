"""Application endpoints for authored text; no model-provider calls."""
from fastapi import APIRouter, HTTPException, Query
from pydantic import Field

from .models import Model
from .prompt_text import PromptText, PromptVersion, PromptVersionPage, PromptTextRepository
from .workspace import WorkspaceRepository, WorkspaceConflict
from .workspace_api import NAMESPACE


class SavePromptText(Model):
    draft_revision: int = Field(ge=1)
    expected_head_id: str | None = Field(default=None, min_length=1, max_length=128)
    based_on_id: str | None = Field(default=None, min_length=1, max_length=128)
    content: PromptText
    note: str = Field(default="", max_length=2000)


def prompt_text_router(connect):
    router = APIRouter(prefix="/api/drafts/{draft_id}/prompt-versions")

    def parent(store, draft_id):
        try:
            return WorkspaceRepository(store.connection).get_draft(NAMESPACE, draft_id)
        except KeyError as error:
            raise HTTPException(404, "Draft not found") from error

    @router.get("", response_model=PromptVersionPage)
    def history(draft_id: str, limit: int = Query(default=20, ge=1, le=100), offset: int = Query(default=0, ge=0)):
        with connect() as store:
            parent(store, draft_id)
            return PromptTextRepository(store.connection).list(draft_id, limit, offset)

    @router.get("/{id}", response_model=PromptVersion)
    def version(draft_id: str, id: str):
        with connect() as store:
            parent(store, draft_id)
            try:
                return PromptTextRepository(store.connection).get(draft_id, id)
            except KeyError as error:
                raise HTTPException(404, str(error.args[0])) from error

    @router.post("", response_model=PromptVersion, status_code=201)
    def save(draft_id: str, request: SavePromptText):
        with connect() as store:
            draft = parent(store, draft_id)
            if draft.revision != request.draft_revision:
                raise HTTPException(409, "Saved draft changed. Refresh its context before saving text.")
            try:
                return PromptTextRepository(store.connection).save(draft, request.content,
                    request.expected_head_id, request.note, request.based_on_id)
            except WorkspaceConflict as error:
                raise HTTPException(409, str(error)) from error
            except KeyError as error:
                raise HTTPException(404, str(error.args[0])) from error

    return router
