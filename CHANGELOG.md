# Changelog

## Unreleased — public repository preparation

- Named the public project Cowabunga AI, updated branding and permission links to AndreasV77/cowabunga-ai, and retained existing package/application identifiers for compatibility.

- Adopted custom Personal Use and Integration License 1.0 under AndreasV, with GitHub Issues for integration requests and explicit third-party exclusions.
- Added current licensing examples, package license metadata and a temporary hold on external code contributions pending contribution terms.

- Excluded private challenge work, local validation notes, configuration and runtime data from Git.
- Removed public-test dependencies on private challenge logs; added synthetic conversion cases and a provenance-preserving CC0 vocabulary fixture.
- Documented publication scope and reproducible checks; own-code licensing is documented separately from upstream terms.
- Recorded the confirmed licensing goal: free individual use including monetized songs, with prior permission required for platform/project integration and third-party rights preserved.
- Added a non-operative English license draft covering personal clients/MCP, creative monetization, permission-based integration, upstream exclusions and public repository hosting, with scenario-based review examples.
- Compared published n8n, Dify, Elastic, PolyForm and FSL licensing boundaries; clarified indirect/partial platform access in draft 0.2 and recorded the owner's decision to proceed without commissioned legal review.

## 0.11.0 — 2026-10-27

- Added authored style/lyrics editing with immutable text versions, exact UTF-8 hashes and saved draft/source snapshots.
- Added chronological/base-version links, paged history, reuse of older text as new versions and saved TXT/JSON exports.
- Added atomic head/draft revision checks, cross-draft isolation and preservation of edits after conflicts.
- Added migration 5 for append-only text history; prior reference/workspace/listening data remains unchanged.
- Added PromptText/PromptVersion/PromptVersionPage contracts, independent core/API and controlled editor/hook.
- Verified 90 tests, TypeScript/Vite build, browser three-version history/reload/export and backup/data-integrity checks.

### Integration priority

- Made MCP, skills and host-specific plugins the primary AI integration path; direct model-provider APIs are optional and lower priority.
- Documented the shared application-owned core and delivery order in docs/roadmap.md.

## 0.10.0 — 2026-10-27

- Added explicit Keep with draft choices across library searches, save/reopen, remove and combined reference-pack export.
- Added portable LibrarySelection/DraftReferencePack contracts and immutable full source/record retention.
- Kept free choices separate from concept context; only checked core candidates enter the combined export.
- Retained historical library choices, marked inactive sources and checked new selections against active snapshots.
- Preserved omitted library fields for older clients, explicit clearing, copy-from revisions and saved-export revision checks.
- Added controlled kept-reference view; choices participate in unsaved-change protection and deliberate save.
- Reused schema-4 storage with no migration; original drafts/listening evidence and personal defaults unchanged.
- Verified 83 tests, TypeScript/Vite build and browser pick/search/save/reload/remove/export with exact original metadata.

## 0.9.0 — 2026-10-26

- Added direct full-corpus library search over active records, with V6-first ordering, core/type filters and bounded result expansion.
- Added independent typed library core/API, LibraryPage JSON Schema and single-record Bundle export.
- Exposed MUSAI recipes in the workbench with explicit model-unspecified status, publisher settings and original recipe data.
- Extended shared source inspection with recipe prompts/arrangements, pinned repository/license links and original evidence.
- Rechecked exact active snapshots at export; preserved raw records, evidence and licensing without silent substitution.
- Kept search separate from concept/draft selections and personal defaults; no migration or new source imports.
- Verified 77 tests, TypeScript/Vite build, native browser search/filter/expansion/inspection/export and unchanged database contents.

## Unreleased — challenge evaluation closure, 2026-10-26

- Closed this development-step evaluation at the user's judgment that current findings suffice and further variance testing would be disproportionate.
- Recorded ordinary generation variability as the user's partial explanation; retained causal uncertainty and all original reports.

### Style B listening reports

