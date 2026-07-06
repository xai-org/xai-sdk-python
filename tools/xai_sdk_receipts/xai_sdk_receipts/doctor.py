"""Diagnose Collections indexing health and RAG readiness."""

from __future__ import annotations

from typing import Any

from xai_sdk.proto import collections_pb2

from .indexing import fetch_collection_documents, summarize_documents
from .probe import probe_search_smoke


def _finding(
    severity: str,
    code: str,
    message: str,
    *,
    collection_id: str | None = None,
    action: str | None = None,
) -> dict[str, Any]:
    return {
        "severity": severity,
        "code": code,
        "message": message,
        "collection_id": collection_id,
        "action": action,
    }


def diagnose_collection(
    client: Any,
    collection: collections_pb2.CollectionMetadata,
    *,
    document_limit: int = 100,
    run_search_smoke: bool = True,
) -> dict[str, Any]:
    """Run indexing + RAG readiness checks on one collection."""
    collection_id = collection.collection_id
    documents = fetch_collection_documents(client.collections, collection_id, limit=document_limit)
    indexing = summarize_documents(documents)

    findings: list[dict[str, Any]] = []

    if collection.documents_count and indexing["processed"] == 0 and indexing["in_flight"] == 0:
        findings.append(
            _finding(
                "critical",
                "rag_not_ready",
                f"Collection '{collection.collection_name}' has {collection.documents_count} documents "
                "but none are processed for search.",
                collection_id=collection_id,
                action="Re-upload documents or call reindex_document on failed items.",
            )
        )

    if indexing["failed"] > 0:
        findings.append(
            _finding(
                "error",
                "indexing_failed",
                f"{indexing['failed']} document(s) failed indexing.",
                collection_id=collection_id,
                action="Inspect error_message via get_document; fix fields/content and reindex.",
            )
        )

    if indexing["in_flight"] > 0 and indexing["processed"] == 0:
        findings.append(
            _finding(
                "warn",
                "indexing_backlog",
                f"{indexing['in_flight']} document(s) still in the indexing pipeline.",
                collection_id=collection_id,
                action="Wait for processing or use batch_get_documents polling instead of per-doc loops.",
            )
        )

    stuck = [
        d
        for d in indexing["in_flight_documents"]
        if d.get("minutes_since_last_indexed") is not None and d["minutes_since_last_indexed"] > 30
    ]
    if stuck:
        findings.append(
            _finding(
                "warn",
                "indexing_stuck",
                f"{len(stuck)} document(s) appear stuck in-flight (>30 min since last index activity).",
                collection_id=collection_id,
                action="Check server status; consider reindex_document or re-upload.",
            )
        )

    search_smoke = None
    if run_search_smoke and indexing["processed"] > 0:
        search_smoke = probe_search_smoke(client, collection_id)
        if search_smoke["status"] != "ok":
            findings.append(
                _finding(
                    "error",
                    "search_unreachable",
                    "Search RPC failed for a collection with processed documents.",
                    collection_id=collection_id,
                    action="Verify API key scopes and collection_id; check documents service health.",
                )
            )

    health = "healthy"
    if any(f["severity"] == "critical" for f in findings):
        health = "critical"
    elif any(f["severity"] == "error" for f in findings):
        health = "degraded"
    elif findings:
        health = "warn"

    return {
        "collection_id": collection_id,
        "name": collection.collection_name,
        "documents_count": collection.documents_count,
        "embedding_model": collection.index_configuration.model_name,
        "health": health,
        "rag_ready": indexing["rag_ready"],
        "indexing": indexing,
        "search_smoke": search_smoke,
        "findings": findings,
    }


def diagnose_fleet(
    client: Any,
    *,
    collection_id: str | None = None,
    document_limit: int = 100,
) -> dict[str, Any]:
    """Scan collections fleet and return per-collection diagnoses."""
    if collection_id:
        meta = client.collections.get(collection_id)
        collections = [meta]
    else:
        response = client.collections.list(limit=50)
        collections = list(response.collections)

    panels = [
        diagnose_collection(client, col, document_limit=document_limit)
        for col in collections
    ]

    findings = [f for panel in panels for f in panel["findings"]]

    fleet_health = "healthy"
    if any(p["health"] == "critical" for p in panels):
        fleet_health = "critical"
    elif any(p["health"] == "degraded" for p in panels):
        fleet_health = "degraded"
    elif any(p["health"] == "warn" for p in panels):
        fleet_health = "warn"

    rag_ready_count = sum(1 for p in panels if p["rag_ready"])
    total_docs = sum(p["documents_count"] for p in panels)
    failed_docs = sum(p["indexing"]["failed"] for p in panels)
    in_flight_docs = sum(p["indexing"]["in_flight"] for p in panels)

    return {
        "fleet_health": fleet_health,
        "collection_count": len(panels),
        "rag_ready_collections": rag_ready_count,
        "totals": {
            "documents": total_docs,
            "failed": failed_docs,
            "in_flight": in_flight_docs,
        },
        "collections": panels,
        "findings": findings,
    }


