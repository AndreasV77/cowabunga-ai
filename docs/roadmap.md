# Product and integration plan

Decision updated 2026-10-27. This is the authoritative integration priority.

## Integration decision

The primary AI integration path is **MCP, skills and host-specific plugins**.
Direct model-provider APIs are a later, optional path. Provider independence alone
does not express this priority; plans and partner summaries should name it explicitly.

- **Shared core:** reference records, drafts, prompt/lyrics versions, explicit
  preferences and experience remain application-owned, with versioned contracts.
- **MCP adapter:** expose deliberate core operations to connected assistants:
  search/inspect references, obtain selected context, work with drafts and text
  versions, and record user-confirmed observations. The adapter reuses core validation.
- **Skills:** describe musical prompting/review workflows, evidence boundaries and
  how to use the exposed operations. Skills do not become a second database.
- **Plugins:** package workflows, connector configuration and installation for the
  respective host. Host-specific packaging must not fork the underlying records.
- **Direct model-provider APIs:** optional later support for standalone AI features.
  They must use the same selected context and explicit preferences as other clients.

The existing FastAPI REST adapter connects our own UI and core. It is not a model
provider API dependency. Implementing ordinary application endpoints does not
change the integration priority above.

## Delivery order

1. Completed foundation: provenance-preserving reference import/search, reviewed
   context, saved drafts, listening assessments and durable free reference choices.
2. Completed in 0.11: exact style/lyrics text, immutable versions and hashes linked
   to saved draft/source context. This gives assistants a stable editing target.
3. Next: first MCP adapter over the existing core, with explicit read/write boundaries
   and tests for provenance and deliberate mutation. No provider SDK prerequisite.
4. Initial skill workflows and host/plugin packaging; validate real assistant use.
5. Expand exact generation-run linkage and user/project/artist context resolution,
   based on those workflows and user reports.
6. Optional direct model-provider adapters after the assistant integration path.

No MCP server, skill package or host plugin is implemented yet. Their concrete
protocol/host requirements will be checked against current official documentation
when implementation begins. Hosted deployment remains open. Project code licensing
is defined in `LICENSE`; `docs/licensing.md` explains individual use, creative
monetization, integration permissions and separate third-party rights.

Video, LRC, alignment and audio analysis stay external reusable modules. The closed
Cuddlecore challenge evaluation remains a completed development-step exercise;
future software work does not imply more generation experiments.