- Added B1 and B2 as distinct reports with user-confirmed unchanged Style B/lyrics and Variety Off.
- Preserved all raw ratings and ambiguous combined metal scores; no new split scores or later-listening judgments.
- Kept current A W50/SI50 baseline provisional: neither B report improves throat recognition, and B outcomes differ on bridge/coexistence/replay.
- Distinguished new report labels during import; prior A reports and original evidence remain unchanged.

## 0.8.0 — 2026-10-26

- Added a modular listening notebook separating musical execution, sound quality and immediate/later replay value.
- Kept unassessed values distinct from zero and problem occurrence separate from positive scores; no aggregate score.
- Added portable ListeningAssessment/ListeningDocument contracts, API routes, controlled view and independent form hook.
- Pinned reports to complete draft snapshots and retained first assessments/imported raw evidence across revisions.
- Added optimistic update checks, deliberate save, unsaved-note protection and saved-report JSON export.
- Imported both challenge reports with their original ratings and clarifications; ambiguous old combined scores remain unsplit.
- Reused schema-4 workspace storage; no migration, provider calls or new runtime dependencies.
- Verified 70 tests, TypeScript/Vite build and browser report loading/saving/export.

## Unreleased — second listening report, 2026-10-26

- Preserved W45/SI85 metal score 1 with the user clarification: thin Suno sound, explicitly not prompt failure; separated sound-body judgment from arrangement/groove execution.

- Added V6 Standard W50/SI50: user confirms Style A and unchanged lyrics, all positive ratings 2 and listed-problem rating 0.
- Recorded raw throat/metal score differences from 1 to 2; the later user clarification assigns the first metal score to thin rendered sound, not prompt failure. Later listening remains open.
- Kept this same-prompt settings comparison distinct from the unreported style-B experiment.

### First listening report

- Recorded the user's V6 Standard W45/SI85 ratings and enjoyment verbatim, preserving unconfirmed prompt/song metadata.
- Kept later listening open, the problem-question zero separately interpreted, and W50/SI50 as a pending exploratory comparison.
- Identified the mixed-direction rating scale and combined replay question as rubric issues; no aggregate score or slider-effect claim.

### First practical challenge

- Added Tiny Bell, Big Thunder: original English lyrics, a one-difference style-prompt pair and a limited-credit listening plan.
- Audited actual V6-core versus supplementary vocabulary and concept-search coverage.
- Exported four selected V6-core records and four unchanged CC0 MUSAI recipes with provenance.
- Saved/restored the challenge through the workspace API and checked its visible browser state.
- Recorded missing corpus search, direct recipe selection and style/lyrics/run storage as observed platform gaps.
- No application code, corpus import, active-source changes, generation or listening results in this pass.

## 0.7.0 — 2026-10-26

- Added a reusable namespaced document repository for explicit preferences and revisioned drafts.
- Added migration 4, preserving existing source tables and active selections.
- Added named local drafts, direction-only sketches, save-as-new and exact candidate restoration.
- Preserved complete source-backed packets; changed references require deliberate rebuilding.
- Added explicit model/source defaults for new drafts, conflict detection and unsaved-change protection.
- Added independent workspace API routing, a workspace hook and controlled draft/default controls.
- Added generic Draft/Preferences JSON Schema contracts; no provider calls or inferred memory.
- Verified automated persistence/API/migration checks, frontend build and browser save/reopen/defaults.

### Frontend modularity

- Split the workbench view into ConceptLibrary, DirectionEditor, CandidatePalette,
  ReviewNotes, SourceInspector and ExportBar components with typed data/callback props.
- Moved page state and action sequencing into useWorkbench; App now composes the layout.
- Centralized HTTP access, view-facing types and record presentation helpers.
- Verified TypeScript/production build and browser assembly, deselection,
  source inspection, changed-direction export blocking and JSON export.

## 0.6.0 — 2026-10-26

