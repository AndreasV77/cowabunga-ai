# Reviewed foundation expansion — 2026-10-27

This records the nine-entry expansion before the subsequent [search/field correction](search-and-field-review.md). That correction resolves the two retrieval losses and supplies Bundle 1.3 exclusion-field metadata; open-loss/null-field statements below describe this earlier step.

Added nine entries from already pinned files, following the
[selected-source gap review](foundation-gap-review.md). No upstream revision,
license, source file or existing normalized reference record was changed.
**Gate 1 and FND-01/FND-02/FND-04 remain OPEN.**

## Accepted additions

| Source | New IDs | Scope / evidence limit |
|---|---|---|
| Band Manager (5) | `choir`, `gospel-choir`, `tempo-feel-limits`, `positive-instrument-filling`, `negation-context-caveat` | Mixed-source supplementary material. Only tempo-feel guidance has a V6-targeted record basis; bare tag tables and the historical/community exception do not acquire one. |
| Cookbook (2) | `exclude-field-guidance`, `acoustic-section-entrances` | V6-targeted native guidance/example, not independently tested rendering. |
| LIL SYNN (2) | `call-response`, `half-time` | V6-native vocabulary list with editorial musical definitions; no observed execution rate. |

Every new entry retains exact, unique source excerpts and original attribution/
license data through import/export. `independently_verified` remains false;
`test_count` remains null. Rewriter or publisher confidence labels are not test
counts. Choir is not silently made equivalent to gang shouting, and half-time
does not mean halving every simultaneous musical layer.

Guidance about the separate Exclude Styles field has `input_field: null`: the
current contract supports style, lyrics and settings, but has no dedicated
exclusion field. Falsely labeling that method as style-field wording would lose
the distinction. Explicit exclusion-field metadata remains a foundation contract
question; this update does not pretend to implement it.

## Context and crosschecks

- Retained 12 concepts, with new answering-arrangement, exclusion-field/caveat and
  acoustic-entrance links where relevant. A vocabulary item need not belong to
  every concept; the reference library remains the full selection access path.
- Added `negation-context` (tension) and `tempo-scope` (complementary), for six
  editorial crosschecks. They retain context limitations and no independent
  confirmation. Absolute source statements about tempo or a universal negative
  parser are not admitted as proven rules.
- Updated exact snapshot pins and review-file hash consistently in the catalog,
  crosschecks and task suite. Old records are not retroactively promoted.

## Search and coverage effect

Current totals: **159 entries, 567 recipes**, with **68 entries and 3 recipes** in
the strict V6 core. Band Manager has 88 entries, Cookbook 47 entries and 3 recipes,
and LIL SYNN 24 entries. MUSAI remains 564 model-unspecified recipes.

The eleven briefs now have **34 retrieval probes**. Call-and-response and
half-time have explicit V6-core vocabulary candidates. Choir/Gospel Choir are
distinct supplementary entries. `exclude` finds the new field guidance, but
still misses the earlier experimental avoidance record: that specific loss
remains open, along with `gallop/galloping`. More search hits are not acceptance
of musical coverage or proof of generation effects.

Still unresolved: precise bass/guitar dependency wording, vocal-only pauses over
unchanged rhythm, harmony depth, source-candidate decisions, full semantic review
and any effects requiring listening. The lack of an exclusion-field enum is now
explicit. No assistant integration or UI feature is claimed.

## Preservation and verification

Exact pre-expansion selections and their catalog/reviews/task suite are tracked
under `curations/archive/0.11-foundation/`. Their original curation hashes identify
the old snapshots. Regression tests load those selections and prove that all old
entries and recipes are unchanged, old catalog/reviews resolve, import does not
activate a new snapshot, and old exports remain intact after explicit activation.

Strict validation: **143 tests passed, zero skipped**. The existing
Starlette/httpx deprecation warning remains. Isolated reconstruction/export,
all 34 probes, current catalog/crosschecks and history/evidence boundary tests
passed. Local report: `data/audits/foundation-expansion-20261027-accepted.json`.

The local working database was backed up consistently to ignored
`data/backups/reference-before-foundation-expansion-20261027.sqlite3`; backup
integrity and the pre-change active map/user tables were checked before import.
The three reviewed curation snapshots were then activated explicitly. All eight
pre-existing historical snapshots and all user-table row digests remained
unchanged. SQLite
integrity/foreign keys and the task audit passed after activation. The detailed
private preservation report stays in ignored
`data/audits/foundation-expansion-live-20261027.json`.

Existing draft/reference snapshots keep their original data and can appear as
historical after this deliberate source update. They are not rewritten to the
new selections. Other installations must explicitly import and activate the
new snapshot IDs after a consistent backup; a Git update alone does not change
their local database. Use the import/activation commands in README and inspect
the IDs returned by each import.

Historical seed/V6/concept builders now refuse to overwrite the newer reviewed selection.
The glossary exporter still regenerates the readable view from current curations.
The overwrite-protection regression runs all three scripts in a disposable copy.
