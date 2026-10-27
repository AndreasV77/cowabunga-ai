# Publication scope

The repository includes the reusable core, optional local web workbench, contracts,
curations, source manifests, reviews, tests and reproducible import tools.

Local SQLite databases, preferences, authored drafts, listening evidence, challenge
working directories, screenshots, downloaded source snapshots, logs and the detailed
machine-specific VALIDATION.md are excluded. The files remain in the local workspace.
The public test suite does not require the private challenge directory.

`tests/fixtures/musai-vocabulary.json` is a small unmodified source-bound CC0 recipe
selection. Its repository, revision and file hashes are retained in the bundle;
see THIRD_PARTY_NOTICES.md. Listening-conversion tests use synthetic reports.

## Validation

Run `uv sync --locked --extra web`, then `uv run pytest`.
Optional checks skip when pinned source snapshots or the built web assets are absent.
Synthetic core and API tests run without downloaded source snapshots.
For the UI, run `npm ci` and `npm run build` in `web/`.

Before publication, also verify a clean source copy with no local data directory.
No CI, hosted deployment or implemented MCP adapter is implied by this document.

Preparation check on 2026-10-27: the working checkout passed 90 tests. A separate
copy containing only the 116 publishable files passed 83 tests with 7 optional
checks skipped, without private challenge files, downloaded snapshots or built UI
assets. Both runs reported the existing Starlette/httpx deprecation warning.

Final license preparation on 2026-10-27: adopted custom license version 1.0 under
AndreasV, preserving separate reference-source rights. Package metadata uses
`LicenseRef-PromptReference-Personal-Use-1.0`; a wheel build succeeded and contains
LICENSE and THIRD_PARTY_NOTICES.md. The dependency lock remains current. Public
document links and frontend license metadata were checked. Staged files exclude
private working directories and contain no matches for the credential patterns
checked; this is not a guarantee that every possible secret format is detectable.
