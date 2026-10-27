import argparse
import json
import sqlite3
import sys
from typing import get_args
from pathlib import Path
from urllib.error import URLError

from .adapters.musai import fetch_snapshot, load_snapshot
from .adapters.curated import DEFINITIONS, fetch_curated_source, load_curated_source
from .models import Bundle, ReferenceEntry
from .workspace import Draft, Preferences
from .listening import ListeningAssessment, ListeningDocument
from .library import LibraryPage
from .reference_selection import LibrarySelection, DraftReferencePack
from .prompt_text import PromptText, PromptVersion, PromptVersionPage
from .store import Store
from .search import plan_query
from .reviews import resolve_reviews
from .concepts import CatalogService, ConceptCatalog, ContextPacket, render_context


def main():
    parser = argparse.ArgumentParser(description="Portable music prompt reference core")
    parser.add_argument("--db", type=Path, default=Path("data/reference.sqlite3"))
    sub = parser.add_subparsers(dest="command", required=True)
    fetch = sub.add_parser("fetch-musai", help="Download a pinned, licensed source snapshot")
    fetch.add_argument("revision")
    fetch.add_argument("directory", type=Path)
    imp = sub.add_parser("import-musai", help="Validate and atomically import a local snapshot")
    imp.add_argument("directory", type=Path)
    reference_fetch = sub.add_parser("fetch-reference", help="Fetch a pinned Band Manager or Cookbook source selection")
    reference_fetch.add_argument("source", choices=DEFINITIONS)
    reference_fetch.add_argument("revision")
    reference_fetch.add_argument("directory", type=Path)
    reference_import = sub.add_parser("import-reference", help="Import an explicit reviewed curation against a local source")
    reference_import.add_argument("directory", type=Path)
    reference_import.add_argument("curation", type=Path)
    search = sub.add_parser("search")
    search.add_argument("query")
    search.add_argument("--literal", action="store_true", help="Disable reviewed query expansions")
    search.add_argument("--explain", action="store_true", help="Include the explicit query expansion plan")
    search.add_argument("--limit", type=int, default=20)
    search.add_argument("--snapshot")
    search.add_argument("--kind", choices=["recipe", "term", "phrase", "guidance"])
    search.add_argument("--category", choices=get_args(ReferenceEntry.model_fields["category"].annotation))
    search.add_argument("--history", action="store_true", help="Include inactive historical selections")
    search.add_argument("--v6-core", action="store_true", help="Only V6-targeted records from reviewed V6-native sources; not a tested-effects filter")
    search.add_argument("--model-basis", choices=["unspecified", "v6_targeted", "pre_v6"])
    sub.add_parser("snapshots")
    activate = sub.add_parser("activate", help="Select one snapshot as the active version of its source")
    activate.add_argument("snapshot")
    stats = sub.add_parser("stats")
    stats.add_argument("--history", action="store_true")
    stats.add_argument("--v6-core", action="store_true")
    crosscheck = sub.add_parser("crosschecks", help="Resolve editorial comparisons against their exact source snapshots")
    crosscheck.add_argument("file", type=Path)
    concepts = sub.add_parser("concepts", help="Find reviewed musical concepts by English labels and aliases")
    concepts.add_argument("query", nargs="?", default="")
    context = sub.add_parser("context", help="Assemble a source-bound context packet; no AI call or automatic prompt mixing")
    context.add_argument("concept_ids", nargs="+")
    context.add_argument("--intent", default="")
    context.add_argument("--model", choices=["v6", "v6-wild", "v6-mini"], default="v6")
    context.add_argument("--supplementary", action="store_true")
    context.add_argument("--limit", type=int, default=24)
    context.add_argument("--format", choices=["json", "markdown"], default="json")
    context.add_argument("--output", type=Path)
    for command in (concepts, context):
        command.add_argument("--catalog", type=Path, default=Path("curations/concepts.json"))
        command.add_argument("--reviews", type=Path, default=Path("reviews/v6-crosschecks.json"))
    export = sub.add_parser("export")
    export.add_argument("snapshot")
    export.add_argument("output", type=Path)
    schema = sub.add_parser("schema")
    schema.add_argument("output", type=Path)
    schema.add_argument("--contract", choices=["bundle", "concepts", "context", "draft", "preferences", "listening", "listening-document", "library", "library-selection", "draft-references", "prompt-text", "prompt-version", "prompt-history"], default="bundle")
    serve = sub.add_parser("serve", help="Open the local workbench server on 127.0.0.1")
    serve.add_argument("--port", type=int, default=8765)
    serve.add_argument("--catalog", type=Path, default=Path("curations/concepts.json"))
    serve.add_argument("--reviews", type=Path, default=Path("reviews/v6-crosschecks.json"))
    serve.add_argument("--frontend", type=Path, default=Path("web/dist"))
    args = parser.parse_args()
    try:
        if args.command == "serve":
            if not 1 <= args.port <= 65535:
                raise ValueError("Port must be between 1 and 65535")
            try:
                import uvicorn
                from .server import create_app
            except ImportError as error:
                raise ValueError("Install the web extra first: uv sync --extra web") from error
            uvicorn.run(create_app(args.db, args.catalog, args.reviews, args.frontend), host="127.0.0.1", port=args.port)
            return
        if args.command == "fetch-musai":
            print(fetch_snapshot(args.directory, args.revision).model_dump_json(indent=2))
            return
        if args.command == "fetch-reference":
            print(fetch_curated_source(args.source, args.revision, args.directory).model_dump_json(indent=2))
            return
        if args.command == "schema":
            args.output.parent.mkdir(parents=True, exist_ok=True)
            contract = {"bundle": Bundle, "concepts": ConceptCatalog, "context": ContextPacket, "draft": Draft, "preferences": Preferences, "listening": ListeningAssessment, "listening-document": ListeningDocument, "library": LibraryPage, "library-selection": LibrarySelection, "draft-references": DraftReferencePack, "prompt-text": PromptText, "prompt-version": PromptVersion, "prompt-history": PromptVersionPage}[args.contract]
            args.output.write_text(json.dumps(contract.model_json_schema(), indent=2) + "\n", encoding="utf-8")
            return
        # Validate all source records before opening/mutating the database.
        bundle = load_snapshot(args.directory) if args.command == "import-musai" else None
        if args.command == "import-reference":
            bundle = load_curated_source(args.directory, args.curation)
        args.db.parent.mkdir(parents=True, exist_ok=True)
        with Store(args.db) as store:
            if args.command in ("import-musai", "import-reference"):
                print(json.dumps({"snapshot_id": bundle.source.snapshot_id, "imported": store.import_bundle(bundle),
                                  "total_in_source": len(bundle.recipes) + len(bundle.entries),
                                  "recipes": len(bundle.recipes), "entries": len(bundle.entries)}))
            elif args.command == "search":
                hits = store.search(args.query, args.limit, args.snapshot, args.kind, args.history, args.category, args.v6_core, args.model_basis, expand=not args.literal)
                payload = {"search_plan": plan_query(args.query, expand=not args.literal).model_dump(), "items": hits} if args.explain else hits
                print(json.dumps(payload, indent=2, ensure_ascii=False))
            elif args.command == "snapshots":
                print(json.dumps(store.snapshots(), indent=2))
            elif args.command == "activate":
                store.activate(args.snapshot)
                print(json.dumps(store.active_snapshots(), indent=2))
            elif args.command == "stats":
                print(json.dumps(store.stats(args.history, args.v6_core), indent=2))
            elif args.command == "crosschecks":
                print(json.dumps(resolve_reviews(store, args.file), indent=2, ensure_ascii=False))
            elif args.command in ("concepts", "context"):
                service = CatalogService(store, args.catalog, args.reviews)
                if args.command == "concepts":
                    print(json.dumps([concept.model_dump() for concept in service.find(args.query)], indent=2, ensure_ascii=False))
                else:
                    packet = service.build_context(args.concept_ids, args.intent, args.model, args.supplementary, args.limit)
                    payload = render_context(packet) if args.format == "markdown" else packet.model_dump_json(indent=2)
                    if args.output:
                        args.output.parent.mkdir(parents=True, exist_ok=True)
                        with args.output.open("x", encoding="utf-8") as output:
                            output.write(payload)
                    else:
                        print(payload)
            elif args.command == "export":
                payload = store.export(args.snapshot).model_dump_json(indent=2)
                args.output.parent.mkdir(parents=True, exist_ok=True)
                with args.output.open("x", encoding="utf-8") as output:
                    output.write(payload + "\n")
    except (ValueError, OSError, sqlite3.Error, URLError) as error:
        print(f"Error: {error}", file=sys.stderr)
        raise SystemExit(1) from error


if __name__ == "__main__":
    main()
