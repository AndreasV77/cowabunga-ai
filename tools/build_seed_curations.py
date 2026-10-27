"""Reproduce the reviewed 0.3 selections from pinned, locally fetched files.

The lists below are explicit editorial choices, not automatic vocabulary mining.
Definitions are our adaptations; excerpts remain verbatim source lines.
"""
import json
from pathlib import Path

from expanded_vocabulary import extend_vocabulary

ROOT = Path(__file__).resolve().parents[1]
BAND = "73c52379833af51e9d3ce7731746d3bfff3f5266"
COOK = "c8e40ff0b10636a7719cbc88bc5f58443ad19907"
TAGS = "src/skills/suno-lyric-transformer/references/metatag-reference.md"
CORE = "src/skills/suno-style-prompt-builder/references/v6-build-core.md"
SAFETY = "src/skills/suno-style-prompt-builder/references/safety-tables.md"


def document(source, revision, path):
    return (ROOT / "data" / "sources" / source / revision / path).read_text(encoding="utf-8")


def selected_line(source, revision, path, fragment):
    lines = [line for line in document(source, revision, path).splitlines() if fragment in line]
    if len(lines) != 1:
        raise ValueError(f"Expected one line for {fragment!r}, got {len(lines)}")
    return lines[0]


def evidence(label, context, models=(), status="source_claim"):
    return dict(status=status, source_label=label, independently_verified=False,
                model_scope=list(models), test_count=None, context=context)


def entry(source, revision, id, kind, path, fragment, text, meaning, category, ev, field=None):
    return dict(id=id, kind=kind, path=path,
                excerpt=selected_line(source, revision, path, fragment), text=text,
                meaning=meaning, category=category, evidence=ev, input_field=field)


