# License comparison and draft review

Research date: 2026-10-27. These are observations of published texts and our
interpretation of their fit. Publication or adoption is not evidence of judicial
enforceability. We have not verified court decisions validating these clauses.
No third-party license is being adopted, combined or relabeled here.

## Comparable projects and licensing models

| Primary source | Observed boundary | Fit for PromptReference |
|---|---|---|
| [n8n repository license](https://github.com/n8n-io/n8n/blob/master/LICENSE.md) | Distinguishes internal/personal/noncommercial use and free noncommercial distribution from other uses; separates third-party components. | Useful structural comparison, but grants broader internal and noncommercial rights than our intended individual-use grant. |
| [n8n use-case guidance](https://support.n8n.io/article/can-i-use-your-license-for-my-use-case) | Distinguishes client outputs from access to configure workflows, including access through APIs, MCP or agents. | Useful analogy for completed creative work versus offering tool functions. Product guidance is not our license and may change. |
| [Dify repository license](https://github.com/langgenius/dify/blob/main/LICENSE) | Allows commercial uses, including backend applications, but requires written authorization for multi-tenant environments. | Demonstrates explicit permission requirements; narrower trigger than ours. We do not copy its branding or contributor provisions or call our license Apache. |
| [Elastic License 2.0](https://www.elastic.co/licensing/elastic-license) and [official FAQ](https://www.elastic.co/licensing/elastic-license/faq) | Restricts managed/hosted offerings exposing substantial functionality; permits modification and redistribution subject to its limits. | The substantial-functionality threshold and permitted embedded uses are broader than our requirement. Do not silently import those exceptions. |
| [PolyForm Shield 1.0.0](https://polyformproject.org/licenses/shield/1.0.0) | Permits uses except competing products, including competition across interfaces and free offerings. | Supports checking function rather than interface or price. Competition is a different trigger from prior permission for every platform integration. |
| [PolyForm Noncommercial](https://polyformproject.org/licenses/noncommercial/1.0.0) and [Strict](https://polyformproject.org/licenses/strict/1.0.0) | Both allow noncommercial purposes and specified organization uses; Noncommercial permits changes/distribution, Strict does not. | Neither matches the combination of private modifications, monetized creative work and permission-based platform integration unchanged. |
| [Functional Source License](https://fsl.software/) | Each release converts to MIT or Apache after two years. | Not a fit for a continuing permission requirement; we do not adopt a timed conversion. |

Repository links above follow moving branches. They identify observations on the
research date, not frozen source snapshots or imported project dependencies.
No license text was copied wholesale into our draft; the comparison informs an
independently worded custom license. It does not transfer any third-party legal
review to our wording.

## Review of our draft

| Check | Result / action |
|---|---|
| Monetized songs versus paid tool access | Separate grants and restrictions; commercial creativity is expressly allowed. |
| Hidden backend/API/MCP/bot integration | Clarified that indirect access and partial functionality still require permission. |
| Public and free community tools | Permission requirement does not depend on price or profit. |
| Private MCP client or private server | Allowed for the individual's use; interface alone does not trigger a restriction. |
| Outputs used as an integration loophole | Completed creative work is allowed; automated access to tool functions is not excused by returning only outputs. |
| Human creative commissions | Allowed; delivering a song/prompt as creative work does not itself supply tool access. |
| MIT/CC BY/CC0 source rights | Excluded from our restrictions, including source-derived reference material; separate upstream terms remain. |
| Private source modifications | Allowed; distributing builds is a separate permission. |
| Public source hosting | Host's independently granted rights are preserved; no blanket no-fork claim. |
| Source/license visibility | No claim that this custom restrictive license is OSI open source or a standard license. |
| Separate permission | Affirmative written authorization; attribution or silence is not approval. |
| Later releases | No retroactive withdrawal of compliant individual-use grants. |
| External contributions | Separate contribution terms required before accepting code for which separate integration grants are intended. |

## Remaining release decisions and limits

- Identify the licensor and permission-request channel in the operative notice.
- Review the commissioned-work and organization-use examples as policy choices;
  their inclusion is not evidence of independent legal validation.
- Use a clear file/material scope and preserve upstream notices with exports.
- Check actual distributed dependencies and material, not just reference licenses.
- Do not describe the draft as legally certified, court-tested or nearly certain.
  Copyright ownership, protectability, mandatory law, assent and cross-border
  enforcement are not established by comparing repositories.
- The owner has chosen to proceed without commissioned legal review. That is not
  a release blocker imposed by this project; remaining uncertainty is documented.

Version 1.0 is now adopted in [LICENSE](../LICENSE), naming AndreasV as Licensor
and GitHub Issues as the permission-request channel. This comparison remains
research rationale, not additional terms or legal certification. Publication is
a separate operation; see [current guidance](licensing.md).
