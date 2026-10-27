import pytest

pytest.importorskip("fastapi")
from fastapi.testclient import TestClient
from prompt_reference.server import create_app
from prompt_reference.reference_selection import DraftReferencePack
from prompt_reference.store import Store
from test_core import bundle
from test_concepts import setup_catalog


def test_combined_draft_references_preserve_legacy_clients_and_exact_selections(setup_catalog, bundle):
    database, catalog, reviews, _ = setup_catalog
    with Store(database) as store:
        store.import_bundle(bundle)
    with TestClient(create_app(database, catalog, reviews)) as client:
        form = {"concept_ids": ["space"], "supplementary": True}
        packet = client.post("/api/context", json=form).json()
        reference = {"snapshot_id": bundle.source.snapshot_id, "record_id": bundle.recipes[0].id}
        payload = dict(title="Combined", form=form, selected_ids=["cookbook:pad"], catalog_sha256=packet["catalog_sha256"], library_records=[reference])
        response = client.post("/api/drafts", json=payload)
        assert response.status_code == 201
        draft = response.json()
        assert draft["selection"]["library"]["items"][0]["record"] == bundle.recipes[0].model_dump(mode="json")
        url = f"/api/drafts/{draft['id']}/reference-pack"
        pack = DraftReferencePack.model_validate_json(client.get(url, params={"revision": 1}).text)
        assert len(pack.context.items) == 1 and pack.context.items[0].record.id == "cookbook:pad"
        assert pack.context.omitted[-1].reason == "user_deselected"
        assert pack.context.sources[pack.context.items[0].snapshot_id].license_text == "Test notice"
        assert len(pack.library.items) == 1 and not pack.library.items[0].v6_core
        assert client.get(url, params={"revision": 99}).status_code == 409
        assert client.post(f"/api/drafts/{draft['id']}/restore-context", json={}).status_code == 200
        # An older client omitting library_records must not discard pinned choices.
        legacy = {key: value for key, value in payload.items() if key != "library_records"}
        updated = client.put(f"/api/drafts/{draft['id']}", json={**legacy, "revision": 1})
        assert updated.status_code == 200 and updated.json()["selection"]["library"] == draft["selection"]["library"]
        assert client.put(f"/api/drafts/{draft['id']}", json={**payload, "revision": 1}).status_code == 409
        cleared = client.put(f"/api/drafts/{draft['id']}", json={**payload, "revision": 2, "library_records": []}).json()
        assert "library" not in cleared["selection"]


def test_library_only_drafts_retain_historical_choices_and_export_without_catalog(setup_catalog, bundle, tmp_path):
    database, _, _, _ = setup_catalog
    with Store(database) as store:
        store.import_bundle(bundle)
    with TestClient(create_app(database, tmp_path / "missing", tmp_path / "missing-reviews")) as client:
        reference = {"snapshot_id": bundle.source.snapshot_id, "record_id": bundle.recipes[0].id}
        request = dict(title="Library only", form={"intent": "A new direction"}, library_records=[reference])
        saved = client.post("/api/drafts", json=request).json()
        assert saved["id"]
        assert client.post(f"/api/drafts/{saved['id']}/restore-context", json={}).json()["packet"] is None
        replacement = bundle.model_copy(deep=True)
        replacement.source.revision = "d" * 40
        with Store(database) as store:
            store.import_bundle(replacement)
            store.activate(replacement.source.snapshot_id)
        assert client.get("/api/library/active-snapshots").json()["musai"] == replacement.source.snapshot_id
        assert client.post("/api/drafts", json=request).status_code == 409
        updated = client.put(f"/api/drafts/{saved['id']}", json={**request, "revision": 1}).json()
        assert updated["selection"] == saved["selection"]
        pack = client.get(f"/api/drafts/{saved['id']}/reference-pack").json()
        assert pack["inactive_library_records"] == [reference]
        assert pack["library"]["items"][0]["source"]["license"] == "CC0-1.0"
        assert pack["library"]["items"][0]["record"]["style_prompt"] == bundle.recipes[0].style_prompt
        copied = client.post("/api/drafts", json={**request, "copy_from": {"draft_id": saved["id"], "revision": 2}})
        assert copied.status_code == 201
        assert copied.json()["selection"] == saved["selection"]
        assert copied.json()["id"] != saved["id"]
        assert client.post("/api/drafts", json={**request, "copy_from": {"draft_id": saved["id"], "revision": 1}}).status_code == 409


def test_invalid_or_duplicated_reference_requests_cannot_forge_source_metadata(setup_catalog, bundle):
    database, catalog, reviews, _ = setup_catalog
    with Store(database) as store:
        store.import_bundle(bundle)
    with TestClient(create_app(database, catalog, reviews)) as client:
        reference = {"snapshot_id": bundle.source.snapshot_id, "record_id": bundle.recipes[0].id}
        request = dict(title="Invalid", form={})
        assert client.post("/api/drafts", json={**request, "library_records": [reference, reference]}).status_code == 400
        assert client.post("/api/drafts", json={**request, "library_records": [reference] * 51}).status_code == 422
        assert client.post("/api/drafts", json={**request, "library_records": [{**reference, "source": {"license": "made-up"}}]}).status_code == 422
        assert client.post("/api/drafts", json={**request, "library_records": [{**reference, "record_id": "missing"}]}).status_code == 404
        assert client.get("/api/drafts/missing/reference-pack").status_code == 404