def main():
    band_entries = []
    legacy = evidence("unmarked legacy tag catalogue",
                      "Tag usage is attributed to the publisher. This table does not establish a current-model test or sample size.")
    tags = [
        ("pre-chorus", "| `[Pre-Chorus]` |", "[Pre-Chorus]", "A short transition that builds tension or lift before the chorus."),
        ("post-chorus", "| `[Post-Chorus]` |", "[Post-Chorus]", "A section following the chorus that extends or relaxes its energy."),
        ("bridge", "| `[Bridge]` |", "[Bridge]", "A contrasting section offering new harmonic or melodic material."),
        ("instrumental-break", "| `[Instrumental Break]` |", "[Instrumental Break]", "A mid-song passage intended to foreground instruments rather than sung lyrics."),
        ("drum-break", "| `[Drum Break]` |", "[Drum Break]", "A passage focused on drums, described here as a percussion-only break."),
        ("interlude", "| `[Interlude]` |", "[Interlude]", "A transitional instrumental passage between larger sections."),
    ]
    for id, fragment, text, meaning in tags:
        label = legacy if id not in ("instrumental-break", "drum-break") else evidence(
            "HIGH (publisher grading)", "Publisher grades agreement between sources as HIGH; model/version and test count remain unspecified.")
        band_entries.append(entry("band-manager", BAND, id, "term", TAGS, fragment, text, meaning, "structure", label, "lyrics"))
    v6 = ("v6", "v6-wild", "v6-mini")
    phrases = [
        ("riff-under-verse", "Each instrument gets a job", "the intro riff continues under the verse vocal, palm-muted and lower",
         "Keep the opening guitar motif present underneath the verse singer, with muted articulation and reduced level.", "arrangement", "COMMUNITY + VENDOR"),
        ("vocal-placement", "Place the vocal instead", "vocal in front of the band, close-mic'd and dry, the loudest element; instruments sit behind and below the voice",
         "Specify foreground vocal placement and a supporting instrumental balance.", "production", "VENDOR + COMMUNITY"),
        ("intro-length", "State both edges", "4-bar guitar intro, instrumental only",
         "Request an opening guitar passage of four bars without a sung part; execution is not guaranteed.", "structure", "VENDOR + COMMUNITY"),
        ("heavy-backbeat", "Tempo as feel", "72 BPM feel with a slow heavy backbeat",
         "Pair a tempo target with the felt placement and weight of the drum accents.", "rhythm", "COMMUNITY"),
        ("guitar-vocal-space", "band-side vocal-space clause", "rhythm guitars leave midrange space for the lead vocal",
         "Ask the rhythm-guitar arrangement to leave room for the voice in the midrange.", "arrangement", "LOCAL; no phrase alone lifted a vocal"),
        ("off-home-chord", 'Carry "unresolved" as harmony', "ends off the home chord",
         "Request a harmonically unresolved ending rather than an emotional adjective.", "harmony", "LOCAL, n=1"),
    ]
    for id, fragment, text, meaning, category, label in phrases:
        ev = evidence(label, "Wording and claimed effect belong to the source; no independent listening verification was performed.", v6)
        if id == "off-home-chord":
            ev["test_count"] = 1
        band_entries.append(entry("band-manager", BAND, id, "phrase", CORE, fragment, text, meaning, category, ev, "style"))
    # Keep explicit counter-evidence and legacy scope alongside current instructions.
    band_entries.append(entry("band-manager", BAND, "refrain-legacy-limit", "guidance", TAGS,
        '**Reserve `[Chorus]`', "Not yet re-tested on v6.",
        "The publisher's quiet-refrain workaround for heavy genres predates v6 and is explicitly not re-tested on v6.",
        "structure", evidence("LOCAL-CONFIRMED, 2026-07; not re-tested on v6",
        "Applies to the complete refrain/role/exclude workaround, not to every use of Refrain.")))
    band_entries.append(entry("band-manager", BAND, "line-end-comma-counterevidence", "guidance", TAGS,
        "Mid-line commas make", "leave the writer's line-end commas alone",
        "The publisher reports that line-end comma stuttering did not reproduce in its own v6 takes; preserve the distinction from mid-line commas.",
        "vocals", evidence("ANECDOTAL-controlled + production counter-evidence",
        "No exact production test count is supplied in this passage.", v6), "lyrics"))
    band_entries.append(entry("band-manager", BAND, "room-sound", "phrase", SAFETY,
        "Say the quality, not the venue", "natural room ambience",
        "Describe the acoustic impression of a room without necessarily requesting an audience recording.",
        "production", evidence("LOCAL-CONFIRMED (section heading); model unspecified",
        "The surrounding claim that every live-word form causes crowds is a publisher heuristic, not a general exclusion rule."), "style"))

    cook_entries = []
    groups = [
        ("acoustic-folk", "Fingerpicked guitar, wooden room", "working-hypothesis", [
            ("fingerpicked-guitar", "Fingerpicked guitar", "Guitar played with individual finger-plucked notes rather than only strummed chords.", "instrumentation"),
            ("warm-harmonies", "warm harmonies", "A soft or full-sounding harmonic blend; the source leaves the exact voicing unspecified.", "vocals"),
            ("gentle-mandolin", "gentle mandolin", "A lightly delivered mandolin part supporting the arrangement.", "instrumentation"),
            ("upright-bass", "soft upright bass", "An acoustic upright-bass role with restrained attack or level.", "instrumentation"),
        ]),
        ("english-indie-pop", "Jangly electric guitar, handclaps", "official-informed", [
            ("jangly-guitar", "Jangly electric guitar", "Bright, ringing electric-guitar texture with overlapping resonances.", "instrumentation"),
            ("melodic-bass", "melodic bass", "A bass part with a noticeable melodic contour rather than only repeated roots.", "instrumentation"),
            ("sing-along-chorus", "sing-along chorus", "A chorus designed around an easily repeated vocal hook.", "structure"),
            ("dry-close-vocal", "dry close vocal", "An intimate foreground vocal with little apparent room or reverb.", "production"),
        ]),
        ("electronic-dance", "Punchy four-on-the-floor, sidechain pad", "working-hypothesis", [
            ("four-on-floor", "Punchy four-on-the-floor", "A forceful kick pulse on each quarter-note beat in a four-beat dance groove.", "rhythm"),
            ("sidechain-pad", "sidechain pad", "A sustained synth layer shaped by level reduction triggered from another signal, commonly the kick.", "production"),
            ("wide-sweep", "wide stereo sweep", "A broad motion or sweep across the stereo image.", "production"),
            ("short-vocal-phrase", "concise vocal sample-like phrase", "A brief rhythmic vocal motif used like a sample; this does not imply using third-party recordings.", "vocals"),
        ]),
    ]
    for genre, fragment, label, rows in groups:
        for id, text, meaning, category in rows:
            cook_entries.append(entry("cookbook", COOK, id, "phrase", f"library/genres/{genre}.md", fragment, text, meaning, category,
                evidence(label, "Descriptor selected from this genre page. Explanation is an editorial adaptation; the page's evidence label is not independent verification.", ("v6",),
                         "working_hypothesis" if label == "working-hypothesis" else "source_claim"), "style"))
    for id, fragment, text, meaning in [
        ("breakdown", "| `[Breakdown]` |", "[Breakdown]", "A section with a sparser arrangement in the cookbook's terminology."),
        ("drop", "| `[Drop]` |", "[Drop]", "An electronic-music payoff after a build, where appropriate to the genre."),
    ]:
        cook_entries.append(entry("cookbook", COOK, id, "term", "docs/lyric-and-section-tags.md", fragment, text, meaning, "structure",
            evidence("ungraded conventional tags", "The source presents conventional labels, not a dedicated Suno UI control or a verified syntax specification."), "lyrics"))
    cook_entries.append(entry("cookbook", COOK, "main-theme-example", "phrase", "docs/lyric-and-section-tags.md",
        "[Main Theme - warm cello enters]", "[Main Theme - warm cello enters]",
        "The cookbook's instrumental example requests a cello entrance at the main theme. Retained as an unverified example, despite Band Manager's preference for recognized section labels.",
        "structure", evidence("unverified instrumental example", "This is a source example, not a confirmed recognized tag.", status="unverified_example"), "lyrics"))
    example_path = "library/examples/03-parking-lot-bloom.md"
    example = document("cookbook", COOK, example_path)
    style = example.split("## Style Prompt\n", 1)[1].split("\n\n", 1)[0].strip()
    excludes = example.split("## Exclude Styles\n", 1)[1].split("\n\n", 1)[0].strip()
    lyrics = example.split("```text\n", 1)[1].split("\n```", 1)[0]
    recipe = dict(id="parking-lot-bloom", path=example_path, title="Parking Lot Bloom", family="english-indie-pop",
                  style_prompt=style, structure="[Verse] → [Chorus]", structure_excerpt=lyrics, exclude_styles=excludes,
                  evidence=evidence("official-informed", "Source frontmatter: verified: false. Section sequence is normalized from the example lyrics; exclude wording is preserved, not endorsed.", ("v6",), "unverified_example"))
    extend_vocabulary(band_entries, cook_entries, entry, evidence, BAND, COOK, TAGS, CORE)
    target = ROOT / "curations"
    target.mkdir(exist_ok=True)
    for source, revision, entries, recipes in [("band-manager", BAND, band_entries, []), ("cookbook", COOK, cook_entries, [recipe])]:
        payload = dict(source_id=source, revision=revision,
                       changes="Selected source excerpts; added English explanatory adaptations, categories and explicit evidence limits; normalized recipe section order. No independent musical-effect verification.",
                       entries=entries, recipes=recipes)
        (target / f"{source}.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"{source}: {len(entries)} entries, {len(recipes)} recipes")


if __name__ == "__main__":
    main()
