# Product and integration plan

Decision updated 2026-10-27. This is the authoritative integration priority.

## Mandatory delivery gates

The owner's order is **basics first, complete assistant integration second,
user experience third**. Visual progress is not a reason to bypass open questions.

### Gate 1 — data, resource composition and controls (CURRENT: OPEN)

Audit the admitted sources, editorial quality, musical coverage, evidence grades,
reuse terms, retrieval behavior, source-change handling and reproducible real-source
tests. Keep actual evidence separate from assumed completeness. The current
[foundation audit](foundation-audit.md) records checks and blocking work FND-01–04.
FND-03 (strict reproducible validation) is closed for the current pins; resource
coverage, task-based retrieval and editorial review remain open.
Do not begin Gate 2 until the blocking work has documented closure. UI polish,
branding, app packaging and other visible enhancements wait; diagnostic changes
needed to resolve foundation defects are permitted.

### Gate 2 — complete AI-assisted work, not just connectivity

After Gate 1, implement MCP/skills/host packaging as the preferred integration.
An assistant must interpret a musical brief, retrieve relevant vocabulary, assess
fit/conflicts, distinguish sourced material from creative proposals, and produce
a coherent prompt that clearly expresses the user's intended direction. Preserve
deliberate writes, exact text versions, provenance and uncertainty throughout.

Acceptance requires a real assistant-driven workflow, including Tiny Bell and a
contrasting musical brief, missing/ambiguous/contradictory reference cases, and
save/reopen/export of the result without manual authoring outside the workflow.
Do not hard-code the historic Tiny Bell prompt or require new paid Suno generations
merely to demonstrate software integration. Listening outcomes and software tests
are different evidence. An ideal tag mixture or guaranteed musical result is not
the acceptance criterion.

README and user-facing documentation must explicitly describe what users must do
manually without an AI assistant, and which connected workflows actually exist.
A connected endpoint alone does not satisfy this gate. The UI may remain rough.

### Gate 3 — accessible, forgiving user experience

After Gate 2 demonstrates the promised assistance, iterate with owner feedback
towards a workflow usable without knowing prompting terminology. Improve defaults,
clarification, discoverability, recovery and explanations against real tasks.
Do not demand that novices manually reconstruct the assistant's composition logic.

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

## Implemented components versus acceptance

Reference import/search, source-bound context, saved drafts, listening assessments,
durable reference choices and immutable exact style/lyrics versions are implemented.
That is not a closed foundation gate or an implemented prompt-composition assistant.
The remaining foundation work is FND-01, FND-02 and FND-04, not another user-visible
feature or MCP transport. Rerun the closed FND-03 control when inputs change.

After Gate 1, deliver the MCP adapter and tested skill/plugin workflows together
as the Gate 2 user capability. Add generation-run linkage and explicit user/project/
artist context resolution as required by that workflow, without hiding missing
decisions in a provider's memory. Direct model-provider APIs remain optional later
work and must not become a prerequisite for the primary integration path.

No MCP server, skill package or host plugin is implemented yet. Their concrete
protocol/host requirements will be checked against current official documentation
when implementation begins. Hosted deployment remains open. Project code licensing
is defined in `LICENSE`; `docs/licensing.md` explains individual use, creative
monetization, integration permissions and separate third-party rights.

Video, LRC, alignment and audio analysis stay external reusable modules. The closed
Cuddlecore challenge evaluation remains a completed development-step exercise;
future software work does not imply more generation experiments.
