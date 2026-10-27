import hashlib
import json

import pytest
from pydantic import ValidationError

from prompt_reference.adapters.musai import FILES, REPOSITORY, load_snapshot
from prompt_reference.models import Bundle, Recipe, SettingsRecommendation, Source
from prompt_reference.store import Store


@pytest.fixture
def bundle():
    return Bundle(source=Source(id="musai", repository=REPOSITORY, revision="a" * 40,
                                license="CC0-1.0", retrieved_at="2026-10-26T00:00:00Z", files={}),
                  recipes=[Recipe(id="musai:test", title="Free Jazz", family="Jazz",
                                  style_prompt="Free jazz, acoustic bass, loose drums",
                                  structure="[Intro] → [Improvisation]", source_record_url="https://musaisong.app/en/style/test",
                                  settings=SettingsRecommendation(bpm=None, weirdness=60, style_influence=90),
                                  raw_record={"bpm": None})])


def test_round_trip_search_and_idempotency(tmp_path, bundle):
    with Store(tmp_path / "test.sqlite3") as store:
        assert store.import_bundle(bundle) == 1
        assert store.import_bundle(bundle) == 0
        snapshot = store.snapshots()[0]
        assert store.export(snapshot) == bundle
        assert store.search("acoustic bass")[0]["recipe"]["settings"]["bpm"] is None
        assert store.search("missing") == []
        assert store.search("") == []
        assert store.search('" OR jazz --') == []
        assert store.search("jazz", snapshot="missing") == []
    with Store(tmp_path / "test.sqlite3") as reopened:
        assert reopened.export(snapshot) == bundle


def test_snapshots_coexist_and_conflicts_do_not_overwrite(tmp_path, bundle):
    with Store(tmp_path / "test.sqlite3") as store:
        store.import_bundle(bundle)
        changed = bundle.model_copy(deep=True)
        changed.recipes[0].title = "Changed"
        with pytest.raises(ValueError, match="immutable"):
            store.import_bundle(changed)
        changed.source.revision = "b" * 40
        store.import_bundle(changed)
        assert len(store.snapshots()) == 2
        assert len(store.search("acoustic")) == 1
        assert len(store.search("acoustic", history=True)) == 2


def test_duplicate_ids_leave_no_partial_snapshot(tmp_path, bundle):
    bundle.recipes.append(bundle.recipes[0])
    with Store(tmp_path / "test.sqlite3") as store:
        with pytest.raises(ValueError, match="Duplicate"):
            store.import_bundle(bundle)
        assert store.snapshots() == []


def test_transaction_rolls_back_on_storage_failure(tmp_path, bundle):
    with Store(tmp_path / "test.sqlite3") as store:
        store.connection.execute("CREATE TRIGGER reject_recipe BEFORE INSERT ON recipes BEGIN SELECT RAISE(ABORT, 'test failure'); END")
        import sqlite3
        with pytest.raises(sqlite3.IntegrityError):
            store.import_bundle(bundle)
        assert store.snapshots() == []
        assert store.search("jazz") == []


def test_reject_invalid_settings():
    with pytest.raises(ValidationError):
        SettingsRecommendation(bpm=0)
    with pytest.raises(ValidationError):
        SettingsRecommendation(weirdness=101)
    with pytest.raises(ValidationError):
        SettingsRecommendation(style_influence="90")


def write_snapshot(path, *, count=1, license="CC0-1.0", duplicate=False):
    row = dict(style="Free Jazz", family="Jazz", bpm=None, weirdness=60,
               style_influence=90, style_prompt="Free jazz", structure="[Improvisation]",
               url="https://musaisong.app/en/style/test")
    payload = dict(count=count, license=license, source="https://musaisong.app/en/styles",
                   repository=REPOSITORY, dataset="https://huggingface.co/datasets/musaisong/suno-style-recipes",
                   styles=[row, row] if duplicate else [row])
    for name in FILES:
        (path / name).write_text(json.dumps(payload) if name == "styles.json" else "source", encoding="utf-8")
    source = Source(id="musai", repository=REPOSITORY, revision="a" * 40, license="CC0-1.0",
                    retrieved_at="2026-10-26T00:00:00Z",
                    files={name: hashlib.sha256((path / name).read_bytes()).hexdigest() for name in FILES})
    (path / "manifest.json").write_text(source.model_dump_json(), encoding="utf-8")