- Added a local English React/TypeScript/Vite workbench over the existing context service.
- Added optional FastAPI/Uvicorn endpoints for corpus metadata, concepts, context and selected-record exports.
- Added candidate selection, source inspection, citations, evidence limits, counterchecks and JSON/Markdown downloads.
- Added context copying and export blocking after changes to the direction or source/model selection.
- Left alternatives, dimensions and whole recipes unchecked by default.
- Added a compact-viewport source drawer, keyboard close support and responsive layout.
- Added a Windows launcher and optional web dependency group; CLI/data-core use remains independent.
- Added `user_deselected` to explicit packet omission reasons and retained notices in selected exports.
- Verified 55 automated tests, a production frontend build and native browser interaction.

## 0.5.0 — 2026-10-26

- Added 12 reviewed musical concepts linking source records without automatic synonym merging.
- Added English concept/alias lookup and deterministic context assembly as an independent module.
- Added portable ContextPacket and ConceptCatalog JSON Schema contracts.
- Context candidates default to the V6 core; mixed-source supplements require an explicit option.
- Preserved model scope, exact source snapshots, licenses, notices and relevant counterchecks in packets.
- Added explicit omission reasons for model mismatch, supplementary candidates and record limits.
- Rejected inactive catalog selections and changed review files instead of silently substituting sources.
- Added JSON/Markdown context export with overwrite refusal and provenance validation.
- No new source imports, database migrations, AI calls or provider dependencies were needed.

## 0.4.0 — 2026-10-26

- Added a selective LIL SYNN adapter/curation: 22 V6-oriented phrases and method notes.
- Expanded Cookbook with six phrases and two English text-based examples.
- Established a two-source V6 core: 64 entries and three unverified recipes.
- Added reviewed source orientation and separate record-level model basis in contract 1.2.
- Prioritized matching V6-core records in search; added strict core/model-basis filters.
- Added four source-pinned editorial counterchecks with explicit evidence limits.
- Preserved 0.3 curations and left historical records/model uncertainty intact.
- Excluded the unsupported Audio Quality Rescue recipe from the core.
- Updated the generated glossary, notices, source map and reproducibility instructions.

## 0.3.0 — 2026-10-26

- Expanded the reviewed vocabulary from 30 to 122 entries, preserving all seed records unchanged.
- Added instrument timbres and roles, vocal techniques, rhythmic feels, articulation,
  production texture, harmonic movement and dynamic transitions.
- Added a generated, source-linked English review glossary.
- Archived the exact 0.2 curation files for reproducible historical imports.
- Added SQLite migration 3 and explicit active selections per source, so expanded
  curations do not duplicate old versions in default search.
- Added activation, history search, category filtering and corpus statistics to CLI.
- Kept schema 1.1 unchanged; source evidence limits remain attached to every entry.


## 0.2.0 — 2026-10-26

- Reviewed the contract against pinned Band Manager and Suno v6 Cookbook sources.
- Added 30 curated terms, phrases and scoped guidance records plus one unverified
  Cookbook example; musical explanations are marked editorial adaptations.
- Added exact source-line citations, evidence context, model scope and retained
  source grading without upgrading it to independent verification.
- Added license text, attribution, license links and change notices to source
  metadata and exports; retained source-specific exclusions without endorsing them.
- Added reviewed curation imports, curation-content hashes and SQLite migration 2.
- Extended search across recipes and entries with optional record-kind filtering.
- Expanded the portable contract to 1.1; old 1.0 bundles remain readable.
- Verified migration from the previous SQLite schema without losing MUSAI records.


## 0.1.0 — 2026-10-26

- Added the provider-independent Python reference core and CLI.
- Added strict Pydantic exchange models and generated JSON Schema.
- Added versioned SQLite storage, transactional imports and FTS5 search.
- Added pinned MUSAI snapshots with source records, license and file checksums.
- Imported all 564 recipes from revision e34ad57e3450efccf792d1e4e1685ca089ce3c25.
- Kept unknown model version and publisher-recommendation status explicit.
- Preserved source titles, structures, setting values and original records.
- Documented the source's nine-versus-three null-BPM discrepancy.
- Added offline tests plus optional validation against the full pinned dataset.
