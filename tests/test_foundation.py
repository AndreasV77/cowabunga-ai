"""Failures of the strict gate must be failures, even with otherwise green tests."""
import json
import subprocess
import sys

import pytest

from prompt_reference.foundation import INPUTS, load_inputs, rebuild
from test_references import reference_bundle


def test_missing_inputs_report_all_sources(tmp_path):
    with pytest.raises(ValueError) as failure:
        load_inputs(tmp_path)
    for manifest, _, _ in INPUTS:
        assert manifest in str(failure.value)


def test_tracked_hashes_reject_locally_rehashed_manifest(tmp_path):
    source = reference_bundle().source
    (tmp_path / "sources").mkdir()
    local = tmp_path / "data/sources" / source.id / source.revision
    local.mkdir(parents=True)
    (tmp_path / "sources/musai-snapshot.json").write_text(source.model_dump_json())
    source.files = {"LICENSE": "a" * 64}
    (local / "manifest.json").write_text(source.model_dump_json())
    with pytest.raises(ValueError, match="Local files differs from tracked pin"):
        load_inputs(tmp_path)


def test_rebuild_refuses_existing_database_without_touching_it(tmp_path):
    database = tmp_path / "owner.sqlite3"
    database.write_bytes(b"owner data")
    with pytest.raises(ValueError, match="new database"):
        rebuild(tmp_path, database, [])
    assert database.read_bytes() == b"owner data"


@pytest.mark.parametrize("body,expected", [
    ("def test_ok(): assert True", 0),
    ("def test_fail(): assert False", 1),
    ("import pytest\ndef test_skip(): pytest.skip('missing input')", 1),
    ("import pytest\npytest.skip('missing module', allow_module_level=True)", 1),
    ("import pytest\n@pytest.mark.xfail\ndef test_expected_failure(): assert False", 1),
])
def test_strict_plugin_exit_status(tmp_path, body, expected):
    case = tmp_path / "test_case.py"
    case.write_text(body, encoding="utf-8")
    code = ("import pytest,sys; from prompt_reference.foundation import NoIncompleteTests; "
            "sys.exit(pytest.main([sys.argv[1], '-q'], plugins=[NoIncompleteTests()]))")
    result = subprocess.run([sys.executable, "-c", code, str(case)], cwd=tmp_path,
                            capture_output=True, text=True)
    assert (result.returncode == 0) == (expected == 0), result.stdout + result.stderr
    if "skip" in body or "xfail" in body:
        assert "STRICT VALIDATION INCOMPLETE" in result.stdout


def test_command_missing_inputs_writes_failed_report(tmp_path):
    report = tmp_path / "report.json"
    result = subprocess.run([sys.executable, "-m", "prompt_reference.foundation",
                             "--report", str(report)], cwd=tmp_path,
                            capture_output=True, text=True)
    assert result.returncode == 1, result.stdout + result.stderr
    assert json.loads(report.read_text())["status"] == "failed"
    assert "Required pinned inputs" in json.loads(report.read_text())["error"]
    original = report.read_bytes()
    again = subprocess.run([sys.executable, "-m", "prompt_reference.foundation",
                            "--report", str(report)], cwd=tmp_path, capture_output=True)
    assert again.returncode != 0
    assert report.read_bytes() == original
