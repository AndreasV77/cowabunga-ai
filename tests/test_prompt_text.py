import json
import sqlite3
from pathlib import Path

import pytest
from pydantic import ValidationError

from prompt_reference.prompt_text import PromptText, PromptVersion, PromptVersionPage, PromptTextRepository, text_hash
from prompt_reference.workspace import WorkspaceRepository, WorkspaceConflict
from prompt_reference.store import Store, MIGRATIONS


def test_text_is_exact_history_is_append_only_and_reuse_preserves_both_links(tmp_path):
    database = tmp_path / "text.sqlite3"
    with Store(database) as store:
        workspace = WorkspaceRepository(store.connection)
        draft = workspace.create_draft("prompt-reference", "First", {"intent": "Original"}, None)
        repository = PromptTextRepository(store.connection)
        text = PromptText(style_prompt="  Drone 🔔\r\n", lyrics="[Verse]\nTiny bell\n\n")
        first = repository.save(draft, text, None, "First")
        assert first.style_sha256 == text_hash("  Drone 🔔\r\n")
        text.style_prompt = "Edited"
        assert first.content.style_prompt == "  Drone 🔔\r\n"
        second = repository.save(draft, text, first.id, "Edited", first.id)
        updated_draft = workspace.update_draft("prompt-reference", draft.id, "First", {"intent": "New context"}, None, 1)
        third = repository.save(updated_draft, first.content, second.id, "Reuse first", first.id)
        assert third.previous_id == second.id and third.based_on_id == first.id
        assert third.style_sha256 == first.style_sha256
        assert third.draft_snapshot.revision == 2
        assert repository.get(draft.id, first.id) == first
        assert first.draft_snapshot.revision == 1
        page = repository.list(draft.id, limit=1)
        assert page.head_id == third.id and page.items[0].version == 3 and page.has_more
        assert repository.list(draft.id, limit=1, offset=1).items[0].id == second.id
        assert PromptVersion.model_validate_json(third.model_dump_json()) == third
        with pytest.raises(WorkspaceConflict, match="history changed"):
            repository.save(updated_draft, text, first.id)
        with pytest.raises(WorkspaceConflict, match="draft changed"):
            repository.save(draft, text, third.id)
        with pytest.raises(KeyError):
            repository.save(updated_draft, text, third.id, based_on_id="missing")
        assert len(repository.list(draft.id).items) == 3
        assert repository.head_id(draft.id) == third.id
        tampered = third.model_dump(mode="json")
        tampered["content"]["lyrics"] += "changed"
        with pytest.raises(ValidationError, match="hashes"):
            PromptVersion.model_validate(tampered)
    with Store(database) as store:
        assert PromptTextRepository(store.connection).get(draft.id, first.id).content.lyrics == "[Verse]\nTiny bell\n\n"


def test_v4_migration_preserves_existing_workspace_documents(tmp_path):
    database = tmp_path / "old.sqlite3"
    with sqlite3.connect(database) as connection:
        for migration in MIGRATIONS[:4]:
            for statement in migration:
                connection.execute(statement)
        connection.execute("PRAGMA user_version=4")
        draft = WorkspaceRepository(connection).create_draft("prompt-reference", "Old", {}, None)
    with Store(database) as store:
        assert store.connection.execute("PRAGMA user_version").fetchone()[0] == len(MIGRATIONS)
        assert WorkspaceRepository(store.connection).get_draft("prompt-reference", draft.id) == draft
        assert PromptTextRepository(store.connection).list(draft.id).items == []


@pytest.mark.parametrize("name, contract", [("prompt-text", PromptText), ("prompt-version", PromptVersion), ("prompt-history", PromptVersionPage)])
def test_prompt_contract_schemas_are_current(name, contract):
    path = Path(__file__).resolve().parents[1] / "schemas" / f"{name}.schema.json"
    assert json.loads(path.read_text(encoding="utf-8")) == contract.model_json_schema()
