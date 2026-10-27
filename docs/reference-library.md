# Direct reference library — 0.10

The workbench now searches the active imported corpus directly, including MUSAI
recipes outside the reviewed concept catalog. Search **Mongolian**, **kawaii** or
**metal** in the Reference library above the listening notebook and direction editor.

## Search and inspect

- **All active references · V6 first** includes supplementary/model-unspecified
  material while sorting V6-targeted core records ahead of other matches.
- **V6-targeted core only** restricts both source orientation and record model basis.
  That classification does not assert verified musical effects.
- Record types filter recipes, terms, phrases or guidance.
- Searches start with 20 displayed matches; Show more raises that to at most 100.
  If more remain, refine the words or type. Counts describe displayed matches,
  not an inferred total or number of distinct genres.

Search uses AND semantics with explicitly reviewed gallop/exclude query expansions over titles, families, prompts,
structures and entry text/meaning/categories as indexed by the existing store.
It does not interpret an expression as FTS operators, infer synonyms or promise
stemming. For example, `gallop` does not currently find `galloping`. A `metal` match
may refer to a metal instrument rather than the Metal genre. Inactive historical
sources are excluded; broader historical inspection remains a CLI concern.

The displayed results retain their submitted query/scope. Editing inputs shows a
notice until the new search is submitted. No-result searches suggest broadening
the scope or trying other words. A selected library inspection is cleared if that
record is absent from the new result page.

**Inspect reference** uses the shared source pane/drawer. It shows source grade,
model status, full recipe style prompt and arrangement, original passages when
present, pinned repository revision, source license and notices. Recipe sliders
are explicitly publisher suggestions, with their model version shown separately.
They do not change personal defaults or workbench settings.

## Portable single-record export

**Export reference JSON** returns the Bundle 1.3 contract containing
exactly that record and its complete original source metadata. Exclusions, raw
records, settings, evidence, citations and notices remain separate original fields.
The active source snapshot and record ID are checked again at export time. An
inactive snapshot returns an explicit conflict; no newer wording is substituted.

Use **Keep with draft** to retain records independently of the current search.
[Saved library choices](pinned-references.md) travel beside the reviewed concept
context, with a combined saved-pack export. They are not automatically mixed into
a finished prompt. Search inputs and the inspected hit remain page-local and are
not saved as personal preferences.

## Reusable boundaries and API

`library.py` owns LibraryHit/LibraryPage and exact-record Bundle export. It reuses
Store.search, active snapshots and immutable source bundles. It does not depend on
FastAPI, a provider SDK or the concept catalog. LibraryHit validates source identity,
record kind and the V6 classification against its actual source evidence.

`library_api.py` exposes:

| Endpoint | Behavior |
|---|---|
| `GET /api/library?q=...&scope=all&kind=recipe&limit=20` | Typed active-record search; scope all/v6_core; kind optional |
| `GET /api/library?q=gallop&expand=false` | Literal comparison with reviewed query expansions disabled |
| `POST /api/library/export` | Body: snapshot_id and record_id; returns one-record Bundle JSON |

Queries are limited to 300 characters and displayed limits to 1–100. Invalid
filters/limits return 422, missing records 404, inactive source exports 409 and
missing databases 503. Direct search remains usable when the concept catalog or
review file is unavailable. Existing concept APIs still report their own errors.

`hooks/useLibrary.ts` owns search/inspection/export state. The controlled
`ReferenceLibrary.tsx` renders it; App selects whether the shared SourceInspector
shows a library record or a context candidate. Existing concept exports, saved
drafts and listening notes keep their own state and contracts.

Portable search response schema:

```powershell
.\.venv\Scripts\python.exe -m prompt_reference.cli schema schemas/library.schema.json --contract library
```

No new imports, database migration, runtime dependency, AI calls or source edits
are part of this feature. The library uses the schema-4 foundation; authored text history subsequently adds
migration 5.

The [2026-10-27 search correction](search-and-field-review.md) adds two explicit
query expansions and LibraryPage 1.1 query-plan metadata. Current views display
those groups. Bundle 1.3 also distinguishes `exclude_styles` field guidance;
this is not automatically composed style text. Legacy library pages/bundles remain
readable. The SQLite schema remains 5.
