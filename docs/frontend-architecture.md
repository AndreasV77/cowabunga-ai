# Frontend module boundaries

The 0.11 workbench is now composed from controlled view components. The visual
markup, CSS classes and selection behavior were preserved in this extraction.

| Module | Owns |
|---|---|
| `App.tsx` | Page composition and status-message placement |
| `hooks/useWorkbench.ts` | Current-page state, initial loading, assembly, candidate selection, source-inspector state and export sequencing |
| `hooks/useWorkspace.ts` | Draft persistence, explicit defaults, revisions and unsaved-change protection |
| `components/WorkspaceBar.tsx` | Controlled draft/default controls and save status |
| `hooks/useListening.ts` | Independent draft-bound listening form, report save/update, original evidence and JSON export |
| `components/ListeningPanel.tsx` | Controlled musical-execution, sound-quality, replay and problem controls |
| `hooks/useLibrary.ts` | Full-corpus search, filters, result expansion, record inspection and Bundle export |
| `components/ReferenceLibrary.tsx` | Controlled reference search/results view |
| `components/DraftReferences.tsx` | Kept library references, historical status and inspect/remove actions |
| `hooks/usePromptVersions.ts` | Bound saved draft, exact text, immutable version history, source-context refresh and exports |
| `components/PromptEditor.tsx` | Controlled style/lyrics editing and text-history controls |
| `api.ts` | HTTP requests and response-error handling |
| `types.ts` | Shared view-facing API types |
| `presentation.ts` | Source display names, record titles and field labels |
| `components/ConceptLibrary.tsx` | Search field, concept rail and selection controls |
| `components/DirectionEditor.tsx` | Intent, target model, supplement setting, selected concept chips and assembly action |
| `components/CandidatePalette.tsx` | Initial guidance, results and individually selectable candidate records |
| `components/ReviewNotes.tsx` | Counterchecks and filtered-out records |
| `components/SourceInspector.tsx` | Evidence, provenance, original passages and license inspection |
| `components/ExportBar.tsx` | Copy/download controls and export eligibility display |

## Ownership rule

View components receive typed data and callbacks. They do not fetch from the API,
modify source records or own a second copy of page selection state. For example,
CandidatePalette reads a `ReadonlySet` of included IDs and calls
`onToggleCandidate(id)`. The hook owns the actual set update.

DirectionEditor receives readiness/assembly flags rather than requiring the
whole metadata or context packet. ExportBar receives eligibility and an action,
so it can be restyled independently of the download implementation. SourceInspector
receives only its selected record, source and open/close controls.

The hook coordinates browser behavior. Musical selection logic and source
validation remain in the Python core, accessed through the existing API. These
React types describe the view's required fields; the portable Pydantic/JSON Schema
contracts remain the data boundary for other modules.

## Adding a feature

A profile pane can be added as a controlled view with its own service/hook and
composed in App. Persistent profile data belongs behind an explicit API, rather
than inside a source-inspection or candidate component. Layout changes can move
or replace individual view components while retaining their callbacks and core
contracts. Accessibility labels and interaction invariants should be checked
alongside any subsequent visual or functional changes.

## Verification for this extraction

TypeScript checking and the Vite production build passed. The native browser
flow verified initial loading, two selected concepts producing seven candidates,
three direct wordings checked by default, individual deselection, export blocking
after changed intent, rebuilding, source-inspector updates and JSON export.
CSS compiled to the same asset hash as before the extraction. Backend/data
contracts were outside this change; the prior backend test suite was not repeated.

## Reusable workspace storage

`workspace.py` owns provider-independent JSON document contracts, namespaced storage
and revision checks. It does not import Suno concepts, HTTP or React. `workspace_api.py`
validates this application's musical forms and pins selected context to catalog/source
provenance. Its router is composed in `server.py`. Generic Draft and Preferences JSON
Schemas are available through `schema --contract draft` and `schema --contract preferences`.
Other projects can reuse the repository with their own namespace and application adapter;
this is an in-process Python interface, not yet a separately distributed service.

The workspace hook invokes the workbench's explicit restore/default operations;
visual components continue to receive data and callbacks. Preference reads do not
write, and delayed startup defaults cannot replace a direction the user already edited.

Listening observations have their own hook and draft selector; switching the main
workbench direction does not move an open report to another draft. Typed observations
and original draft snapshots live in the core listening module, not in source claims
or personal defaults. See `listening-notebook.md` for contracts and evidence limits.

App routes inspection between context candidates and direct library hits without
moving either selection into the other module. Library results remain typed source
records; they are not manufactured concept links. See `reference-library.md`.

Since 0.10, kept references belong to useWorkspace's draft lifecycle; useLibrary
still owns only search/inspection/single-record export. The picker and kept-list
components receive typed records/callbacks. LibrarySelection and DraftReferencePack
are portable core contracts; persistence is parallel to reviewed concept context,
with original source versions retained. See `pinned-references.md`.

The text editor explicitly binds to a saved draft and retains that binding when
the main workbench changes. Its own hook protects unsaved text and appends versions
through the prompt-text core. It does not modify reference selection or invoke AI
providers. Integration priority is defined in `roadmap.md`: MCP/skills/plugins first.
