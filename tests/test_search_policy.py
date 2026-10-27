import json
import subprocess
import sys

import pytest
from pydantic import ValidationError

from prompt_reference.library import LibraryPage, search_library
from prompt_reference.models import Bundle
from prompt_reference.search import plan_query
from prompt_reference.store import Store
from test_core import bundle
from test_references import reference_bundle
from test_concepts import setup_catalog


def test_reviewed_recall_keeps_and_scope_and_original_data(tmp_path, bundle):
    bundle.recipes[0].style_prompt = "galloping guitars, clear drums"
    guidance = reference_bundle()
    guidance.entries[0].text = "negative wording"
    guidance.entries[0].meaning = "Experimental avoidance, not guaranteed suppression."
    database = tmp_path / "search.sqlite3"
    with Store(database) as store:
        store.import_bundle(bundle)
        store.import_bundle(guidance)
        before = list(store.connection.iterdump())
        assert store.search("gallop")[0]["recipe"]["id"] == bundle.recipes[0].id
        assert store.search("gallop", expand=False) == []
        assert store.search("gallop guitars")
        assert not store.search("gallop piano")
        assert not store.search("gal")
        assert not store.search("gallop", v6_core=True)
        assert not store.search("gallop", kind="guidance")
        assert store.search("exclude")[0]["entry"]["id"] == guidance.entries[0].id
        assert not store.search("exclude", expand=False)
        for query in ('" OR guitars --', 'exclude OR missing', 'gallop" ) OR guitars', 'excluded'):
            assert not store.search(query)
        assert store.export(bundle.source.snapshot_id) == bundle
        assert list(store.connection.iterdump()) == before


def test_library_trace_and_legacy_page_are_explicit(tmp_path, bundle):
    bundle.recipes[0].style_prompt = "galloping guitars"
    with Store(tmp_path / "search.sqlite3") as store:
        store.import_bundle(bundle)
        page = search_library(store, "GAllop")
        assert page.query == "GAllop"
        assert page.search_plan.expanded
        assert page.search_plan.term_groups == [["gallop", "galloping"]]
        literal = search_library(store, "gallop", expand=False)
        assert not literal.items and not literal.search_plan.expanded
        old = page.model_dump()
        old["schema_version"] = "1.0"
        old.pop("search_plan")
        assert LibraryPage.model_validate(old).search_plan is None
    assert not plan_query("Mongolian Tibetan choir gang").expanded


@pytest.mark.parametrize("version", ["1.0", "1.1", "1.2", "1.3"])
def test_old_bundle_versions_and_separate_exclude_field(version):
    bundle = reference_bundle()
    data = bundle.model_dump()
    data["schema_version"] = version
    assert Bundle.model_validate(data).entries[0].input_field == bundle.entries[0].input_field
    data["entries"][0]["input_field"] = "exclude_styles"
    restored = Bundle.model_validate(data)
    assert Bundle.model_validate_json(restored.model_dump_json()).entries[0].input_field == "exclude_styles"
    data["entries"][0]["input_field"] = "invented"
    with pytest.raises(ValidationError):
        Bundle.model_validate(data)


def test_cli_explains_and_can_disable_expansion(tmp_path, bundle):
    bundle.recipes[0].style_prompt = "galloping guitars"
    database = tmp_path / "cli.sqlite3"
    with Store(database) as store:
        store.import_bundle(bundle)
    args = [sys.executable, "-m", "prompt_reference.cli", "--db", str(database), "search", "gallop", "--explain"]
    expanded = json.loads(subprocess.check_output(args, text=True))
    assert expanded["search_plan"]["expanded"] and expanded["items"]
    literal = json.loads(subprocess.check_output([*args, "--literal"], text=True))
    assert not literal["search_plan"]["expanded"] and literal["items"] == []


def test_api_exposes_same_plan_and_literal_option(setup_catalog, bundle):
    from fastapi.testclient import TestClient
    from prompt_reference.server import create_app
    database, catalog, reviews, _ = setup_catalog
    bundle.recipes[0].style_prompt = "galloping guitars"
    with Store(database) as store:
        store.import_bundle(bundle)
    with TestClient(create_app(database, catalog, reviews)) as client:
        result = client.get("/api/library", params={"q": "gallop"})
        assert result.status_code == 200
        assert result.json()["search_plan"]["expanded"] and result.json()["items"]
        literal = client.get("/api/library", params={"q": "gallop", "expand": "false"}).json()
        assert not literal["search_plan"]["expanded"] and not literal["items"]
