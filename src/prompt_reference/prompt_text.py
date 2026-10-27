"""Exact authored text with immutable history and pinned draft/source context."""
import hashlib
import sqlite3
from datetime import datetime, timezone
from typing import Literal
from uuid import uuid4

from pydantic import Field, model_validator

from .models import Model
from .workspace import Draft, WorkspaceConflict

PROMPT_TEXT_MIGRATION = (
    "CREATE TABLE prompt_versions (id TEXT PRIMARY KEY, draft_id TEXT NOT NULL REFERENCES workspace_drafts(id), version INTEGER NOT NULL, created_at TEXT NOT NULL, payload TEXT NOT NULL, UNIQUE(draft_id, version))",
    "CREATE TABLE prompt_heads (draft_id TEXT PRIMARY KEY REFERENCES workspace_drafts(id), version_id TEXT NOT NULL REFERENCES prompt_versions(id))",
)


def text_hash(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


class PromptText(Model):
    schema_version: Literal["1.0"] = "1.0"
    language: Literal["en"] = "en"
    style_prompt: str = Field(default="", max_length=20000)
    lyrics: str = Field(default="", max_length=100000)


class PromptVersion(Model):
    schema_version: Literal["1.0"] = "1.0"
    id: str
    draft_id: str
    version: int = Field(ge=1)
    previous_id: str | None
    based_on_id: str | None
    created_at: str
    note: str = Field(default="", max_length=2000)
    content: PromptText
    style_sha256: str
    lyrics_sha256: str
    draft_snapshot: Draft

    @model_validator(mode="after")
    def check_content(self):
        if self.style_sha256 != text_hash(self.content.style_prompt) or self.lyrics_sha256 != text_hash(self.content.lyrics):
            raise ValueError("Text content and hashes differ")
        if self.draft_snapshot.id != self.draft_id:
            raise ValueError("Text version and draft snapshot differ")
        if (self.version == 1) != (self.previous_id is None):
            raise ValueError("Text version requires its preceding history link")
        return self


class PromptVersionSummary(Model):
    id: str
    version: int
    created_at: str
    note: str
    style_sha256: str
    lyrics_sha256: str
    draft_revision: int


class PromptVersionPage(Model):
    schema_version: Literal["1.0"] = "1.0"
    draft_id: str
    head_id: str | None
    items: list[PromptVersionSummary]
    has_more: bool


class PromptTextRepository:
    def __init__(self, connection: sqlite3.Connection):
        self.connection = connection

    def head_id(self, draft_id: str) -> str | None:
        row = self.connection.execute("SELECT version_id FROM prompt_heads WHERE draft_id=?", (draft_id,)).fetchone()
        return row[0] if row else None

    def get(self, draft_id: str, id: str) -> PromptVersion:
        row = self.connection.execute("SELECT payload FROM prompt_versions WHERE draft_id=? AND id=?", (draft_id, id)).fetchone()
        if row is None:
            raise KeyError("Text version not found")
        return PromptVersion.model_validate_json(row[0])

    def list(self, draft_id: str, limit: int = 20, offset: int = 0) -> PromptVersionPage:
        if not 1 <= limit <= 100 or offset < 0:
            raise ValueError("Invalid text-history page")
        rows = self.connection.execute("SELECT payload FROM prompt_versions WHERE draft_id=? ORDER BY version DESC LIMIT ? OFFSET ?",
                                       (draft_id, limit + 1, offset)).fetchall()
        documents = [PromptVersion.model_validate_json(row[0]) for row in rows[:limit]]
        return PromptVersionPage(draft_id=draft_id, head_id=self.head_id(draft_id), has_more=len(rows) > limit,
            items=[PromptVersionSummary(id=doc.id, version=doc.version, created_at=doc.created_at, note=doc.note,
                style_sha256=doc.style_sha256, lyrics_sha256=doc.lyrics_sha256, draft_revision=doc.draft_snapshot.revision) for doc in documents])

    def save(self, draft: Draft, content: PromptText, expected_head_id: str | None,
             note: str = "", based_on_id: str | None = None) -> PromptVersion:
        # Lock before checking either revision, so draft/source context and text
        # history cannot change between the checks and this append.
        with self.connection:
            self.connection.execute("BEGIN IMMEDIATE")
            row = self.connection.execute("SELECT payload FROM workspace_drafts WHERE id=?", (draft.id,)).fetchone()
            if row is None or Draft.model_validate_json(row[0]) != draft:
                raise WorkspaceConflict("Saved draft changed. Refresh its context before saving text.")
            actual_head = self.head_id(draft.id)
            if actual_head != expected_head_id:
                raise WorkspaceConflict("Text history changed in another window. Review the latest version before saving.")
            previous = self.get(draft.id, actual_head) if actual_head else None
            if based_on_id:
                self.get(draft.id, based_on_id)
            document = PromptVersion(id=str(uuid4()), draft_id=draft.id,
                version=previous.version + 1 if previous else 1, previous_id=actual_head, based_on_id=based_on_id,
                created_at=datetime.now(timezone.utc).isoformat(), note=note, content=content.model_copy(deep=True),
                style_sha256=text_hash(content.style_prompt), lyrics_sha256=text_hash(content.lyrics), draft_snapshot=draft.model_copy(deep=True))
            self.connection.execute("INSERT INTO prompt_versions VALUES (?, ?, ?, ?, ?)",
                (document.id, draft.id, document.version, document.created_at, document.model_dump_json()))
            self.connection.execute("INSERT INTO prompt_heads VALUES (?, ?) ON CONFLICT(draft_id) DO UPDATE SET version_id=excluded.version_id",
                (draft.id, document.id))
        return document
