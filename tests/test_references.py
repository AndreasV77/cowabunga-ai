import hashlib
import json
import sqlite3
from pathlib import Path

import pytest

from prompt_reference.adapters.curated import DEFINITIONS, load_curated_source
from prompt_reference.models import Bundle, Citation, Evidence, Recipe, ReferenceEntry, SettingsRecommendation, Source
from prompt_reference.store import MIGRATIONS, Store

ROOT = Path(__file__).resolve().parents[1]


def reference_bundle():
    return Bundle(source=Source(id="cookbook", revision="a" * 40,
        repository="https://github.com/MJorgin/suno-v6-cookbook", license="CC-BY-4.0",
        retrieved_at="2026-10-26T00:00:00Z", files={}, attribution="Test author",
        license_url="https://creativecommons.org/licenses/by/4.0/", license_text="Test notice",
        changes="Selected and adapted", curation_sha256="b" * 64),
        entries=[ReferenceEntry(id="cookbook:pad", kind="phrase", text="sidechain pad",
            meaning="A synth pad with rhythmic level reduction.", category="production", input_field="style",
            evidence=Evidence(status="working_hypothesis", source_label="working-hypothesis",
                              model_scope=["v6"], context="Not independently tested"),
            citations=[Citation(path="page.md", line_start=4, line_end=4,
                                url="https://example.com/page#L4", excerpt="sidechain pad")])])


def test_mixed_search_filters_export_and_license(tmp_path):
    bundle = reference_bundle()
    bundle.recipes.append(Recipe(id="cookbook:recipe", title="Sidechain Dance", family="dance",
        style_prompt="sidechain pad", structure="[Drop]", settings=SettingsRecommendation(),
        source_record_url="https://example.com/recipe", raw_record={}))
    with Store(tmp_path / "mixed.sqlite3") as store:
        assert store.import_bundle(bundle) == 2
        assert store.import_bundle(bundle) == 0
        assert len(store.search("sidechain")) == 2
        assert len(store.search("sidechain", limit=1)) == 1
        assert store.search("sidechain", kind="phrase")[0]["entry"]["id"] == "cookbook:pad"
        assert store.search("sidechain", kind="recipe")[0]["recipe"]["id"] == "cookbook:recipe"
        assert store.search("sidechain", kind="term") == []
        hit = store.search("sidechain", kind="phrase")[0]
        assert hit["source"]["license_text"] == "Test notice"
        assert hit["entry"]["evidence"]["independently_verified"] is False
        assert store.export(bundle.source.snapshot_id) == bundle
        assert store.search("sidechain", snapshot="missing") == []


def test_real_version_one_database_migrates_without_losing_recipes(tmp_path):
    path = tmp_path / "old.sqlite3"
    source = Source(id="musai", revision="a" * 40, repository="https://example.com", license="CC0-1.0",
                    retrieved_at="2026-10-26T00:00:00Z", files={})
    recipe = Recipe(id="musai:old", title="Jazz", family="Jazz", style_prompt="walking bass",
                    structure="[Solo]", settings=SettingsRecommendation(), source_record_url="https://example.com/jazz", raw_record={})
    with sqlite3.connect(path) as connection:
        for statement in MIGRATIONS[0]:
            connection.execute(statement)
        connection.execute("PRAGMA user_version=1")
        connection.execute("INSERT INTO snapshots VALUES (?, ?)", (source.snapshot_id, source.model_dump_json(exclude_none=True)))
        connection.execute("INSERT INTO recipes VALUES (?, ?, ?)", (source.snapshot_id, recipe.id, recipe.model_dump_json(exclude_none=True)))
        connection.execute("INSERT INTO recipe_search VALUES (?, ?, ?, ?, ?, ?)", (source.snapshot_id, recipe.id, "Jazz", "Jazz", "walking bass", "[Solo]"))
    with Store(path) as store:
        assert store.connection.execute("PRAGMA user_version").fetchone()[0] == len(MIGRATIONS)
        assert store.export(source.snapshot_id).recipes == [recipe]
        assert store.search("walking bass")[0]["recipe"]["id"] == recipe.id
        assert store.import_bundle(Bundle(source=source, recipes=[recipe])) == 0
        assert store.import_bundle(reference_bundle()) == 1


def test_entry_failure_rolls_back_snapshot_recipes_and_indexes(tmp_path):
    bundle = reference_bundle()
    bundle.recipes.append(Recipe(id="cookbook:r", title="Pad", family="Dance", style_prompt="pad",
                                structure="[Drop]", settings=SettingsRecommendation(), source_record_url="https://example.com", raw_record={}))
    with Store(tmp_path / "rollback.sqlite3") as store:
        store.connection.execute("CREATE TRIGGER reject_entry BEFORE INSERT ON entries BEGIN SELECT RAISE(ABORT, 'test failure'); END")
        with pytest.raises(sqlite3.IntegrityError):
            store.import_bundle(bundle)
        assert store.snapshots() == []
        assert store.search("pad") == []
        assert store.connection.execute("SELECT COUNT(*) FROM recipes").fetchone()[0] == 0


