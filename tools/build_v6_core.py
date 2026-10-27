"""Build the reviewed V6 core from frozen 0.3 selections and pinned sources."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BAND = "73c52379833af51e9d3ce7731746d3bfff3f5266"
COOK = "c8e40ff0b10636a7719cbc88bc5f58443ad19907"
LIL = "6b805bf77a350e7fba00bfd2451273327482827c"
ADD = "SUNO-V6-ULTIMATE-CONTROL-AND-PRODUCTION-ADDENDUM-2026.md"
GAP = "SUNO-V6-GAP-CLOSURE-ALL-REMAINING-CURRENT.md"


def directory(source, revision):
    suffix = "-v0.4" if source == "cookbook" else ""
    return ROOT / "data" / "sources" / source / (revision + suffix)


def read(source, revision, path):
    return (directory(source, revision) / path).read_text(encoding="utf-8")


def line(source, revision, path, fragment):
    lines = [line for line in read(source, revision, path).splitlines() if fragment in line]
    if len(lines) != 1:
        raise ValueError(f"Expected one source line for {fragment!r}: {len(lines)}")
    return lines[0]


def ev(label, context, models=None, status="working_hypothesis"):
    return dict(status=status, source_label=label, independently_verified=False,
                model_scope=models or ["v6", "v6-wild", "v6-mini"], test_count=None,
                context=context, model_basis="v6_targeted")


def add_entry(collection, source, revision, id, path, fragment, text, meaning, category,
              kind="phrase", field="style", label="V6 guide vocabulary; untested wording", context=None):
    collection.append(dict(id=id, kind=kind, path=path, excerpt=line(source, revision, path, fragment),
        text=text, meaning=meaning, category=category, input_field=field,
        evidence=ev(label, context or "Selected for a V6-family application. This establishes the target, not an observed effect; meaning is an editorial adaptation.")))


def main():
    if (ROOT / "curations/archive/0.11-foundation").exists():
        raise SystemExit("Historical builder: refusing to overwrite the reviewed foundation selection. Use current curations and export_glossary.py; reproduce old builders in a separate historical checkout.")
    band = json.loads((ROOT / "curations/archive/0.3/band-manager.json").read_text(encoding="utf-8"))
    cook = json.loads((ROOT / "curations/archive/0.3/cookbook.json").read_text(encoding="utf-8"))
    band["orientation"] = "mixed"
    band["orientation_excerpt"] = line("band-manager", BAND, "README.md", "The v6 guidance in this release is a **preview**")
    for entry in band["entries"]:
        entry["evidence"]["model_basis"] = "v6_targeted" if entry["evidence"]["model_scope"] else "unspecified"
        if entry["id"] == "refrain-legacy-limit":
            entry["evidence"]["model_basis"] = "pre_v6"
    cook["orientation"] = "v6_native"
    cook["orientation_excerpt"] = line("cookbook", COOK, "README.md", "A community cookbook for Suno v6 prompting")
    for record in [*cook["entries"], *cook["recipes"]]:
        record["evidence"]["model_basis"] = "v6_targeted" if record["evidence"]["model_scope"] else "unspecified"
    cook["recipes"][0]["workflow"] = "text-to-song"

    example_specs = [
        ("05-cassette-highway", "cassette-highway", "Cassette Highway", "synthwave", "wild-to-flagship-refinement", ["v6-wild", "v6"], "official-informed",
         "Exploration question → bridge seed → v6 refinement"),
        ("07-break-the-silence", "break-the-silence", "Break the Silence", "rock-anthem", "text-to-song", ["v6"], "working-hypothesis", "[Verse] → [Chorus]"),
    ]
    for filename, id, title, family, workflow, models, label, structure in example_specs:
        path = f"library/examples/{filename}.md"
        doc = read("cookbook", COOK, path)
        style = doc.split("## Style Prompt\n", 1)[1].split("\n\n", 1)[0].strip()
        excludes = doc.split("## Exclude Styles\n", 1)[1].split("\n\n", 1)[0].strip()
        block = doc.split("```text\n", 1)[1].split("\n```", 1)[0]
        cook["recipes"].append(dict(id=id, path=path, title=title, family=family, workflow=workflow,
            style_prompt=style, structure=structure, structure_excerpt=block, exclude_styles=excludes,
            evidence=ev(label, "Source frontmatter verified: false. Structure is an editorial summary of the source's section or exploration sequence; expected results are not measured results.", models, "unverified_example")))
    for id, file, text, meaning, category in [
        ("gated-snare", "05-cassette-highway", "gated snare", "A snare timbre with an abruptly curtailed reverb envelope.", "production"),
        ("rising-arpeggios", "05-cassette-highway", "rising arpeggios", "Successive chord tones moving upward to create motion.", "arrangement"),
        ("delayed-guitar", "05-cassette-highway", "delayed electric guitar", "An electric-guitar part with audible time-delayed repeats.", "production"),
        ("propulsive-drums", "07-break-the-silence", "propulsive live drums", "An intended driving drum performance; retained even though another source warns about the word live.", "rhythm"),
        ("locked-bass", "07-break-the-silence", "locked bass", "A bass part coordinated closely with the groove rather than a free accompanying line.", "instrumentation"),
        ("wider-group-vocals", "07-break-the-silence", "wider group vocals in the chorus", "A chorus-specific ensemble vocal expansion, explicitly appropriate only when multiple voices are wanted.", "vocals"),
    ]:
        add_entry(cook["entries"], "cookbook", COOK, id, f"library/examples/{file}.md", "Original synthwave," if file.startswith("05") else "Original uplifting rock anthem,",
                  text, meaning, category, label="unverified V6 example; verified: false")

    entries = []
    for id, text, meaning in [
        ("sustained-phrases", "long sustained phrases", "Extended sung phrases that maintain tone across a longer breath or melodic span."),
        ("clipped-phrases", "short clipped phrases", "Brief phrases with deliberately curtailed endings and audible gaps."),
        ("behind-beat", "behind-the-beat delivery", "Place vocal attacks slightly after the reference pulse for a laid-back feel without necessarily changing tempo."),
        ("forward-rhythm", "forward rhythmic delivery", "A vocal delivery intended to feel rhythmically pushing or urgent; exact timing remains unspecified."),
        ("melismatic", "melismatic", "Singing multiple pitches on one syllable, rather than assigning a new syllable to each note."),
        ("syllabic", "syllabic", "A primarily one-note-per-syllable relationship between text and melody."),
    ]:
        add_entry(entries, "lil-synn", LIL, id, ADD, text, text, meaning, "vocals")
    for id, text, meaning, fragment in [
        ("grainy", "grainy", "A finely roughened or textured vocal timbre; not a specific loudness or register.", "clean / husky / breathy / raspy / grainy"),
        ("husky", "husky", "A darker or breath-rough vocal color, distinct from a pitch-register instruction.", "clean / husky / breathy / raspy / grainy"),
        ("head-dominant", "head-dominant", "A head-dominant registration quality; not assumed identical to falsetto.", "low / baritone / tenor / alto / high"),
        ("chest-dominant", "chest-dominant", "A chest-dominant registration quality, separate from the lyric's emotional delivery.", "low / baritone / tenor / alto / high"),
    ]:
        add_entry(entries, "lil-synn", LIL, id, ADD, fragment, text, meaning, "vocals")
    for id, fragment, text, meaning in [
        ("kick-ducking", "| Sidechain |", "subtle kick-driven ducking", "A request for a restrained level dip triggered by the kick; no exact compression setting is implied."),
        ("centered-bass", "| Mono compatibility |", "centered low end, controlled stereo bass", "A low-frequency spatial intention; this wording alone does not establish measured mono compatibility."),
        ("upper-mid-edge", "| Harshness |", "softened upper-mid edge", "A request to reduce an abrasive upper-midrange impression without prescribing a numeric EQ operation."),
        ("foreground-depth", "| Depth |", "intimate foreground, distant ambience", "Contrast a near main element with farther ambient space."),
    ]:
        add_entry(entries, "lil-synn", LIL, id, GAP, fragment, text, meaning, "production")
    for id, fragment, text, meaning, category, field in [
        ("working-hierarchy", "There is no official Suno document saying", "working production model", "The proposed instruction hierarchy is an author heuristic, not an official implementation specification.", "arrangement", None),
        ("avoidance-experimental", "Negative prompting is **not documented", "experimental technique", "Negative wording is offered as a test candidate, not as a deterministic exclusion language.", "controls", "style"),
        ("positive-replacement", "A positive replacement is often more actionable", "A positive replacement", "State what should fill the role instead of relying only on a prohibition.", "arrangement", "style"),
        ("single-success", "A technique is not “proven”", "one generation worked", "A successful single output is insufficient to establish a prompt technique's repeatable effect.", "controls", None),
        ("test-variable", "VARIABLE CHANGED:", "VARIABLE CHANGED:", "Record the changed variable alongside model, references, controls, failures and output IDs.", "controls", None),
    ]:
        add_entry(entries, "lil-synn", LIL, id, ADD, fragment, text, meaning, category, "guidance", field,
                  label="V6 workflow/testing guidance; not an empirical effect report")
    for id, fragment, meaning in [
        ("sparse-verse", "Verse: intimate acoustic guitar, close vocal, sparse percussion.", "Assign acoustic guitar, near vocal and sparse percussion specifically to the verse."),
        ("expanded-chorus", "Chorus: introduce huge drums, wide synths and stacked harmonies.", "Reserve the added drum, synth and vocal density for the chorus rather than imposing it on every section."),
    ]:
        add_entry(entries, "lil-synn", LIL, id, ADD, fragment, fragment, meaning, "arrangement")
    add_entry(entries, "lil-synn", LIL, "wild-discovery", ADD, "v6-wild → unusual discoveries", "v6-wild → unusual discoveries",
              "Use wild for exploratory candidates; a discovery does not imply identical reconstruction with another model.", "controls", "guidance", "settings",
              label="author workflow based on model roles; refinement recipe not tested")
    lil = dict(source_id="lil-synn", revision=LIL, orientation="v6_native",
        orientation_excerpt=line("lil-synn", LIL, "README.md", "It is a **complete working reference"),
        changes="Selected V6-oriented wording and method notes; added English explanatory adaptations and evidence limits. Excluded the unsubstantiated Audio Quality Rescue recipe. No independent effect testing.",
        entries=entries, recipes=[])
    for source_id, payload in [("band-manager", band), ("cookbook", cook), ("lil-synn", lil)]:
        payload["changes"] += " Source orientation and record-level model basis reviewed for the 0.4 V6 core; targeting is not test evidence."
        (ROOT / "curations" / f"{source_id}.json").write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"{source_id}: {len(payload['entries'])} entries, {len(payload['recipes'])} recipes")
    from prompt_reference.adapters.curated import load_curated_source
    from prompt_reference.reviews import ReviewSet
    specs = [("band-manager", BAND), ("cookbook", COOK), ("lil-synn", LIL)]
    bundles = [load_curated_source(directory(source, revision), ROOT / "curations" / f"{source}.json") for source, revision in specs]
    cases = [
        dict(id="model-routing", topic="Exploration versus controlled refinement",
             record_ids=["lil-synn:wild-discovery", "cookbook:cassette-highway"], assessment="complementary",
             conclusion="The guide's discovery loop and the cookbook's bridge exercise fit the official model-role distinction. This does not prove faithful reconstruction of a wild output in v6.",
             evidence_limit="Both may draw on the same Suno model documentation; they are not two independent tests.",
             primary_links=["https://help.suno.com/en/articles/13924737"]),
        dict(id="exclusions", topic="Negative wording and positive replacement",
             record_ids=["lil-synn:avoidance-experimental", "lil-synn:positive-replacement", "cookbook:break-the-silence"], assessment="complementary",
             conclusion="The cookbook keeps exclusions as a separate field; LIL SYNN treats avoidance as experimental and proposes positive replacements. Neither establishes a universal negation rule.",
             evidence_limit="Prompt examples and editorial advice only. No controlled paired audio results were found for these records."),
        dict(id="live-drums", topic="The word live versus intended acoustic drum character",
             record_ids=["cookbook:propulsive-drums", "band-manager:room-sound"], assessment="tension",
             conclusion="The V6 cookbook intentionally requests live drums; Band Manager's room-sound advice reflects its concern about crowd associations. Preserve both as context-dependent alternatives, without automatically banning live.",
             evidence_limit="The cookbook example is unverified; the selected Band Manager caveat lacks an isolated current-model test. This comparison does not establish which wording works better."),
        dict(id="vocal-facets", topic="Vocal timing versus conversational character",
             record_ids=["lil-synn:behind-beat", "cookbook:conversational-vocal"], assessment="complementary",
             conclusion="Behind-the-beat placement describes timing; conversational describes delivery character. They can be selected separately rather than treated as interchangeable voice labels.",
             evidence_limit="A musical distinction useful for prompt composition; not a demonstrated improvement in Suno output."),
    ]
    review = ReviewSet.model_validate(dict(reviewed_on="2026-10-26",
        snapshots={bundle.source.id: bundle.source.snapshot_id for bundle in bundles}, cases=cases))
    (ROOT / "reviews").mkdir(exist_ok=True)
    (ROOT / "reviews/v6-crosschecks.json").write_text(review.model_dump_json(indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
