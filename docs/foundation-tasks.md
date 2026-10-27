# Musical task and retrieval audit — first pass

Reviewed 2026-10-27. **FND-01 and FND-04 remain OPEN; FND-02 is closed for the current 36-probe scope.** See [the search/field review](search-and-field-review.md).

The owner's private notebook suggested practical research questions. The public
briefs in `reviews/foundation-tasks.json` are newly authored English examples;
they contain no private lyrics, historical prompts, third-party prompt examples
or listening reports. Private notebook material is not admitted reference data.
Selected upstream records retain their own licenses and pinned provenance.

## What this checks

Eleven briefs cover all eight reference categories. Each has explicit source
record IDs and their limited contribution, missing information, an evidence
boundary, a future assistant criterion and a separate listening question.

Thirty-six retrieval probes check required and forbidden records, two spellings of
Mongolian overtone terminology, `sax/saxophone`, core versus supplementary scope,
an unknown query, two corrected retrieval losses and their literal baseline controls. Expected IDs are evaluated in
the complete pinned corpus, not against the owner's working database. Every
referenced record must exist in the declared active snapshots.

The brief is not sent to an assistant and is not used as a semantic search query.
These probes test vocabulary access; they do not demonstrate context-sensitive
selection, successful composition or generation effects. Future assistant and
listening criteria are specifications, not passed tests.

## Coverage matrix

All rows are partial. A linked record supports the stated dimension, not the
whole brief. Full IDs and missing information are in the JSON task set.

| Task ID | Required dimensions | Representative current records | Remaining gap |
|---|---|---|---|
| pulse-and-subdivision | Rhythm, vocals, arrangement | `band-manager:half-time`, `cookbook:four-on-floor`, MUSAI Power Metal | Independent vocal pulse and drum subdivision; gallop recall |
| instrument-relationships | Instrumentation, rhythm, arrangement | `cookbook:locked-bass`, `band-manager:palm-muted` | Exact guitar-to-kick / bass-to-guitar relationships |
| ensemble-and-section-scope | Vocals, harmony, arrangement, structure | `band-manager:choir`, `lil-synn:call-response`, `cookbook:wider-group-vocals` | Modifier effects, ensemble realization and independent section scope remain untested |
| change-one-layer | Vocals, rhythm, arrangement, structure | `cookbook:four-on-floor`, `cookbook:locked-bass`, `band-manager:instrumental-break` | Vocal-only gap with invariant rhythm section; timing reliability |
| rough-clear-vocal | Vocals, production | `lil-synn:grainy`, `band-manager:raspy`, `cookbook:clear-consonants` | Desired timbre/delivery outcome without shouting |
| cross-genre-drive | Rhythm, instrumentation, arrangement | `band-manager:breakbeat`, `band-manager:trap-hihats`, MUSAI Breakbeat | Continuous movement without unwanted genre drift |
| exclusions-and-positive-roles | Controls, vocals, production | `lil-synn:avoidance-experimental`, `lil-synn:positive-replacement` | Exclusion-category/field behavior and query wording |
| priority-and-conflicts | Controls, arrangement, structure | `lil-synn:working-hierarchy`, scoped verse/chorus examples, `lil-synn:test-variable` | No established parser hierarchy; unresolved user priorities need clarification |
| intimate-acoustic | Instrumentation, vocals, production, structure | `cookbook:fingerpicked-guitar`, `cookbook:dry-close-vocal`, `cookbook:verse-chorus-contrast` | Choosing the dimension of a deliberately small lift |
| harmonic-ending | Harmony, structure | `band-manager:off-home-chord`, `band-manager:key-change`, `band-manager:hard-stop` | Precise progression/voicing and strict-core harmony coverage |
| overtone-tradition | Vocals, instrumentation, arrangement | MUSAI Mongolian overtone recipe, `band-manager:palm-muted`, `cookbook:sing-along-chorus` | Strict-core overtone reference and evidence for simultaneous role fusion |

Current data establishes gaps in the **admitted selection** only. Whether missing
material exists elsewhere in an already admitted repository, in a new licensable
source or nowhere suitable remains to be checked. Do not automatically fetch a
new collection or label any of these an exhaustive upstream absence. The broader
candidate-source decisions required by FND-01 remain pending.

## Retrieval findings and dispositions

