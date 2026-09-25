"""Build reliability receipts for multimodal Collections roundtrips."""

from __future__ import annotations

import json
import time
import uuid
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Callable

from xai_sdk import __version__ as sdk_version
from xai_sdk.multimodal_collections import (
    DEFAULT_IMAGE_PATH_FIELD,
    document_fields_by_file_id,
    multimodal_field_definitions,
    resolve_multimodal_search_results,
    upload_multimodal_document,
)
from xai_sdk.proto import documents_pb2

from .redact import redact_step


def _now_iso() -> str:
    return datetime.now(UTC).isoformat()


def _step(
    name: str,
    status: str,
    started_at: float,
    **extra: Any,
) -> dict[str, Any]:
    return {
        "step": name,
        "status": status,
        "duration_ms": round((time.perf_counter() - started_at) * 1000, 2),
        **extra,
    }


def _finalize(steps: list[dict[str, Any]], mode: str, query: str) -> dict[str, Any]:
    redacted_steps = [redact_step(s) for s in steps]
    failed = [s for s in steps if s.get("status") != "ok"]
    resolved = next((s for s in steps if s.get("step") == "resolve_paths"), None)
    return {
        "receipt_version": "1.0",
        "run_id": str(uuid.uuid4()),
        "generated_at": _now_iso(),
        "mode": mode,
        "sdk_version": sdk_version,
        "workflow": "collections_multimodal_roundtrip",
        "query": query,
        "steps": redacted_steps,
        "summary": {
            "overall": "pass" if not failed else "fail",
            "step_count": len(steps),
            "failed_steps": len(failed),
            "roundtrip_verified": resolved is not None and resolved.get("status") == "ok",
            "paths_resolved": resolved.get("path_count", 0) if resolved else 0,
        },
        "disclaimer": (
            "Third-party reliability harness for xAI SDK multimodal Collections helpers. "
            "Not affiliated with xAI."
        ),
    }


def build_demo_receipt(
    *,
    image_path: str = "/data/catalog/widget-a.jpg",
    query: str = "glossy red widget",
) -> dict[str, Any]:
    """Offline receipt simulating upload → search → resolve without API calls."""
    steps: list[dict[str, Any]] = []
    file_id = "demo-file-0001"
    collection_id = "demo-collection-01"
    resolved_path = str(Path(image_path).resolve() if Path(image_path).is_absolute() else image_path)

    t0 = time.perf_counter()
    fields = {DEFAULT_IMAGE_PATH_FIELD: resolved_path, "sku": "W-001"}
    steps.append(
        _step(
            "prepare_multimodal_upload",
            "ok",
            t0,
            document_name="widget-a.txt",
            fields=fields,
        )
    )

    t0 = time.perf_counter()
    match = documents_pb2.SearchMatch(
        file_id=file_id,
        chunk_id="chunk-demo-1",
        chunk_content=f"{resolved_path}\nRed widget, 12cm, glossy finish with chrome trim.",
        score=0.91,
        collection_ids=[collection_id],
    )
    steps.append(
        _step(
            "search",
            "ok",
            t0,
            match_count=1,
            top_score=match.score,
        )
    )

    t0 = time.perf_counter()
    fields_map = {file_id: fields}
    resolved = resolve_multimodal_search_results([match], fields_map)
    steps.append(
        _step(
            "resolve_paths",
            "ok",
            t0,
            path_count=len(resolved[0]["image_paths"]) if resolved else 0,
            image_paths=resolved[0]["image_paths"] if resolved else [],
            chunk_preview=resolved[0]["chunk_content"][:120] if resolved else "",
        )
    )

    t0 = time.perf_counter()
    steps.append(
        _step(
            "vision_chat_ready",
            "ok",
            t0,
            message="multimodal_user_message() inputs validated (demo — no API call)",
        )
    )

    return _finalize(steps, mode="demo", query=query)


