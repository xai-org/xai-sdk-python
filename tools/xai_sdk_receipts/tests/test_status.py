from xai_sdk.proto import collections_pb2

from xai_sdk_receipts.dashboard import build_dashboard, export_dashboard
from xai_sdk_receipts.doctor import build_demo_fleet
from xai_sdk_receipts.indexing import summarize_documents
from xai_sdk_receipts.probe import build_demo_probes


def test_build_demo_probes():
    probes = build_demo_probes()
    assert probes["overall"] == "healthy"
    assert len(probes["probes"]) == 2


def test_summarize_documents_processed():
    docs = [
        collections_pb2.DocumentMetadata(
            file_metadata=collections_pb2.FileMetadata(file_id="a", name="a.txt"),
            status=collections_pb2.DocumentStatus.DOCUMENT_STATUS_PROCESSED,
        ),
        collections_pb2.DocumentMetadata(
            file_metadata=collections_pb2.FileMetadata(file_id="b", name="b.txt"),
            status=collections_pb2.DocumentStatus.DOCUMENT_STATUS_FAILED,
            error_message="bad field",
        ),
    ]
    summary = summarize_documents(docs)
    assert summary["processed"] == 1
    assert summary["failed"] == 1
    assert summary["rag_ready"] is False
    assert len(summary["failed_documents"]) == 1


def test_build_demo_fleet_has_findings():
    fleet = build_demo_fleet()
    assert fleet["collection_count"] == 3
    assert fleet["rag_ready_collections"] == 1
    degraded = [c for c in fleet["collections"] if c["health"] == "degraded"]
    assert degraded


def test_build_demo_dashboard():
    dash = build_dashboard(demo=True)
    assert dash["product"] == "xAI Collections Status"
    assert dash["overall"] in ("healthy", "warn", "degraded", "critical")
    assert dash["probes"]["overall"] == "healthy"
    assert dash["fleet"]["collection_count"] == 3
    assert dash["multimodal_roundtrip"]["roundtrip_verified"] is True


def test_export_dashboard(tmp_path):
    out = tmp_path / "dashboard.json"
    export_dashboard(out, demo=True)
    dash = build_dashboard(demo=True)
    assert out.exists()
    assert "fleet" in out.read_text()
    assert dash["mode"] == "demo"
