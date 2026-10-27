"""Explicit, reviewed source selections; no execution of upstream code/skills."""
import hashlib
import json
from typing import Literal
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import Request, urlopen

from ..models import Bundle, Citation, Evidence, Model, Recipe, ReferenceEntry, SettingsRecommendation, Source

BAND_PREFIX = "src/skills/suno-style-prompt-builder/references/"
BAND_TAGS = "src/skills/suno-lyric-transformer/references/metatag-reference.md"
DEFINITIONS = {
    "band-manager": {
        "repository": "https://github.com/zarlor/suno-band-manager",
        "license": "MIT", "license_url": "https://opensource.org/license/mit",
        "attribution": "zarlor / suno-band-manager; Copyright (c) 2026",
        "files": ("LICENSE", "README.md", BAND_TAGS, BAND_PREFIX + "v6-build-core.md",
                  BAND_PREFIX + "safety-tables.md", BAND_PREFIX + "research-sources.md"),
        "license_marker": "MIT License",
    },
    "cookbook": {
        "repository": "https://github.com/MJorgin/suno-v6-cookbook",
        "license": "CC-BY-4.0", "license_url": "https://creativecommons.org/licenses/by/4.0/",
        "attribution": "MJorgin and the Suno v6 Cookbook contributors; Copyright (c) 2026",
        "files": ("LICENSE", "README.md", "docs/case-schema.md", "docs/lyric-and-section-tags.md",
                  "docs/prompt-anatomy.md", "library/genres/acoustic-folk.md",
                  "library/genres/english-indie-pop.md", "library/genres/electronic-dance.md",
                  "library/examples/03-parking-lot-bloom.md"),
        "license_marker": "Creative Commons Attribution 4.0",
        "extra_files": ("library/examples/05-cassette-highway.md", "library/examples/07-break-the-silence.md"),
    },
    "lil-synn": {
        "repository": "https://github.com/LILSYNNOFFICIAL/LIL-SYNN-s-Complete-Suno-V6-Guide",
        "license": "CC0-1.0", "license_url": "https://creativecommons.org/publicdomain/zero/1.0/",
        "attribution": "LIL SYNN / LILSYNNOFFICIAL",
        "files": ("LICENSE", "README.md", "SUNO-V6-ULTIMATE-CONTROL-AND-PRODUCTION-ADDENDUM-2026.md",
                  "SUNO-V6-GAP-CLOSURE-ALL-REMAINING-CURRENT.md"),
        "license_marker": "CC0 1.0 Universal",
    },
}


def fetch_curated_source(source_id: str, revision: str, destination: Path) -> Source:
    definition = DEFINITIONS[source_id]
    source = Source(id=source_id, repository=definition["repository"], revision=revision,
                    license=definition["license"], retrieved_at=datetime.now(timezone.utc).isoformat(), files={})
    destination.mkdir(parents=True, exist_ok=False)
    for name in (*definition["files"], *definition.get("extra_files", ())):
        url = f"https://raw.githubusercontent.com/{source.repository.removeprefix('https://github.com/')}/{revision}/{name}"
        with urlopen(Request(url, headers={"User-Agent": "PromptReference/0.2"}), timeout=60) as response:
            data = response.read()
        target = destination / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
        source.files[name] = hashlib.sha256(data).hexdigest()
    (destination / "manifest.json").write_text(source.model_dump_json(indent=2), encoding="utf-8")
    return source


class Selection(Model):
    id: str
    kind: str
    path: str
    excerpt: str
    text: str
    meaning: str
    category: str
    evidence: Evidence
    input_field: str | None = None


class RecipeSelection(Model):
    id: str
    path: str
    title: str
    family: str
    style_prompt: str
    structure: str
    structure_excerpt: str
    exclude_styles: str
    evidence: Evidence
    workflow: str | None = None


class Curation(Model):
    source_id: str
    revision: str
    changes: str
    entries: list[Selection]
    recipes: list[RecipeSelection]
    orientation: Literal["unspecified", "mixed", "v6_native"] = "unspecified"
    orientation_excerpt: str | None = None


