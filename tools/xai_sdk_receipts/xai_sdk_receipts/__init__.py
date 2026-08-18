"""xAI Collections Status — indexing doctor, channel probes, and RAG readiness dashboard."""

from .dashboard import build_dashboard, export_dashboard
from .doctor import diagnose_collection, diagnose_fleet
from .probe import probe_channels
from .receipt import build_demo_receipt, build_live_receipt, write_receipt

__all__ = [
    "build_dashboard",
    "build_demo_receipt",
    "build_live_receipt",
    "diagnose_collection",
    "diagnose_fleet",
    "export_dashboard",
    "probe_channels",
    "write_receipt",
]