def test_curation_versions_are_distinct(tmp_path):
    first = reference_bundle()
    second = first.model_copy(deep=True)
    second.source.curation_sha256 = "c" * 64
    second.entries[0].meaning = "Revised explanation"
    with Store(tmp_path / "versions.sqlite3") as store:
        store.import_bundle(first)
        store.import_bundle(second)
        assert len(store.snapshots()) == 2
        assert store.export(first.source.snapshot_id).entries[0].meaning != "Revised explanation"


def test_active_selection_prevents_duplicates_and_old_reimport_cannot_reactivate(tmp_path):
    first = reference_bundle()
    second = first.model_copy(deep=True)
    second.source.curation_sha256 = "c" * 64
    second.entries[0].meaning = "Updated explanation"
    with Store(tmp_path / "active.sqlite3") as store:
        store.import_bundle(first)
        store.import_bundle(second)
        assert store.active_snapshots()["cookbook"] == first.source.snapshot_id
        assert len(store.search("sidechain")) == 1
        assert len(store.search("sidechain", history=True)) == 2
        store.activate(second.source.snapshot_id)
        assert store.search("sidechain")[0]["entry"]["meaning"] == "Updated explanation"
        assert store.import_bundle(first) == 0
        assert store.active_snapshots()["cookbook"] == second.source.snapshot_id
        assert store.search("sidechain", snapshot=first.source.snapshot_id)[0]["entry"]["meaning"] != "Updated explanation"
        assert store.stats()["entries"] == 1
        assert store.stats(history=True)["entries"] == 2
        assert store.search("sidechain", category="production")
        assert not store.search("sidechain", category="vocals")
        before = store.active_snapshots()
        with pytest.raises(ValueError, match="Unknown snapshot"):
            store.activate("missing")
        assert store.active_snapshots() == before


def test_v2_migration_requires_explicit_selection_for_ambiguous_source(tmp_path):
    path = tmp_path / "v2.sqlite3"
    first = reference_bundle()
    second = first.model_copy(deep=True)
    second.source.curation_sha256 = "c" * 64
    with Store(path) as store:
        store.import_bundle(first)
        store.import_bundle(second)
    with sqlite3.connect(path) as connection:
        connection.execute("DROP TABLE prompt_heads")
        connection.execute("DROP TABLE prompt_versions")
        connection.execute("DROP TABLE active_sources")
        connection.execute("DROP TABLE workspace_preferences")
        connection.execute("DROP TABLE workspace_drafts")
        connection.execute("PRAGMA user_version=2")
    with Store(path) as store:
        assert store.active_snapshots() == {}
        assert store.search("sidechain") == []
        assert len(store.search("sidechain", history=True)) == 2
        store.activate(second.source.snapshot_id)
        assert len(store.search("sidechain")) == 1


def test_expanded_curation_retains_seed_ids_and_precise_musical_definitions():
    entries = []
    for source_id in ("band-manager", "cookbook"):
        seed = json.loads((ROOT / "curations" / "archive" / "0.2" / f"{source_id}.json").read_text(encoding="utf-8"))
        current = json.loads((ROOT / "curations" / f"{source_id}.json").read_text(encoding="utf-8"))
        old_by_id = {entry["id"]: entry for entry in seed["entries"]}
        new_by_id = {entry["id"]: entry for entry in current["entries"]}
        assert len(new_by_id) == len(current["entries"])
        for id, original in old_by_id.items():
            record = json.loads(json.dumps(new_by_id[id]))
            record["evidence"].pop("model_basis", None)
            assert record == original
        entries.extend(current["entries"])
    assert len(entries) == 135
    by_id = {entry["id"]: entry for entry in entries}
    assert "one syllable" in by_id["melisma"]["meaning"]
    assert by_id["falsetto"]["evidence"]["source_label"].startswith("LOW")
    assert "underlying tempo" in by_id["half-time"]["meaning"]
    assert "not a verified control" in by_id["ritardando"]["evidence"]["context"].lower()


def test_active_selection_does_not_resurrect_removed_entries(tmp_path):
    first = reference_bundle()
    revised = first.model_copy(deep=True)
    revised.source.curation_sha256 = "d" * 64
    revised.entries = []
    with Store(tmp_path / "removed.sqlite3") as store:
        store.import_bundle(first)
        store.import_bundle(revised)
        store.activate(revised.source.snapshot_id)
        assert store.search("sidechain") == []
        assert store.stats()["entries"] == 0
        assert len(store.search("sidechain", history=True)) == 1


