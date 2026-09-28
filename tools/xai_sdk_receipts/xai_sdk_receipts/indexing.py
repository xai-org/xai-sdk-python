"""Aggregate document indexing status across a collection."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from xai_sdk.proto import collections_pb2

_STATUS_NAMES = {
    collections_pb2.DocumentStatus.DOCUMENT_STATUS_UNKNOWN: "unknown",
    collections_pb2.DocumentStatus.DOCUMENT_STATUS_PROCESSING: "processing",
    collections_pb2.DocumentStatus.DOCUMENT_STATUS_PROCESSED: "processed",
    collections_pb2.DocumentStatus.DOCUMENT_STATUS_FAILED: "failed",
    collections_pb2.DocumentStatus.DOCUMENT_STATUS_CHUNKED: "chunked",
    collections_pb2.DocumentStatus.DOCUMENT_STATUS_EMBEDDING: "embedding",
    collections_pb2.DocumentStatus.DOCUMENT_STATUS_WRITING: "writing",
}

_IN_FLIGHT = frozenset(
    {
        collections_pb2.DocumentStatus.DOCUMENT_STATUS_PROCESSING,
        collections_pb2.DocumentStatus.DOCUMENT_STATUS_CHUNKED,
        collections_pb2.DocumentStatus.DOCUMENT_STATUS_EMBEDDING,
        collections_pb2.DocumentStatus.DOCUMENT_STATUS_WRITING,
    }
)


def status_name(status: int) -> str:
    return _STATUS_NAMES.get(status, f"status_{status}")


def summarize_documents(documents: list[collections_pb2.DocumentMetadata]) -> dict[str, Any]:
    """Build indexing funnel counts and failure details from document metadata."""
    counts: dict[str, int] = {name: 0 for name in set(_STATUS_NAMES.values())}
    failed: list[dict[str, str]] = []
    in_flight: list[dict[str, Any]] = []
    now = datetime.now(UTC)

    for doc in documents:
        name = status_name(doc.status)
        counts[name] = counts.get(name, 0) + 1

        file_id = doc.file_metadata.file_id
        doc_name = doc.file_metadata.name

        if doc.status == collections_pb2.DocumentStatus.DOCUMENT_STATUS_FAILED:
            failed.append(
                {
                    "file_id": file_id,
                    "name": doc_name,
                    "error": doc.error_message or "unknown error",
                }
            )
        elif doc.status in _IN_FLIGHT:
            age_minutes = None
            if doc.last_indexed_at.seconds:
                indexed = doc.last_indexed_at.ToDatetime().replace(tzinfo=UTC)
                age_minutes = round((now - indexed).total_seconds() / 60, 1)
            in_flight.append(
                {
                    "file_id": file_id,
                    "name": doc_name,
                    "status": name,
                    "chunks_processed": doc.chunks_processed_count,
                    "chunk_count": doc.chunk_count,
                    "minutes_since_last_indexed": age_minutes,
                }
            )

    total = sum(counts.values())
    processed = counts.get("processed", 0)
    rag_ready = processed > 0 and counts.get("failed", 0) == 0

    return {
        "total_sampled": total,
        "counts": counts,
        "processed": processed,
        "failed": counts.get("failed", 0),
        "in_flight": sum(counts.get(s, 0) for s in ("processing", "chunked", "embedding", "writing")),
        "rag_ready": rag_ready,
        "rag_ready_ratio": round(processed / total, 3) if total else 0.0,
        "failed_documents": failed[:20],
        "in_flight_documents": in_flight[:20],
        "pipeline": [
            {"stage": "processing", "count": counts.get("processing", 0)},
            {"stage": "chunked", "count": counts.get("chunked", 0)},
            {"stage": "embedding", "count": counts.get("embedding", 0)},
            {"stage": "writing", "count": counts.get("writing", 0)},
            {"stage": "processed", "count": counts.get("processed", 0)},
            {"stage": "failed", "count": counts.get("failed", 0)},
        ],
    }


def fetch_collection_documents(
    collections_client: Any,
    collection_id: str,
    *,
    limit: int = 100,
) -> list[collections_pb2.DocumentMetadata]:
    """List documents for indexing analysis (paginated up to limit)."""
    documents: list[collections_pb2.DocumentMetadata] = []
    token: str | None = None

    while len(documents) < limit:
        page_limit = min(50, limit - len(documents))
        response = collections_client.list_documents(
            collection_id,
            limit=page_limit,
            pagination_token=token,
        )
        documents.extend(response.documents)
        token = response.pagination_token or None
        if not token or not response.documents:
            break

    return documents
