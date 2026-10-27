"""Generate a readable review view from the validated current curations."""
from collections import Counter
from pathlib import Path

from prompt_reference.adapters.curated import load_curated_source

ROOT = Path(__file__).resolve().parents[1]
SOURCES = (
    ("band-manager", "73c52379833af51e9d3ce7731746d3bfff3f5266"),
    ("cookbook", "c8e40ff0b10636a7719cbc88bc5f58443ad19907-v0.4"),
    ("lil-synn", "6b805bf77a350e7fba00bfd2451273327482827c"),
)


def cell(text):
    return text.replace("|", "\\|").replace("\n", " ")


def main():
    bundles = [load_curated_source(ROOT / "data" / "sources" / source / revision,
                                  ROOT / "curations" / f"{source}.json") for source, revision in SOURCES]
    entries = [(bundle.source, entry) for bundle in bundles for entry in bundle.entries]
    counts = Counter(entry.category for _, entry in entries)
    lines = ["# Reviewed English vocabulary — 0.4", "",
        f"{len(entries)} source-bound entries: " + ", ".join(f"{category} ({count})" for category, count in sorted(counts.items())) + ".", "",
        "Generated from validated, pinned sources. Meanings are editorial adaptations. Source wording and grades are retained; none of these entries is independently verified for musical effect.", "",
        "Model scope is stated only where the reviewed passage or example supplies it. An empty scope is not a current-v6 certification. Useful musical vocabulary is retained even when source tag reliability is low.", "",
        "Attribution: zarlor / suno-band-manager (MIT); MJorgin and the Suno v6 Cookbook contributors (CC BY 4.0); LIL SYNN (CC0). Selected excerpts, English explanations and categories are adaptations. See [full notices](../THIRD_PARTY_NOTICES.md).", "",
        "V6 core = reviewed V6-native source plus explicit V6 targeting on the record. It is a relevance selection, not a verification grade. Mixed-source V6 advice remains separate. See [V6 core policy](v6-core.md).", ""]
    for category in sorted(counts):
        lines += [f"## {category.capitalize()}", "", "| Wording | Kind / field | Audible meaning or scope | Source grade | Model basis | Citation |", "|---|---|---|---|---|---|"]
        for source, entry in sorted(entries, key=lambda item: (item[1].text.casefold(), item[0].id)):
            if entry.category != category:
                continue
            citation = entry.citations[0]
            core = source.orientation == "v6_native" and entry.evidence.model_basis == "v6_targeted"
            basis = "V6 core" if core else entry.evidence.model_basis
            lines.append(f"| {cell(entry.text)} | {entry.kind} / {entry.input_field or 'unspecified'} | {cell(entry.meaning)} | {cell(entry.evidence.source_label)} | {basis} | [{source.id}, L{citation.line_start}]({citation.url}) |")
        lines.append("")
    target = ROOT / "docs" / "vocabulary.md"
    target.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {len(entries)} entries to {target}")


if __name__ == "__main__":
    main()
