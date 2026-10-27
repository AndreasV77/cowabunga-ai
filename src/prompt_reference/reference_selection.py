"""Pinned, explicit library choices and portable saved-draft reference packs."""
from typing import Literal

from pydantic import Field, JsonValue, model_validator

from .concepts import ContextPacket, select_items
from .library import LibraryHit, RecordRequest, export_record
from .models import Model
from .store import Store
from .workspace import Draft


class LibrarySelection(Model):
    schema_version: Literal["1.0"] = "1.0"
    items: list[LibraryHit] = Field(default_factory=list, max_length=50)

    @model_validator(mode="after")
    def unique_records(self):
        keys = [(item.snapshot_id, item.record.id) for item in self.items]
        if len(keys) != len(set(keys)):
            raise ValueError("A reference snapshot/record pair may only be selected once")
        return self


def saved_library(draft: Draft | None) -> LibrarySelection:
    payload = draft.selection.get("library") if draft and draft.selection else None
    return LibrarySelection.model_validate(payload) if payload is not None else LibrarySelection()


def capture_library(store: Store, requests: list[RecordRequest] | None,
                    retained: LibrarySelection | None = None) -> LibrarySelection:
    retained = retained or LibrarySelection()
    if requests is None:
        return retained.model_copy(deep=True)
    if len(requests) > 50:
        raise ValueError("Keep at most 50 library references per draft")
    previous = {(item.snapshot_id, item.record.id): item for item in retained.items}
    items = []
    for request in requests:
        key = (request.snapshot_id, request.record_id)
        if key in previous:
            # Existing saved choices retain their original record and source,
            # including after source deactivation. New picks must be active.
            items.append(previous[key].model_copy(deep=True))
            continue
        bundle = export_record(store, request)
        record = (bundle.recipes or bundle.entries)[0]
        core = bundle.source.orientation == "v6_native" and record.evidence is not None and record.evidence.model_basis == "v6_targeted"
        items.append(LibraryHit(snapshot_id=request.snapshot_id,
            kind="recipe" if bundle.recipes else record.kind, v6_core=core, source=bundle.source, record=record))
    return LibrarySelection(items=items)


class DraftReferencePack(Model):
    schema_version: Literal["1.0"] = "1.0"
    draft_id: str
    title: str
    revision: int
    form: dict[str, JsonValue]
    context: ContextPacket | None
    library: LibrarySelection
    inactive_library_records: list[RecordRequest]
    inactive_context_snapshots: list[str]
    independently_verified: Literal[False] = False


def build_reference_pack(store: Store, draft: Draft) -> DraftReferencePack:
    library = saved_library(draft)
    active = set(store.active_snapshots().values())
    selection = draft.selection or {}
    packet = ContextPacket.model_validate(selection["packet"]) if selection.get("packet") else None
    ids = selection.get("selected_ids") or []
    context = select_items(packet, ids) if packet is not None and ids else None
    return DraftReferencePack(draft_id=draft.id, title=draft.title, revision=draft.revision,
        form=draft.form, context=context, library=library,
        inactive_library_records=[RecordRequest(snapshot_id=item.snapshot_id, record_id=item.record.id)
            for item in library.items if item.snapshot_id not in active],
        inactive_context_snapshots=sorted({item.snapshot_id for item in context.items if item.snapshot_id not in active}) if context else [])
