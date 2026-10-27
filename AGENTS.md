# Cowabunga AI — shared agent instructions

Applies to this repository and its subdirectories. Keep this file concise and
shared across coding assistants; put detailed design and history in `docs/`.

## Start here

- Read `README.md`, the head of `CHANGELOG.md` and `docs/roadmap.md` before work.
  Then read the relevant module documentation rather than the whole repository.
- Check `git status --short --branch` and the configured remote before editing.
  Other assistants and the owner may be working here; reread files before edits,
  preserve unrelated changes and coordinate overlapping work.
- Work in the actual checkout. Do not recreate the former `PromptReference`
  directory or move the checkout to an assistant's temporary working folder.
- Public project name: **Cowabunga AI**. `prompt_reference`, `prompt-ref`, the
  `prompt-reference` application namespace and existing IDs are compatibility
  identifiers. Do not rename them as a cosmetic cleanup or break saved data.
- The existing public repository uses `master`; check the live branch state
  rather than assuming `main`. The local `main` may retain pre-publication history.

## Product decisions

- Mandatory delivery order: **foundation acceptance → complete AI-assisted workflow
  → user experience**. Gate 1 is currently open; `docs/foundation-audit.md` owns
  findings and exit evidence. Do not replace unresolved basics with UI polish,
  branding, packaging or attractive features, or begin Gate 2 before Gate 1 closes.
- Passing the current suite is not proof of complete data/resource coverage.
  Keep README and progress reports explicit about manual work without an AI
  assistant. A musical brief should ultimately yield a directionally appropriate
  prompt; no ideal/optimal tag combination or guaranteed Suno result is promised.
- English is the default for reference vocabulary, prompts, lyrics metadata,
  contracts and product UI. Preserve upstream originals without translating them
  in place. Match the owner's language in conversation.
- Useful musical vocabulary matters more than speculative prompt-confidence
  claims. Write prompts around audible roles, sections, transitions and movement.
- Primary assistant integration: **MCP, skills and host plugins**, over the shared
  core. Direct model-provider APIs are optional and lower priority. Do not add an
  API-key requirement or provider SDK as a prerequisite for the core.
- Preferences, authored work, selected context and experience are application-owned
  data. Provider-specific hidden memory must not become their source of truth.
- Video, LRC, alignment and audio analysis stay separate reusable modules with
  explicit interfaces. Do not grow this workbench into an unrelated tool suite.
- The repository has implemented 0.11 foundation components; their readiness gate
  is not closed. Its MCP adapter and skill/plugin packages are not implemented.
  Check `docs/roadmap.md` before extending it.

## Architecture and module map

- Python 3.11+, Pydantic contracts, SQLite FTS5. Optional FastAPI/Uvicorn adapter;
  React/TypeScript/Vite UI. No hosted database or model provider is required.
- `src/prompt_reference/models.py`, `workspace.py`, `listening.py`, `prompt_text.py`:
  typed records and reusable domain services. `store.py` owns ordered migrations
  and reference indexing. Keep core logic independent of HTTP and React.
- `adapters/` imports source formats; `concepts.py`, `library.py` and
  `reference_selection.py` handle selected context and source-bound references.
- `server.py` composes the web app; `*_api.py` adapts core operations to HTTP.
  New adapters should reuse core validation rather than implement parallel rules.
- `web/src/components/` contains controlled views; `hooks/` owns state/actions;
  `api.ts` owns transport. Keep musical selection rules in the Python core.
- `schemas/` contains generated JSON Schema contracts. Change the Pydantic model
  first, regenerate affected schemas through the CLI and check client types.
- `sources/` stores manifests, `curations/` reviewed selections, `reviews/`
  crosschecks. Downloaded snapshots and the live SQLite store are local `data/`.
- Consult `docs/frontend-architecture.md`, `docs/workbench.md`,
  `docs/pinned-references.md`, `docs/prompt-text.md` and
  `docs/listening-notebook.md` for the corresponding behavior and invariants.

## Provenance, evidence and licensing

- Preserve repository/revision, source-file hashes, original passages, attribution,
  change notices, model scope and license information through import and export.
  Do not silently refresh pinned source content or mutate imported snapshots.
- Band Manager and the Cookbook are primary research sources; LIL SYNN and MUSAI
  are also imported. `THIRD_PARTY_NOTICES.md` and record provenance specify terms.
  Discovery directories such as Awesome-Suno are not themselves verification.
- Keep official statements, community claims, user reports, assistant inference
  and independent tests distinct. A V6 label is not proof of a musical effect.
  Do not infer controls, sample counts or listening results that were not supplied.
- Keep musical execution, rendered sound quality and replay value separate.
  Unassessed is `null`, not zero. Preserve original raw listening evidence and
  distinguish a user's causal attribution from an established cause.
- The custom source-available license in `LICENSE` is operative; AndreasV is the
  licensor. Free personal use includes monetized creative work. Platform/service
  integration requires prior written permission, including free and indirect
  API/MCP/bot offerings. Third-party rights remain separate and unrestricted by
  our approval requirement. Do not describe the project as OSI open source.
- `docs/licensing.md` is current guidance. Historical drafts and comparison notes
  are rationale, not competing licenses. Follow `CONTRIBUTING.md`; outside code
  contributions are on hold pending suitable contribution terms.

## Data integrity and local files

- Preserve exact submitted prompt/lyrics text, whitespace, hashes, immutable text
  versions, pinned source/draft snapshots and revision-conflict checks.
- Use ordered migrations; never reset a live database to make a test pass.
  Before changing a populated local store, make a consistent SQLite backup under
  ignored `data/backups/` and verify the intended preservation checks.
- Tests use temporary stores and fixtures. Do not test against the owner's live
  database or import personal drafts/listening evidence into public fixtures.
- Keep `data/`, `challenges/`, `.venv/`, built assets, logs, secrets, local assistant
  settings and `VALIDATION.md` out of commits. Do not publish copied chats, private
  screenshots or external Vault material. `docs/publication.md` records the scope.
- Record durable shared decisions in the relevant tracked docs and meaningful
  changes in `CHANGELOG.md`; do not rely on one assistant's private memory.

## Setup and verification

Run from the checkout root; the examples below use PowerShell:

```powershell
uv sync --locked --extra web
uv run --extra web python -m pytest -q
Push-Location web
npm ci
npm run build
Pop-Location
```

- For frontend-only changes, run the TypeScript/Vite build and check affected UI
  behavior. For core/API/storage changes, run the relevant Python tests; broaden
  when shared contracts or migrations are affected. Documentation-only changes
  need link, command and consistency checks, not a repeated full test suite.
- If temporary-directory access is restricted, create the parent `data/test-runs/`
  and give pytest a fresh `--basetemp=data/test-runs/<unique-run>` path.
- Real-source integration checks may skip without pinned downloaded snapshots;
  do not report skipped checks as passed or fetch a new revision to hide a failure.
- Import the pinned sources using the README before launching a fresh workbench.
  `Start-Workbench.ps1` starts/reuses the local server; `-NoBrowser` suppresses
  browser launch. A CLI alternative is `uv run --extra web prompt-ref serve`.
- After moving a checkout, its existing `.venv` may contain old absolute paths;
  check/recreate only the environment as needed, preserving ignored user data.
- Check the final diff and publication scope before committing or uploading.
  Report what changed, relevant checks, and any unresolved limitations accurately.
