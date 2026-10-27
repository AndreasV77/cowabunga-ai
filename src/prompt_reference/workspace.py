"""Provider-independent explicit preferences and revisioned local drafts.

The repository stores JSON documents without knowing Suno, source catalogs or UI
controls. Application adapters validate their own form/selection contents.
"""
import sqlite3
from datetime import datetime, timezone
from typing import Literal
from uuid import uuid4

from pydantic import Field, JsonValue, field_validator

from .models import Model

WORKSPACE_MIGRATION = (
    "CREATE TABLE workspace_preferences (namespace TEXT NOT NULL, scope TEXT NOT NULL, subject_id TEXT NOT NULL, revision INTEGER NOT NULL, payload TEXT NOT NULL, PRIMARY KEY(namespace, scope, subject_id))",
    "CREATE TABLE workspace_drafts (id TEXT PRIMARY KEY, namespace TEXT NOT NULL, revision INTEGER NOT NULL, updated_at TEXT NOT NULL, payload TEXT NOT NULL)",
    "CREATE INDEX workspace_drafts_by_namespace ON workspace_drafts(namespace, updated_at)",
)


class WorkspaceConflict(ValueError):
    """The saved revision changed; never overwrite it silently."""


class Preferences(Model):
    schema_version: Literal["1.0"] = "1.0"
    namespace: str = Field(min_length=1, max_length=80)
    scope: Literal["user", "project", "artist"]
    subject_id: str = Field(min_length=1, max_length=128)
    revision: int = Field(ge=1)
    updated_at: str
    values: dict[str, JsonValue]


class Draft(Model):
    schema_version: Literal["1.0"] = "1.0"
    id: str
    namespace: str = Field(min_length=1, max_length=80)
    title: str = Field(min_length=1, max_length=120)
    revision: int = Field(ge=1)
    created_at: str
    updated_at: str
    form: dict[str, JsonValue]
    selection: dict[str, JsonValue] | None = None

    @field_validator("title")
    @classmethod
    def nonblank_title(cls, value):
        value = value.strip()
        if not value:
            raise ValueError("Draft name must not be blank")
        return value


class WorkspaceRepository:
    def __init__(self, connection: sqlite3.Connection):
        self.connection = connection

    def get_preferences(self, namespace: str, scope: str, subject_id: str) -> Preferences | None:
        row = self.connection.execute("SELECT payload FROM workspace_preferences WHERE namespace=? AND scope=? AND subject_id=?",
                                      (namespace, scope, subject_id)).fetchone()
        return Preferences.model_validate_json(row[0]) if row else None

    def save_preferences(self, namespace: str, scope: str, subject_id: str,
                         values: dict, expected_revision: int) -> Preferences:
        if expected_revision < 0:
            raise ValueError("Invalid preference revision")
        document = Preferences(namespace=namespace, scope=scope, subject_id=subject_id,
            revision=expected_revision + 1, updated_at=datetime.now(timezone.utc).isoformat(), values=values)
        try:
            with self.connection:
                if expected_revision == 0:
                    self.connection.execute("INSERT INTO workspace_preferences VALUES (?, ?, ?, ?, ?)",
                        (namespace, scope, subject_id, document.revision, document.model_dump_json()))
                else:
                    result = self.connection.execute("UPDATE workspace_preferences SET revision=?, payload=? WHERE namespace=? AND scope=? AND subject_id=? AND revision=?",
                        (document.revision, document.model_dump_json(), namespace, scope, subject_id, expected_revision))
                    if result.rowcount != 1:
                        raise WorkspaceConflict("Defaults changed in another window. Reload before saving again.")
        except sqlite3.IntegrityError as error:
            raise WorkspaceConflict("Defaults already exist. Reload before saving again.") from error
        return document

    def list_drafts(self, namespace: str, limit: int = 100) -> list[Draft]:
        if not 1 <= limit <= 500:
            raise ValueError("Draft limit must be between 1 and 500")
        return [Draft.model_validate_json(row[0]) for row in self.connection.execute(
            "SELECT payload FROM workspace_drafts WHERE namespace=? ORDER BY updated_at DESC, id LIMIT ?", (namespace, limit))]

    def get_draft(self, namespace: str, id: str) -> Draft:
        row = self.connection.execute("SELECT payload FROM workspace_drafts WHERE namespace=? AND id=?", (namespace, id)).fetchone()
        if row is None:
            raise KeyError("Draft not found")
        return Draft.model_validate_json(row[0])

    def create_draft(self, namespace: str, title: str, form: dict, selection: dict | None) -> Draft:
        timestamp = datetime.now(timezone.utc).isoformat()
        document = Draft(id=str(uuid4()), namespace=namespace, title=title, revision=1,
                         created_at=timestamp, updated_at=timestamp, form=form, selection=selection)
        with self.connection:
            self.connection.execute("INSERT INTO workspace_drafts VALUES (?, ?, ?, ?, ?)",
                (document.id, namespace, document.revision, document.updated_at, document.model_dump_json()))
        return document

    def update_draft(self, namespace: str, id: str, title: str, form: dict,
                     selection: dict | None, expected_revision: int) -> Draft:
        old = self.get_draft(namespace, id)
        document = Draft(id=id, namespace=namespace, title=title, revision=expected_revision + 1,
            created_at=old.created_at, updated_at=datetime.now(timezone.utc).isoformat(), form=form, selection=selection)
        with self.connection:
            result = self.connection.execute("UPDATE workspace_drafts SET revision=?, updated_at=?, payload=? WHERE id=? AND namespace=? AND revision=?",
                (document.revision, document.updated_at, document.model_dump_json(), id, namespace, expected_revision))
            if result.rowcount != 1:
                raise WorkspaceConflict("Draft changed in another window. Reload it or save as a new draft.")
        return document