def build_demo_fleet() -> dict[str, Any]:
    """Synthetic fleet for offline dashboard demos."""
    return {
        "fleet_health": "warn",
        "collection_count": 3,
        "rag_ready_collections": 1,
        "totals": {"documents": 1247, "failed": 12, "in_flight": 89},
        "collections": [
            {
                "collection_id": "col-prod-catalog",
                "name": "prod-product-catalog",
                "documents_count": 842,
                "embedding_model": "grok-embedding-small",
                "health": "healthy",
                "rag_ready": True,
                "indexing": {
                    "total_sampled": 100,
                    "counts": {
                        "processed": 100,
                        "failed": 0,
                        "processing": 0,
                        "chunked": 0,
                        "embedding": 0,
                        "writing": 0,
                        "unknown": 0,
                    },
                    "processed": 100,
                    "failed": 0,
                    "in_flight": 0,
                    "rag_ready": True,
                    "rag_ready_ratio": 1.0,
                    "failed_documents": [],
                    "in_flight_documents": [],
                    "pipeline": [
                        {"stage": "processing", "count": 0},
                        {"stage": "chunked", "count": 0},
                        {"stage": "embedding", "count": 0},
                        {"stage": "writing", "count": 0},
                        {"stage": "processed", "count": 100},
                        {"stage": "failed", "count": 0},
                    ],
                },
                "search_smoke": {"status": "ok", "latency_ms": 231.4, "match_count": 3},
                "findings": [],
            },
            {
                "collection_id": "col-hackathon-rag",
                "name": "hackathon-design-reviews",
                "documents_count": 312,
                "embedding_model": "grok-embedding-small",
                "health": "degraded",
                "rag_ready": False,
                "indexing": {
                    "total_sampled": 80,
                    "counts": {
                        "processed": 45,
                        "failed": 12,
                        "processing": 8,
                        "chunked": 5,
                        "embedding": 6,
                        "writing": 4,
                        "unknown": 0,
                    },
                    "processed": 45,
                    "failed": 12,
                    "in_flight": 23,
                    "rag_ready": False,
                    "rag_ready_ratio": 0.562,
                    "failed_documents": [
                        {
                            "file_id": "file-9a2f",
                            "name": "workflow-3.pdf",
                            "error": "required field 'author' missing",
                        },
                        {
                            "file_id": "file-7c11",
                            "name": "scaling-report.md",
                            "error": "unique constraint violated for field 'doc_id'",
                        },
                    ],
                    "in_flight_documents": [
                        {
                            "file_id": "file-b881",
                            "name": "batch-upload-044.json",
                            "status": "embedding",
                            "chunks_processed": 12,
                            "chunk_count": 18,
                            "minutes_since_last_indexed": 47.2,
                        }
                    ],
                    "pipeline": [
                        {"stage": "processing", "count": 8},
                        {"stage": "chunked", "count": 5},
                        {"stage": "embedding", "count": 6},
                        {"stage": "writing", "count": 4},
                        {"stage": "processed", "count": 45},
                        {"stage": "failed", "count": 12},
                    ],
                },
                "search_smoke": {"status": "ok", "latency_ms": 284.1, "match_count": 2},
                "findings": [
                    _finding(
                        "error",
                        "indexing_failed",
                        "12 document(s) failed indexing.",
                        collection_id="col-hackathon-rag",
                        action="Inspect error_message via get_document; fix fields/content and reindex.",
                    ),
                    _finding(
                        "warn",
                        "indexing_stuck",
                        "1 document(s) appear stuck in-flight (>30 min since last index activity).",
                        collection_id="col-hackathon-rag",
                        action="Check server status; consider reindex_document or re-upload.",
                    ),
                ],
            },
            {
                "collection_id": "col-legal-corpus",
                "name": "legal-corpus-v2",
                "documents_count": 93,
                "embedding_model": "grok-embedding-small",
                "health": "warn",
                "rag_ready": False,
                "indexing": {
                    "total_sampled": 93,
                    "counts": {
                        "processed": 0,
                        "failed": 0,
                        "processing": 22,
                        "chunked": 31,
                        "embedding": 28,
                        "writing": 12,
                        "unknown": 0,
                    },
                    "processed": 0,
                    "failed": 0,
                    "in_flight": 93,
                    "rag_ready": False,
                    "rag_ready_ratio": 0.0,
                    "failed_documents": [],
                    "in_flight_documents": [],
                    "pipeline": [
                        {"stage": "processing", "count": 22},
                        {"stage": "chunked", "count": 31},
                        {"stage": "embedding", "count": 28},
                        {"stage": "writing", "count": 12},
                        {"stage": "processed", "count": 0},
                        {"stage": "failed", "count": 0},
                    ],
                },
                "search_smoke": None,
                "findings": [
                    _finding(
                        "warn",
                        "indexing_backlog",
                        "93 document(s) still in the indexing pipeline.",
                        collection_id="col-legal-corpus",
                        action="Use batch_get_documents polling (#77) instead of per-document wait loops.",
                    ),
                ],
            },
        ],
        "findings": [],
    }
