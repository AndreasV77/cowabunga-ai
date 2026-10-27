"""Portable listening observations, separate from prompt claims and preferences."""
from typing import Annotated, Literal

from pydantic import Field, JsonValue, model_validator

from .models import Model
from .workspace import Draft, WorkspaceRepository

Score = Annotated[int, Field(ge=0, le=2)]


class RatedObservation(Model):
    id: str = Field(pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
    label: str = Field(min_length=1, max_length=200)
    score: Score | None = None
    note: str = Field(default="", max_length=4000)


class ListeningValue(Model):
    immediate_replay: Score | None = None
    later_replay: Score | None = None
    later_listening_context: str = Field(default="", max_length=2000)


class ReportedProblems(Model):
    sung_instructions: Literal["unknown", "none", "present"] = "unknown"
    omitted_lyrics: Literal["unknown", "none", "present"] = "unknown"
    merged_voices: Literal["unknown", "none", "present"] = "unknown"
    note: str = Field(default="", max_length=4000)


class GenerationContext(Model):
    provider: str = Field(default="", max_length=100)
    model: str = Field(default="", max_length=100)
    settings: dict[str, JsonValue] = Field(default_factory=dict)
    song_reference: str = Field(default="", max_length=2000)
    input_note: str = Field(default="", max_length=4000)
    style_sha256: str | None = Field(default=None, pattern=r"^[0-9a-f]{64}$")
    lyrics_sha256: str | None = Field(default=None, pattern=r"^[0-9a-f]{64}$")


class ListeningAssessment(Model):
    schema_version: Literal["1.0"] = "1.0"
    evidence_source: Literal["user_report"] = "user_report"
    independently_verified: Literal[False] = False
    generation: GenerationContext = Field(default_factory=GenerationContext)
    musical_execution: list[RatedObservation] = Field(default_factory=list, max_length=30)
    sound_quality: list[RatedObservation] = Field(default_factory=list, max_length=30)
    listening_value: ListeningValue = Field(default_factory=ListeningValue)
    problems: ReportedProblems = Field(default_factory=ReportedProblems)
    interpretation: str = Field(default="", max_length=8000)
    raw_report: dict[str, JsonValue] | None = None

    @model_validator(mode="after")
    def unique_dimensions(self):
        for group in [self.musical_execution, self.sound_quality]:
            ids = [item.id for item in group]
            if len(ids) != len(set(ids)):
                raise ValueError("Observation IDs must be unique within a group")
        return self


class ListeningDocument(Model):
    id: str
    title: str
    revision: int
    updated_at: str
    assessment: ListeningAssessment
    original_assessment: ListeningAssessment
    draft_snapshot: Draft


class ListeningRepository:
    """Reuse namespaced workspace storage; pin the actual draft, not just its ID."""
    def __init__(self, workspace: WorkspaceRepository, draft_id: str):
        self.workspace = workspace
        self.draft_id = draft_id
        self.namespace = f"prompt-reference:listening:{draft_id}"

    @staticmethod
    def document(saved: Draft) -> ListeningDocument:
        return ListeningDocument(id=saved.id, title=saved.title, revision=saved.revision,
            updated_at=saved.updated_at, assessment=ListeningAssessment.model_validate(saved.form),
            original_assessment=ListeningAssessment.model_validate(saved.selection["original_assessment"]),
            draft_snapshot=Draft.model_validate(saved.selection["draft_snapshot"]))

    def list(self) -> list[ListeningDocument]:
        return [self.document(saved) for saved in self.workspace.list_drafts(self.namespace)]

    def get(self, id: str) -> ListeningDocument:
        return self.document(self.workspace.get_draft(self.namespace, id))

    def create(self, title: str, assessment: ListeningAssessment, draft: Draft) -> ListeningDocument:
        if draft.id != self.draft_id:
            raise ValueError("Listening namespace and draft must match")
        payload = assessment.model_dump(mode="json")
        saved = self.workspace.create_draft(self.namespace, title, payload,
            {"draft_snapshot": draft.model_dump(mode="json"), "original_assessment": payload})
        return self.document(saved)

    def update(self, id: str, title: str, assessment: ListeningAssessment, revision: int) -> ListeningDocument:
        old = self.workspace.get_draft(self.namespace, id)
        if assessment.raw_report != old.form.get("raw_report"):
            raise ValueError("Original report evidence cannot be replaced")
        saved = self.workspace.update_draft(self.namespace, id, title,
            assessment.model_dump(mode="json"), old.selection, revision)
        return self.document(saved)
