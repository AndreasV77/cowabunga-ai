import pytest

pytest.importorskip("fastapi")
from fastapi.testclient import TestClient
from prompt_reference.server import create_app
from test_concepts import setup_catalog


def test_listening_api_pins_draft_preserves_original_and_checks_revision(setup_catalog):
    database, catalog, reviews, _ = setup_catalog
    with TestClient(create_app(database, catalog, reviews)) as client:
        parent = client.post("/api/drafts", json={"title": "Song", "form": {"intent": "Original"}}).json()
        base = f"/api/drafts/{parent['id']}/listening"
        request = {"title": "First listen", "draft_revision": 1, "assessment": {"raw_report": {"original": 1}}}
        created = client.post(base, json=request)
        assert created.status_code == 201
        report = created.json()
        assert report["draft_snapshot"] == parent
        assert client.get(base).json() == [report]
        assert client.get(base + "/" + report["id"]).json() == report
        client.put(f"/api/drafts/{parent['id']}", json={"title": "Changed", "form": {"intent": "Changed"}, "revision": 1})
        assert client.post(base, json=request).status_code == 409
        revised = {**request, "revision": 1, "assessment": {"raw_report": {"original": 1}, "listening_value": {"later_replay": 2}}}
        update = client.put(base + "/" + report["id"], json=revised)
        assert update.status_code == 200
        assert update.json()["original_assessment"] == report["assessment"]
        assert update.json()["draft_snapshot"] == parent
        assert client.put(base + "/" + report["id"], json=revised).status_code == 409
        revised["revision"] = 2
        revised["assessment"]["raw_report"] = {"original": 9}
        assert client.put(base + "/" + report["id"], json=revised).status_code == 400
        assert client.post("/api/drafts/missing/listening", json=request).status_code == 404
        assert client.get(base + "/missing").status_code == 404


def test_listening_api_rejects_invalid_scores_and_does_not_mix_drafts(setup_catalog):
    database, catalog, reviews, _ = setup_catalog
    with TestClient(create_app(database, catalog, reviews)) as client:
        first = client.post("/api/drafts", json={"title": "One", "form": {}}).json()
        second = client.post("/api/drafts", json={"title": "Two", "form": {}}).json()
        base = f"/api/drafts/{first['id']}/listening"
        request = {"title": "Listen", "draft_revision": 1, "assessment": {}}
        document = client.post(base, json=request).json()
        other = f"/api/drafts/{second['id']}/listening"
        assert client.get(other).json() == []
        assert client.get(other + "/" + document["id"]).status_code == 404
        for assessment in [{"listening_value": {"immediate_replay": 3}}, {"problems": {"merged_voices": 0}}, {"total_score": 10}]:
            assert client.post(base, json={**request, "assessment": assessment}).status_code == 422
        assert client.post(base, json={**request, "title": "  "}).status_code == 400
