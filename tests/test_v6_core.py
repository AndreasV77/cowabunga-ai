import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from prompt_reference.adapters.curated import load_curated_source
from prompt_reference.models import Bundle, Evidence
from prompt_reference.store import Store
from prompt_reference.reviews import ReviewSet, resolve_reviews
from test_references import reference_bundle, synthetic_source

ROOT = Path(__file__).resolve().parents[1]


def test_source_orientation_is_not_record_evidence(tmp_path):
    bundle = reference_bundle()
    bundle.source.orientation = "v6_native"
    bundle.source.orientation_basis = "Reviewed source introduction"
    with Store(tmp_path / "core.sqlite3") as store:
        store.import_bundle(bundle)
        assert store.search("sidechain")
        assert store.search("sidechain", v6_core=True) == []
        assert store.stats(v6_core=True)["entries"] == 0
        updated = bundle.model_copy(deep=True)
        updated.source.curation_sha256 = "c" * 64
        updated.entries[0].evidence.model_basis = "v6_targeted"
        store.import_bundle(updated)
        store.activate(updated.source.snapshot_id)
        hit = store.search("sidechain", v6_core=True)[0]
        assert hit["entry"]["evidence"]["independently_verified"] is False
        assert store.stats(v6_core=True)["entries"] == 1
        assert len(store.search("sidechain", v6_core=True, history=True)) == 1


def test_mixed_source_targeted_record_is_not_v6_native_core(tmp_path):
    bundle = reference_bundle()
    bundle.source.orientation = "mixed"
    bundle.entries[0].evidence.model_basis = "v6_targeted"
    with Store(tmp_path / "mixed.sqlite3") as store:
        store.import_bundle(bundle)
        assert store.search("sidechain", model_basis="v6_targeted")
        assert not store.search("sidechain", v6_core=True)
        with pytest.raises(ValueError, match="model basis"):
            store.search("sidechain", model_basis="verified")


def test_legacy_exports_default_to_unspecified_instead_of_guessing(tmp_path):
    bundle = reference_bundle()
    old = bundle.model_dump()
    old["schema_version"] = "1.1"
    old["source"].pop("orientation")
    old["source"].pop("orientation_basis")
    old["entries"][0]["evidence"].pop("model_basis")
    restored = Bundle.model_validate(old)
    with Store(tmp_path / "old.sqlite3") as store:
        store.import_bundle(restored)
        assert store.search("sidechain", model_basis="unspecified")
        assert not store.search("sidechain", v6_core=True)


def test_model_basis_invariants():
    with pytest.raises(ValidationError, match="explicit V6"):
        Evidence(status="source_claim", source_label="test", context="test", model_basis="v6_targeted")
    with pytest.raises(ValidationError, match="Legacy"):
        Evidence(status="source_claim", source_label="test", context="test", model_basis="pre_v6", model_scope=["v6"])
    with pytest.raises(ValidationError):
        Evidence(status="source_claim", source_label="test", context="test", independently_verified=True)


def test_orientation_requires_exact_source_excerpt(tmp_path):
    directory, path, curation = synthetic_source(tmp_path)
    curation["orientation"] = "v6_native"
    path.write_text(json.dumps(curation), encoding="utf-8")
    with pytest.raises(ValueError, match="reviewed README"):
        load_curated_source(directory, path)
    curation["orientation_excerpt"] = "not in the README"
    path.write_text(json.dumps(curation), encoding="utf-8")
    with pytest.raises(ValueError, match="match exactly"):
        load_curated_source(directory, path)


