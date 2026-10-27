from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


class Model(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)


class Source(Model):
    id: str = Field(min_length=1)
    repository: str
    revision: str = Field(pattern=r"^[0-9a-f]{40}$")
    license: str
    retrieved_at: str
    files: dict[str, str]  # relative filename -> SHA-256
    attribution: str | None = None
    license_url: str | None = None
    license_text: str | None = None
    changes: str | None = None
    curation_sha256: str | None = Field(default=None, pattern=r"^[0-9a-f]{64}$")
    orientation: Literal["unspecified", "mixed", "v6_native"] = "unspecified"
    orientation_basis: str | None = None

    @property
    def snapshot_id(self) -> str:
        base = f"{self.id}@{self.revision}"
        return base if self.curation_sha256 is None else f"{base}+{self.curation_sha256}"


class Citation(Model):
    path: str
    line_start: int = Field(ge=1)
    line_end: int = Field(ge=1)
    url: str
    excerpt: str = Field(min_length=1)


class Evidence(Model):
    status: Literal["source_claim", "working_hypothesis", "unverified_example"]
    source_label: str
    independently_verified: Literal[False] = False
    model_scope: list[str] = Field(default_factory=list)
    test_count: int | None = Field(default=None, ge=1)
    context: str
    model_basis: Literal["unspecified", "v6_targeted", "pre_v6"] = "unspecified"

    @model_validator(mode="after")
    def check_model_basis(self):
        has_v6 = bool(set(self.model_scope) & {"v6", "v6-wild", "v6-mini"})
        if self.model_basis == "v6_targeted" and not has_v6:
            raise ValueError("V6 targeting requires an explicit V6-family model scope")
        if self.model_basis == "pre_v6" and has_v6:
            raise ValueError("Legacy evidence cannot carry V6 model scope")
        return self


class ReferenceEntry(Model):
    id: str
    kind: Literal["term", "phrase", "guidance"]
    text: str = Field(min_length=1)
    meaning: str = Field(min_length=1)
    category: Literal["instrumentation", "rhythm", "vocals", "structure", "production", "arrangement", "controls", "harmony", "genre"]
    language: Literal["en"] = "en"
    input_field: Literal["style", "lyrics", "settings"] | None = None
    evidence: Evidence
    citations: list[Citation] = Field(min_length=1)


class SettingsRecommendation(Model):
    bpm: int | None = Field(default=None, gt=0)
    weirdness: int | None = Field(default=None, ge=0, le=100)
    style_influence: int | None = Field(default=None, ge=0, le=100)
    evidence: Literal["publisher_recommendation"] = "publisher_recommendation"
    model_version: str | None = None


class Recipe(Model):
    id: str
    title: str = Field(min_length=1)
    prompt_language: Literal["en"] = "en"
    family: str
    style_prompt: str = Field(min_length=1)
    structure: str
    settings: SettingsRecommendation
    source_record_url: str
    raw_record: dict[str, Any]
    exclude_styles: str | None = None
    evidence: Evidence | None = None
    citations: list[Citation] = Field(default_factory=list)
    workflow: str | None = None


class Bundle(Model):
    schema_version: Literal["1.0", "1.1", "1.2"] = "1.2"
    source: Source
    recipes: list[Recipe] = Field(default_factory=list)
    entries: list[ReferenceEntry] = Field(default_factory=list)
