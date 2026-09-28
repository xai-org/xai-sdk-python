import json
from pathlib import Path

from xai_sdk_receipts.receipt import build_demo_receipt, write_receipt
from xai_sdk_receipts.redact import redact_path, redact_step


def test_build_demo_receipt_passes():
    receipt = build_demo_receipt()
    assert receipt["mode"] == "demo"
    assert receipt["summary"]["overall"] == "pass"
    assert receipt["summary"]["roundtrip_verified"] is True
    assert len(receipt["steps"]) >= 4


def test_redact_path_keeps_filename():
    assert redact_path("/secret/dir/widget.jpg") == "[REDACTED_PATH]/widget.jpg"


def test_redact_step_masks_file_id():
    step = redact_step({"step": "upload", "status": "ok", "file_id": "abcdefgh12345678"})
    assert "…" in step["file_id"]


def test_write_receipt(tmp_path: Path):
    receipt = build_demo_receipt()
    out = write_receipt(receipt, tmp_path / "receipt.json")
    data = json.loads(out.read_text())
    assert data["workflow"] == "collections_multimodal_roundtrip"
