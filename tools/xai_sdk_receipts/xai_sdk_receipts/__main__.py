"""CLI: python -m xai_sdk_receipts run --demo | --live"""

from __future__ import annotations

import argparse
import json
import sys
import tempfile
from pathlib import Path

from .receipt import build_demo_receipt, build_live_receipt, write_receipt


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="xAI SDK Reliability Receipts — multimodal Collections roundtrip audit",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    run = sub.add_parser("run", help="Execute roundtrip and emit receipt JSON")
    mode = run.add_mutually_exclusive_group(required=True)
    mode.add_argument("--demo", action="store_true", help="Offline simulated roundtrip")
    mode.add_argument("--live", action="store_true", help="Live API roundtrip (needs XAI_API_KEY)")
    run.add_argument("--output", "-o", type=Path, help="Write receipt JSON to file")
    run.add_argument("--query", default="glossy red widget", help="Search query for live mode")
    run.add_argument(
        "--image",
        type=Path,
        help="Local image path for live mode (temp file created in demo if omitted)",
    )
    run.add_argument("--collection-id", help="Existing collection ID (live mode)")
    run.add_argument("--keep-collection", action="store_true", help="Do not delete temp collection")

    args = parser.parse_args(argv)

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
            path = write_receipt(receipt, args.output.expanduser().resolve())
            print(f"\nWrote {path}", file=sys.stderr)

        return 0 if receipt["summary"]["overall"] == "pass" else 2

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
