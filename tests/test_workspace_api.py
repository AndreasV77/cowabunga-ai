import pytest

pytest.importorskip("fastapi")
from fastapi.testclient import TestClient
from prompt_reference.server import create_app
from prompt_reference.store import Store
from test_concepts import setup_catalog


def test_explicit_defaults_do_not_write_on_read_and_reject_stale_writes(setup_catalog):
    database, catalog, reviews, _ = setup_catalog
    with TestClient(create_app(database, catalog, reviews)) as client:
        defaults = client.get("/api/preferences").json()
        assert defaults == dict(revision=0, target_model="v6", supplementary=False, prompt_language="en")
        with Store(database) as store:
            assert store.connection.execute("SELECT COUNT(*) FROM workspace_preferences").fetchone()[0] == 0
        request = dict(revision=0, target_model="v6-wild", supplementary=True)
        assert client.put("/api/preferences", json=request).json()["revision"] == 1
        assert client.put("/api/preferences", json=request).status_code == 409
        assert client.put("/api/preferences", json={**request, "target_model": "v5"}).status_code == 422
    with TestClient(create_app(database, catalog, reviews)) as client:
        assert client.get("/api/preferences").json()["target_model"] == "v6-wild"


def test_drafts_roundtrip_selection_provenance_and_conflicts(setup_catalog):
    database, catalog, reviews, _ = setup_catalog
    with TestClient(create_app(database, catalog, reviews)) as client:
        form = dict(concept_ids=["space"], intent="Close singer", target_model="v6", supplementary=True, limit=24)
        packet = client.post("/api/context", json=form).json()
        request = dict(title="Intimate vocal", form=form, selected_ids=["cookbook:pad"], catalog_sha256=packet["catalog_sha256"])
        response = client.post("/api/drafts", json=request)
        assert response.status_code == 201
        draft = response.json()
        id = draft["id"]
        assert draft["selection"]["packet"] == packet
        assert client.get(f"/api/drafts/{id}").json() == draft
        assert client.get("/api/drafts").json()[0]["id"] == id
        restored = client.post(f"/api/drafts/{id}/restore-context", json={}).json()
        assert restored == dict(packet=packet, selected_ids=["cookbook:pad"])
        updated = client.put(f"/api/drafts/{id}", json={**request, "revision": 1, "title": "Updated"})
        assert updated.json()["revision"] == 2
        assert client.put(f"/api/drafts/{id}", json={**request, "revision": 1}).status_code == 409
        assert client.get(f"/api/drafts/{id}").json()["title"] == "Updated"
        # Any catalog change requires deliberate reassembly; historic wording survives.
        catalog.write_bytes(catalog.read_bytes() + b"\n")
        assert client.post(f"/api/drafts/{id}/restore-context", json={}).status_code == 409
        assert client.get(f"/api/drafts/{id}").json()["selection"]["packet"] == packet
        assert client.post("/api/drafts", json=request).status_code == 409


def test_direction_only_drafts_empty_selections_and_invalid_requests(setup_catalog):
    database, catalog, reviews, _ = setup_catalog
    with TestClient(create_app(database, catalog, reviews)) as client:
        draft = client.post("/api/drafts", json=dict(title="Sketch", form=dict(intent="Rhythm keeps moving"))).json()
        assert draft["selection"] is None
        assert client.post(f"/api/drafts/{draft['id']}/restore-context", json={}).json()["packet"] is None
        assert client.get("/api/drafts/missing").status_code == 404
        assert client.put("/api/drafts/missing", json=dict(title="No", form={})).status_code == 404
        assert client.post("/api/drafts", json=dict(title="  ", form={})).status_code == 400
        assert client.post("/api/drafts", json=dict(title="No", form=dict(target_model="v5"))).status_code == 422
        form = dict(concept_ids=["space"])
        packet = client.post("/api/context", json=form).json()
        request = dict(title="Empty choice", form=form, selected_ids=[], catalog_sha256=packet["catalog_sha256"])
        assert client.post("/api/drafts", json=request).status_code == 201
        assert client.post("/api/drafts", json={**request, "selected_ids": ["missing"]}).status_code == 400


def test_inactive_saved_sources_block_selection_restore_but_keep_direction_readable(setup_catalog):
    database, catalog, reviews, original = setup_catalog
    with TestClient(create_app(database, catalog, reviews)) as client:
        form = dict(concept_ids=["space"], intent="Keep the original direction")
        packet = client.post("/api/context", json=form).json()
        draft = client.post("/api/drafts", json=dict(title="Pinned", form=form,
            selected_ids=["cookbook:pad"], catalog_sha256=packet["catalog_sha256"])).json()
        replacement = original.model_copy(deep=True)
        replacement.source.curation_sha256 = "d" * 64
        with Store(database) as store:
            store.import_bundle(replacement)
            store.activate(replacement.source.snapshot_id)
        assert client.post(f"/api/drafts/{draft['id']}/restore-context", json={}).status_code == 409
        saved = client.get(f"/api/drafts/{draft['id']}").json()
        assert saved["form"]["intent"] == form["intent"]
        assert saved["selection"]["packet"] == packet
