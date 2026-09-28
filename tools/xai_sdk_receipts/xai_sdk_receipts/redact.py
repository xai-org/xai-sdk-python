"""Redact sensitive values from receipt audit logs."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

_REDACTED = "[REDACTED]"
_PATH_REDACTED = "[REDACTED_PATH]"
_KEY_PATTERN = re.compile(r"(?i)(api[_-]?key|token|secret|password)\s*[:=]\s*\S+")
_UUID_LIKE = re.compile(
    r"\b[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\b",
    re.IGNORECASE,
)


def redact_path(value: str) -> str:
    if not value:
        return value
    path = Path(value)
    return f"{_PATH_REDACTED}/{path.name}" if path.name else _PATH_REDACTED


def redact_file_id(file_id: str) -> str:
    if len(file_id) <= 8:
        return _REDACTED
    return f"{file_id[:4]}…{file_id[-4:]}"


def redact_text(text: str) -> str:
    text = _KEY_PATTERN.sub(r"\1=[REDACTED]", text)
    text = _UUID_LIKE.sub(_REDACTED, text)
    return text


def redact_fields(fields: dict[str, str]) -> dict[str, str]:
    redacted: dict[str, str] = {}
    for key, value in fields.items():
        if key == "image_path" or "path" in key.lower():
            redacted[key] = redact_path(value)
        else:
            redacted[key] = value
    return redacted


def redact_step(step: dict[str, Any]) -> dict[str, Any]:
    out = dict(step)
    if "file_id" in out and isinstance(out["file_id"], str):
        out["file_id"] = redact_file_id(out["file_id"])
    if "collection_id" in out and isinstance(out["collection_id"], str):
        out["collection_id"] = redact_file_id(out["collection_id"])
    if "image_paths" in out and isinstance(out["image_paths"], list):
        out["image_paths"] = [redact_path(str(p)) for p in out["image_paths"]]
    if "fields" in out and isinstance(out["fields"], dict):
        out["fields"] = redact_fields(out["fields"])
    if "chunk_content" in out and isinstance(out["chunk_content"], str):
        out["chunk_content"] = redact_text(out["chunk_content"][:240])
    if "error" in out and isinstance(out["error"], str):
        out["error"] = redact_text(out["error"])
    return out
