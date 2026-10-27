# Cowabunga AI

**Your AI music buddy — ready to be your new best friend.**

An English-first, provider-independent music creation workbench built around
source-backed vocabulary, deliberate prompt design and documented experience.
Previously developed under the working name PromptReference; implementation
started 2026-10-26. The Python package `prompt_reference`, CLI `prompt-ref`,
application identifiers and local data formats retain their existing names.

The core imports MUSAI style recipes and reviewed selections from Band Manager,
Suno v6 Cookbook and LIL SYNN into SQLite. It preserves source data, licenses, attribution
and evidence limits, searches with FTS5, and exports portable JSON bundles.
The core CLI requires no AI account, API key, database server or web server.

## Local workbench

Version 0.11 provides an English React/TypeScript workbench served by an optional local
FastAPI adapter. The data core and CLI remain usable without the web extra.

After the source imports described below, install and build once:

```powershell
uv sync --locked --extra web
Set-Location web
npm ci
npm run build
Set-Location ..
.\Start-Workbench.ps1
```

Open [the local workbench](http://127.0.0.1:8765). The launcher reuses an existing
Cowabunga AI server, or starts one hidden in the background with logs under
`data/logs/`. `-NoBrowser` starts it without opening the default browser.
Alternatively, run the foreground server and stop it with Ctrl+C:

```powershell
.\.venv\Scripts\python.exe -m prompt_reference.cli serve
```

Choose concepts, describe the musical direction and assemble a selection. Direct
wording candidates start included; alternatives, dimensions and complete recipes
require selection. Inspect any candidate's source notes, original passages and
reuse terms. Export the checked candidates as Markdown/JSON or copy their context.
Changing direction/model/concepts/source scope requires rebuilding before export.
Save named drafts locally, including candidate choices and their exact source-backed
context. Reopen a draft after refreshing. Explicit personal defaults for target
model and source scope apply to new drafts; prompts remain English.
Saving is deliberate, with a warning before discarding unsaved changes.
Artist/project profiles and learned experience remain separate future modules.

See [workbench operation and API](docs/workbench.md).

The [direct reference library](docs/reference-library.md) searches the full active
corpus, including recipes outside the concept palette. Filter by V6 core or type,
inspect source/model/license information and export individual references as
portable source-bound JSON bundles. [Keep references with a draft](docs/pinned-references.md)
to preserve choices across searches and reloads, retain exact source versions and
export them together with selected concept context.

The [style and lyrics editor](docs/prompt-text.md) stores exact authored text in
immutable versions, linked to saved draft/source context. Older versions can be
reused as new versions; text and complete version JSON can be exported.

The [listening notebook](docs/listening-notebook.md) records musical execution,
sound quality and personal replay value separately. Reports retain original
evidence and the exact linked draft context, with JSON export and revision checks.

The first practical case explored Mongolian throat singing with kawaii metal.
Personal drafts, listening reports, screenshots and local databases are excluded
from this repository. Tests use synthetic reports and a source-bound CC0 vocabulary
fixture instead. See [publication scope](docs/publication.md).

## Setup (PowerShell)

Python 3.11+ and uv are required. From this directory:

```powershell
uv sync --locked
```

This workspace was verified with Python 3.13.12. If the Windows Store Python
alias shadows an installed interpreter, pass its actual path with `--python`.
An alternative setup without uv is `python -m venv .venv`, followed by
`.\.venv\Scripts\python.exe -m pip install -e . pytest` (not lockfile-pinned).

## Reproduce the first import

The snapshot below was resolved from the upstream main branch on 2026-10-26.
Fetch refuses to overwrite an existing directory. After fetching, all other
operations work offline.

```powershell
$revision = 'e34ad57e3450efccf792d1e4e1685ca089ce3c25'
.\.venv\Scripts\python.exe -m prompt_reference.cli fetch-musai $revision "data/sources/musai/$revision"
.\.venv\Scripts\python.exe -m prompt_reference.cli import-musai "data/sources/musai/$revision"
.\.venv\Scripts\python.exe -m prompt_reference.cli snapshots
.\.venv\Scripts\python.exe -m prompt_reference.cli search 'acoustic bass' --limit 5
.\.venv\Scripts\python.exe -m prompt_reference.cli export "musai@$revision" 'data/exports/musai.json'
.\.venv\Scripts\python.exe -m prompt_reference.cli schema 'schemas/bundle.schema.json'
.\.venv\Scripts\python.exe -m pytest
```

The installed `prompt-ref` command is an equivalent entry point. The module form
above also works where the Windows sandbox blocks console-script launchers.
Use `--db path/to/database.sqlite3` **before** the subcommand to select a database.
Search returns complete records with snapshot identifiers, not only prompt text.
Words are matched literally with AND semantics; FTS operators are not exposed.
Search can be restricted with `--snapshot "musai@$revision"`. Multiple source
revisions are retained; default search uses the active selection of each source.
Use `--history` to include older selections. Export refuses to overwrite a file.

## Band Manager and Cookbook seed imports

Version 0.4 includes **150 selected entries and three Cookbook recipes**, not an
exhaustive import of either repository. The reviewed selections live in
`curations/`; wording, definitions, categories and evidence scope can be reviewed
there before importing. No upstream skill is installed or executed.

```powershell
$band = '73c52379833af51e9d3ce7731746d3bfff3f5266'
$cook = 'c8e40ff0b10636a7719cbc88bc5f58443ad19907'
$lil = '6b805bf77a350e7fba00bfd2451273327482827c'
.\.venv\Scripts\python.exe -m prompt_reference.cli fetch-reference band-manager $band "data/sources/band-manager/$band"
.\.venv\Scripts\python.exe -m prompt_reference.cli fetch-reference cookbook $cook "data/sources/cookbook/${cook}-v0.4"
.\.venv\Scripts\python.exe -m prompt_reference.cli fetch-reference lil-synn $lil "data/sources/lil-synn/$lil"
.\.venv\Scripts\python.exe -m prompt_reference.cli import-reference "data/sources/band-manager/$band" curations/band-manager.json
.\.venv\Scripts\python.exe -m prompt_reference.cli import-reference "data/sources/cookbook/${cook}-v0.4" curations/cookbook.json
.\.venv\Scripts\python.exe -m prompt_reference.cli import-reference "data/sources/lil-synn/$lil" curations/lil-synn.json
.\.venv\Scripts\python.exe -m prompt_reference.cli search 'midrange' --kind phrase
.\.venv\Scripts\python.exe -m prompt_reference.cli search 'refrain' --kind guidance
.\.venv\Scripts\python.exe -m prompt_reference.cli search 'Main Theme' --kind phrase
.\.venv\Scripts\python.exe -m prompt_reference.cli search 'detached' --category vocals
.\.venv\Scripts\python.exe -m prompt_reference.cli stats
```

If the snapshots already exist, skip fetching. Each import prints its snapshot
ID, including the curation file's SHA-256 hash. Use that full ID for `export` or
`--snapshot`. A changed reviewed selection gets a separate snapshot even when
the upstream commit is the same. Original source records are never overwritten.

**When updating an existing source:** import does not replace its active selection.
Run `activate` with the snapshot ID printed by the import to select the new one:

```powershell
.\.venv\Scripts\python.exe -m prompt_reference.cli activate 'SOURCE@REVISION+CURATION_HASH'
.\.venv\Scripts\python.exe -m prompt_reference.cli search 'sidechain' --history
.\.venv\Scripts\python.exe -m prompt_reference.cli stats --history
```

The first version imported for a source is activated automatically. Importing or
re-importing another version does not change the selection. `--snapshot` searches
that exact snapshot even when inactive. Migration 3 activates a source's sole
existing snapshot; if a source already has several, it requires an explicit
selection rather than guessing. `snapshots` lists all available IDs and `stats`
shows active selections. Activation is reversible and does not delete history.
The exact initial 0.2 and 0.3 curations are preserved under `curations/archive/`.

Search supports `--kind recipe|term|phrase|guidance`; without it, both complete
recipes and reference entries are searched. `--category` restricts results to
reference entries in that musical category. Hits carry source metadata, including
attribution and license notices. Matching active V6-core records rank before other
matches, then FTS ranks lexical relevance, not musical efficacy;
scores from the two indexes do not establish a calibrated cross-type ranking.

For human review, open [the English vocabulary](docs/vocabulary.md). It includes
83 Band Manager entries, 45 Cookbook entries and 22 LIL SYNN entries with direct source citations.
Reproduce it after fetching the pinned sources:

```powershell
.\.venv\Scripts\python.exe tools/build_v6_core.py
.\.venv\Scripts\python.exe tools/export_glossary.py
```

## Explicit V6 core

The core contains **64 entries and three recipes from two V6-native sources**:
Cookbook and LIL SYNN. Source orientation is anchored to an exact introduction;
record-level `model_basis` distinguishes V6 targeting, legacy information and
unspecified applicability. Targeting does not mean tested efficacy. Mixed-source
Band Manager V6 records remain separately searchable.

```powershell
.\.venv\Scripts\python.exe -m prompt_reference.cli search vocal --v6-core
.\.venv\Scripts\python.exe -m prompt_reference.cli search riff --model-basis v6_targeted
.\.venv\Scripts\python.exe -m prompt_reference.cli stats --v6-core
.\.venv\Scripts\python.exe -m prompt_reference.cli crosschecks reviews/v6-crosschecks.json
```

Four pinned editorial comparisons cover model routing, exclusions, live-drum
wording and vocal dimensions. They do not turn agreement between publishers into
independent tests. See [V6 core policy and counterchecks](docs/v6-core.md).
`tools/build_seed_curations.py` reproduces the historical 0.3 selection; use the
V6 builder above for the current selection.

## Modules and data flow

Version 0.5 adds [concept lookup and context assembly](docs/concepts-and-context.md):

```powershell
.\.venv\Scripts\python.exe -m prompt_reference.cli concepts 'intimate singer'
.\.venv\Scripts\python.exe -m prompt_reference.cli context vocal-placement verse-chorus-contrast --intent 'Intimate verses opening into a wider chorus' --format markdown
```

Twelve reviewed concepts link source wording, dimensions, examples and
alternatives. Context packets default to V6-core candidates and carry evidence,
notices, omissions and relevant counterchecks. They are inspectable context for
composition, not an automatically finished prompt. No AI or network call occurs.

```text
Pinned upstream files → MUSAI adapter → validated Bundle → Store → SQLite/FTS5
                                              ↑             ↓
                                    JSON Schema         JSON export
```

- `models.py` defines the shared, versioned exchange contract (Pydantic).
- `adapters/musai.py` owns upstream-specific parsing and mapping.
- `adapters/curated.py` checks pinned Markdown snapshots against explicit reviewed selections.
- `store.py` exposes import, search, snapshot listing and export independently of CLI.
- `cli.py` is the initial consumer. A later FastAPI layer can use the same interface.
- `concepts.py` supplies reviewed concept lookup, portable context packets and Markdown rendering.
- `schemas/bundle.schema.json` is generated, not hand-maintained.

SQLite's `user_version` tracks ordered schema migrations. Imports are transactional
and repeatable: the same source/revision/content imports zero new records;
conflicting content for that revision is rejected. IDs derive from source URLs,
not titles. New revisions coexist with old ones. The database is local runtime
state, excluded from Git. Source snapshots include README, LICENSE, datapackage,
original styles JSON, retrieval time and SHA-256 checksums. Checksums detect local
changes; they are not signatures or independent verification of musical claims.

## Evidence and source boundaries

[MUSAI Song's suno-style-recipes](https://github.com/samuelgrupolimex-prog/suno-style-recipes)
publishes the dataset under CC0-1.0. Its license text is retained in every snapshot.
Original records remain intact alongside normalized recipes. Exact source bytes
remain in the snapshot. No derived text or vocabularies are presented as original.

MUSAI values are **publisher recommendations**, not verified Suno behavior.
Model version is unknown (`null`), not inferred from the download date. Missing
tempo remains null. Genre families and proposed structures are source-specific
descriptions, not authoritative music taxonomy or guaranteed Suno syntax.
`prompt_language` describes the English prompt text, not the original title;
some original titles are Spanish and are preserved without silent translation.
At the pinned revision, README/datapackage describe nine free-time styles but
the actual JSON has three null BPM values. The importer preserves the JSON
values and does not fill in or remove tempos to match that prose claim.

Contract 1.2 separates recipes, settings, terms, phrases and application guidance,
and adds source orientation, per-record model basis and optional workflow.
English explanations are editorial adaptations, not verbatim source definitions.
Entries retain source-specific identity; similarly named concepts from different
sources are not automatically merged. Confidence does not gate vocabulary import.
The old 1.0 and 1.1 formats remain readable. Missing model-basis and orientation
fields default to unspecified. Source records remain untouched; source activation
uses schema 3, local workspace documents add schema 4 and authored text histories
add schema 5. Exports use the current
1.2 bundle contract.

Band Manager is MIT-licensed; its full notice travels with derived exports.
Cookbook is CC BY 4.0; author credit, source links, license link and change notice
are included. LIL SYNN is CC0, with source and license notice preserved.
Publisher labels such as HIGH, LOCAL-CONFIRMED or official-informed
remain publisher labels. Every new entry explicitly has
`independently_verified: false`. An unspecified model scope is an empty list,
not an inferred v6 certification. Cookbook's example retains `verified: false`
in its original Markdown and `unverified_example` in the normalized record.
Repository copies of the source notices are in
[THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).

See [the data model review](docs/data-model-review.md) for scope decisions and
source disagreements. Awesome Suno Prompts remains an accepted candidate;
Awesome-Suno is a discovery directory.

## Next boundaries

The [product and integration plan](docs/roadmap.md) makes MCP, skills and host-specific
plugins the primary AI integration path. Direct model-provider APIs are optional
and lower priority. The current REST adapter connects the application UI/core;
it is not a model-provider dependency.

The reference/context, draft, explicit-default and listening foundations are
implemented, including versioned style/lyrics content. Next comes the first MCP
adapter and skill/plugin workflows over the same core. Project/artist preference
resolution and complete generation-run linkage follow those integration workflows.

Video, LRC, alignment and audio analysis remain reusable external modules.
Revisit JSON payload storage when larger relationships and filtered claims require
relational tables; concurrent hosted services would also require revisiting storage.

Technical references: [Pydantic models](https://docs.pydantic.dev/latest/concepts/models/),
[Python sqlite3](https://docs.python.org/3/library/sqlite3.html).


## Working with coding assistants

Shared project instructions are in [AGENTS.md](AGENTS.md). [CLAUDE.md](CLAUDE.md)
imports that same file for Claude Code, keeping architecture, evidence boundaries
and working conventions in one place. Start assistants in the repository root.

## Code license

Copyright (c) 2026 AndreasV. The custom [Personal Use and Integration License](LICENSE)
permits free individual use, private modifications and monetization of your own
creative work. Platform integration, services for other users and distribution of
builds require prior written permission, including free offerings.

See [examples and integration requests](docs/licensing.md). This is source-available
software, not OSI open source. Third-party reference material retains its own terms
in [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).
