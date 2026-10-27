# Strict foundation validation

This checkout-only developer check addresses FND-03. It validates pinned inputs
and software behavior; it does not establish musical effectiveness, sufficient
vocabulary coverage or complete editorial review. Gate 1 has other open tasks.

## Fresh checkout

From the repository root:

```powershell
uv sync --locked --extra web
$musai = 'e34ad57e3450efccf792d1e4e1685ca089ce3c25'
$band = '73c52379833af51e9d3ce7731746d3bfff3f5266'
$cook = 'c8e40ff0b10636a7719cbc88bc5f58443ad19907'
$lil = '6b805bf77a350e7fba00bfd2451273327482827c'
uv run --locked --extra web python -m prompt_reference.cli fetch-musai $musai "data/sources/musai/$musai"
uv run --locked --extra web python -m prompt_reference.cli fetch-reference band-manager $band "data/sources/band-manager/$band"
uv run --locked --extra web python -m prompt_reference.cli fetch-reference cookbook $cook "data/sources/cookbook/${cook}-v0.4"
uv run --locked --extra web python -m prompt_reference.cli fetch-reference lil-synn $lil "data/sources/lil-synn/$lil"
uv run --locked --extra web python -m prompt_reference.foundation --report data/audits/foundation-strict-001.json
```

Only fetch missing snapshots. Fetch refuses to overwrite existing directories;
a partial or damaged download must be investigated rather than silently reused.
The validation command never downloads, refreshes or repairs source data. Once
dependencies and snapshots exist, it runs offline. No import into the working
database or frontend build is required. Use a new report filename for each run.

## Required checks and failure behavior

- Check all four local manifests against the tracked pins: identity, repository,
  revision, license and complete file-to-SHA-256 maps. Retrieval timestamps may
  differ. Rehashing a modified local file and its manifest cannot bypass the pin.
- Use the production adapters to validate actual file hashes, licenses, excerpts,
  curations and input contracts. Cookbook uses the expanded eleven-file snapshot,
  not its older nine-file selection.
- Rebuild a fresh isolated store, check full source/entry/recipe export equality,
  repeat-import idempotency, SQLite integrity and foreign keys.
- Resolve all pinned crosschecks and catalog links; build and validate each
  concept packet both with and without supplementary sources.
- Evaluate the [task and retrieval audit](foundation-tasks.md) against its pinned
  sources. Its report retains known search losses and coverage gaps explicitly;
  matching those observations is not acceptance of their musical sufficiency.
- Run the complete Python suite, including real-source and web-adapter tests.
  Any failure, collection/runtime skip, deselected test or expected-failure marker
  makes the command unsuccessful. Missing pytest/web dependencies cannot count
  as a successful reduced run. Ordinary `python -m pytest` retains its optional
  source behavior for development and is not a substitute for this command.

The exit code is zero only on success. A new JSON report records timestamps,
reconstruction results, test outcomes and incomplete test IDs, or a preflight
error. A missing input stops validation before tests. Existing reports are never
overwritten. Report creation errors fail immediately. Temporary stores and test
directories live under ignored `data/test-runs/` and are removed after the run;
the owner's working database is never opened. Reports belong under ignored
`data/audits/`, not in public fixtures.

## Tests of the validator

`tests/test_foundation.py` checks missing pins, altered local manifest hashes,
refusal to rebuild an existing database, passing/failing/skipped/xfail subprocess
tests, failure report contents and report overwrite refusal. The complete strict
run supplies the real-corpus round-trip and catalog checks.

When pins, curations, adapters or search behavior change, rerun strict validation
alongside the coverage, retrieval and editorial reviews in
[the foundation audit](foundation-audit.md). A passing report closes only the
mechanical validation task, not the entire foundation gate.
