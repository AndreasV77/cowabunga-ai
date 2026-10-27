import pytest

pytest.importorskip("fastapi")
from fastapi.testclient import TestClient
from prompt_reference.server import create_app
from prompt_reference.store import Store
from prompt_reference.models import Bundle
from test_core import bundle
from test_concepts import setup_catalog


def test_library_api_search_filters_and_single_record_export(setup_catalog, bundle):
    database, catalog, reviews, _ = setup_catalog
    bundle.recipes[0].style_prompt = "Mongolian throat singing, sidechain pad"
    with Store(database) as store:
        store.import_bundle(bundle)
        before = list(store.connection.iterdump())
    with TestClient(create_app(database, catalog, reviews)) as client:
        response = client.get("/api/library", params={"q": "pad", "limit": 1})
        assert response.status_code == 200
        assert response.json()["has_more"] and response.json()["items"][0]["v6_core"]
        recipe = client.get("/api/library", params={"q": "Mongolian", "kind": "recipe"}).json()["items"][0]
        assert recipe["source"]["license"] == "CC0-1.0"
        assert client.get("/api/library", params={"q": "Mongolian", "scope": "v6_core"}).json()["items"] == []
        request = {"snapshot_id": recipe["snapshot_id"], "record_id": recipe["record"]["id"]}
        exported = client.post("/api/library/export", json=request)
        assert exported.status_code == 200 and "attachment" in exported.headers["content-disposition"]
        assert Bundle.model_validate_json(exported.text) == bundle
        assert client.post("/api/library/export", json={**request, "record_id": "missing"}).status_code == 404
        assert client.post("/api/library/export", json={**request, "snapshot_id": "inactive"}).status_code == 409
        for params in [{"limit": 0}, {"limit": 101}, {"scope": "legacy"}, {"kind": "audio"}, {"q": "x" * 301}]:
            assert client.get("/api/library", params=params).status_code == 422
    with Store(database) as store:
        assert list(store.connection.iterdump()) == before


def test_library_does_not_require_concept_catalog_and_missing_database_is_explicit(setup_catalog, tmp_path):
    database, _, _, _ = setup_catalog
    with TestClient(create_app(database, tmp_path / "missing-catalog", tmp_path / "missing-reviews")) as client:
        assert client.get("/api/library", params={"q": "pad"}).json()["items"]
        assert client.get("/api/concepts").status_code == 409
    with TestClient(create_app(tmp_path / "missing.sqlite3", tmp_path / "catalog", tmp_path / "reviews")) as client:
        assert client.get("/api/library", params={"q": "pad"}).status_code == 503
