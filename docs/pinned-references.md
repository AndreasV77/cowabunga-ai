# References kept with a draft — 0.10

Use **Keep with draft** on a library search result. The **References kept with this
draft** section holds those choices across subsequent searches. Each record shows
its source, license, revision and core/supplementary classification. Inspect or
remove a kept record directly from that section. Up to 50 references can be kept.

Give the draft a name and save it deliberately. Reopening it restores the exact
kept records and their original source metadata, alongside the concept context
and candidate checkboxes. New draft clears the choices; changing the direction or
rebuilding concepts leaves these deliberate library choices intact until removed.
There is no autosave or automatic merging of complete recipe prompts.

## Exact source versions

New choices must refer to an active source snapshot and a real record. The browser
submits only snapshot/record IDs; the server retrieves the original record and
metadata. The client cannot substitute a different license or prompt in that save.

An already saved choice keeps its full original record if its source later becomes
inactive or unavailable in the active corpus. Reopening the draft checks source
activity and marks such choices as historical. It never replaces them with a newer
version silently. To choose a current version deliberately, remove the historical
choice and add the desired search result. Save as new retains historical choices
through an explicit source-draft ID/revision checked by the server.

The activity indicator is refreshed when the draft is opened; it is not a live
source monitor. Export checks activity again. Separate versions of the same
record may be kept intentionally; exact snapshot/ID duplicates are rejected.

## Export the saved reference pack

**Export draft references** is enabled for saved, unchanged drafts with references.
It downloads a `DraftReferencePack` containing:

- Draft identity, revision and direction/model form.
- Only the checked concept-context items, with evidence, counterchecks and notices.
- All deliberately kept library records with their full original sources.
- Explicit lists of inactive library identities and used context snapshots.

Core and library choices remain separate, even if the same record was deliberately
selected through both paths. The result is source material for prompt engineering;
it is not a concatenated finished prompt. Publisher slider suggestions remain
source data and never change personal defaults or actual generation settings.

This export uses the saved content. It can preserve historical context even when
the normal current-context restoration asks for reassembly. It does not revalidate
old concept mappings against the latest catalog; the original catalog hash/version
travels inside the context. Source activity is reported separately. Exporting with
a stale expected draft revision is rejected instead of returning another revision.

## Reusable contracts and compatibility

`reference_selection.py` owns `LibrarySelection` and `DraftReferencePack`, captures
new records from the existing library core and restores saved choices without
alteration. Both use existing record/source models and are independent of HTTP and
the React view. Context record selection now lives in the concepts core and is
shared by the web context exporter and saved-pack exporter.

The workbench stores `selection.library` alongside the existing optional
`selection.packet` / `selection.selected_ids`. It reuses schema-4 JSON document
storage; no migration or new dependency is required. Direction-only, concept-only,
library-only and combined drafts remain valid. Existing listening snapshots and
legacy drafts remain readable without rewriting their payloads.

API additions:

| Operation | Contract |
|---|---|
| Create/update draft | Optional `library_records`: list of `{snapshot_id, record_id}` |
| Older client omits `library_records` | Existing kept records are preserved on update |
| Explicit `library_records: []` | Removes kept library choices on save |
| Create a copy | Optional `copy_from: {draft_id, revision}` permits retaining source-draft historical choices |
| `GET /api/library/active-snapshots` | Current source ID to active snapshot ID map |
| `GET /api/drafts/{id}/reference-pack?revision=N` | Exact saved pack; mismatched expected revision returns 409 |

Unknown records return 404, new inactive selections 409, duplicate pairs 400,
oversized/malformed requests 422 and stale draft updates 409. Kept choices alone
do not require a working concept catalog. Client-submitted record bodies or source
metadata are not accepted in identity requests.

`useWorkspace` owns durable choices and their dirty/save/open/export lifecycle.
`ReferenceLibrary` exposes the keep/remove action, `DraftReferences` displays kept
records, and `WorkspaceBar` exposes the saved export. Search state still belongs
to `useLibrary`; source inspection remains shared through App.

Generate portable JSON Schemas with:

```powershell
.\.venv\Scripts\python.exe -m prompt_reference.cli schema schemas/library-selection.schema.json --contract library-selection
.\.venv\Scripts\python.exe -m prompt_reference.cli schema schemas/draft-references.schema.json --contract draft-references
```

Style/lyrics has a separate [immutable text history](prompt-text.md) since 0.11.
Automatic prompt composition, arbitrary reference-pack imports and full draft
revision history remain separate future features.
