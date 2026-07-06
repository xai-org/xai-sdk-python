"""CLI for xAI Collections Status."""

from __future__ import annotations

import argparse
import json
import sys
import tempfile
from pathlib import Path

from .dashboard import build_dashboard, export_dashboard
from .doctor import diagnose_fleet
from .probe import probe_channels
from .receipt import build_demo_receipt, build_live_receipt, write_receipt


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="xAI Collections Status — is your collection actually ready for search?",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    probe = sub.add_parser("probe", help="Probe API + Management API channel health")
    probe.add_argument("--demo", action="store_true", help="Offline demo probes")

    doctor = sub.add_parser("doctor", help="Diagnose indexing health across collections")
    doctor.add_argument("--demo", action="store_true", help="Offline demo fleet")
    doctor.add_argument("--collection-id", help="Scope to one collection")
    doctor.add_argument("--limit", type=int, default=100, help="Max documents to sample per collection")

    dash = sub.add_parser("dashboard", help="Export full status dashboard JSON")
    dash.add_argument("--demo", action="store_true", help="Offline demo dashboard")
    dash.add_argument("-o", "--output", type=Path, required=True, help="Output JSON path")
    dash.add_argument("--collection-id", help="Scope to one collection (live mode)")

    run = sub.add_parser("run", help="Run multimodal roundtrip receipt (legacy)")
    mode = run.add_mutually_exclusive_group(required=True)
    mode.add_argument("--demo", action="store_true", help="Offline simulated roundtrip")
    mode.add_argument("--live", action="store_true", help="Live API roundtrip (needs XAI_API_KEY)")
    run.add_argument("--output", "-o", type=Path, help="Write receipt JSON to file")
    run.add_argument("--query", default="glossy red widget", help="Search query for live mode")
    run.add_argument("--image", type=Path, help="Local image path for live mode")
    run.add_argument("--collection-id", help="Existing collection ID (live mode)")
    run.add_argument("--keep-collection", action="store_true", help="Do not delete temp collection")

    args = parser.parse_args(argv)

    if args.command == "probe":
        if args.demo:
            payload = build_dashboard(demo=True)["probes"]
        else:
            from xai_sdk import Client

            payload = probe_channels(Client())
        print(json.dumps(payload, indent=2))
        return 0 if payload.get("overall") == "healthy" else 2

    if args.command == "doctor":
        if args.demo:
            payload = build_dashboard(demo=True)["fleet"]
        else:
            from xai_sdk import Client

            payload = diagnose_fleet(Client(), collection_id=args.collection_id, document_limit=args.limit)
        print(json.dumps(payload, indent=2))
        health = payload.get("fleet_health", "healthy")
        return 0 if health == "healthy" else 2

    if args.command == "dashboard":
        client = None
        if not args.demo:
            from xai_sdk import Client

            client = Client()
        path = export_dashboard(
            args.output.expanduser().resolve(),
            client,
            collection_id=args.collection_id,
            demo=args.demo,
        )
        print(f"Wrote {path}", file=sys.stderr)
        payload = json.loads(path.read_text())
        return 0 if payload.get("overall") in ("healthy", "warn") else 2

    if args.command == "run":
        if args.demo:
            receipt = build_demo_receipt(query=args.query)
        else:
            from xai_sdk import Client

            image_path = args.image
            if image_path is None:
                with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as tmp:
                    tmp.write(b"\xff\xd8\xff demo-image")
                    image_path = Path(tmp.name)

            image_path = image_path.expanduser().resolve()
            if not image_path.is_file():
                print(f"error: image not found: {image_path}", file=sys.stderr)
                return 1

            client = Client()
            receipt = build_live_receipt(
                client,
                collection_id=args.collection_id,
                image_path=image_path,
                query=args.query,
                cleanup=not args.keep_collection,
                on_progress=lambda msg: print(msg, file=sys.stderr),
            )

        print(json.dumps(receipt, indent=2))
        if args.output:
            out = write_receipt(receipt, args.output.expanduser().resolve())
            print(f"\nWrote {out}", file=sys.stderr)

        return 0 if receipt["summary"]["overall"] == "pass" else 2

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
