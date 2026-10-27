import hashlib
import json
import subprocess
import sys
from pathlib import Path

import pytest
from pydantic import ValidationError

from prompt_reference.concepts import CatalogService, ConceptCatalog, ContextPacket, render_context
from prompt_reference.reviews import ReviewSet
from prompt_reference.store import Store
from test_references import reference_bundle

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def setup_catalog(tmp_path):
    core = reference_bundle()
    core.source.orientation = "v6_native"
    core.entries[0].evidence.model_basis = "v6_targeted"
    supplement = reference_bundle()
    supplement.source.id = "band-manager"
    supplement.source.orientation = "mixed"
    supplement.entries[0].id = "band-manager:pad"
    supplement.entries[0].evidence.model_scope = []
    reviews = ReviewSet(reviewed_on="2026-10-26", snapshots={"cookbook": core.source.snapshot_id,
                                                         "band-manager": supplement.source.snapshot_id}, cases=[])
    reviews_path = tmp_path / "reviews.json"
    reviews_path.write_text(reviews.model_dump_json(), encoding="utf-8")
    links = [dict(record_id="cookbook:pad", relation="wording", note="Main candidate"),
             dict(record_id="band-manager:pad", relation="alternative", note="Not declared equivalent")]
    catalog = ConceptCatalog.model_validate(dict(version="test", reviewed_on="2026-10-26",
        snapshots=reviews.snapshots, reviews_sha256=hashlib.sha256(reviews_path.read_bytes()).hexdigest(),
        concepts=[dict(id="space", label="Vocal space", aliases=["intimate singer"], description="Foreground and background", links=links),
                  dict(id="depth", label="Depth", aliases=[], description="Near and far", links=links[:1])]))
    catalog_path = tmp_path / "catalog.json"
    catalog_path.write_text(catalog.model_dump_json(), encoding="utf-8")
    database = tmp_path / "concepts.sqlite3"
    with Store(database) as store:
        store.import_bundle(core)
        store.import_bundle(supplement)
    return database, catalog_path, reviews_path, core


def test_context_default_is_core_only_deduplicated_and_portable(setup_catalog):
    database, path, reviews, _ = setup_catalog
    with Store(database) as store:
        service = CatalogService(store, path, reviews)
        assert service.find("intimate singer")[0].id == "space"
        assert service.find("not present") == []
        packet = service.build_context(["space", "depth", "space"], intent="A close singer")
        assert len(packet.concepts) == 2
        assert len(packet.items) == 1
        assert len(packet.items[0].uses) == 2
        assert packet.items[0].v6_core
        assert packet.omitted[0].reason == "outside_v6_core"
        assert ContextPacket.model_validate_json(packet.model_dump_json()) == packet
        assert packet.sources[packet.items[0].snapshot_id].license_text == "Test notice"
        assert packet.items[0].record.evidence.independently_verified is False
        assert service.build_context(["space", "depth"], intent="A close singer") == packet


def test_supplementary_context_and_limit_are_explicit(setup_catalog):
    database, path, reviews, _ = setup_catalog
    with Store(database) as store:
        service = CatalogService(store, path, reviews)
        packet = service.build_context(["space"], supplementary=True)
        assert [item.v6_core for item in packet.items] == [True, False]
        limited = service.build_context(["space"], supplementary=True, limit=1)
        assert len(limited.items) == 1
        assert limited.omitted[0].reason == "limit"
        assert "Source attribution" in render_context(packet)
        assert "Test notice" in render_context(packet)
        assert "supplementary" in render_context(packet)


def test_target_model_scope_is_not_silently_expanded(setup_catalog):
    database, path, reviews, _ = setup_catalog
    with Store(database) as store:
        packet = CatalogService(store, path, reviews).build_context(["space"], target_model="v6-mini")
        assert packet.items == []
        assert any(item.reason == "model_scope_mismatch" for item in packet.omitted)


def test_inactive_selected_source_requires_review(setup_catalog):
    database, path, reviews, core = setup_catalog
    updated = core.model_copy(deep=True)
    updated.source.curation_sha256 = "c" * 64
    with Store(database) as store:
        store.import_bundle(updated)
        store.activate(updated.source.snapshot_id)
        with pytest.raises(ValueError, match="inactive"):
            CatalogService(store, path, reviews).build_context(["space"])


