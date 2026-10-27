import json
from pathlib import Path

import pytest

from prompt_reference.reference_selection import LibrarySelection, DraftReferencePack, capture_library, saved_library, build_reference_pack
from prompt_reference.library import RecordRequest
from prompt_reference.workspace import WorkspaceRepository
from prompt_reference.store import Store
from test_core import bundle


def test_pinned_library_selection_survives_deactivation_and_exports_original_metadata(tmp_path, bundle):
    database = tmp_path / "reference-selection.sqlite3"
    request = RecordRequest(snapshot_id=bundle.source.snapshot_id, record_id=bundle.recipes[0].id)
    with Store(database) as store:
        store.import_bundle(bundle)
        selected = capture_library(store, [request])
        assert not selected.items[0].v6_core
        assert selected.items[0].record == bundle.recipes[0]
        parent = WorkspaceRepository(store.connection).create_draft("prompt-reference", "Song", {}, {"library": selected.model_dump(mode="json")})
        next_version = bundle.model_copy(deep=True)
        next_version.source.revision = "c" * 40
        next_version.recipes[0].style_prompt = "Different wording"
        store.import_bundle(next_version)
        store.activate(next_version.source.snapshot_id)
        assert capture_library(store, [request], saved_library(parent)) == selected
        with pytest.raises(ValueError, match="no longer active"):
            capture_library(store, [request])
        assert capture_library(store, None, selected) == selected
        assert capture_library(store, [], selected).items == []
        with pytest.raises(ValueError, match="once"):
            capture_library(store, [request, request], selected)
        with pytest.raises(ValueError, match="50"):
            capture_library(store, [request] * 51, selected)
        pack = build_reference_pack(store, parent)
        assert pack.library == selected
        assert pack.inactive_library_records == [request]
        assert pack.context is None and pack.inactive_context_snapshots == []
        assert DraftReferencePack.model_validate_json(pack.model_dump_json()) == pack
    with Store(database) as store:
        assert build_reference_pack(store, WorkspaceRepository(store.connection).get_draft("prompt-reference", parent.id)) == pack


@pytest.mark.parametrize("name, contract", [("library-selection", LibrarySelection), ("draft-references", DraftReferencePack)])
def test_selection_contract_schemas_are_current(name, contract):
    path = Path(__file__).resolve().parents[1] / "schemas" / f"{name}.schema.json"
    assert json.loads(path.read_text(encoding="utf-8")) == contract.model_json_schema()
