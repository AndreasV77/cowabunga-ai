# Foundation audit and acceptance gate

Audit date: 2026-10-27. **Gate 1 is OPEN — foundation readiness has not been
established.** Implemented storage/import features and passing tests are evidence,
not a declaration that resource composition and useful coverage are complete.

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

These are concrete acceptance tasks. Do not start Gate 2 or substitute UI work
for them. Close a row with evidence and an explicit treatment of limitations;
adding more source records or more tests by itself is not closure.

| ID | Open foundation question | Required closure evidence |
|---|---|---|
| FND-01 | What resource scope and musical coverage are sufficient for the first assistant workflow? | Reviewed matrix of roles, timbre/technique, rhythm, arrangement/transitions, structure, harmony and controls; map tasks to actual source records, distinguish selection gaps from upstream gaps, and record decisions on remaining source candidates. |
| FND-02 | Which expected queries fail through wording, scope or indexing? | A maintained task-based retrieval set with expected records and negative cases, including `gallop/galloping`, spelling variants, strict-core versus supplements, wrong-tradition distractors and empty results; document/fix each loss without falsely merging traditions or evidence grades. |
| FND-03 | Can a fresh checkout demonstrate all required real-source checks rather than silently skip them? | Reproducible strict validation entry point or job: check required pinned inputs, rebuild the corpus, run real-source tests and fail clearly on missing inputs; retain normal optional developer tests as distinct from gate acceptance. |
| FND-04 | Are editorial meaning, applicable input field, model scope and conflicts sufficiently reviewed? | Item-level review of the admitted curated entries and representative recipe cases, findings register, corrections as new source/curation snapshots, and regression examples for discovered errors. Mechanical quote matching alone is insufficient. |

No numeric code-coverage percentage substitutes for these targets. For admitted
sources, the gate target is all four complete imports/round trips and all required
real-source checks running. For the retrieval task set, every expected result or
documented limitation needs an explicit disposition, including negative cases.

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