def test_changed_review_file_and_missing_record_are_rejected(setup_catalog):
    database, path, reviews, _ = setup_catalog
    with Store(database) as store:
        original = reviews.read_bytes()
        reviews.write_bytes(original + b"\n")
        with pytest.raises(ValueError, match="Crosscheck file changed"):
            CatalogService(store, path, reviews)
        reviews.write_bytes(original)
        payload = json.loads(path.read_text(encoding="utf-8"))
        payload["concepts"][0]["links"][0]["record_id"] = "cookbook:missing"
        path.write_text(json.dumps(payload), encoding="utf-8")
        with pytest.raises(ValueError, match="Missing concept record"):
            CatalogService(store, path, reviews)


def test_duplicate_concept_ids_are_rejected(setup_catalog):
    _, path, _, _ = setup_catalog
    payload = json.loads(path.read_text(encoding="utf-8"))
    payload["concepts"].append(payload["concepts"][0])
    with pytest.raises(ValidationError, match="Duplicate concept"):
        ConceptCatalog.model_validate(payload)


def test_invalid_context_requests_fail_without_implicit_selection(setup_catalog):
    database, path, reviews, _ = setup_catalog
    with Store(database) as store:
        service = CatalogService(store, path, reviews)
        for ids, kwargs, message in [([], {}, "at least one"), (["unknown"], {}, "Unknown concepts"),
                                     (["space"], {"limit": 0}, "limit"), (["space"], {"target_model": "v5"}, "Unsupported")]:
            with pytest.raises(ValueError, match=message):
                service.build_context(ids, **kwargs)


def test_cli_context_export_and_overwrite_refusal(setup_catalog, tmp_path):
    database, path, reviews, _ = setup_catalog
    output = tmp_path / "packet.json"
    command = [sys.executable, "-m", "prompt_reference.cli", "--db", str(database), "context", "space",
               "--catalog", str(path), "--reviews", str(reviews), "--output", str(output)]
    first = subprocess.run(command, capture_output=True, text=True)
    assert first.returncode == 0, first.stderr
    assert ContextPacket.model_validate_json(output.read_text(encoding="utf-8")).items
    assert subprocess.run(command, capture_output=True).returncode == 1


def test_real_catalog_resolves_if_snapshots_available(tmp_path):
    # The store is built from the exact current selections rather than a developer's live DB.
    from prompt_reference.adapters.curated import load_curated_source
    specs = [("band-manager", "73c52379833af51e9d3ce7731746d3bfff3f5266"),
             ("cookbook", "c8e40ff0b10636a7719cbc88bc5f58443ad19907-v0.4"),
             ("lil-synn", "6b805bf77a350e7fba00bfd2451273327482827c")]
    with Store(tmp_path / "real.sqlite3") as store:
        for source, revision in specs:
            directory = ROOT / "data/sources" / source / revision
            if not (directory / "manifest.json").exists():
                pytest.skip("Optional source snapshot not fetched")
            store.import_bundle(load_curated_source(directory, ROOT / "curations" / f"{source}.json"))
        service = CatalogService(store, ROOT / "curations/concepts.json", ROOT / "reviews/v6-crosschecks.json")
        assert len(service.find()) == 12
        for concept in service.catalog.concepts:
            packet = service.build_context([concept.id])
            assert packet.items
            assert all(item.v6_core for item in packet.items)
            assert ContextPacket.model_validate_json(packet.model_dump_json()) == packet
        packet = service.build_context(["acoustic-drums"])
        assert packet.crosschecks[0].assessment == "tension"
        assert packet.crosschecks[0].independent_test_confirmation is False
        assert any(source.id == "band-manager" for source in packet.sources.values())
        recipe_packet = service.build_context(["positive-replacement"])
        rendered = render_context(recipe_packet)
        assert "Separate source exclusions" in rendered
        assert "Screamed verses" in rendered
        assert "These are source-bound candidates" in rendered


def test_packet_provenance_cannot_be_dropped_or_core_flag_changed(setup_catalog):
    database, path, reviews, _ = setup_catalog
    with Store(database) as store:
        packet = CatalogService(store, path, reviews).build_context(["space"])
        payload = packet.model_dump(mode="json")
        payload["sources"] = {}
        with pytest.raises(ValidationError, match="missing source metadata"):
            ContextPacket.model_validate(payload)
        payload = packet.model_dump(mode="json")
        payload["items"][0]["v6_core"] = False
        with pytest.raises(ValidationError, match="core flag differs"):
            ContextPacket.model_validate(payload)
