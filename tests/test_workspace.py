import sqlite3
import json
from pathlib import Path

import pytest

from prompt_reference.store import Store, MIGRATIONS
from prompt_reference.workspace import WorkspaceRepository, WorkspaceConflict, Draft, Preferences


def test_revisioned_documents_survive_reopen_and_namespaces_are_isolated(tmp_path):
    database = tmp_path / "workspace.sqlite3"
    with Store(database) as store:
        repository = WorkspaceRepository(store.connection)
        assert repository.get_preferences("one", "user", "local") is None
        defaults = repository.save_preferences("one", "user", "local", {"language": "en"}, 0)
        draft = repository.create_draft("one", "  First song  ", {"intent": "Forward motion"}, None)
        assert draft.title == "First song"
        assert repository.list_drafts("two") == []
        assert repository.get_preferences("one", "artist", "local") is None
        with pytest.raises(KeyError):
            repository.get_draft("two", draft.id)
        with pytest.raises(WorkspaceConflict):
            repository.save_preferences("one", "user", "local", {"language": "de"}, 0)
        changed = repository.update_draft("one", draft.id, "Second", {}, {"ids": ["a"]}, 1)
        assert changed.revision == 2 and changed.created_at == draft.created_at
        with pytest.raises(WorkspaceConflict):
            repository.update_draft("one", draft.id, "Stale", {}, None, 1)
    with Store(database) as store:
        repository = WorkspaceRepository(store.connection)
        assert repository.get_preferences("one", "user", "local") == defaults
        assert repository.get_draft("one", draft.id) == changed
        updated = repository.save_preferences("one", "user", "local", {"language": "fr"}, 1)
        assert updated.revision == 2
        with pytest.raises(WorkspaceConflict):
            repository.save_preferences("one", "user", "local", {}, 1)
        assert repository.get_preferences("one", "user", "local") == updated


def test_v3_database_migrates_without_losing_existing_data(tmp_path):
    database = tmp_path / "old.sqlite3"
    with sqlite3.connect(database) as connection:
        for migration in MIGRATIONS[:3]:
            for statement in migration:
                connection.execute(statement)
        connection.execute("INSERT INTO active_sources VALUES ('existing', 'old@snapshot')")
        connection.execute("PRAGMA user_version=3")
    with Store(database) as store:
        assert store.connection.execute("SELECT snapshot_id FROM active_sources").fetchone()[0] == "old@snapshot"
        assert store.connection.execute("PRAGMA user_version").fetchone()[0] == len(MIGRATIONS)
        assert WorkspaceRepository(store.connection).list_drafts("one") == []


@pytest.mark.parametrize("name, contract", [("draft", Draft), ("preferences", Preferences)])
def test_workspace_schema_contracts_are_current(name, contract):
    path = Path(__file__).resolve().parents[1] / "schemas" / f"{name}.schema.json"
    assert json.loads(path.read_text(encoding="utf-8")) == contract.model_json_schema()
