# Selected-source gap review — 2026-10-27

**FND-01, FND-02 and FND-04 remain OPEN.** This pass distinguishes missing
selections from missing vocabulary, authored relationships and uncertain effects.
It proposes selections; it does not change curations or activate a source snapshot.

This is the pre-expansion review record. The later
[nine-entry expansion](foundation-expansion.md) implements the selected candidates
and documents validation and activation; the original findings below remain history.

## Scope and method

Validated all four pinned inputs through the production adapters before reviewing
their content: MUSAI four files, Band Manager six, Cookbook eleven and LIL SYNN
four. Searched those 25 admitted files for task vocabulary, read relevant passages
with surrounding caveats and compared them to the normalized selected entries.
MUSAI recipes are already all imported; Markdown mentions are not extra recipes.

This is not a review of every file in the upstream repositories or of the current
web. A failed literal phrase search does not establish semantic absence. No
additional source, private notebook text, user draft or listening report was
imported. Working databases and existing snapshots were not changed.

## Task-by-task disposition

| Task | Finding in the pinned files | Decision / remaining work |
|---|---|---|
| Pulse and subdivision | Band Manager's core and research notes describe feel over one pulse, with explicit V6 reliability limits. LIL SYNN lists half-time in its V6 drum vocabulary. | Selection gap for V6-native vocabulary and scoped guidance. Neither passage establishes slower vocal phrasing over independently fast drums. `gallop/galloping` remains a separate retrieval loss. |
| Instrument relationships | Existing locked-bass example does not identify a guitar or kick target. Exact bass-following-guitar phrases were not found by the narrow scan. | Keep the task partial. General coordination vocabulary is present; the requested relationship is an authored arrangement instruction, not evidence that a new source is necessarily required. Inspect broader phrasing before claiming source absence. |
| Ensemble and section scope | Band Manager explicitly lists Choir, Gospel Choir, Chant, Harmonies and Stacked Harmonies; the selection omits some of them. LIL SYNN includes call-and-response in its V6 vocabulary. | Clear selection gaps. Add distinct ensemble/function candidates rather than an equivalence group. Layered/stacked effect differences remain untested. |
| Change one layer | Band Manager gives instrument jobs per section and a continuing-riff example, already partly represented by `band-manager:riff-under-verse`. Its positive instrument-filling section adds a general method. | Existing reference mapping can be improved. None of these inspected passages specifies the exact one-bar vocal-only gap while kick and bass continue unchanged. No timing guarantee or need to copy the private example. |
| Rough clear vocal | Available definitions already separate texture, delivery, articulation and placement. Band Manager additionally lists vocal styles, with some oversimplified register descriptions. | Primarily semantic review and composition work. More synonyms alone do not establish the desired audible outcome. Do not import loose register equations as definitions. |
| Cross-genre drive | MUSAI and Band Manager already supply breakbeat vocabulary. LIL SYNN supplies several rhythm descriptors, but these inspected passages do not demonstrate genre-preserving breakbeat substitution. | Vocabulary is present; transfer/effect remains an open listening question. No full recipe transplant or automatic genre-equivalence rule. |
| Exclusions | Cookbook directly recommends short, specific exclusions and using the Exclude Styles field when available. Band Manager has field-specific guidance plus unresolved bracket-context exceptions. | Clear selection gap, plus a semantic disagreement to retain. `exclude` still misses the related selected avoidance entry. Adding field guidance would improve coverage but would not by itself fix that entry's retrieval. |
| Priority and conflicts | LIL SYNN's hierarchy section explicitly calls itself a working production model; scoped verse/chorus examples are already selected. | No newly discovered official parser hierarchy. Prioritization is an authored workflow, and incompatible mandatory requests need clarification. |
| Intimate acoustic | Cookbook's prompt anatomy includes sparse instrumentation, timed entrances and a final-chorus-only string layer. | Additional arrangement example is available, but the task's small lift still requires an explicit choice of dimension and scale. Avoid mistaking an example for a universal recipe. |
| Harmonic ending | Selected off-home-chord guidance already captures the relevant ending distinction. Cookbook asks for key/harmonic color if known; LIL SYNN mentions tonal/modal character. | Broad labels exist, but the inspected passages do not supply a precise unresolved-ending progression. Strict-core harmony vocabulary and deeper theory/source coverage remain unresolved; do not count a category heading as adequate vocabulary. |
| Overtone tradition | The narrow scan finds Mongolian/khoomei vocabulary in MUSAI, whose recipes are all imported; it finds no additional exact terminology in the other admitted files. | No new overtone candidate from this pass. Keep model-unspecified supplementary evidence and the tradition boundary. This is not an exhaustive claim about all upstream files or all spellings. |

## Concrete selection candidates

These are reviewed **candidates**, not new source records. Source licenses remain
MIT for Band Manager, CC BY 4.0 for Cookbook and CC0 for LIL SYNN. Existing
`THIRD_PARTY_NOTICES.md` and pinned source metadata retain attribution and terms.

