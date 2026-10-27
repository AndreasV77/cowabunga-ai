import hashlib
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import Request, urlopen

from pydantic import Field

from ..models import Bundle, Model, Recipe, SettingsRecommendation, Source

REPOSITORY = "https://github.com/samuelgrupolimex-prog/suno-style-recipes"
FILES = ("styles.json", "LICENSE", "README.md", "datapackage.json")


class MusaiRow(Model):
    style: str = Field(min_length=1)
    family: str
    bpm: int | None = Field(gt=0)
    weirdness: int = Field(ge=0, le=100)
    style_influence: int = Field(ge=0, le=100)
    style_prompt: str = Field(min_length=1)
    structure: str
    url: str = Field(pattern=r"^https://musaisong\.app/")


class MusaiDataset(Model):
    count: int = Field(ge=1)
    license: str
    source: str
    repository: str
    dataset: str
    styles: list[MusaiRow]


def fetch_snapshot(destination: Path, revision: str) -> Source:
    """Fetch immutable source files; never overwrite an existing snapshot directory."""
    # Validate revision before using it in a URL or path.
    Source(id="musai", repository=REPOSITORY, revision=revision,
           license="CC0-1.0", retrieved_at="", files={})
    destination.mkdir(parents=True, exist_ok=False)
    hashes = {}
    for name in FILES:
        url = f"https://raw.githubusercontent.com/samuelgrupolimex-prog/suno-style-recipes/{revision}/{name}"
        with urlopen(Request(url, headers={"User-Agent": "PromptReference/0.1"}), timeout=60) as response:
            payload = response.read()
        (destination / name).write_bytes(payload)
        hashes[name] = hashlib.sha256(payload).hexdigest()
    source = Source(id="musai", repository=REPOSITORY, revision=revision,
                    license="CC0-1.0", retrieved_at=datetime.now(timezone.utc).isoformat(),
                    files=hashes)
    (destination / "manifest.json").write_text(source.model_dump_json(indent=2), encoding="utf-8")
    return source


def load_snapshot(directory: Path) -> Bundle:
    source = Source.model_validate_json((directory / "manifest.json").read_text(encoding="utf-8"))
    if source.id != "musai" or source.repository != REPOSITORY or source.license != "CC0-1.0":
        raise ValueError("Unsupported MUSAI source identity or license")
    if set(source.files) != set(FILES):
        raise ValueError("Snapshot must contain the complete expected file set")
    for name in FILES:
        if hashlib.sha256((directory / name).read_bytes()).hexdigest() != source.files[name]:
            raise ValueError(f"Snapshot checksum mismatch: {name}")
    dataset = MusaiDataset.model_validate_json((directory / "styles.json").read_text(encoding="utf-8"))
    if dataset.license != source.license or dataset.repository != REPOSITORY:
        raise ValueError("Dataset identity or license differs from manifest")
    if dataset.count != len(dataset.styles):
        raise ValueError("Declared record count differs from actual count")
    recipes = []
    seen = set()
    for row in dataset.styles:
        if row.url in seen:
            raise ValueError(f"Duplicate source URL: {row.url}")
        seen.add(row.url)
        recipes.append(Recipe(
            id="musai:" + hashlib.sha256(row.url.encode()).hexdigest(),
            title=row.style, family=row.family, style_prompt=row.style_prompt,
            structure=row.structure, source_record_url=row.url,
            settings=SettingsRecommendation(bpm=row.bpm, weirdness=row.weirdness,
                                            style_influence=row.style_influence),
            raw_record=row.model_dump(),
        ))
    return Bundle(source=source, recipes=recipes)
