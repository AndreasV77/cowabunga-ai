"""Pinned editorial crosschecks; agreement is not counted as experiment evidence."""
from pathlib import Path
from typing import Literal

from pydantic import Field

from .models import Model
from .store import Store


class Crosscheck(Model):
    id: str
    topic: str
    record_ids: list[str] = Field(min_length=2)
    assessment: Literal["complementary", "tension", "agreement"]
    conclusion: str
    evidence_limit: str
    primary_links: list[str] = Field(default_factory=list)
    independent_test_confirmation: Literal[False] = False


class ReviewSet(Model):
    schema_version: Literal["1.0"] = "1.0"
    reviewed_on: str
    snapshots: dict[str, str]
    cases: list[Crosscheck]


def resolve_reviews(store: Store, path: Path) -> dict:
    review = ReviewSet.model_validate_json(path.read_text(encoding="utf-8"))
    records = {}
    for source_id, snapshot_id in review.snapshots.items():
        bundle = store.export(snapshot_id)
        if bundle.source.id != source_id:
            raise ValueError("Review source/snapshot identity mismatch")
        records.update({record.id: (snapshot_id, record) for record in [*bundle.recipes, *bundle.entries]})
    cases = []
    for case in review.cases:
        if len(set(case.record_ids)) != len(case.record_ids):
            raise ValueError(f"Duplicate comparison record: {case.id}")
        if any(id not in records for id in case.record_ids):
            raise ValueError(f"Missing comparison record: {case.id}")
        cases.append({**case.model_dump(), "records": [
            {"snapshot_id": records[id][0], "record": records[id][1].model_dump(mode="json")}
            for id in case.record_ids]})
    return {"reviewed_on": review.reviewed_on, "snapshots": review.snapshots, "cases": cases}