def build_live_receipt(
    client: Any,
    *,
    collection_id: str | None = None,
    text: str = "Red widget, 12cm, glossy finish with chrome trim.",
    image_path: str | Path,
    query: str = "glossy red widget",
    cleanup: bool = True,
    on_progress: Callable[[str], None] | None = None,
) -> dict[str, Any]:
    """Run a live multimodal Collections roundtrip and capture a redacted receipt."""
    steps: list[dict[str, Any]] = []
    created_collection = False
    collection_to_delete: str | None = None
    image = Path(image_path).expanduser().resolve()

    def log(msg: str) -> None:
        if on_progress:
            on_progress(msg)

    try:
        if collection_id is None:
            t0 = time.perf_counter()
            log("Creating multimodal collection…")
            collection = client.collections.create(
                name=f"receipts-{uuid.uuid4().hex[:8]}",
                field_definitions=multimodal_field_definitions(),
            )
            collection_id = collection.collection_id
            created_collection = True
            collection_to_delete = collection_id
            steps.append(_step("create_collection", "ok", t0, collection_id=collection_id))
        else:
            steps.append(
                {
                    "step": "create_collection",
                    "status": "skipped",
                    "duration_ms": 0,
                    "collection_id": collection_id,
                }
            )

        t0 = time.perf_counter()
        log("Uploading multimodal document…")
        document = upload_multimodal_document(
            client.collections,
            collection_id,
            name="receipt-item.txt",
            text=text,
            image_path=image,
            extra_fields={"sku": "receipt-demo"},
            wait_for_indexing=True,
        )
        file_id = document.file_metadata.file_id
        steps.append(
            _step(
                "upload_multimodal",
                "ok",
                t0,
                file_id=file_id,
                fields=dict(document.fields),
            )
        )

        t0 = time.perf_counter()
        log("Searching collection…")
        results = client.collections.search(query=query, collection_ids=[collection_id], limit=5)
        steps.append(
            _step(
                "search",
                "ok",
                t0,
                match_count=len(results.matches),
                top_score=results.matches[0].score if results.matches else None,
            )
        )

        t0 = time.perf_counter()
        log("Resolving image paths…")
        if results.matches:
            fields_map = document_fields_by_file_id(client.collections, collection_id, results.matches)
            resolved = resolve_multimodal_search_results(results.matches, fields_map)
            paths = resolved[0]["image_paths"] if resolved else []
            status = "ok" if paths else "warn"
        else:
            match = documents_pb2.SearchMatch(
                file_id=file_id,
                chunk_id="fallback-chunk",
                chunk_content=f"{image}\n{text}",
                score=1.0,
                collection_ids=[collection_id],
            )
            fields_map = document_fields_by_file_id(client.collections, collection_id, [match])
            resolved = resolve_multimodal_search_results([match], fields_map)
            paths = resolved[0]["image_paths"] if resolved else []
            status = "ok" if paths else "warn"

        steps.append(
            _step(
                "resolve_paths",
                status,
                t0,
                path_count=len(paths),
                image_paths=paths,
            )
        )

        t0 = time.perf_counter()
        steps.append(
            _step(
                "vision_chat_ready",
                "ok" if paths else "skipped",
                t0,
                message="Paths ready for multimodal_user_message()" if paths else "No paths resolved",
            )
        )

    except Exception as exc:
        steps.append(
            {
                "step": "error",
                "status": "fail",
                "duration_ms": 0,
                "error": str(exc),
            }
        )
        receipt = _finalize(steps, mode="live", query=query)
        if cleanup and created_collection and collection_to_delete:
            try:
                client.collections.delete(collection_to_delete)
            except Exception:
                pass
        return receipt

    receipt = _finalize(steps, mode="live", query=query)

    if cleanup and created_collection and collection_to_delete:
        try:
            client.collections.delete(collection_to_delete)
        except Exception:
            pass

    return receipt


def write_receipt(receipt: dict[str, Any], output: Path) -> Path:
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(receipt, indent=2) + "\n")
    return output
