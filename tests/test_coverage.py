import json

import pytest
from pydantic import ValidationError

from prompt_reference.coverage import CoverageReview, evaluate_coverage
from test_foundation_tasks import corpus, ROOT

PATH = ROOT / "reviews/coverage-scope.json"
TASKS = ROOT / "reviews/foundation-tasks.json"


def test_coverage_keeps_missing_definitions_and_authored_relations_distinct(corpus):
    before = corpus.active_snapshots()
    report = evaluate_coverage(corpus, PATH, TASKS)
    assert report["status"] == "coverage_review_open_not_foundation_acceptance"
    assert set(report["vocabulary_gaps"]) == {
        "meter-and-grouping", "chord-quality", "tonal-modal-color",
        "harmonic-function", "harmonic-pedal", "overtone-technique",
    }
    assert set(report["authored_relationships"]) == {
        "instrument-dependencies", "change-and-invariants", "small-contrast",
    }
    assert set(report["historical_gaps"]) == {"genre-lineage", "regional-evolution"}
    assert report["source_decisions"]["musicmap"] == "research_only"
    assert report["source_decisions"]["tonal"] == "shortlist"
    assert report["source_decisions"]["open-music-theory"] == "shortlist"
    assert corpus.active_snapshots() == before
    assert len(report["holdouts"]) == 4


@pytest.mark.parametrize("case,expected", [
    ("recipe-as-definition", "recipe mention"),
    ("unknown-task", "Unknown task"),
    ("missing-reference", "Unknown coverage reference"),
    ("stale-pin", "snapshots differ"),
    ("unadmitted-source", "Retained sources differ"),
])
def test_coverage_rejects_invalid_support(corpus, tmp_path, case, expected):
    data = json.loads(PATH.read_text(encoding="utf-8"))
    if case == "recipe-as-definition":
        data["requirements"][0]["references"][0]["support"] = "definition"
    elif case == "unknown-task":
        data["requirements"][0]["task_ids"] = ["invented-task"]
    elif case == "missing-reference":
        data["requirements"][0]["references"][0]["record_id"] = "invented:record"
    elif case == "stale-pin":
        data["snapshots"]["cookbook"] = "cookbook@stale"
    else:
        next(row for row in data["source_decisions"] if row["id"] == "tonal")["decision"] = "retain"
    path = tmp_path / "coverage.json"
    path.write_text(json.dumps(data), encoding="utf-8")
    with pytest.raises(ValueError, match=expected):
        evaluate_coverage(corpus, path, TASKS)


def test_holdout_must_reference_an_actual_requirement():
    data = json.loads(PATH.read_text(encoding="utf-8"))
    data["holdouts"][0]["requirement_ids"] = ["invented-requirement"]
    with pytest.raises(ValidationError, match="unknown coverage requirement"):
        CoverageReview.model_validate(data)
