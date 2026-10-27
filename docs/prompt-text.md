# Style and lyrics versions — 0.11

Save or open a workbench draft, expand **Style & lyrics · version history**, then
choose **Load text history for saved draft**. Enter a style prompt, lyrics/section
instructions and an optional version note. **Save new text version** appends a
new immutable version. It does not overwrite existing text history.

## Exact content and source context

Each version contains the submitted text without trimming, rewriting or translating
it, separate SHA-256 fingerprints for style and lyrics, creation time, note and a
complete snapshot of the saved draft. That snapshot includes its direction, settings,
chosen concept IDs and reference selection, with exact source/license metadata.

Whitespace and line breaks are meaningful and are preserved as submitted by the
client. A browser textarea may normalize pasted platform-specific newlines before
submission; the server does not claim byte identity with an uninspected original
file. Text TXT exports use UTF-8 and can be checked against the saved fingerprints.
The UI's 20,000/100,000 character limits are application storage limits, not claims
about current Suno input limits. Language metadata is English; there is no automatic
language detection or translation.

## History and older versions

History shows saved versions newest first, with further pages when needed. Clicking
an older version loads it as an editing base. Saving appends a new version with:

- `previous_id`: the chronological head immediately before this append.
- `based_on_id`: the older text version used as the editing base, if supplied.

For example, returning to version 1 after version 2 creates version 3, preserving
both earlier versions. Identical text has identical fingerprints even when a new
version has different notes or saved source context. Versions are never described
as independent listening tests or successful generations merely because they exist.

The editor stays attached to its explicitly loaded draft when the main workbench
switches drafts. To switch text targets, load the current saved draft explicitly;
unsaved text prompts before being discarded. Loading an old version also restores
its original saved context. If the musical draft has since changed, refresh its
saved context deliberately before saving new text. Refresh retains the text edits.

Changing a workbench draft and saving a text version are separate operations.
Copying a workbench draft currently copies direction/reference choices; it does not
automatically clone or reassign text history. Listening reports are not yet linked
to these version IDs; exact generation-run linkage remains a later module.

## Save conflicts and exports

Writes check both the expected text head and the exact current saved draft under
one SQLite write transaction. A stale draft or another writer's text append returns
409 without creating a partial version. The editor keeps unsaved edits after errors;
review/reload newer history deliberately before retrying. There is no automatic merge.

Use **Export saved style**, **Export saved lyrics** or **Export text version JSON**.
Exports refer to the loaded immutable version and are disabled during unsaved text
changes. JSON includes text, hashes, history links and its source/draft snapshot.
The separate draft-reference-pack export continues to export reference context;
it does not silently choose a text version for the consumer.

## Core contracts and transport

`prompt_text.py` owns PromptText, PromptVersion, paged summaries and the repository.
It uses SQLite and the generic Draft contract, without HTTP, a model-provider SDK
or generation calls. Migration 5 adds prompt_versions/prompt_heads; prior source,
workspace and listening tables retain their contents.

| Endpoint | Behavior |
|---|---|
| `GET /api/drafts/{id}/prompt-versions?limit=20&offset=0` | Paged summaries and current head ID |
| `GET /api/drafts/{id}/prompt-versions/{version_id}` | One complete immutable version |
| `POST /api/drafts/{id}/prompt-versions` | Append with content, draft_revision, expected_head_id, optional based_on_id/note |

The client supplies text, not computed hashes or version numbers. The server
computes these. Cross-draft version references are rejected. There are no update
or delete endpoints for saved text versions. The core validates hashes against
content when reading a version. The UI uses a dedicated hook and controlled view.

Portable schema commands:

```powershell
.\.venv\Scripts\python.exe -m prompt_reference.cli schema schemas/prompt-text.schema.json --contract prompt-text
.\.venv\Scripts\python.exe -m prompt_reference.cli schema schemas/prompt-version.schema.json --contract prompt-version
.\.venv\Scripts\python.exe -m prompt_reference.cli schema schemas/prompt-history.schema.json --contract prompt-history
```

These contracts provide a stable editing target for the next MCP adapter. See the
[integration plan](roadmap.md): MCP/skills/plugins take priority over optional
direct model-provider API integration.
