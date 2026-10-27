import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from prompt_reference.listening import ListeningAssessment, ListeningDocument, RatedObservation, ListeningRepository
from prompt_reference.workspace import WorkspaceRepository, WorkspaceConflict
from prompt_reference.store import Store
from prompt_reference.adapters.challenge_listening import convert_report

ROOT = Path(__file__).resolve().parents[1]


def test_unassessed_is_distinct_from_zero_and_problems_have_no_numeric_score():
    report = ListeningAssessment()
    assert report.listening_value.immediate_replay is None
    assert report.listening_value.later_replay is None
    assert report.problems.sung_instructions == "unknown"
    for score in [-1, 3, "2", True]:
        with pytest.raises(ValidationError):
            RatedObservation(id="test", label="Test", score=score)
    with pytest.raises(ValidationError):
        ListeningAssessment(problems={"sung_instructions": 0})
    with pytest.raises(ValidationError):
        ListeningAssessment(independently_verified=True)
    with pytest.raises(ValidationError):
        ListeningAssessment(musical_execution=[RatedObservation(id="same", label="One"), RatedObservation(id="same", label="Two")])


def test_report_updates_retain_original_assessment_raw_evidence_and_draft_snapshot(tmp_path):
    with Store(tmp_path / "listening.sqlite3") as store:
        workspace = WorkspaceRepository(store.connection)
        draft = workspace.create_draft("prompt-reference", "First", {"intent": "Original direction"}, None)
        repository = ListeningRepository(workspace, draft.id)
        assessment = ListeningAssessment(raw_report={"value": 1}, generation={"provider": "Other provider", "settings": {"custom": "setting"}})
        saved = repository.create("First listen", assessment, draft)
        workspace.update_draft("prompt-reference", draft.id, "Changed", {"intent": "Changed"}, None, 1)
        revised = assessment.model_copy(deep=True)
        revised.listening_value.later_replay = 2
        updated = repository.update(saved.id, saved.title, revised, 1)
        assert updated.original_assessment == assessment
        assert updated.assessment.listening_value.later_replay == 2
        assert updated.draft_snapshot == draft
        with pytest.raises(WorkspaceConflict):
            repository.update(saved.id, "Stale", revised, 1)
        revised.raw_report = {"value": 2}
        with pytest.raises(ValueError, match="evidence"):
            repository.update(saved.id, "Changed evidence", revised, 2)
        assert repository.get(saved.id) == updated
        other = workspace.create_draft("prompt-reference", "Other", {}, None)
        with pytest.raises(KeyError):
            ListeningRepository(workspace, other.id).get(saved.id)
        with pytest.raises(ValueError, match="match"):
            repository.create("Wrong parent", assessment, other)


def test_legacy_challenge_conversion_preserves_raw_ratings_without_inventing_split_scores():
    # Synthetic legacy inputs: no personal listening history is shipped.
    base = {
        "actual_model": "V6 Standard", "weirdness": 50, "style_influence": 50,
        "observations": {"heavy_riff_and_drums": 2, "first_listen_replay_value": 2},
        "issue_observation": {"interpretation": "No listed problems heard",
                              "confirmation": "explicit_user_confirmation"},
        "prompt_identity_confirmation": {"source": "explicit_user_confirmation",
                                         "style": "Example style", "lyrics": "unchanged example lyrics"},
    }
    second_raw = base
    first_raw = {**base, "weirdness": 45, "style_influence": 85,
                 "observations": {**base["observations"], "heavy_riff_and_drums": 1},
                 "rating_qualifications": {"heavy_riff_and_drums": {"rated_property": "Thin sound"}}}
    first, second = convert_report(first_raw), convert_report(second_raw)
    assert first.raw_report == first_raw
    assert second.raw_report == second_raw
    assert first.sound_quality[0].score == 1
    assert second.sound_quality[0].score is None
    assert first.musical_execution[2].score is None
    assert second.musical_execution[2].score is None
    assert first.listening_value.later_replay is None
    assert second.problems.omitted_lyrics == "none"
    assert first.generation.settings["variety"] is None
    unconfirmed = {**second_raw, "prompt_identity_confirmation": {}}
    assert "unconfirmed" in convert_report(unconfirmed).generation.input_note


@pytest.mark.parametrize("name, contract", [("listening", ListeningAssessment), ("listening-document", ListeningDocument)])
def test_listening_contract_files_are_current(name, contract):
    assert json.loads((ROOT / "schemas" / f"{name}.schema.json").read_text(encoding="utf-8")) == contract.model_json_schema()
