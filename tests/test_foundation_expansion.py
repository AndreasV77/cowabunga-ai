"""The expansion adds context without rewriting old records or promoting claims."""
import subprocess
import sys
import shutil
from prompt_reference.adapters.curated import load_curated_source
from prompt_reference.concepts import CatalogService
from prompt_reference.foundation_tasks import evaluate_tasks
from prompt_reference.reviews import resolve_reviews
from prompt_reference.store import Store
from test_foundation_tasks import corpus, ROOT

ARCHIVE = ROOT / "curations/archive/0.11-foundation"
NEW_IDS = {
    "band-manager:choir", "band-manager:gospel-choir", "band-manager:tempo-feel-limits",
    "band-manager:positive-instrument-filling", "band-manager:negation-context-caveat",
    "cookbook:exclude-field-guidance", "cookbook:acoustic-section-entrances",
    "lil-synn:call-response", "lil-synn:half-time",
}


def test_historical_builders_cannot_overwrite_current_reviewed_data(tmp_path):
    (tmp_path / "tools").mkdir()
    (tmp_path / "curations/archive/0.11-foundation").mkdir(parents=True)
    (tmp_path / "reviews").mkdir()
    for module in (ROOT / "tools").glob("*.py"):
        shutil.copyfile(module, tmp_path / "tools" / module.name)
    relatives = [f"curations/{name}.json" for name in ("band-manager", "cookbook", "lil-synn", "concepts")]
    relatives.append("reviews/v6-crosschecks.json")
    for relative in relatives:
        shutil.copyfile(ROOT / relative, tmp_path / relative)
    paths = [tmp_path / relative for relative in relatives]
    before = {path: path.read_bytes() for path in paths}
    for script in ("build_seed_curations.py", "build_v6_core.py", "build_concepts.py"):
        shutil.copyfile(ROOT / "tools" / script, tmp_path / "tools" / script)
        result = subprocess.run([sys.executable, str(tmp_path / "tools" / script)], capture_output=True, text=True)
        assert result.returncode != 0
        assert "refusing to overwrite" in result.stdout + result.stderr
        assert before == {path: path.read_bytes() for path in paths}


def test_old_records_unchanged_and_activation_explicit(corpus, tmp_path):
    with Store(tmp_path / "upgrade.sqlite3") as store:
        old_pins = {}
        observed_added = set()
        for source_id, snapshot in corpus.active_snapshots().items():
            if source_id == "musai":
                continue
            new = corpus.export(snapshot)
            directory = ROOT / "data/sources" / source_id / (new.source.revision + ("-v0.4" if source_id == "cookbook" else ""))
            old = load_curated_source(directory, ARCHIVE / f"{source_id}.json")
            old_pins[source_id] = old.source.snapshot_id
            assert old.source.snapshot_id != new.source.snapshot_id
            assert old.source.files == new.source.files
            before = {e.id: e for e in old.entries}
            after = {e.id: e for e in new.entries}
            assert all(after[key] == value for key, value in before.items())
            assert sorted(old.recipes, key=lambda r: r.id) == new.recipes
            observed_added.update(after.keys() - before.keys())
            store.import_bundle(old)
            store.import_bundle(new)
            assert store.active_snapshots()[source_id] == old.source.snapshot_id
            store.activate(new.source.snapshot_id)
            assert store.export(old.source.snapshot_id) == old.model_copy(update={
                "entries": sorted(old.entries, key=lambda e: e.id),
                "recipes": sorted(old.recipes, key=lambda e: e.id)})
        assert observed_added == NEW_IDS
        # Historical catalog/reviews still resolve against their immutable snapshots.
        assert resolve_reviews(store, ARCHIVE / "v6-crosschecks.json")["snapshots"] == old_pins
        CatalogService(store, ARCHIVE / "concepts.json", ARCHIVE / "v6-crosschecks.json")


def test_new_context_and_gaps_keep_evidence_boundaries(corpus):
    records = {e.id: e for pin in corpus.active_snapshots().values() for e in corpus.export(pin).entries}
    for record_id in NEW_IDS:
        assert records[record_id].evidence.independently_verified is False
        assert records[record_id].evidence.test_count is None
    assert records["cookbook:exclude-field-guidance"].input_field is None
    assert "not" in records["band-manager:tempo-feel-limits"].meaning
    assert records["band-manager:negation-context-caveat"].evidence.model_basis == "unspecified"
    assert records["band-manager:choir"].evidence.model_scope == []
    report = evaluate_tasks(corpus, ROOT / "reviews/foundation-tasks.json")
    assert set(report["open_retrieval_losses"]) == {"gallop-word-form-loss", "exclude-wording-loss"}
    reviews = resolve_reviews(corpus, ROOT / "reviews/v6-crosschecks.json")
    caveat = next(case for case in reviews["cases"] if case["id"] == "negation-context")
    assert caveat["assessment"] == "tension"
    assert caveat["independent_test_confirmation"] is False
    service = CatalogService(corpus, ROOT / "curations/concepts.json", ROOT / "reviews/v6-crosschecks.json")
    packet = service.build_context(["positive-replacement"])
    assert any(case.id == "negation-context" for case in packet.crosschecks)
