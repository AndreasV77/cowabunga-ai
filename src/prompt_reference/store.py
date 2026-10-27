import json
import sqlite3
from pathlib import Path

from .models import Bundle, Recipe, ReferenceEntry, Source
from .search import plan_query
from .workspace import WORKSPACE_MIGRATION
from .prompt_text import PROMPT_TEXT_MIGRATION


def evidence_filters(v6_core: bool = False, model_basis: str | None = None) -> tuple[list[str], list[str]]:
    if model_basis not in (None, "unspecified", "v6_targeted", "pre_v6"):
        raise ValueError("Unknown model basis")
    clauses, params = [], []
    if v6_core:
        clauses += ["r.snapshot_id IN (SELECT id FROM snapshots WHERE json_extract(source_json, '$.orientation')='v6_native')",
                    "json_extract(r.payload, '$.evidence.model_basis')='v6_targeted'"]
    if model_basis:
        clauses.append("COALESCE(json_extract(r.payload, '$.evidence.model_basis'), 'unspecified')=?")
        params.append(model_basis)
    return clauses, params

MIGRATIONS = [
    (
        "CREATE TABLE snapshots (id TEXT PRIMARY KEY, source_json TEXT NOT NULL)",
        "CREATE TABLE recipes (snapshot_id TEXT NOT NULL REFERENCES snapshots(id), id TEXT NOT NULL, payload TEXT NOT NULL, PRIMARY KEY(snapshot_id, id))",
        "CREATE VIRTUAL TABLE recipe_search USING fts5(snapshot_id UNINDEXED, recipe_id UNINDEXED, title, family, prompt, structure)",
    ),
    (
        "CREATE TABLE entries (snapshot_id TEXT NOT NULL REFERENCES snapshots(id), id TEXT NOT NULL, payload TEXT NOT NULL, PRIMARY KEY(snapshot_id, id))",
        "CREATE VIRTUAL TABLE entry_search USING fts5(snapshot_id UNINDEXED, entry_id UNINDEXED, kind UNINDEXED, text, meaning, category)",
    ),
    (
        "CREATE TABLE active_sources (source_id TEXT PRIMARY KEY, snapshot_id TEXT NOT NULL UNIQUE REFERENCES snapshots(id))",
    ),
    WORKSPACE_MIGRATION,
    PROMPT_TEXT_MIGRATION,
]


