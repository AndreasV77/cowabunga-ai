# Reviewed search expansion and exclusion-field contract — 2026-10-27

**FND-02 is closed for the current 36-probe scope. Gate 1 remains OPEN:** source
composition/coverage (FND-01) and complete editorial review (FND-04) are unfinished.
New tasks, source selections or search changes require reviewing and rerunning
the retrieval scope; this is not a claim of exhaustive semantic search.

## Two resolved losses

The core now applies only these reviewed, directional query expansions:

| Input term | Search alternatives | Purpose |
|---|---|---|
| `gallop` | gallop OR galloping | Recall a missing word form without a general stemmer |
| `exclude` | exclude OR exclusion OR exclusions OR avoidance OR negative | Discover related exclusion/avoidance guidance, without asserting that fields or techniques are equivalent |

Input terms remain joined with AND; alternatives within a group use OR. Every
term is quoted as literal FTS input. User-supplied OR, quotation marks or SQL-like
text do not become query operators. Expansion is case-insensitive and limited to
whole input tokens; `gal` and `excluded` are not expanded. Other traditions,
ensemble types and arbitrary synonyms are not merged. Ranking still prioritizes
matching active V6-core records, then lexical relevance. Source/model/history/
kind filters and complete source-bound results retain their meaning.

Search does not modify source records or infer musical effects. `gallop` now
finds the Power Metal recipe found by `galloping`. `exclude` now also finds
`lil-synn:avoidance-experimental`, not only the newer Cookbook field guidance.
The two old misses remain explicit **literal baseline controls** in the task set;
they are no longer unresolved losses of the default search.

## Explainability and literal comparison

```powershell
.\.venv\Scripts\python.exe -m prompt_reference.cli search gallop --explain
.\.venv\Scripts\python.exe -m prompt_reference.cli search gallop --literal --explain
```

`Store.search(..., expand=False)` disables the reviewed expansion. The library
API accepts `expand=false`, and LibraryPage 1.1 includes `search_plan` with the
original query, exact term groups, policy identifier and an equivalence warning.
The workbench displays applied expansions beside the results. Legacy 1.0 library
pages without that metadata still deserialize; no hidden provider context is used.

## Separate Exclude Styles association

Bundle **1.3** adds `exclude_styles` to `ReferenceEntry.input_field`. Existing
style/lyrics/settings/null fields and Bundle 1.0–1.2 input remain readable.
Updated clients can distinguish exclusion guidance from style wording. Older
software is not promised support for the new enum value; update clients that
consume 1.3 data. The five affected JSON Schemas were regenerated from Pydantic
models; TypeScript field/response types were updated. No SQLite migration or
source-file revision is necessary.

Only `cookbook:exclude-field-guidance` changes its field association from null
to `exclude_styles`, with a clarified evidence context. Its source passage and
wording remain unchanged, and it is still a **guidance** record. The field
association is not a suggestion to paste the heading itself into Exclude Styles.
Actual recipe exclusions remain separate in `Recipe.exclude_styles`; authored
style/lyrics text, user settings and historical draft content are not rewritten.

The changed curation produces a new immutable Cookbook snapshot. Exact prior
Cookbook curation, catalog, crosschecks and task suite are archived in
`curations/archive/0.11-before-exclusion-field/`; current pins and the catalog's
review hash were updated together. Old null-field records remain historical;
they are not relabeled in place. All musical evidence stays independently
unverified.

## Verification and closure limits

- Strict foundation validation: **153 passed, zero skipped**; all four pinned
  sources rebuild/export, current catalog/crosschecks resolve and all 36 retrieval
  probes have an explicit disposition. Report: ignored
  `data/audits/search-exclusion-20261027.json`.
- Regression checks include both fixes, AND constraints, disabled expansion,
  prefix non-expansion, literal operator-like input, model/kind isolation,
  unchanged search storage, API/CLI trace agreement and legacy data decoding.
  Existing tests retain inactive-history, tradition and core/supplement boundaries.
- TypeScript/Vite production build passed. The source inspector/result field
  label now identifies Exclude Styles guidance; applied search groups are exposed
  in the same reference view. No composition assistant or broader UI redesign
  was introduced. Existing Starlette/httpx deprecation warning remains.
- Before local activation, a consistent SQLite backup was checked at ignored
  `data/backups/reference-before-exclusion-field-20261027.sqlite3`. All user-table
  row digests and eleven previous source-snapshot exports were unchanged after
  import/activation. Integrity, foreign keys and task audit passed. The private
  preservation report is ignored `data/audits/search-exclusion-live-20261027.json`.

Closing these retrieval defects does not establish reliable exclusion behavior,
tempo control, independent instrument-role execution or adequate coverage of all
musical briefs. Those remain distinct foundation/editorial or listening questions.
