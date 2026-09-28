"""Helpers for multimodal Collections workflows (text + local image path references).

Collections documents are text-only. These helpers store a local image path in document
metadata fields and reconstruct paths after search for vision chat follow-up.
"""

from __future__ import annotations

import base64
import datetime
import mimetypes
from pathlib import Path
from typing import TYPE_CHECKING, Mapping, Optional, Sequence

from typing_extensions import NotRequired, TypedDict

from .collections import FieldDefinition
from .proto import chat_pb2, collections_pb2, documents_pb2

if TYPE_CHECKING:
    from .aio.collections import Client as AsyncCollectionsClient
    from .sync.collections import Client as SyncCollectionsClient
    from .types import ImageDetail

DEFAULT_IMAGE_PATH_FIELD = "image_path"
_WINDOWS_DRIVE_PATH_MIN_LENGTH = 2

SUPPORTED_IMAGE_SUFFIXES = frozenset({".jpg", ".jpeg", ".png", ".webp", ".gif"})


class MultimodalSearchResult(TypedDict):
    """A collection search hit with resolved local image paths."""

    file_id: str
    chunk_id: str
    chunk_content: str
    score: float
    collection_ids: list[str]
    image_paths: list[str]


class MultimodalUploadParams(TypedDict):
    """Prepared arguments for collections.upload_document."""

    name: str
    data: bytes
    fields: dict[str, str]
    wait_for_indexing: NotRequired[bool]
    poll_interval: NotRequired[datetime.timedelta]
    timeout: NotRequired[datetime.timedelta]


def multimodal_field_definitions(
    *,
    field_key: str = DEFAULT_IMAGE_PATH_FIELD,
    inject_into_chunk: bool = True,
) -> list[FieldDefinition]:
    """Return field definitions for a multimodal collection schema.

    Args:
        field_key: Metadata key used to store the local image path on each document.
        inject_into_chunk: When True, the image path is prepended to each chunk so search
            results may contain the path even before a metadata lookup.

    Returns:
        A list suitable for the `field_definitions` argument of `collections.create()`.
    """
    return [
        {
            "key": field_key,
            "required": True,
            "inject_into_chunk": inject_into_chunk,
            "unique": False,
            "description": "Local filesystem path to the associated image.",
        }
    ]


def _normalize_image_path(image_path: str | Path) -> Path:
    path = Path(image_path).expanduser()
    if not path.is_file():
        msg = f"Image path does not exist or is not a file: {image_path}"
        raise FileNotFoundError(msg)
    return path.resolve()


def _validate_image_suffix(path: Path) -> None:
    if path.suffix.lower() not in SUPPORTED_IMAGE_SUFFIXES:
        supported = ", ".join(sorted(SUPPORTED_IMAGE_SUFFIXES))
        msg = f"Unsupported image type {path.suffix!r}. Supported suffixes: {supported}"
        raise ValueError(msg)


def build_multimodal_fields(
    image_path: str | Path,
    *,
    field_key: str = DEFAULT_IMAGE_PATH_FIELD,
    validate_image: bool = True,
    **extra_fields: str,
) -> dict[str, str]:
    """Build document metadata fields for a multimodal upload.

    Args:
        image_path: Local path to the associated image.
        field_key: Metadata key for the image path.
        validate_image: When True, require a supported image file extension.
        **extra_fields: Additional string metadata fields merged into the result.

    Returns:
        A fields dict for `collections.upload_document()`.
    """
    path = _normalize_image_path(image_path)
    if validate_image:
        _validate_image_suffix(path)
    return {field_key: str(path), **extra_fields}


def prepare_multimodal_upload(
    name: str,
    text: str,
    image_path: str | Path,
    *,
    field_key: str = DEFAULT_IMAGE_PATH_FIELD,
    validate_image: bool = True,
    extra_fields: Optional[dict[str, str]] = None,
    wait_for_indexing: bool = False,
    poll_interval: Optional[datetime.timedelta] = None,
    timeout: Optional[datetime.timedelta] = None,
) -> MultimodalUploadParams:
    """Prepare name, bytes, and fields for a multimodal document upload.

    Example:
        ```python
        params = prepare_multimodal_upload("item.txt", "Description", "/img/a.jpg")
        client.collections.upload_document(collection_id, **params)
        ```
    """
    merged_extra = dict(extra_fields or {})
    fields = build_multimodal_fields(
        image_path,
        field_key=field_key,
        validate_image=validate_image,
        **merged_extra,
    )
    params: MultimodalUploadParams = {
        "name": name,
        "data": text.encode("utf-8"),
        "fields": fields,
    }
    if wait_for_indexing:
        params["wait_for_indexing"] = True
    if poll_interval is not None:
        params["poll_interval"] = poll_interval
    if timeout is not None:
        params["timeout"] = timeout
    return params


def image_paths_from_fields(
    fields: Mapping[str, str],
    *,
    field_key: str = DEFAULT_IMAGE_PATH_FIELD,
) -> list[Path]:
    """Extract image paths from document metadata fields."""
    value = fields.get(field_key)
    if not value:
        return []
    return [Path(value).expanduser()]


def image_paths_from_chunk_content(chunk_content: str) -> list[Path]:
    """Best-effort extraction of a prepended local path from chunk text.

    When `inject_into_chunk` is enabled on the image path field, the indexer prepends
    the field value to each chunk. This helper reads the first line when it looks like
    a filesystem path.
    """
    if not chunk_content:
        return []

    first_line = chunk_content.split("\n", 1)[0].strip()
    if not first_line:
        return []

    candidate = Path(first_line).expanduser()
    if first_line.startswith("/") or first_line.startswith("~"):
        return [candidate]
    if len(first_line) > _WINDOWS_DRIVE_PATH_MIN_LENGTH and first_line[1] == ":":
        return [candidate]
    return []


