"""Pinned task/retrieval audit, not a prompt composer or musical-effect test."""
from pathlib import Path
from typing import Literal

from pydantic import Field, model_validator

from .models import Model
from .store import Store


class TaskReference(Model):
    record_id: str
    contribution: str = Field(min_length=1)


class FoundationTask(Model):
    id: str
    brief: str = Field(min_length=1)
    dimensions: list[Literal["instrumentation", "vocals", "rhythm", "harmony",
                             "arrangement", "structure", "production", "controls"]] = Field(min_length=1)
    references: list[TaskReference] = Field(min_length=1)
    coverage: Literal["partial", "vocabulary_available"]
    missing: list[str] = Field(min_length=1)
    evidence_boundary: str = Field(min_length=1)
    future_assistant_check: str = Field(min_length=1)
    listening_question: str = Field(min_length=1)


class RetrievalProbe(Model):
    id: str
    task_id: str
    query: str
    scope: Literal["all", "v6_core"] = "all"
    required_ids: list[str] = Field(default_factory=list)
    forbidden_ids: list[str] = Field(default_factory=list)
    desired_but_missing_ids: list[str] = Field(default_factory=list)
    expect_empty: bool = False
    expand: bool = True
    disposition: Literal["supported", "retrieval_loss", "scope_boundary", "negative_control", "literal_baseline"]
    rationale: str = Field(min_length=1)

    @model_validator(mode="after")
    def coherent_expectations(self):
        required, forbidden, missing = map(set, (self.required_ids, self.forbidden_ids,
                                               self.desired_but_missing_ids))
        if required & (forbidden | missing) or (self.expect_empty and required):
            raise ValueError("Contradictory retrieval expectations")
        if self.disposition == "retrieval_loss" and not missing:
            raise ValueError("A retrieval loss needs a desired missing record")
        if missing and self.disposition not in ("retrieval_loss", "scope_boundary", "literal_baseline"):
            raise ValueError("Missing records require an explicit loss or scope disposition")
        return self


class FoundationTasks(Model):
    schema_version: Literal["1.0"] = "1.0"
    reviewed_on: str
    provenance: str
    snapshots: dict[str, str]
    tasks: list[FoundationTask] = Field(min_length=1)
    probes: list[RetrievalProbe] = Field(min_length=1)

    @model_validator(mode="after")
    def check_links(self):
        task_ids = [task.id for task in self.tasks]
        if len(set(task_ids)) != len(task_ids):
            raise ValueError("Duplicate foundation task")
        if len({probe.id for probe in self.probes}) != len(self.probes):
            raise ValueError("Duplicate retrieval probe")
        if any(probe.task_id not in task_ids for probe in self.probes):
            raise ValueError("Probe refers to unknown task")
        if set(task_ids) != {probe.task_id for probe in self.probes}:
            raise ValueError("Every task needs a retrieval probe")
        return self


def evaluate_tasks(store: Store, path: Path) -> dict:
    """Fail on changed observations; preserve known gaps explicitly in the report."""
    suite = FoundationTasks.model_validate_json(path.read_bytes())
    records = {}
    for source_id, snapshot_id in suite.snapshots.items():
        if store.active_snapshots().get(source_id) != snapshot_id:
            raise ValueError(f"Task audit requires the pinned active source: {source_id}")
        bundle = store.export(snapshot_id)
        records.update({record.id: (bundle.source, record) for record in [*bundle.entries, *bundle.recipes]})
    referenced = {reference.record_id for task in suite.tasks for reference in task.references}
    referenced.update(record_id for probe in suite.probes for record_id in
                      [*probe.required_ids, *probe.forbidden_ids, *probe.desired_but_missing_ids])
    if referenced - records.keys():
        raise ValueError(f"Unknown task references: {sorted(referenced - records.keys())}")
    observations = []
    for probe in suite.probes:
        hits = store.search(probe.query, limit=1000, v6_core=probe.scope == "v6_core", expand=probe.expand)
        hit_ids = {(hit.get("entry") or hit.get("recipe"))["id"] for hit in hits}
        missing_required = set(probe.required_ids) - hit_ids
        forbidden_found = set(probe.forbidden_ids) & hit_ids
        closed_gap = set(probe.desired_but_missing_ids) & hit_ids
        if missing_required or forbidden_found or closed_gap or (probe.expect_empty and hits):
            raise ValueError(f"Review changed retrieval observation {probe.id}: "
                             f"missing={sorted(missing_required)}, forbidden={sorted(forbidden_found)}, "
                             f"previous_gap_now_found={sorted(closed_gap)}, hits={len(hits)}")
        observations.append({"id": probe.id, "query": probe.query, "scope": probe.scope,
                             "hit_ids": sorted(hit_ids), "disposition": probe.disposition, "expand": probe.expand,
                             "desired_but_missing_ids": probe.desired_but_missing_ids})
    return {"status": "observations_matched_not_foundation_acceptance",
            "tasks": len(suite.tasks), "probes": observations,
            "open_retrieval_losses": [p.id for p in suite.probes if p.disposition == "retrieval_loss"],
            "task_gaps": {task.id: task.missing for task in suite.tasks},
            "note": "No generation effects or assistant behavior were tested. Coverage gaps remain open."}
