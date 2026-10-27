# Concepts and context packets — 0.5

The reference corpus remains 150 entries and 567 recipes, including the 64-entry,
3-recipe V6 core. This release makes a reviewed subset easier to select rather
than adding more source material.

## Twelve musical concepts

| ID | Selection task |
|---|---|
| `vocal-placement` | Apparent vocal distance and foreground/background balance |
| `vocal-phrasing` | Phrase length, syllable density and ornamentation |
| `vocal-timing` | Beat placement versus conversational delivery |
| `vocal-texture` | Grainy, husky, rough or breathy color |
| `verse-chorus-contrast` | Separate instrumental/vocal jobs across sections |
| `kick-bass-space` | Timing coordination, ducking and spatial bass behavior |
| `stereo-depth` | Left-right spread versus near-far distance |
| `acoustic-drums` | Acoustic performance character, density and room |
| `hook-focus` | Repeated ideas and space for a hook |
| `positive-replacement` | Desired replacement roles versus separate exclusions |
| `model-routing` | Exploration and controlled refinement |
| `acoustic-room` | Room color, breath and apparent distance |

The catalog lives in `curations/concepts.json`. Links have explicit editorial
roles: `wording`, `dimension`, `example`, or `alternative`. Sharing a concept
does not make phrases synonyms, prove their effect, or mean they should all be
combined. Falsetto/head voice, long notes/melisma, width/depth and bass
coordination/ducking remain distinct musical choices.

## Use from PowerShell

After importing and activating the source snapshots described in README:

```powershell
.\.venv\Scripts\python.exe -m prompt_reference.cli concepts
.\.venv\Scripts\python.exe -m prompt_reference.cli concepts 'intimate singer'
.\.venv\Scripts\python.exe -m prompt_reference.cli context vocal-placement verse-chorus-contrast --intent 'Intimate verses opening into a wider chorus' --format markdown
.\.venv\Scripts\python.exe -m prompt_reference.cli context acoustic-drums --supplementary --output data/exports/drum-context.json
```

Concept search uses reviewed English labels, descriptions and aliases. It is
literal token lookup, not an embedding model or an automatic interpretation of
arbitrary prose. Context selection uses exact concept IDs.

Options include `--model v6|v6-wild|v6-mini`, `--limit 1..100`, JSON or Markdown
format, and explicit catalog/review paths. Output files cannot be overwritten.
Default context includes V6-core candidates only; `--supplementary` permits
mixed/unspecified-model candidates, with their limits still attached. An explicit
model mismatch is omitted even when supplements are enabled.

## What a packet contains

- The user's intent and requested target model, preserved as input.
- The exact catalog content hash and selected concept descriptions.
- Deduplicated source records, ordered with V6 candidates first, and every concept
  relation explaining why a record was selected.
- Exact snapshot IDs, record-level evidence, source citations and full notices.
- Relevant source counterchecks, including disagreements and evidence limits.
- Explicit omissions for outside-core candidates, target-model mismatch or limits.

Relevant counterchecks may cite a supplementary source even when candidate
selection is core-only. Such citations do not silently add supplementary prompt
wording. The packet distinguishes candidate items from countercheck notes.

JSON retains original recipe records; the Markdown view shows relevant style
wording and source exclusions separately. It does not rewrite historical prompts,
mix exclusions into the style field or paste every alternative into one prompt.
Settings/workflow advice remains identified as advice rather than a style string.

An inactive source selection causes an error for a selected candidate. A changed
crosscheck file also requires review. Neither a newer active source nor changed
comparison text is substituted automatically. This keeps context reproducible.

## Portable interfaces

`CatalogService.find()` and `CatalogService.build_context()` are independent of
the CLI and can be reused by a web UI or provider adapter. `render_context()`
produces the human-readable view. The module performs no network or AI calls.

```powershell
.\.venv\Scripts\python.exe -m prompt_reference.cli schema schemas/concepts.schema.json --contract concepts
.\.venv\Scripts\python.exe -m prompt_reference.cli schema schemas/context.schema.json --contract context
```

`tools/build_concepts.py` is a historical 0.5 generator and refuses to overwrite
the newer reviewed catalog. Use current curated JSON and strict foundation
validation; reproduce the historical generator in a separate historical checkout.

The source Bundle remains contract 1.2; current SQLite migrations reach schema 5. ConceptCatalog
and ContextPacket are separate version-1.0 contracts. Catalog links stay in
reviewable JSON at this scale; relational concept storage can be introduced
behind this interface if larger relationships or editing workflows require it.

Explicit profiles, learned preferences and session memory are still separate
future modules. They are not inferred from an intent or saved automatically.