def synthetic_source(tmp_path):
    source_dir = tmp_path / "source"
    source_dir.mkdir()
    definition = DEFINITIONS["cookbook"]
    hashes = {}
    for path in definition["files"]:
        target = source_dir / path
        target.parent.mkdir(parents=True, exist_ok=True)
        text = definition["license_marker"] if path == "LICENSE" else "Header\nsidechain pad\nFooter\n"
        target.write_text(text, encoding="utf-8")
        hashes[path] = hashlib.sha256(target.read_bytes()).hexdigest()
    source = Source(id="cookbook", revision="a" * 40, repository=definition["repository"],
                    license=definition["license"], retrieved_at="2026-10-26", files=hashes)
    (source_dir / "manifest.json").write_text(source.model_dump_json(), encoding="utf-8")
    record = reference_bundle().entries[0]
    selection = dict(id="pad", kind="phrase", path="library/genres/electronic-dance.md",
                     excerpt="sidechain pad", text=record.text, meaning=record.meaning,
                     category=record.category, input_field=record.input_field, evidence=record.evidence.model_dump())
    curation = dict(source_id="cookbook", revision="a" * 40, changes="Editorial adaptation", entries=[selection], recipes=[])
    curation_path = tmp_path / "curation.json"
    curation_path.write_text(json.dumps(curation), encoding="utf-8")
    return source_dir, curation_path, curation


def test_curated_adapter_checks_quotes_and_keeps_attribution(tmp_path):
    directory, path, _ = synthetic_source(tmp_path)
    bundle = load_curated_source(directory, path)
    assert bundle.entries[0].citations[0].line_start == 2
    assert bundle.entries[0].citations[0].line_end == 2
    assert bundle.source.curation_sha256 == hashlib.sha256(path.read_bytes()).hexdigest()
    assert "MJorgin" in bundle.source.attribution
    assert bundle.source.license_text
    assert bundle.source.changes == "Editorial adaptation"


@pytest.mark.parametrize("case, message", [("excerpt", "match exactly"), ("revision", "source/revision"), ("text", "wording absent"), ("traversal", "citation path"), ("tamper", "checksum"), ("missing-file", "file set")])
def test_curated_adapter_rejects_unreviewed_changes(tmp_path, case, message):
    directory, path, curation = synthetic_source(tmp_path)
    if case == "excerpt":
        curation["entries"][0]["excerpt"] = "not in source"
    elif case == "revision":
        curation["revision"] = "b" * 40
    elif case == "text":
        curation["entries"][0]["text"] = "invented wording"
    elif case == "traversal":
        curation["entries"][0]["path"] = "../outside.md"
    elif case == "tamper":
        (directory / "LICENSE").write_text("modified")
    elif case == "missing-file":
        manifest_path = directory / "manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["files"].pop("LICENSE")
        manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
    path.write_text(json.dumps(curation), encoding="utf-8")
    with pytest.raises(ValueError, match=message):
        load_curated_source(directory, path)


@pytest.mark.parametrize("source_id,revision,entries,recipes", [
    ("band-manager", "73c52379833af51e9d3ce7731746d3bfff3f5266", 88, 0),
    ("cookbook", "c8e40ff0b10636a7719cbc88bc5f58443ad19907-v0.4", 47, 3),
    ("lil-synn", "6b805bf77a350e7fba00bfd2451273327482827c", 24, 0),
])
def test_full_reviewed_source_if_available(tmp_path, source_id, revision, entries, recipes):
    directory = ROOT / "data" / "sources" / source_id / revision
    if not (directory / "manifest.json").exists():
        pytest.skip("Optional pinned source snapshot not fetched")
    bundle = load_curated_source(directory, ROOT / "curations" / f"{source_id}.json")
    assert len(bundle.entries) == entries
    assert len(bundle.recipes) == recipes
    with Store(tmp_path / "source.sqlite3") as store:
        assert store.import_bundle(bundle) == entries + recipes
        assert store.import_bundle(bundle) == 0
        result = store.export(bundle.source.snapshot_id)
        assert result.entries == sorted(bundle.entries, key=lambda entry: entry.id)
        assert result.source.license_text == (directory / "LICENSE").read_text(encoding="utf-8")
        for entry in result.entries:
            assert entry.evidence.independently_verified is False
            for citation in entry.citations:
                lines = (directory / citation.path).read_text(encoding="utf-8").splitlines()
                assert citation.excerpt in "\n".join(lines[citation.line_start - 1:citation.line_end])
        if source_id == "band-manager":
            legacy = next(e for e in result.entries if e.id.endswith(":refrain-legacy-limit"))
            assert legacy.evidence.model_scope == []
            assert "not re-tested" in legacy.evidence.source_label
        elif source_id == "cookbook":
            assert result.recipes[0].evidence.status == "unverified_example"
            assert "verified: false" in result.recipes[0].raw_record["markdown"]
            assert "Main Theme" in store.search("Main Theme", kind="phrase")[0]["entry"]["text"]
