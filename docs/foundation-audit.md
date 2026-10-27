# Foundation audit and acceptance gate

Audit date: 2026-10-27. **Gate 1 is OPEN — foundation readiness has not been
established.** Implemented storage/import features and passing tests are evidence,
not a declaration that resource composition and useful coverage are complete.

Latest update, 2026-10-27: the [reviewed nine-entry expansion](foundation-expansion.md)
has **159 entries, 567 recipes, 12 concepts and 6 crosschecks**; strict V6 core has
**68 entries and 3 recipes**. The subsequent [search/field review](search-and-field-review.md) passed **153 tests, zero skips** and closed FND-02 for the current 36-probe scope.
The initial reconstruction counts and FND-03 closure run below are historical.
FND-01 and FND-04 remain open.

## Owner's priority and meaning of completion

1. Resolve foundation questions and establish tested controls first, even when
   that produces no visible product progress.
2. Only after Gate 1, implement and test the complete assistant-supported workflow.
3. Only after that workflow delivers the promised result, improve user experience.

Completion applies to a stated, reviewed scope, not every possible music term or
every future Suno version. Unverified musical effects may remain unverified if
they are explicitly represented and handled as such. Useful vocabulary does not
need to be promoted to a proven generation technique to be retained.

## Checks actually performed

- Ran the existing suite after the directory rename: **90 passed, 0 skipped**.
  The existing Starlette/httpx deprecation warning remains non-blocking.
- Rebuilt a separate, empty SQLite store from all four pinned source collections,
  with no use of the owner's live database, drafts or listening reports.
- Reimported every bundle: all second imports inserted zero records.
- Exported every bundle and compared complete source metadata and every normalized
  entry/recipe to its imported version: all matched. SQLite integrity was `ok`.
- Loaded the real concept catalog and crosschecks against that rebuilt store.
- Probed literal search behavior, including Tiny Bell vocabulary and word variants.
- Checked default-branch heads of the four upstream repositories through GitHub.

The detailed local run output is retained under ignored `data/audits/`. These are
observations on this date; no continuous monitoring or completed release gate is
implied.

### Admitted collections and reconstructed content

| Source | Imported selection | Role | License recorded |
|---|---:|---|---|
| Band Manager | 83 entries | Mixed-model vocabulary/guidance with per-record scope | MIT |
| Suno v6 Cookbook | 45 entries, 3 recipes | V6-oriented community material | CC BY 4.0 |
| LIL SYNN | 22 entries | V6-oriented community material | CC0-1.0 |
| MUSAI | 564 recipes | Broad vocabulary; model version unspecified | CC0-1.0 |

Total: **150 entries and 567 recipes**, 12 reviewed concepts, 4 crosschecks.
Strict V6 core: **64 entries and 3 recipes**. Across all records, 74 have a
V6-targeted record basis, 642 have unspecified model basis and 1 is pre-V6. The
strict core is narrower because it also requires a V6-native source orientation.
These labels describe provenance/applicability, not independent musical success.

Entry categories: instrumentation 40, vocals 40, production 17, structure 17,
arrangement 16, rhythm 14, controls 4, harmony 2. Counts do not establish adequate
coverage; complete recipes also contain vocabulary outside those entry categories.

### Upstream review

