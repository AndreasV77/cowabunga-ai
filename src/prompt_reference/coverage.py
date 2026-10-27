"""Auditable resource coverage, independent of retrieval or musical-effect claims."""
from collections import Counter
from pathlib import Path
from typing import Literal

from pydantic import Field, model_validator

from .foundation_tasks import FoundationTasks
from .models import Model, Recipe
from .store import Store


class CoverageLink(Model):
    record_id: str
    support: Literal["definition", "example", "guidance"]
    contribution: str = Field(min_length=1)


class CoverageRequirement(Model):
    id: str
    dimension: Literal["genre", "instrumentation", "vocals", "rhythm", "harmony",
                       "arrangement", "structure", "production", "controls"]
    need: str = Field(min_length=1)
    task_ids: list[str] = Field(min_length=1)
    references: list[CoverageLink]
    disposition: Literal["references_available", "selection_gap", "definition_gap",
                         "authored_relation", "effect_question"]
    next_action: str = Field(min_length=1)
    evidence_limit: str = Field(min_length=1)


class SourceDecision(Model):
    id: str
    url: str
    revision: str | None
    checked_on: str
    decision: Literal["retain", "discovery_only", "defer_legacy", "outside_scope",
                      "shortlist", "research_only"]
    evidence_urls: list[str] = Field(min_length=1)
    license_observation: str = Field(min_length=1)
    reason: str = Field(min_length=1)


class CoverageHoldout(Model):
    id: str
    brief: str = Field(min_length=1)
    requirement_ids: list[str] = Field(min_length=1)
    finding: str = Field(min_length=1)


class CoverageReview(Model):
    schema_version: Literal["1.0"] = "1.0"
    reviewed_on: str
    profile: str
    exclusions: list[str]
    snapshots: dict[str, str]
    requirements: list[CoverageRequirement] = Field(min_length=1)
    source_decisions: list[SourceDecision] = Field(min_length=1)
    holdouts: list[CoverageHoldout] = Field(min_length=1)

    @model_validator(mode="after")
    def unique_and_linked(self):
        for name in ("requirements", "source_decisions", "holdouts"):
            rows = getattr(self, name)
            if len({row.id for row in rows}) != len(rows):
                raise ValueError(f"Duplicate coverage {name}")
        known = {row.id for row in self.requirements}
        if any(not set(row.requirement_ids) <= known for row in self.holdouts):
            raise ValueError("Holdout has unknown coverage requirement")
        return self


def evaluate_coverage(store: Store, path: Path, tasks_path: Path) -> dict:
    review = CoverageReview.model_validate_json(path.read_bytes())
    tasks = FoundationTasks.model_validate_json(tasks_path.read_bytes())
    task_ids = {task.id for task in tasks.tasks}
    if review.snapshots != tasks.snapshots:
        raise ValueError("Coverage and task snapshots differ")
    records = {}
    for source_id, pin in review.snapshots.items():
        if store.active_snapshots().get(source_id) != pin:
            raise ValueError(f"Coverage requires active pinned source: {source_id}")
        bundle = store.export(pin)
        records.update({r.id: r for r in [*bundle.entries, *bundle.recipes]})
    retained = {source.id for source in review.source_decisions if source.decision == "retain"}
    if retained != set(review.snapshots):
        raise ValueError("Retained sources differ from admitted snapshots")
    for requirement in review.requirements:
        if not set(requirement.task_ids) <= task_ids:
            raise ValueError(f"Unknown task in coverage: {requirement.id}")
        for link in requirement.references:
            if link.record_id not in records:
                raise ValueError(f"Unknown coverage reference: {link.record_id}")
            if link.support == "definition" and isinstance(records[link.record_id], Recipe):
                raise ValueError("A recipe mention cannot stand in for a reference definition")
        if requirement.disposition == "references_available" and not requirement.references:
            raise ValueError("Available references require actual linked records")
    return {"status": "coverage_review_open_not_foundation_acceptance",
            "requirements": len(review.requirements),
            "dispositions": dict(Counter(row.disposition for row in review.requirements)),
            "vocabulary_gaps": [row.id for row in review.requirements
                                if row.disposition in ("definition_gap", "selection_gap")],
            "authored_relationships": [row.id for row in review.requirements if row.disposition == "authored_relation"],
            "effect_questions": [row.id for row in review.requirements if row.disposition == "effect_question"],
            "source_decisions": {row.id: row.decision for row in review.source_decisions},
            "holdouts": [row.model_dump() for row in review.holdouts],
            "note": "Links and editorial dispositions are checked; vocabulary presence is not a generation test or sufficient-coverage proof."}
