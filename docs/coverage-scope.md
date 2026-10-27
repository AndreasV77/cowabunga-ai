# Resource coverage and source decisions — 2026-10-27

**FND-01 and FND-04 remain OPEN.** This review defines a bounded starting scope
and identifies actual missing information before adding more collections.

The owner also wants music theory to be useful beyond the first prompting
workflow. Treat it as a reusable, provider-independent reference area with
explicit interfaces, not as Suno-specific lore or a one-off challenge glossary.
Start with the gaps below and extend it by concrete needs. A theory definition
does not establish how reliably a music generator follows the term.

## Three information roles

1. **General musical meaning:** instrument/technique names, meter, chords,
   harmonic function, texture and arrangement relationships. A stable theory
   source can be useful even if it predates a current model.
2. **Platform application:** which field a direction belongs in, model/version,
   controls, source examples and limitations. Current-model provenance matters.
3. **Authored musical choices:** deciding how bass follows guitar, which layer
   keeps playing or how large a chorus lift should be. These require explicit
   composition reasoning; not every possible sentence needs a database recipe.

Keep roles and evidence separate in context/export. Do not discard general music
knowledge for lacking a V6 label or turn it into V6 execution evidence.

## Coverage matrix

`reviews/coverage-scope.json` links **24 information requirements** to real source
records and the eleven task briefs. It records 15 source decisions and four
additional synthetic holdout briefs. Current dispositions are:

| Disposition | Count | Meaning |
|---|---:|---|
| References available | 12 | Linked material contributes the specified information; full editorial review remains pending |
| Historical relationship gap | 2 | Genre lineage and regional evolution need sourced relationships, not more flat labels |
| Definition gap | 6 | A coherent reference definition is still missing from the admitted selection |
| Authored relationship | 3 | Vocabulary exists in part; the arrangement relationship must be composed explicitly |
| Effect question | 1 | Listening/generation question, not a missing word to solve by importing more tags |

These counts are **not a completeness percentage or a musical success score**.
Every requirement retains its next action and evidence limit.

### Actual definition gaps

| Requirement | Needed information | Current limitation |
|---|---|---|
| Meter and grouping | Simple/compound meter; 6/8 versus 3/4; subdivision versus swing | Triplet vocabulary and one 6/8 recipe do not supply a meter explanation |
| Chord quality | Major/minor triads, suspended chords and extensions | No selected standalone major/minor/triad definition; recipe mentions are insufficient |
| Tonal/modal color | Key versus scale/mode; major/minor and Dorian | Key-change guidance does not define these distinctions |
| Harmonic function | Tonic, dominant, cadence and unresolved endings | Off-home-chord wording is useful but not a functional-harmony reference |
| Harmonic pedal | A sustained/repeated note beneath changing harmonies | An audio-effect pedal word match is not the intended definition |
| Overtone technique | Drone, focused overtone and technique/tradition distinctions | The model-unspecified Mongolian recipe supplies terms, not a specialist explanation |

The authored relationships are instrument dependencies, a changed layer over
unchanged layers, and a deliberately small contrast. Their absence as complete
stored phrases is not automatically a reason to buy or import another database.

## Holdouts and lexical observations

The original three English briefs test whether the matrix merely fits the
existing task set: suspended harmony over a tonic pedal, compound-meter acoustic
lilt, and cello/lead counterline role exchange. A fourth now probes genre ancestry, influence and classification. They are coverage probes, not
new assistant or audio tests.

On the pinned corpus, literal searches returned no entry definitions for major,
minor, triad or Dorian. Suspended, pedal and cadence occur in recipes, but those
occurrences do not establish coherent definitions. `compound` finds the
negation-context entry about compound tags, not a meter definition. Cello and
countermelody have useful selected references. These observations concern this
index/selection, not universal absence from all upstream material.

The closed FND-02 scope remains its 36 lexical probes. These holdouts reviewed
additional information needs; they did not reveal another defect in the two
reviewed query expansions. Future source/selection changes must review and
extend retrieval expectations where appropriate.

## Source decisions

The registry records exact Git revisions where available, checked date, evidence
URLs, observed licensing and the reason for each decision. No candidate is
installed or imported in this pass.