class Store:
    """Public storage interface. Source adapters do not access SQL directly."""

    def __init__(self, path: Path | str):
        self.connection = sqlite3.connect(path)
        self.connection.execute("PRAGMA foreign_keys=ON")
        current = self.connection.execute("PRAGMA user_version").fetchone()[0]
        if current > len(MIGRATIONS):
            self.close()
            raise ValueError("Database schema is newer than this application")
        with self.connection:
            self.connection.execute("BEGIN")
            for index in range(current, len(MIGRATIONS)):
                for statement in MIGRATIONS[index]:
                    self.connection.execute(statement)
                if index == 2:
                    candidates = {}
                    for snapshot_id, payload in self.connection.execute("SELECT id, source_json FROM snapshots ORDER BY id"):
                        source_id = Source.model_validate_json(payload).id
                        candidates.setdefault(source_id, []).append(snapshot_id)
                    # Do not guess between several historical versions during migration.
                    for source_id, snapshots in candidates.items():
                        if len(snapshots) == 1:
                            self.connection.execute("INSERT INTO active_sources VALUES (?, ?)", (source_id, snapshots[0]))
                self.connection.execute(f"PRAGMA user_version={index + 1}")

    def close(self):
        self.connection.close()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()

    def import_bundle(self, bundle: Bundle) -> int:
        ids = [record.id for record in [*bundle.recipes, *bundle.entries]]
        if len(set(ids)) != len(ids):
            raise ValueError("Duplicate record IDs")
        snapshot_id = bundle.source.snapshot_id
        existing = self.connection.execute("SELECT source_json FROM snapshots WHERE id=?", (snapshot_id,)).fetchone()
        if existing:
            previous = Source.model_validate_json(existing[0])
            old = self.export(snapshot_id)
            if (previous.model_dump(exclude={"retrieved_at"}) != bundle.source.model_dump(exclude={"retrieved_at"})
                    or old.recipes != sorted(bundle.recipes, key=lambda r: r.id)
                    or old.entries != sorted(bundle.entries, key=lambda r: r.id)):
                raise ValueError("Existing immutable snapshot differs from import")
            return 0
        with self.connection:
            self.connection.execute("INSERT INTO snapshots VALUES (?, ?)", (snapshot_id, bundle.source.model_dump_json()))
            for recipe in bundle.recipes:
                self.connection.execute("INSERT INTO recipes VALUES (?, ?, ?)", (snapshot_id, recipe.id, recipe.model_dump_json()))
                self.connection.execute("INSERT INTO recipe_search VALUES (?, ?, ?, ?, ?, ?)",
                                        (snapshot_id, recipe.id, recipe.title, recipe.family, recipe.style_prompt, recipe.structure))
            for entry in bundle.entries:
                self.connection.execute("INSERT INTO entries VALUES (?, ?, ?)", (snapshot_id, entry.id, entry.model_dump_json()))
                self.connection.execute("INSERT INTO entry_search VALUES (?, ?, ?, ?, ?, ?)",
                                        (snapshot_id, entry.id, entry.kind, entry.text, entry.meaning, entry.category))
            self.connection.execute("INSERT OR IGNORE INTO active_sources VALUES (?, ?)", (bundle.source.id, snapshot_id))
        return len(bundle.recipes) + len(bundle.entries)

    def snapshots(self) -> list[str]:
        return [row[0] for row in self.connection.execute("SELECT id FROM snapshots ORDER BY id")]

    def active_snapshots(self) -> dict[str, str]:
        return dict(self.connection.execute("SELECT source_id, snapshot_id FROM active_sources ORDER BY source_id"))

    def activate(self, snapshot_id: str) -> None:
        row = self.connection.execute("SELECT source_json FROM snapshots WHERE id=?", (snapshot_id,)).fetchone()
        if row is None:
            raise ValueError(f"Unknown snapshot: {snapshot_id}")
        source_id = Source.model_validate_json(row[0]).id
        with self.connection:
            self.connection.execute("INSERT INTO active_sources VALUES (?, ?) ON CONFLICT(source_id) DO UPDATE SET snapshot_id=excluded.snapshot_id", (source_id, snapshot_id))

    def stats(self, history: bool = False, v6_core: bool = False) -> dict:
        clauses, params = evidence_filters(v6_core)
        if not history:
            clauses.append("r.snapshot_id IN (SELECT snapshot_id FROM active_sources)")
        suffix = " WHERE " + " AND ".join(clauses) if clauses else ""
        entries = [ReferenceEntry.model_validate_json(row[0]) for row in self.connection.execute("SELECT r.payload FROM entries r" + suffix, params)]
        recipes = [Recipe.model_validate_json(row[0]) for row in self.connection.execute("SELECT r.payload FROM recipes r" + suffix, params)]
        from collections import Counter
        return {
            "scope": "history" if history else "active",
            "v6_core": v6_core,
            "recipes": len(recipes),
            "entries": len(entries),
            "categories": dict(sorted(Counter(entry.category for entry in entries).items())),
            "kinds": dict(sorted(Counter(entry.kind for entry in entries).items())),
            "active_snapshots": self.active_snapshots(),
            "total_snapshots": len(self.snapshots()),
            "model_basis": dict(sorted(Counter(record.evidence.model_basis if record.evidence else "unspecified" for record in [*entries, *recipes]).items())),
            "source_orientations": {source_id: self.export(snapshot).source.orientation for source_id, snapshot in self.active_snapshots().items()},
        }

    def search(self, query: str, limit: int = 20, snapshot: str | None = None, kind: str | None = None,
               history: bool = False, category: str | None = None,
               v6_core: bool = False, model_basis: str | None = None,
               expand: bool = True) -> list[dict]:
        if not 1 <= limit <= 1000:
            raise ValueError("limit must be between 1 and 1000")
        if kind not in (None, "recipe", "term", "phrase", "guidance"):
            raise ValueError("Unknown record kind")
        from typing import get_args
        categories = get_args(ReferenceEntry.model_fields["category"].annotation)
        if category is not None and category not in categories:
            raise ValueError("Unknown category")
        filters, filter_params = evidence_filters(v6_core, model_basis)
        # Quote every term, including reviewed aliases; never expose FTS operators.
        plan = plan_query(query, expand=expand)
        if not plan.term_groups:
            return []
        match = plan.match_expression()
        core_clauses, _ = evidence_filters(v6_core=True)
        priority = "CASE WHEN " + " AND ".join(core_clauses) + " THEN 0 ELSE 1 END"
        sql = f"""SELECT r.snapshot_id AS snapshot_id, r.id AS id, r.payload, 'recipe' AS kind, bm25(recipe_search) AS rank, {priority} AS core_priority FROM recipe_search s
                 JOIN recipes r ON r.snapshot_id=s.snapshot_id AND r.id=s.recipe_id
                 WHERE recipe_search MATCH ?"""
        params = [match]
        if snapshot:
            sql += " AND r.snapshot_id=?"
            params.append(snapshot)
        elif not history:
            sql += " AND r.snapshot_id IN (SELECT snapshot_id FROM active_sources)"
        if (kind is not None and kind != "recipe") or category:
            sql += " AND 0"
        entry_sql = f"""SELECT r.snapshot_id, r.id, r.payload, s.kind, bm25(entry_search) AS rank, {priority} AS core_priority FROM entry_search s
                       JOIN entries r ON r.snapshot_id=s.snapshot_id AND r.id=s.entry_id
                       WHERE entry_search MATCH ?"""
        entry_params = [match]
        if snapshot:
            entry_sql += " AND r.snapshot_id=?"
            entry_params.append(snapshot)
        elif not history:
            entry_sql += " AND r.snapshot_id IN (SELECT snapshot_id FROM active_sources)"
        if kind:
            entry_sql += " AND s.kind=?"
            entry_params.append(kind)
        if category:
            entry_sql += " AND s.category=?"
            entry_params.append(category)
        if filters:
            sql += " AND " + " AND ".join(filters)
            entry_sql += " AND " + " AND ".join(filters)
            params.extend(filter_params)
            entry_params.extend(filter_params)
        sql = f"{sql} UNION ALL {entry_sql} ORDER BY core_priority, rank, snapshot_id, id LIMIT ?"
        rows = self.connection.execute(sql, [*params, *entry_params, limit])
        results = []
        for snapshot_id, _, payload, record_kind, _, priority in rows:
            source = self.connection.execute("SELECT source_json FROM snapshots WHERE id=?", (snapshot_id,)).fetchone()[0]
            results.append({"snapshot_id": snapshot_id, "kind": record_kind, "v6_core": priority == 0,
                            "source": json.loads(source),
                            "recipe" if record_kind == "recipe" else "entry": json.loads(payload)})
        return results

    def export(self, snapshot_id: str) -> Bundle:
        row = self.connection.execute("SELECT source_json FROM snapshots WHERE id=?", (snapshot_id,)).fetchone()
        if row is None:
            raise ValueError(f"Unknown snapshot: {snapshot_id}")
        return Bundle(source=Source.model_validate_json(row[0]), recipes=[
            Recipe.model_validate_json(record[0]) for record in self.connection.execute(
                "SELECT payload FROM recipes WHERE snapshot_id=? ORDER BY id", (snapshot_id,))],
            entries=[ReferenceEntry.model_validate_json(record[0]) for record in self.connection.execute(
                "SELECT payload FROM entries WHERE snapshot_id=? ORDER BY id", (snapshot_id,))])
