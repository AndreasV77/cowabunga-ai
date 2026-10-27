"""Search and export active reference records without concept-catalog coupling."""
from typing import Literal

from pydantic import Field, model_validator

from .models import Bundle, Model, Recipe, ReferenceEntry, Source
from .store import Store
from .search import SearchPlan, plan_query

RecordKind = Literal["recipe", "term", "phrase", "guidance"]
LibraryScope = Literal["all", "v6_core"]


class LibraryHit(Model):
    snapshot_id: str
    kind: RecordKind
    v6_core: bool
    source: Source
    record: Recipe | ReferenceEntry

    @model_validator(mode="after")
    def check_identity(self):
        if self.source.snapshot_id != self.snapshot_id:
            raise ValueError("Library source snapshot does not match")
        kind = "recipe" if isinstance(self.record, Recipe) else self.record.kind
        if self.kind != kind:
            raise ValueError("Library record kind does not match")
        expected_core = self.source.orientation == "v6_native" and self.record.evidence is not None and self.record.evidence.model_basis == "v6_targeted"
        if self.v6_core != expected_core:
            raise ValueError("Library V6 classification does not match source evidence")
        return self


class LibraryPage(Model):
    schema_version: Literal["1.0", "1.1"] = "1.1"
    query: str
    scope: LibraryScope
    kind: RecordKind | None
    limit: int
    has_more: bool
    items: list[LibraryHit]
    search_plan: SearchPlan | None = None


class RecordRequest(Model):
    snapshot_id: str = Field(min_length=1, max_length=300)
    record_id: str = Field(min_length=1, max_length=200)


def search_library(store: Store, query: str, scope: LibraryScope = "all", kind: RecordKind | None = None,
                   limit: int = 20, expand: bool = True) -> LibraryPage:
    if scope not in ("all", "v6_core"):
        raise ValueError("Unknown library scope")
    if not 1 <= limit <= 100:
        raise ValueError("Library limit must be between 1 and 100")
    if len(query) > 300:
        raise ValueError("Library query is too long")
    rows = store.search(query, limit=limit + 1, kind=kind, v6_core=scope == "v6_core", expand=expand)
    items = [LibraryHit(snapshot_id=row["snapshot_id"], kind=row["kind"], v6_core=row["v6_core"],
        source=Source.model_validate(row["source"]), record=row.get("recipe") or row["entry"]) for row in rows[:limit]]
    return LibraryPage(query=query.strip(), scope=scope, kind=kind, limit=limit,
                       has_more=len(rows) > limit, items=items, search_plan=plan_query(query, expand=expand))


def export_record(store: Store, request: RecordRequest) -> Bundle:
    if request.snapshot_id not in store.active_snapshots().values():
        raise ValueError("Source snapshot is no longer active. Search again before exporting.")
    original = store.export(request.snapshot_id)
    recipes = [record for record in original.recipes if record.id == request.record_id]
    entries = [record for record in original.entries if record.id == request.record_id]
    if not recipes and not entries:
        raise KeyError("Reference record not found in this source snapshot")
    return Bundle(source=original.source, recipes=recipes, entries=entries)
