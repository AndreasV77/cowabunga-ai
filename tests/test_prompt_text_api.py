import pytest

pytest.importorskip("fastapi")
from fastapi.testclient import TestClient
from prompt_reference.server import create_app
from prompt_reference.prompt_text import PromptVersion, text_hash
from test_concepts import setup_catalog


def test_text_api_checks_head_context_parent_and_keeps_immutable_versions(setup_catalog):
    database, catalog, reviews, _ = setup_catalog
    with TestClient(create_app(database, catalog, reviews)) as client:
        parent = client.post("/api/drafts", json={"title": "Song", "form": {}}).json()
        base = f"/api/drafts/{parent['id']}/prompt-versions"
        assert client.get(base).json()["head_id"] is None
        request = {"draft_revision": 1, "content": {"style_prompt": "  Kehlgesang 🔔\r\n", "lyrics": "[Verse]\nOne\n\n"}}
        first_response = client.post(base, json=request)
        assert first_response.status_code == 201
        first = PromptVersion.model_validate(first_response.json())
        assert first.draft_snapshot.id == parent["id"]
        assert first.style_sha256 == text_hash(request["content"]["style_prompt"])
        assert client.post(base, json=request).status_code == 409
        second = client.post(base, json={**request, "expected_head_id": first.id, "based_on_id": first.id, "note": "Second"}).json()
        assert second["version"] == 2 and second["previous_id"] == first.id
        assert client.get(base + "/" + first.id).json() == first.model_dump(mode="json")
        assert client.put(base + "/" + first.id, json=request).status_code == 405
        assert client.get(base, params={"limit": 1}).json()["has_more"]
        assert client.get(base, params={"offset": 1, "limit": 1}).json()["items"][0]["id"] == first.id
        client.put(f"/api/drafts/{parent['id']}", json={"title": "Updated", "form": {}, "revision": 1})
        assert client.post(base, json={**request, "expected_head_id": second["id"]}).status_code == 409
        next_version = client.post(base, json={**request, "draft_revision": 2, "expected_head_id": second["id"], "based_on_id": first.id}).json()
        assert next_version["version"] == 3 and next_version["draft_snapshot"]["revision"] == 2
        assert next_version["style_sha256"] == first.style_sha256


def test_text_api_rejects_cross_draft_history_and_forged_or_oversized_payloads(setup_catalog):
    database, catalog, reviews, _ = setup_catalog
    with TestClient(create_app(database, catalog, reviews)) as client:
        first = client.post("/api/drafts", json={"title": "One", "form": {}}).json()
        second = client.post("/api/drafts", json={"title": "Two", "form": {}}).json()
        base = f"/api/drafts/{first['id']}/prompt-versions"
        other = f"/api/drafts/{second['id']}/prompt-versions"
        request = {"draft_revision": 1, "content": {"style_prompt": "One"}}
        version = client.post(base, json=request).json()
        assert client.get(other + "/" + version["id"]).status_code == 404
        assert client.post(other, json={**request, "based_on_id": version["id"]}).status_code == 404
        assert client.get(other).json()["items"] == []
        assert client.post(other, json={**request, "content": {"style_prompt": "x" * 20001}}).status_code == 422
        assert client.post(other, json={**request, "style_sha256": "made up"}).status_code == 422
        assert client.get(base, params={"offset": -1}).status_code == 422
        assert client.get("/api/drafts/missing/prompt-versions").status_code == 404
