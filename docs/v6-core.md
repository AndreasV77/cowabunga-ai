# V6 core policy and source counterchecks — 0.4

## What the core means

The core contains **68 entries and 3 recipes from two explicitly V6-oriented
publishers**: 44 entries and 3 recipes from MJorgin's Cookbook; 24 entries from
LIL SYNN. Each selected record has an explicit V6-family target. These are
application candidates, not 71 verified effects.

| Source | Reviewed orientation | Role |
|---|---|---|
| Suno v6 Cookbook | `v6_native` | Original V6 examples, model routing, genre descriptions and failure cases |
| LIL SYNN V6 Guide | `v6_native` | Vocal dimensions, concrete phrasing, production descriptions and testing discipline |
| Band Manager | `mixed` | V6-targeted guidance plus version-unspecified vocabulary and one explicitly legacy finding |
| MUSAI | `unspecified` | Broad recipe vocabulary; model version remains unknown |

`v6_native` records a reviewed declared purpose, anchored to a pinned source
introduction. It is **not** a forensic claim that the author used no earlier
knowledge, and it does not establish independence of underlying evidence.

Source orientation and per-record `evidence.model_basis` are separate axes.
The latter is `unspecified`, `v6_targeted`, or `pre_v6`. Existing source grades,
model scope, sample-size information and context remain separate. All imported
effects remain `independently_verified: false`. No new field infers an experiment
from the repository name, date, V6 label or agreement between authors.

Three general Cookbook tag examples lack explicit record-level V6 scope and
therefore stay outside the strict core despite the source's V6 orientation.
Mixed-source V6 records are searchable separately; old vocabulary is retained.

## Search and review

```powershell
.\.venv\Scripts\python.exe -m prompt_reference.cli search 'vocal' --v6-core
.\.venv\Scripts\python.exe -m prompt_reference.cli search 'riff' --model-basis v6_targeted
.\.venv\Scripts\python.exe -m prompt_reference.cli search 'refrain' --model-basis pre_v6
.\.venv\Scripts\python.exe -m prompt_reference.cli stats --v6-core
.\.venv\Scripts\python.exe -m prompt_reference.cli crosschecks reviews/v6-crosschecks.json
```

Default search gives matching active V6-core records priority, then orders lexical
matches within the groups. `--v6-core` limits results to the core. The hit's
`v6_core` flag is a relevance flag, not a confidence label. History and explicit
snapshot searches keep their earlier meanings.

## Six concrete crosschecks

The machine-readable review set pins exact curation snapshot IDs and links to
the selected records, so later imports cannot silently change the reviewed text.

| Topic | Comparison | Result |
|---|---|---|
| Model roles | LIL SYNN discovery loop and Cookbook Cassette Highway | Complementary exploration/refinement advice; official model roles support the broad distinction, not faithful reconstruction |
| Exclusions | LIL SYNN's experimental avoidance and positive replacement versus Cookbook's explicit exclusion field | Useful alternatives; neither source proves a universal negation rule |
| Live drums | Cookbook's requested live drums versus Band Manager room-sound advice | Tension retained; the word is not automatically banned |
| Vocal facets | Behind-the-beat timing versus conversational delivery | Complementary musical dimensions rather than interchangeable labels |
| Negation context | Band Manager bracket exception, Cookbook field guidance and LIL SYNN experimental wording | Tension retained; no deterministic rule across all input contexts |
| Tempo scope | Band Manager's limited feel guidance and LIL SYNN half-time vocabulary | A pulse/feel distinction, not a verified impossibility law |

Official primary baseline checked on 2026-10-26:
[Current Models: v6](https://help.suno.com/en/articles/13924737).
The official [Creative Sliders page](https://help.suno.com/en/articles/6141377)
was also checked, but is dated 2025. It supports broad control descriptions, not
a new V6-specific causal claim. It is not counted as a second V6 test.

Cookbook and LIL SYNN both draw on official Suno material. Two publishers can
repeat one underlying claim. The review cases therefore explicitly retain
`independent_test_confirmation: false`; agreement never increments a test count.

## Exclusions and deliberate limits

The LIL SYNN Audio Quality Rescue recipe was reviewed but not imported as a
validated repair. It prescribes exact values without a published paired-audio
test corpus in the reviewed files. Production-concept translations are kept as
wording suggestions, not technical guarantees or measurements.

Only English text-oriented Cookbook examples were added: Cassette Highway and
Break the Silence. Original text, exclusions, instructions and `verified: false`
are preserved. Source parsing checks the frontmatter model against the declared
target scope. Source code and skills from the repositories are never executed.

The existing 0.3 selections are preserved in `curations/archive/0.3/`. Contract
1.2 adds metadata; existing SQLite tables and historical records are retained.
Old 1.0/1.1 bundles load with unspecified new fields instead of invented claims.
