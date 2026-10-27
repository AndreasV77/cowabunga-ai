# Local workbench — 0.11

The UI is a local selection surface for reviewed musical information. It does not
call an AI provider or generate Suno audio. It reuses CatalogService, ContextPacket
and source evidence from the existing data core.

The view is split into controlled components; page state and HTTP transport have
separate owners. See [frontend module boundaries](frontend-architecture.md).

## Workflow

1. Select musical jobs in the concept rail. Search English labels and aliases.
2. Enter the musical direction and choose a V6-family target. V6 core is the default;
   mixed-model supplements are an explicit choice.
3. Assemble candidates. Direct wording starts checked; alternatives, related
   dimensions and complete examples remain available without automatic inclusion.
4. Inspect a candidate's original source passages, publisher grade, application
   scope, context and license. The compact layout opens a closeable side inspector.
5. Choose the records to keep, then copy or export Markdown/JSON context.

The output is a deliberate context selection, not a claim that all checked
phrases should be concatenated into a finished style prompt. Recipe exclusions
remain a separate field. User-deselected items receive an explicit omission
reason in export. Full notices and counterchecks travel with the packet.

Changes to the direction, target model, concepts or supplementary toggle mark the
last assembly as outdated and disable export. Rebuilding reassembles candidates
and resets checkbox selection. The source-record checkboxes alone do not require
rebuilding. Unknown, empty or stale-source requests return explicit API errors.

## Drafts and personal defaults

Give the current direction a name and choose **Save draft**. This saves the form
and, if assembled and current, the exact candidate packet and checked IDs in the
local SQLite database. Direction-only sketches can also be saved without concepts.
Changing a direction before saving stores the new direction without the outdated
selection. **Save as new** preserves the original draft; **New draft** applies
personal defaults. The saved-draft list shows the latest 100 drafts.

Open a saved draft to recover its model, intent, concepts and deliberate candidate
choices. Restoration checks the current catalog and complete rebuilt source packet
against the saved one. Changed or unavailable references leave the direction
editable and request reassembly; the stored historical packet stays intact until
an explicit subsequent save. Updates require the saved revision, so another
window's changes produce a conflict rather than a silent overwrite.

Under **Personal defaults**, explicitly save the current target model and source
scope. These defaults apply to new drafts and fresh page visits. Existing drafts
retain their own settings. There is no inferred preference learning, automatic
song history or provider-owned memory. All prompts remain English. The repository
supports namespaced user/project/artist documents; this UI currently exposes only
the local user's model/source defaults.

Unsaved changes prompt before opening another draft, starting a new one or leaving
the page. There is no autosave. Browser exit/crash recovery is not guaranteed.
Workspace tables are added by SQLite migration 4; back up the database before an
upgrade. Reference imports, source provenance and active snapshots are unchanged.

## Authored style and lyrics

The [versioned text editor](prompt-text.md) stores exact submitted style/lyrics,
immutable history, text fingerprints and saved draft/source context. Load a saved
draft explicitly, edit, then save a new text version. Older text can be reused as
a new version. This requires migration 5; existing reference/workspace data remains
unchanged. The [integration plan](roadmap.md) prioritizes MCP/skills/plugins next.

## Full reference search

The [direct reference library](reference-library.md) searches all active records,
with V6-first ordering, optional core/type filters, source inspection and exact
single-record JSON export. It also exposes recipes outside the concept catalog.
Use Keep with draft for [persistent library choices](pinned-references.md), stored
beside the concept context. Export draft references combines both deliberate
selections with exact source metadata; it does not compose a final prompt.

## Listening observations

The [listening notebook](listening-notebook.md) attaches explicit reports to saved
drafts, separating musical execution, render quality and personal listening value.
Original evidence and draft snapshots are retained. It makes no inferred provider
preferences and does not evaluate audio automatically.

## Run and develop

Install `uv sync --locked --extra web` and run `npm ci` / `npm run build` in `web/`.
`Start-Workbench.ps1` starts or reuses the loopback-only server and opens its URL;
`-NoBrowser` suppresses browser launch. Logs and the started process ID are under
`data/logs/`. No OS startup or recurring task is registered.

For a foreground server, use `python -m prompt_reference.cli serve --port 8765`.
Stop that invocation with Ctrl+C. `--db` precedes the serve subcommand. Catalog,
review and frontend paths can be supplied explicitly.

For frontend editing, start the API on port 8765 and run `npm run dev` in `web/`.
Vite proxies `/api` to that local server. The production build is served by
FastAPI from `web/dist/`, so normal use requires only one running server.

## API

| Endpoint | Behavior |
|---|---|
| `GET /api/meta` | Version, corpus/core counts and concept count |
| `GET /api/concepts?q=...` | Reviewed concept lookup |
| `POST /api/context` | Assemble a complete candidate packet |
| `GET /api/preferences` | Read explicit local defaults; absent defaults do not create a record |
| `PUT /api/preferences` | Save model/source defaults with an expected revision |
| `GET /api/drafts` | List latest 100 draft summaries |
| `GET /api/drafts/{id}` | Read a complete saved document, including historical context |
| `POST /api/drafts` | Create a named direction and optional source-bound selection |
| `PUT /api/drafts/{id}` | Update only the expected draft revision |
| `POST /api/drafts/{id}/restore-context` | Restore checked IDs only against identical current references |
| `POST /api/export` | Reassemble, validate selected IDs and return a selected JSON/Markdown packet |

Context request fields: `concept_ids`, `intent`, `target_model`, `supplementary`,
`limit`. Export adds `selected_ids` and `format` (`json` or `markdown`). Unknown
fields, invalid model names, more than 4000 intent characters and empty candidate
exports are rejected. Full typed API details are available at `/docs` locally.

The server has no endpoint for activation, source imports, file uploads, arbitrary file writes or provider calls. It opens a database connection
per request and closes it after the core operation. Its factory accepts explicit
paths, so other clients need not share this project's directory layout.

## Current limits

Unsaved page selections are held in memory; saved drafts persist locally. Artist/project
profile resolution, draft deletion, cloud sync and provider adapters remain future
modules. The concept palette covers the 12 reviewed concept links, not every
possible task in the full source corpus. Direct library search covers the active
corpus; historical searches remain available in the CLI. Style/lyrics has its own immutable history; full generation-run capture remains a future feature. Source claims remain unverified musical effects.
