"""Build dashboard payloads for xAI Collections Status."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from xai_sdk import __version__ as sdk_version

from .doctor import build_demo_fleet, diagnose_fleet
from .probe import build_demo_probes, probe_channels
from .receipt import build_demo_receipt


def build_dashboard(
    client: Any | None = None,
    *,
    collection_id: str | None = None,
    document_limit: int = 100,
    demo: bool = False,
) -> dict[str, Any]:
    """Assemble full status dashboard: probes + fleet doctor + multimodal receipt."""
    if demo or client is None:
        probes = build_demo_probes()
        fleet = build_demo_fleet()
        fleet["findings"] = [f for panel in fleet["collections"] for f in panel["findings"]]
        multimodal = build_demo_receipt()
        mode = "demo"
    else:
        probes = probe_channels(client)
        fleet = diagnose_fleet(client, collection_id=collection_id, document_limit=document_limit)
        multimodal = None
        mode = "live"

        if not probes["management_key_configured"]:
            fleet["findings"].insert(
                0,
                {
                    "severity": "critical",
                    "code": "missing_management_key",
                    "message": "XAI_MANAGEMENT_KEY is not set — Collections management APIs will fail.",
                    "collection_id": None,
                    "action": "Create a management key in console.x.ai and export XAI_MANAGEMENT_KEY.",
                },
            )
            fleet["fleet_health"] = "critical"

    overall = probes["overall"]
    if fleet["fleet_health"] in ("critical", "degraded", "unhealthy"):
        overall = fleet["fleet_health"]
    elif fleet["fleet_health"] == "warn" and overall == "healthy":
        overall = "warn"

    return {
        "product": "xAI Collections Status",
        "tagline": "Is your collection actually ready for search?",
        "generated_at": datetime.now(UTC).isoformat(),
        "mode": mode,
        "sdk_version": sdk_version,
        "overall": overall,
        "probes": probes,
        "fleet": fleet,
        "multimodal_roundtrip": (
            {
                "overall": multimodal["summary"]["overall"],
                "roundtrip_verified": multimodal["summary"]["roundtrip_verified"],
                "paths_resolved": multimodal["summary"]["paths_resolved"],
            }
            if multimodal
            else None
        ),
        "issue_refs": {
            "indexing_scaling": "https://github.com/xai-org/xai-sdk-python/issues/77",
            "multimodal_helpers": "https://github.com/xai-org/xai-sdk-python/issues/78",
            "sdk_pr": "https://github.com/xai-org/xai-sdk-python/pull/169",
        },
        "disclaimer": (
            "Third-party Collections health monitor for the xAI Python SDK. "
            "Not affiliated with xAI. Inspired by platform status tooling (e.g. tinker-status)."
        ),
    }


def export_dashboard(
    output: Path,
    client: Any | None = None,
    *,
    collection_id: str | None = None,
    demo: bool = False,
) -> Path:
    payload = build_dashboard(client, collection_id=collection_id, demo=demo)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2) + "\n")
    return output