| Source | Decision and evidence |
|---|---|
| Band Manager, Cookbook, LIL SYNN, MUSAI | Retain all four current pinned collections in their existing roles. Two V6-native publishers, mixed guidance and model-unspecified recipe vocabulary remain distinct. |
| [Awesome Suno](https://github.com/Zizwar/Awesome-Suno/blob/afd51fe0c161dcd6c150f5fa5e33d586f5f202fe/README.md) | Discovery only. Rechecked at the 2026-10-22 revision; predominantly tools/APIs. Listing a project does not establish reuse rights or verification. No detected repository license was treated as permission to copy the list. |
| [stayen/suno-reference](https://github.com/stayen/suno-reference/blob/4fd18c1c91fc36b6904880713a3e4111c94f5673/README.md) | Defer. MIT license read; README names v5 and a November 2025 tag update. Potential later vocabulary deduplication, not a V6-native solution to the current theory gaps. |
| [suno-songtags](https://github.com/develephant/suno-songtags/blob/d5455258b044abe863004554d694b6e9f97275e2/README.md) | Defer. MIT license read; latest observed commit July 2025, minimal README without V6 evidence. Full contents were not audited; no unique gap-closing contribution established in this pass. |
| [Korean lyrics skill](https://github.com/previtlab/suno-lyrics-skill/blob/1339571d4ff0d1cc6399b824f39b2d116dbea1cd/README.md) | Outside current English-first reference scope. CC BY 4.0 file/attribution read; current lyric-workflow ideas may be revisited after the foundation gate. No skill installed. |
| [Suno GPT](https://sunogpt.ai/) | Research only. Public landing page claims V6 and producer experience but did not expose a reusable corpus or auditable database-building method in the material read. This is not a conclusion about every interview, private resource or page. No example output imported. |
| [Tonal](https://github.com/tonaljs/tonal/tree/e555422aef910daa87cb924028f71f0a013f3ed7) | Shortlist for structured general-music information. [MIT file](https://github.com/tonaljs/tonal/blob/e555422aef910daa87cb924028f71f0a013f3ed7/docs/LICENSE) exists under docs despite absent GitHub root-license detection. Chord/scale tables cite Wikibooks/Wikipedia origins; follow those before wholesale copying. No runtime dependency is needed for this review. |
| [Open Music Theory](https://viva.pressbooks.pub/openmusictheory/front-matter/introduction/) | Shortlist for explanatory fundamentals/harmony/modes. Indexed primary-page text states CC BY-SA 4.0 except where noted; direct home/introduction fetch returned 403. Capture selected pages and review attribution/material exceptions and ShareAlike obligations before adapting content. Do not infer a global code-license change. |
| [Bergevin et al., eLife 2020](https://elifesciences.org/articles/50476) | Shortlist for bounded vocal acoustics. Primary acoustic/MRI research, article CC BY 4.0 confirmed via its copyright link. It studies Tuvan singing; it cannot establish Mongolian cultural terminology or Suno behavior. Its age does not make it pre-V6 prompting evidence: it is a general mechanism source. |

Open Music Theory's [fundamentals](https://viva.pressbooks.pub/openmusictheory/part/fundamentals/)
and [modal schemas](https://viva.pressbooks.pub/openmusictheory/chapter/modal-schemas/)
are relevant starting pages. The applicable [CC BY-SA 4.0 terms](https://creativecommons.org/licenses/by-sa/4.0/)
must remain attached to any admitted adaptations; linked figures/media may have
their own terms. Only source-selection observations are recorded here.

## Technical consequence and next work

The present importers assume repository revisions and GitHub-style passage URLs;
`Source.revision` currently requires 40 hexadecimal characters. A DOI or changing
textbook page is not a Git commit. Before admitting a page/journal source, define
honest versioned capture and locator metadata; do not fabricate a commit SHA or
point it at an unrelated repository. This is a foundation-contract question,
not an AI-provider feature.

Next deliverable: a small, reusable general-music definition set for the six
gaps, with actual selected passages, checked rights, attribution, clear source
roles and a suitable importer/locator. Assess Tonal structures and textbook
explanations separately; one does not automatically replace the other. The vocal
mechanism pilot must preserve Tuvan/Mongolian scope distinctions. No bulk scrape
or runtime theory engine is required.

FND-01 closes only after required gaps have adequate admitted material or an
explicitly justified scope limitation, source decisions are resolved at that
level and the holdouts no longer conceal material gaps. FND-04 still requires
full item-level review. Neither gate closes because this matrix is complete.

## Validation

Strict foundation validation now includes `coverage_audit`. It rejects stale
source pins, missing record/task links, unadmitted sources marked retained and a
recipe passed off as a reference definition. Coverage stays explicitly open in
the output, even when mechanical checks pass.

**160 tests passed, zero skipped**. The final twelve-source decision registry was
also evaluated against the isolated pinned corpus after the final specialist
candidate was added. Reports remain ignored under `data/audits/`. The existing
Starlette/httpx deprecation warning remains. No source activation, working-data
change, new runtime dependency, UI work or generation experiment occurred.

## Genre-history extension

The owner additionally requires one or two sources with genre roots and later branches.
[The genre-history review](genre-history-sources.md) records two historical-information
gaps, a fourth holdout and candidate decisions. Musicmap is research-only; English
Wikipedia/Wikidata is a shortlisted, related source family. They are not admitted
data and do not remove the six definition gaps above. The earlier twelve-source
validation description records the first pass before this extension.

The extended fifteen-source decision registry and four holdouts passed the strict
validation run with **160 tests, zero skips**; local report:
`data/audits/genre-coverage-20261027.json`. The source corpus and working database
remain unchanged.
