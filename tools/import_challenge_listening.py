"""Import the first challenge reports through the public local API, without duplicates."""
import argparse
import json
from pathlib import Path
from urllib.request import Request, urlopen

from prompt_reference.adapters.challenge_listening import convert_report


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("case", type=Path)
    args = parser.parse_args()
    case = json.loads((args.case / "challenge.json").read_text(encoding="utf-8"))
    log = json.loads((args.case / "listening-log.json").read_text(encoding="utf-8"))
    base = "http://127.0.0.1:8765/api/drafts/" + case["workspace_draft_id"]

    def api(path="", body=None):
        request = Request(base + path, data=None if body is None else json.dumps(body).encode(),
                          headers={"Content-Type": "application/json"})
        with urlopen(request, timeout=15) as response:
            return json.load(response)

    parent = api()
    existing = api("/listening")
    imported = []
    for raw in log["runs"]:
        matches = [record for record in existing if
            (record["original_assessment"].get("raw_report") or {}).get("run_id") == raw["run_id"]]
        if matches:
            if len(matches) != 1 or matches[0]["original_assessment"]["raw_report"] != raw:
                raise ValueError("Existing imported evidence differs; review it explicitly instead of overwriting")
            imported.append(matches[0])
            continue
        assessment = convert_report(raw)
        imported.append(api("/listening", {
            "title": raw.get("display_label") or f"{raw['actual_model']} · W{raw['weirdness']}/SI{raw['style_influence']}",
            "draft_revision": parent["revision"], "assessment": assessment.model_dump(mode="json"),
        }))
    output = args.case / "listening-records.json"
    output.write_text(json.dumps(imported, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"{len(imported)} reports available; original evidence preserved. Export: {output}")


if __name__ == "__main__":
    main()
