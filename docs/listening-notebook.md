# Listening notebook — 0.8

Open **Listening notebook · execution, sound and replay value** in the workbench.
Choose a saved draft and load its notes. This notebook has its own draft choice;
editing the musical direction elsewhere does not silently reattach a report.

Each report keeps three distinct groups:

- **Musical execution:** requested voices, instruments, rhythms, motifs and transitions.
- **Sound quality:** body, fullness, clarity and separation of the generated render.
- **Personal listening value:** immediate replay desire and replay desire on a later listen.

Positive observations use 0 (absent/weak), 1 (partial/uncertain), 2 (clear/fulfilled).
Replay uses no/maybe/yes. **Not assessed** is null, never an automatic zero. Problems
use separate unknown/none-heard/present fields; there is no combined score.
Observations, context and interpretation have separate places. A listener's
attribution to a provider remains their interpretation, not a verified cause.

## Save, revisit and export

Name the report and save deliberately. Open saved reports from the report buttons;
add later listening context or a later replay judgment when that listening occurs.
Unsaved changes block export and prompt before another report or draft is loaded,
or a new report is started. A page-leave warning is registered. There is no autosave.

Every saved report retains:

- The latest assessment and a revision used to prevent silent concurrent overwrites.
- An immutable copy of its first assessment, including any imported raw report.
- A complete copy of the attached draft at creation, including source context.
- Generation metadata and optional input hashes/song reference supplied by the listener.

Later changes to the musical draft do not replace that saved snapshot. A new
report requires the current draft revision; an existing report remains attached
to its original revision. **Export listening JSON** exports the saved document
with original evidence and draft context. It is disabled while notes are unsaved.

The first assessment is retained, but intermediate edited revisions are not a
complete version history in this release. Add a separate report when a distinct
listening occasion should remain separately accessible. The latest 100 reports
per draft are listed. Deletion, rankings, audio uploads, playback and inferred
preference learning are outside this module.

## Existing challenge reports

The initial local challenge reports were imported from a private working log.
The converter retains each complete raw report and its clarifications:

- W45/SI85 sound body = 1, based on the user's explicit clarification about thin
  sound. The independent arrangement/groove score stays unassessed.
- W50/SI50's original combined metal question = 2 stays in the raw evidence.
  Neither an independent sound-body nor arrangement score is invented from it.
- Later replay stays unassessed for both reports. Reported absence of problems
  maps to none-heard, not to a failed musical score.

The original case log, styles and lyrics remain local and are excluded from the public repository. The converter is an
explicit adapter for this case format, not an automatic import of arbitrary chats.

```powershell
.\.venv\Scripts\python.exe tools/import_challenge_listening.py <local-case-directory>
```

The importer uses the public local API and skips identical imported report IDs.
It refuses to replace differing existing evidence. Its export is
`listening-records.json` inside the case folder.

## Module and API boundaries

`listening.py` owns typed observations and persistence through the existing generic
workspace repository. It has no HTTP, Suno model enum or provider SDK dependency.
Observation IDs/labels are extensible, generation settings are namespaced JSON
values, and each report is explicitly a user report without independent verification.
The current UI offers a small default rubric and supports imported dimension labels;
custom dimension creation is currently an API concern.

`listening_api.py` adapts this to saved workbench drafts:

| Endpoint | Behavior |
|---|---|
| `GET /api/drafts/{id}/listening` | Latest 100 report documents for that draft |
| `POST /api/drafts/{id}/listening` | Create with title, assessment and expected draft_revision |
| `GET /api/drafts/{id}/listening/{report_id}` | Read saved report and original evidence |
| `PUT /api/drafts/{id}/listening/{report_id}` | Update with expected report revision and original draft_revision |

Unknown fields, invalid scores and numeric problem states are rejected. Imported
raw evidence cannot be changed through updates. Stale revisions return 409; unknown
drafts/reports return 404. Original evidence/snapshot data travels in the response.

`hooks/useListening.ts` owns form state, HTTP actions, unsaved-change protection and
export. `components/ListeningPanel.tsx` is the controlled view. Application composition
keeps this independent of the concept palette, source inspector and draft-form hook.

The module reuses schema-4 workspace tables under a per-draft listening namespace;
no database migration or new runtime dependency is required. Portable contracts:

```powershell
.\.venv\Scripts\python.exe -m prompt_reference.cli schema schemas/listening.schema.json --contract listening
.\.venv\Scripts\python.exe -m prompt_reference.cli schema schemas/listening-document.schema.json --contract listening-document
```
