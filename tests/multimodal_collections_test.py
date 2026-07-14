import base64
from pathlib import Path

import pytest

from xai_sdk.multimodal_collections import (
    DEFAULT_IMAGE_PATH_FIELD,
    build_multimodal_fields,
    image_paths_from_chunk_content,
    image_paths_from_fields,
    local_image_data_url,
    multimodal_field_definitions,
    prepare_multimodal_upload,
    resolve_image_paths,
    resolve_multimodal_search_results,
)
from xai_sdk.proto import documents_pb2


def test_multimodal_field_definitions_defaults():
    definitions = multimodal_field_definitions()
    assert len(definitions) == 1
    assert definitions[0]["key"] == DEFAULT_IMAGE_PATH_FIELD
    assert definitions[0]["required"] is True
    assert definitions[0]["inject_into_chunk"] is True


def test_build_multimodal_fields(tmp_path: Path):
    image = tmp_path / "photo.jpg"
    image.write_bytes(b"fake-jpeg")
    fields = build_multimodal_fields(image, sku="widget-1")
    assert fields[DEFAULT_IMAGE_PATH_FIELD] == str(image.resolve())
    assert fields["sku"] == "widget-1"


def test_build_multimodal_fields_rejects_missing_file(tmp_path: Path):
    with pytest.raises(FileNotFoundError, match="does not exist"):
        build_multimodal_fields(tmp_path / "missing.jpg")


def test_build_multimodal_fields_rejects_unsupported_suffix(tmp_path: Path):
    text_file = tmp_path / "notes.txt"
    text_file.write_text("not an image")
    with pytest.raises(ValueError, match="Unsupported image type"):
        build_multimodal_fields(text_file)


def test_prepare_multimodal_upload(tmp_path: Path):
    image = tmp_path / "photo.png"
    image.write_bytes(b"fake-png")
    params = prepare_multimodal_upload("item.txt", "hello", image, wait_for_indexing=True)
    assert params["name"] == "item.txt"
    assert params["data"] == b"hello"
    assert params["fields"][DEFAULT_IMAGE_PATH_FIELD] == str(image.resolve())
    assert params["wait_for_indexing"] is True


def test_image_paths_from_fields(tmp_path: Path):
    image = tmp_path / "a.jpg"
    image.write_bytes(b"jpeg")
    paths = image_paths_from_fields({DEFAULT_IMAGE_PATH_FIELD: str(image)})
    assert paths == [image]


def test_image_paths_from_chunk_content_absolute_path():
    chunk = "/data/images/widget.jpg\nRed widget description."
    paths = image_paths_from_chunk_content(chunk)
    assert paths == [Path("/data/images/widget.jpg")]


def test_image_paths_from_chunk_content_windows_path():
    chunk = "C:\\images\\widget.jpg\nDescription"
    paths = image_paths_from_chunk_content(chunk)
    assert paths == [Path("C:\\images\\widget.jpg")]


def test_resolve_image_paths_prefers_fields():
    match = documents_pb2.SearchMatch(
        file_id="file-1",
        chunk_id="chunk-1",
        chunk_content="/other/path.jpg\nbody",
        score=0.9,
    )
    paths = resolve_image_paths(match, {DEFAULT_IMAGE_PATH_FIELD: "/data/a.jpg"})
    assert paths == [Path("/data/a.jpg")]


def test_resolve_multimodal_search_results():
    matches = [
        documents_pb2.SearchMatch(
            file_id="file-1",
            chunk_id="chunk-1",
            chunk_content="/data/a.jpg\ntext",
            score=0.8,
            collection_ids=["col-1"],
        )
    ]
    fields_map = {"file-1": {DEFAULT_IMAGE_PATH_FIELD: "/data/a.jpg"}}
    results = resolve_multimodal_search_results(matches, fields_map)
    assert len(results) == 1
    assert results[0]["file_id"] == "file-1"
    assert results[0]["image_paths"] == ["/data/a.jpg"]


def test_local_image_data_url(tmp_path: Path):
    image = tmp_path / "photo.jpg"
    payload = b"binary-image"
    image.write_bytes(payload)
    data_url = local_image_data_url(image)
    assert data_url.startswith("data:image/jpeg;base64,")
    encoded = data_url.split(",", 1)[1]
    assert base64.b64decode(encoded) == payload
