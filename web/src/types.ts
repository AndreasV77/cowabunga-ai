export type Concept = { id: string; label: string; description: string; aliases: string[]; links: unknown[] };
export type Evidence = { source_label: string; status: string; context: string; model_scope: string[]; model_basis: string; independently_verified: boolean };
export type Citation = { path: string; line_start: number; url: string; excerpt: string };
export type Entry = { id: string; text: string; meaning: string; input_field: 'style' | 'lyrics' | 'settings' | 'exclude_styles' | null; kind: string; evidence: Evidence; citations: Citation[] };
export type Recipe = { id: string; title: string; style_prompt: string; structure: string; exclude_styles: string | null; evidence: Evidence | null; citations: Citation[]; workflow: string | null; source_record_url: string; settings: { bpm: number | null; weirdness: number | null; style_influence: number | null; model_version: string | null } };
export type Item = { snapshot_id: string; v6_core: boolean; uses: { concept_id: string; relation: string; note: string }[]; record: Entry | Recipe };
export type Source = { id: string; repository: string; revision: string; license: string; license_url: string | null; license_text: string | null; attribution: string | null; changes: string | null; orientation: string; files: Record<string, string> };
export type Packet = { catalog_sha256: string; items: Item[]; sources: Record<string, Source>; omitted: { record_id: string; reason: string }[]; crosschecks: { id: string; topic: string; assessment: string; conclusion: string; evidence_limit: string }[] };
export type BuildRequest = { concept_ids: string[]; intent: string; target_model: string; supplementary: boolean; limit: number };
export type Meta = { version: string; concepts: number; core: { entries: number; recipes: number } };

export type Defaults = { revision: number; target_model: string; supplementary: boolean; prompt_language: 'en' };
export type DraftSummary = { id: string; title: string; revision: number; updated_at: string };
export type Draft = DraftSummary & { form: BuildRequest; selection: { selected_ids?: string[]; packet?: Packet; library?: LibrarySelection } | null };

export type Score = 0 | 1 | 2 | null;
export type RatedObservation = { id: string; label: string; score: Score; note: string };
export type ListeningAssessment = {
  schema_version: '1.0'; evidence_source: 'user_report'; independently_verified: false;
  generation: { provider: string; model: string; settings: Record<string, unknown>; song_reference: string; input_note: string; style_sha256: string | null; lyrics_sha256: string | null };
  musical_execution: RatedObservation[]; sound_quality: RatedObservation[];
  listening_value: { immediate_replay: Score; later_replay: Score; later_listening_context: string };
  problems: { sung_instructions: 'unknown' | 'none' | 'present'; omitted_lyrics: 'unknown' | 'none' | 'present'; merged_voices: 'unknown' | 'none' | 'present'; note: string };
  interpretation: string; raw_report: Record<string, unknown> | null;
};
export type ListeningDocument = { id: string; title: string; revision: number; updated_at: string; assessment: ListeningAssessment; original_assessment: ListeningAssessment; draft_snapshot: Draft };

export type LibraryHit = { snapshot_id: string; kind: 'recipe' | 'term' | 'phrase' | 'guidance'; v6_core: boolean; source: Source; record: Entry | Recipe };
export type SearchPlan = { policy: 'reviewed-query-aliases-1'; query: string; term_groups: string[][]; expanded: boolean; note: string };
export type LibraryPage = { schema_version: '1.0' | '1.1'; query: string; scope: 'all' | 'v6_core'; kind: string | null; limit: number; has_more: boolean; items: LibraryHit[]; search_plan?: SearchPlan | null };

export type ReferenceIdentity = { snapshot_id: string; record_id: string };
export type LibrarySelection = { schema_version: '1.0'; items: LibraryHit[] };
export type DraftReferencePack = { schema_version: '1.0'; draft_id: string; title: string; revision: number; form: BuildRequest; context: Packet | null; library: LibrarySelection; inactive_library_records: ReferenceIdentity[]; inactive_context_snapshots: string[]; independently_verified: false };

export type PromptText = { schema_version: '1.0'; language: 'en'; style_prompt: string; lyrics: string };
export type PromptVersion = { schema_version: '1.0'; id: string; draft_id: string; version: number; previous_id: string | null; based_on_id: string | null; created_at: string; note: string; content: PromptText; style_sha256: string; lyrics_sha256: string; draft_snapshot: Draft };
export type PromptVersionSummary = { id: string; version: number; created_at: string; note: string; style_sha256: string; lyrics_sha256: string; draft_revision: number };
export type PromptVersionPage = { schema_version: '1.0'; draft_id: string; head_id: string | null; items: PromptVersionSummary[]; has_more: boolean };