def locate(source: Source, path: str, excerpt: str, documents: dict[str, str]) -> Citation:
    if path not in documents or path == "LICENSE":
        raise ValueError(f"Unrecognized citation path: {path}")
    document = documents[path]
    if not excerpt or document.count(excerpt) != 1:
        raise ValueError(f"Citation excerpt must match exactly once in {path}: {excerpt[:60]}")
    offset = document.index(excerpt)
    start = document[:offset].count("\n") + 1
    end = start + excerpt.count("\n")
    return Citation(path=path, line_start=start, line_end=end,
                    url=f"{source.repository}/blob/{source.revision}/{path}#L{start}-L{end}", excerpt=excerpt)


def load_curated_source(directory: Path, curation_path: Path) -> Bundle:
    source = Source.model_validate_json((directory / "manifest.json").read_text(encoding="utf-8"))
    definition = DEFINITIONS.get(source.id)
    if definition is None or source.repository != definition["repository"] or source.license != definition["license"]:
        raise ValueError("Unknown source identity or license")
    allowed_sets = [set(definition["files"]), set((*definition["files"], *definition.get("extra_files", ())))]
    if set(source.files) not in allowed_sets:
        raise ValueError("Snapshot must contain the complete expected file set")
    documents = {}
    for name in source.files:
        data = (directory / name).read_bytes()
        if hashlib.sha256(data).hexdigest() != source.files[name]:
            raise ValueError(f"Snapshot checksum mismatch: {name}")
        documents[name] = data.decode("utf-8")
    if definition["license_marker"] not in documents["LICENSE"]:
        raise ValueError("Source license text does not match expected license")
    curation_bytes = curation_path.read_bytes()
    curation = Curation.model_validate_json(curation_bytes)
    if curation.source_id != source.id or curation.revision != source.revision:
        raise ValueError("Curation does not match source/revision")
    source.curation_sha256 = hashlib.sha256(curation_bytes).hexdigest()
    source.attribution = definition["attribution"]
    source.license_url = definition["license_url"]
    source.license_text = documents["LICENSE"]
    source.changes = curation.changes
    source.orientation = curation.orientation
    if curation.orientation != "unspecified":
        if not curation.orientation_excerpt:
            raise ValueError("Source orientation requires a reviewed README excerpt")
        citation = locate(source, "README.md", curation.orientation_excerpt, documents)
        source.orientation_basis = citation.url + " — " + citation.excerpt
    entries = []
    for selection in curation.entries:
        citation = locate(source, selection.path, selection.excerpt, documents)
        if selection.text not in selection.excerpt:
            raise ValueError(f"Selected wording absent from cited excerpt: {selection.id}")
        entries.append(ReferenceEntry(
            id=f"{source.id}:{selection.id}", kind=selection.kind, text=selection.text,
            meaning=selection.meaning, category=selection.category, input_field=selection.input_field,
            evidence=selection.evidence, citations=[citation]))
    recipes = []
    for selection in curation.recipes:
        document = documents.get(selection.path, "")
        # Cookbook examples are explicitly unverified. Refuse a silently changed source.
        if "verified: false" not in document:
            raise ValueError("Cookbook example verification status requires review")
        citations = [locate(source, selection.path, text, documents) for text in
                     (selection.style_prompt, selection.structure_excerpt, selection.exclude_styles)]
        if "language: en" not in document or f"evidence_tier: {selection.evidence.source_label}" not in document:
            raise ValueError("Cookbook example language/evidence metadata requires review")
        model_lines = [line.removeprefix("model: ") for line in document.splitlines() if line.startswith("model: ")]
        if selection.evidence.model_basis == "v6_targeted" and (len(model_lines) != 1 or model_lines[0] not in selection.evidence.model_scope):
            raise ValueError("Recipe model scope differs from source frontmatter")
        recipes.append(Recipe(
            id=f"{source.id}:{selection.id}", title=selection.title, family=selection.family,
            style_prompt=selection.style_prompt, structure=selection.structure,
            exclude_styles=selection.exclude_styles, settings=SettingsRecommendation(),
            evidence=selection.evidence, citations=citations, workflow=selection.workflow,
            source_record_url=f"{source.repository}/blob/{source.revision}/{selection.path}",
            raw_record={"path": selection.path, "markdown": document}))
    return Bundle(source=source, entries=entries, recipes=recipes)