| Candidate | Source passage | Intended contribution and boundary |
|---|---|---|
| V6 call-and-response vocabulary | [LIL SYNN README, lines 1050–1055](https://github.com/LILSYNNOFFICIAL/LIL-SYNN-s-Complete-Suno-V6-Guide/blob/6b805bf77a350e7fba00bfd2451273327482827c/README.md#L1050-L1055) | V6-native vocabulary candidate. The list establishes inclusion in the guide, not a tested execution rate. Field choice/definition must remain explicitly editorial. |
| V6 half-time vocabulary | [LIL SYNN README, lines 1058–1062](https://github.com/LILSYNNOFFICIAL/LIL-SYNN-s-Complete-Suno-V6-Guide/blob/6b805bf77a350e7fba00bfd2451273327482827c/README.md#L1058-L1062) | Rhythm term; not a command to halve every layer or a numeric tempo control. |
| Choir ensemble | [Band Manager metatag reference, lines 208–222](https://github.com/zarlor/suno-band-manager/blob/73c52379833af51e9d3ce7731746d3bfff3f5266/src/skills/suno-lyric-transformer/references/metatag-reference.md#L208-L222) | Choir/Gospel Choir vocabulary, distinguished from chant and generic harmonies. Mixed source; do not infer V6-targeted record scope from a bare table. |
| Specific short exclusions / field placement | [Cookbook prompt anatomy, lines 74–84](https://github.com/MJorgin/suno-v6-cookbook/blob/c8e40ff0b10636a7719cbc88bc5f58443ad19907/docs/prompt-anatomy.md#L74-L84) | Guidance for the exclusion workflow. Keep the field qualifier and do not imply field/inline equivalence or reliable suppression. |
| Feel contrast over one pulse | [Band Manager build core, line 20](https://github.com/zarlor/suno-band-manager/blob/73c52379833af51e9d3ce7731746d3bfff3f5266/src/skills/suno-style-prompt-builder/references/v6-build-core.md#L20) and [research notes, lines 86–91](https://github.com/zarlor/suno-band-manager/blob/73c52379833af51e9d3ce7731746d3bfff3f5266/src/skills/suno-style-prompt-builder/references/research-sources.md#L86-L91) | Guidance must retain mixed pre-V6/community/local evidence and possible-but-unreliable feel switches. Not a proven global tempo law. |
| Positive section instrument filling | [Band Manager metatag reference, lines 542–562](https://github.com/zarlor/suno-band-manager/blob/73c52379833af51e9d3ce7731746d3bfff3f5266/src/skills/suno-lyric-transformer/references/metatag-reference.md#L542-L562) | Positive role specification as a method candidate. Do not promote the attention/crowding explanation into established model internals. Preserve the adjacent negation caveat. |
| Acoustic section entrances | [Cookbook prompt anatomy, lines 16–31](https://github.com/MJorgin/suno-v6-cookbook/blob/c8e40ff0b10636a7719cbc88bc5f58443ad19907/docs/prompt-anatomy.md#L16-L31) | Source example of section-bound instrument entrances; not evidence that a requested entrance reliably renders. |

The V6-native vocabulary candidates could address parts of empty core queries
without adding another publisher. They would not promote the existing mixed-source
entries or change their historical evidence. Selection/import review is still
required, including model/field interpretation and snapshot/catalog updates.

## Claims that must not be imported as blanket rules

1. **Tempo:** the metatag file states categorically that tempo never changes and
   BPM tags have zero effect (lines 878–894). The same source's V6 research notes
   explicitly describe confounded observations, a clean test with a missed feel
   change, possible-but-unreliable switches and BPM as soft conditioning. The
   absolute wording is broader than the attached evidence. Preserve the narrower
   guidance and attach the tension; do not certify a global impossibility.
2. **Negation:** safety tables state that inline negatives act as inclusion. The
   metatag reference distinguishes standalone brackets from an unresolved compound
   pipe-tag exception (lines 544–554); LIL SYNN supplies experimental avoidance
   wording, and Cookbook includes an Avoid line while recommending the separate
   field. Context and evidence differ. No universal negative parser rule is justified
   by simply combining these passages.
3. **Ensembles:** Band Manager's claim that choir/gang/stacked arrangements differ
   does not establish a measured distinction for every genre or the effect of
   layered versus stacked. Its label HIGH is the publisher's confidence label.
4. **Register:** the metatag table groups falsetto/head voice and describes chest
   voice as a lower register. Existing normalized entries intentionally separate
   registration from pitch range. Importing the raw shorthand as a definition
   would undo that distinction.

These are editorial scope tensions, not newly performed audio experiments or a
declaration that the sources are unusable. Useful vocabulary remains reusable
with careful definitions and evidence limits.

## Next disposition

Prepare a small candidate curation update for the specific vocabulary/guidance
above with exact excerpts, conservative record scope and linked tensions. Preserve
the current snapshots and activate nothing silently. Resolve query losses
separately; continue the broader source-candidate and 150-entry editorial reviews.
No Gate 1 task closes merely because more possible excerpts were found.