| Source | Pinned revision | Observation on 2026-10-27 |
|---|---|---|
| [Band Manager](https://github.com/zarlor/suno-band-manager/commit/73c52379833af51e9d3ce7731746d3bfff3f5266) | `73c52379833af51e9d3ce7731746d3bfff3f5266` | Matches default-branch head |
| [Cookbook](https://github.com/MJorgin/suno-v6-cookbook/commit/c8e40ff0b10636a7719cbc88bc5f58443ad19907) | `c8e40ff0b10636a7719cbc88bc5f58443ad19907` | Matches default-branch head |
| [LIL SYNN](https://github.com/LILSYNNOFFICIAL/LIL-SYNN-s-Complete-Suno-V6-Guide/commit/6b805bf77a350e7fba00bfd2451273327482827c) | `6b805bf77a350e7fba00bfd2451273327482827c` | Matches default-branch head |
| [MUSAI](https://github.com/samuelgrupolimex-prog/suno-style-recipes/commit/e34ad57e3450efccf792d1e4e1685ca089ce3c25) | `e34ad57e3450efccf792d1e4e1685ca089ce3c25` | Head advanced; reviewed difference below |

MUSAI head [7a76f24](https://github.com/samuelgrupolimex-prog/suno-style-recipes/commit/7a76f24f4c6ea348238dbc92251b9f8ededf7ef1)
has the pinned revision as its sole parent and changes only `styles.parquet`.
The importer uses `styles.json`, not that Parquet file. This observed change does
not change any imported input. The pinned revision was deliberately retained;
no live source selection was changed.

### Search observations

| Literal query | Full admitted corpus hits | Strict V6-core hits |
|---|---:|---:|
| Mongolian | 1 | 0 |
| kawaii | 1 | 0 |
| khöömei / khoomei | 1 each | 0 |
| overtone / overtones | 2 each | 0 |
| gallop | 0 | 0 |
| galloping | 5 | 0 |
| sax / saxophone | 22 / 14 | 0 |

No-hit results are not proof that a musical technique is absent from all sources.
FTS is lexical. In particular, `gallop` currently misses records found by
`galloping`. A filtered core result is not a full-corpus coverage judgment.

Changing only the free-text musical intent while keeping selected concepts fixed
did not change the reference items. This is an absent assistant interpretation
feature, not a failed claim that the present selector performs semantic matching.

## Existing control/test evidence

| Area | Existing evidence | What it does not establish |
|---|---|---|
| Import identity and corruption | `tests/test_core.py`, `tests/test_references.py`: identity/license markers, file hashes, duplicates, source counts, rollback | Truth of musical source claims or exhaustive source selection |
| Quotes and editorial changes | Exact, unique source excerpts; curation hash; rejected changed excerpts/path traversal/missing files | Correctness of every original English explanation |
| Model applicability | `tests/test_v6_core.py`: orientation versus record basis, two V6 publishers, legacy and unknown scope | Independently verified generation effects |
| Conflict and provenance retention | Pinned crosschecks, missing-record rejection, source notices and source-bound exports | Automatic resolution of every musical disagreement |
| Search and active versions | Literal queries, active/history isolation, no resurrection of removed records | Task-based coverage, complete alias recall or contextual relevance |
| Persistence | Migration/rollback, revision conflicts, immutable authored versions and original listening evidence tests | Every possible migration fault, backup restore scenario or data-loss condition |

## Blocking work register

These are concrete acceptance tasks. FND-02/FND-03 are closed for their stated scopes;
FND-01 and FND-04 remain open. Do not start Gate 2 or substitute UI work
for them. Close a row with evidence and an explicit treatment of limitations;
adding more source records or more tests by itself is not closure.

| ID | Open foundation question | Required closure evidence |
|---|---|---|
| FND-01 | What resource scope and musical coverage are sufficient for the first assistant workflow? | Reviewed matrix of roles, timbre/technique, rhythm, arrangement/transitions, structure, harmony and controls; map tasks to actual source records, distinguish selection gaps from upstream gaps, and record decisions on remaining source candidates. |
| FND-02 — CLOSED 2026-10-27 | Which expected queries fail through wording, scope or indexing? | A maintained task-based retrieval set with expected records and negative cases, including `gallop/galloping`, spelling variants, strict-core versus supplements, wrong-tradition distractors and empty results; document/fix each loss without falsely merging traditions or evidence grades. Closed for the current 36 probes by [the search/field review](search-and-field-review.md): both known misses resolved, literal controls retained, 153 tests passed without skips; review scope again for new tasks/inputs. |
| FND-03 — CLOSED 2026-10-27 | Can a fresh checkout demonstrate all required real-source checks rather than silently skip them? | Implemented `python -m prompt_reference.foundation`; checked missing/tampered inputs, isolated full rebuild, complete exports and rejection of incomplete tests. Both existing checkout and clean source-copy runs passed 99 tests, zero skips. See evidence below and [reproduction instructions](foundation-validation.md). |
| FND-04 | Are editorial meaning, applicable input field, model scope and conflicts sufficiently reviewed? | Item-level review of the admitted curated entries and representative recipe cases, findings register, corrections as new source/curation snapshots, and regression examples for discovered errors. Mechanical quote matching alone is insufficient. Exclude Styles metadata is resolved in Bundle 1.3; broader semantic review remains pending. |

No numeric code-coverage percentage substitutes for these targets. For admitted
sources, the gate target is all four complete imports/round trips and all required
real-source checks running. For the retrieval task set, every expected result or
documented limitation needs an explicit disposition, including negative cases.

### FND-03 closure evidence — 2026-10-27

The strict command checks local manifests against tracked revision/license/file
hash pins before using production importers. It reconstructs all four sources
(150 entries, 567 recipes), verifies full source/record round trips, idempotency,
SQLite integrity/foreign keys, 12 concepts and 4 crosschecks, then runs all tests.
Missing inputs, skips (including module collection), deselections and xfails
cannot produce a successful strict result. Nine new validator regression cases
cover successful/failed/incomplete runs and protection of existing files.

Both runs passed **99 tests, zero skips**:

- Existing checkout: `data/audits/foundation-strict-20261027-a.json`.
- Clean source copy without local reference data: downloaded all four exact
  upstream revisions again, checked them against the tracked file hashes and ran
  the same strict command: `data/audits/foundation-clean-20261027-a.json`.

The second run used the existing locked Python environment with the clean copy's
`src/` on its import path; it did not claim a fresh dependency installation or a
second operating-system test. The existing Starlette/httpx deprecation warning
remains. Neither run opened the owner's working database. Reports stay local and
ignored; the implementation, negative tests and reproduction commands are tracked.
Source changes require rerunning this check. Coverage, retrieval and semantic
editorial acceptance remain separate open work; Gate 1 stays OPEN.

## Task-based follow-up — 2026-10-27

Added eleven independently authored English briefs and 31 retrieval probes in
`reviews/foundation-tasks.json`, evaluated by strict validation. The
[task coverage/retrieval report](foundation-tasks.md) maps all eight categories
to actual source records and records an initial semantic review of eight entries.
Two query losses (`gallop`, `exclude`) are explicitly open; empty strict-core
queries are separated from full-corpus absence. Candidate-source decisions,
selection-versus-upstream gap review, fixes and the complete editorial review
remain pending. **FND-01, FND-02 and FND-04 stay OPEN.**

The tasks are synthetic examples. Private notebook source material was read to
identify research questions, not copied into the public corpus or fixtures.

## Source-change control

Before Gate 1 acceptance and whenever a source revision, license, imported file,
curation, source applicability assumption or retrieval behavior changes:

1. Compare upstream revisions and affected files, including license/attribution.
2. Keep the old snapshot; review the candidate selection without auto-activation.
3. Rebuild an isolated store, check counts, quote/field/model meaning, export
   notices, retrieval tasks and crosschecks. Test changed assumptions negatively.
4. Run the strict real-source checks and relevant persistence/contract regressions.
5. Record findings and the activation decision. Back up any populated store before
   an authorized migration or update; do not use live user data as test fixtures.

## Gate 1 exit and subsequent gates

Gate 1 remains OPEN until FND-01 through FND-04 have documented closure, with no
unexplained required skips/failures or concealed material resource limitations.
Unresolved claims may remain explicitly uncertain; they must not become guarantees.

Gate 2 must then demonstrate an actual assistant taking a musical brief to a
directionally appropriate prompt with useful reasoning and source/creative-choice
separation. A connected MCP endpoint or manually pasted example is not sufficient.
Gate 3 concerns novice-friendly interaction after that workflow is demonstrated.
See [the authoritative roadmap](roadmap.md).
