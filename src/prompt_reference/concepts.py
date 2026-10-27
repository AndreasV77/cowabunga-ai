"""Reviewed concept links and deterministic, provider-independent context packets."""
import hashlib
from pathlib import Path
from typing import Literal

from pydantic import Field, model_validator

from .models import Model, Recipe, ReferenceEntry, Source
from .reviews import Crosscheck, ReviewSet
from .store import Store


class ConceptLink(Model):
    record_id: str
    relation: Literal["wording", "dimension", "example", "alternative"]
    note: str = Field(min_length=1)


class Concept(Model):
    id: str = Field(pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
    label: str
    aliases: list[str] = Field(default_factory=list)
    description: str
    links: list[ConceptLink] = Field(min_length=1)
    crosscheck_ids: list[str] = Field(default_factory=list)


class ConceptCatalog(Model):
    schema_version: Literal["1.0"] = "1.0"
    version: str
    reviewed_on: str
    snapshots: dict[str, str]
    reviews_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    concepts: list[Concept]

    @model_validator(mode="after")
    def unique_links(self):
        ids = [concept.id for concept in self.concepts]
        if len(ids) != len(set(ids)):
            raise ValueError("Duplicate concept IDs")
        for concept in self.concepts:
            refs = [link.record_id for link in concept.links]
            if len(refs) != len(set(refs)):
                raise ValueError(f"Duplicate concept links: {concept.id}")
        return self


class ConceptUse(Model):
    concept_id: str
    relation: Literal["wording", "dimension", "example", "alternative"]
    note: str


class ContextItem(Model):
    snapshot_id: str
    v6_core: bool
    uses: list[ConceptUse]
    record: ReferenceEntry | Recipe


class ContextOmission(Model):
    record_id: str
    reason: Literal["outside_v6_core", "model_scope_mismatch", "limit", "user_deselected"]


class ContextPacket(Model):
    schema_version: Literal["1.0"] = "1.0"
    intent: str
    target_model: Literal["v6", "v6-wild", "v6-mini"]
    catalog_sha256: str
    catalog_version: str
    concepts: list[Concept]
    items: list[ContextItem]
    sources: dict[str, Source]
    crosschecks: list[Crosscheck]
    omitted: list[ContextOmission]
    independently_verified: Literal[False] = False

    @model_validator(mode="after")
    def check_packet_provenance(self):
        for snapshot_id, source in self.sources.items():
            if snapshot_id != source.snapshot_id:
                raise ValueError("Context source snapshot key differs from source metadata")
        seen = set()
        for item in self.items:
            if item.snapshot_id not in self.sources:
                raise ValueError("Context item is missing source metadata")
            key = (item.snapshot_id, item.record.id)
            if key in seen:
                raise ValueError("Duplicate context record")
            seen.add(key)
            source = self.sources[item.snapshot_id]
            core = source.orientation == "v6_native" and item.record.evidence is not None and item.record.evidence.model_basis == "v6_targeted"
            if item.v6_core != core:
                raise ValueError("Context core flag differs from record/source evidence")
        return self


def select_items(packet: ContextPacket, selected_ids: list[str]) -> ContextPacket:
    selected = set(selected_ids)
    known = {item.record.id for item in packet.items}
    if not selected or not selected <= known:
        raise ValueError("Choose at least one available candidate")
    result = packet.model_copy(deep=True)
    result.omitted.extend(ContextOmission(record_id=item.record.id, reason="user_deselected")
                          for item in packet.items if item.record.id not in selected)
    result.items = [item for item in result.items if item.record.id in selected]
    return ContextPacket.model_validate(result.model_dump())


class CatalogService:
    def __init__(self, store: Store, catalog_path: Path, reviews_path: Path):
        payload = catalog_path.read_bytes()
        self.catalog = ConceptCatalog.model_validate_json(payload)
        self.sha256 = hashlib.sha256(payload).hexdigest()
        reviews_bytes = reviews_path.read_bytes()
        if hashlib.sha256(reviews_bytes).hexdigest() != self.catalog.reviews_sha256:
            raise ValueError("Crosscheck file changed; review the concept catalog before reuse")
        self.reviews = ReviewSet.model_validate_json(reviews_bytes)
        self.store = store
        self.sources = {}
        self.records = {}
        self.record_snapshots = {}
        for source_id, snapshot_id in self.catalog.snapshots.items():
            bundle = store.export(snapshot_id)
            if bundle.source.id != source_id:
                raise ValueError("Concept source/snapshot identity mismatch")
            self.sources[snapshot_id] = bundle.source
            for record in [*bundle.recipes, *bundle.entries]:
                if record.id in self.records:
                    raise ValueError(f"Ambiguous concept record identity: {record.id}")
                self.records[record.id] = record
                self.record_snapshots[record.id] = snapshot_id
        cases = {case.id: case for case in self.reviews.cases}
        for concept in self.catalog.concepts:
            for link in concept.links:
                if link.record_id not in self.records:
                    raise ValueError(f"Missing concept record: {link.record_id}")
            for case_id in concept.crosscheck_ids:
                if case_id not in cases:
                    raise ValueError(f"Missing concept crosscheck: {case_id}")
                for record_id in cases[case_id].record_ids:
                    source_id = record_id.split(":", 1)[0]
                    if self.reviews.snapshots.get(source_id) != self.catalog.snapshots.get(source_id):
                        raise ValueError("Concept and crosscheck snapshots differ")
                    if record_id not in self.records:
                        raise ValueError(f"Missing crosscheck record: {record_id}")

    def find(self, query: str = "") -> list[Concept]:
        tokens = query.casefold().split()
        return [concept for concept in self.catalog.concepts
                if all(token in " ".join([concept.id, concept.label, concept.description, *concept.aliases]).casefold() for token in tokens)]

    def build_context(self, concept_ids: list[str], intent: str = "", target_model: str = "v6",
                      supplementary: bool = False, limit: int = 24) -> ContextPacket:
        if target_model not in ("v6", "v6-wild", "v6-mini"):
            raise ValueError("Unsupported target model")
        if not 1 <= limit <= 100:
            raise ValueError("Context limit must be between 1 and 100")
        if not concept_ids:
            raise ValueError("Select at least one concept")
        by_id = {concept.id: concept for concept in self.catalog.concepts}
        unknown = set(concept_ids) - set(by_id)
        if unknown:
            raise ValueError("Unknown concepts: " + ", ".join(sorted(unknown)))
        selected = [by_id[id] for id in dict.fromkeys(concept_ids)]
        active = self.store.active_snapshots()
        candidates, omitted = {}, {}
        for concept in selected:
            for link in concept.links:
                record = self.records[link.record_id]
                snapshot = self.record_snapshots[link.record_id]
                source = self.sources[snapshot]
                core = source.orientation == "v6_native" and record.evidence is not None and record.evidence.model_basis == "v6_targeted"
                if not core and not supplementary:
                    omitted[record.id] = ContextOmission(record_id=record.id, reason="outside_v6_core")
                    continue
                scope = record.evidence.model_scope if record.evidence else []
                if scope and target_model not in scope:
                    omitted[record.id] = ContextOmission(record_id=record.id, reason="model_scope_mismatch")
                    continue
                if active.get(source.id) != snapshot:
                    raise ValueError(f"Catalog selection is inactive for {source.id}; explicitly activate it or review/rebuild the catalog")
                if record.id not in candidates:
                    candidates[record.id] = ContextItem(snapshot_id=snapshot, v6_core=core, uses=[], record=record)
                candidates[record.id].uses.append(ConceptUse(concept_id=concept.id, relation=link.relation, note=link.note))
        # Preserve concept order within the V6/supplementary groups. No implicit synonym merging.
        ranked = sorted(candidates.values(), key=lambda item: not item.v6_core)
        for item in ranked[limit:]:
            omitted[item.record.id] = ContextOmission(record_id=item.record.id, reason="limit")
        items = ranked[:limit]
        used_snapshots = {item.snapshot_id for item in items}
        case_ids = {id for concept in selected for id in concept.crosscheck_ids}
        crosschecks = [case for case in self.reviews.cases if case.id in case_ids]
        # Include exact source metadata needed to interpret the crosscheck references as well.
        for case in crosschecks:
            for id in case.record_ids:
                used_snapshots.add(self.record_snapshots[id])
        return ContextPacket(intent=intent, target_model=target_model, catalog_sha256=self.sha256,
            catalog_version=self.catalog.version, concepts=selected, items=items,
            sources={id: self.sources[id] for id in sorted(used_snapshots)}, crosschecks=crosschecks,
            omitted=list(omitted.values()))


def render_context(packet: ContextPacket) -> str:
    lines = ["# Music prompt context", "", f"Target model: {packet.target_model}",
             f"Intent: {packet.intent}", "", "Selected concepts: " + ", ".join(c.label for c in packet.concepts), "",
             "These are source-bound candidates, not a finished prompt or verified effect claims.",
             "Alternatives and related dimensions are listed for selection; do not automatically combine every candidate.", ""]
    for item in packet.items:
        record = item.record
        title = record.text if isinstance(record, ReferenceEntry) else record.title
        lines += [f"## {title}", "", f"Scope: {'V6 core' if item.v6_core else 'supplementary'}; snapshot: {item.snapshot_id}", ""]
        lines += [f"- Concept: {use.concept_id}; relation: {use.relation}. {use.note}" for use in item.uses]
        lines.append("")
        if isinstance(record, ReferenceEntry):
            lines += [f"Field: {record.input_field or 'not a generation field'}", record.meaning, "", "````text", record.text, "````", ""]
        else:
            lines += ["Style recipe:", "````text", record.style_prompt, "````", ""]
            if record.exclude_styles:
                lines += ["Separate source exclusions (not mixed into the style text):", "````text", record.exclude_styles, "````", ""]
        if record.evidence:
            lines += [f"Source evidence: {record.evidence.source_label}; model basis: {record.evidence.model_basis}.", record.evidence.context, ""]
        for citation in record.citations:
            lines.append(f"Source: [{citation.path}, L{citation.line_start}]({citation.url})")
        lines.append("")
    if packet.crosschecks:
        lines += ["## Relevant counterchecks", ""]
        for case in packet.crosschecks:
            lines += [f"- {case.topic} ({case.assessment}): {case.conclusion} {case.evidence_limit}"]
        lines.append("")
    if packet.omitted:
        lines += ["## Omitted candidates", ""]
        lines += [f"- {item.record_id}: {item.reason}" for item in packet.omitted]
        lines.append("")
    lines += ["## Source attribution and notices", ""]
    for id, source in packet.sources.items():
        lines += [f"### {source.id}", "", f"{source.attribution or source.id} — {source.repository}",
                  f"License: {source.license_url or source.license}", f"Changes: {source.changes or 'No additional adaptation recorded'}", ""]
        if source.license_text:
            lines += ["````text", source.license_text, "````", ""]
    return "\n".join(lines) + "\n"
