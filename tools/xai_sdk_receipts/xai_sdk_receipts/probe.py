"""Probe xAI API and Management API channel health."""

from __future__ import annotations

import os
import time
from typing import Any, Callable

import grpc

PROBE_QUERY = "__collections_status_probe__"


def _latency_ms(started: float) -> float:
    return round((time.perf_counter() - started) * 1000, 2)


def _status_from_error(exc: Exception) -> str:
    if isinstance(exc, grpc.RpcError):
        return exc.code().name  # type: ignore[union-attr]
    return type(exc).__name__


def probe_channels(client: Any) -> dict[str, Any]:
    """Probe API and Management API channels with lightweight RPCs."""
    probes: list[dict[str, Any]] = []

    t0 = time.perf_counter()
    try:
        models = client.models.list_embedding_models()
        probes.append(
            {
                "channel": "api",
                "check": "list_embedding_models",
                "status": "ok",
                "latency_ms": _latency_ms(t0),
                "detail": f"{len(models)} embedding models",
            }
        )
    except Exception as exc:
        probes.append(
            {
                "channel": "api",
                "check": "list_embedding_models",
                "status": "fail",
                "latency_ms": _latency_ms(t0),
                "error": str(exc),
                "grpc_code": _status_from_error(exc),
            }
        )

    has_mgmt_key = bool(os.getenv("XAI_MANAGEMENT_KEY"))
    t0 = time.perf_counter()
    try:
        response = client.collections.list(limit=1)
        probes.append(
            {
                "channel": "management",
                "check": "list_collections",
                "status": "ok",
                "latency_ms": _latency_ms(t0),
                "detail": f"{len(response.collections)} collections returned (page)",
                "management_key_configured": has_mgmt_key,
            }
        )
    except Exception as exc:
        probes.append(
            {
                "channel": "management",
                "check": "list_collections",
                "status": "fail",
                "latency_ms": _latency_ms(t0),
                "error": str(exc),
                "grpc_code": _status_from_error(exc),
                "management_key_configured": has_mgmt_key,
            }
        )

    overall = "healthy" if all(p["status"] == "ok" for p in probes) else "degraded"
    if any(p["status"] == "fail" for p in probes):
        overall = "unhealthy"

    return {
        "overall": overall,
        "probes": probes,
        "management_key_configured": has_mgmt_key,
    }


def probe_search_smoke(client: Any, collection_id: str) -> dict[str, Any]:
    """Run a lightweight search to verify RAG path is live."""
    t0 = time.perf_counter()
    try:
        response = client.collections.search(
            query=PROBE_QUERY,
            collection_ids=[collection_id],
            limit=1,
        )
        return {
            "status": "ok",
            "latency_ms": _latency_ms(t0),
            "match_count": len(response.matches),
            "note": "Empty matches are OK for probe query; RPC success means search path is up.",
        }
    except Exception as exc:
        return {
            "status": "fail",
            "latency_ms": _latency_ms(t0),
            "error": str(exc),
            "grpc_code": _status_from_error(exc),
        }


def build_demo_probes() -> dict[str, Any]:
    return {
        "overall": "healthy",
        "management_key_configured": True,
        "probes": [
            {
                "channel": "api",
                "check": "list_embedding_models",
                "status": "ok",
                "latency_ms": 142.3,
                "detail": "3 embedding models",
            },
            {
                "channel": "management",
                "check": "list_collections",
                "status": "ok",
                "latency_ms": 198.7,
                "detail": "3 collections returned (page)",
                "management_key_configured": True,
            },
        ],
    }