def test_real_v6_core_with_two_distinct_publishers_if_available(tmp_path):
    specs = [("cookbook", "c8e40ff0b10636a7719cbc88bc5f58443ad19907-v0.4"),
             ("lil-synn", "6b805bf77a350e7fba00bfd2451273327482827c")]
    bundles = []
    for source, revision in specs:
        directory = ROOT / "data/sources" / source / revision
        if not (directory / "manifest.json").exists():
            pytest.skip("Optional V6 source snapshot not fetched")
        bundles.append(load_curated_source(directory, ROOT / "curations" / f"{source}.json"))
    with Store(tmp_path / "v6.sqlite3") as store:
        for bundle in bundles:
            store.import_bundle(bundle)
        assert store.stats(v6_core=True)["entries"] == 64
        assert store.stats(v6_core=True)["recipes"] == 3
        results = store.search("vocal", v6_core=True, limit=100)
        assert {hit["source"]["id"] for hit in results} == {"cookbook", "lil-synn"}
        assert all(hit.get("entry", hit.get("recipe"))["evidence"]["independently_verified"] is False for hit in results)
        assert all("reproducible operational workaround" not in e.text for bundle in bundles for e in bundle.entries)


def test_core_relevance_precedes_lexical_rank_without_claiming_verification(tmp_path):
    mixed = reference_bundle()
    mixed.source.orientation = "mixed"
    mixed.entries[0].evidence.model_basis = "v6_targeted"
    native = mixed.model_copy(deep=True)
    native.source.id = "native"
    native.source.orientation = "v6_native"
    native.entries[0].id = "native:pad"
    with Store(tmp_path / "rank.sqlite3") as store:
        store.import_bundle(mixed)
        store.import_bundle(native)
        hits = store.search("sidechain")
        assert hits[0]["source"]["id"] == "native"
        assert hits[0]["v6_core"] is True
        assert hits[1]["v6_core"] is False
        assert all(hit["entry"]["evidence"]["independently_verified"] is False for hit in hits)


def test_review_resolution_is_pinned_and_rejects_missing_records(tmp_path):
    bundle = reference_bundle()
    second = bundle.entries[0].model_copy(deep=True)
    second.id = "cookbook:second"
    bundle.entries.append(second)
    review = ReviewSet.model_validate(dict(reviewed_on="2026-10-26", snapshots={"cookbook": bundle.source.snapshot_id},
        cases=[dict(id="test", topic="two interpretations", record_ids=["cookbook:pad", "cookbook:second"],
                    assessment="complementary", conclusion="Different wording", evidence_limit="No listening test")]))
    path = tmp_path / "reviews.json"
    path.write_text(review.model_dump_json(), encoding="utf-8")
    with Store(tmp_path / "review.sqlite3") as store:
        store.import_bundle(bundle)
        assert len(resolve_reviews(store, path)["cases"][0]["records"]) == 2
        review.cases[0].record_ids[1] = "cookbook:missing"
        path.write_text(review.model_dump_json(), encoding="utf-8")
        with pytest.raises(ValueError, match="Missing comparison"):
            resolve_reviews(store, path)


def test_review_cannot_claim_independent_test_confirmation():
    from prompt_reference.reviews import Crosscheck
    with pytest.raises(ValidationError):
        Crosscheck(id="test", topic="test", record_ids=["a", "b"], assessment="agreement",
                   conclusion="Same advice", evidence_limit="No test", independent_test_confirmation=True)


def test_real_crosschecks_resolve_without_upgrading_evidence_if_available(tmp_path):
    specs = [("band-manager", "73c52379833af51e9d3ce7731746d3bfff3f5266"),
             ("cookbook", "c8e40ff0b10636a7719cbc88bc5f58443ad19907-v0.4"),
             ("lil-synn", "6b805bf77a350e7fba00bfd2451273327482827c")]
    with Store(tmp_path / "reviews.sqlite3") as store:
        for source, revision in specs:
            directory = ROOT / "data/sources" / source / revision
            if not (directory / "manifest.json").exists():
                pytest.skip("Optional source snapshot not fetched")
            store.import_bundle(load_curated_source(directory, ROOT / "curations" / f"{source}.json"))
        result = resolve_reviews(store, ROOT / "reviews/v6-crosschecks.json")
        assert len(result["cases"]) == 4
        assert any(case["assessment"] == "tension" for case in result["cases"])
        assert all(case["independent_test_confirmation"] is False for case in result["cases"])
        assert {record["record"]["id"].split(":")[0] for case in result["cases"] for record in case["records"]} == {"cookbook", "lil-synn", "band-manager"}