def test_adapter_preserves_source_and_unknown_model(tmp_path):
    write_snapshot(tmp_path)
    bundle = load_snapshot(tmp_path)
    assert bundle.recipes[0].raw_record["bpm"] is None
    assert bundle.recipes[0].settings.model_version is None
    assert bundle.recipes[0].settings.evidence == "publisher_recommendation"


@pytest.mark.parametrize("case, message", [("tamper", "checksum"), ("count", "count"), ("license", "license"), ("duplicate", "Duplicate")])
def test_adapter_rejects_invalid_snapshot(tmp_path, case, message):
    write_snapshot(tmp_path, count=2 if case in ("count", "duplicate") else 1,
                   license="unknown" if case == "license" else "CC0-1.0", duplicate=case == "duplicate")
    if case == "tamper":
        (tmp_path / "styles.json").write_text("{}")
    with pytest.raises(ValueError, match=message):
        load_snapshot(tmp_path)


def test_future_database_version_rejected(tmp_path):
    import sqlite3
    path = tmp_path / "future.sqlite3"
    with sqlite3.connect(path) as connection:
        connection.execute("PRAGMA user_version=99")
    with pytest.raises(ValueError, match="newer"):
        Store(path)


def test_cli_pipeline(tmp_path):
    import subprocess
    import sys
    source = tmp_path / "source"
    source.mkdir()
    write_snapshot(source)
    db = tmp_path / "cli.sqlite3"

    def run(*args):
        return subprocess.run([sys.executable, "-m", "prompt_reference.cli", "--db", str(db), *map(str, args)],
                              capture_output=True, text=True, encoding="utf-8")

    assert json.loads(run("import-musai", source).stdout)["imported"] == 1
    assert json.loads(run("import-musai", source).stdout)["imported"] == 0
    snapshot = json.loads(run("snapshots").stdout)[0]
    assert json.loads(run("search", "jazz").stdout)[0]["snapshot_id"] == snapshot
    output = tmp_path / "export.json"
    assert run("export", snapshot, output).returncode == 0
    exported = Bundle.model_validate_json(output.read_text(encoding="utf-8"))
    assert exported.recipes[0].raw_record["bpm"] is None
    assert run("export", snapshot, output).returncode == 1
    assert run("export", "unknown", tmp_path / "missing.json").returncode == 1
    assert not (tmp_path / "missing.json").exists()


def test_full_pinned_musai_snapshot_if_available(tmp_path):
    from pathlib import Path
    revision = "e34ad57e3450efccf792d1e4e1685ca089ce3c25"
    directory = Path(__file__).resolve().parents[1] / "data" / "sources" / "musai" / revision
    if not (directory / "manifest.json").exists():
        pytest.skip("Optional real-source snapshot has not been fetched")
    bundle = load_snapshot(directory)
    original = json.loads((directory / "styles.json").read_text(encoding="utf-8"))
    assert len(bundle.recipes) == 564
    with Store(tmp_path / "full.sqlite3") as store:
        assert store.import_bundle(bundle) == 564
        assert store.import_bundle(bundle) == 0
        exported = Bundle.model_validate_json(store.export(store.snapshots()[0]).model_dump_json())
        assert {r.source_record_url: r.raw_record for r in exported.recipes} == {r["url"]: r for r in original["styles"]}
        assert all(r.settings.model_version is None for r in exported.recipes)
        assert sum(r.settings.bpm is None for r in exported.recipes) == sum(r["bpm"] is None for r in original["styles"])
        assert store.search("acoustic bass")