def resolve_image_paths(
    match: documents_pb2.SearchMatch,
    document_fields: Mapping[str, str] | None = None,
    *,
    field_key: str = DEFAULT_IMAGE_PATH_FIELD,
) -> list[Path]:
    """Resolve local image paths for a single search match.

    Document fields are authoritative when provided. Chunk content is used as a fallback.
    """
    if document_fields is not None:
        field_paths = image_paths_from_fields(document_fields, field_key=field_key)
        if field_paths:
            return field_paths

    return image_paths_from_chunk_content(match.chunk_content)


def resolve_multimodal_search_results(
    matches: Sequence[documents_pb2.SearchMatch],
    document_fields_by_file_id: Mapping[str, Mapping[str, str]],
    *,
    field_key: str = DEFAULT_IMAGE_PATH_FIELD,
) -> list[MultimodalSearchResult]:
    """Attach resolved image paths to each search match."""
    results: list[MultimodalSearchResult] = []
    for match in matches:
        fields = document_fields_by_file_id.get(match.file_id)
        image_paths = resolve_image_paths(match, fields, field_key=field_key)
        results.append(
            {
                "file_id": match.file_id,
                "chunk_id": match.chunk_id,
                "chunk_content": match.chunk_content,
                "score": match.score,
                "collection_ids": list(match.collection_ids),
                "image_paths": [str(path) for path in image_paths],
            }
        )
    return results


def document_fields_by_file_id(
    collections_client: SyncCollectionsClient,
    collection_id: str,
    matches: Sequence[documents_pb2.SearchMatch],
) -> dict[str, dict[str, str]]:
    """Batch-fetch document fields for the file IDs present in search matches."""
    file_ids = list(dict.fromkeys(match.file_id for match in matches))
    if not file_ids:
        return {}

    response = collections_client.batch_get_documents(collection_id, file_ids)
    return {
        document.file_metadata.file_id: dict(document.fields)
        for document in response.documents
        if document.fields
    }


async def document_fields_by_file_id_async(
    collections_client: AsyncCollectionsClient,
    collection_id: str,
    matches: Sequence[documents_pb2.SearchMatch],
) -> dict[str, dict[str, str]]:
    """Async variant of `document_fields_by_file_id`."""
    file_ids = list(dict.fromkeys(match.file_id for match in matches))
    if not file_ids:
        return {}

    response = await collections_client.batch_get_documents(collection_id, file_ids)
    return {
        document.file_metadata.file_id: dict(document.fields)
        for document in response.documents
        if document.fields
    }


def upload_multimodal_document(
    collections_client: SyncCollectionsClient,
    collection_id: str,
    name: str,
    text: str,
    image_path: str | Path,
    *,
    field_key: str = DEFAULT_IMAGE_PATH_FIELD,
    validate_image: bool = True,
    extra_fields: Optional[dict[str, str]] = None,
    wait_for_indexing: bool = False,
    poll_interval: Optional[datetime.timedelta] = None,
    timeout: Optional[datetime.timedelta] = None,
) -> collections_pb2.DocumentMetadata:
    """Upload searchable text with a local image path stored in document metadata."""
    params = prepare_multimodal_upload(
        name,
        text,
        image_path,
        field_key=field_key,
        validate_image=validate_image,
        extra_fields=extra_fields,
        wait_for_indexing=wait_for_indexing,
        poll_interval=poll_interval,
        timeout=timeout,
    )
    return collections_client.upload_document(collection_id, **params)


async def upload_multimodal_document_async(
    collections_client: AsyncCollectionsClient,
    collection_id: str,
    name: str,
    text: str,
    image_path: str | Path,
    *,
    field_key: str = DEFAULT_IMAGE_PATH_FIELD,
    validate_image: bool = True,
    extra_fields: Optional[dict[str, str]] = None,
    wait_for_indexing: bool = False,
    poll_interval: Optional[datetime.timedelta] = None,
    timeout: Optional[datetime.timedelta] = None,
) -> collections_pb2.DocumentMetadata:
    """Async variant of `upload_multimodal_document`."""
    params = prepare_multimodal_upload(
        name,
        text,
        image_path,
        field_key=field_key,
        validate_image=validate_image,
        extra_fields=extra_fields,
        wait_for_indexing=wait_for_indexing,
        poll_interval=poll_interval,
        timeout=timeout,
    )
    return await collections_client.upload_document(collection_id, **params)


def local_image_data_url(path: str | Path) -> str:
    """Read a local image and return a base64 data URL for `chat.image()`.

    Args:
        path: Local filesystem path to a PNG or JPEG image.

    Returns:
        A string like `data:image/jpeg;base64,...` suitable for `chat.image()`.
    """
    resolved = _normalize_image_path(path)
    if resolved.suffix.lower() not in SUPPORTED_IMAGE_SUFFIXES:
        _validate_image_suffix(resolved)

    mime_type, _ = mimetypes.guess_type(resolved.name)
    if mime_type is None:
        mime_type = "image/jpeg"

    encoded = base64.b64encode(resolved.read_bytes()).decode("utf-8")
    return f"data:{mime_type};base64,{encoded}"


def multimodal_user_message(
    text: str,
    image_paths: Sequence[str | Path],
    *,
    detail: Optional[ImageDetail] = "auto",
) -> chat_pb2.Message:
    """Build a vision user message from text and local image paths.

    Example:
        ```python
        chat.append(multimodal_user_message("Describe this item.", ["/data/a.jpg"]))
        ```
    """
    from .chat import image, user
    from .types import Content

    contents: list[Content] = [text]
    for image_path in image_paths:
        contents.append(image(local_image_data_url(image_path), detail=detail))
    return user(*contents)
