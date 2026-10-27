import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from prompt_reference.library import LibraryHit, LibraryPage, RecordRequest, search_library, export_record
from prompt_reference.models import Bundle
from prompt_reference.store import Store
from test_core import bundle
from test_concepts import setup_catalog

ROOT = Path(__file__).resolve().parents[1]


def test_library_search_prioritizes_v6_and_exposes_unlinked_recipes(setup_catalog, bundle):
    database, _, _, core = setup_catalog
    bundle.recipes[0].style_prompt = "Mongolian throat singing, pad, galloping guitars"
    with Store(database) as store:
        store.import_bundle(bundle)
        page = search_library(store, "pad", limit=1)
        assert page.has_more and page.items[0].v6_core
        assert page.items[0].source.license_text == "Test notice"
        core_only = search_library(store, "pad", scope="v6_core")
        assert len(core_only.items) == 1
        recipe = search_library(store, "pad", kind="recipe").items[0]
        assert recipe.source.id == "musai" and not recipe.v6_core
        assert recipe.record.settings.model_version is None
        assert recipe.record.evidence is None
        assert search_library(store, "gallop").items == []
        assert len(search_library(store, "galloping").items) == 1
        assert search_library(store, '" OR pad --').items == []
        assert search_library(store, " ").items == []
        assert LibraryPage.model_validate_json(page.model_dump_json()) == page
        for kwargs in [dict(scope="bad"), dict(limit=0), dict(limit=101), dict(query="x" * 301)]:
            with pytest.raises(ValueError):
                search_library(store, **({"query": "pad"} | kwargs))


def test_record_export_preserves_full_original_and_rejects_inactive_snapshots(tmp_path, bundle):
    with Store(tmp_path / "references.sqlite3") as store:
        store.import_bundle(bundle)
        request = RecordRequest(snapshot_id=bundle.source.snapshot_id, record_id=bundle.recipes[0].id)
        assert export_record(store, request) == bundle
        with pytest.raises(KeyError):
            export_record(store, request.model_copy(update={"record_id": "missing"}))
        next_version = bundle.model_copy(deep=True)
        next_version.source.revision = "c" * 40
        store.import_bundle(next_version)
        store.activate(next_version.source.snapshot_id)
        with pytest.raises(ValueError, match="no longer active"):
            export_record(store, request)
        assert store.export(bundle.source.snapshot_id) == bundle


def test_library_hit_rejects_false_v6_flag_or_source_identity(setup_catalog):
    database, _, _, _ = setup_catalog
    with Store(database) as store:
        hit = search_library(store, "pad").items[0].model_dump(mode="json")
        hit["v6_core"] = False
        with pytest.raises(ValidationError, match="classification"):
            LibraryHit.model_validate(hit)
        hit["source"]["id"] = "wrong"
        with pytest.raises(ValidationError, match="snapshot"):
            LibraryHit.model_validate(hit)


def test_challenge_mongolian_and_kawaii_vocabulary_is_searchable_without_concepts(tmp_path):
    supplement = Bundle.model_validate_json((ROOT / "tests/fixtures/musai-vocabulary.json").read_text(encoding="utf-8"))
    with Store(tmp_path / "challenge.sqlite3") as store:
        store.import_bundle(supplement)
        for query in ["Mongolian", "kawaii"]:
            page = search_library(store, query)
            assert len(page.items) == 1 and not page.items[0].v6_core
            assert page.items[0].source.license == "CC0-1.0"
            assert search_library(store, query, scope="v6_core").items == []
            record = page.items[0]
            exported = export_record(store, RecordRequest(snapshot_id=record.snapshot_id, record_id=record.record.id))
            assert exported.recipes[0] == record.record


def test_library_json_schema_is_current():
    assert json.loads((ROOT / "schemas/library.schema.json").read_text(encoding="utf-8")) == LibraryPage.model_json_schema()
