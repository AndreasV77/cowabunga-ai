from pathlib import Path

import pytest

pytest.importorskip("fastapi")
from fastapi.testclient import TestClient
from prompt_reference.server import create_app
from prompt_reference.concepts import ContextPacket
from test_concepts import setup_catalog


def test_api_uses_real_context_service_and_preserves_selected_records(setup_catalog):
    db, catalog, reviews, _ = setup_catalog
    with TestClient(create_app(db, catalog, reviews)) as client:
        assert client.get("/api/meta").json()["concepts"] == 2
        assert client.get("/api/concepts?q=intimate%20singer").json()[0]["id"] == "space"
        payload = {"concept_ids": ["space"], "intent": "Close singer", "supplementary": True}
        response = client.post("/api/context", json=payload)
        assert response.status_code == 200
        packet = ContextPacket.model_validate(response.json())
        assert len(packet.items) == 2
        result = client.post("/api/export", json={**payload, "selected_ids": ["cookbook:pad"], "format": "json"})
        assert result.status_code == 200
        exported = ContextPacket.model_validate_json(result.text)
        assert len(exported.items) == 1
        assert exported.omitted[-1].reason == "user_deselected"
        assert exported.sources[exported.items[0].snapshot_id].license_text == "Test notice"
        markdown = client.post("/api/export", json={**payload, "selected_ids": ["cookbook:pad"], "format": "markdown"})
        assert "Music prompt context" in markdown.text
        assert "Test notice" in markdown.text
        assert "attachment" in markdown.headers["content-disposition"]


def test_api_rejects_unknown_or_empty_selection_and_oversized_intent(setup_catalog):
    db, catalog, reviews, _ = setup_catalog
    with TestClient(create_app(db, catalog, reviews)) as client:
        assert client.post("/api/context", json={"concept_ids": []}).status_code == 422
        assert client.post("/api/context", json={"concept_ids": ["missing"]}).status_code == 400
        assert client.post("/api/context", json={"concept_ids": ["space"], "intent": "x" * 4001}).status_code == 422
        assert client.post("/api/export", json={"concept_ids": ["space"], "selected_ids": ["unknown"]}).status_code == 400
        assert client.post("/api/export", json={"concept_ids": ["space"], "selected_ids": []}).status_code == 422


def test_api_reports_missing_database_and_stale_catalog(setup_catalog, tmp_path):
    db, catalog, reviews, _ = setup_catalog
    with TestClient(create_app(tmp_path / "missing.sqlite3", catalog, reviews)) as client:
        assert client.get("/api/meta").status_code == 503
    reviews.write_bytes(reviews.read_bytes() + b"\n")
    with TestClient(create_app(db, catalog, reviews)) as client:
        assert client.get("/api/concepts").status_code == 409


def test_static_build_and_missing_build_are_explicit(setup_catalog, tmp_path):
    db, catalog, reviews, _ = setup_catalog
    with TestClient(create_app(db, catalog, reviews)) as client:
        assert client.get("/").status_code == 503
    dist = tmp_path / "dist"
    dist.mkdir()
    (dist / "index.html").write_text("<html>Workbench</html>", encoding="utf-8")
    with TestClient(create_app(db, catalog, reviews, dist)) as client:
        assert "Workbench" in client.get("/").text
        assert client.get("/api/meta").status_code == 200
