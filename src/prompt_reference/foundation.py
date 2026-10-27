"""Strict checkout validation; never opens the owner's working database."""
import argparse
from collections import Counter
from datetime import datetime, timezone
import json
from pathlib import Path
import sqlite3
import tempfile

from .adapters.curated import load_curated_source
from .adapters.musai import load_snapshot
from .concepts import CatalogService, ContextPacket
from .foundation_tasks import evaluate_tasks
from .coverage import evaluate_coverage
from .models import Source
from .reviews import resolve_reviews
from .store import Store


# The expanded Cookbook pin is intentional. The older manifest remains history.
INPUTS = (
    ("musai-snapshot.json", "", None),
    ("band-manager-snapshot.json", "", "band-manager.json"),
    ("cookbook-expanded-snapshot.json", "-v0.4", "cookbook.json"),
    ("lil-synn-snapshot.json", "", "lil-synn.json"),
)


def load_inputs(root: Path):
    """Reject missing, substituted or self-consistently rehashed source inputs."""
    bundles = []
    errors = []
    for manifest, suffix, curation in INPUTS:
        try:
            pinned = Source.model_validate_json((root / "sources" / manifest).read_bytes())
            directory = root / "data/sources" / pinned.id / (pinned.revision + suffix)
            local = Source.model_validate_json((directory / "manifest.json").read_bytes())
            for field in ("id", "repository", "revision", "license", "files"):
                if getattr(local, field) != getattr(pinned, field):
                    raise ValueError(f"Local {field} differs from tracked pin")
            bundle = (load_curated_source(directory, root / "curations" / curation)
                      if curation else load_snapshot(directory))
            bundles.append(bundle)
        except (ValueError, OSError) as error:
            errors.append(f"{manifest}: {error}")
    if errors:
        raise ValueError("Required pinned inputs are unavailable or invalid:\n" + "\n".join(errors))
    return bundles


def rebuild(root: Path, database: Path, bundles):
    """Validate exact round trips, idempotency and all catalog links in a fresh store."""
    if database.exists():
        raise ValueError("Foundation rebuild requires a new database")
    imported = []
    with Store(database) as store:
        for bundle in bundles:
            expected = len(bundle.entries) + len(bundle.recipes)
            if store.import_bundle(bundle) != expected or store.import_bundle(bundle) != 0:
                raise ValueError(f"Import/idempotency mismatch: {bundle.source.id}")
            exported = store.export(bundle.source.snapshot_id)
            if (exported.source != bundle.source
                    or exported.entries != sorted(bundle.entries, key=lambda item: item.id)
                    or exported.recipes != sorted(bundle.recipes, key=lambda item: item.id)):
                raise ValueError(f"Round-trip mismatch: {bundle.source.id}")
            imported.append({"snapshot_id": bundle.source.snapshot_id,
                             "entries": len(bundle.entries), "recipes": len(bundle.recipes)})
        if store.connection.execute("PRAGMA integrity_check").fetchall() != [("ok",)]:
            raise ValueError("SQLite integrity check failed")
        if store.connection.execute("PRAGMA foreign_key_check").fetchall():
            raise ValueError("SQLite foreign key check failed")
        reviews_path = root / "reviews/v6-crosschecks.json"
        reviews = resolve_reviews(store, reviews_path)
        service = CatalogService(store, root / "curations/concepts.json", reviews_path)
        for concept in service.catalog.concepts:
            for supplementary in (False, True):
                packet = service.build_context([concept.id], supplementary=supplementary)
                ContextPacket.model_validate_json(packet.model_dump_json())
        return {"sources": imported, "stats": store.stats(), "v6_core": store.stats(v6_core=True),
                "task_audit": evaluate_tasks(store, root / "reviews/foundation-tasks.json"),
                "coverage_audit": evaluate_coverage(store, root / "reviews/coverage-scope.json", root / "reviews/foundation-tasks.json"),
                "concepts": len(service.catalog.concepts), "crosschecks": len(reviews["cases"])}


class NoIncompleteTests:
    """A green strict run cannot conceal collection skips, runtime skips or xfails."""
    def __init__(self):
        self.incomplete = set()
        self.outcomes = Counter()

    def pytest_collectreport(self, report):
        if report.skipped:
            self.incomplete.add(report.nodeid)

    def pytest_runtest_logreport(self, report):
        if report.skipped or getattr(report, "wasxfail", False):
            self.incomplete.add(report.nodeid)
        if report.when == "call":
            self.outcomes[report.outcome] += 1

    def pytest_deselected(self, items):
        self.incomplete.update(item.nodeid for item in items)

    def pytest_sessionfinish(self, session, exitstatus):
        if self.incomplete and not exitstatus:
            session.exitstatus = 1

    def pytest_terminal_summary(self, terminalreporter):
        if self.incomplete:
            terminalreporter.write_sep("=", "STRICT VALIDATION INCOMPLETE", red=True)
            for nodeid in sorted(self.incomplete):
                terminalreporter.write_line(nodeid)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report", type=Path, required=True,
                        help="New JSON report path; refuses to overwrite")
    args = parser.parse_args()
    root = Path.cwd()
    args.report.parent.mkdir(parents=True, exist_ok=True)
    # Reserve the report before expensive work; never overwrite prior evidence.
    with args.report.open("x", encoding="utf-8") as output:
        report = {"started_at": datetime.now(timezone.utc).isoformat(), "status": "failed",
                  "scope": "Mechanical validation only; not Gate 1 acceptance"}
        exit_code = 1
        try:
            import pytest  # Developer validation dependency, not a core requirement.
            bundles = load_inputs(root)
            scratch = root / "data/test-runs"
            scratch.mkdir(parents=True, exist_ok=True)
            with tempfile.TemporaryDirectory(prefix="foundation-", dir=scratch) as temporary:
                directory = Path(temporary)
                report["rebuild"] = rebuild(root, directory / "isolated.sqlite3", bundles)
                plugin = NoIncompleteTests()
                exit_code = int(pytest.main([str(root / "tests"), "-q", "--tb=short",
                                            f"--basetemp={directory / 'pytest'}"], plugins=[plugin]))
                report["tests"] = {"exit_code": exit_code, "outcomes": dict(plugin.outcomes),
                                   "incomplete": sorted(plugin.incomplete)}
                if exit_code == 0:
                    report["status"] = "passed"
        except (ValueError, OSError, sqlite3.Error, ImportError) as error:
            report["error"] = str(error)
            print(f"Foundation validation failed: {error}")
        finally:
            report["finished_at"] = datetime.now(timezone.utc).isoformat()
            json.dump(report, output, indent=2, ensure_ascii=False)
            output.write("\n")
    raise SystemExit(exit_code)


if __name__ == "__main__":
    main()
