# Licensing policy proposal — not an operative license

Status: historical policy discussion, 2026-10-27. The operative version 1.0 is now
in [LICENSE](../LICENSE); this document is retained as rationale, not as additional terms.

The [English license wording draft](license-draft.md) implements these goals for
historical review and includes practical examples. See [current guidance](licensing.md).

## Confirmed owner requirements

- Individuals should be able to use the tool privately for themselves at no cost.
- Individuals may create, publish and monetize their own songs using the tool.
  Earning money from their music does not itself require an integration license.
- Integration into another platform or project requires prior permission, which
  the owner may refuse. This includes free platforms as well as paid services.
- The owner specifically wants to prevent other platforms from monetizing access
  to this tool without permission when individuals can obtain it here for free.
- Third-party reference material retains its existing licenses and reuse rights.

MIT and AGPL do not provide this case-by-case approval right. AGPL's source-sharing
conditions are not a veto over otherwise compliant service operators. A license
with the requested restrictions would be source-available, not OSI open source.

## Proposed boundaries for review

- Permit individuals to run and modify the tool for their own use, including
  private workflows with skills, plugins and MCP clients.
- Require separate written permission to offer the tool to others as a hosted
  service, integrate or redistribute its covered code in another product, or
  distribute modified builds. Do not limit this condition to commercial services.
- Implement the confirmed permission to publish and monetize individuals' own
  songs. Proposed wording should also expressly cover their original prompts and
  lyrics without a separate tool license or mandatory tool credit.
  This must not imply ownership or unrestricted redistribution of copied source
  passages, source bundles or other third-party material contained in an export.
- Apply restrictions only to material over which the project owner has sufficient
  rights. Do not claim exclusive rights over musical vocabulary, facts, general
  methods, independently written implementations or upstream works.
- Keep upstream notices and an explicit third-party exclusion in the actual
  license. Source-derived translations and adaptations must also retain any
  applicable upstream obligations; they are not automatically wholly proprietary.
- Resolve contribution rights and permission to issue separate integration
  licenses before accepting external code contributions.

These boundaries need a precise license text before release. The owner has chosen
to proceed without commissioned legal review. The [comparison and review](license-comparison.md)
documents published models, differences and remaining uncertainty; it is not a
legal certification or an adoption of a third-party license.

## Pinned reference material

The local THIRD_PARTY_NOTICES.md records the imported revisions and notices:

| Source | Recorded license | Consequence for this proposal |
|---|---|---|
| Band Manager | MIT | Preserve the notice; upstream reuse permissions remain available. |
| Suno v6 Cookbook | CC BY 4.0 | Credit, license link and change notices; do not restrict the freedoms granted for the licensed material. |
| MUSAI Song | CC0-1.0 | No project approval right over the upstream material follows from its inclusion here. |
| LIL SYNN | CC0-1.0 | Same boundary as MUSAI. |

A platform may obtain and reuse those upstream materials under their own terms
without permission from PromptReference. Permission for this tool's covered code
does not replace the platform's third-party compliance obligations.

## Primary references

- [MIT](https://choosealicense.com/licenses/mit/)
- [AGPL-3.0](https://choosealicense.com/licenses/agpl-3.0/)
- [Open Source Definition](https://opensource.org/osd)
- [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)
- [CC0-1.0](https://creativecommons.org/publicdomain/zero/1.0/)