| Finding | Disposition |
|---|---|
| `gallop` previously missed the Power Metal recipe | Resolved by the explicit gallop/galloping expansion; the unexpanded baseline preserves the old miss. |
| `exclude` previously missed the experimental avoidance entry | Resolved by a directional discovery expansion; the unexpanded baseline remains and field equivalence is not asserted. |
| Call-and-response now has a V6-native core hit; the Band Manager entry remains supplementary | Explicit reviewed selection expansion, without upgrading the old entry's source/model scope. |
| Breakbeat, Mongolian technique and unresolved harmony have empty strict-core queries in this set | Explicit scope boundaries, not missing full-corpus vocabulary. Some V6-targeted Band Manager material remains outside core because source orientation is mixed. |
| `khoomei` and `khöömei` both find the Mongolian recipe | Supported for this pinned record; not proof of general transliteration support. |
| `sax` and `saxophone` both find the tenor-sax entry | Text and explanation cover both forms; not a synonym engine. |
| Tibetan material remains searchable but is excluded from the specific Mongolian query expectations | Tradition boundary, not a global ban on Tibetan references. |
| Unknown query returns no references | Supported negative control; no invented fallback. |

The evaluator reports any open losses even when observations match. The current two losses have explicit fixes and literal baseline controls; the linked review records scoped FND-02 closure.
If a missing record becomes findable, the observation fails until its disposition
is explicitly reviewed and updated. Green tests preserve a known finding; they
do not accept the defect or silently close FND-02.

Initial validation on 2026-10-27: the strict command passed **137 tests, zero skips**,
including all 31 probes, complete source reconstruction and negative tests for
stale pins, missing records and changed required/forbidden hits. Its ignored
report is `data/audits/foundation-tasks-20261027-a.json`; the existing
Starlette/httpx deprecation warning remains. The eight-entry semantic review
below was a text review, not one of those automated tests.

## Initial semantic review — eight entries, not the whole corpus

Compared the normalized meaning/field/model evidence against pinned passages;
for Cookbook examples and the LIL SYNN hierarchy/avoidance sections, also checked
surrounding context. No curation edits or source activations were made.

| Record | Review decision / boundary |
|---|---|
| `band-manager:half-time` | Lyrics-tag vocabulary with unspecified record model basis. The normalized musical explanation adds specificity to a terse source description; do not treat it as evidence of independent per-layer control. |
| `band-manager:stacked-harmonies` | Source describes dense layered harmonies. Its HIGH label does not prove equivalence to choir, gang-shouted or a tested layered/stacked difference. |
| `band-manager:off-home-chord` | Style wording explicitly targets harmonic non-resolution. Source reports a local single-case example; neither emotional mood nor global harmonic success is established. |
| `cookbook:locked-bass` | Style phrase inside a V6 working hypothesis, `verified: false`. It does not specify whether bass follows guitar or kick. |
| `cookbook:wider-group-vocals` | Same unverified example; chorus scope is explicit. Ensemble expansion is not evidence of which exact singers or voicings appear. |
| `lil-synn:grainy` | Vocal-color vocabulary in a descriptor list; definition is an editorial gloss. It does not specify register, loudness or verified audible outcome. |
| `lil-synn:working-hierarchy` | Context explicitly denies an official deterministic hierarchy. No direct input field; retain as a heuristic, not composable style wording or parser fact. |
| `lil-synn:avoidance-experimental` | Source calls exclusion wording experimental. Style-field candidate, not proof that a separate Exclude Styles field behaves identically. |

This limited semantic review identifies valid interpretation boundaries. It does
not complete the full entry review, representative recipe review or FND-04. It
does not turn existing community claims into independently verified techniques.

## How to run and continue

Run [strict foundation validation](foundation-validation.md). Its reconstruction
report includes the task audit: hits, core boundaries, explicit retrieval losses
and coverage gaps. Missing/mismatched source pins or changed retrieval observations
fail validation. The optional developer tests are in `tests/test_foundation_tasks.py`.

Next: inspect full admitted-source material for the declared selection gaps,
review candidate-source decisions, resolve the two retrieval losses with negative
controls, and continue item-level semantic review. Retain generation questions
separately; running this software audit does not authorize or require paid Suno
experiments, an AI adapter or UI work.

The [first selected-source gap review](foundation-gap-review.md) distinguishes
selection gaps from unresolved composition/effect questions. Its 25-file scope
is narrower than a review of every upstream repository file. The subsequent
[nine-entry expansion](foundation-expansion.md) passed **143 tests, zero skips**;
both retrieval losses were subsequently resolved in the 153-test search/field review. Current counts are 159 entries and 567
recipes, including 68 strict-core entries and 3 strict-core recipes.
