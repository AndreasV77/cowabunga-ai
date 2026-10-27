# Reference contract review — 2026-10-26

## Decision

**0.4 update:** contract 1.2 adds separate source orientation and record-level
model basis. [The V6 core policy](v6-core.md) now defines two selected V6-oriented
sources and four pinned comparisons. The original 1.1 review below records the
design reasoning before that extension.

Keep complete recipes distinct from musical terms, reusable phrases and
source-attributed application guidance. Introduce bundle contract 1.1 and SQLite
migration 2. Preserve the existing MUSAI recipe IDs and source snapshots.

This review uses these immutable upstream revisions:

| Source | Revision | License | Reviewed input |
|---|---|---|---|
| MUSAI | e34ad57e3450efccf792d1e4e1685ca089ce3c25 | CC0-1.0 | Structured style recipes |
| Band Manager | 73c52379833af51e9d3ce7731746d3bfff3f5266 | MIT | Metatag reference, v6 build core, safety tables, source index |
| Suno v6 Cookbook | c8e40ff0b10636a7719cbc88bc5f58443ad19907 | CC BY 4.0 | Three genre pages, section-tag guide, prompt anatomy, case schema, one English example |

Band Manager changed materially since the earlier source-map research. Current
reference paths are under `src/skills/`; the importer pins those current paths
instead of assuming the old repository layout.

## Gaps exposed by the counterexamples

| Original assumption | Counterexample | Contract change |
|---|---|---|
| Every record is a full style recipe with three settings | Band Manager has an individual guitar-role phrase | Add `ReferenceEntry`, with a phrase kind and audible meaning |
| All useful information belongs in the style field | Section cues belong in lyrics; control advice belongs in settings | Explicit optional `input_field` |
| Repository-level provenance is sufficient | A legacy refrain result is explicitly not re-tested on v6 | Exact file/line citations and per-entry model scope/context |
| A quality label can serve as confirmation | Cookbook says official-informed but verified: false | Preserve source label separately from independent verification |
| Recipe fields can represent all source material | Cookbook example has separate exclusions and lyrics | Retain exclusions, original Markdown and normalized section order separately |
| Source URL plus SPDX-like name is enough for reuse | MIT notice and CC BY attribution/change information must travel | Export full notice, author credit, license URL and adaptation notice |
| A source commit identifies a curated dataset | Editorial selections may change while upstream stays fixed | Include the curation file hash in snapshot identity |

The first reviewed selection contains 15 Band Manager entries, 15 Cookbook
entries and one Cookbook recipe. It covers instrumentation, rhythm, vocals,
production, harmony, arrangement and song structure. Definitions are our English
explanations. Exact source wording remains in each citation excerpt; the selection
must still match the pinned source or import fails. No automatic comma splitting
or automatic synonym merging is used.

### Expansion in 0.3

The expanded selection contains 83 Band Manager entries and 39 Cookbook entries,
with all 30 initial records preserved unchanged. Seven existing categories cover
this selection without changing the exchange contract. It adds instrument roles,
articulation, vocal techniques, rhythmic feel and dynamic transitions rather than
only additional genre labels. The [review glossary](vocabulary.md) exposes every
selected wording, explanation, source grade and citation.

Expanding a curation changes its hash and creates a historical version. SQLite
migration 3 therefore adds an explicit active snapshot per source. Default search
uses active selections, while `--history` or `--snapshot` preserves audit access.
No lexical score or timestamp silently chooses between source versions. New
versions must be explicitly activated after the source already has a selection.
An entry removed from an active selection is not silently recovered from history.

## Evidence boundaries and disagreements

- Band Manager's quiet `[Refrain]` workaround was production-tested in July 2026
  according to the publisher, but the source explicitly says it is not re-tested
  on v6. It is stored as legacy scoped guidance, not a current-v6 rule.
- Band Manager reports both an outside comma claim and its own counter-evidence
  for line-end commas. The counter-evidence stays searchable rather than becoming
  a blanket punctuation prohibition.
- Cookbook uses `[Main Theme - warm cello enters]` in an instrumental example.
  Band Manager recommends recognized section labels and warns against invented
  ones. Keep the cookbook cue as an unverified example. We have no listening test
  establishing which instruction works for a given model/context.
- Source phrasing and exclusions are preserved in the Cookbook recipe, even
  where Band Manager would advise a different prompt-writing convention.
- Musical vocabulary is useful independently of a demonstrated Suno effect.
  Publisher evidence labels therefore do not exclude vocabulary from search.

## Trade-offs and deferred work

Explicit selections are slower to expand than bulk extraction, but make source
scope and meaning reviewable. The included generator reproduces these selections
from pinned files; it is not a universal Markdown parser. A changed source commit
requires review rather than silently inheriting the old curation.

Per-source IDs intentionally retain duplicate or competing terms. Cross-source
concept links, user-specific preferences, experience records, provider adapters
and FastAPI remain separate next modules. No universal rules engine or ontology
is implied by the current categories. FTS is lexical; semantic ranking can be
added after useful search tasks expose its limits.
