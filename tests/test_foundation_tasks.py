"""Task observations protect retrieval/evidence boundaries, not generation claims."""
import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from prompt_reference.foundation import INPUTS, load_inputs
from prompt_reference.foundation_tasks import FoundationTasks, RetrievalProbe, evaluate_tasks
from prompt_reference.models import Source
from prompt_reference.store import Store

ROOT = Path(__file__).resolve().parents[1]
TASKS = ROOT / "reviews/foundation-tasks.json"


@pytest.fixture(scope="module")
def corpus():
    for manifest, suffix, _ in INPUTS:
        pin = Source.model_validate_json((ROOT / "sources" / manifest).read_bytes())
        if not (ROOT / "data/sources" / pin.id / (pin.revision + suffix) / "manifest.json").exists():
            pytest.skip("Optional pinned input missing; strict validation requires all inputs")
    with Store(":memory:") as store:
        for bundle in load_inputs(ROOT):
            store.import_bundle(bundle)
        yield store


SUITE = FoundationTasks.model_validate_json(TASKS.read_bytes())


@pytest.mark.parametrize("probe", SUITE.probes, ids=lambda probe: probe.id)
def test_pinned_task_retrieval(corpus, probe):
    hits = corpus.search(probe.query, limit=1000, v6_core=probe.scope == "v6_core")
    ids = {(hit.get("entry") or hit.get("recipe"))["id"] for hit in hits}
    assert set(probe.required_ids) <= ids
    assert not ids.intersection(probe.forbidden_ids)
    assert not ids.intersection(probe.desired_but_missing_ids), "Review and update a resolved gap explicitly"
    if probe.expect_empty:
        assert not hits


def test_known_losses_stay_open_in_report(corpus):
    report = evaluate_tasks(corpus, TASKS)
    assert report["status"] == "observations_matched_not_foundation_acceptance"
    assert set(report["open_retrieval_losses"]) == {"gallop-word-form-loss", "exclude-wording-loss"}
    assert set(report["task_gaps"]) == {task.id for task in SUITE.tasks}
    assert all(report["task_gaps"].values())


@pytest.mark.parametrize("mutation,message", [
    ("unknown", "Unknown task references"),
    ("missing-required", "changed retrieval observation"),
    ("forbidden", "changed retrieval observation"),
    ("stale-pin", "pinned active source"),
])
def test_task_audit_rejects_broken_expectations(corpus, tmp_path, mutation, message):
    data = json.loads(TASKS.read_text(encoding="utf-8"))
    if mutation == "unknown":
        data["tasks"][0]["references"][0]["record_id"] = "invented:record"
    elif mutation == "missing-required":
        data["probes"][0]["query"] = "qzxnonexistentmusic"
    elif mutation == "forbidden":
        data["probes"][0]["forbidden_ids"] = ["band-manager:four-floor"]
        data["probes"][0]["scope"] = "all"
        data["probes"][0]["query"] = "four"
    else:
        data["snapshots"]["cookbook"] = "cookbook@stale"
    path = tmp_path / "tasks.json"
    path.write_text(json.dumps(data), encoding="utf-8")
    with pytest.raises(ValueError, match=message):
        evaluate_tasks(corpus, path)


def test_retrieval_loss_requires_explicit_target():
    with pytest.raises(ValidationError, match="desired missing record"):
        RetrievalProbe(id="loss", task_id="task", query="gallop", disposition="retrieval_loss",
                       rationale="Must identify the lost record")


def test_task_set_rejects_unlinked_probe():
    data = SUITE.model_dump()
    data["probes"][0]["task_id"] = "invented-task"
    with pytest.raises(ValidationError, match="unknown task"):
        FoundationTasks.model_validate(data)
