"""Reproduce the reviewed, non-equivalence concept links for release 0.5."""
import hashlib
from pathlib import Path

from prompt_reference.concepts import ConceptCatalog
from prompt_reference.reviews import ReviewSet

ROOT = Path(__file__).resolve().parents[1]


def concept(id, label, aliases, description, rows, checks=()):
    return dict(id=id, label=label, aliases=aliases, description=description,
                links=[dict(record_id=id, relation=relation, note=note) for id, relation, note in rows],
                crosscheck_ids=list(checks))


def main():
    concepts = [
        concept("vocal-placement", "Vocal placement and intimacy", ["close singer", "foreground voice", "intimate vocal"],
            "Choose apparent distance and foreground/background balance independently of voice register or texture.", [
                ("cookbook:dry-close-vocal", "wording", "A direct close/dry vocal description."),
                ("lil-synn:foreground-depth", "dimension", "Adds depth contrast between foreground and ambience; not a synonym for dry."),
                ("band-manager:vocal-placement", "alternative", "Mixed-source band/voice balance wording; not independently verified."),
                ("band-manager:guitar-vocal-space", "alternative", "Leave instrumental midrange room rather than merely increasing vocal adjectives."),
            ]),
        concept("vocal-phrasing", "Vocal phrasing and syllable density", ["melisma", "syllabic", "long notes", "short phrases"],
            "Keep phrase length, note-to-syllable relationship and ornamentation separate instead of treating them as equivalent.", [
                ("lil-synn:sustained-phrases", "wording", "Long phrase shape; does not by itself specify ornamentation."),
                ("lil-synn:clipped-phrases", "alternative", "Short phrase endings, offered as an alternative to sustained phrasing."),
                ("lil-synn:melismatic", "dimension", "Multiple pitches on one syllable; not the same as simply singing a long note."),
                ("lil-synn:syllabic", "alternative", "One-note-per-syllable tendency rather than melismatic ornamentation."),
                ("cookbook:restrained-ornament", "dimension", "Limits embellishment without forcing all phrases to be short."),
                ("band-manager:legato", "dimension", "Articulation across notes, not a synonym for sustained or melismatic."),
            ]),
        concept("vocal-timing", "Vocal timing and conversational delivery", ["laid back singer", "behind beat", "speech like"],
            "Separate rhythmic placement from speech-like character and intelligibility.", [
                ("lil-synn:behind-beat", "wording", "Timing relative to the pulse."),
                ("lil-synn:forward-rhythm", "alternative", "A more pushing rhythmic intention."),
                ("cookbook:conversational-vocal", "dimension", "Delivery character; may coexist with different timing placements."),
                ("cookbook:clear-consonants", "dimension", "Intelligibility is an additional choice, not a timing substitute."),
            ], ["vocal-facets"]),
        concept("vocal-texture", "Vocal texture", ["grainy voice", "husky singer", "rough voice"],
            "Describe timbre separately from register, emotional intensity and microphone distance.", [
                ("lil-synn:grainy", "wording", "A grain-like roughness description."),
                ("lil-synn:husky", "alternative", "A breath-rough or darker color; not declared equivalent to grainy."),
                ("band-manager:raspy", "alternative", "Legacy catalogue term with related musical meaning but uncertain current tag reliability."),
                ("band-manager:breathy", "dimension", "Airflow component rather than necessarily roughness."),
            ]),
        concept("verse-chorus-contrast", "Verse-to-chorus arrangement contrast", ["chorus lift", "sparse verse", "bigger chorus"],
            "Assign different instrumental and vocal jobs to sections instead of applying every characteristic globally.", [
                ("lil-synn:sparse-verse", "wording", "A deliberately sparse verse scene."),
                ("lil-synn:expanded-chorus", "wording", "A separate expanded chorus scene; not intended to describe the verse simultaneously."),
                ("cookbook:verse-chorus-contrast", "dimension", "The overall contrast goal."),
                ("cookbook:wider-group-vocals", "alternative", "A chorus expansion for songs that want multiple voices; unsuitable as an automatic solo-vocal default."),
                ("cookbook:break-the-silence", "example", "An unverified complete V6 rock example, not proof of the smaller wording effects."),
            ]),
        concept("kick-bass-space", "Kick and bass relationship", ["low end separation", "ducking", "bass groove"],
            "Choose timing coordination, level interaction and spatial bass behavior as distinct dimensions.", [
                ("lil-synn:kick-ducking", "wording", "A level interaction triggered by the kick."),
                ("cookbook:locked-bass", "dimension", "Rhythmic coordination; not equivalent to sidechain processing."),
                ("cookbook:bass-synth", "dimension", "The sound-producing role, independent of its kick interaction."),
                ("lil-synn:centered-bass", "dimension", "A spatial intention; does not guarantee a mono-compatibility measurement."),
            ]),
        concept("stereo-depth", "Stereo width and apparent depth", ["wide mix", "near far", "soundstage"],
            "Distinguish left-right spread, near-far distance and low-end placement.", [
                ("cookbook:wide-sweep", "wording", "Stereo movement or width."),
                ("lil-synn:foreground-depth", "dimension", "Foreground/background distance, not width alone."),
                ("lil-synn:centered-bass", "dimension", "Keep the low-end spatial role separate from wide upper elements."),
            ]),
        concept("acoustic-drums", "Acoustic drum character", ["live drums", "room drums", "natural percussion"],
            "Choose the intended performance, density and room impression without automatically importing a crowd-noise prohibition.", [
                ("cookbook:propulsive-drums", "wording", "The V6 recipe deliberately uses the word live for driving drums."),
                ("cookbook:light-percussion", "alternative", "A restrained percussion role rather than necessarily a driving kit."),
                ("band-manager:brushed-drums", "alternative", "A specific softer articulation from a mixed-model catalogue."),
                ("band-manager:room-sound", "alternative", "An alternate room-description phrase, with the source's trigger concern retained."),
            ], ["live-drums"]),
        concept("hook-focus", "Hook focus", ["repeatable chorus", "memorable phrase", "sing along"],
            "Choose a clear repeated idea and enough space for it; phrase length is a related choice rather than a guaranteed hook recipe.", [
                ("cookbook:repeated-melodic-phrase", "wording", "A repeated melodic idea."),
                ("cookbook:sing-along-chorus", "dimension", "A participation-oriented chorus goal."),
                ("cookbook:pre-drop-phrase", "alternative", "A short identifying idea placed before an electronic payoff."),
                ("lil-synn:clipped-phrases", "dimension", "A phrase-shape option that can leave space; it is not inherently more memorable."),
            ]),
        concept("positive-replacement", "Avoidance and positive replacement", ["negative prompt", "exclude styles", "avoid instruments"],
            "Keep desired replacements and source exclusions distinct; no automatic negation rule is assumed.", [
                ("lil-synn:positive-replacement", "wording", "A method for describing the replacement role, not a literal style command."),
                ("lil-synn:avoidance-experimental", "dimension", "The source's explicit uncertainty about avoidance syntax."),
                ("cookbook:break-the-silence", "example", "A recipe with separate source exclusions; those exclusions remain separate from its style text."),
            ], ["exclusions"]),
        concept("model-routing", "Exploration and controlled refinement", ["wild model", "discovery", "bridge idea"],
            "Use model roles to structure an experiment without promising identical reconstruction across models.", [
                ("lil-synn:wild-discovery", "wording", "A model-role workflow, not an audible style descriptor."),
                ("cookbook:cassette-highway", "example", "An unverified v6-wild bridge exercise followed by v6 refinement."),
            ], ["model-routing"]),
        concept("acoustic-room", "Acoustic room impression", ["room sound", "breath", "wooden room"],
            "Describe environmental texture and distance separately from a literal live-audience recording.", [
                ("cookbook:room-breath", "wording", "Retain breath and room cues."),
                ("cookbook:wooden-room", "alternative", "A woody room-color association, not a measured acoustic property."),
                ("lil-synn:foreground-depth", "dimension", "A separate near-far arrangement of direct sound and ambience."),
                ("band-manager:room-sound", "alternative", "Mixed-source room wording with explicit limits on its surrounding trigger claim."),
            ], ["live-drums"]),
    ]
    review_bytes = (ROOT / "reviews/v6-crosschecks.json").read_bytes()
    reviews = ReviewSet.model_validate_json(review_bytes)
    catalog = ConceptCatalog.model_validate(dict(version="0.5", reviewed_on="2026-10-26",
        snapshots=reviews.snapshots, reviews_sha256=hashlib.sha256(review_bytes).hexdigest(), concepts=concepts))
    path = ROOT / "curations/concepts.json"
    path.write_text(catalog.model_dump_json(indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {len(catalog.concepts)} concepts to {path}")


if __name__ == "__main__":
    main()
